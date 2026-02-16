
### Interface between item_actions and the verbs.

#import time
from time import sleep
from xml.etree.ElementInclude import include
from logger import logging_fn, traceback_fn
from env_data import cardinalInstance, locRegistry as loc, placeInstance
from interactions import item_interactions
from interactions.player_movement import new_relocate, turn_around
from itemRegistry import ItemInstance, registry
from misc_utilities import assign_colour, col_list, generate_clean_inventory, is_plural_noun
from printing import print_yellow
from set_up_game import game
from verb_definitions import directions, semantics, formats

can_open_codes = [0,5,8]
can_pickup_codes = [0,3,4]
in_container_codes = [3,4]
can_lookat_codes = [0,3,4,5,8]
interactable_codes = [0,3,4,5,8]

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
down_words = ["down", "on"]

update_description_attrs = [
    "is_open", "is_broken", "is_dirty", "is_burned", "is_spoiled", "is_charged"
]
#### Fundamental Operations ####

def get_current_loc():
    logging_fn()

    from env_data import locRegistry
    location = locRegistry.currentPlace
    cardinal = locRegistry.current
    return location, cardinal

def set_noun_attr(*values, noun:ItemInstance):
    logging_fn()
    """
    'noun' must be provided at `noun=  `, as it needs to be differentiated from *values
    """
    from eventRegistry import trigger_acts, events
    if hasattr(noun, "event") and getattr(noun, "event") and hasattr(noun, "is_event_key") and noun.is_event_key:
            events.is_event_trigger(noun, noun.location, values)

    else:
        triggers = {}
        for item in trigger_acts:
            for k, v in trigger_acts[item].items():
                triggers[k] = v

        for item_val in values:
            #print(f"Values: {values}")
            #print(f"item_val in values: {item_val}")
            item, val = item_val
            #print(f"TRIGGERs: {triggers}")
            if item in triggers:
                #print(f"item in triggers: {item}")
                if val == triggers[item]:

                    events.is_event_trigger(noun, noun.location, reason = values)
            setattr(noun, item, val)

        if item in update_description_attrs:
            from itemRegistry import registry
            if hasattr(noun, "descriptions") and noun.descriptions and hasattr(noun, "event") and noun.event:
                registry.init_descriptions(noun)


def is_loc_current_loc(location=None, cardinal=None):
    logging_fn()

    current_location, current_cardinal = get_current_loc()
    if location and location == current_location:
        return 1, current_location, current_cardinal
    if not location and cardinal: ## so it can check if the facing direction is current without needing location.
        if cardinal == current_cardinal:
            return 1, current_location, current_cardinal
    return 0, current_location, current_cardinal # 0 if not matching. Always returns current.

def get_transition_noun(noun, format_tuple, input_dict, take_first=False):
    logging_fn()
    local_items_list = registry.get_item_by_location(loc.current)
    #print(f"local items in get_transition_noun: {local_items_list}")
    if hasattr(noun, "is_loc_exterior"):
        #print(f"has noun.in_loc_ext: {noun.is_loc_exterior}")
        if hasattr(noun, "transition_objs"):
            if isinstance(noun.transition_objs, ItemInstance):
                #print(f"noun transition objs: {noun.transition_objs}")
                noun = noun.transition_objs
                return noun

            else:
                if len(noun.transition_objs) == 1:
                    #print("1 noun.transition_objs")
                    for neW_noun in noun.transition_objs:
                        #print(f"neW_noun: {neW_noun}")
                        return neW_noun
                else:
                    print(f"More than one transition object for {noun}. Can't deal with this yet. Exiting.")
                    exit()
    if not noun:
        #print(f"Not noun: input_dict: {input_dict}")
        if get_location(input_dict):
            location = get_location(input_dict)
            if not location:
                location = loc.current.place
            if hasattr(location, "entry_item"):
                loc_item = location.entry_item
                #print(f"HAs loc item: {loc_item}")
                if take_first:
                    return loc_item
                if isinstance(loc_item, str) and local_items_list:
                    for loc_item in local_items_list:
                        if loc_item.name == loc_item:
                            noun = loc_item
                            return noun


                elif isinstance(loc_item, ItemInstance) and local_items_list:
                    if loc_item in local_items_list:
                        noun = loc_item
                        return noun
                    else:
                        local_names = dict()
                        for item in local_items_list:
                            local_names[item.name] = item
                        if loc_item.name in local_names: ## Fix this later, this should not be necessary.
                            return local_names[loc_item.name]

        return None


    return noun

def move_a_to_b(a, b, action=None, direction=None, current_loc = None):
    logging_fn()

    location = None
    from itemRegistry import container_limit_sizes
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

def can_interact(noun_inst): # succeeds if accessible

    _, _, reason_val, meaning = registry.check_item_is_accessible(noun_inst)
    if reason_val in interactable_codes:
        return 1, reason_val, meaning
    else:
        return 0, reason_val, meaning

def check_lock_open_state(noun_inst):
    logging_fn()

    is_closed = is_locked = locked_have_key = False

    #if reason_val in (0, 3, 4, 5, 8): # all 'not closed/locked container options
    if hasattr(noun_inst, "is_open") and not noun_inst.is_open:
        is_closed = True
    if hasattr(noun_inst, "is_locked") and noun_inst.is_locked:
        is_locked = True
        if hasattr(noun_inst, "needs_key"):
            interactable, _, _ = can_interact(noun_inst.requires_key)
            if interactable:
                locked_have_key = True

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

def get_nouns(input_dict):

    noun = get_noun(input_dict)
    noun_2 = get_noun(input_dict, 2)
    return (noun, noun_2)


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


def get_meta(input_dict:dict) -> str:
    logging_fn()
    # x_noun: 1 == 1st noun, 2 == "2nd noun", etc. Otherwise will always return the first found.

    for data in input_dict.values():
        for kind, entry in data.items():
            if "meta" in kind:
                return entry["text"]

def verb_requires_noun(input_dict, verb_name, local=False):
    logging_fn()
    noun = get_noun(input_dict)
    if not noun:
        print(f"What do you want to {verb_name}?")
        return
    if local:
        if noun and noun.location == loc.current or noun.location == loc.inv_place:
            return noun
        print(f"There's no {assign_colour(noun)} around here to {verb_name}.")
        return
    return noun

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
            get_loc_descriptions(place=loc.current.place, cardinal=loc.current)
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
    elif meta_verb == "describe":
        look(("verb", "sem"), None)
        return
    elif meta_verb == "inventory":
        generate_clean_inventory(will_print=True, coloured=True)
        return
    elif meta_verb == "quit":
        exit("Okay, quitting the game. Goodbye!\n\n")
        return
    #elif meta_verb == "update_json": # testClass is gone, need to add this elsewhere.
    #    from testclass import add_confirms
    #    add_confirms()
    #    return
    else:
        from interactions.meta_commands import meta_control

        noun = get_noun(input_dict)
        location = get_location(input_dict)
        cardinal = get_cardinal(input_dict)

        meta_control(format_tuple, noun, location, cardinal)
        return

def move_through_trans_obj(noun, input_dict):
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
            print("You can't go enter something unless you're nearby to it.")
            return 1


def go(format_tuple, input_dict): ## move to a location/cardinal/inside
    logging_fn()

    if len(format_tuple) == 1:
        if not "cardinal" in format_tuple and not "location" in format_tuple:
            print("Where do you want to go?")
            return
    current_loc, current_card = get_current_loc()

    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    if len(format_tuple) == 2 and noun_entry:
        noun = noun_entry["instance"]
        if hasattr(noun, "enter_location"):
            return move_through_trans_obj(noun, input_dict)

    if (direction_entry and direction_entry["str_name"] in to_words and len(format_tuple) < 5) or (not direction_entry and len(format_tuple) < 4) or (direction_entry and not cardinal_entry and not location_entry):
        if location_entry and not cardinal_entry:
            #print(f"Location entry, not cardinal enter: {location_entry}")
            if location_entry["instance"] == loc.currentPlace:
                if input_dict[0].get("verb") and input_dict[0]["verb"]["str_name"] == "leave":
                    if hasattr(loc.current.place, "entry_item"):
                        if enter(format_tuple, input_dict, noun=loc.current.place.entry_item):
                            return

                    print("You can't leave without a new destination in mind. Where do you want to go?")
                    return

            if hasattr(location_entry["instance"], "entry_item"):
                print(f"hasattr location_entry[instance], entry_item: {location_entry["instance"].entry_item}")
                if not get_noun(input_dict):
                    #input_dict[len(format_tuple)] = {}
                    input_dict[len(format_tuple)]["noun"] = ({"instance": location_entry["instance"].entry_item, "str_name": location_entry["instance"].entry_item.name})

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
                print("Sorry, where do you want to go?")
                return
                print("If this does not have a location, it breaks. Why am I still using location_entry etc after determining they don't exist. Works if the direction is something internal, but not if I just type 'go to church', a location that doesn't exist.")
                #if len(format_tuple) == 3:
                print(f"FORMAT TUPLE: {format_tuple}")
                new_relocate(new_location=location_entry["instance"], new_cardinal = cardinal_entry["instance"])
                return

        elif location_entry and cardinal_entry:

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


def look(format_tuple=None, input_dict=None):
    logging_fn()

    if not format_tuple or (format_tuple == tuple(("verb", "sem")) and not input_dict):
        from misc_utilities import look_around
        look_around()
        return

    if get_meta(input_dict) == "inventory":
        meta(format_tuple, input_dict)
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
            #if hasattr(noun, "description_detailed"):
            #    read(format_tuple, input_dict)
            #else:
            item_interactions.look_at_item(noun, noun_entry)
        elif location_entry:
            from misc_utilities import look_around
            look_around()
            return

    elif len(format_tuple) == 3:

        if noun and format_tuple[1] == "direction":
            #if hasattr(noun, "description_detailed"):
            #    read(format_tuple, input_dict)
            #else:
            item_interactions.look_at_item(noun, noun_entry)
            return
        if format_tuple[2] == "cardinal" and format_tuple[1] == "direction":
            turn_cardinal(inst_from_idx(input_dict[2], "cardinal"), turning = False)
            return
        if format_tuple[1] == "sem" and semantic_entry["text"] == "for":
            find(format_tuple, input_dict)
            return

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

def find(format_tuple, input_dict):
    """
    look around the current location's cardinals to find the object of interest. Might cut this later.
    """
    noun = get_noun(input_dict)
    location = get_location(input_dict)
    if not noun:
        noun = get_transition_noun(None, format_tuple, input_dict, take_first=True)
        if not noun:
            print("I can only look for nouns at the moment.")
            return

    if not location:
        location = loc.current.place
    if not isinstance(location, placeInstance):
        if isinstance(location, cardinalInstance):
            location = location.place

    local_items = set()
    items_at = {}
    for card in location.cardinals:
        cardinal_inst = loc.by_cardinal_str(card, location)
        items = registry.get_item_by_location(cardinal_inst)
        if items:
            local_items = local_items | set(items)
            items_at[cardinal_inst] = set(items)

    if local_items:
        if noun in local_items:
            for card in items_at:
                if noun in items_at[card]:
                    #if len(items_at) == 1:
                    print(f"There's a {assign_colour(noun)} at {assign_colour(card.place_name, "loc")}, is that what you were looking for?")
                    return card
            print(f"Somehow {noun.name} wasn't found in the location dict, but is in local_items. Something broke.")
    print("end of def find(); something must have gone wrong.")


def read(format_tuple, input_dict):
    logging_fn()
    verb_inst = get_verb(input_dict)
    noun = get_noun(input_dict)
    if hasattr(noun, "location") and (noun.location == loc.inv_place or noun.location == loc.current):
        if hasattr(noun, "description_detailed"):
            if noun.description_detailed.get("is_tested"):
                from rolling import roll_risk
                outcome = roll_risk()
                print(f"Outcome: {outcome}")
                if outcome > 1:
                    test = noun.description_detailed.get("crit")
                    if not test:
                        test = noun.description_detailed.get(1)
                        #NOTE: have not accounted for various degrees of success here. Need to.
                    print(assign_colour(test, "b_yellow"))
                else:
                    test = noun.description_detailed.get("failure")
                    if not test:
                        test = noun.description_detailed.get(4)
                    print(assign_colour(test, "b_yellow"))
            else:
                to_print = noun.description_detailed.get("print_str")
                print(assign_colour(to_print, "b_yellow"))

            if hasattr(noun, "is_map"):
                from interactions.item_interactions import show_map
                show_map(noun)

            #if hasattr(noun_inst, "can_pick_up") and hasattr(noun_inst, "location") and noun_inst.location != None:
            #    take(format_tuple, input_dict)
            #else:
            if hasattr(noun, "event"):
                from eventRegistry import events
                events.is_event_trigger(noun, noun.location, "item_is_read") # just check, in case it's a street sign or something that you can't pick up but might still be a trigger. Unlikely but silly to exclude it arbitrarily.
            return

        else:
            look(format_tuple, input_dict)
            #print(f"It seems like you can't read the {assign_colour(noun_inst)}") # just look at it instead of saying this.
            return

    print(f"You can't see a {assign_colour(noun)} to read.")


def eat(format_tuple, input_dict):
    logging_fn()
    noun_inst = get_noun(input_dict)

    verb = input_dict[0]["verb"]["str_name"]
    if hasattr(noun_inst, "can_consume"):
        print(f"You decide to {verb} the {assign_colour(noun_inst)}.")
        print("something something consequences")
        game.inventory.remove(noun_inst)
        registry.delete_instance(noun_inst)
        return

    else:
        print("This doesn't seem like something you can eat...")


def clean(format_tuple, input_dict):
    logging_fn()
    print(f"format list: {format_tuple}, type: {type(format_tuple)}, length: {len(format_tuple)}")
    if len(format_tuple) == 2:
        if format_tuple == tuple(("verb", "location")):
        #if "verb" in format_tuple and "location" in format_tuple:
            print(f"You want to clean the {assign_colour(get_location(input_dict))}? Not implemented yet.")
            return
        elif "noun" in format_tuple:
            noun = get_noun(input_dict)
            if hasattr(noun, "is_dirty") and noun.is_dirty:
                print(f"You clean the {assign_colour(noun)}")
                return
            print(f"The {assign_colour(noun)} seems pretty clean already.")
            return


    noun = get_noun(input_dict)
    noun_2 = get_noun(input_dict, 2)
    dir_or_sem = get_dir_or_sem_if_singular(input_dict)
    if noun and dir_or_sem and dir_or_sem in ("with", "using"):
        if noun_2:
            print(f"You want to clean the {assign_colour(noun)} with the {assign_colour(noun_2)}? Not implemented yet.")
            return
        elif get_location(input_dict):
            print(f"You want to clean {assign_colour(get_location(input_dict))} with {assign_colour(noun)}? Odd choice, and not one that's implemented yet.")

    print(f"Cannot process {input_dict} in def clean() End of function, unresolved. (Function not yet written)")


def burn(format_tuple, input_dict):
    logging_fn()

    noun = get_noun(input_dict)
    noun2 = get_noun(input_dict, 2)

    from config import require_firesource

    can_burn = False
    firesource_found = False

    if "flammable" not in noun.item_type:
        print(f"The {assign_colour(noun)} can't burn, it seems.")
        return

    elif "flammable" in noun.item_type and (hasattr(noun, "is_burned") and noun.is_burned):
        print(f"The {assign_colour(noun)} is already burned.")
        return

    if require_firesource:
        if not noun2:
            local_items = registry.get_local_items(include_inv=True)
            if local_items:
                for item in local_items:
                    if "firesource" in item.item_type:
                        firesource_found = item
                        break
        if noun2:
            dir_or_sem = get_dir_or_sem_if_singular(input_dict)
            if dir_or_sem in ("with", "using"):
                if "firesource" in noun2.item_type:
                    firesource_found = noun2
                else:
                    print(f"You can't set a fire with {assign_colour(noun2)}.")
                    return

    if not require_firesource or (require_firesource and firesource_found):
        print(f"You set fire to the {assign_colour(noun)}, using the {assign_colour(firesource_found)}." if require_firesource else f"You set fire to the {assign_colour(noun)}.")
        set_noun_attr(("is_burned", True), noun=noun)
        return

    elif require_firesource:
        print(f"You don't have anything to burn the {assign_colour(noun)} with.")

def barricade(format_tuple, input_dict):

    noun, noun2 = get_nouns(input_dict)
    if not noun:
        print("Barricade what, exactly?")
        return
    if not noun2:
        print(f"What do you want to use to barricade the {assign_colour(noun)}?")
        return
    if "door_window" in noun.item_type:
        print(f"You want to barricade the window/door {assign_colour(noun)}. A valiant effort, I just haven't coded it yet.")


def break_item(format_tuple, input_dict):
    logging_fn()
    print_desc = False
    noun = verb_requires_noun(input_dict, "break", local=True)
    if not noun:
        return

    noun_2 = get_noun(input_dict, 2)

    if not noun_2:
        if noun.smash_defence > 4:
            print(f"What do you want to break the {assign_colour(noun)} with?")
            return
        #assume the ground is hard. ground isn't properly set up yet so we'll assume for now.
        print(f"You smash the {assign_colour(noun)} on the ground.\n") # NOTE: added_printline
        set_noun_attr(("is_broken", True), noun=noun)
        if hasattr(noun, "children") and noun.children:
            noun_children = set()
            for child in noun.children:
                noun_children.add(child)
    #NOTE: This move does not trigger the event trigger checks. If an item being removed from a container etc is a trigger, registry.move_item will not check it. So for now I do a manual line just to notify, but this is not a solution.
                if hasattr(child, "event") and child.event:
                    print(f"{child.name} is connected to an event: {child.event.name}")

            for child in noun_children:
                registry.move_item(inst=child, location=loc.current, old_container=noun, no_print=True)

            turn_cardinal(prospective_cardinal=loc.current, turning = False)
        return


    dir_or_sem = get_dir_or_sem_if_singular(input_dict)
    if dir_or_sem and dir_or_sem in ("with", "using", "on", "against"):
        for attack in ('smash', 'slice'):
            if getattr(noun_2, f"{attack}_attack") > getattr(noun, f"{attack}_defence"):
                print(f"You {attack} the {assign_colour(noun)} with the {assign_colour(noun_2)}, and it breaks.")
                set_noun_attr(("is_broken", True), noun=noun)
                return
            if getattr(noun, f"{attack}_attack") < getattr(noun_2, f"{attack}_defence"):
                print(f"You {attack} the {assign_colour(noun)} with the {assign_colour(noun_2)}, but {assign_colour(noun_2)} was weaker - {assign_colour(noun_2)} breaks.")
                set_noun_attr(("is_broken", True), noun=noun_2)
                return
            if getattr(noun, f"{attack}_attack") == getattr(noun_2, f"{attack}_defence"):
                print(f"You {attack} the {assign_colour(noun)} with the {assign_colour(noun_2)}, but the {assign_colour(noun)} and the {assign_colour(noun_2)} are evenly matched; nothing happens.")
                return

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
        return
    elif len(format_tuple) == 4:
        #print(f"Format is len 4: {format_tuple}")
        if format_tuple.count("noun") == 2:
            #print("format tuple has 2 nouns")
            accessible_1, _, _ = can_interact(noun)
            noun_2 = get_noun(input_dict, 2)
            accessible_2, _, _ = can_interact(noun_2)
            if accessible_1 and accessible_2:
                #rint(f"{noun_1} and {noun_2} are both accessible.")
                success = check_key_lock_pairing(noun, noun_2)
                if success:
                    #print(f"Key {noun_1} is accessible and will open lock {noun_2}")
                    key = noun
                    lock = noun_2

                else:
                    success = check_key_lock_pairing(noun_2, noun)
                    if success:
                        #print(f"Key {noun_2} is accessible and will open lock {noun_1}")
                        key = noun_2
                        lock = noun
                if key and lock:
                    if lock.is_locked and do_open:
                            print(f"You use the {assign_colour(key)} to unlock the {assign_colour(lock)}, and open it.")
                            set_noun_attr(("is_locked", False), ("is_open", True), noun=lock)
                            return
                    elif lock.is_locked and not do_open:
                        print(f"You use the {assign_colour(key)} to unlock the {assign_colour(lock)}")
                        set_noun_attr(("is_locked", False), noun=lock)
                        return

                    elif not lock.is_locked:
                        if verb.name == "lock":
                            print(f"You use the {assign_colour(key)} to lock the {assign_colour(lock)}.")
                            set_noun_attr(("is_open", False), ("is_locked", True), noun=lock)
                            return
                        else:
                            print(f"You can't unlock the {assign_colour(lock)}; it's already unlocked.")
                            return

                    elif do_open:
                        print(f"You open {lock} with {key}? This doesn't work yet.")

                else:
                    print(f"You can't open the {assign_colour(noun)} with {assign_colour(noun_2)}")
                    return

            else:
                print(f"{noun} and/or {noun_2} are not accessible: 1: {accessible_1}, 2: {accessible_2}")
        else:
            print(f"Not two nouns in {format_tuple}")

    else:
        print(f"Don't know what to do with {input_dict} in lock_unlock, not 2 or 4 len.")
        return


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
        return

    verb_inst = get_verb(input_dict)

    inst, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst)
    if reason_val not in interactable_codes:
        print(f"{noun_inst.name} isn't accessible, you can't interact with it.")
        print(f"[{meaning}]")
        return

    #print(f"open_close noun vars: {vars(noun_inst)}")

    if verb_inst.name == "open":
        if hasattr(noun_inst, "is_locked") and noun_inst.is_locked:
            print(f"You cannot open a locked {assign_colour(noun_inst.name)}.")
            return

    is_closed, is_locked, locked_and_have_key = check_lock_open_state(noun_inst)

    print(f"is_closed: {is_closed}, is_locked: {is_locked}, locked_and_have_key : {locked_and_have_key}")

    if verb_inst.name in ("close", "lock"):
        if verb_inst.name == "close":
            if not is_closed:
                print(f"You closed the {assign_colour(noun_inst)}")
                noun_inst.is_open = False
            else:
                print(f"The {assign_colour(noun_inst)} is already closed.")

        elif verb_inst.name == "lock":
            if not is_closed:
                print(f"You need to close the {noun_inst.name} first.")
            else:
                if not is_locked and not locked_and_have_key:

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

    if get_meta(input_dict) == "inventory":
        meta(format_tuple, input_dict)

    verb_inst = get_verb(input_dict)
    noun_inst = get_noun(input_dict)

    if len(format_tuple) > 3:
        if ('verb', 'noun', 'direction', 'location') == format_tuple:
            location = get_location(input_dict)
            if (location == loc.inv_place or loc.inv_place.place):
                print("The location is actually the inventory.")
                if noun_inst.location != loc.inv_place:
                    print(f"The {assign_colour(noun_inst)} isn't in your inventory...")
                    return
                print("The item is in your inventory, continue.")
            elif location != loc.current and location != loc.current.place:
                print(f"You aren't at {assign_colour(location, colour="loc")}, so how can you open {assign_colour(noun_inst)}?")
                return
        else:
            use_item_w_item(format_tuple, input_dict)
            return

    interactable, val, meaning = can_interact(noun_inst) # succeeds if accessible
    if not interactable:
        if val == 6:
            print(f"You can't open something you aren't nearby to...")
            return
        print(f"You can't do that right now.\n[{noun_inst} / {meaning}]")
        return

    from interactions.item_interactions import is_loc_ext

    outcome = is_loc_ext(noun_inst)
    if outcome:
        if get_noun(input_dict, 2):
            noun_inst_2 = get_noun(input_dict, 2) # pleased with this bit. Makes 'open work shed door' work cleanly without having to adjust the parser.
            test = is_loc_ext(noun_inst, return_trans_obj=True)
            if test == noun_inst_2:
                noun_inst = noun_inst_2
        else:
            print(outcome)
            return

    if not hasattr(noun_inst, "is_open"):
        print(f"You can't open the {assign_colour(noun_inst)}.")
        return

    if verb_inst.name == "open":
        if not hasattr(noun_inst, "can_be_opened") or (hasattr(noun_inst, "can_be_opened") and noun_inst.can_be_opened != True):
            print(f"You can't open the {assign_colour(noun_inst)}")
            return
            #print(f"meaning: {meaning}")
        if noun_inst.is_open == True:
            print(f"{assign_colour(noun_inst)} is already open.")
            return

        if hasattr(noun_inst, "is_locked") and noun_inst.is_locked == True:
            print(f"You can't open a locked {assign_colour(noun_inst)}.")
            #open_close(format_tuple, input_dict)
            return

        if val in can_open_codes:
            print(f"You open the {assign_colour(noun_inst)}.")
            set_noun_attr(("is_open", True), noun=noun_inst)
            return
       # _, confirmed_container, reason_val, meaning  = registry.check_item_is_accessible(noun_inst)

        if val in in_container_codes and hasattr(noun_inst, "contained_in"):#confirmed_container:
            print(f"You need to remove the {assign_colour(noun_inst)} from the {assign_colour(noun_inst.contained_in)} it's in, first.")
            return

        else:
            print(f"Cannot open {noun_inst.name} because {meaning}.")
            return
        #print(f"reason_val: {reason_val}, meaning: {meaning}")

    else:
        if noun_inst.is_open == False:
            # cancelling the next lines because if it's closed and I'm saying 'close', why are we going into locked processes?
            #if hasattr(noun_inst, "is_locked") and noun_inst.is_locked == True:
            #    open_close(format_tuple, input_dict)
            #    return
            print(f"The {assign_colour(noun_inst)} is already closed.")
            return

        print(f"You close the {assign_colour(noun_inst)}.")
        #print(f"noun_inst.is_open now: {noun_inst.is_open}")
        set_noun_attr(("is_open", False), noun=noun_inst)
        #print(f"noun_inst.is_open now: {noun_inst.is_open}")
        return

def combine(format_tuple, input_dict):
    logging_fn()
    #if verb_noun_sem_noun, verb_noun_dir_noun, combine a+b
    #if verb_noun == what do you want to combine it with.
    noun, noun2 = get_nouns(input_dict)
    if not noun2:
        print(f"What do you want to combine with the {assign_colour(noun)}")
        return

    if "container" in noun.item_type:
        #check relative sizes here; haven't implemente that anywhere yet.
        #assuming the sizes are suitable:
        put(format_tuple, input_dict) # might be a fair guess if b is a container?
        return

    print(f"You want to combine {assign_colour(noun)} and {assign_colour(noun2)}? Sounds good, but we don't do that yet...")

    #print(f"Cannot process {input_dict} in def combine() End of function, unresolved. (Function not yet written)")
    pass

def separate(format_tuple, input_dict):
    logging_fn()

    noun = verb_requires_noun(input_dict, "separate", local=True)
    if not noun:
        return
    noun2 = get_noun(input_dict, 2)

    if not noun2:
        print(f"What do you want to separate the {assign_colour(noun)} from?")
        return

        #if "container" in noun.item_type and hasattr(noun, "children") and noun.children:
        #    child_names = list((i.name for i in noun.children))
        #    child_names = ", ".join(child_names)
        #    print(f"{assign_colour(noun)} contains {child_names}.")
    #if verb_noun_sem_noun, verb_noun_dir_noun, combine a+b
    #if verb_noun == what do you want to combine it with.

    def is_one_a_child(parent, child):
        if hasattr(parent, "children") and parent.children != None:
            if child in parent.children:
                print(f"Removing child {child} from parent {parent}.")
                registry.move_from_container_to_inv(child, parent=parent) # untested
                return True

    if not is_one_a_child(noun, noun2):
        if not is_one_a_child(noun2, noun):
            print(f"Sorry, I can't figure out how to separate the {assign_colour(noun)} from the {assign_colour(noun2)}.")
            return

def combine_and_separate(format_tuple, input_dict):
    logging_fn()

    print(f"length of format list: {len(format_tuple)}")

    print(f"Cannot process {input_dict} in def separate_and_combine() End of function, unresolved. (Function not yet written)")

def move(format_tuple, input_dict):
    logging_fn()

    noun = get_noun(input_dict)
    if get_location(input_dict) and get_dir_or_sem_if_singular(input_dict): # so if it's 'move to graveyard', it just treats it as 'go to'.
        if noun:
            print(f"This probably isn't a simply 'move to graveyard', seeing as we have {noun} here. Not written yet, sorry.")
            return
        go(format_tuple, input_dict)
        return

    noun2 = get_noun(input_dict, 2)

    if noun and noun2:
        dir_or_sem = get_dir_or_sem_if_singular(input_dict)
        if dir_or_sem:
            print(f"Something about moving the {assign_colour(noun)} {dir_or_sem} the {assign_colour(noun2)}? Not written yet, sorry.")
            return
    elif noun:
        if "static" in noun.item_type:
            print(f"Try as you might, you can't move the {assign_colour(noun)}.")
            return
        print(f"Where do you want to move the {assign_colour(noun)}?")
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
    noun = get_noun(input_dict)
    #noun = verb_requires_noun(input_dict, "take", local=True)
    added_to_inv = False

    def can_take(noun_inst):
        logging_fn()
        added_to_inv = False

        inst, container, reason_val, meaning = registry.check_item_is_accessible(noun_inst)
        #print(f"CAN_TAKE: {noun_inst} / meaning: {meaning} / reason_val: {reason_val}")
        if reason_val not in (0, 3, 4, 5):
            print(f"Sorry, you can't take the {assign_colour(noun_inst)} right now.")
            return 1, added_to_inv
            #print(f"Reason code: {reason_val}")
        elif reason_val == 5:
            local_items = registry.get_item_by_location(loc.current)
            if local_items:
                local_item_names = dict()
                for loc_item in local_items:
                    if loc_item != noun_inst:
                        local_item_names[loc_item.name] = loc_item

                if noun_inst.name in local_item_names:
                    val, added_to_inv = can_take(local_item_names[noun_inst.name])
                    return val, added_to_inv # if another one is found locally, use that instead.
                    #print(f"{noun_inst} is already in your inventory, but {local_item_names[noun_inst.name]} is local.")
            else:
                items_by_name = registry.by_name.get(noun_inst.name)
                if items_by_name:
                    #print(f"Items matching {noun_inst.name}: \n{items_by_name}\nThis won't do anything yet, but later it should.")
                    if items_by_name:
                        for item in items_by_name:
                            if item != noun_inst and item.location == loc.current:
                                print(f"There's another {noun_inst.name} here, but it was not found in local_items. This means the item location wasn't assigned properly, something is broken.")

                    #for instance in items_by_name:
                        #print(f"Instance vars: {instance}\n{vars(instance)}")
                        #TODO: Do something else here. Currently this is failing due to other issues, but this still needs to be resolved; if I already have x in my inventory, check to see if x.2 is in the local area before giving up.
            print(f"{assign_colour(noun_inst)} is already in your inventory.")
            return 1, added_to_inv
        else:
            #can_pickup = verb_membrane.check_noun_actions(noun_inst, "take")
            #print("can_take, 'else' before pick_up check.")
            #print(f'if hasattr(noun_inst), "can_pick_up": {hasattr(noun_inst, "can_pick_up")}')
            if hasattr(noun_inst, "can_pick_up") and noun_inst.can_pick_up:
                #print(f"{noun_inst} can be picked up.")
                if reason_val in (3, 4):
                    outcome = registry.move_from_container_to_inv(noun_inst, parent=container)
                    #if outcome != noun_inst:
                        #print(f"Outcome: {outcome}, noun_inst: {noun_inst}")
                        #if outcome in loc.inv_place.items:
                            #print("Outcome is in inventory (line 1466).")
                            #return 0, outcome
                        #if noun_inst in loc.inv_place.items:
                            #print("noun_inst is in inventory. line 1469")
                    added_to_inv = outcome
                    #print("added to inv, returning.")
                    return 0, added_to_inv
                elif reason_val == 0:
                    outcome = registry.move_item(noun_inst, location = loc.inv_place)
                    #outcome = registry.move_item(inst, location = loc.inv_place)
                    #outcome = registry.pick_up(noun_inst, location = loc.inv_place) ## the can_take function shouldn't be doing this part.
                    #print("Did pick_up")
                    if outcome in loc.inv_place.items:
                        #print("Outcome is in inventory. (line 1480)")
                        return 0, outcome
                    if noun_inst in loc.inv_place.items: # Once confirmed, remove the
                        #print("noun_inst is in inventory. line 1483")
                        added_to_inv = noun_inst
                        return 0, added_to_inv
                print(f"{noun_inst} failed to be processed, not reasonval 3, 4, 5. reason_val: {reason_val}/{meaning}")
            else:
                print(f"You can't pick up the {assign_colour(noun_inst)}.")
                return 1, added_to_inv

    dir_or_sem = get_dir_or_sem_if_singular(input_dict)
    location = get_location(input_dict)
    if format_tuple in (("verb", "noun"), ("verb", "direction", "noun")):

        noun_loc = noun.location
        cannot_take, added_to_inv = can_take(noun)
        #print(f"after can_take: cannot_take: {cannot_take} // added_to_inv: {added_to_inv}")


        if cannot_take and hasattr(noun, "can_consume"):
            print(f"\nDid you mean to consume the {assign_colour(noun)}? ")
            return

    elif dir_or_sem in ("in", "at") and location:
        if location == loc.current or location == loc.current.place:
            cannot_take, added_to_inv = can_take(noun)



    elif format_tuple == (("verb", "noun", "direction", "noun")): ## will later include scenery. Don't know how that's going to work yet.
        verb_str = input_dict[0]["verb"]["str_name"]
        if verb_str in ("take", "remove", "separate", "get"):
            noun_loc = noun.location
            dir_inst = get_dir_or_sem_if_singular(input_dict)
            if dir_inst not in ("and", "from"):
                print(f"dir_inst is {dir_inst}; was expecting 'from' or 'and'. May need to adjust take function.")

            container_inst = get_noun(input_dict, 2)
            if "battery" in noun.item_type and hasattr(container_inst, "takes_batteries") and container_inst.takes_batteries and container_inst.has_batteries:
                print(f"You can take the batteries from the {assign_colour(container_inst)}. (Though it's not actually scripted yet.)")

            inst, container, reason_val, reason = registry.check_item_is_accessible(noun)
            print(f"REASON: {reason_val} / {reason}")
            if reason_val not in (0, 3, 4):
                #print(f"Cannot take {noun_inst.name}.")
                #print(f"Reason code: {reason_val}")
                print(f"Sorry, you can't take the {assign_colour(noun)} right now.")
                if reason_val == 2:
                    print(f"{assign_colour(noun)} is already in your inventory.")
            else:
                if container == container_inst and reason_val in (3, 4):
                    output_noun = registry.move_from_container_to_inv(noun, parent=container)
                    #print(f"Output noun: {output_noun}")
                    if output_noun in loc.inv_place.items:
                        added_to_inv = output_noun
                        #output_noun = noun
                    #if noun in game.inventory:
                    #    added_to_inv = True
                    else:
                        print("Tried to add {assign_colour(noun_inst)} to inventory, but something must have gone wrong.")
                        traceback_fn()
                else:
                    print(f"The {assign_colour(noun)} doesn't seem to be in {container_inst.name}.")

    else:
        print(f"Cannot process {input_dict} in def take() End of function, unresolved.")
        return

    if added_to_inv:
        #print(f"ADDED TO INV: {added_to_inv}")
        if isinstance(added_to_inv, ItemInstance): # added_to_inv smuggles out the single/local instance I actually want to pick up. So here we just swap them if needed. added_to_inv, if successful, is either the existing noun, or the corrected output.
            if added_to_inv != noun:
                noun = added_to_inv
        #print(f"{assign_colour(noun_inst)} is now in your inventory.") # original
        #print(f"ITEM: {noun}")
        if not events.is_event_trigger(noun, noun_loc, reason = "item_in_inv"):
            print(f"The {assign_colour(noun)} {is_plural_noun(noun)} now in your inventory.")
        return

def put(format_tuple, input_dict, location=None):
    logging_fn()
    action_word = "You put"

    noun = verb_requires_noun(input_dict, "place", local=True)
    noun2 = get_noun(input_dict, 2)
    sem_or_dir = get_dir_or_sem_if_singular(input_dict)

    if noun2:

        if hasattr(noun2, "contained_in") and noun == noun2.contained_in:
                print(f"Cannot put {assign_colour(noun)} in {assign_colour(noun2)}, as {assign_colour(noun2)} is already inside {assign_colour(noun)}. You'll need to remove it first.")
                return

        if noun == noun2:
            print(f"You cannot put the {assign_colour(noun)} in itself.")
            return
        if sem_or_dir in ("in", "to", "into", "inside") and len(format_tuple) == 4:
            if hasattr(noun, "contained_in") and noun2 == noun.contained_in:
                print(f"{noun2.name} is already in {noun}")
                return
            registry.move_item(inst=get_noun(input_dict), new_container=(get_noun(input_dict, 2)))
            if noun in game.inventory:
                game.inventory.remove(get_noun(input_dict))
                if noun in game.inventory:
                    exit(f"{assign_colour(get_noun(input_dict))} still in inventory, something went wrong.")
            else:
                from misc_utilities import smart_capitalise
                text = smart_capitalise(f"{action_word} {assign_colour(get_noun(input_dict))} {sem_or_dir} {assign_colour(get_noun(input_dict, 2))}")
                print(text)
            return

    else:
        if sem_or_dir:
            if not noun2:
                move_a_to_b(a=a, b=location, action=action_word, current_loc=location)
                return

        if sem_or_dir in down_words:
            move_a_to_b(a=noun, b=location, action=action_word, current_loc=location)
            return

        if len(format_tuple) == 5:
            a, sem_or_dir, b, sem_or_dir_2, c = five_parts_a_x_b_in_c(input_dict)
            if c == location:
                move_a_to_b(a=a, b=b, action=action_word, direction=sem_or_dir, current_loc=location)
                return

    print(f"You can't put {assign_colour(noun)} on {assign_colour(noun2)}; I just haven't programmed it yet.")

def throw(format_tuple, input_dict):
    logging_fn()

    noun = verb_requires_noun(input_dict, "throw", local=True)

    if not noun:
        print("What do you want to throw?")
        return
    if len(format_tuple) == 2:
        print(f"Where do you want to throw the {assign_colour(noun)}?")
        return
    dir_or_sem = get_dir_or_sem_if_singular(input_dict)
    noun2 = get_noun(input_dict, 2)

    if noun and noun2 and noun == noun2:
        verb = get_verb(input_dict)
        print(f"You can't {verb.name} the {assign_colour(noun)} {dir_or_sem} itself.")
        return
    if dir_or_sem and dir_or_sem in down_words:
        move_a_to_b(noun, loc.current, "You drop the", "to leave it at the")

    if dir_or_sem in to_words and noun2:
        print(f"You throw the {assign_colour(noun)} at the {assign_colour(noun2)}")
        if hasattr(noun2, "smash_defence") and hasattr(noun, "smash_attack"):
            if noun2.smash_defence < noun.smash_attack:
                print(f"The {assign_colour(noun2)} breaks as the {assign_colour(noun)} hits it.") # TODO: custom breaking messages for obviously breakable things with [[]] or smth for the breaker obj name.
                set_noun_attr(("is_broken", True), noun=noun2)
                return
            elif noun2.smash_defence >= noun.smash_attack:
                print(f"The {assign_colour(noun)} hits the {assign_colour(noun2)}, but doesn't seem to damage it.")
                return




    # verb_noun == where do you want to throw it (unless context),
    # verb_noun_dir == throw ball up (check if 'dir' makes sense)
    # verb_noun_dir_noun  == throw ball at tree

    print(f"Cannot process {input_dict} in def throw() End of function, unresolved. (Function not yet written)")


def push(format_tuple, input_dict):
    logging_fn()
    noun = get_noun(input_dict)
    if "door_window" in noun.item_type:
        if hasattr(noun, "can_be_opened"):
            print("NOTE: This doesn't check if the noun is accessible. I guess we're doing that using local_items in the parser now?")
            if noun.is_open:
                print(f"You push against the {assign_colour(noun)}, but it doesn't move much further.")
                return
            else:
                if noun.is_locked:
                    print(f"You push against the {noun}, but it doesn't budge.")
                    return
                else:
                    print(f"You push against the {noun}, and it opens just enough for you to see inside.")
                    if noun.location == loc.current:
                        if noun.exit_to_location == loc.current.place:
                            enter(format_tuple, input_dict)
                            return
                    else:
                        print("No description here. Should be one eventually.")
                        return

    noun2 = get_noun(input_dict, 2)
    if noun2:
        dir_or_sem = get_dir_or_sem_if_singular(input_dict)
        if dir_or_sem in to_words:
            print(f"Things don't have weight yet, I don't know if you can push the {assign_colour(noun)} {dir_or_sem} the {assign_colour(noun2)}.")
            return
    print(f"Things don't have weight yet, I don't know if you can push the {assign_colour(noun)}.")
    return

    # verb_noun == to move things out the way in general
    # verb_noun_dir == #push box left
    # verb_noun_dir_noun == push box away from cabinet

def drop(format_tuple, input_dict):
    logging_fn()

    action_word = "you dropped the"
    #print("This is the drop function.")

    _, location = get_current_loc() # don't know if separating the tuple is making life harder for myself here...
    noun = get_noun(input_dict)
    #noun = verb_requires_noun(input_dict, "drop", local=True)
    if not noun:
        print("What do you want to drop?")
        return

    if noun not in loc.inv_place.items:
        inv_items = loc.inv_place.items
        #print(f"inv items: {inv_items}")
        if inv_items:
            for item in inv_items:
                if hasattr(item, "is_hidden") and item.is_hidden:
                    continue
                if item.name == noun.name:
                    noun=item
                    break

    if len(input_dict) == 3:
        direction = get_dir_or_sem_if_singular(input_dict)
        if noun and direction and (direction == "here" or direction in down_words):
            input_dict.pop(2, None)

    #print(f"FORMAT: {format_tuple}\n INPUT DICT: \n{input_dict}\n")
    if len(input_dict) == 2:
        #print(f"location: {location}")
        _, container, reason_val, meaning = registry.check_item_is_accessible(noun)
        #print(f"reason val: {reason_val}, meaning: {meaning}, for item: {noun}")
        if reason_val == 5:
            dropped = registry.drop(noun)

        elif reason_val == 3:
            print(f"You can't drop the {assign_colour(noun)}; you'd need to get it out of the {assign_colour(container)} first.")
            return

        else:
            print(f"You can't drop the {assign_colour(noun)}; you aren't holding it.")
            return

    elif len(input_dict) == 4:
        dir_or_sem = get_dir_or_sem_if_singular(input_dict)
        #item_to_place, direction, container_or_location = three_parts_a_x_b(input_dict)
        #print(f"item_to_place: {item_to_place}, direction: {direction}, dir type: {type(direction)}")
        if dir_or_sem in ["in", "into", "on", "onto", "at"]:
            if get_location(input_dict):
                if get_location(input_dict) != loc.current:
                    print(f"You can't drop the {assign_colour(noun)} at {assign_colour(get_location(input_dict))} because you aren't there.")
                    return

            _, container, reason_val, meaning = registry.check_item_is_accessible(noun)
            #print(f"meaning: {meaning}")
            if reason_val in (0, 3, 4, 5):
                noun2 = get_noun(input_dict, 2)
                if noun2 and "container" in noun2.item_type:
                    registry.move_item(noun, new_container=noun2)
                    #move_a_to_b(a=item_to_place, b=container_or_location, action=action_word, direction=direction)

            else:
                print(f"Couldn't move {noun.name} because {meaning}")
        else:
            print(f"Cannot process {input_dict} in def drop(); 4 long but direction str is not suitable.")
            return

    if noun not in loc.inv_place.items:
        triggered = None
        if hasattr(noun, "event") and noun.event:
            from eventRegistry import events
            triggered = events.is_event_trigger(noun, noun.location, reason = "item_not_in_inv")
            #print(f"Triggered: {triggered}")
        if not triggered:
            print(f"Dropped the {assign_colour(noun)} onto the ground here at the {assign_colour(loc.current, card_type='ern_name')}")
        return

    print(f"Cannot process {input_dict} in def drop() End of function, unresolved.")


def set_action(format_tuple, input_dict):
    logging_fn()
    verb = get_verb(input_dict)
    if verb.name == "set":
        noun = verb_requires_noun(input_dict, "set", local=True)
        if noun:
            if len(format_tuple) == 2:
                if "watch" == noun.name or "watch" in noun.name:
                    from set_up_game import game
                    game.time
                    print(f"You set an arbitrary time on the watch.  Seeing as it's {game.time}, you set it to around <some relevant time>. Make this better later. Currently it cound't cope with 'set watch to 2am', though I've no clue why anyone would try.")
        print("This should always be a 'place thing somewhere' type command. If not, fix me.")

    # verb_noun_dir == set item down == drop
    # verb_noun_dir_noun == set item on fire if noun2 == 'fire' == burn
    # verb_dir_noun_sem_noun set on fire with item
    print(f"Cannot process {input_dict} in def set() End of function, unresolved. (Function not yet written)")


def use_item_w_item(format_tuple, input_dict):
    logging_fn()
    #print(f"Format list: {format_tuple}")
    #print(f"Length format list: {len(format_tuple)}")
    ## use x on y
    _, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)
    dir_or_sem = get_dir_or_sem_if_singular(input_dict)

    verb = get_verb(input_dict)
    actor_noun = verb_requires_noun(input_dict, verb.name, local=True)
    target_noun = get_noun(input_dict, 2)
    if not target_noun:
        print(f"No second noun: {format_tuple} should not be in use_item_w_item function. Check routing.")
        return
    requires_key = None
    if format_tuple == (('verb', 'noun', 'direction', 'noun')) or format_tuple == (('verb', 'noun', 'sem', 'noun')):
        if verb.name in ("use", "unlock", "lock", "open") and dir_or_sem and dir_or_sem in  ("on", "using", "with"):
            #print(f"use_item_w_item: verb name: `{verb.name}`, dir_or_sem is `{dir_or_sem}`, actor_noun: {actor_noun}, target_noun: {target_noun}")
            for noun in (actor_noun, target_noun):
                if hasattr(noun, "is_key") or hasattr(noun, "requires_key"):
                    lock_unlock(format_tuple, input_dict)
                    return
            if verb.name in ("lock", "unlock"):
                print(f"Cannot {verb.name}.")
                return

            print(f"You want to {verb.name} the {actor_noun} {dir_or_sem} a {target_noun}; I'm not sure what that means; {assign_colour(actor_noun)} doesn't need a key...")
            return


        print(f"Not sure how to deal with {format_tuple}")

    print(f"Failed use_item_w_item: FORMAT TUPLE: {format_tuple}")
    print(f"Cannot process {input_dict} in def use_item_w_item() End of function, unresolved. (Function partially written but doesn't do anything.)")

def use_item(format_tuple, input_dict):
    logging_fn()

    if len(format_tuple) == 4:
        use_item_w_item(format_tuple, input_dict)
        return

    noun = verb_requires_noun(input_dict, "use", local=True)
    if "map" in noun.name:
        from interactions.item_interactions import show_map
        show_map(noun)
        return

    print(f"Cannot process {input_dict} in def use_item() End of function, unresolved. (Function not yet written)")

def wait(format_tuple, input_dict):
    print("Future wait function, for spending time-portions doing a simple activity or nothing. Might be used at some point...?")


def enter(format_tuple, input_dict, noun=None):
    logging_fn()
    ### NEED TO FORMALISE DOORS/TRANSITION OBJECTS.
    # just realised you can add str to exit like you can with print/input: exit(code="Exiting because reason given above.")
    if not noun:
        if format_tuple == ("verb", "noun", "noun"):
            noun = get_noun(input_dict, 2)
        else:
            noun = get_noun(input_dict)
    #print(f"NOUN: {noun}")
    #if hasattr(noun, "is_loc_exterior"):
    #    print(f"{noun} is a location exterior object, this will work later.")
    if not noun or hasattr(noun, "is_loc_exterior") or hasattr(noun, "is_transition_obj"):
        noun = get_transition_noun(noun, format_tuple, input_dict)

    if not noun:
        noun = get_noun(input_dict, get_str=True)
        if noun:
            print(f"You can't enter a {assign_colour(noun)} here.")
            return
        print("There's nothing to enter here.")
        return
    #print(f"NOUN after get_transition_noun: {noun}")
    if hasattr(noun, "enter_location"):
        return move_through_trans_obj(noun, input_dict)

    else:
        target_loc = find(format_tuple, input_dict)
        if target_loc:
            if target_loc == loc.current:
                look(format_tuple, input_dict)
                return
            else:
                print("You'll have to go there first.")
                return
        print(f"This {noun} doesn't lead anywhere")



def router(viable_format, inst_dict, input_str=None):
    logging_fn()

    verb_inst = None
    quick_list = []
    input_strings = []
    for v in inst_dict.values():
        for data in v.values():
            quick_list.append(data["str_name"])
            input_strings.append(data["text"])
    MOVE_UP = "\033[A"

    from config import print_input_str

    if print_input_str:
        if input_str:
            print(f'{MOVE_UP}\033[1;32m[[  {input_str}  ]]\033[0m\n')
            #print(f'{MOVE_UP}{MOVE_UP}\n\033[1;32m[[  {input_str}  ]]\033[0m\n')
        else:
            print(f'{MOVE_UP}{MOVE_UP}\n\033[1;32m[[  {" ".join(input_strings)}  ]]\033[0m\n')

    else: #print processed str
        print(f'{MOVE_UP}{MOVE_UP}\n\033[1;32m[[  {" ".join(quick_list)}  ]]\033[0m\n')

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
        "find": find,

        "read": read,
        "eat": eat,
        "clean": clean,
        "burn": burn,
        "break": break_item,

        "lock": lock_unlock,
        "unlock": lock_unlock,
        "open": simple_open_close,#open_close,#open_item,
        "close": simple_open_close,#open_close,#close,

        "barricade": barricade,

        "enter": enter,

        "combine": combine,
        "separate": separate,

        "use": use_item,
        "move": move,
        "turn": turn,
        "take": take,
        "put": put,
        "throw": throw,
        "push": push,
        "drop": drop,
        "set": set_action,

        "time": wait
    }

    can_be_not_local = ["find", "go", "move", "enter"]

    try:
        if isinstance(verb_inst, str):
            func = function_dict["meta"]
        elif len(viable_format) in (1, 2) and list(inst_dict[0].keys())[0] in ("location", "direction", "cardinal"):
            func = function_dict["go"]
        else:
            func = function_dict[verb_inst.name]

        if func != function_dict["go"] and get_location(inst_dict):
            mentioned_loc = get_location(inst_dict)
            if mentioned_loc != loc.current and mentioned_loc != loc.current.place and mentioned_loc != loc.inv_place.place:
                if func.__name__ not in can_be_not_local:
                    print(f"You want to {verb_inst.name} at {assign_colour(mentioned_loc)} but you aren't there...")
                    return

        response = func(format_tuple = viable_format, input_dict = inst_dict)
        return response
    except Exception as e:
        print(f"Failed to find the correct function to use for {verb_inst}: {e}")
