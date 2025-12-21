# loot.name_col(item) == adding col to class
# assign_colour(text) == to print w colour

import choices
import env_data
from misc_utilities import assign_colour, col_list, switch_the, generate_clean_inventory, get_inventory_names
from set_up_game import load_world, set_up, init_settings
from choices import choose
import random
from locations import run_loc, places
from env_data import placedata_init, p_data
from pprint import pprint
import time

from item_management_2 import ItemInstance, registry

from tui_elements import run_tui_intro
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

enable_tui=False

def slowLines(txt, speed=0.1, end=None, edit=False):
    if isinstance(txt, str) and txt.strip=="":
        edit=True
    update_text_box(to_print=txt, end=False, edit_list=edit, use_TUI=enable_tui)
    update_text_box(to_print="  ", end=False, use_TUI=enable_tui)

def do_input():

    print(SHOW, end='')
    print("About to hit do_input edit")
    text=input()
    print("Just ended text input.")
    print(HIDE, end='')
    do_print(edit_list=True)
    if text == "" or text == None:
        slowLines(" ")
        #update_text_box(to_print=[f" "])
    else:
        slowLines(f"{assign_colour(f'Chosen: ({text.strip()})', 'yellow')}")
    return text

def do_print(text=None, end=None, edit_list=False):
    if text==None:
        text=" "
    slowLines(txt=text, speed=0.1, end=end, edit=edit_list)

def slowWriting(txt, speed=0.001, end=None, edit=False): # Just keeping this here for now as a way to maintain that once, these calls were different from the line prints.
    slowLines(txt, speed, end, edit)

def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s

def separate_loot(child_input=None, parent_input=None): ## should be inside registry, not here.

    child = None
    parent = None
    for item in (parent_input, child_input):
        if item:
            if isinstance(item, ItemInstance):
                continue
            if isinstance(item, str):
                items = registry.instances_by_name()
                for inst in game.inventory:
                    if inst in items:
                        if item == parent:
                            parent=inst
                        elif item == child:
                            child = inst
                        break

    if parent and not child:
        children = registry.instances_by_container(parent)
        #or
        children = parent.children # < Seems much more straightforward. Any downside?

        if children:
            for item in children:
                registry.move_item(inst=item, place=game.place, direction=game.facing_direction, new_container=None)
                print("Add children to inventory etc")
                ## TODO: this

    elif child and not parent:
        parent = child.contained_in


    #entry = loc_loot.get_item(item)
    if item:
        if item.get('children'):
            for child in item['children']:
                game.inventory.append(child)
                do_print(f"{child} separated from {item}")


def get_items_at_here(print_list=False, return_coloured=True):

    instance_objs_at = (registry.instances_at(switch_the(game.place, replace_with=""), game.facing_direction))
    print_list = []
    coloured_list = []
    if instance_objs_at:
        for item in instance_objs_at:
            print_list.append(item.name)
        coloured_list = col_list(print_list)

    if coloured_list:
        if print_list:
            slowWriting(coloured_list)
        if return_coloured:
            return coloured_list
    return print_list


def from_inventory_name(inst_inventory, test): # works now with no_xval_names to reference beforehand.

    cleaned_name = test.split(" x")[0]

    for inst in inst_inventory:
        if inst.name == cleaned_name:
            return inst

    print(f"Could not find inst `{inst}` in inst_inventory.")
    input()

def do_inventory():
    done=False
    slowWriting("INVENTORY: ")
    while done == False:
        test_raw=None
        test=None
        inventory_names, no_xval_names = generate_clean_inventory(game.inventory, will_print=True, coloured=True, tui_enabled=enable_tui)
        do_print(" ")
        do_print("Type the name of an object to examine it, or hit 'enter' to continue.")
        test_raw=user_input()
        if test_raw:
            test = test_raw.split(" x")[0]
        if not test or test=="" or test==None:
            do_print("Continuing.")
            break
        if test and (test in inventory_names or test in no_xval_names):
            test=from_inventory_name(game.inventory, test)
            desc = registry.describe(test, caps=True)
            if desc and desc != "" and desc != f"[DESCRIBE] No such item: {test}":
                slowWriting((f"Description: {assign_colour(desc, "description")}"))
            else:
                slowWriting(f"Not much to say about the {test}.")
        if test == "drop_done" or test == "done":
            do_print("Continuing.")
            break
        else:
            do_print(f"`{test}` is not a valid input. Please try again or hit enter to continue.")

def god_mode():

    attr_dict={
        "time":choices.time_of_day,
        "weather":list(env_data.weatherdict.keys())
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


def user_input():
    text = do_input()
    if text != None:
        text=text.strip() # this should solve the issues of leading spaces altogether.
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
        item = registry.instances_by_name(textparts)
        if item:
            item=item[0]
            #do_print(f"Sending item to drop: {item}") ## always drops the first. This needs to check for dupes too. Maybe do that internally in item_management. Probably better.
            drop_loot(item)
        return "drop_done"
    if text and text.lower() in ("exit", "quit", "stop", "q"):
        # Should add the option of saving and returning later.
        ##TODO: Need to work on this. Not urgently, but I'd at least like the setup done so it's an option conceptually; pretty much save everything in game, registry and item_management (or at least the data required to reconstruct). Will be a project in itself. Maybe tomorrow.

        do_print("Okay, bye now!")
        exit()
    else:
        return text

def option(*values, no_lookup=None, print_all=False, none_possible=True, preamble=None, inventory=False):

    values = [v for v in values if v is not None]
    option_chosen = False

    def get_formatted(values):
        if inventory:
            values = game.inventory ## force use the actual inventory instead of the list values.

        values = [v for v in values if v != None]
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
        return values, formatted

    values, formatted=get_formatted(values)

    while option_chosen != True:
        if inventory:
             values, formatted=get_formatted(values)
        if preamble:
            slowWriting(preamble)
        if len(formatted) > 1 and not inventory:
            slowWriting(f"    ({', '.join(formatted[:-1])}) or {formatted[-1]}")
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
                        #f value.startswith("\\x1b") or value.startswith("\\033"):
                            #value = value.strip()--- ### TODO: Replace with regex so the values we're selecting from are the uncoloured versions. I don't know why it's colouring them in advance.
                    elif isinstance(value, ItemInstance):
                        clean_values.append(value.name)
                    else:
                        for value_deeper in value:
                            if type(value_deeper) == str:
                                clean_values.append(value_deeper)

        #print(f"values: {values}, clean_values: {clean_values}")

        test=user_input()
        #print(f"test: {test}")
        if test in ("inventory_done", "description_done", "drop_done"):
            if test == "drop_done":
                #inventory_names = get_inventory_names(game.inventory) ## not sure why this is here.
                values=game.inventory ## should this be 'inventory_names'? Or should it be here at all? I guess so, so it can clean them from instances. Though that'll break... Yes. Okay I need to do the get_names here so it maintains the proper integrity of multiples etc.
            continue
        if none_possible and test=="":
            return None
        #print(f"Test: {test}")
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
                #print(f"RETURNING: {returning}")
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

def drop_loot(named=None, forced_drop=False):

    inventory_names = get_inventory_names(game.inventory)
    if forced_drop:
        test = random.choice((game.inventory))
        _, game.inventory = registry.drop(test, switch_the(game.place,replace_with=""), game.facing_direction, game.inventory)
        if enable_tui:
            add_infobox_data(inventory=game.inventory)
        return

    if named:
        test=named
    else:
        if len(game.inventory) < 1:
            slowWriting("You don't have anything to drop!")
            return
        test = option(inventory_names, print_all=True, preamble="[Type the name of the object you want to leave behind]", inventory=True)

    if test in inventory_names or isinstance(test, ItemInstance):
        if isinstance(test, ItemInstance):
            item_test=test
        else:
            do_print(f"Test in inventory names: {test}")
            item_test=from_inventory_name(test)

        if item_test in game.inventory:
            _, game.inventory = registry.drop(test, switch_the(game.place,replace_with=""), game.facing_direction, game.inventory)
            inventory_names.remove(item_test.name)
            do_print(f"test from inventory name: {test}")
            slowWriting(f"Dropped {assign_colour(test)}.")
        else:
            do_print(assign_colour("Error: This item was not found in the inventory.", colour="red"))

    # paperclip (x2)
    # Chosen: (paperclip)
    # Dropped paperclip.
    ## automatically just drops one. Wasn't sure if it would, but that's nice. Weird that it places it in a later spot, but I guess it drops the first one, so the second one is suddenly shown in its 'original' position (just before it wasn't shown because it was in the symbolic 2x). So might have to make it remove the last one it finds instead, so the 'x2' just turns into 'paperclip', instead of 'paperclip (x2)' disappearing and a new 'paperclip' appearing elsewhere. Doesn't matter but it'd be better.

    ## ALSO:

    #  Chosen: (drop paperclip)
    #  Error: This item was not found in the inventory.

#        --  despite the dual paperclips being reduced in the list to a single one, that single one apparently isn't found.

    if enable_tui:
        add_infobox_data(print_data=True, inventory=game.inventory, clear_datablock=True) ## clear the inventory window first, then print the new list

    slowWriting("Load lightened, you decide to carry on.")
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

    # get_inventory_names() # I think this was just here because I had to rebuild game.inventory_names. Now I fetch it manually when rebuilt + needing to print, so this call isn't necessary. Probs the same w/ the one inside option()
    if enable_tui:
        add_infobox_data(inventory=game.inventory)

#def switch_the(text, replace_with=""): # remember: if specifying the replace_with string, it must end with a space. Might just add that here actually...
#    if isinstance(text, list):
#        if len(text) == 1:
#            text=text[0]
#            text=text.name
#        else:
#            do_print("Trying to `switch_the`, but text is a list with more than one item.")
#            exit()
#    if isinstance(text, ItemInstance):
#        text=text.name
#    for article in ("a ", "an "):
#        if text.startswith(article):# in text:
#            if replace_with != "":
#                #print(f"replace with isn't blank: `{replace_with}`")
#                if replace_with[-1] != " ":
#                    #print(f"replace with doesn't end with a space: `{replace_with}`")
#                    replace_with = replace_with + " "
#                    #print(f"replace with should now have a space: `{replace_with}`")
#            text = text.replace(article, replace_with) # added 'replace with' so I can specify 'the' if needed. Testing.
#
#
#    if replace_with == "" or replace_with == None: # should only trigger if neither article is in the text. This might need testing.
#        text = "the "+ text # so I can add 'the' in front of a string, even if it doesn't start w 'a' or 'an'.
#    return text

def move_item_any(item):
    game.inventory.append(item)
    slowWriting(f"[[ `{assign_colour(item)}` added to inventory.")

def get_loot(value=None, random=True, named="", message:str=None):
    item=None
    carryweight = game.carryweight
    #print(f"in get_loot: value: {value}, random: {random}, named: {named}, message: {message}")
    if named != "" and value == None: # don't add value for location items.
        #do_print(f"Named in get_loot, about to go to pick_up_test: `{named}`, type: {type(named)}")
        if isinstance(named, str):
            items_list = registry.instances_by_name(named)
            if isinstance(items_list, list) and len(items_list) == 1: ## it'll be this for anything with a default location. The rest only applies to things that are moved or dropped, really. So I can't test it until 'dropped' adds it to the world in a way this script recognises. So I need to change 'describe location' to use registry.by_location, so it recognises dropped items.
                item=items_list[0]
            else:
                for inst in items_list:
                    if inst not in game.inventory and (inst.location == None or (inst.location != None and inst.location == {game.place: game.facing_direction})):
                        ## Does not account for items in containers, which do not have a location but are in a container. So maybe if in container, check if that container is in this location.
                        item_inst=inst
                    elif inst.contained_in: ## does this need to be hasattr()? Probably.
                        container = inst.contained_in
                        if container.location == (game.place, game.facing_direction): ## don't know if this'll work and it only works for one level of parent depth
                            item_inst=inst
                if item_inst == None: # if all else fails,
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
        item_picked_up, game.inventory = registry.pick_up(item, game.inventory, game.place, game.facing_direction) ##
        if item_picked_up:
            slowWriting(f"{assign_colour(item)} added to inventory.") ## Doesn't check if a thing can be picked up. This plays even after "Item cannot be picked up.".
            if enable_tui:
                add_infobox_data(print_data=True, inventory=game.inventory) ### Not sure exactly why but: TODO:: This print didn't add a new one, instead overwriting the previously added item.

    #move_item_any(item)

### drop random item if inventory full // not sure if I hate this. ###
    if len(game.inventory) > carryweight:
        do_print()
        #switched = switch_the(item, 'the ')
        test = option(f"drop", "ignore", preamble=f"It looks like you're already carrying too much. If you want to pick up {assign_colour(item, None, nicename=registry.nicename(item), switch=True)}, you might need to drop something - or you can try to carry it all.")
        if test in ("ignore", "i"):
            slowWriting("Well alright. You're the one in charge...")

            if game.player["encumbered"]: # 50/50 chance to drop something if already encumbered and choose to ignore
                outcome = roll_risk()
                if outcome in (1, 2):
                    #print(f"Forced to drop something.") #TODO: remove this later.
                    drop_loot(forced_drop=True) # force drop something.
                    if enable_tui:
                        add_infobox_data(print_data=True, inventory=game.inventory) ## TODO: Need to clear this first, otherwise it overwrites in an awful way. Also set a limiter on how many lines it can write on, even if the inventory is more than that.
                    do_print("You feel a little lighter all of a sudden...") ## does not add the item to the location yet. Have to do that.
            if len(game.inventory) > game.carryweight:
                game.player["encumbered"] = True
            else:
                game.player["encumbered"] = False

        else:
            slowWriting("You decide to look in your inventory and figure out what you don't need.")
            drop_loot()
    do_print()
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
        options = choices.trip_over["any"] + choices.trip_over["inside"]
    else:
        options = choices.trip_over["any"] + choices.trip_over["outside"]
    hazard = random.choice(options)
    return hazard

def relocate(need_sleep=None):
    options = []

    current_loc = game.place
    current_weather = game.weather

    times_of_day = choices.time_of_day
    time_index=times_of_day.index(game.time)
    new_time_index=time_index + 1 # works
    if new_time_index == len(times_of_day):
        new_time_index=0
    game.time=times_of_day[new_time_index]

    weather_options = list(env_data.weatherdict)
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

    if game.place==current_loc:
        do_print(f"You decided to stay at {assign_colour(switch_the(game.place, 'the'), 'loc')} a while longer.")
    else:
        slowWriting(f"You make your way to {assign_colour(game.place, 'loc')}. It's {game.time}, the weather is {game.weather}, and you're feeling {game.emotional_summary}.")
        print(f"places: {places}")
        print(f"game.place: {game.place}")
        if places[game.place].visited:
            slowWriting(f"You've been here before... It was {places[game.place].first_weather} the first time you came.")
            if places[game.place].first_weather == game.weather:
                do_print(places[game.place].same_weather)
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
    do_print()
    slowWriting("    ...")
    do_print()
    slowWriting("       ...")
    do_print()
    slowWriting("Imagine a dream here. Something meaningful...")
    slowWriting("And/or wild animals if sleeping outside, and/or people, and/or ghosts/monster vibes if weird.")
    new_day()

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
                        #slowWriting(f"It's only a minor injury, sure, but damn it stings. You did find {item} while facefirst in the middle of {place}, though.") # don't need these two lines. Need to combine them into just the loot message..
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
            do_print(f"\n  You're facing {assign_colour(game.facing_direction)}. {obj}\n") # so it fails to print exclusively if not obj.
        remainders = list(x for x in game.cardinals if x is not game.facing_direction)
        #print(f"Directions to look: {remainders}")

        potential = get_items_at_here(print_list=False, return_coloured=False) ## I hate that these are alphabetical now instead of their original order. TODO: see if I can fix?

        text=None
        is_done=False

        while not text and is_done == False:
            #print(f"Remainders: {remainders}, potential: {potential}")
            text=option(remainders, "leave", potential, no_lookup=None, print_all=True, preamble="You can look around more, leave, or try to interact with the environment:")

# okay the issue of 'north, east, south, leave or  ' is because:

       ## INPUT:  Values: [['south', 'east', 'west'], 'leave', []], formatted: ['\x1b[1;34msouth\x1b[0m, \x1b[1;36meast\x1b[0m, \x1b[1;35mwest\x1b[0m', '\x1b[1;34mleave\x1b[0m', '']                 mgo elsewhere\x1b[0m']

# it applies colour even if null, which then means the value is not None so is not discarded.


        if text == "leave":
            slowWriting(f"You decide to move on from {assign_colour(switch_the(game.place, "the "), 'loc')}")
            relocate()
        if text != "" and text is not None:
            if text in remainders: ## this doesn't seem to be working.
    ### More specifically, it seems like once you've chosen a direction or an object, you're stuck in that mode. So if you're looking east and you interact with your inventory, you get shown the options to go in a direction, but it treats it as null input and just asks you again, without turning.

#  Finally figured out why, I think:

#
#         File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 765, in look_light
#           if text in remainders: ## this doesn't seem to be working.
#           ^^^^^^^^^^^^^^^^^^^^^
#         [Previous line repeated 5 more times]
#         File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 777, in look_light
#           #print(f"loc loot: {loc_loot}")
#       TypeError: 'NoneType' object is not subscriptable


                game.facing_direction=text
                remainders = list(x for x in game.cardinals if x is not game.facing_direction)
                look_light("turning") # run it again, just printing the description of where you turned to.
            if text in obj or text in potential:
                #print(f"Text: {text}, obj: {obj}")
                if text in list(potential):
                #for option_entry in options: ## 'if text in options', surely?
                #    if text in option_entry: # this gets 'television' if I type 'e'. Not working...
                    #print(f"text just before get_item: {text}")
                    #print(f"loc loot: {loc_loot}")
                    #print(f"text: {text}")
                    #item_entry = getattr(loc_loot[game.place][game.facing_direction], text)

### I need to make sure that obj and item_entry are the same. They should be, but it's weird to get it from place data, no? Surely should be going by item_entry.
                    obj = getattr(p_data[game.place], game.facing_direction)
                    item_entry = registry.instances_by_name(text)

                    item_entry = item_entry[0] ## TODO: Fix this, it's always defaulting to the first one and it shouldn't, will break dupes when they're introduced.
                    #item_entry = registry.get_item(text)
                    #print(f"item entry: {item_entry}")
                    if item_entry:
                        do_print(f"{registry.describe(item_entry, caps=True)}")
                        #print("What do you want to do? [Investigate] item, [take] item, [leave] it alone.") # Do I want to list the options like this, or just try to make a megalist of what options may be chosen and work from that?
                        decision=option("investigate", "take", "leave", preamble=f"What do you want to do with {assign_colour(text, switch=True)} - investigate it, take it, or leave it alone?")



                        #print(f"text after decision: {text}")
                        #decision=user_input()
                        if decision.lower()=="investigate":
                            do_print("Nothing here yet.")
                        elif decision.lower()=="take":
                            #print(f"text in decision lower == take: {text}")
                                ## Might have to change how I do this. Currently, flowers + jar are listed separately from each other, but when picked up are one unit.
                                # Maybe I need to rename the glass jar, if children, glass jar with flowers, otherwise just glass jar when they're separated.
                            picked_up = get_loot(value=None, random=True, named=text, message=None)
                            #if picked_up:
                            #    if text not in game.inventory:
                            #        game.inventory.append(text) # doing this here, so the children aren't added, but are part of the main object.
                            #    #print(f"To set location: {picked_up}, {assign_colour(game.place, 'loc')}, {game.facing_direction}")
                            #    set_items:list = loc_loot.set_location(picked_up, game.place, game.facing_direction, picked_up=True) ## I'm dong this inside get loot too. Shouldn't need todo this, it's silly. ## also it breaks if inventory isn't in local loot immediately.
                            #    for item_name in set_items:
                            #        #print(f"Full list before: {choices.location_loot[game.place][game.facing_direction]}")
                            #        #print("testing: choices.location_loot[game.place][game.facing_direction].pop(picked_up)")
                            #        choices.location_loot[game.place][game.facing_direction].pop(item_name)
                                    #print(f"Full list after: {choices.location_loot[game.place][game.facing_direction]}")
                            #    do_print("[Find the loot taking function that already exists, make sure the item is removed from the list here.]") # does the current loot table allow for 'already picked up'? I don't think it does. Need to do that.
                        elif decision.lower()=="leave":
                            do_print(f"You decide to leave the {assign_colour(text)} where you found it.")



                    else:
                        do_print(f"No entry in loc_loot for {item_entry}")
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
        add_text="outside"
    else:
        add_text=""
    slowWriting(f"With the weather {add_text}{game.weather}, you decide to look around the {game.facing_direction} of {assign_colour(switch_the(game.place, 'the '), 'loc')}.")
    if time in night:
        slowWriting(f"It's {game.time}, so it's {random.choice(choices.emphasis["low"])} dark.")
        look_dark()
    else:
        if places[game.place].sub_places: ## TODO: sub_places doesn't exist in this format. I imagine this was supposed to be the cardinals, but I'd not implemented it yet. I think this is just old code I never noticed because I'm usually in graveyard and/or at night, so this doesn't apply.
            for sub_place in places[game.place].sub_places:
                do_print(f"[[[[  sub_place: {sub_place}  ]]]]")
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

def run():

    do_print("\n \n")
    global game
    run_loc()
    placedata_init()
    rigged=True
    if rigged:
        playernm = "Testbot"
    else:
        intro()
        do_print()
        slowWriting("What's your name?")
        playernm = do_input()
    game = set_up(weirdness=True, bad_language=True, player_name=playernm)
    col_list(game.inventory)

    do_print()
    slowWriting("[[ Type 'help' for controls and options. ]]")
    do_print()
    inner_loop()

#run() # uncomment me to actually play again.


import os
def test():

    test_mode=True
    os.system("cls")
    global game
    game = set_up(weirdness=True, bad_language=True, player_name="A")

    if enable_tui:

        player_name = run_tui_intro(play_intro=False)

        if player_name:
            game.playername = player_name

        world = (game.place, game.weather, game.time, game.day_number)
        player = (game.player, game.carryweight, game.playername)
        add_infobox_data(print_data = True, backgrounds = False, inventory=None, playerdata=player, worldstate=world)
        print_commands(backgrounds=False)
        update_infobox(hp_value=game.player["hp"], name=game.playername, carryweight_value=game.carryweight, location=game.place, weather=game.weather, time_of_day=game.time, day=game.day_number)
        add_infobox_data(print_data = True, inventory=game.inventory)

    if not test_mode:
        slowWriting("[[ Type 'help' for controls and options. ]]")
        do_print()
    inner_loop(speed_mode=test_mode)

os.system("cls")
time.sleep(1)
test()

