
### Interface between item_actions and the verbs.

#import time
from calendar import c
from time import sleep
from logger import logging_fn, traceback_fn
from env_data import cardinalInstance, locRegistry as loc, placeInstance
from interactions import item_interactions
from interactions.player_movement import new_relocate, turn_around
from itemRegistry import ItemInstance, registry
from misc_utilities import assign_colour, col_list, generate_clean_inventory, is_plural_noun
from printing import print_yellow
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

def set_noun_attr(*values, noun:ItemInstance):
    logging_fn()

    if hasattr(noun, "event") and getattr(noun, "event"):
        if hasattr(noun, "is_event_key") and noun.is_event_key:
            from eventRegistry import events
            events.is_event_trigger(noun, noun.location, values)

    for item_val in values:
        #print(f"Values: {values}")
        #print(f"item_val in values: {item_val}")
        item, val = item_val
        setattr(noun, item, val)
        #noun.event = None # Once it's served its purpose, stop it being an event obj. TODO add a proper function here to remove it from anywhere it's stored. Need to formalise the language for that first though. This works for now as the padlock can now be picked up.


def is_loc_current_loc(location=None, cardinal=None):
    logging_fn()

    current_location, current_cardinal = get_current_loc()
    if location and location == current_location:
        return 1, current_location, current_cardinal
    if not location and cardinal: ## so it can check if the facing direction is current without needing location.
        if cardinal == current_cardinal:
            return 1, current_location, current_cardinal
    return 0, current_location, current_cardinal # 0 if not matching. Always returns current.

def get_transition_noun(noun, format_tuple, input_dict):
    logging_fn()
    local_items_list = registry.get_item_by_location(loc.current)
    if hasattr(noun, "is_loc_exterior"):
        if hasattr(noun, "transition_objs"):
            if isinstance(noun.transition_objs, ItemInstance):
                noun = noun.transition_objs
                return noun

            else:
                if len(noun.transition_objs) == 1:
                    for neW_noun in noun.transition_objs:
                        return neW_noun
                else:
                    print(f"More than one transition object for {noun}. Can't deal with this yet. Exiting.")
                    exit()
    if not noun:
        if get_location(input_dict):
            location = get_location(input_dict)
            if hasattr(location, "entry_item"):
                loc_item = location.entry_item
                if isinstance(loc_item, str):
                    for loc_item in local_items_list:
                        if loc_item.name == loc_item:
                            noun = loc_item
                            return noun

                elif isinstance(loc_item, ItemInstance):
                    if local_items_list and loc_item in local_items_list:
                        noun = loc_item
                        return noun

    return noun

def move_a_to_b(a, b, action=None, direction=None, current_loc = None):
    logging_fn()

    location = None
    from item_definitions import container_limit_sizes
   ## This is the terminus of any 'move a to b' type action. a must be an item instance, b may be an item instance (container-type) or a location.
    if not direction:
        if action == "dropping" or action == "you dropped the":
            direction = "at"
        else:
            direction = "to"
    if not action:
        action = "moving"

    if isinstance(a, ItemInstance):
        if not b:
            b = loc.current
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

    #if reason_val in (0, 3, 4, 5, 8): # all 'not closed/locked container options
    if hasattr(noun_inst, "is_open") and not noun_inst.is_open:
        is_closed = True
    if hasattr(noun_inst, "is_locked") and noun_inst.is_locked:
        is_locked = True
        if hasattr(noun_inst, "needs_key"):
            inst, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst.needs_key)
            if reason_val in (0, 3, 4, 5):
                locked_have_key = True

    return is_closed, is_locked, locked_have_key

def can_interact(noun_inst): # succeeds if accessible

    _, _, reason_val, meaning = registry.check_item_is_accessible(noun_inst)
    if reason_val in (0, 3, 4, 5, 8):
        return 1, reason_val
    else:
        return 0, reason_val

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
                    #print(f"More than one `noun`: {noun_entry} already exists, {entry} will be ignored.")
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

def get_cardinal(input_dict:dict) -> ItemInstance:
    logging_fn()
    for i, _ in enumerate(input_dict):
        if input_dict[i].get("cardinal"):
            return list(input_dict[i].values())[0]["instance"]

def get_location(input_dict:dict) -> ItemInstance:
    logging_fn()
    for i, _ in enumerate(input_dict):
        if input_dict[i].get("location"):
            return list(input_dict[i].values())[0]["instance"]
    get_cardinal(input_dict) # so it tries automatically if fails to get loc.

def get_verb(input_dict:dict) -> ItemInstance:
    logging_fn()
    if input_dict[0].get("verb"):
        return list(input_dict[0].values())[0]["instance"] # works as long as verb is always first


def get_noun(input_dict:dict, x_noun:int=None, get_str=False) -> ItemInstance:
    logging_fn()
    # x_noun: 1 == 1st noun, 2 == "2nd noun", etc. Otherwise will always return the first found.

    noun_counter = 0
    for data in input_dict.values():
        for kind, entry in data.items():
            if "noun" in kind:
                if x_noun:
                    noun_counter += 1
                    if noun_counter == x_noun:
                        if get_str:
                            return entry["text"]
                        return entry["instance"]
                else:
                    if get_str:
                        return entry["text"]
                    return entry["instance"]

    #print(f"get_noun failed to find the noun instance: {input_dict}")

def get_location(input_dict:dict, get_str=False) -> cardinalInstance|placeInstance:
    logging_fn()
    # x_noun: 1 == 1st noun, 2 == "2nd noun", etc. Otherwise will always return the first found.

    for data in input_dict.values():
        for kind, entry in data.items():
            if "location" in kind:
                if get_str:
                    return entry["text"]
                else:
                    return entry["instance"]


def get_dir_or_sem_if_singular(input_dict:dict) -> str:
    logging_fn()
    for data in input_dict.values():
        for kind, entry in data.items():
            if "direction" in kind or "sem" in kind:
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

def three_parts_a_x_b(input_dict):
    logging_fn()
    noun_1 = get_noun(input_dict)
    noun_2 = get_noun(input_dict, 2)
    sem_or_dir = get_dir_or_sem_if_singular(input_dict)

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
        if prospective_cardinal == "left":
            new_int = int((turning_dict[current_facing] + 1)%4)
        else:
            new_int = int((turning_dict[current_facing] - 1)%4)

        for k, v in turning_dict.items():
            if v == new_int:
                prospective_cardinal = loc.by_cardinal_str(k)


    if isinstance(prospective_cardinal, dict):
        test = prospective_cardinal.get("cardinal")
        if test:
            prospective_cardinal = test.get("instance")
        else:
            test = prospective_cardinal.get("instance")
            if test:
                prospective_cardinal = test

    from interactions.player_movement import check_loc_card
    to_loc, to_card, is_same_loc, is_same_card = check_loc_card(location=None, cardinal=prospective_cardinal)
    from env_data import get_loc_descriptions

    if not is_same_card:
    #if not bool_test:
        if not to_card.cardinal_data:
            if hasattr(to_card.place, "missing_cardinal"):
                print(assign_colour(to_card.place.missing_cardinal, "event_msg"))

            else:
                print(assign_colour("There's nothing over that way.", colour="event_msg"))

            print(assign_colour("\n    You decide to turn back.\n", colour="event_msg"))
            get_loc_descriptions(place=loc.currentPlace)
            print(loc.current.description)
            return

        else:
            turn_around(to_card)
    else:
        if turning:
            print(f"You're already facing the {assign_colour(loc.current, card_type="ern_name")}.\n")
        else:
            print(f"You're facing the {assign_colour(loc.current, card_type="place_name")}.")
            get_loc_descriptions(place=loc.currentPlace)
            print(loc.current.description)

        return "no_change", None


#######################

def meta(format_tuple, input_dict):
    logging_fn()

    for idx in input_dict:
        for kind, entry in input_dict[idx].items():
            if kind == "meta":
                meta_verb = entry["str_name"]

    if meta_verb == "help":
        print_yellow("Type words to progress, 'i' for 'inventory', 'd' to describe the environment, 'settings' for settings, 'show visited' to see where you've been this run: - that's about it.")
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
        exit("Okay, quitting the game. Goodbye!\n\n")
        return
    elif meta_verb == "update_json":
        from testclass import add_confirms
        add_confirms()
        return
    else:
        from interactions.meta_commands import meta_control

        noun = get_noun(input_dict)
        location = get_location(input_dict)
        cardinal = get_cardinal(input_dict)

        meta_control(format_tuple, noun, location, cardinal)
        return

def go(format_tuple, input_dict): ## move to a location/cardinal/inside
    logging_fn()

    current_loc, current_card = get_current_loc()

    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    if (direction_entry and direction_entry["str_name"] in to_words and len(format_tuple) < 5) or (not direction_entry and len(format_tuple) < 4) or (direction_entry and not cardinal_entry and not location_entry):
        if location_entry and not cardinal_entry:
            #print(f"Location entry, no card: {location_entry}")
            #print(f"location vars: \n{vars(location_entry["instance"])}")
            if location_entry["instance"] == loc.currentPlace:
                if input_dict[0].get("verb") and input_dict[0]["verb"]["str_name"] == "leave":
                    if hasattr(loc.current.place, "entry_item"):
                        #print(f"loc.current has entry item: {loc.current.place.entry_item}")
                        if enter(format_tuple, input_dict, noun=loc.current.place.entry_item):
                            return

                        #for item in loc.current.entry_item:
                        #    if item.get("exit_to_location"):
                        #        print(f"Go through the {item} to leave {loc.current}")
                    #else:
                       # print(f"No entry item for loc.current. Vars: {vars(loc.current.place)}")

                    print("You can't leave without a new destination in mind. Where do you want to go?")
                    return

            if hasattr(location_entry["instance"], "entry_item"):
                #print(location_entry["instance"].entry_item)
                if not get_noun(input_dict):
                    input_dict[len(format_tuple)] = {}
                    input_dict[len(format_tuple)]["noun"] = ({"instance": location_entry["instance"].entry_item, "str_name": location_entry["instance"].entry_item.name})
                    #print(f"input_dict: {input_dict}")

                #for cardinal in location_entry["instance"].cardinals:
                #    card = location_entry["instance"].cardinals.get(cardinal)
                #    if hasattr(card, "loc_exterior_items") or hasattr(card, "transition_objs"):
                #        new_relocate(new_cardinal=card)
                #        return
                #print("enter location via go")
                enter(format_tuple, input_dict) # Anything that needs you to go through a door goes via enter.
                return
            new_relocate(new_location=location_entry["instance"])
            return

        elif cardinal_entry and not location_entry:
            #print(f"CARDINAL ENTRY: {cardinal_entry}\nloc.current: {loc.current}, loc.current.place: {loc.current.place}, loc.currentPlace: {loc.currentPlace}")
            if cardinal_entry["instance"].place == loc.current.place:
                turn_cardinal(cardinal_entry["instance"])
                return
            else:
                new_relocate(new_location=location_entry["instance"], new_cardinal = cardinal_entry["instance"])
                return

        elif direction_entry and not location_entry and not cardinal_entry:# and verb_entry["str_name"] in ("go", "turn", "head", "travel", "move"):
            if direction_entry["str_name"] in ("left", "right"):
                turn_cardinal(direction_entry["str_name"])
                return
            else:
                if get_noun(input_dict):
                    ("Going to enter via get_noun")
                    enter(format_tuple, input_dict)
                    return
                print("If this does not have a location, it breaks. Why am I still using location_entry etc after determining they don't exist. Works if the direction is something internal, but not if I just type 'go to church', a location that doesn't exist.")
                #if len(format_tuple) == 3:
                print(f"FORMAT TUPLE: {format_tuple}")
                new_relocate(new_location=location_entry["instance"], new_cardinal = cardinal_entry["instance"])
                return

        elif location_entry and cardinal_entry:

            #print("has location and cardinal")
            new_relocate(new_location=location_entry["instance"], new_cardinal = cardinal_entry["instance"])
            return

    elif direction_entry["str_name"] in in_words:
        if location_entry.get("instance"):
            #print(f"loc vars: {vars(location_entry['instance'])}")
            if hasattr(location_entry["instance"], "entry_item"):
                #print(f"Location {location_entry['instance']} can be entered via {location_entry["instance"].entry_item}")

            #if not get_noun(input_dict):
                input_dict[len(format_tuple)] = {}
                input_dict[len(format_tuple)].setdefault("noun", dict()).setdefault("instance", location_entry['instance'].entry_item)
                input_dict[len(format_tuple)]["noun"]["str_name"] = location_entry['instance'].entry_item.name
            enter(format_tuple, input_dict)
            return
        #print(f"Can {input_dict[1]["direction"]["str_name"]} be entered?")
        #print("This isn't done yet.")

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


def look(format_tuple=None, input_dict=None):
    logging_fn()

    if not format_tuple or (format_tuple == tuple(("verb", "sem")) and not input_dict):
        from misc_utilities import look_around
        look_around()
        return

    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)
    noun = get_noun(input_dict)

    if len(format_tuple) == 1 or (len(format_tuple) == 2 and semantic_entry != None and input_dict[1]["sem"]["str_name"] == "around"):
        from misc_utilities import look_around
        look_around()

    elif len(format_tuple) == 2:
        if cardinal_entry != None:
            turn_cardinal(cardinal_entry["instance"], turning = False)

        elif direction_entry != None: # if facing north, turn east, etc.)
            intended_direction = direction_entry["str_name"]
            if intended_direction in ("left", "right"):
                turn_cardinal(intended_direction, turning=False)

        elif noun:
            item_interactions.look_at_item(noun)

    elif len(format_tuple) == 3:
        if noun and format_tuple[1] == "direction":
            item_interactions.look_at_item(noun)
        elif format_tuple[2] == "cardinal" and format_tuple[1] == "direction":
            turn_cardinal(inst_from_idx(input_dict[2], "cardinal"), turning = False)

    elif len(format_tuple) == 4:
        if cardinal_entry and location_entry:
            if location_entry["instance"] != loc.currentPlace:
                print(f"You can only look at locations you're currently in. You'll need to go to {location_entry["instance"].name} first.")
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
        #if "verb" in format_tuple and "location" in format_tuple:
            print(f"You want to clean the {assign_colour(get_location(input_dict))}? Not implemented yet.")
            return
    noun = get_noun(input_dict)
    noun_2 = get_noun(input_dict, 2)
    dir_or_sem = get_dir_or_sem_if_singular(input_dict)
    if noun and dir_or_sem and dir_or_sem in ("with", "using"):
        if noun_2:
#    if format_tuple == formats("verb_noun_sem_noun"):# verb_noun == clean item
            print(f"You want to clean the {assign_colour(noun)} with the {assign_colour(noun_2)}? Not implemented yet.")
            return
        elif get_location(input_dict):
            print(f"You want to clean {assign_colour(get_location(input_dict))} with {assign_colour(noun)}? Odd choice, and not one that's implemented yet.")

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

    noun = get_noun(input_dict)
    noun_2 = get_noun(input_dict, 2)

    if hasattr(noun, "can_break"):
        if not noun_2:
            print(f"What do you want to break the {assign_colour(noun)} with?")

    if noun_2:
        dir_or_sem = get_dir_or_sem_if_singular(input_dict)
        if dir_or_sem in ("with", "using", "on"):
            if hasattr(noun_2, "can_break"):
                print("Chance to break either object. Need to implement a breakability scale, so I can test which item breaks. Need to formalise the break/flammable setup overall.")


    # verb_noun == break item (if it's fragile enough)
    # verb_noun_sem_noun == break item with item2
    pass

    print()
    print(f"Cannot process {input_dict} in def break_item() End of function, unresolved. (Function not yet written)")

def check_key_lock_pairing(noun_1, noun_2):
    logging_fn()
    if hasattr(noun_1, "is_key"):
        if hasattr(noun_2, "requires_key"):
            if noun_1 == noun_2.requires_key:
                return 1
    return 0


def lock_unlock(format_tuple, input_dict, do_open=False):
    logging_fn()

    key=None
    lock=None
    verb = get_verb(input_dict)
    noun = get_noun(input_dict)
    if len(format_tuple) == 2:
        print(f"{assign_colour(noun.name)} requires a key, no?")
    elif len(format_tuple) == 4:
        #print(f"Format is len 4: {format_tuple}")
        if format_tuple.count("noun") == 2:
            #print("format tuple has 2 nouns")
            noun_1 = get_noun(input_dict)
            accessible_1, _ = can_interact(noun_1)
            noun_2 = get_noun(input_dict, 2)
            accessible_2, _ = can_interact(noun_2)
            if accessible_1 and accessible_2:
                #rint(f"{noun_1} and {noun_2} are both accessible.")
                success = check_key_lock_pairing(noun_1, noun_2)
                if success:
                    #print(f"Key {noun_1} is accessible and will open lock {noun_2}")
                    key = noun_1
                    lock = noun_2

                else:
                    success = check_key_lock_pairing(noun_2, noun_1)
                    if success:
                        #print(f"Key {noun_2} is accessible and will open lock {noun_1}")
                        key = noun_2
                        lock = noun_1
                if key and lock:
                    if lock.is_locked and not do_open:
                        print(f"You use the {assign_colour(key.name)} to unlock the {assign_colour(lock.name)}")
                        set_noun_attr(("is_locked", False), noun=lock)
                        return

                    elif lock.is_locked and do_open:
                            print(f"You use the {assign_colour(key)} to unlock the {assign_colour(lock)}, and open it.")
                            set_noun_attr(("is_locked", False), ("is_open", True), noun=lock)
                            return

                    elif not lock.is_locked:
                        print(f"You use the {assign_colour(key)} to lock the {assign_colour(lock)}.")
                        set_noun_attr(("is_open", False), ("is_locked", True), noun=lock)
                        return

                else:
                    print(f"You can't open the {assign_colour(noun_1)} with {assign_colour(noun_2)}")
                    #print(f"{noun_1} and {noun_2} are not a pairing. Key: {key}, lock: {lock}")
                    #print(f"VARS: {vars(noun_1)}\n Noun 2 vars: {vars(noun_2)}")

            else:
                print(f"{noun_1} and/or {noun_2} are not accessible: 1: {accessible_1}, 2: {accessible_2}")
        else:
            print(f"Not two nouns in {format_tuple}")

    else:
        print(f"Don't know what to do with {input_dict} in lock_unlock, not 2 or 4 len.")
    if verb.name == "lock":
        print("verbname == lock, don't know why I'm here.")
    print(f"Cannot process {input_dict} in def lock() End of function, unresolved. (Function not yet written, should use open_close variant instead)")

def open_item(format_tuple, input_dict):
    logging_fn()

    verb_entry, noun_entry, _, _, _, _ = get_entries_from_dict(input_dict)

    noun_inst = noun_entry["instance"]
    if get_noun(input_dict, 2):
        for noun in (noun_inst, get_noun(input_dict, 2)):
            if hasattr(noun, "is_key"):
                lock_unlock(format_tuple, input_dict, do_open=True)
                return

    if hasattr(noun, "is_transition_obj"):
        noun_inst = noun

    accessible, _ = can_interact(noun_inst)
    inst, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst)
    if reason_val in (0, 3, 4, 5):
        is_closed, is_locked, locked_and_have_key = check_lock_open_state(noun_inst=noun_inst, verb_inst = verb_entry["instance"])

        if is_locked or locked_and_have_key:
            if len(format_tuple) < 3:
                print(f"{assign_colour(noun_inst)} is locked; you have to unlock it before it'll open.")
        elif is_closed:
            set_noun_attr(("is_open", True), noun=noun_inst)
            print(f"You open the {assign_colour(noun_inst)}.")
            #print(f"noun.is_open: {noun_inst.is_open}")
    else:
        print(f"You can't open the {assign_colour(noun_inst)} right now.")

def close(format_tuple, input_dict):
    logging_fn()


    ## Use same checks for lock and unlock maybe? Not sure.
    #verb_noun == lock if noun does not require key to lock (padlock etc)
    # verb_noun_sem_noun lock noun w noun2 if noun2 is correct key and in inventory
    print(f"Cannot process {input_dict} in def close() End of function, unresolved. (Function not yet written)")

def print_children_in_container(noun_inst):

    children = set()
    if hasattr(noun_inst, "children"):
        children = noun_inst.children

    if children:
        print(f"\nThe {assign_colour(noun_inst)} contains:")
        children = ", ".join(col_list(children))
        print(f"  {children}")


def open_close(format_tuple, input_dict):
    logging_fn()

    noun_inst = get_noun(input_dict)

    if get_noun(input_dict, 2):
        for option in noun_inst, get_noun(input_dict, 2):
            open_item(format_tuple, input_dict)
            return
            if hasattr(option, "is_open"):
                noun_inst = option # if one of the nouns mentioned can be opened, assume we mean to open that one.

    verb_inst = get_verb(input_dict)

    inst, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst)
    if reason_val not in (0, 3, 4, 5):
        print(f"{noun_inst.name} isn't accessible, you can't interact with it.")
        print(f"[{meaning}]")
        return

    #print(f"open_close noun vars: {vars(noun_inst)}")

    if verb_inst.name == "open":
        if hasattr(noun_inst, "is_locked") and noun_inst.is_locked:
            print(f"You cannot open a locked {assign_colour(noun_inst.name)}.")
            return # not perfect because it returns even if you couldn't have accessed the door to check, but works for the moment while I'm testing the events. TODO Fix this later

## I think part of the issue is that the check_lock_open_state tries to combine both 'is this a thinkg I could access to try to unlock' with 'is this is a thing I can unlock'. I need to separate them out. a) is this a thing I can access, return. b) if so, is this a thing I can unlock.
    is_closed, is_locked, locked_and_have_key = check_lock_open_state(noun_inst, verb_inst)

    print("is_closed, is_locked, locked_and_have_key : ", is_closed, is_locked, locked_and_have_key)
    if verb_inst.name in ("close", "lock"):

        if verb_inst.name == "close":
            if not is_closed:
                print(f"You closed the {assign_colour(noun_inst)}")
                noun_inst.is_open = False

        elif verb_inst.name == "lock":
            if not is_closed:
                print(f"You need to close the {noun_inst.name} first.")
            else:
                if not is_locked and not locked_and_have_key:
    ### TODO fix this whole bit, it's a senseless mess for no reason. It's not this complicated...
                    # need to check if it needs a key to lock (some may only need a key to unlock)
                    #noun_inst.is_open = False
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
                                #noun_inst.is_open = False
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
#            if verb_inst.name in ("close", "lock"):
#                print(f"The {noun_inst["instance"].name} is already closed.")
#                return
            #print(f"Noun {noun_inst} is closed, sending to set_noun_attr")
            set_noun_attr(("is_open", True), noun=noun_inst)
            print(f"You open the {assign_colour(noun_inst)}")
            noun_inst.is_locked = False
            print_children_in_container(noun_inst)
            return

        elif locked_and_have_key:
            if verb_inst.name in ("close", "lock"):
                print(f"The {noun_inst["instance"].name} is already closed.")
                return
            if verb_inst.name == "open":
                print(assign_colour("You need to unlock it before you can open it. You do have the key, though...", "description"))
                return
            elif verb_inst.name == "unlock":
                print(f"You use the {noun_inst.needs_key} to unlock the {noun_inst.in_container}")
                noun_inst.is_open=True
                noun_inst.is_locked=False
                print_children_in_container(noun_inst)
                return
        else:
            if verb_inst.name in ("close", "lock"):
                if noun_inst.is_open:
                    print(f"You close the {assign_colour(noun_inst)}.")
                else:
                    print(f"The {assign_colour(noun_inst)} is already closed.")
                return
            if noun_inst.is_open:
                print(f"{assign_colour(noun_inst)} is already open.")
                return
            elif verb_inst.name == "open":
                print(assign_colour("You need to unlock it before you can open it. What you need should be around somewhere...", "description"))
                return
            elif verb_inst.name == "unlock":
                print(assign_colour("You need to find something to unlock it with first.", "description"))
                return

    print(f"is_closed, is_locked, locked_and_have_key: {is_closed, is_locked, locked_and_have_key}")
    print(f"Cannot process {input_dict} in def open_close() End of function, unresolved.")


def simple_open_close(format_tuple, input_dict):
    logging_fn()

    if len(format_tuple) > 2:
        open_close(format_tuple, input_dict)
        return
    verb_inst = get_verb(input_dict)
    noun_inst = get_noun(input_dict)

    if verb_inst.name == "open":
        if hasattr(noun_inst, "is_loc_exterior"):
            if hasattr(noun_inst, "is_loc_exterior"):
               noun = noun_inst.transition_objs

            if isinstance(noun, ItemInstance):
                noun_inst = noun
        if hasattr(noun_inst, "is_open"):
            if noun_inst.is_open == True:
                print(f"{assign_colour(noun_inst)} is already open.")
                return
            if noun_inst.is_open == False:
                if hasattr(noun_inst, "is_locked") and noun_inst.is_locked == True:
                    open_close(format_tuple, input_dict)
                    return
                #print(f"noun_inst.is_open now: {noun_inst.is_open}")
                _, _, reason_val, meaning  = registry.check_item_is_accessible(noun_inst)
                if reason_val in (0, 5) or (reason_val == 6 and hasattr(noun_inst, "is_transition_obj") and (hasattr(noun_inst, "enter_location") and noun_inst.enter_location == loc.current.place)):
# NOTE: This is where 'open x' goes to. I have far too many routes for opening/closing items. CULL THEM.
                    print(f"Noun {noun_inst} is closed, sending to set_noun_attr")
                    print(f"You open the {assign_colour(noun_inst)}.")
                    set_noun_attr(("is_open", True), noun=noun_inst)
                    #noun_inst.is_open = True
                    #print(f"noun_inst.is_open now: {noun_inst.is_open}")
                    return

                if reason_val == 6:
                    print(f"You can't open something you aren't nearby to...")
                    return
                else:
                    print(f"Cannot open {noun_inst.name} because {meaning}.")
                    return
        else:
            if hasattr(noun_inst, "is_loc_exterior"):
                if hasattr(noun_inst, "transition_objs"):
                    for trans_obj in noun_inst.transition_objs:
                        print(f"You can't enter the {assign_colour(noun_inst)}, but maybe the {assign_colour(trans_obj)}?")
                        return
            print(f"{assign_colour(noun_inst)} cannot be opened; this is odd. Potentially. Or maybe a totally normal thing.")
    else:
        if noun_inst.is_open == True:
            print(f"You close the {assign_colour(noun_inst)}.")
            #print(f"noun_inst.is_open now: {noun_inst.is_open}")
            noun_inst.is_open = False
            #print(f"noun_inst.is_open now: {noun_inst.is_open}")
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

    if get_location(input_dict) and get_dir_or_sem_if_singular(input_dict): # so if it's 'move to graveyard', it just treats it as 'go to'.
        go(format_tuple, input_dict)
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
    from eventRegistry import events
    logging_fn()

    added_to_inv = False

    def can_take(noun_inst):
        added_to_inv = False

        inst, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst)
        #print(f"TAKE: {reason_val} Meaning: {meaning}")
        if reason_val not in (0, 3, 4, 5):
            print(f"Sorry, you can't take the {assign_colour(noun_inst)} right now.")
            return 1, added_to_inv
            #print(f"Reason code: {reason_val}")
        elif reason_val == 5:
            print(f"{assign_colour(noun_inst)} is already in your inventory.")
            return 1, added_to_inv
        else:
            #can_pickup = verb_membrane.check_noun_actions(noun_inst, "take")
            if noun_inst.can_pick_up:
                if hasattr(noun_inst, "can_pick_up") and noun_inst.can_pick_up == True:
                    if reason_val in (3, 4):
                        registry.move_from_container_to_inv(noun_inst, inventory=game.inventory, parent=container)
                        if noun_inst in game.inventory:
                            added_to_inv = True
                            return 0, added_to_inv
                    elif reason_val == 0:
                        #print("About to try to pick up")
                        registry.pick_up(noun_inst, inventory_list=game.inventory) ## the can_take function shouldn't be doing this part.
                        #print("Did pick_up")
                        if noun_inst in game.inventory:
                            added_to_inv = True
                            return 0, added_to_inv
                else:
                    print(f"You can't pick up the {assign_colour(noun_inst)}.")
                    return 1, added_to_inv
            else:
                print(f"You can't pick up the {assign_colour(noun_inst)}.")
                return 1, added_to_inv

    if format_tuple in (("verb", "noun"), ("verb", "direction", "noun")):

        noun_inst = get_noun(input_dict)
        noun_loc = noun_inst.location
        cannot_take, added_to_inv = can_take(noun_inst)

        if cannot_take and hasattr(noun_inst, "can_consume"):
            print(f"\nDid you mean to consume the {assign_colour(noun_inst)}? ")
            return

    elif format_tuple == (("verb", "noun", "direction", "noun")): ## will later include scenery. Don't know how that's going to work yet.
        verb_str = input_dict[0]["verb"]["str_name"]
        if verb_str in ("take", "remove", "separate", "get"):
            noun_inst = get_noun(input_dict)
            noun_loc = noun_inst.location
            dir_inst = get_dir_or_sem_if_singular(input_dict)
            if dir_inst not in ("and", "from"):
                print(f"dir_inst is {dir_inst}; was expecting 'from' or 'and'. May need to adjust take function.")

            container_inst = get_noun(input_dict, 2)

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
        #print(f"{assign_colour(noun_inst)} is now in your inventory.") # original
        print(f"The {assign_colour(noun_inst)} {is_plural_noun(noun_inst)} now in your inventory.")
        events.is_event_trigger(noun_inst, noun_loc, reason = "item_in_inv")
        return

def put(format_tuple, input_dict, location=None):
    logging_fn()
    action_word = "You put"

    noun_1 = get_noun(input_dict)
    noun_2 = get_noun(input_dict, 2)
    sem_or_dir = get_dir_or_sem_if_singular(input_dict)

    if noun_2:

        if hasattr(noun_2, "contained_in") and noun_1 == noun_2.contained_in:
                print(f"Cannot put {assign_colour(noun_1)} in {assign_colour(noun_2)}, as {assign_colour(noun_2)} is already inside {assign_colour(noun_1)}. You'll need to remove it first.")
                return

        if noun_1 == noun_2:
            print(f"You cannot put the {assign_colour(noun_1)} in itself.")
            return
        if sem_or_dir in ("in", "to", "into", "inside") and len(format_tuple) == 4:
            if hasattr(noun_1, "contained_in") and noun_2 == noun_1.contained_in:
                print(f"{noun_2.name} is already in {noun_1}")
                return
            registry.move_item(inst=get_noun(input_dict), new_container=(get_noun(input_dict, 2)))
            if noun_1 in game.inventory:
                game.inventory.remove(get_noun(input_dict))
                if noun_1 in game.inventory:
                    exit(f"{assign_colour(get_noun(input_dict))} still in inventory, something went wrong.")
            else:
                from misc_utilities import smart_capitalise
                text = smart_capitalise(f"{action_word} {assign_colour(get_noun(input_dict))} {sem_or_dir} {assign_colour(get_noun(input_dict, 2))}")
                print(text)
            return

    else:
        if sem_or_dir:
            if not noun_2:
                move_a_to_b(a=a, b=location, action=action_word, current_loc=location)
                return

        if sem_or_dir in down_words:
            move_a_to_b(a=noun_1, b=location, action=action_word, current_loc=location)
            return

        if len(format_tuple) == 5:
            a, sem_or_dir, b, sem_or_dir_2, c = five_parts_a_x_b_in_c(input_dict)
            if c == location:
                move_a_to_b(a=a, b=b, action=action_word, direction=sem_or_dir, current_loc=location)
                return

    print(f"Cannot process {input_dict} in def put() End of function, unresolved.")

def throw(format_tuple, input_dict):
    logging_fn()

    noun = get_noun(input_dict)
    if not noun:
        print("What do you want to throw?")
        return
    if len(format_tuple) == 2:
        print(f"Where do you want to throw the {assign_colour(noun)}?")
        return
    dir_or_sem = get_dir_or_sem_if_singular(input_dict)
    if dir_or_sem and dir_or_sem in down_words:
        move_a_to_b(noun, loc.current, "You drop the", "to leave it at the")


    # verb_noun == where do you want to throw it (unless context),
    # verb_noun_dir == throw ball up (check if 'dir' makes sense)
    # verb_noun_dir_noun  == throw ball at tree

    print(f"Cannot process {input_dict} in def throw() End of function, unresolved. (Function not yet written)")


def push(format_tuple, input_dict):
    logging_fn()
    noun = get_noun(input_dict)
    if "door_window" in noun.item_type:
        if hasattr(noun, "can_be_opened"):
            if noun.is_open:
                print(f"You push against the {assign_colour(noun)}, but it doesn't move much further.")
            elif not noun.is_open:
                if noun.is_locked:
                    print(f"You push against the {noun}, but it doesn't budge.")
                else:
                    print(f"You push against the {noun}, and it opens just enough for you to see inside.")
                    if noun.location == loc.current:
                        if noun.exit_to_location == loc.current.place:
                            enter(format_tuple, input_dict)
                    else:
                        print("No description here. Should be one eventually.")


    # verb_noun == to move things out the way in general
    # verb_noun_dir == #push box left
    # verb_noun_dir_noun == push box away from cabinet

    print(f"Cannot process {input_dict} in def push() End of function, unresolved. (Function not yet written)")


def drop(format_tuple, input_dict):
    logging_fn()

    action_word = "you dropped the"
    #print("This is the drop function.")

    _, location = get_current_loc() # don't know if separating the tuple is making life harder for myself here...
    noun_1 = get_noun(input_dict)

    if len(input_dict) == 3:
        direction = get_dir_or_sem_if_singular(input_dict)
        if noun_1 and direction and (direction == "here" or direction in down_words):
            input_dict.pop(2, None)

    #print(f"FORMAT: {format_tuple}\n INPUT DICT: \n{input_dict}\n")
    if len(input_dict) == 2:
        #print(f"location: {location}")
        if input_dict[1].get("noun"):
            _, container, reason_val, meaning = registry.check_item_is_accessible(noun_1)

            if reason_val == 5:
                registry.drop(noun_1, game.inventory)
                print(f"Dropped the {assign_colour(noun_1)} onto the ground here at the {assign_colour(loc.current, card_type='ern_name')}")


            elif reason_val == 3:
                print(f"You can't drop the {assign_colour(noun_1)}; you'd need to get it out of the {assign_colour(container)} first.")
                return

            else:
                print(f"You can't drop the {assign_colour(noun_1)}; you can't drop something you aren't carrying.")
                return

    elif len(input_dict) == 4:
        dir_or_sem = get_dir_or_sem_if_singular(input_dict)
        #item_to_place, direction, container_or_location = three_parts_a_x_b(input_dict)
        #print(f"item_to_place: {item_to_place}, direction: {direction}, dir type: {type(direction)}")
        if dir_or_sem in ["in", "into", "on", "onto", "at"]:
            if get_location(input_dict):
                if get_location(input_dict) != loc.current:
                    print(f"You can't drop the {assign_colour(noun_1)} at {assign_colour(get_location(input_dict))} because you aren't there.")
                    return

            _, container, reason_val, meaning = registry.check_item_is_accessible(noun_1)
            print(f"meaning: {meaning}")
            if reason_val in (0, 3, 4, 5):
                if get_noun(input_dict, 2):
                    registry.move_item(noun_1, new_container=get_noun(input_dict, 2))
                    #move_a_to_b(a=item_to_place, b=container_or_location, action=action_word, direction=direction)
                    item_interactions.add_item_to_loc()

            else:
                print(f"Couldn't move {noun_1.name} because {meaning}")
        else:
            print(f"Cannot process {input_dict} in def drop(); 4 long but direction str is not suitable.")
            return

    if noun_1 not in game.inventory:
        from eventRegistry import events
        events.is_event_trigger(noun_1, noun_1.location, reason = "item_not_in_inv")
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
    #print(f"Format list: {format_tuple}")
    #print(f"Length format list: {len(format_tuple)}")
    ## use x on y
    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)
    if format_tuple == (('verb', 'noun', 'direction', 'noun')):
        if verb_entry["str_name"] == "use" and ((direction_entry and direction_entry["str_name"] == "on") or (semantic_entry and semantic_entry["str_name"] == "with")):
            # need to figure out the best way to divert from here to lock_unlock, so we don't repeat it over an over.
            # Maybe just if one of the nouns == is_key?
            actor_noun = get_noun(input_dict)
            target_noun = get_noun(input_dict, 2)
            for noun in (actor_noun, target_noun):
                if hasattr(noun, "is_key"):
                    lock_unlock(format_tuple, input_dict)
                    return
            print(f"Apparently neither {actor_noun} or {target_noun} are is_key?")
            if hasattr(target_noun, "requires_key"):
                key_is_accessible=False
                if actor_noun == target_noun.requires_key:
                    _, container, reason_val, meaning = registry.check_item_is_accessible(actor_noun)
                    print(f"meaning: {meaning}")
                    if reason_val in (0, 3, 4, 5, 8):
                        key_is_accessible=True
                    _, container, reason_val, meaning = registry.check_item_is_accessible(target_noun)
                    print(f"meaning: {meaning}")
                    if reason_val in (0, 3, 4, 5, 8):
                        if key_is_accessible:
                            print("You use the key to open the lock.")
                            print("Though it does't actually do it yet, I'm just testing. This whole thing needs rewriting.")
                            target_noun.is_locked=False
                            return

            closed, locked, locked_have_key = check_lock_open_state(actor_noun, verb_entry["instance"])
            print(f"Actor-noun: {actor_noun}, target-noun: {target_noun}. Closed: {closed}, locked: {locked}, locked and have key: {locked_have_key}")
            if locked_have_key:
                if noun_entry["instance"].name == input_dict[3]["verb"]["instance"].children:
                    print(f"input_dict[3]['verb']['instance']: {input_dict[3]['verb']['instance']} == child")

    print(f"Cannot process {input_dict} in def use_item_w_item() End of function, unresolved. (Function partially written but doesn't do anything.)")

def use_item(format_tuple, input_dict):
    logging_fn()
    #print(f"format_tuple = {format_tuple}")
    if len(format_tuple) == 4:
        use_item_w_item(format_tuple, input_dict)
        return
    print(f"Cannot process {input_dict} in def use_item() End of function, unresolved. (Function not yet written)")

def enter(format_tuple, input_dict, noun=None):
    logging_fn()
    ### NEED TO FORMALISE DOORS/TRANSITION OBJECTS.
    # just realised you can add str to exit like you can with print/input: exit(code="Exiting because reason given above.")
    if not noun:
        if format_tuple == ("verb", "noun", "noun"):
            noun = get_noun(input_dict, 2)
        else:
            noun = get_noun(input_dict)

    #if hasattr(noun, "is_loc_exterior"):
    #    print(f"{noun} is a location exterior object, this will work later.")
    if not noun or hasattr(noun, "is_loc_exterior") or hasattr(noun, "is_transition_obj"):
        noun = get_transition_noun(noun, format_tuple, input_dict)

    if hasattr(noun, "enter_location"):
        #print(f"noun.enter_location: {noun.enter_location}")
        inside_location = noun.enter_location ## Noun must have both enter loc and exit_to_loc if it has either.
        outside_location = noun.exit_to_location
        if hasattr(noun, "exit_to_location"):
            if outside_location == loc.current.place:
                if hasattr(noun, "is_open") and noun.is_open == True:
                    print(assign_colour("The door creaks, but allows you to head inside.", colour="event_msg"))
                    print()
                    # want like, recklessly/cautiously/quietly, depending on playstyle. Long way off that but wanted to note it.
                    return new_relocate(inside_location)
                    sleep(.02)
                    print("Done new_relocate")

                else:
                    if noun.location == loc.current:
                        print("You can't enter through a closed door.")
                    else:
                        turn_around(new_cardinal = noun.location)
                    return 1
            elif inside_location == loc.current.place:
                if not get_location(input_dict) or (get_location(input_dict) and get_location(input_dict) != loc.current):
                    if hasattr(noun, "is_open") and noun.is_open == True:
                        print(assign_colour("You head back out through the door.", colour="event_msg"))
                        new_relocate(outside_location)
                        return 1
                    else:
                        print("You can't leave through a closed door.")
                        return 1
                else:
                    print(f"You're already in the {assign_colour(loc.current.place)}.")
            else:
                print("You can't go through the door unless you're nearby to it.")
                return 1
    else:

        print(f"This {noun} doesn't lead anywhere")



def router(viable_format, inst_dict):
    logging_fn()

    verb_inst = None
    quick_list = []
    for v in inst_dict.values():
        for data in v.values():
            quick_list.append(data["str_name"])
    MOVE_UP = "\033[A"
    print(f'{MOVE_UP}{MOVE_UP}\n\033[1;32m[[  {" ".join(quick_list)}  ]]\033[0m\n') ## TODO put this back on when the testing's done.
    #print(f"Dict for output: {inst_dict}")

    for data in inst_dict.values():
        for kind, entry in data.items():
            if kind == "verb":
                verb_inst = entry["instance"]
            if kind == "meta" and verb_inst == None:
                verb_inst = entry["str_name"]

    function_dict = {
        "meta": meta,
        "attributes": item_attributes, # delete this later.
        "go": go,
        "leave": go,

        "look": look,

        "read": read,
        "eat": eat,
        "clean": clean,
        "burn": burn,
        "break": break_item,

        "lock": lock_unlock,
        "unlock": lock_unlock,
        "open": simple_open_close,#open_close,#open_item,
        "close": simple_open_close,#open_close,#close,

        "enter": enter,

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
