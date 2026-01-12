## I'm not really sure what the identify of this particular script is in the new version. It used to be the core of everything because it held the loops, but the loops aren't used anymore...

from os import system
import random

from misc_utilities import assign_colour, col_list, generate_clean_inventory, get_inst_list_names, from_inventory_name, check_name, print_type, compare_input_to_options, smart_capitalise, do_print, do_input

from set_up_game import load_world, set_up, init_settings
from choices import choose, time_of_day, night, trip_over, emphasis

from item_definitions import container_limit_sizes, detail_data
from itemRegistry import ItemInstance, registry

from tui.tui_elements import add_infobox_data, print_commands
from tui.tui_update import update_infobox

from logger import logging_fn
import config

from verb_membrane import run_membrane

from env_data import locRegistry as loc


user_prefs = r"D:\Git_Repos\Choose_your_own\path_userprefs.json"
run_again = False

yes = ["y", "yes"]
no = ["n", "no", "nope"]

clear_screen = False

def do_clearscreen():
    if clear_screen:
        system("cls")

def slowLines(txt, speed=0.1, end=None, edit=False):
    if isinstance(txt, str) and txt.strip=="":
        edit=True
    do_print(text=txt, end=end, do_edit_list=edit)

def slowWriting(txt, speed=0.001, end=None, edit=False): # Just keeping this here for now as a way to maintain that once, these calls were different from the line prints.
    do_print(text=txt, do_edit_list=edit)

def get_visited_map():

    for place_obj in loc.places:
        if place_obj.visited:
            do_print(f"Visited {place_obj.name}. \n {assign_colour(f'Description: {place_obj.overview}', "b_yellow")}")
            for cardinal in loc.cardinals[place_obj]:
                cardinal_inst = loc.cardinals[place_obj][cardinal]
                items = get_items_at_here(place=cardinal_inst, print_list=False, return_coloured=True)
                if items:
                    items = ", ".join(items)
                    print(f"Items at {cardinal_inst.place_name}: {items}")

    do_print("\nEnd of Past Visits.")


def get_items_at_here(print_list=False, return_coloured=True, place=loc.current_cardinal) -> list: # default to current_cardinal as place, otherwise you have to state what you want.

    instance_objs_at = (registry.get_item_by_location(place))
        #print(f"Instance objs at: {instance_objs_at}")

    #if not instance_objs_at:
    #    print(f"There are no items at {place.place_name}")

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

def do_action(action:str, inst:ItemInstance|str)->list:
    logging_fn()
    if action == "continue":
        return

    if "remove " in action:

        if isinstance(inst,str):
            parent = from_inventory_name(inst)
        elif isinstance(inst,ItemInstance):
            parent = inst
        else:
            parent=None

        child = action.replace("remove ", "")
        children = registry.instances_by_container(parent)
        child = from_inventory_name(child, children)
        print(f"Parent: {parent}, child: {child}")
        from misc_utilities import separate_loot
        inventory, _ = separate_loot(child_input=child, parent_input=parent, inventory=game.inventory)
        if inventory:
            game.inventory = inventory
        return inventory

    elif "add to" in action:

        registry.add_item_to_container(inst)

        # currently not tracking how 'full' a container is, so implement that and then check against it.
        # then list any items that would fit and let user choose from that list, and then add that to the container and remove from open inventory. (though currently, open inventory includes in-container items.)
        ##TODO ooh. I should stop listing child items in the inventory and just have inventory marked with '<item>*' if it contains something (and the something is known about (so not wallet* if we haven't looked in it yet, etc.))

    elif "drop" in action:
        if isinstance(inst, ItemInstance):
            new_inst = inst.name
        else:
            new_inst = inst
        name, metadata = compare_input_to_options(game.inventory, input=new_inst, use_last=True)
        if name:
            #print(f"Name: {name}")
            #print(f"Original instance: {inst}")
            final_inst = metadata[name].get("instance")
            drop_loot(named=final_inst)
        else:
            drop_loot(named=inst)

    elif "pick up" in action:
        _, test_inventory = registry.pick_up(inst, game.inventory, loc.current, loc.current_cardinal)
        if test_inventory != None:
            game.inventory = test_inventory
            return game.inventory

    elif "read" in action:

        while True:
            test = option("read a while", "continue", preamble="You can sit and read a while if you like, or continue and carry on.")
            print("Need to determine how much time passes and what the benefit of reading is. For now it's just this. The two-step version is useless at the moment but keeping the structure for now anyway. Will fill it out later.")
            if test != None:
                if test in ("continue", "carry on"):
                    break
                if test in "read a while" or test in "read":

                    details = inst.name + "_details"
                    details = details.replace(" ", "_")
                    details_data = detail_data.get(details)
                    #print(f"Details data: {details_data}")
                    if details_data:
                        if details_data.get("is_tested"):
                            outcome = roll_risk()
                            test = details_data.get(outcome)
                            if not test:
                                test = details_data.get(outcome + 1)
                            if not test:
                                do_print(f"Failed to find result for {inst.name} in detail_data.")
                            else:
                                do_print(assign_colour(test, "b_yellow"))

                            #print("Need to roll the dice here to determine outcome.")
                        else:
                            details_str = details_data.get("print_str")
                            do_print(assign_colour(details_str, "b_yellow"))
                    #print("Randomly pick a number of hours/time-parts to wait, then wait them.")
                    #print("And there should be some kind of benefit to this. And/or deciding how long to read for.")
    #               # inst.times_read +=1 # doesn't exist yet but something like this might be good. Can read each thing x times (maybe varying based on the book/type) before it stops giving you value and only spends time.
                    break

    else:
        print(f"No routing found for {action} for {inst}")
        exit()


def item_interaction(inst:str, inventory_names:list=None, no_xval_names:list=None):
    logging_fn()
    if isinstance(inst, str):
        inv_test=from_inventory_name(inst, game.inventory)
        if inv_test:
            inst=inv_test
        else:
            inv_test = registry.instances_by_name(inst)[0]
            if inv_test:
                inst=inv_test

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
        test = None
        test = option(actions, print_all=True, preamble=f"\n{assign_colour("Actions available for ", "yellow")}{assign_colour(inst)}: ")
        match, _ = compare_input_to_options(actions, input=test)
        if match:
            test_inventory = do_action(match, inst) ## added so I don't accidentally wipe game.inventory if something fails.
            if test_inventory != None:
                game.inventory = test_inventory
            actions = registry.get_actions_for_item(inst, game.inventory)
            if "drop" in test:
                break

        if test == "" or test is None or test == "continue":
            #do_print(assign_colour(f"(Chosen: <NONE>) [item_interaction]", "yellow"))
            break

    return test


def do_inventory():
    done=False
    while done == False:
        slowWriting("INVENTORY: ")
        test=None
        inventory_names, no_xval_names = generate_clean_inventory(game.inventory, will_print=True, coloured=True)
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
    from env_data import weatherdict
    attr_dict={
        "time":time_of_day,
        "weather":list(weatherdict.keys())
    }

    slowLines("God mode: set game.[] parameters during a playthrough. For a print of all game.[] parameters, type 'game_all. Otherwise, just type the change you wish to make.")

    while True:
        text=do_input()
        if "game_all" in text:
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
            #if text == "":
                #do_print(assign_colour(f"(Chosen: <NONE>) [god_mode]", "yellow"))
            do_print("Returning to game with changes made.")
            break

def instance_name_in_inventory(inst_name:str)->ItemInstance:
    logging_fn()

    item_entry = registry.instances_by_name(inst_name)
    if item_entry and isinstance(item_entry, list):
        for entry in item_entry:
            if entry in game.inventory:
                return entry

    print(f"Did not find entry for {inst_name}")
    input()


def user_input():
    text = do_input()

    if text != None:
        text=text.strip()
    #if text.lower() == "godmode":
    #    do_print("Allowing input to set parameters. Please type 'done' or hit enter on a blank line when you're finished.")
    #    god_mode()
    #    do_print()
    #    return "done"
    #if text.lower() == "help":
    #    do_print()
    #    slowWriting(f"  Type words to progress, 'i' for 'inventory', 'd' to describe the environment, 'settings' for settings, 'show visited' to see where you've been this run: - that's about it.")
    #    do_print()
    #    return "done"
    #if text.lower()== "settings":
    #    do_print("Settings:")
    #    init_settings(manual=True)
    #    do_print()
    #    return "done"
    if text.lower() == "stats":
        do_print(f"    weird: [{game.weirdness}]. location: [{assign_colour(loc.current.name, 'loc')}]. time: [{game.time}]. weather: [{game.weather}]. checks: {game.checks}")
        inventory_names = get_inst_list_names(game.inventory)
        do_print(f"    inventory: {inventory_names}, inventory weight: [{len(inventory_names)}], carryweight: [{game.carryweight}]")
        do_print(f"    Player data: {game.player}")
        do_print()
    #if text.lower() == "i":
    #    # removed the print line from here, goes from 3 blank lines between i and inventory to 1.
    #    do_inventory()
    #if text.lower() == "d" or text.lower() == "description": ##TODO: make this a function instead of having it here. This is silly.
    #    #loc_data = places[game.place]
    #    do_print(assign_colour(f"[ Describe location. ]", "yellow"))
    #    slowWriting(f"[{assign_colour(smart_capitalise(loc.current.name), 'loc')}]  {loc.current.overview}")
    #    obj = getattr(loc.current, loc.current_cardinal.name)
    #    slowWriting(f"You're facing {assign_colour(loc.current_cardinal)}. {obj}")
    #    do_print(end='')
    #    is_items = get_items_at_here(print_list=False, place=loc.current_cardinal)
    #    if is_items:
    #        do_print(assign_colour("You see a few scattered objects in this area:", "b_white"))
    #        is_items = ", ".join(col_list(is_items))
    #        print(f"   {is_items}")
    #        #get_items_at_here(print_list=True)
    #    text=None
    if text and text.lower() == "show visited":
        get_visited_map()
        text = None
    #if text.lower().startswith("drop "):
    #    #do_print(f"Text starts with drop: {text}")
    #    textparts=text.split()[1:]
    #    #do_print(f"textparts: {textparts}, len: {len(textparts)}")
    #    if len(textparts) > 1:
    #        textparts = " ".join(textparts[0:])
    #    else:
    #        textparts = textparts[0]
    #    do_action("drop", textparts)
        #item = instance_name_in_inventory(textparts)
        #if item:
        #    drop_loot(item)
#    if text and text.lower() in ("exit", "quit", "stop", "q"):
#        # Should add the option of saving and returning later.
#        ##TODO: Need to work on this. Not urgently, but I'd at least like the setup done so it's an option conceptually; pretty much save everything in game, registry and item_management (or at least the data required to reconstruct). Will be a project in itself. Maybe tomorrow.
#
#        do_print("Okay, bye now!")
#        exit()
    else:
        return text

def option(*values, no_lookup=None, print_all=False, none_possible=True, preamble=None, inventory=False, look_around=False, return_any=False):
    logging_fn()

    if preamble:
        print(preamble)
    print("\n")
    test=user_input()

    response = run_membrane(test)

    #if test in ("inventory_done", "description_done", "drop_done"):
    #    return None
    #if test == "":
    #    do_print(assign_colour(f"(Chosen: <NONE>) [in option()]", "yellow"))
#
    #if test in no:
    #    return no
    #if test in yes:
    #    return yes
#
    #if return_any:
    #    return test




def roll_risk(rangemin=None, rangemax=None):
    logging_fn()

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
    logging_fn()

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
            loc.current.items.append(dropped)
        item = dropped
    return outcome

def drop_loot(named:ItemInstance|str=None, forced_drop=False)->str:
    logging_fn()

    if forced_drop:
        test = random.choice((game.inventory))
        _, test_inventory = registry.drop(test, loc.current, loc.current_cardinal, game.inventory)
        if test_inventory != None:
            game.inventory = test_inventory
        if config.enable_tui:
            add_infobox_data(inventory=game.inventory)
        return test

    inventory_names, _ = generate_clean_inventory(game.inventory)
    #inventory_names = get_inst_list_names(game.inventory)

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
        _, test_inventory = registry.drop(test, game.inventory)
        if test_inventory != None:
            game.inventory = test_inventory
        slowWriting(f"Dropped {assign_colour(test)}.")
    else:
        do_print(assign_colour(f"Error: This item (`{test}`) was not found in the inventory.", colour="red"))

    if config.enable_tui:
        add_infobox_data(print_data=True, inventory=game.inventory, clear_datablock=True)

    slowWriting("Load lightened, you decide to carry on.")

    if config.enable_tui:
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
    logging_fn()
    item=None
    carryweight = game.carryweight
    if named != "" and value == None: # don't add value for location items.
        if isinstance(named, str):
            items_list = registry.instances_by_name(named) ## wait I didn't even provide a name here. wtf...
            print(f"items list: {items_list}")
            for inst in items_list:
                if inst != instance_name_in_inventory(named) and registry.get_item_by_location(loc.current, loc.current_cardinal):

                    item_inst=inst
                elif inst.contained_in: ## does this need to be hasattr()? Probably.
                    print(f"inst.contained_in: {inst.contained_in}")
                    container = inst.contained_in
                    if container.location == {loc.current: loc.current_cardinal}: ## don't know if this'll work and it only works for one level of parent depth
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
        message = message.replace("[place]", loc.current.name)
        slowWriting(message)

    if item:
        item_picked_up, game.inventory = registry.pick_up(item, game.inventory) ##
        if item_picked_up:
            slowWriting(f"{assign_colour(item)} added to inventory.")
            if config.enable_tui:
                add_infobox_data(print_data=True, inventory=game.inventory)
        else:
            do_print(f"Seems you can't pick up {assign_colour(item, switch=True)}.")

### drop random item if inventory full // not sure if I hate this. ###
    if len(game.inventory) > carryweight and game.player["inventory_management"] == True:
        do_print()
        #switched = switch_the(item, 'the ')
        test = option(f"drop", "ignore", preamble=f"It looks like you're already carrying too much. If you want to pick up {assign_colour(item, None, nicename=registry.nicename(item), switch=True)}, you might need to drop something - or you can try to carry it all.")
        if test in ("ignore", "i"):
            slowWriting("Well alright. You're the one in charge...")

            if game.player["encumbered"]:
                outcome = roll_risk()
                if outcome in (1, 2):
                    dropped_item = drop_loot(forced_drop=True) # force drop something.
                    if config.enable_tui:
                        add_infobox_data(print_data=True, inventory=game.inventory)
                    do_print("You feel a little lighter all of a sudden...")
            if len(game.inventory) > game.carryweight:
                if not game.player["encumbered"]:
                    game.player["encumbered"] = 1
                else:
                    game.player["encumbered"] = 2
                    game.player["hp"] -= 1
                    if game.player["hp"] <= 0:
                        do_print("You died. I don't even have anything written for this. Umm... Awkward.")
                        exit()
                    do_print("You're carrying far too much. You can maintain it for now, but... Ouch.")

        else:
            slowWriting("You decide to look in your inventory and figure out what you don't need.")
            drop_loot()
    #do_print()
    return item

def have_a_rest():
    logging_fn()
    slowWriting("You decide to take it easy for a while.")
    # can do things like read a book, check phone if you have them, daydream (roll for it), etc.
    do_print()
    slowWriting("But after a while, you decide to get up anyway.")
    look_around()

def get_hazard():
    logging_fn()
    inside = getattr(loc.current, "inside")
    if inside:
        options = trip_over["any"] + trip_over["inside"]
    else:
        options = trip_over["any"] + trip_over["outside"]
    hazard = random.choice(options)
    return hazard

def relocate(need_sleep=None):
    from env_data import weatherdict, locRegistry as loc
    logging_fn()
    options = []

    current_loc = loc.current
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

    #while len(options) < len(list(loc.places.values())):
    #    new_place = random.choice((list(loc.places.values())))
    #    if new_place not in options: # and new_place != current_loc <- turn on when I don't want current loc as an option anymore.
    #        options.append(new_place.name)
    # instead of choosing random place names as above, instead:
    options = list(loc.by_name.keys())

    test = option(options, print_all=True, preamble="Please pick your destination:")
    new_location = test
    print(f"OPTIONS: {options}")
    if new_location in options:
        print(f"New location in options: {new_location}")
        #print(f"new location in options: {new_location}")
        new_location = loc.places[new_location]
        print(f"new location in options: {new_location}")
        print(f"new location in options (name): {new_location.name}")
        ##NOTE: this is working, but the rest is pretty broken. Going to leave it as-is as the whole thing needs to be rewritten for the new parser anyway.

        load_world(relocate=True, new_loc=new_location)
        if config.enable_tui:
            update_infobox(location=loc.current, weather=game.weather, t_o_d=game.time, day=game.day_number)

    if loc.current==current_loc:
        print(f"loc.places[loc.current]: {loc.current.name}")
        do_print(f"You decided to stay at {assign_colour(loc.current.the_name, 'loc')} a while longer.")
    else:
        slowWriting(f"You make your way to {assign_colour(loc.current.the_name, 'loc')}. It's {game.time}, the weather is {game.weather}, and you're feeling {game.emotional_summary}.")
        if loc.current.visited:
            slowWriting(f"You've been here before... It was {loc.current.first_weather} the first time you came.")
            if loc.current.first_weather == game.weather:
                do_print(weatherdict[game.weather].get("same_weather"))
        else:
            loc.current.visited = True # maybe a counter instead of a bool. Maybe returning x times means something. No idea what. Probably not.
            loc.current.first_weather = current_weather

    if need_sleep:
        decision = option("rest", "look", preamble="You're getting exhausted. You can look around if you like but the sleep deprivation's getting to you.")
        if decision == "rest":
            if loc.current.inside == False:
                sleep_outside()
            else:
                sleep_inside()
        else:
            look_around(status="exhausted")
    else:
        look_around()

def sleep_outside():
    logging_fn()
    if getattr(loc.current, "nature"):
        slowWriting("You decide to spend a night outside in nature.")
    else:
        slowWriting(f"You decide to spend a night outside in {assign_colour(loc.current.the_name, 'loc')}.")
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
    logging_fn()
    slowWriting(f"Deciding to hunker down in {assign_colour(loc.current.the_name, 'loc')} for the night, you find the comfiest spot you can and try to rest.")
    risk = roll_risk(10, 21)
    outcome = outcomes(risk, "sleep")
    slowWriting(outcome)
    the_nighttime()

def the_nighttime():
    logging_fn()
    do_print()
    slowWriting("Finally asleep, you dream deeply.")
    slowWriting("  ...")
    slowWriting("    ...")
    slowWriting("       ...")
    slowWriting("Imagine a dream here. Something meaningful...")
    slowWriting("And/or wild animals if sleeping outside, and/or people, and/or ghosts/monster vibes if weird.")
    new_day()

def location_item_interaction(item_name):
    logging_fn()

    item_entry = registry.instances_by_name(item_name)
    if item_entry:
        local_items = registry.get_item_by_location(loc.current, loc.current_cardinal)
        for item in item_entry:
            if item in local_items and item not in game.inventory:
                ### TODO: and item not in container that is in inventory
                entry = item
                break

        slowWriting((f"Description: {assign_colour(registry.describe(entry, caps=True), "description")}"))

        while True:
            decision=option("take", "leave", preamble=f"What do you want to do with {assign_colour(entry, switch=True)} - take it, or leave it alone?")
            if decision == "":
                do_print(assign_colour(f"(Chosen: <NONE>) [location_item_interaction]", "yellow"))
                do_print("Leaving it be.")
                break
            if decision and decision != "" and decision is not None:
                if decision.lower()=="investigate": ## this deep nesting is an issue. Withdrawing from here gets you all the way to 'relocate'.
                    do_print("Nothing here yet.")
                    break
                elif decision.lower()=="take":
                    picked_up = get_loot(value=None, random=True, named=entry, message=None)
                    if not picked_up:
                        do_print(f"Seems you can't take {assign_colour(entry, switch=True)} with you.")
                    break

                elif decision.lower()=="leave":
                    do_print(f"You decide to leave the {assign_colour(entry)} where you found it.")
                    break
    else:
        do_print(f"No entry found for {item_entry}")

def look_around(status=None):
    logging_fn()
    item = None
    place = loc.current
    time = game.time
    weather = game.weather

    def look_dark():
        logging_fn()
        if ("torch" or "phone" or "matchstick") not in game.inventory:
            if getattr(place, "electricity"):
                #print(f"Has attr electricity at {place}")
#            if descriptions[place].get("electricity"):
                test=option("yes", "no", preamble="It's dark, but you can try to find a light switch if you want.")
                if test in yes:
                    outcome = roll_risk()
                    if outcome in (1, 2):
                        slowWriting("Try as you might, you can't find a lightswitch...")
                    else:
                        slowWriting("The light flickers on - you can see.")
                        look_light(reason="electricity")

            test=option("yes", "no", preamble=f"It's too dark to see much of anything in {assign_colour(loc.current.the_name, 'loc')}, and without a torch or some other light source, you might trip over something. Do you want to keep looking?")
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
            test = option("stay here", "move on", preamble=f"You could stay and sleep in {assign_colour(loc.current.the_name, 'loc')} until morning, or go somewhere else to spend the wee hours. What do you do?")
            if test in ("sleep", "stay", "stay here"):
                if loc.current.inside == False:
                    sleep_outside()
                else:
                    sleep_inside()
            else:
                slowWriting(f"Keeping in mind that it's {time} and {weather}, where do you want to go?")
                print(f"game.place before relocate: {loc.current.name}")
                relocate()

        else:
            slowWriting("Using your torch, you see things. Probably. I haven't written this yet. How do you have a torch?!?")



    def look_light(skip_intro = False, reason=None):
        logging_fn()
# from stackoverflow:
# print(inspect.currentframe().f_code.co_name) or to get the caller's name: print(inspect.currentframe().f_back.f_code.co_name)

        skip_intro=skip_intro
        if reason == "turning" or reason == "skip_intro":
            skip_intro=True
        elif reason == None:
            reason = "the sun"
        if skip_intro==False:
            slowWriting(f"Using the power of {reason}, you're able to look around {assign_colour(loc.current.the_name, 'loc')} without too much fear of a tragic demise.")
        while True:
            remainders = list(x for x in game.cardinals if x is not loc.current_cardinal)

            text=None
            is_done=False

            while not text and is_done == False:
                local_items = get_items_at_here(print_list=False, return_coloured=False)
                #print(f"Local items: {local_items}")
                text=option(remainders, "leave", no_lookup=None, print_all=True, preamble="You can look around more, leave, or try to interact with the environment:", look_around=local_items, return_any=True)

                if text != None:
                    if text == "leave":
                        slowWriting(f"You decide to move on from {assign_colour(loc.current.the_name, 'loc')}")
                        relocate()

                    if text in game.cardinals or text[:1] in [i[:1] for i in game.cardinals]:
                        if text in remainders:
                            loc.current_cardinal=text
                            remainders = list(x for x in game.cardinals if x is not loc.current_cardinal)
                            look_light("turning")
                        else:
                            do_print(f"You're already facing {loc.current_cardinal}")

                    if local_items and text in local_items:
                        location_item_interaction(text)
                        text=None


                #else:
                    #do_print(f"Could not find what you're looking for. The options: {potential}")
            options = ["stay here", "move on"]
            text = option(options, no_lookup=None, print_all=True, preamble="Do you want to stay here or move on?")
            checked_str, _ = compare_input_to_options(options, input=text)
            if checked_str == "stay here":
                continue
            if checked_str == "move on":
                break

            slowWriting("Unfortunately I haven't written anything here yet so this'll just repeat for now.")

        slowWriting(f"Keeping in mind that it's {time} and {weather}, where do you want to go?")
        relocate()

    if status == "exhausted" and time not in night:
        slowWriting("Stumbling, you're going to hurt yourself even if it's nice and bright. Haven't written it yet though.")
        look_dark()

## ==== Actual start here ===
    inside = getattr(loc.current, "inside")
    if inside:
        add_text="outside "
    else:
        add_text=""
    slowWriting(f"With the weather {add_text}{game.weather}, you decide to look around the {loc.current_cardinal} of {assign_colour(loc.current.the_name, 'loc')}.")
    if time in night:
        slowWriting(f"It's {game.time}, so it's {random.choice(emphasis["low"])} dark.")
        look_dark()
    else:
        look_light("skip_intro")

def new_day():
    logging_fn()

    if game.loop==False:
        decision = option("yes", "no", preamble="Keep looping?")
        if decision in no:
            slowWriting("Hope you had fun? Not sure really what this is, but thank you.")
            exit()

    game.checks["play_again"]
    game.time = random.choice(["pre-dawn", "early morning", "mid-morning"])
    inner_loop()

def describe_loc():
    logging_fn()

    slowWriting(f"You take a moment to take in your surroundings. {loc.current.overview}")
    #test=option(game.cardinals, "go elsewhere", print_all=True, preamble="Pick a direction to investigate, or go elsewhere?")
    ### TODO: I miss when it used to print 'chosen: (go elsewhere)' if I entered 'g'. Need to get that back.
    #if test in game.cardinals:
    #    loc.current_cardinal = test
    #    look_around()
    #else:
    #    slowWriting(f"You decide to leave {assign_colour(loc.current.the_name, 'loc')}")
    #    relocate()

def inner_loop(speed_mode=False):
    logging_fn()

    loc.current.visited = True
    loc.current.first_weather = game.weather

    if not speed_mode:
        slowWriting(f"You wake up in {assign_colour(loc.current.a_name, 'loc')}, right around {game.time}. You find have a bizarrely good sense of cardinal directions; how odd.")
        slowWriting(f"`{game.playername}`, you think to yourself, `is it weird to be in {assign_colour(loc.current.the_name, 'loc')} at {game.time}, while it's {game.weather}?`")
        do_print()
        describe_loc()
    while True:
        test=option()

def intro():

    #First run setup
    # ascii from https://patorjk.com/software/taag/#p=display&f=Big+Money-ne&t=paths&x=none&v=4&h=4&w=80&we=false
    do_print("\n")
    slowLines("                          /================================ #", end="no")
    slowLines("                         /                                  #", end="no")
    slowLines("   # ===================/     /$$     /$$                   #", end="no")
    slowLines("   #                         | $$    | $$                   #", end="no")
    slowLines("   #     /$$$$$$   /$$$$$$  /$$$$$$  | $$$$$$$   /$$$$$$$   #", end="no")
    slowLines("   #    /$$__  $$ |____  $$|_  $$_/  | $$__  $$ /$$_____/   #", end="no")
    slowLines(r"   #   | $$  \ $$  /$$$$$$$  | $$    | $$  \ $$|  $$$$$$    #", end="no")
    slowLines(r"   #   | $$  | $$ /$$__  $$  | $$ /$$| $$  | $$ \____  $$   #", end="no")
    slowLines("   #   | $$$$$$$/|  $$$$$$$  |  $$$$/| $$  | $$ /$$$$$$$/   #", end="no")
    slowLines(r"   #   | $$____/  \_______/   \___/  |__/  |__/|_______/    #", end="no")
    slowLines("   #   | $$                                                 #", end="no")
    slowLines("   #   | $$       /======================================== #", end="no")
    slowLines("   #   |__/      /", end="no")
    slowLines("   #            /", end="no")
    slowLines("   # ==========/", end="no")
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

    test = None
    global loc
    from env_data import locRegistry as loc
    #do_clearscreen()
    playernm = ""

    test_mode=False#True
    if test_mode:
        playernm = "Testbot"
        enable_tui = False
    else:
        intro()
        do_print()
        slowWriting("What's your name?")
        while  playernm == "":
            playernm = do_input()
    global game
    game = set_up(weirdness=True, bad_language=True, player_name=playernm)

    #do_clearscreen()

    if config.enable_tui:
        from tui.tui_elements import run_tui_intro
        player_name = run_tui_intro(play_intro=False)

        if player_name:
            game.playername = player_name

        world = (loc.current, game.weather, game.time, game.day_number)
        player = (game.player, game.carryweight, game.playername)
        add_infobox_data(print_data = True, backgrounds = False, inventory=None, playerdata=player, worldstate=world)
        print_commands(backgrounds=False)
        update_infobox(hp_value=game.player["hp"], name=game.playername, carryweight_value=game.carryweight, location=loc.current.name, weather=game.weather, t_o_d=game.time, day=game.day_number)

        add_infobox_data(print_data = True, inventory=game.inventory)

    ## Add glass jar to inventory for container tests
    #game.carryweight += 5
    #inst = registry.instances_by_name("glass jar")
    #_, game.inventory = registry.pick_up(inst, game.inventory)

    if not test_mode:
        slowWriting("[[ Type 'help' for controls and options. ]]")
        do_print()

    #while test != "quit":
    print()
    inner_loop(speed_mode=test_mode)


def temp_run():
    import config
    config.enable_tui = False
    print("Temp run")
    run()



#if __name__ == "__main__":
#    #do_clearscreen()
#    import sys
#    if sys.argv:
#        #print(f"sys.argv: {sys.argv}")
#
#        if len(sys.argv) == 2:
#            #disable_tui_test = sys.argv[1] ## at present the content doesn't matter, either it's plain and uses tui, or python choose_a_path disable_tui (where 'disable_tui' can be literally anything). Works for the moment.
#            enable_tui = False
#            config.enable_tui = False
#        else:
#            enable_tui = True
#            config.enable_tui = True
#
#
#
#    enable_tui = False
#    config.enable_tui = False
#    run()
