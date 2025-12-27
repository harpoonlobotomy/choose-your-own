# loot.name_col(item) == adding col to class
# assign_colour(text) == to print w colour

from os import system
from pprint import pprint
from time import sleep
import random

from misc_utilities import assign_colour, col_list, switch_the, generate_clean_inventory, get_inventory_names, from_inventory_name, check_name, print_type
from set_up_game import load_world, set_up, init_settings
from choices import choose, time_of_day, trip_over, emphasis
from env_data import p_data, weatherdict
from locations import places
from item_definitions import container_limit_sizes, detail_data

from item_management_2 import ItemInstance, registry

from tui_elements import add_infobox_data, print_commands
from tui_update import update_infobox, update_text_box

print("Importing choose_a_path_tui_vers.py")

user_prefs = r"D:\Git_Repos\Choose_your_own\path_userprefs.json"
run_again = False

END="\x1b[0m"
RESET = "\033[0m"
HIDE = "\033[?25l"
SHOW = "\033[?25h"

yes = ["y", "yes"]
no = ["n", "no", "nope"]
night = ["midnight", "late evening", "night", "pre-dawn"]

enable_tui=False#True

def slowLines(txt, speed=0.1, end=None, edit=False):
    if isinstance(txt, str) and txt.strip=="":
        edit=True
    update_text_box(to_print=txt, end=False, edit_list=edit, use_TUI=enable_tui)
    update_text_box(to_print="  ", end=False, use_TUI=enable_tui)

def do_print(text=None, end=None, edit_list=False):
    if text==None:
        text=" "
    slowLines(txt=text, speed=0.1, end=end, edit=edit_list)

def do_input():

    print(SHOW, end='')
    text=input()
    do_print(f"{HIDE}")
    if text == "" or text == None:
        #slowLines(" ")
        slowLines(" ")
    else:
        slowLines(f"{assign_colour(f'Chosen: ({text.strip()})', 'yellow')}")
    return text


def slowWriting(txt, speed=0.001, end=None, edit=False): # Just keeping this here for now as a way to maintain that once, these calls were different from the line prints.
    slowLines(txt, speed, end, edit)

def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def clean_separation_result(result:list, to_print=False):

    if not result:
        print("No result in clean_separation_result")
        return
    if not isinstance(result, list):
        print(f"Expecting a list of 'result'. Result is type {type(result)}. Contents: {result}")
        return

    results_len = len(result)
    for result_set in result:
        string = result_set[0]
        split_string = string.split("[")
        joint_split=[]
        for item in split_string:
            if item != "" and item != None:
                splits = item.split("]")
                for split_item in splits:
                    if split_item != "" and split_item != None:
                        joint_split.append(split_item)

        #print(joint_split)
        child = result_set[1]
        parent = result_set[2]

        coloured_list = []

        for i, item in enumerate(joint_split):
            if item == "child":
                item = assign_colour(child)#, caps=True)
            elif item == "parent" or item == "new_container":
                item = assign_colour(parent)
            else:
                item = assign_colour(item, colour="yellow")

            coloured_list.append(item)
        coloured_list = "".join(coloured_list)
        if to_print:
            do_print(coloured_list)

def separate_loot(child_input=None, parent_input=None): ## should be inside registry, not here.

    child = None
    parent = None

    if child_input and isinstance(child_input, ItemInstance):
        child = child_input

    if parent_input and isinstance(parent_input, ItemInstance):
        parent = parent_input

    #print(f"parent: {parent}, child: {child}")
    if parent and not child:
        children = registry.instances_by_container(parent)
        #or
        #children = parent.children # < Seems much more straightforward. Any downside?
        #print(f"children: {children}")
        if children:
            for item in children:
                game.inventory, result = registry.move_from_container_to_inv(item, game.inventory, parent)

    else:
        game.inventory, result = registry.move_from_container_to_inv(child, game.inventory, parent)

    clean_separation_result(result, to_print=True)
    #  return strings:
#   (f"[child] removed from old container [parent]", inst, parent)
#   (f"Added [child] to new container [new_container]", inst, new_container)


    #print(f"game.inventory: {game.inventory}")
    return game.inventory, result

def get_items_at_here(print_list=False, return_coloured=True) -> list:

    instance_objs_at = (registry.instances_by_location(switch_the(game.place, replace_with=""), game.facing_direction))

    to_print_list = []
    coloured_list = []
    if instance_objs_at:
        for item in instance_objs_at:
            to_print_list.append(item.name)
        coloured_list = col_list(to_print_list)

    if coloured_list:
        if print_list:
            slowWriting(coloured_list)
        if return_coloured:
            return coloured_list
    return to_print_list

def add_item_to_container(container:ItemInstance):

    if "container" in container.flags:
        container_size = container.container_limits
        container_size = container_limit_sizes[container_size]

        def get_suitable_items():
            add_x_to = []
            for item in game.inventory:
            ## get items in inventory that are small enough to fit (use item_size)
                item_size = item.item_size
                item_size = container_limit_sizes[item_size]
                if item_size < container_size:
                    #print(f"Item size {item}, {item_size}, < container size {container.name}, container_size: {container_size}")
                    add_x_to.append(item)
                    inv_list, _ = generate_clean_inventory(add_x_to)
            return inv_list, add_x_to

        done=False
        while not done:
            inv_list, add_x_to = get_suitable_items()
            test = option(inv_list, preamble=f"Choose an object to put inside {assign_colour(container, switch=True)} or hit enter when done:", print_all=True)
            if test == "" or test == None:
                done=True
            if test in inv_list:
                instance = from_inventory_name(test, add_x_to)
                result = [(f"Added [child] to [new_container]", assign_colour(instance), assign_colour(container))]
                clean_separation_result(result, to_print=True)
                registry.move_item(instance, new_container=container)


def do_action(trial:str, inst:ItemInstance|str)->list:

    if "remove " in trial:

        if isinstance(inst,str):
            parent = from_inventory_name(inst)

        elif isinstance(inst,ItemInstance):
            parent = inst
        else:
            parent=None

        child = trial.replace("remove ", "")

        inventory, _ = separate_loot(child_input=child, parent_input=parent)

        return inventory


    elif "add to" in trial:

        add_item_to_container(inst)

        # currently not tracking how 'full' a container is, so implement that and then check against it.
        # then list any items that would fit and let user choose from that list, and then add that to the container and remove from open inventory. (though currently, open inventory includes in-container items.)
        ##TODO ooh. I should stop listing child items in the inventory and just have inventory marked with '<item>*' if it contains something (and the something is known about (so not wallet* if we haven't looked in it yet, etc.))

    elif "drop" in trial:
        drop_loot(named=inst)

    elif "pick up" in trial:
        _, test_inventory = registry.pick_up(inst, game.inventory, game.place, game.facing_direction)
        if test_inventory != None:
            game.inventory = test_inventory
            return game.inventory

    elif "read" in trial:

        details = inst.name + "_details"
        details = details.replace(" ", "_")
        details_data = detail_data.get(details)
        if details_data:
            if details_data.get("is_tested"):
                print("Need to roll the dice here to determine outcome.")
            else:
                details_str = details_data.get("print_str")
                do_print(assign_colour(details_str, "b_yellow"))

        while True:
            test = option("read a while", "continue", preamble="You can sit and read a while if you like, or continue and carry on.")
            if test == "" or test == None or test in ("continue", "carry on"):
                break
            if test in "read a while" or test in "read":
                print("Randomly pick a number of hours/time-parts to wait, then wait them.")
                print("And there should be some kind of benefit to this. And/or deciding how long to read for.")
#                inst.times_read +=1 # doesn't exist yet but something like this might be good. Can read each thing x times (maybe varying based on the book/type) before it stops giving you value and only spends time.
                break

    else:
        print(f"No routing found for {trial} for {inst}")
        exit()


def item_interaction(inst:str, inventory_names:list=None, no_xval_names:list=None):

    if isinstance(inst, str):
        test=from_inventory_name(inst, game.inventory)
        if test:
            inst=test
        else:
            test = registry.instances_by_name(inst)[0]
            if test:
                inst=test

    if not isinstance(inst, ItemInstance):
        print(f"Is not an instance. Something is wrong. `{inst}`, type: {type(inst)}")
        exit()

    desc = registry.describe(inst, caps=True)
    if desc and desc != "" and desc != f"[DESCRIBE] No such item: {inst}":
        slowWriting((f"Description: {assign_colour(desc, "description")}"))
    else:
        slowWriting(f"Not much to say about the {inst}.")

    children_val = False
    multiple_val = False

    if inventory_names != None and no_xval_names != None:
        special_names = list(set(inventory_names) - set(no_xval_names))
        for item in special_names:
            plain_name, name_type = check_name(item)
            if name_type == 1:
                test_inst = from_inventory_name(plain_name, game.inventory)
                if test_inst == inst:
                    children_val = registry.instances_by_container(inst)

            elif name_type > 1:
                if plain_name == inst.name:
                    multiple_val = name_type
                    do_print(f"You currently have {multiple_val} {plain_name}s") # hardcoded simple plural 's', will upgrade it later.

    ### TODO: Possibly if >1 (or >2) children, make the action 'remove item', with submenu of children, instead of a big long list. Not necessary at this point at all but worth thinking about.

    actions = registry.get_actions_for_item(inst, game.inventory, has_children=children_val, has_multiple=multiple_val)

    while True:
        trial = None
        trial = option(actions, print_all=True, preamble=f"\n{assign_colour("Actions available for ", "yellow")}{assign_colour(inst)}: ")
        if trial in actions: ## currently this is case sensitive. Need to fix that.
            # TODO: a 'compare input to options' function that deals with case sensitivity. Put it in misc_utilities so it can be used everywhere.
            test_inventory = do_action(trial, inst) ## added so I don't accidentally wipe game.inventory if something fails.
            if test_inventory != None:
                game.inventory = test_inventory
            actions = registry.get_actions_for_item(inst, game.inventory)
            if "drop" in trial:
                break

        if trial == "" or trial is None:
            break

    return trial


def do_inventory():
    done=False
    while done == False:
        slowWriting("INVENTORY: ")
        test=None
        inventory_names = no_xval_names = None
        inventory_names, no_xval_names = generate_clean_inventory(game.inventory, will_print=True, coloured=True, tui_enabled=enable_tui)
        #print(f"inventory names: {inventory_names}")
        do_print(" ")
        do_print("Type the name of an object to examine it, or hit 'enter' to continue.")

        test=user_input()
        if not test or test=="" or test==None:
            do_print("Continuing.")
            break
        if test and (test in inventory_names or test in no_xval_names):
            trial = item_interaction(test, inventory_names, no_xval_names)
        elif test == "drop_done" or test == "done":
            do_print("Continuing.")
            break
        else:
            do_print(f"`{test}` is not a valid input. Please try again or hit enter to continue.")

def god_mode():

    attr_dict={
        "time":time_of_day,
        "weather":list(weatherdict.keys())
    }

    slowLines("God mode: set game.[] parameters during a playthrough. For a print of all game.[] parameters, type 'game_all. Otherwise, just type the change you wish to make.")

    while True:
        text=do_input()
        if "game_all" in text:
            do_print("Trying to print all attr of 'game' class: ")
            attributes = [attr for attr in dir(game)
              if not attr.startswith('__')]
            do_print(f"attributes: {attributes}")
        if "print" in text:
            text=text.replace("print ", "")
            obj = getattr(game, text)
            if type(obj) == str:
                obj = attr_dict.get(obj)
            do_print(obj)

        if "game." in text:
            textstart, value=text.split("=")
            do_print(f"Text: {text}, textstart: {textstart}, value: {value}")
            if textstart in ("game.time", "game.weather", "game.place"):
                try:
                    if "time" in textstart:
                        game.time=value
                        do_print(f"{textstart} has been set: game.time: {game.time}")
                    if "weather" in textstart:
                        game.weather=value
                        do_print(f"{textstart} has been set: game.weather: {game.weather}")
                    if "place" in textstart:
                        game.place=value
                        do_print(f"{textstart} has been set: {assign_colour(game.place, 'loc')}")
                except Exception as e:
                    do_print(f"Cannot set {text}: {e}.")
        if "done" in text or text == "":
            do_print("Returning to game with changes made.")
            break

def instance_name_in_inventory(inst_name:str)->ItemInstance:

    item_entry = registry.instances_by_name(inst_name)
    if item_entry:
        if isinstance(item_entry, list):
            for i, entry in enumerate(item_entry):
                if item_entry[i] not in game.inventory:
                    entry = item_entry[i]
    if entry:
        return entry
    print(f"Did not find entry for {inst_name}")
    input()


def user_input():
    text = do_input()
    if text != None:
        text=text.strip()
    if text.lower() == "godmode":
        do_print("Allowing input to set parameters. Please type 'done' or hit enter on a blank line when you're finished.")
        god_mode()
        do_print()
        return "done"
    if text.lower() == "help":
        do_print()
        slowWriting(f"  Type the (highlighted) words to progress, 'i' for 'inventory', 'd' to describe the environment, 'settings' to set some settings - that's about it.")
        do_print()
        return "done"
    if text.lower()== "settings":
        do_print()
        do_print("Settings:")
        init_settings(manual=True)
        do_print()
        return "done"
    if text.lower() == "stats":
        do_print()
        do_print(f"    weird: {game.weirdness}. location: {assign_colour(game.place, 'loc')}. time: {game.time}. weather: {game.weather}. checks: {game.checks}")
        inventory_names = get_inventory_names(game.inventory)
        do_print(f"    inventory: {inventory_names}, carryweight: {game.carryweight}")
        pprint(f"    {game.player}")
        do_print()
        return "done"
    if text.lower() == "i":
        do_print()
        do_inventory()
        return "inventory_done"
    if text.lower() == "d" or text.lower() == "description": ##TODO: make this a function instead of having it here. This is silly.
        loc_data = p_data[game.place]
        do_print(assign_colour(f"[ Describe location. ]", "yellow"))
        slowWriting(f"[{assign_colour(smart_capitalise(game.place), 'loc')}]  {loc_data.overview}")
        obj = getattr(p_data[game.place], game.facing_direction)
        slowWriting(f"You're facing {assign_colour(game.facing_direction)}. {obj}")
        do_print()
        do_print(f"{places[game.place].description}")#{descriptions[game.place].get('description')}")
        is_items = get_items_at_here(print_list=False)
        if is_items:
            do_print(assign_colour("You see a few scattered objects in this area:", "b_white"))
            get_items_at_here(print_list=True)
        return "done"
    if text.lower().startswith("drop "):
        #do_print(f"Text starts with drop: {text}")
        textparts=text.split()[1:]
        #do_print(f"textparts: {textparts}, len: {len(textparts)}")
        if len(textparts) > 1:
            textparts = " ".join(textparts[0:])
        else:
            textparts = textparts[0]
        item = instance_name_in_inventory(textparts)
        if item:
            drop_loot(item)
        return "drop_done"
    if text and text.lower() in ("exit", "quit", "stop", "q"):
        # Should add the option of saving and returning later.
        ##TODO: Need to work on this. Not urgently, but I'd at least like the setup done so it's an option conceptually; pretty much save everything in game, registry and item_management (or at least the data required to reconstruct). Will be a project in itself. Maybe tomorrow.

        do_print("Okay, bye now!")
        exit()
    else:
        return text

def option(*values, no_lookup=None, print_all=False, none_possible=True, preamble=None, inventory=False, look_around=False):

    values = [v for v in values if v is not None]
    option_chosen = False
    #print(f"Values: {values}, type: {type(values)}")

    def get_formatted(values):
        if inventory:
            values = game.inventory

        formatted = []
        for i, v in enumerate(values):
            if v == None or v == []:
                continue
            if isinstance(v, (list, tuple)):
                if v == None:
                    continue
                if print_all:
                    v=col_list(v)
                    formatted.append(f"{', '.join(v)}")
                else:
                    formatted.append(f"{assign_colour(v[0])}")
            else:
                formatted.append(f"{assign_colour(v, i)}")

        if look_around:
            temp_values = get_items_at_here(print_list=False, return_coloured=False)
            #print(f"temp_values: {temp_values}")
            if temp_values:
                v=col_list(temp_values)
                formatted.append(f"{', '.join(v)}")

        return values, formatted


    values, formatted=get_formatted(values)

    while option_chosen != True:
        if inventory or look_around:
            values, formatted=get_formatted(values)
        if preamble:
            slowWriting(preamble)
        if len(formatted) > 1 and not inventory:
            slowWriting(f"    {', '.join(formatted[:-1])} or {formatted[-1]}")
        elif len(formatted) > 1 and inventory:
            slowWriting(f"    {', '.join(formatted)}")
        else:
            slowWriting(f"    {formatted[0]}")

        if no_lookup:
            return

        clean_values=[]
        if type(values) in (list, tuple, set):
            for value in values:
                if value is not None:
                    if type(value) == str:
                        clean_values.append(value)
                    elif isinstance(value, ItemInstance):
                        clean_values.append(value.name)
                    else:
                        for value_deeper in value:
                            if type(value_deeper) == str:
                                clean_values.append(value_deeper)

        if look_around:
            temp_values = get_items_at_here(print_list=False, return_coloured=False)
            if temp_values:
                for item in temp_values:
                    clean_values.append(item)

        test=user_input()
        if test in ("inventory_done", "description_done", "drop_done"):
            continue
        if none_possible and test=="":
            return None
        if not test or test == "":
            if test is None: ## wtf is this bit
                return None

        if test.isdigit():
            while test.isdigit():
                index = int(test)
                if 1 <= index <= len(clean_values):
                    test = clean_values[index - 1]
                    return test
                do_print(f"{test} is not a valid option, please try again.")
                test=user_input()

        for v in clean_values:
            returning=None
            if len(test) == 1 and test.lower() == v[0].strip().lower():
                returning = v
            elif v.lower() == test.lower():
                returning = v
            elif v.lower().startswith("a ") or v.startswith("a "):
                if v.lower().startswith("a "):
                    new_v = v[2:]
                elif v.lower().startswith("an "):
                    new_v = v[3:]
                if test.lower() == v.strip().lower() or test.lower() == new_v.strip().lower():
                    returning = v
            else:
                if len(test) > 1 and test.lower() == choose.get(v.lower()):
                    returning = v

            if returning:
                return returning

        if test == "stay" and  ("stay here" in values or "stay here" in clean_values):
            return "stay here"
        if test == "go" and ("go elsewhere" in values or "go elsewhere" in clean_values):
            return "go elsewhere"

        if test in no:
            return no
        if test in yes:
            return yes

def roll_risk(rangemin=None, rangemax=None):

    min = 1
    max = 20
    if rangemin:
        min = rangemin
    if rangemax:
        max = rangemax

    results = [
    ((1, 4), "INJURY", 1),
    ((5, 11), "MINOR SUCCESS", 2),
    ((12, 18), "GREATER SUCCESS", 3),
    ((19, 20), "GREATEST SUCCESS!", 4)
    ]

    roll = random.randint(min, max)
    for r, msg, val in results:
        if r[0] <= roll <= r[1] or roll in r:
            if game.show_rolls:
                slowWriting(f"Roll: {roll}\n{msg}")
            return val

def outcomes(state, activity):
    item = None
    ## item needs to be a random item from inventory, droppable. (TODO: Add droppable (or, 'undroppable', probably better) to relevant items so you can't drop anything too important.)
    # Also it needs to be dropped at the location you're currently at.
    very_negative = ["It hurts suddenly. This isn't good...", f"You suddenly realise, your {assign_colour(item)} is missing. Did you leave it somewhere?"]
    negative = [f"Uncomfortable, but broadly okay. Not the worst {activity} ever.", f"Entirely survivable, but not much else to say about this {activity}.", f"You did a {activity}. Not much else to say about it really."]
    positive = [f"Honestly, quite a good {activity}", f"One of the better {activity}-based events, it turns out."]
    very_positive = [f"Your best {activity} in a long, long time."]

    outcome_table = {
        1: very_negative,
        2: negative,
        3: positive,
        4: very_positive
    }

    outcome = random.choice((outcome_table[state]))
    if "is missing. Did" in outcome:
        if not game.inventory:
            dropped = "everything"
        else:
            dropped = random.choice((game.inventory))
            places[game.place].items.append(dropped)
        item = dropped
    return outcome

def drop_loot(named:ItemInstance|str=None, forced_drop=False)->str:

    if forced_drop:
        test = random.choice((game.inventory))
        _, test_inventory = registry.drop(test, switch_the(game.place,replace_with=""), game.facing_direction, game.inventory)
        if test_inventory != None:
            game.inventory = test_inventory
        if enable_tui:
            add_infobox_data(inventory=game.inventory)
        return test

    inventory_names, no_x_val_list = generate_clean_inventory(game.inventory, tui_enabled=enable_tui)
    #inventory_names = get_inventory_names(game.inventory)

    if len(game.inventory) < 1:
        slowWriting("You don't have anything to drop!")
        return None
    if named:
        test=named
    else:
        test = option(inventory_names, print_all=True, preamble="[Type the name of the object you want to leave behind]", inventory=True)
    inst_test=None
    if isinstance(test, ItemInstance):
        inst_test = test
    elif test in inventory_names:
        inst_test=from_inventory_name(test)

    if inst_test != None:
        _, test_inventory = registry.drop(test, switch_the(game.place,replace_with=""), game.facing_direction, game.inventory)
        if test_inventory != None:
            game.inventory = test_inventory
        slowWriting(f"Dropped {assign_colour(test)}.")
    else:
        do_print(assign_colour(f"Error: This item (`{test}`) was not found in the inventory.", colour="red"))

    if enable_tui:
        add_infobox_data(print_data=True, inventory=game.inventory, clear_datablock=True)

    slowWriting("Load lightened, you decide to carry on.")

    if enable_tui:
        add_infobox_data(inventory=game.inventory)

    if game.checks["inventory_asked"] == False:
        slowWriting("[[ Psst. Hey. Type 'secret' for a secret hidden option, otherwise type literally anything else. ]]")
        game.checks["inventory_asked"] = True
        test = user_input()
        if test == "secret":
            test=option("yes", "no", preamble="Hey so... not everyone loves inventory management. So I'll give you the option now - do you want to turn it off and carry without limitation?")
            if test in yes:
                game.player["inventory_management"] = False
                update_settings_json=option("yes", "no", preamble="Do you want to update this for future runs too?")
                if update_settings_json in yes:
                    import json
                    with open("settings.json") as f:
                        data = json.load(f)
                        inventory_state=data["no_inv"]
                        if inventory_state == False and 'yes' in test:
                            data["no_inv"] = True
                        elif inventory_state != False and not 'yes' in test:
                            data["no_inv"] = False

                    with open("settings.json", "w+") as f:
                        json.dump(data, f)
                do_print("Settings updated. Returning.")
        else:
            return

def get_loot(value=None, random=True, named="", message:str=None):
    item=None
    carryweight = game.carryweight
    if named != "" and value == None: # don't add value for location items.
        if isinstance(named, str):
            items_list = registry.instances_by_name()
            for inst in items_list:
                if inst != instance_name_in_inventory(named) and (inst.location == None or (inst.location != None and inst.location == {game.place: game.facing_direction})):
                    ## Does not account for items in containers, which do not have a location but are in a container. So maybe if in container, check if that container is in this location.
                    item_inst=inst
                elif inst.contained_in: ## does this need to be hasattr()? Probably.
                    container = inst.contained_in
                    if container.location == {game.place: game.facing_direction}: ## don't know if this'll work and it only works for one level of parent depth
                        item_inst=inst
                if item_inst == None: # if all else fails,
                    print(f"Failed to find item too much. Defaulting to item[0], {item[0]}")
                    item_inst=item[0]

        # not implemented yet but here for safekeeping. Need to have the description printing respond to it.
            #        print_list[i] = str(spaced_item + " (x2)") ## only allows for a single duplicate but will do for the moment
            #        dupe_list = registry.get_duplicate_details(item, game.inventory) ## not using this yet but want to remember it exists.
            #        print(f"Dupe list: {dupe_list}")
            #        do_print(f"You have {len(dupe_list)} {item}s.") ### This does work. Not useful here, but works.

        elif isinstance(named, ItemInstance):
            item = named

        if not item:
            do_print(f"Failed to check pickupability. Count not get item instance. named: {named}.")

    elif random:
        item = registry.random_from(value)
    else:
        do_print("Not random and no name given. This shouldn't happen, but defaulting to random.")
        do_print(f"value: {value}")
        item = registry.random_from(value)

    if message:
        message = message.replace("[item]", assign_colour(item, None, nicename=registry.nicename(item)))
        message = message.replace("[place]", game.place)
        slowWriting(message)

    if item:
        item_picked_up, game.inventory = registry.pick_up(item, game.inventory) ##
        if item_picked_up:
            slowWriting(f"{assign_colour(item)} added to inventory.")
            if enable_tui:
                add_infobox_data(print_data=True, inventory=game.inventory)
        else:
            do_print(f"Seems you can't pick up {assign_colour(item, switch=True)}")

### drop random item if inventory full // not sure if I hate this. ###
    if len(game.inventory) > carryweight:
        do_print()
        #switched = switch_the(item, 'the ')
        test = option(f"drop", "ignore", preamble=f"It looks like you're already carrying too much. If you want to pick up {assign_colour(item, None, nicename=registry.nicename(item), switch=True)}, you might need to drop something - or you can try to carry it all.")
        if test in ("ignore", "i"):
            slowWriting("Well alright. You're the one in charge...")

            if game.player["encumbered"]:
                outcome = roll_risk()
                if outcome in (1, 2):
                    dropped_item = drop_loot(forced_drop=True) # force drop something.
                    if enable_tui:
                        add_infobox_data(print_data=True, inventory=game.inventory)
                    do_print("You feel a little lighter all of a sudden...")
            if len(game.inventory) > game.carryweight:
                game.player["encumbered"] = True
            else:
                game.player["encumbered"] = False

        else:
            slowWriting("You decide to look in your inventory and figure out what you don't need.")
            drop_loot()
    #do_print()
    return item

def have_a_rest():
    slowWriting("You decide to take it easy for a while.")
    # can do things like read a book, check phone if you have them, daydream (roll for it), etc.
    do_print()
    slowWriting("But after a while, you decide to get up anyway.")
    look_around()

def get_hazard():
    inside = getattr(p_data[game.place], "inside")
    if inside:
        options = trip_over["any"] + trip_over["inside"]
    else:
        options = trip_over["any"] + trip_over["outside"]
    hazard = random.choice(options)
    return hazard

def relocate(need_sleep=None):
    options = []

    current_loc = game.place
    current_weather = game.weather


    time_index=time_of_day.index(game.time)
    new_time_index=time_index + 1 # works
    if new_time_index == len(time_of_day):
        new_time_index=0
    game.time=time_of_day[new_time_index]

    weather_options = list(weatherdict)
    weather_index=weather_options.index(game.weather)
    weather_variance=random.choice([int(-1), int(1)])
    new_weather_index=weather_index + int(weather_variance)
    if new_weather_index == len(weather_options):
        new_weather_index=0
    game.weather=weather_options[new_weather_index]

    while len(options) < 3:
        new_place = random.choice((game.loc_list))
        if new_place not in options: # and new_place != current_loc <- turn on when I don't want current loc as an option anymore.
            options.append(new_place)

    new_location = option(options, print_all=True, preamble="Please pick your destination:")
    if new_location in options:
        game.place=new_location
        load_world(relocate=True, new_loc=new_location)
        if enable_tui:
            update_infobox(location=game.place, weather=game.weather, t_o_d=game.time, day=game.day_number)

    if game.place==current_loc:
        do_print(f"You decided to stay at {assign_colour(switch_the(game.place, 'the'), 'loc')} a while longer.")
    else:
        slowWriting(f"You make your way to {assign_colour(game.place, 'loc')}. It's {game.time}, the weather is {game.weather}, and you're feeling {game.emotional_summary}.")
        if places[game.place].visited:
            slowWriting(f"You've been here before... It was {places[game.place].first_weather} the first time you came.")
            if places[game.place].first_weather == game.weather:
                do_print(weatherdict[game.weather].get("same_weather"))
        else:
            places[game.place].visited = True # maybe a counter instead of a bool. Maybe returning x times means something. No idea what. Probably not.
            places[game.place].first_weather = current_weather

    if need_sleep:
        decision = option("rest", "look", preamble="You're getting exhausted. You can look around if you like but the sleep deprivation's getting to you.")
        if decision == "rest":
            if places[game.place].inside == False:
                sleep_outside()
            else:
                sleep_inside()
        else:
            look_around(status="exhausted")
    else:
        look_around()

def sleep_outside():
    if getattr(p_data[game.place], "nature"):
        slowWriting("You decide to spend a night outside in nature.")
    else:
        slowWriting(f"You decide to spend a night outside in {assign_colour(switch_the(game.place, "the "), 'loc')}.")
    if not game.bad_weather:
        slowWriting("Thankfully, the weather isn't terrible at least.")
        slowWriting("You sleep until morning.")
        the_nighttime()
    else:
        slowWriting(f"Unfortunately, it's {game.weather}")
        slowWriting("You can weather it out (no pun intended) or try a last minute relocation - what do you do?")
        decision = option("stay", "move")
        if decision == "stay":
            risk = roll_risk()
            outcome = outcomes(risk, "sleep")
            slowWriting(outcome)
            slowWriting("Something else happens here. Who knows what. Interactive dream scene.")
            the_nighttime()
        else:
            relocate(need_sleep=True)

def sleep_inside():
    slowWriting(f"Deciding to hunker down in {assign_colour(switch_the(game.place, "the "), 'loc')} for the night, you find the comfiest spot you can and try to rest.")
    risk = roll_risk(10, 21)
    outcome = outcomes(risk, "sleep")
    slowWriting(outcome)
    the_nighttime()

def the_nighttime():
    do_print()
    slowWriting("Finally asleep, you dream deeply.")
    slowWriting("  ...")
    slowWriting("    ...")
    slowWriting("       ...")
    slowWriting("Imagine a dream here. Something meaningful...")
    slowWriting("And/or wild animals if sleeping outside, and/or people, and/or ghosts/monster vibes if weird.")
    new_day()

def location_item_interaction(item_name, local_items=None):

    item_entry = registry.instances_by_name(item_name)
    if item_entry:
        if local_items==None:
            local_items = registry.instances_by_location(game.place, game.facing_direction)
        for item in item_entry:
            if item in local_items and item not in game.inventory:
                ### TODO: and item not in container that is in inventory
                entry = item

        slowWriting((f"Description: {assign_colour(registry.describe(entry, caps=True), "description")}"))

        decision=option("take", "leave", preamble=f"What do you want to do with {assign_colour(item_name, switch=True)} - take it, or leave it alone?")
        if decision == "":
            do_print("Leaving it be.")
        if decision and decision != "" and decision is not None:
            if decision.lower()=="investigate": ## this deep nesting is an issue. Withdrawing from here gets you all the way to 'relocate'.
                do_print("Nothing here yet.")
            elif decision.lower()=="take":
                picked_up = get_loot(value=None, random=True, named=entry, message=None)
                if not picked_up:
                    do_print(f"Seems you can't take {assign_colour(item_name, switch=True)} with you.")

            elif decision.lower()=="leave":
                do_print(f"You decide to leave the {assign_colour(item_name)} where you found it.")
    else:
        do_print(f"No entry found for {item_entry}")

def look_around(status=None):
    item = None
    place = game.place
    time = game.time
    weather = game.weather

    def look_dark():
        if ("torch" or "phone" or "matchstick") not in game.inventory:
            if hasattr(place, "electricity"):
                print(f"Has attr electricity at {place}")
#            if descriptions[place].get("electricity"):
                test=option("yes", "no", preamble="It's dark, but you can try to find a light switch if you want.")
                if test in yes:
                    outcome = roll_risk()
                    if outcome in (1, 2):
                        slowWriting("Try as you might, you can't find a lightswitch...")
                    else:
                        slowWriting("The light flickers on - you can see.")
                        look_light(reason="electricity")

            test=option("yes", "no", preamble=f"It's too dark to see much of anything in {assign_colour(switch_the(game.place, "the "), 'loc')}, and without a torch or some other light source, you might trip over something. Do you want to keep looking?")
            if test in yes:
                slowWriting("Determined, you peer through the darkness.")
                outcome = roll_risk()
                if outcome == 1:
                    slowWriting("OW! You roll your ankle pretty badly.")
                    if len(game.inventory) < 4:
                        get_loot(1, random=True, message=f"It's only a minor injury, sure, but damn it stings. You did find [item] while facefirst in the middle of [place], though.")
                    if game.w_value:
                        ("You see something shimmer slightly off in a bush, but by the time you hobble over, whatever it was has vanished.")
                if outcome == 2:
                    hazard = get_hazard()
                    get_loot(1, random=True, message=f"Narrowly avoiding tripping over {hazard}, you find [item]. Better than nothing, but probably all you'll find until there's more light.") # want options for the poorly lit hazard part.
                    # game.carrier_size compared to item.size? Can I be bothered?
                if outcome in (3,4):
                    get_loot(2, random=True, message=f"Once your eyes adjust a bit, you manage to make out more shapes than you expected - you find [item].")
            if test in no:
                slowWriting("Thinking better of it, you decide to keep the advanced investigations until you have more light. What now, though?")
            test = option("stay here", "move on", preamble=f"You could stay and sleep in {assign_colour(switch_the(game.place, "the "), 'loc')} until morning, or go somewhere else to spend the wee hours. What do you do?")
            if test in ("sleep", "stay", "stay here"):
                if places[game.place].inside == False:
                    sleep_outside()
                else:
                    sleep_inside()
            else:
                slowWriting(f"Keeping in mind that it's {time} and {weather}, where do you want to go?")
                print(f"game.place before relocate: {game.place}")
                relocate()

        else:
            slowWriting("Using your torch, you see things. Probably. I haven't written this yet. How do you have a torch?!?")



    def look_light(skip_intro = False, reason=None):
        skip_intro=skip_intro
        if reason == "turning" or reason == "skip_intro":
            skip_intro=True
        elif reason == None:
            reason = "the sun"
        if skip_intro==False: # if there are no other reason to skip intro, can just combine the above into one 'if/else'.
            slowWriting(f"Using the power of {reason}, you're able to look around {assign_colour(switch_the(game.place, "the "), 'loc')} without too much fear of a tragic demise.")
        obj = getattr(p_data[game.place], game.facing_direction)
        #print(f"\n{obj}\n")
        if obj == None or obj == "None":
            do_print("This description hasn't been written yet... It should have some ")
            exit()
        else:
            do_print(f"\n  You're facing {assign_colour(game.facing_direction)}. {obj}\n")
        remainders = list(x for x in game.cardinals if x is not game.facing_direction)

        potential = get_items_at_here(print_list=False, return_coloured=False)

        text=None
        is_done=False

        while not text and is_done == False:
            text=option(remainders, "leave", no_lookup=None, print_all=True, preamble="You can look around more, leave, or try to interact with the environment:", look_around=True)

        if text == "leave":
            slowWriting(f"You decide to move on from {assign_colour(switch_the(game.place, "the "), 'loc')}")
            relocate()
        if text != "" and text is not None:
            if text in remainders:

                game.facing_direction=text
                remainders = list(x for x in game.cardinals if x is not game.facing_direction)
                look_light("turning")

            local_items = get_items_at_here(print_list=False, return_coloured=False)
            if local_items and text in local_items: # have changed this, it may be broken
                location_item_interaction(text)

            else:
                do_print(f"Could not find what you're looking for. The options: {potential}")

        slowWriting("Unfortunately I haven't written anything here yet. Maybe just... go somewhere else?")
        slowWriting(f"Keeping in mind that it's {time} and {weather}, where do you want to go?")
        relocate()

    if status == "exhausted" and time not in night:
        slowWriting("Stumbling, you're going to hurt yourself even if it's nice and bright. Haven't written it yet though.")
        look_dark()

## ==== Actual start here ===
    inside = getattr(p_data[game.place], "inside")
    if inside:
        add_text="outside "
    else:
        add_text=""
    slowWriting(f"With the weather {add_text}{game.weather}, you decide to look around the {game.facing_direction} of {assign_colour(switch_the(game.place, 'the '), 'loc')}.")
    if time in night:
        slowWriting(f"It's {game.time}, so it's {random.choice(emphasis["low"])} dark.")
        look_dark()
    else:
        look_light("skip_intro")

def new_day():

    if game.loop==False:
        decision = option("yes", "no", preamble="Keep looping?")
        if decision in no:
            slowWriting("Hope you had fun? Not sure really what this is, but thank you.")
            exit()

    game.checks["play_again"]
    game.time = random.choice(["pre-dawn", "early morning", "mid-morning"])
    inner_loop()

def describe_loc():

    loc_data = p_data[game.place]
    slowWriting(f"You take a moment to take in your surroundings. {loc_data.overview}")
    test=option(game.cardinals, "go elsewhere", print_all=True, preamble="Pick a direction to investigate, or go elsewhere?")
    ## TODO: I miss when it used to print 'chosen: (go elsewhere)' if I entered 'g'. Need to get that back.
    if test in game.cardinals:
        game.facing_direction = test
        look_around()
    else:
        slowWriting(f"You decide to leave {assign_colour(switch_the(game.place, 'the '), 'loc')}")
        relocate()

def inner_loop(speed_mode=False):

    places[game.place].visited = True
    places[game.place].first_weather = game.weather

    if not speed_mode:
        slowWriting(f"You wake up in {assign_colour(game.place, 'loc')}, right around {game.time}. You find have a bizarrely good sense of cardinal directions; how odd.")
        slowWriting(f"`{game.playername}`, you think to yourself, `is it weird to be in {assign_colour(game.place, 'loc')} at {game.time}, while it's {game.weather}?`")
        do_print()
        describe_loc()

    test=option("stay here", "go elsewhere", preamble="What do you want to do? Stay here and look around, or go elsewhere?")
    if test in ("stay", "stay here", "look"):
        slowWriting("You decide to look around a while.")
        look_around()
    else:
        relocate()

def intro():

    #First run setup
    # ascii from https://patorjk.com/software/taag/#p=display&f=Big+Money-ne&t=paths&x=none&v=4&h=4&w=80&we=false
    do_print("\n")
    slowLines("                          /================================ #")
    slowLines("                         /                                  #")
    slowLines("   # ===================/     /$$     /$$                   #")
    slowLines("   #                         | $$    | $$                   #")
    slowLines("   #     /$$$$$$   /$$$$$$  /$$$$$$  | $$$$$$$   /$$$$$$$   #")
    slowLines("   #    /$$__  $$ |____  $$|_  $$_/  | $$__  $$ /$$_____/   #")
    slowLines(r"   #   | $$  \ $$  /$$$$$$$  | $$    | $$  \ $$|  $$$$$$    #")
    slowLines(r"   #   | $$  | $$ /$$__  $$  | $$ /$$| $$  | $$ \____  $$   #")
    slowLines("   #   | $$$$$$$/|  $$$$$$$  |  $$$$/| $$  | $$ /$$$$$$$/   #")
    slowLines(r"   #   | $$____/  \_______/   \___/  |__/  |__/|_______/    #")
    slowLines("   #   | $$                                                 #")
    slowLines("   #   | $$       /======================================== #")
    slowLines("   #   |__/      /")
    slowLines("   #            /")
    slowLines("   # ==========/")
    do_print("\n")
    do_print("To play: ")
    do_print("Type the words in parentheses, or select by number")
    do_print("    eg: for [[  (stay) or (go))  ]], '1' would choose 'stay'.")


def add_rocks():
    rock, game.inventory = registry.pick_up("pretty rock", game.inventory)
    print(f"Rock: {rock}")
    print(f"Rock description: {rock.description}")
    print(f"Proper description: {registry.describe(rock, caps=True)}")

def run():

    system("cls")

    test_mode=True
    if test_mode:
        playernm = "Testbot"
    else:
        intro()
        do_print()
        slowWriting("What's your name?")
        playernm = do_input()
    global game
    game = set_up(weirdness=True, bad_language=True, player_name=playernm)

    system("cls")

    if enable_tui:
        from tui_elements import run_tui_intro
        player_name = run_tui_intro(play_intro=False)

        if player_name:
            game.playername = player_name

        world = (game.place, game.weather, game.time, game.day_number)
        player = (game.player, game.carryweight, game.playername)
        add_infobox_data(print_data = True, backgrounds = False, inventory=None, playerdata=player, worldstate=world)
        print_commands(backgrounds=False)
        update_infobox(hp_value=game.player["hp"], name=game.playername, carryweight_value=game.carryweight, location=game.place, weather=game.weather, t_o_d=game.time, day=game.day_number)

        add_infobox_data(print_data = True, inventory=game.inventory)

    ## Add glass jar to inventory for container tests
    #game.carryweight += 5
    #inst = registry.instances_by_name("glass jar")
    #_, game.inventory = registry.pick_up(inst, game.inventory)

    if not test_mode:
        slowWriting("[[ Type 'help' for controls and options. ]]")
        do_print()

    from misc_utilities import compare_input_to_options
    outcome, alignment = compare_input_to_options(game.inventory, game.player, input="paperclip")
    outcome_ref = alignment.get(outcome)
    print(f"outcome: {outcome}, alignment: {outcome_ref}")
    ## Okay. So this gives me an instance obj not just from inventory, but from the available options. I really like this.

    exit()
    inner_loop(speed_mode=test_mode)

system("cls")
sleep(1)
run()

