
### Interface between item_actions and the verbs.

#import time
from logger import logging_fn, traceback_fn
from env_data import cardinalInstance, locRegistry as loc, placeInstance
from interactions import item_interactions
from interactions.player_movement import new_relocate, turn_around
from itemRegistry import ItemInstance, registry
from misc_utilities import assign_colour, col_list, generate_clean_inventory
from set_up_game import game
from verb_definitions import directions, semantics, formats

movable_objects = ["put", "take", "combine", "separate", "throw", "push", "drop", "set", "move"]

flag_actions = {
    "can_pick_up": movable_objects,
    "is_container": movable_objects,
    "flammable": ["burn", "set"],
    "dirty": "clean",
    "locked": "unlock",
    "can_lock": "lock",
    "fragile": "break",
    "can_open": "open",
    "can_read": "read",
    "can_combine": "combine",
    "weird": "",
    "dupe": "",
    "is_child": "",
    "combine_with": "combine", ## falling asleep tbh.
    "can_remove_from": ""
    }

in_words = ["in", "inside", "into"]
to_words = ["to", "towards", "at", "for"] ## these two (< + ^) are v similar but have some exclusive uses, so keeping them separately makes sense here. # 'for' in the sense of 'leave for the graveyard'.
down_words = ["down"]


#### Fundamental Operations ####

def get_current_loc():
    logging_fn()

    from env_data import locRegistry
    location = locRegistry.currentPlace
    cardinal = locRegistry.current
    return location, cardinal

def is_loc_current_loc(location=None, cardinal=None):
    logging_fn()

    current_location, current_cardinal = get_current_loc()
    if location and location == current_location:
        return 1, current_location, current_cardinal
    if not location and cardinal: ## so it can check if the facing direction is current without needing location.
        if cardinal == current_cardinal:
            return 1, current_location, current_cardinal
    return 0, current_location, current_cardinal # 0 if not matching. Always returns current.


def move_a_to_b(a, b, action=None, direction=None, current_loc = None):
    logging_fn()

    location = None
    from item_definitions import container_limit_sizes
   ## This is the terminus of any 'move a to b' type action. a must be an item instance, b may be an item instance (container-type) or a location.
    if not direction:
        if action == "dropping":
            direction = "at"
        else:
            direction = "to"
    if not action:
        action = "moving"

    if isinstance(a, ItemInstance):
        if not isinstance(b, ItemInstance):
            if isinstance(b, cardinalInstance):
                if b == loc.current:
                    from misc_utilities import smart_capitalise
                    text = smart_capitalise(f"{action} {assign_colour(a)} {direction} {assign_colour(b, card_type = "place_name")}")
                    print(text)
                    item_interactions.add_item_to_loc(a, b)
                    return "yes"
            print("B is not an instance. move a to b requires two things: What is the second item? (pass for now.)")
            return None

        else:
            if hasattr(b, "container_limits"): ## This won't work long term, currently the only option for move noun x noun is if hte second is a container. Not 'move noun towards noun', etc, which I want for later. No idea how to implement it, but for now I'm just noting it here.
                print(f"{b.name} is a container with capacity {b.container_limits}.")
                container_size = container_limit_sizes.get(b.container_limits)
                if isinstance(a, ItemInstance):
                    if hasattr(a, "item_size"):
                        print(f"{b.name} is an item with size {a.item_size}.")
                        item_size = container_limit_sizes.get(a.item_size)
                        if item_size < container_size:
                            print(f"{a.name} will fit in {b.name}")
                            print(f"{action} {a} {direction} {b}")
                            registry.move_item(a, new_container=b)

    elif isinstance(b, tuple):
        print(f"b is a tuple: {b}")
        if not current_loc:
            _, current_loc = get_current_loc() ## this may pick up cardinals accidentally. Changing to break the tuple. Might break things.
        if b[0] in current_loc:
            location = b[0]
            print(f"{action} {a.name} {direction} {b}")

        else:
            print("Can only move items to the location you're currently in.")

    elif isinstance(b, cardinalInstance):
        location = b

    else:
        print("B is not an instance.")
        if not current_loc:
            _, current_loc = get_current_loc()

        if b == current_loc:
            print(f"B is the current location: {b}")
            location = b
        elif "a " + b == current_loc:
            print(f"B is the current location: {b}")
            location = "a " + b

        if location:
            print(f"{action} {a.name} {direction} {b}")
        else:
            print(f"Failed to move `{a}` to `{b}`.")
            print(f"Reason: `{b}` is not the current location.")

def check_lock_open_state(noun_inst, verb_inst):
    logging_fn()

    is_closed = is_locked = locked_have_key = False

    inst, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst) ## checks if the item is accessible, not if it itself is locked. It only checks the lock/key for the containing obj.
    print(f"MEANING for {noun_inst} ({reason_val}): {meaning}")
    #print(f"reason val: {reason_val}")
    if reason_val in (0, 3, 4, 5): # all 'not closed/locked container options
        if hasattr(noun_inst, "is_open"):
            if noun_inst.is_open == False:
                is_closed = True
        if hasattr(noun_inst, "is_locked"):
            if noun_inst.is_locked == False:
                is_locked = True
    elif reason_val == 1:
        is_closed = True
    elif reason_val == 2:
        #is_locked = True
        if hasattr(noun_inst, "is_locked") and noun_inst.is_locked:
            print(f"IS_LOCKED: `{noun_inst.is_locked}`")
            if hasattr(noun_inst, "needs_key"):
                key_inst = None
                print(f"key: `{noun_inst.needs_key}`")
                inst, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst.needs_key)
                print(f"MEANING (is locked, is not open): {meaning}")
                #if container and isinstance(container, ItemInstance) and container.name == noun_inst.needs_key:
                #    key_inst = container ## Not sure what this was meant to be doing. I'm too tired to be doing this.
                if reason_val in (0, 3, 4, 5):
                    locked_have_key = True
                else:
                    is_locked = True

    return is_closed, is_locked, locked_have_key


def get_entries_from_dict(input_dict):
    logging_fn()

    verb_entry = None
    noun_entry = None
    direction_entry = None
    cardinal_entry = None
    location_entry = None
    semantic_entry = None

    #get the values from the dict for location+cardinal right at the start.

    for idx in input_dict.values():
        for kind, entry in idx.items():
            if kind == "noun":
                if noun_entry != None:
                    print(f"More than one `noun`: {noun_entry} already exists, {entry} will be ignored.")
                    continue
                noun_entry = entry
            if kind == "verb":
                if verb_entry != None:
                    print(f"More than one `verb`: {verb_entry} already exists, {entry} will be ignored.")
                    continue
                verb_entry = entry
            if kind == "direction":
                if direction_entry != None:
                    print(f"More than one `direction`: {direction_entry} already exists, {entry} will be ignored.")
                    continue
                direction_entry = entry

            if kind == "cardinal":
                if cardinal_entry != None:
                    print(f"More than one `cardinal`: {direction_entry} already exists, {entry} will be ignored.")
                    continue
                cardinal_entry = entry
            if kind == "location":
                if location_entry != None:
                    print(f"More than one `location`: {direction_entry} already exists, {entry} will be ignored.")
                    continue
                location_entry = entry
            if kind == "sem":
                if semantic_entry != None:
                    print(f"More than one `sem`: {direction_entry} already exists, {entry} will be ignored.")
                    continue
                semantic_entry = entry

    return verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry


     #################################
## Simple 'get this element' functions. ##

def get_verb(input_dict:dict) -> ItemInstance:
    logging_fn()
    if input_dict[0].get("verb"):
        #print(f"{input_dict[0]} is a verb, confirmed in get_verb")
        return list(input_dict[0].values())[0]["instance"] # works as long as verb is always first

    print(f"get_verb failed to find the verb instance: {input_dict}")

def get_noun(input_dict:dict, x_noun:int=None) -> ItemInstance:
    logging_fn()
    # x_noun: 1 == 1st noun, 2 == "2nd noun", etc. Otherwise will always return the first found.

    noun_counter = 0
    for data in input_dict.values():
        for kind, entry in data.items():
            if "noun" in kind:
                if x_noun:
                    noun_counter += 1
                    if noun_counter == x_noun:
                        return entry["instance"]
                else:
                    return entry["instance"]

    print(f"get_noun failed to find the noun instance: {input_dict}")

def get_location(input_dict:dict) -> cardinalInstance|placeInstance:
    logging_fn()
    # x_noun: 1 == 1st noun, 2 == "2nd noun", etc. Otherwise will always return the first found.

    for data in input_dict.values():
        for kind, entry in data.items():
            if "location" in kind:
                    return entry["instance"]

    print(f"get_location failed to find the location instance: {input_dict}")


def get_dir_or_sem_if_singular(input_dict:dict) -> str:
    logging_fn()
    for data in input_dict.values():
        for kind, entry in data.items():
            if "direction" in kind or "sem" in kind:
                #print(f"{kind} in kind: {entry}")
                return entry["str_name"]

    print(f"get_dir_or_sem failed to find the dir/sem instance: {input_dict}")


def item_attributes(format_tuple, input_dict):
    # want to be able to print noun attributes at will.
    inst_to_print = get_noun(input_dict)
    if not inst_to_print:
        inst_to_print = get_location(input_dict) # just in case I want location attributes instead

    from pprint import pprint
    pprint(vars(inst_to_print))

##### Parts Parsing ########

def two_parts_a_b(input_dict):
    logging_fn()
    return list(input_dict[1].values())[0]

def three_parts_a_x_b(input_dict): # kinda hate this because it returns the entry. But I guess that's useful. Am using the get_element versions more now, though.
    logging_fn()
    print(f"list(input_dict[2].values())[0]: {list(input_dict[2].values())[0]["str_name"]}")
    if list(input_dict[2].values())[0]["str_name"] in directions or list(input_dict[2].values())[0]["str_name"] in semantics:
        a = list(input_dict[1].values())[0]
        sem_or_dir = list(input_dict[2].values())[0]
        b = list(input_dict[3].values())[0]

        return a, sem_or_dir, b

    print(f"Cannot process {input_dict} in def three_parts_a_x_b() End of function, unresolved.")

                                  #       0          1       2    3       4        5
def five_parts_a_x_b_in_c(input_dict): # `drop the paperclip in glass jar in the graveyard`
    logging_fn()

    if list(input_dict[2].values())[0] in directions:
        a = list(input_dict[1].values())[0]
        sem_or_dir = list(input_dict[2].values())[0]
        b = list(input_dict[3].values())[0]
        sem_or_dir_2 = list(input_dict[4].values())[0]
        c = list(input_dict[5].values())[0]

        return a, sem_or_dir, b, sem_or_dir_2, c

    print(f"Cannot process {input_dict} in def five_parts_a_x_b_in_c() End of function, unresolved.")

def get_elements(input_dict) -> tuple:
    logging_fn()
    ## This is only useful if there's some other check going on. Otherwise it should just be per item, I think.
### I don't think this is actually better than each one just doing 'if len(), because it still has to evaluate the number afterwards to unpack it, no?

    if len(input_dict) == 2:
        return 2, list(input_dict[1].values()) # could be 'leave loc', 'drop item', 'get item', 'talk person' etc.

    elif len(input_dict) == 3:
        return 3, three_parts_a_x_b(input_dict)

    elif len(input_dict) == 4:
        return 4, three_parts_a_x_b(input_dict)

    print(f"Cannot process {input_dict} in def get_elements() End of function, unresolved.")


def inst_from_idx(dict_entry:dict, kind_str:str, return_str=False) -> ItemInstance:
    logging_fn()
    if return_str:
        return dict_entry[kind_str]["str_name"]

    return dict_entry[kind_str]["instance"]

##############################
#from interactions.player_movement import new_relocate
            #new_relocate(details)
# little bits, the finer end points that things resolve to.

def turn_cardinal(prospective_cardinal, turning = True):
    logging_fn()


    if prospective_cardinal in ("left", "right"):
        print("prospective cardinal in left/right")
        current_facing = loc.current.name
        turning_dict = {
            "north":0,
            "east":1,
            "south":2,
            "west":3
        }
        #left = 1
        #right = -1
        if prospective_cardinal == "left":
            new_int = int((turning_dict[current_facing] + 1)%4)
        else:
            new_int = int((turning_dict[current_facing] - 1)%4) ## will this wrap around to go from 0 to 3?
        #print(f"NEW INT: {new_int}")
        for k, v in turning_dict.items():
            if v == new_int:
                #print(f"V == new_int: {v}")
                prospective_cardinal = loc.by_cardinal_str(k)
                #print(f"Prospective cardinal is now: {prospective_cardinal.name}")


    if isinstance(prospective_cardinal, dict):
        test = prospective_cardinal.get("cardinal")
        if test:
            prospective_cardinal = test.get("instance")
        else:
            test = prospective_cardinal.get("instance")
            if test:
                prospective_cardinal = test

    if isinstance(prospective_cardinal, str):
        prospective_cardinal = loc.by_cardinal_str(prospective_cardinal)


    #print(f"prospective cardinal going to loc test: {prospective_cardinal}")
    bool_test, _, _ = is_loc_current_loc(None, prospective_cardinal)
    if not bool_test:
        from env_data import loc_dict
        cardinal_str = prospective_cardinal.name
        intended_cardinal = (loc_dict[loc.currentPlace.name][cardinal_str] if loc_dict[loc.currentPlace.name].get(cardinal_str) else None)
        #print(f"Intended_cardinal: {intended_cardinal}")
        if intended_cardinal:
            turning_to = prospective_cardinal
            turn_around(turning_to)
        else:
            print("There's nothing over that way.\n")
            print(f"You're facing {loc.current.place_name}")
            print(loc.current.long_desc)

        return
        #print(f"turning_to: {turning_to}, type: {type(turning_to)}") ## Shouldn't have this, should be able to use this function for just turning.
        #print(f"You turn to the {turning_to.ern_name}")
        #return "new_cardinal", turning_to
    else:
        #print(f"Prospective cardinal: {prospective_cardinal}")
        #print(f"Prospective cardinal.name: {prospective_cardinal.name}")
        if turning:
            print(f"You're already already facing the {assign_colour(prospective_cardinal, card_type="ern_name")}.")
        print(prospective_cardinal.long_desc)
        return "no_change", None


#######################

def meta(format_tuple, input_dict):
    logging_fn()

    for idx in input_dict:
        for kind, entry in input_dict[idx].items():
            if kind == "meta":
                meta_verb = entry["str_name"]

    if meta_verb == "help":
        print("Type words to progress, 'i' for 'inventory', 'd' to describe the environment, 'settings' for settings, 'show visited' to see where you've been this run: - that's about it.")
        return
    elif meta_verb == "settings":
        from choose_a_path_tui_vers import init_settings
        init_settings(manual=True)
        return
    elif meta_verb == "describe":
        look(("verb", "sem"), None)
        return
    elif meta_verb == "inventory":
        generate_clean_inventory(will_print=True, coloured=True)
        return
    elif meta_verb == "godmode":
        from choose_a_path_tui_vers import god_mode
        god_mode()
        return
    elif meta_verb == "quit":
        print("Okay, quitting the game. Goodbye!\n\n")
        exit()
        return
    elif meta_verb == "update_json":
        from testclass import add_confirms
        add_confirms()
        return
    print(f"Cannot process {input_dict} in def meta() End of function, unresolved. (Function not yet written)")

def go(format_tuple, input_dict): ## move to a location/cardinal/inside
    logging_fn()

    current_loc, current_card = get_current_loc()

    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    if (direction_entry and direction_entry["str_name"] in to_words and len(format_tuple) < 5) or (not direction_entry and len(format_tuple) < 4) or (direction_entry and not cardinal_entry and not location_entry):
        if location_entry and not cardinal_entry:
            if location_entry["instance"] == loc.currentPlace:
                if input_dict[0].get("verb") and input_dict[0]["verb"]["str_name"] == "leave":
                    print("You can't leave without a new destination in mind. Where do you want to go?")
                    return
            new_relocate(new_location=location_entry["instance"])

        elif cardinal_entry and not location_entry:
            if cardinal_entry["instance"].place == loc.currentPlace:
                turn_cardinal(cardinal_entry["instance"])
            else:
                new_relocate(new_location=location_entry["instance"], new_cardinal = cardinal_entry["instance"])

        elif direction_entry and not location_entry and not cardinal_entry:# and verb_entry["str_name"] in ("go", "turn", "head", "travel", "move"):
            if direction_entry["str_name"] in ("left", "right"):
                turn_cardinal(direction_entry["str_name"])
            else:
                print("If this does not have a location, it breaks. Why am I still using location_entry etc after determining they don't exist. Works if the direction is something internal, but not if I just type 'go to church', a location that doesn't exist.")
                #if len(format_tuple) == 3:
                print(f"FORMAT TUPLE: {format_tuple}")
                new_relocate(new_location=location_entry["instance"], new_cardinal = cardinal_entry["instance"])

        else:
            new_relocate(new_location=location_entry["instance"], new_cardinal = cardinal_entry["instance"])

    elif direction_entry["str_name"] in in_words:
        print(f"Can {input_dict[1]["direction"]["str_name"]} be entered?")
        print("This isn't done yet.")

    elif direction_entry["str_name"] == "from":
        if location_entry and location_entry["instance"] != current_loc():
            print("Cannot leave a place you are not in.")

    else:
        print(f"Cannot process {input_dict} in def go() End of function, unresolved. (Function not yet written)")
        traceback_fn()




def leave(format_tuple, input_dict):
    logging_fn()
    #verb_only, verb_loc = go
    # verb_noun_dir_noun = movw item to container/surface
    print(f"Cannot process {input_dict} in def leave() End of function, unresolved. (Function not yet written)")


def look(format_tuple, input_dict):
    logging_fn()

    if format_tuple == tuple(("verb", "sem")) and not input_dict:
        from misc_utilities import look_around
        look_around()
        return

    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    if len(format_tuple) == 1:
        from misc_utilities import look_around
        look_around()

    elif len(format_tuple) == 2:
        if semantic_entry != None and input_dict[1]["sem"]["str_name"] == "around":
            from misc_utilities import look_around
            look_around()
            return

        elif cardinal_entry != None:
            turn_cardinal(cardinal_entry["instance"], turning = False)

        elif direction_entry != None: # if facing north, turn east, etc.)
            intended_direction = direction_entry["str_name"]
            if intended_direction in ("left", "right"):
                turn_cardinal(intended_direction, turning=False)

        elif format_tuple[1] == "noun":
            item_interactions.look_at_item(inst_from_idx(input_dict[1], "noun"))

    elif len(format_tuple) == 3:
        if format_tuple[2] == "noun" and format_tuple[1] == "direction":
            item_interactions.look_at_item(inst_from_idx(input_dict[2], "noun"))
        elif format_tuple[2] == "cardinal" and format_tuple[1] == "direction":
            turn_cardinal(inst_from_idx(input_dict[2], "cardinal"), turning = False)

    elif len(format_tuple) == 4:
        if cardinal_entry and location_entry:
            if location_entry["instance"] != loc.currentPlace:
                print(f"You can only look at locations you're currently in. Do you want to go to {location_entry["instance"].name}?")
            else:
                turn_cardinal(cardinal_entry["instance"], turning = False)

        elif format_tuple.count("noun") == 2: # watch x with y
            ## NOTE: Need to make it so that if there's two identical noun-strings, they refer to different objects. Already do this when picking things up, but if I have two watches, I should be using one for each noun. And likewise, if I only have one watch, then I can't use it to affect itself.
            print("`Watch x with y` not yet implemented.")

    else:
        print(f"Cannot process {input_dict} in def look(): \n{format_tuple} \n{input_dict}")


def read(format_tuple, input_dict):
    logging_fn()
    verb_inst = get_verb(input_dict)
    noun_inst = get_noun(input_dict)
    if hasattr(noun_inst, "description_detailed"):
        #print(f"You read the {assign_colour(noun_inst)}:\n")
        if noun_inst.description_detailed.get("is_tested"):
            from rolling import roll_risk
            outcome = roll_risk()
            if outcome > 1:
                test = noun_inst.description_detailed.get("crit")
                print(assign_colour(test, "b_yellow"))
            else:
                test = noun_inst.description_detailed.get("failure")
                print(assign_colour(test, "b_yellow"))
        else:
            to_print = noun_inst.description_detailed.get("print_str")
            print(assign_colour(to_print, "b_yellow"))
    else:
        print(f"It seems like you can't read the {assign_colour(noun_inst)}")

def eat(format_tuple, input_dict):
    logging_fn()
    noun_inst = get_noun(input_dict)

    verb = input_dict[0]["verb"]["str_name"]
    if hasattr(noun_inst, "can_consume"):
        print(f"You decide to {verb} the {assign_colour(noun_inst)}.")
        print("something something consequences")
        game.inventory.remove(noun_inst)
        registry.delete_instance(noun_inst)

    else:
        print("This doesn't seem like something you can eat...")


def clean(format_tuple, input_dict):
    logging_fn()
    print("clean FUNCTION")
    print(f"format list: {format_tuple}, type: {type(format_tuple)}, length: {len(format_tuple)}")
    if len(format_tuple) == 2:
        if format_tuple == tuple(("verb", "location")):
            get_noun
        #if "verb" in format_tuple and "location" in format_tuple:
            print(f"You want to clean the {assign_colour(get_location)}? Not implemented yet.")
            return

    if format_tuple == formats("verb_noun_sem_noun"):# verb_noun == clean item
        print("You want to clean the {assign_colour(get_noun(input_dict))} with the {assign_colour(get_noun(input_dict, x_noun=2))}? Not implemented yet.")
        return

    print(f"Cannot process {input_dict} in def clean() End of function, unresolved. (Function not yet written)")


def burn(format_tuple, input_dict):
    logging_fn()
    print("burn FUNCTION")
    # for all burn items = require fire source, noun1 must be flammable.
    # verb_noun == burn item
    # verb_noun_sem_noun == noun2 must be flammable
    # verb_noun_dir_loc as 'burn item' but with location needlessly added.

        #print(f"Verb name is in noun list: {verb_inst.name}")
    #print(f"Noun for checking: {noun}")
    #formats_for_verb = verb_inst.formats
    #print(f"Formats for verb: {formats_for_verb}")
    #noun_actions = noun_inst[0].verb_actions
    #print(f"{noun}: {noun_actions}")
    #viable_verbs = set()
    #for act in noun_actions:
    #    #print(f"Act: {act}")
    #    for action in flag_actions[act]:
    #        viable_verbs.add(action)
    #print(f"Viable verbs: {viable_verbs}")
#
    #verb_name = set()
    #verb_name.add(verb_inst.name)
    #match = viable_verbs.intersection(verb_name)
    #if match:
    #    print(f"match: {match}")


    #glass jar: {'is_container', 'can_pick_up'}
    print(f"Cannot process {input_dict} in def burn() End of function, unresolved. (Function not yet written)")

def break_item(format_tuple, input_dict):
    logging_fn()
    print("break_item FUNCTION")
    # verb_noun == break item (if it's fragile enough)
    # verb_noun_sem_noun == break item with item2
    pass

    """ ## from itemRegistry:

    def drop(self, inst: ItemInstance, location, direction, inventory_list):
    print("inventory_list")
    if inst not in inventory_list:
        return None, inventory_list
    inventory_list.remove(inst)
    print("inventory_list")
    self.move_item(inst, place=location, direction=direction)
    return inst, inventory_list
    if in inventory
    """
    print()
    print(f"Cannot process {input_dict} in def break_item() End of function, unresolved. (Function not yet written)")


def lock(format_tuple, input_dict):
    logging_fn()
    print(f"Cannot process {input_dict} in def lock() End of function, unresolved. (Function not yet written, should use open_close variant instead)")


def unlock(format_tuple, input_dict):
    logging_fn()
    print(f"Cannot process {input_dict} in def unlock() End of function, unresolved. (Function not yet written, should use open_close variant instead)")

def open_item(format_tuple, input_dict):
    logging_fn()

    verb_entry, noun_entry, _, _, _, _ = get_entries_from_dict(input_dict)

    noun_inst = noun_entry["instance"]

    inst, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst)
    if reason_val in (0, 3, 4, 5):
        is_closed, is_locked, locked_and_have_key = check_lock_open_state(noun_inst=noun_inst, verb_inst = verb_entry["instance"])

        if is_locked or locked_and_have_key:
            if len(format_tuple) < 3:
                print(f"{assign_colour(noun_inst)} is locked; you have to unlock it before it'll open.")
        elif is_closed:
            print(f"noun.is_open: {noun_inst.is_open}")
            noun_inst.is_open = True
            print(f"You open the {assign_colour(noun_inst)}.")
            print(f"noun.is_open: {noun_inst.is_open}")
    else:
        print(f"You can't open the {assign_colour(noun_inst)} right now.")

def close(format_tuple, input_dict):
    logging_fn()


    ## Use same checks for lock and unlock maybe? Not sure.
    #verb_noun == lock if noun does not require key to lock (padlock etc)
    # verb_noun_sem_noun lock noun w noun2 if noun2 is correct key and in inventory
    print(f"Cannot process {input_dict} in def close() End of function, unresolved. (Function not yet written)")

def print_children_in_container(noun_inst):
    children = registry.instances_by_container(noun_inst)
    if children:
        print(f"\nThe {assign_colour(noun_inst)} contains:")
        children = ", ".join(col_list(children))
        print(f"  {children}")



def open_close(format_tuple, input_dict):
    logging_fn()

    verb_entry, noun_entry, _, _, _, _ = get_entries_from_dict(input_dict)
    noun_inst = noun_entry["instance"]

    is_closed, is_locked, locked_and_have_key = check_lock_open_state(noun_inst= noun_entry["instance"], verb_inst = verb_entry["instance"])
    if verb_entry["instance"].name in ("close", "lock"):
        if noun_inst.is_open:
            print("simple is_open check")
            print(f"is_open state now: {noun_inst.is_open}")
            print(f"You closed the {assign_colour(noun_inst)}")
            noun_inst.is_open = False
            print(f"is_open state now: {noun_inst.is_open}")

        if not is_closed and not is_locked and not locked_and_have_key:
            if verb_entry["instance"].name == "close":
                print(f"You closed the {assign_colour(noun_inst)}")
                noun_inst.is_open = False


    elif verb_entry["instance"].name == "lock":
        if not is_locked or not locked_and_have_key:
            # need to check if it needs a key to lock (some may only need a key to unlock)
            noun_inst.is_open = False
            if hasattr(noun_inst, "needs_key_to_lock"):
                key_inst = noun_inst.needs_key_to_lock
                noun_count = format_tuple.count("noun")
                if noun_count < 2:
                    print(f"You need a key to lock the {assign_colour(noun_inst)}")
                    return
                else:
                    a, sem_or_dir, b = three_parts_a_x_b(input_dict)
                    if b == key_inst:
                        print(f"You close and lock the {assign_colour(noun_inst)}")
                        noun_inst.is_open = False
                        noun_inst.is_locked = True
                        return
                print(f"You need a key to lock the {assign_colour(noun_inst)}")
                return
            else:
                print(f"You closed and locked the {assign_colour(noun_inst)}")
                noun_inst.is_locked = True
                return

    else:
        if is_closed:
            if verb_entry["instance"].name in ("close", "lock"):
                print(f"The {noun_inst["instance"].name} is already closed.")
                return
            print(f"You open the {assign_colour(noun_inst)}")
            noun_inst.is_open = True
            noun_inst.is_locked = False
            print_children_in_container(noun_inst)
            return

        elif locked_and_have_key:
            if verb_entry["instance"].name in ("close", "lock"):
                print(f"The {noun_inst["instance"].name} is already closed.")
                return
            if verb_entry["instance"].name == "open":
                print(assign_colour("You need to unlock it before you can open it. You do have the key, though...", "description"))
                return
            elif verb_entry["instance"].name == "unlock":
                print(f"You use the {noun_inst.needs_key} to unlock the {noun_inst.in_container}")
                noun_inst.is_open=True
                noun_inst.is_locked=False
                print_children_in_container(noun_inst)
                return
        else:
            if verb_entry["instance"].name in ("close", "lock"):
                if noun_inst.is_open:
                    print(f"You close the {assign_colour(noun_inst)}.")
                else:
                    print(f"The {assign_colour(noun_inst)} is already closed.")
                return
            if noun_inst.is_open:
                print(f"{assign_colour(noun_inst)} is already open.")
                return
            elif verb_entry["instance"].name == "open":
                print(assign_colour("You need to unlock it before you can open it. What you need should be around somewhere...", "description"))
                return
            elif verb_entry["instance"].name == "unlock":
                print(assign_colour("You need to find something to unlock it with first.", "description"))
                return

    print(f"Cannot process {input_dict} in def open_close() End of function, unresolved.")


def simple_open_close(format_tuple, input_dict):
    logging_fn()
    if len(format_tuple) > 2:
        open_close(format_tuple, input_dict)
        return
    verb_inst = get_verb(input_dict)
    noun_inst = get_noun(input_dict)

    if verb_inst.name == "open":
        if hasattr(noun_inst, "is_open"):
            if noun_inst.is_open == True:
                print(f"{assign_colour(noun_inst)} is already open.")
                return
            if noun_inst.is_open == False:
                if hasattr(noun_inst, "is_locked") and noun_inst.is_locked == True:
                    open_close(format_tuple, input_dict)
                    return
                print(f"noun_inst.is_open now: {noun_inst.is_open}")
                print(f"You open the {assign_colour(noun_inst)}.")
                noun_inst.is_open = True
                print(f"noun_inst.is_open now: {noun_inst.is_open}")
                return
        else:
            print(f"{assign_colour(noun_inst)} cannot be opened; this is odd. Potentially. Or maybe a totally normal thing.")
    else:
        if noun_inst.is_open == True:
            print(f"You close the {assign_colour(noun_inst)}.")
            print(f"noun_inst.is_open now: {noun_inst.is_open}")
            noun_inst.is_open = False
            print(f"noun_inst.is_open now: {noun_inst.is_open}")
            return
        if noun_inst.is_open == False:
            if hasattr(noun_inst, "is_locked") and noun_inst.is_locked == True:
                open_close(format_tuple, input_dict)
                return
            print(f"{assign_colour(noun_inst)} is already closed.")
            return

    print(f"Cannot process {input_dict} in def simple_open_close() End of function, unresolved.")


def combine(format_tuple, input_dict):
    logging_fn()
    #if verb_noun_sem_noun, verb_noun_dir_noun, combine a+b
    #if verb_noun == what do you want to combine it with.
    print("COMBINE FUNCTION")

    print(f"Cannot process {input_dict} in def combine() End of function, unresolved. (Function not yet written)")
    pass

def separate(format_tuple, input_dict):
    logging_fn()
    #if verb_noun_sem_noun, verb_noun_dir_noun, combine a+b
    #if verb_noun == what do you want to combine it with.
    print("SEPARATE FUNCTION")

    print(f"Cannot process {input_dict} in def separate() End of function, unresolved. (Function not yet written)")
    pass

def combine_and_separate(format_tuple, input_dict):
    logging_fn()

    print(f"length of format list: {len(format_tuple)}")

    print(f"Cannot process {input_dict} in def separate_and_combine() End of function, unresolved. (Function not yet written)")

def move(format_tuple, input_dict):
    logging_fn()

    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)
    if location_entry: # so if it's 'move to graveyard', it just treats it as 'go to'.
        go(format_tuple, input_dict, location_entry["instance"])
        return
    print(f"Cannot process {input_dict} in def move() End of function, unresolved.")

def turn(format_tuple, input_dict):
    logging_fn()

    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    if location_entry:
        current_location, current_turning = current_location()
        if location_entry["instance"] != current_location and cardinal_entry:
            print(f"You're not at {location_entry["instance"].the_name}; you can only turn where you already are.")
            return

    if cardinal_entry:
        turn_cardinal(cardinal_entry["instance"])
        return

    if semantic_entry and semantic_entry["str_name"] == "around" and len(format_tuple) == 2:
        invert_cardinals = {
            "south": "north",
            "north":"south",
            "east": "west",
            "west": "east"
            }

        new_cardinal_str = invert_cardinals[loc.current.name]
        new_cardinal = loc.by_cardinal_str(new_cardinal_str)
        turn_cardinal(new_cardinal)
        return

    if direction_entry and direction_entry["str_name"] in ("left", "right"):
        turn_cardinal(direction_entry["str_name"])
        return

    print(f"Cannot process {input_dict} in def turn() End of function, unresolved.")
    #return "new_cardinal", new_cardinal

def take(format_tuple, input_dict):
    logging_fn()

    added_to_inv = False

    def can_take(noun_inst):
        added_to_inv = False

        inst, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst)
        print(f"TAKE: {reason_val} Meaning: {meaning}")
        if reason_val not in (0, 3, 4, 5):
            print(f"Sorry, you can't take the {assign_colour(noun_inst)} right now.")
            return 1, added_to_inv
            #print(f"Reason code: {reason_val}")
        elif reason_val == 5:
            print(f"{assign_colour(noun_inst)} is already in your inventory.")
            return 1, added_to_inv
        else:
            import verb_membrane
            can_pickup = verb_membrane.check_noun_actions(noun_inst, "take")
            if can_pickup:
                print(f"CAN PICK UP {noun_inst}")
                print("VARS noun_inst")
                print(vars(noun_inst))
                if hasattr(noun_inst, "can_pick_up"):
                    print("hasattr(noun_inst, 'can_pick_up'):")
                    print(f"{hasattr(noun_inst, 'can_pick_up')}:")
                    if noun_inst.can_pick_up:
                        print("noun_inst.can_pick_up")
                        if reason_val in (3, 4):
                            registry.move_from_container_to_inv(noun_inst, inventory=game.inventory, parent=container)
                            if noun_inst in game.inventory:
                                added_to_inv = True
                                return 0, added_to_inv
                        elif reason_val == 0:
                            print("About to try to pick up")
                            registry.pick_up(noun_inst, inventory_list=game.inventory) ## the can_take function shouldn't be doing this part.
                            print("Did pick_up")
                            if noun_inst in game.inventory:
                                added_to_inv = True
                                return 0, added_to_inv
                    else:
                        print(f"You can't pick up the {assign_colour(noun_inst)}, it's either too heavy or stuck somehow.")
                        return 1, added_to_inv
            else:
                print(f"You can't pick up the {assign_colour(noun_inst)}.")
                return 1, added_to_inv

    if format_tuple in (("verb", "noun"), ("verb", "direction", "noun")):

        noun_idx = format_tuple.index("noun")
        noun_inst = inst_from_idx(input_dict[noun_idx], "noun")
        cannot_take, added_to_inv = can_take(noun_inst)

        if cannot_take and hasattr(noun_inst, "can_consume"):
            print(f"\nDid you mean to consume the {assign_colour(noun_inst)}? ")
            return

    elif format_tuple == (("verb", "noun", "direction", "noun")): ## will later include scenery. Don't know how that's going to work yet.
        verb_str = input_dict[0]["verb"]["str_name"]
        if verb_str in ("take", "remove", "separate", "get"):
            #print(f"INPUT DICT FOR v,n,d,n in take: {input_dict}")
            noun_idx = format_tuple.index("noun")
            noun_inst = inst_from_idx(input_dict[noun_idx], "noun")
            dir_inst = inst_from_idx(input_dict[noun_idx+1], "direction", return_str=True)
            if dir_inst not in ("and", "from"):
                print(f"dir_inst is {dir_inst}; was expecting 'from' or 'and'. May need to adjust take function.")

            container_idx = len(format_tuple) - 1
            container_inst = inst_from_idx(input_dict[container_idx], "noun")

            inst, container, reason_val, reason = registry.check_item_is_accessible(noun_inst)
            print(f"REASON: {reason_val} / {reason}")
            if reason_val not in (0, 3, 4):
                #print(f"Cannot take {noun_inst.name}.")
                #print(f"Reason code: {reason_val}")
                print(f"Sorry, you can't take the {assign_colour(noun_inst)} right now.")
                if reason_val == 2:
                    print(f"{assign_colour(noun_inst)} is already in your inventory.")
            else:
                if container == container_inst and reason_val in (3, 4):
                    registry.move_from_container_to_inv(noun_inst, inventory=game.inventory, parent=container)
                    if noun_inst in game.inventory:
                        added_to_inv = True
                    else:
                        print("Tried to add {assign_colour(noun_inst)} to inventory, but something must have gone wrong.")
                        traceback_fn()
                else:
                    print(f"The {assign_colour(noun_inst)} doesn't seem to be in {container_inst.name}.")

    else:
        print(f"Cannot process {input_dict} in def take() End of function, unresolved.")
        return

    if added_to_inv:
        print(f"{assign_colour(noun_inst)} is now in your inventory.")
        return

def put(format_tuple, input_dict, location=None):
    logging_fn()
    print("Put varies depending on the format.")
    print(f"Format list: {format_tuple}")
    action_word = "You put"

    print(f"Input dict: {input_dict}")
    count, parts = get_elements(input_dict)

    noun_count = format_tuple.count("noun")
    if noun_count == 2:
        sem_or_dir = get_dir_or_sem_if_singular(input_dict)
        noun_1 = get_noun(input_dict)
        noun_2 = get_noun(input_dict, 2)

        #if registry.by_container.get(noun_1):
        #    print("registry.by_container.get(noun_1): ", registry.by_container.get(noun_1))
        #    if noun_2 in registry.by_container[noun_1]:
        #        print(f"Cannot put {assign_colour(noun_1)} in {assign_colour(noun_2)}, as {assign_colour(noun_2)} is already inside {assign_colour(noun_1)}. You'll need to remove it first.")
        #        return

        if hasattr(noun_2, "contained_in"):
            container = noun_2.contained_in
            print(f"{noun_2}.contained_in: {noun_2.contained_in}")
            print(f"Container: {container}, type: {container}")
            if noun_1 == container:
                print(f"Cannot put {assign_colour(noun_1)} in {assign_colour(noun_2)}, as {assign_colour(noun_2)} is already inside {assign_colour(noun_1)}. You'll need to remove it first.")
                return
            #print("noun_1 is in a container")
            #print(f"noun_2.children: {noun_2.children}")
            #if noun_1 in noun_2.children:
            #    print(f"Cannot put {assign_colour(noun_1)} in {assign_colour(noun_2)}, as {assign_colour(noun_2)} is already inside {assign_colour(noun_1)}. You'll need to remove it first.")
            #    return
        if noun_1 == noun_2:
            print(f"You cannot put the {assign_colour(noun_1)} in itself.")
            return
        if sem_or_dir in ("in", "to") and len(format_tuple) == 4:
            registry.move_item(inst=get_noun(input_dict), new_container=(get_noun(input_dict, 2)))
            if get_noun(input_dict) in game.inventory: # this allows for an item to be locally present but not picked up to be added to a container. Not sure if I want this or not. Will have to use the not-yet-implemented self.discovered flag.
                game.inventory.remove(get_noun(input_dict))
            if get_noun(input_dict) in game.inventory:
                print(f"{assign_colour(get_noun(input_dict))} still in inventory, something went wrong.")
            else:
                from misc_utilities import smart_capitalise
                text = smart_capitalise(f"{action_word} {assign_colour(get_noun(input_dict))} {sem_or_dir} {assign_colour(get_noun(input_dict, 2))}")
                print(text)
            return


    #print(f"Parts: {parts}")
    if isinstance(parts, ItemInstance):
        a=parts
        move_a_to_b(a=a, b=location, action=action_word, current_loc=location)

    elif len(parts) == 3: # put paperclip down
        if list(input_dict[2].values())[0] in down_words:
            a = list(input_dict[1].values())[0]
            move_a_to_b(a=a, b=location, action=action_word, current_loc=location)

    elif len(parts) == 4:
        a, sem_or_dir, b = three_parts_a_x_b()
        move_a_to_b(a=a, b=b, action=action_word, direction=sem_or_dir, current_loc=location)


    elif len(parts) == 5:
        a, sem_or_dir, b, sem_or_dir_2, c = five_parts_a_x_b_in_c(input_dict)
        if c == location:
            move_a_to_b(a=a, b=b, action=action_word, direction=sem_or_dir, current_loc=location)

    print(f"Cannot process {input_dict} in def put() End of function, unresolved.")

def throw(format_tuple, input_dict):
    logging_fn()
    # verb_noun == where do you want to throw it (unless context),
    # verb_noun_dir == throw ball up (check if 'dir' makes sense)
    # verb_noun_dir_noun  == throw ball at tree

    print(f"Cannot process {input_dict} in def throw() End of function, unresolved. (Function not yet written)")


def push(format_tuple, input_dict):
    logging_fn()
    # verb_noun == to move things out the way in general
    # verb_noun_dir == #push box left
    # verb_noun_dir_noun == push box away from cabinet

    print(f"Cannot process {input_dict} in def push() End of function, unresolved. (Function not yet written)")


def drop(format_tuple, input_dict):
    logging_fn()

    action_word = "You dropped"
    #print("This is the drop function.")

    _, location = get_current_loc() # don't know if separating the tuple is making life harder for myself here...
    if len(input_dict) == 3:
        direction = get_dir_or_sem_if_singular(input_dict)
        if input_dict[1].get("noun") and input_dict[2].get("direction") and direction == "here":
            input_dict.pop(2, None)

    #print(f"FORMAT: {format_tuple}\n INPUT DICT: \n{input_dict}\n")
    if len(input_dict) == 2:
        #print(f"location: {location}")
        if input_dict[1].get("noun"):
            noun_inst = input_dict[1]["noun"]["instance"]
            _, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst)

            if reason_val == 5:
                    #print(f"noun_inst.name: {noun_inst.name}")
                    trial = move_a_to_b(a=noun_inst, b=location, action=action_word)
                    if trial:
                        idx = game.inventory.index(noun_inst)
                        game.inventory.pop(idx)
            elif reason_val == 3:
                print(f"You can't drop the {assign_colour(noun_inst)}; you'd need to get it out of the {assign_colour(container)} first.")
            else:
                print(f"You can't drop the {assign_colour(noun_inst)}; you can't drop something you aren't carrying.")
            return
        print(f"Cannot process {input_dict} in def drop(); 4 long but direction str is not suitable.")

    elif len(input_dict) == 4:
        item_to_place, direction, container_or_location = three_parts_a_x_b(input_dict)

        if direction in ["in", "into", "on", "onto", "at"]:
            noun_inst = item_to_place["instance"]
            _, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst)
            print(f"meaning: {meaning}")
            if reason_val in (0, 3, 4, 5):
                move_a_to_b(a=item_to_place, b=container_or_location, action=action_word, direction=direction)
                return
            print(f"Couldn't move {noun_inst.name} because {meaning}")
        else:
            print(f"Cannot process {input_dict} in def drop(); 4 long but direction str is not suitable.")
            return

    print(f"Cannot process {input_dict} in def drop() End of function, unresolved.")


def set_action(format_tuple, input_dict):
    logging_fn()
    # verb_noun_dir == set item down == drop
    # verb_noun_dir_noun == set item on fire if noun2 == 'fire' == burn
    # verb_dir_noun_sem_noun set on fire with item
    print(f"Cannot process {input_dict} in def set() End of function, unresolved. (Function not yet written)")




def use_item_w_item(format_tuple, input_dict):
    logging_fn()
    print(f"Format list: {format_tuple}")
    print(f"Length format list: {len(format_tuple)}")
    ## use x on y
    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict()
    if format_tuple == (('verb', 'noun', 'direction', 'noun')):
        if verb_entry["str_name"] == "use" and ((direction_entry and direction_entry["str_name"] == "on") or (semantic_entry and semantic_entry["str_name"] == "with")):
            closed, locked, locked_have_key = check_lock_open_state(noun_entry["instance"], verb_entry["instance"])
            if locked_have_key:
                if noun_entry["instance"].name == input_dict[3]["verb"]["instance"].children:
                    print(f"input_dict[3]['verb']['instance']: {input_dict[3]['verb']['instance']} == child")

    print(f"Cannot process {input_dict} in def use_item_w_item() End of function, unresolved. (Function partially written but doesn't do anything.)")

def use_item(format_tuple, input_dict):
    logging_fn()
    print(f"format_tuple = {format_tuple}")
    if len(format_tuple) == 4:
        use_item_w_item(format_tuple, input_dict)
        return
    print(f"Cannot process {input_dict} in def use_item() End of function, unresolved. (Function not yet written)")


def router(viable_format, inst_dict):
    logging_fn()

    verb_inst = None
    quick_list = []
    for v in inst_dict.values():
        for data in v.values():
            quick_list.append(data["str_name"])
    MOVE_UP = "\033[A"
    #print(f'{MOVE_UP}{MOVE_UP}\n\033[1;32m[[  {" ".join(quick_list)}  ]]\033[0m\n') ## TODO put this back on when the testing's done.
    #print(f"Dict for output: {inst_dict}")

    for data in inst_dict.values():
        for kind, entry in data.items():
            if kind == "verb":
                verb_inst = entry["instance"]
            if kind == "meta" and verb_inst == None:
                verb_inst = entry["str_name"]

    function_dict = {
        "meta": meta,
        "attributes": item_attributes,
        "go": go,
        "leave": go,

        "look": look,

        "read": read,
        "eat": eat,
        "clean": clean,
        "burn": burn,
        "break": break_item,

        "lock": lock,
        "unlock": unlock,
        "open": simple_open_close,#open_close,#open_item,
        "close": simple_open_close,#open_close,#close,

        "combine": combine,
        "separate": take,

        "use": use_item,
        "move": move,
        "turn": turn,
        "take": take,
        "put": put,
        "throw": throw,
        "push": push,
        "drop": drop,
        "set": set_action
    }

    if isinstance(verb_inst, str):
        func = function_dict["meta"]
    elif len(viable_format) in (1, 2) and list(inst_dict[0].keys())[0] in ("location", "direction", "cardinal"):
        func = function_dict["go"]
    else:
        func = function_dict[verb_inst.name]

    response = func(format_tuple = viable_format, input_dict = inst_dict)

    return response
