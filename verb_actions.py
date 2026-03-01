""" Receives format and input_dict from verb.membrane and forwards the data to a verb function, eg `def g`et, `def drop`, `def eat`."""

from logger import logging_fn, traceback_fn
from env_data import cardinalInstance, placeInstance, locRegistry as loc
from interactions import item_interactions
from interactions.player_movement import relocate
from itemRegistry import itemInstance, registry
from misc_utilities import assign_colour, col_list, generate_clean_inventory, has_and_true, is_plural_noun, smart_capitalise, print_failure_message
from printing import print_yellow
from verb_definitions import directions, semantics

can_open_codes = [0,5,8]
can_pickup_codes = [0,3,4]
in_container_codes = [3,4]
can_lookat_codes = [0,3,4,5,8]
interactable_codes = [0,3,4,5,8]

movable_objects = ["put", "take", "combine", "separate", "throw", "push", "drop", "set", "move"]

in_words = ["in", "inside", "into"]
to_words = ["into", "to", "towards", "at", "for"] ## these two (< + ^) are v similar but have some exclusive uses, so keeping them separately makes sense here. # 'for' in the sense of 'leave for the graveyard'.
down_words = ["down", "on"]

update_description_attrs = [
    "is_open", "is_broken", "is_dirty", "is_burned", "is_spoiled", "is_charged"
]

invert_cardinals = {
    "south": "north",
    "north":"south",
    "east": "west",
    "west": "east"
    }

#### Fundamental Operations ####

def get_current_loc():
    """Returns `location` and `cardinal` instances as a tuple."""
    logging_fn()
    location = loc.current.place
    cardinal = loc.current
    return location, cardinal

def format_list_neatly(list_to_neaten):
    """Really is just a portion of `def compile_long_desc(long_desc)`.\n Formats the incoming list into '`a, b and c`' style formatting."""
    if len(list_to_neaten) == 1:
        formatted_list = assign_colour(list_to_neaten[0], caps=True)
    elif len(list_to_neaten) == 2:
        formatted_list = (f"{assign_colour(list_to_neaten[0], caps=True)} and {assign_colour(list_to_neaten[1])}")
    else:
        formatted_list = (f"{assign_colour(list_to_neaten[0], caps=True)}{', '.assign_colour(list_to_neaten[1:-1])}, and {assign_colour(list_to_neaten[-1])}")

    return formatted_list


def print_moved_children(moved_children, noun, reason):
    """Formats the list of `moved_children`, replaces `[[ ]]` and `< >` text substrings with the appropriate variables."""
    from eventRegistry import acts
    if isinstance(moved_children, set):
        moved_children = list(moved_children)
    reason_str = acts.get(reason)
    if moved_children:
        reason_str = list(reason_str["moved_children"])[0]
    children_str = format_list_neatly(moved_children)
    if len(moved_children) == 1 and not is_plural_noun(moved_children[0], bool_test=True):
        action = "falls"
    else:
        action = "fall"

    reason_str = reason_str.replace("[[children]]", children_str)
    reason_str = reason_str.replace("<fall>", action)
    reason_str = reason_str.replace("[[noun]]", assign_colour(noun))
    print(reason_str)

def set_noun_attr(*values, noun:itemInstance):
    """Sets the attr/val for each set in `values` to `noun`, while also checking `noun` and `values` in `is_event_trigger`."""
    logging_fn()
    """
    'noun' must be provided at `noun=  `, as it needs to be differentiated from *values
    """
    from eventRegistry import trigger_acts, events
    if hasattr(noun, "event") and getattr(noun, "event") and hasattr(noun, "is_event_key") and noun.is_event_key:
        print()
        outcome, moved_children = events.is_event_trigger(noun, values)
        if moved_children:
            print_moved_children(moved_children, noun, values)
        if not outcome:
            print(MOVE_UP) # To add the extra line. Needed for unlocking key items, to avoid always adding another newline after unlocking.

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
                    outcome, moved_children = events.is_event_trigger(noun, reason = item_val)#values)
                    if moved_children:
                        print_moved_children(moved_children, noun, item)

            setattr(noun, item, val)

            if item in update_description_attrs:
                from itemRegistry import registry
                if hasattr(noun, "descriptions") and noun.descriptions:
                    registry.init_descriptions(noun)


def is_loc_current_loc(location=None, cardinal=None):
    """Checks if the incoming `location` and/or `cardinal` match the current location/cardinal."""
    logging_fn()

    current_location, current_cardinal = get_current_loc()
    if location and location == current_location:
        return 1, current_location, current_cardinal
    if not location and cardinal: ## so it can check if the facing direction is current without needing location.
        if cardinal == current_cardinal:
            return 1, current_location, current_cardinal
    return 0, current_location, current_cardinal # 0 if not matching. Always returns current.

def get_transition_noun(noun, format_tuple, input_dict, take_first=False, return_if_exterior = False):
    """Finds transition objects from `loc_exterion` nouns, returning the first transition object found."""
    logging_fn()
    local_items_list = registry.get_item_by_location(loc.current)
    print(f"local items list: {local_items_list}")
    if isinstance(noun, list) and len(noun) == 1:
        noun = noun[0]

    if hasattr(noun, "is_loc_exterior"):
        if not hasattr(noun, "transition_objs") or (hasattr(noun, "transition_objs") and not noun.transition_objs):
            if loc.by_name.get(noun.name):
                location = loc.by_name[noun.name]
                if hasattr(location, "loc_exterior_items") and location.loc_exterior_items:
                    print(f"Location {location.name} has exterior items: {location.loc_exterior_items}") ### I don't know it this ever applies...
                    if return_if_exterior:
                        return True
                if hasattr(location, "transition_objs") and location.transition_objs:
                    print(f"Location {location.name} has transition items: {location.transition_objs}")


        print(f"noun is loc exterior: {vars(noun)}")
        if hasattr(noun, "transition_objs") and noun.transition_objs:
            print("noun has transition objects")
            if isinstance(noun.transition_objs, itemInstance):
                noun = noun.transition_objs
                return noun

            else:
                if len(noun.transition_objs) == 1:
                    #print("1 noun.transition_objs")
                    for neW_noun in noun.transition_objs:
                        print(f"neW_noun: {neW_noun}")
                        #return neW_noun
                else:
                    print(f"More than one transition object for {noun}. Can't deal with this yet. Exiting.")
                    exit()
        else:
            print(f"noun does not have transition nouns.")
            return None
    else:
        if noun:
            print(f"Noun {noun} is not a loc exterior.")
    if not noun:
        #print(f"Not noun: input_dict: {input_dict}")
        if get_location(input_dict):
            location = get_location(input_dict)
            if not location:
                location = loc.current.place
            if hasattr(location, "entry_item"):
                test_item = location.entry_item
                print(f"HAs loc item: {loc_item}")
                if take_first:
                    return test_item
                if isinstance(test_item, str) and local_items_list:
                    for loc_item in local_items_list:
                        if loc_item.name == test_item:
                            noun = loc_item
                            return noun


                elif isinstance(loc_item, itemInstance) and local_items_list:
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

def get_correct_nouns(input_dict, verb=None, access_str=None, access_str2=None):
    """
    Just a function to compile the getting of noun data so each one doesn't have to do it individually.
    Takes input_dict and optionally, verb, and returns noun, noun_str, noun2, noun2_str.
    Uses default settings for the verb, so not all suitable for all usecases, but the vast majority.
    """
    # Have added but not tested `access_str=None, access_str2=None`, to be able to specify access strings from the outside. This would expand it to basically all usecases.
    noun, noun_str, noun2, noun2_str = get_nouns(input_dict)

    from verbRegistry import VerbInstance
    if verb:
        if isinstance(verb, VerbInstance):
            verb = verb.name
    else:
        verb = get_verb(input_dict).name

    if noun:
        outcome = item_interactions.find_local_item_by_name(noun, verb=verb, access_str=access_str)
    if isinstance(outcome, itemInstance):
        noun = outcome
    else:
        if outcome == None:
            logging_fn(f"Going to print error from def {verb} `{input_dict}`")
            print_failure_message(noun=noun_str, verb=verb)
            return

    if noun2:
        outcome = item_interactions.find_local_item_by_name(noun2, verb=verb, access_str=access_str2)
    if isinstance(outcome, itemInstance):
        noun2 = outcome
    else:
        if outcome == None:
            logging_fn(f"Going to print error from def {verb} `{input_dict}`")
            print_failure_message(noun=noun_str, verb=verb)
            return

    return noun, noun_str, noun2, noun2_str


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

    if isinstance(a, itemInstance):
        if not b:
            b = loc.current
        if not isinstance(b, itemInstance):
            if isinstance(b, cardinalInstance):
                if b == loc.current:
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
                if isinstance(a, itemInstance):
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
            current_loc = loc.current.place
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
            current_loc = loc.current.place

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
    """Runs `noun_inst` through `registry.check_item_is_accessible`, returning a boolean for `interactable/not interactable`, and the `reason_val` and `meaning`."""
    _, reason_val, meaning = registry.run_check(noun_inst)

    if reason_val in interactable_codes:
        return 1, reason_val, meaning
    else:
        return 0, reason_val, meaning

def check_lock_open_state(noun_inst):
    """Checks if `noun_inst` is open if it can be, is locked if it can be, and locked and needs a key, checks if that key is available. Returns `is_closed`, `is_locked` and `locked_have_key`."""
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
    """Gets the dictionary entry from `input_dict` for `verb_entry`, `noun_entry`, `direction_entry`, `cardinal_entry`, `location_entry`, `semantic_entry`, and returns them in that order."""
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
def get_cardinal(input_dict:dict) -> itemInstance:
    logging_fn()
    for i, _ in enumerate(input_dict):
        if input_dict[i].get("cardinal"):
            return list(input_dict[i].values())[0]["instance"]

def get_verb(input_dict:dict, get_str=False) -> itemInstance:
    logging_fn()
    if input_dict[0].get("verb"):
        if get_str:
            return list(input_dict[0].values())[0]["text"]
        return list(input_dict[0].values())[0]["instance"] # works as long as verb is always first

def get_noun(input_dict:dict, x_noun:int=None, get_str=False) -> itemInstance:
    """ `x_noun: 1` == 1st noun, `2` == "2nd noun", etc. Otherwise will always return the first found. \n\nReturns the `itemInstance` unless `get_str==True`"""
    logging_fn()

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
    """Return up to two nouns `entry['instance']` + `entry['text']` from input_dict.

    Returns `noun, noun_str, noun2, noun2_str`, with any not found being `None`."""

    noun_counter = 0
    noun = noun_str = noun2 = noun2_str = None

    for data in input_dict.values():
        for kind, entry in data.items():
            if "noun" in kind:
                noun_counter += 1
                if noun_counter == 2:
                    noun2 = entry["instance"]
                    noun2_str = entry["text"]
                else:
                    noun_str = entry["text"]
                    noun = entry["instance"]

    return noun, noun_str, noun2, noun2_str

def get_location(input_dict:dict, get_str=False) -> placeInstance:
    """Returns the first found location entry from `input_dict`. Will return `placeInstance` unless `get_str==True`, in which case it returns `text`."""
    logging_fn()

    for data in input_dict.values():
        for kind, entry in data.items():
            if "location" in kind:
                if get_str:
                    return entry["text"]
                else:
                    return entry["instance"]

def get_number(input_dict:dict, x_val=None) -> str:
    """Returns `str_name` for the first `direction` or `sem` entry in `input_dict`."""
    logging_fn()
    num_counter = 0
    for data in input_dict.values():
        for kind, entry in data.items():
            if "number" in kind:
                if not x_val:
                    return entry["text"]

                num_counter += 1
                if num_counter == x_val:
                    return entry["text"]

def get_dir_or_sem(input_dict:dict, x_val=None) -> str:
    """Returns `str_name` for the first `direction` or `sem` entry in `input_dict`."""
    logging_fn()
    sem_counter = 0
    for data in input_dict.values():
        for kind, entry in data.items():
            if "direction" in kind or "sem" in kind:
                if not x_val:
                    return entry["text"] # was str_name; shoul be text, no? For dirs/sems, should always be the same. Need to check.

                sem_counter += 1
                if sem_counter == x_val:
                    return entry["text"]

def get_meta(input_dict:dict) -> str:
    """Returns `text` for the first `meta` entry in `input_dict`."""
    logging_fn()

    for data in input_dict.values():
        for kind, entry in data.items():
            if "meta" in kind:
                return entry["text"]

def verb_requires_noun(input_dict, verb_name, x_noun=None, local=False):
    logging_fn()
    if x_noun:
        if not isinstance(x_noun, int):
            x_noun = int(x_noun)
        noun = get_noun(input_dict, x_noun=x_noun)
    else:
        noun = get_noun(input_dict)
    if not noun and not x_noun:
        print(f"What do you want to {verb_name}?")
        return
    if local and noun:
        if noun and noun.location == loc.current or noun.location == loc.inv_place:
            return noun
        if noun and x_noun:
            noun = get_noun(input_dict, x_noun=x_noun, get_str=True)
            print(f"There's no {assign_colour(noun)} around here to {verb_name} anything with.")
        else:
            print(f"There's no {assign_colour(noun)} around here to {verb_name}.")
        return
    return noun

def item_attributes(format_tuple, input_dict):
    """Prints the vars for the first noun found in the input_dict. Not entirely useful, especially when meta {noun} exists."""
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
    sem_or_dir = get_dir_or_sem(input_dict)

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

def inst_from_idx(dict_entry:dict, kind_str:str, return_str=False) -> itemInstance:
    """Returns `str_name` or `instance` from `dict_entry`, using the `kind_str` provided."""
    logging_fn()
    if return_str:
        return dict_entry[kind_str]["str_name"]

    return dict_entry[kind_str]["instance"]

def turn_cardinal(prospective_cardinal, turning = True):
    logging_fn()

    if prospective_cardinal in ("left", "right"): ## TODO move this to relocate so it's all done in the same place
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
                test = loc.by_cardinal_str(k)
                if test:
                    prospective_cardinal = test

    if isinstance(prospective_cardinal, dict):
        print(f"PROSPECTIVE CARDINAL IS A DICT: {prospective_cardinal}")
        traceback_fn()
        #test = prospective_cardinal.get("cardinal")
        #if test:
        #    prospective_cardinal = test.get("instance")
        #else:
        #    test = prospective_cardinal.get("instance")
        #    if test:
        #        prospective_cardinal = test

    if not isinstance(prospective_cardinal, cardinalInstance):
        print("turn_cardinal: prospective_cardinal is not cardinal_inst")
        traceback_fn()

    if prospective_cardinal != loc.current:
        relocate(new_cardinal = prospective_cardinal)
    else:
        if turning:
            print(f"You're already facing the {assign_colour(loc.current, card_type="ern_name")}.\n")
        else:
            from env_data import get_loc_descriptions
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

def go_through_door(noun:itemInstance, open_door:bool, destination:cardinalInstance|placeInstance, inside_location):
    logging_fn()
    #print(f"go through door // noun: {noun}, open door: {open_door} // destination: {destination}")
    if (destination == inside_location or destination == inside_location.place) and loc.current == noun.ext_location:
        open_door = True
    if (hasattr(noun, "is_open") and noun.is_open == True) or open_door:
        if not (hasattr(noun, "is_open") and noun.is_open == True):
            setattr(noun, "is_open", True)
            import random
            door_open_text = random.choice(registry.door_open_strings)
            if destination == inside_location or destination == inside_location.place:
                door_open_text = door_open_text.replace("[[inside]]", "inside")
            else:
                door_open_text = door_open_text.replace("[[inside]]", "outside")
            print(assign_colour(door_open_text, colour="enter_door"))
            print()
        # want like, recklessly/cautiously/quietly, depending on playstyle. Long way off that but wanted to note it.
        if isinstance(destination, cardinalInstance):
            return relocate(new_location = destination.place, new_cardinal=destination)
        else:
            return relocate(new_location=destination)

    else:
        if noun.location.visited:
            print(f"You see the closed {assign_colour(noun)} in front of you; you can't phase through a closed door.\n")
        return relocate(new_cardinal=noun.location)

def move_through_trans_obj(noun, input_dict):
    #print(f"move_through_trans_obj, noun: {noun}")
    logging_fn()
    if noun and (not hasattr(noun, "int_location") or not hasattr(noun, "ext_location")):
        print(f"Noun {noun} does not have an int_location or ext_location (or either). Aborting.")
        return None
    #print(f"move_through_trans_obj. input_dict: {input_dict}")
    verb = get_verb(input_dict, get_str=True)
    location = get_location(input_dict)
    if noun:
        noun_str = get_noun(input_dict, get_str=True)
    if not noun:
        #get_transition_noun()
        noun, noun_str, _, _ = get_nouns(input_dict)

    if not noun:
        print("Not much to go on here, no noun, no location...")
    #print(f"VERB: {verb} // location: {location} // noun: {noun}")
    entry_words = ("enter", "go", "inside")
    leaving_words = ("leave", "depart", "exit")
    if verb in ("enter", "leave", "depart", "exit"):
        open_door = True
    else:
        open_door=False

    inside_location = noun.int_location ## Noun must have both enter loc and exit_to_loc if it has either.
    outside_location = noun.ext_location

    def invert_cardinal_str(destination:cardinalInstance = None):
        """ Inverts the cardinal direction of the given `destination`, so that when you leave a door you are facing away from the door (ie, leaving a door on the west side of a location exits you to the east).\n\nIf a `placeInstance` is given, returns the `placeInstance` immediately as there is no cardinal to invert."""
        if isinstance(destination, placeInstance):
            return destination
        if not destination:
            destination = outside_location
        new_cardinal_str = invert_cardinals[destination.name]
        new_cardinal = loc.by_cardinal_str(cardinal_str=new_cardinal_str, loc = destination.place)
        return new_cardinal

    if loc.current == inside_location:
        currently_inside = True
    else:
        currently_inside = False

    if currently_inside:
        if verb in leaving_words or (get_dir_or_sem(input_dict) and get_dir_or_sem(input_dict) == "outside" and verb == "go"):
            #print(f"verb in leaving words ({verb}) // Location: {location}")
            if location == inside_location or location == inside_location.place or not location:
                #print("location == inside_location or not location")
                if get_cardinal(input_dict):
                    cardinal = get_cardinal(input_dict)
                else:
                    cardinal = invert_cardinal_str(outside_location)
                return go_through_door(noun, open_door=True, destination = cardinal, inside_location = inside_location)
        if verb in leaving_words or verb == "go":
            if location and location != inside_location and location != inside_location.place:
                dir_or_sem = get_dir_or_sem(input_dict)
                if dir_or_sem and dir_or_sem == "to":
                    #print("go to > go through door")
                    if get_cardinal(input_dict):
                        cardinal = get_cardinal(input_dict)
                    else:
                        new_card = invert_cardinals.get(outside_location.name)

                    if isinstance(location, placeInstance):
                        location = loc.by_cardinal_str(cardinal_str = new_card, loc = location)
                    else:
                        location = loc.by_cardinal_str(cardinal_str = new_card, loc = location.place)

                    return go_through_door(noun, open_door=True, destination = location, inside_location = inside_location)

        if verb in entry_words:
            if verb == "go" and (location and location != inside_location):
                #print("go to <not inside>")
                return go_through_door(noun, open_door=True, destination = invert_cardinal_str(location), inside_location = inside_location)
            print(f"You're already in the {assign_colour(loc.current.place)}.")
            return 1

    else:
        if verb in leaving_words:
            if location == inside_location or location == inside_location.place or not location:
                print(f"You're already outside the {assign_colour(inside_location, card_type="place")}.")
                return 1

        if verb in entry_words and (location == None and noun) or (location == inside_location or location == inside_location.place):
            if loc.current.place == outside_location.place or verb == "go":
                if inside_location.place.visited:
                    open_door = True

                if get_cardinal(input_dict):
                    cardinal = get_cardinal(input_dict)
                else:
                    cardinal = inside_location

                return go_through_door(noun, open_door=open_door, destination = cardinal, inside_location = inside_location)
            else:
                if not noun_str:
                    noun_str = get_noun(input_dict, get_str=True)
                    if not noun_str:
                        noun_str = get_location(input_dict, get_str=True)

                print(f"There's no {assign_colour(noun_str, colour="yellow")} here to enter.")
                return


        else:
            print(f"Not picked up yet in move_through_trans_obj: {input_dict} // noun: {noun}")
            return

    print(f"End of def enter without being referred anywhere. Noun: {noun} // input_dict: {input_dict}")

def go(format_tuple, input_dict, no_noun=None): ## move to a location/cardinal/inside
    logging_fn()
    #print(f"format for def go: {format_tuple}, input_dict: {input_dict}")
    if len(format_tuple) == 1:
        if not "cardinal" in format_tuple and not "location" in format_tuple:
            print("Where do you want to go?")
            return
        else:
            if "cardinal" in format_tuple:
                return relocate(new_cardinal=get_cardinal(input_dict))
            else:
                return relocate(new_location=get_location(input_dict))

    noun=None

    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    if (len(format_tuple) == 2 and (noun_entry or location_entry)) or (len(format_tuple) == 3 and (direction_entry and direction_entry["text"] in to_words)):
        #print(f"def go len2 or len3. Format tuple: {format_tuple}, dict: {input_dict}")
        if noun_entry:
            noun = noun_entry["instance"]
        elif location_entry and registry.by_name.get(location_entry.get("str_name")):
            noun = registry.instances_by_name(location_entry.get("str_name"))
            if noun:
                noun = noun[0] # arbitrary, while we check for transition items we don't want to pick locations etc yet.

        if noun and ("transition" in noun.item_type or "loc_exterior" in noun.item_type):
            #if location_entry and location_entry["instance"] == loc.current.place:
            if enter(format_tuple, input_dict, noun):
                return

    if (direction_entry and direction_entry["str_name"] in to_words and len(format_tuple) < 5) or (not direction_entry and len(format_tuple) < 4) or (direction_entry and not cardinal_entry and not location_entry):
        if location_entry and not cardinal_entry:
            location = location_entry["instance"]
            if location == loc.current.place:
                #print("location instance == loc.current.place")
                if input_dict[0].get("verb") and input_dict[0]["verb"]["str_name"] == "leave":
                    if enter(format_tuple, input_dict, noun=(list(loc.current.transition_objs)[0]) if noun else None):
                        return

                    print("You can't leave without a new destination in mind. Where do you want to go?")
                    return

            if hasattr(location, "transition_objs") and location not in ({}, None) and location.transition_objs and not no_noun:
                #print(f"hasattr location_entry[instance], transition_objs: {location.transition_objs}")
                for obj in location.transition_objs:
                    print(f"OBJ: {obj}")
                    if obj.int_location.place in (loc.current, location):
                        return enter(format_tuple, input_dict, noun=obj)#: # this only goes to enter if we're aiming for or leaving the interior location.

            print("Going to new_relocate")
            relocate(new_location=location)
            return

        elif cardinal_entry and not location_entry:
            if cardinal_entry["instance"].place == loc.current.place:
                turn_cardinal(cardinal_entry["instance"])
                return
            else:
                relocate(new_location=location_entry["instance"], new_cardinal = cardinal_entry["instance"])
                return

        elif direction_entry and not location_entry and not cardinal_entry:# and verb_entry["str_name"] in ("go", "turn", "head", "travel", "move"):
            if direction_entry["str_name"] in ("left", "right"):
                turn_cardinal(direction_entry["str_name"])
                return
            else:
                if get_noun(input_dict):
                    ("Going to enter via get_noun")
                    enter(format_tuple, input_dict, get_noun(input_dict))
                    return
                if direction_entry["text"] in ("outside", "inside"):
                    if enter(format_tuple, input_dict):
                        return
                    #has_and_true(loc.current, "is_ext_location")
                print("Sorry, where do you want to go?")
                return

        elif location_entry and cardinal_entry:
            relocate(new_location=location_entry["instance"], new_cardinal = cardinal_entry["instance"])
            return
        print("End of if location_entry and not cardinal_entry: elif chain")

    elif direction_entry["str_name"] == "from":
        if location_entry and location_entry["instance"] != loc.current.place():
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

    #noun = get_noun(input_dict)
    noun, noun_text, _, _ = get_nouns(input_dict)

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
            outcome = item_interactions.find_local_item_by_name(noun, noun_text)
            if isinstance(outcome, itemInstance):

                noun = outcome
            else:
                print(f"No noun outcome from find_local_item_by_name in def look. Instead: {outcome}")
            #if hasattr(noun, "description_detailed"):
            #    read(format_tuple, input_dict)
            #else:
            print(f"NOUN: {noun}, vars: {vars(noun)}")
            if hasattr(noun, "ext_location"):
                if noun.ext_location.place == loc.current.place:
                    return turn_cardinal(noun.ext_location, turning = True)
            item_interactions.look_at_item(noun, noun_entry)
        elif location_entry:
            from misc_utilities import look_around
            look_around()
            return

    elif len(format_tuple) == 3:

        if noun and format_tuple[1] == "direction":
            outcome = item_interactions.find_local_item_by_name(noun, noun_text)
            if isinstance(outcome, itemInstance):
                noun = outcome
            else:
                print(f"No noun outcome from find_local_item_by_name in def look. Instead: {outcome}")
            return item_interactions.look_at_item(noun, noun_entry)

        if format_tuple[2] == "cardinal" and format_tuple[1] == "direction":
            return turn_cardinal(inst_from_idx(input_dict[2], "cardinal"), turning = False)

        if format_tuple[1] == "sem" and semantic_entry["text"] == "for":
            return find(format_tuple, input_dict)

        if format_tuple[2] == "location" and format_tuple[1] == "direction":
            noun = registry.by_name.get(location_entry["str_name"])
            if noun:
                noun = noun[0]
                print(f"Is noun: {noun}")
                if noun.location.place == loc.current.place:
                    if loc.current != noun.location:
                        turn_cardinal(prospective_cardinal=noun.location, turning = False)
                    else:
                        turn_cardinal(inst_from_idx(input_dict[2], "location"), turning = True)
            else:
                from misc_utilities import look_around
                return look_around()



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
    if not noun or isinstance(noun, str):
        noun = get_transition_noun(None, format_tuple, input_dict, take_first=True)
        if not noun:
            noun_str = get_noun(input_dict, get_str=True)
            if not noun_str:
                return 0
            noun = registry.by_name.get(noun_str)
            if noun:
                if isinstance(noun, list):
                    noun = noun[0]
            if not noun:
                for word, parts in registry.plural_words.items():
                    if noun_str in parts:
                        noun = registry.by_name.get(word)
                        if isinstance(noun, list):
                            noun = noun[0] # arbitrarily take the first.
            if not noun:
                return 0

    if not location:
        location = loc.current.place
    if not isinstance(location, placeInstance) and isinstance(location, cardinalInstance):
        location = location.place

    local_items = set()
    items_at = {}
    for card in location.cardinals:
        cardinal_inst = loc.by_cardinal_str(card, location)
        items = registry.get_item_by_location(cardinal_inst)
        if items:
            local_items = local_items | set(items)
            items_at[cardinal_inst] = set(items)

    if (local_items and noun in local_items) and (items_at.get(loc.current) and noun in items_at.get(loc.current)):
        for entry in input_dict:
            if input_dict[entry].get("noun"):
                input_dict[entry]["noun"]["instance"] = noun
                input_dict[entry]["noun"]["str_name"] = noun.name
        look(format_tuple, input_dict)
        return 1

        # I'm not sure what I want to do with items that are in the same location but different cardinal. For now I guess we treat all non-current-cardinal the same, but might change it later.
        #print(f"Noun.location: {noun.location}, current loc: {loc.current}")

    if "inventory_place" in noun.location.place_name:
        print(f"There's a {assign_colour(noun)} in your inventory, is that what you were looking for?")
        return 1

    print(f"There's a {assign_colour(noun)} at {assign_colour(noun.location.ern_name, "loc")}, is that what you were looking for?")
    return 1
    #for card in items_at:
    #    if noun in items_at[card]:
    #        #if len(items_at) == 1:
    #        print(f"There's a {assign_colour(noun)} at {assign_colour(card.place_name, "loc")}, is that what you were looking for?")
    #        return card

def get_timeblocks(input_dict, verb:str):

    timeblock = 1
    sem = get_dir_or_sem(input_dict)
    sem2 = get_dir_or_sem(input_dict, 2)
    num = get_number(input_dict)

    if num == "0":
        print(f"You can't {verb} for no duration. Returning.")
        return
    if sem and sem2 and sem == "for":
        sem = sem2
 # ^  make this bit a reusable fn.  v
    if (sem and sem2 and sem == sem2) or not sem2:
        if sem in ["while", "hour", "hours"]:
            if not num:
                timeblock = 1
            else:
                timeblock = int(int(num)/2)
                if timeblock == 0:
                    timeblock == 1
            if verb == "read" and timeblock > 5:
                print("You can't read for that long, but a you sit down to read for a few hours.")
                timeblock = 4
        elif sem in ("day", "days"):
            if not num:
                timeblock = 12
            else:
                timeblock = int(num) * 12
            if verb == "read":
                print("You can't read for days at a time, but maybe for a few hours...")
                timeblock = 4

        ## TODO: At some point put a reasonable limit on how long you can read/wait for, or have a set of potential random interruptions. Assumedly there'll be tasks like learning information from a book you've read, and if you can just 'read for 12 hrs'. For now just limited to 4 hours (unless you specify 5 hrs, I've allowed that.)
    return timeblock, num

def read(format_tuple, input_dict):
    """Reads `description_details` for the noun in `input_dict` if found, otherwise directs to `def look`."""
    logging_fn()
    #verb_inst = get_verb(input_dict)
    noun, noun_str, _, _ = get_nouns(input_dict)
    if noun:
        outcome = item_interactions.find_local_item_by_name(noun, noun_str, verb="look")
        if outcome:
            noun = outcome

    if not noun:
        ### access_str options for this part: "inventory_only" initially, then run again with "not_in_inv"
        # Using 'inv_then_local lets it run these optins internally, checking local if no results from inv, instead of calling it twice here.
        ## Amendment: Using 'look' to get both inv and local, will prioritise non-maps then prioritise inv.
        options = item_interactions.find_local_items_by_itemtype("books_paper", "all_local")
        if not options:
            print("What do yo want to read?")
            return
        nouns = list(i for i in options if hasattr(i, "description_detailed") and i.description_detailed and not hasattr(i, "is_map"))
        if not nouns: # allow map if nothing else to read.
            # Hm. Maybe we get inv and local and then determine. Because if there's a magazine locally and a map in inv, we should read the magazine first.
            nouns = list(i for i in options if hasattr(i, "description_detailed") and i.description_detailed)
        if not nouns:
            print("There's nothing here to read.")
            return

        else:
            if len(nouns) == 1:
                noun = nouns[0]
            else:
                noun = list(i for i in nouns if i.location == loc.inv_place)
                if noun:
                    noun = noun[0]
                else:
                    noun = nouns[0] # if no option in inventory, just take what you find.

    if not noun:
        print("There's nothing here to read. (We should never hit this point. If this prints, fix whatever's wrong in def read(). Exiting.)")
        exit()

    if hasattr(noun, "location") and (noun.location == loc.inv_place or noun.location == loc.current): # shouldn't need this, it should be selected by outcome already.
        if hasattr(noun, "description_detailed") and noun.description_detailed:
            to_print = None
            if noun.description_detailed.get("is_tested"):
                from rolling import roll_risk
                outcome = roll_risk()
                print(f"Outcome: {outcome}")
                if outcome > 1:
                    test = noun.description_detailed.get("crit")
                    if not test:
                        test = noun.description_detailed.get(1)
                    if test:
                        to_print = test
                        #NOTE: have not accounted for various degrees of success here. Need to.
                else:
                    test = noun.description_detailed.get("failure")
                    if not test:
                        test = noun.description_detailed.get(4)
                    if test:
                        to_print = test
            else:
                to_print = noun.description_detailed.get("print_str")

            if to_print:

                timeblock, num = get_timeblocks(input_dict, verb="read")

                from interactions.player_movement import update_loc_data
                from set_up_game import game
                beforetime = game.time
                _ = update_loc_data(loc.current, loc.current, timeblocks = timeblock)
                aftertime = game.time
                text = aftertime
                extra2 = ""
                if noun.location == loc.inv_place:
                    nountext = f"your {assign_colour(noun)}"
                else:
                    nountext = f"a nearby {assign_colour(noun)}"

                print(f"You settle down to read {nountext} in the {loc.current.ern_name}.\n")
    # ignore the next bit, it's not implemented yet.
                to_print = "A gardening magazine, featuring the latest popular varieties of [[choose.plant]] and a particularly opinionated think-piece on the Organic vs Not debate. Could be a decent way to wait out a couple of hours if you ever wanted to."
                if "[[choose." in to_print: ## TODO: This must be done in item init, not at runtime.
                    from misc_utilities import choose_option
                    to_print = choose_option(to_print)

                print(assign_colour(to_print, "b_yellow"))
                print(f"\nIt was {beforetime}, now it's {text}.{extra2}")
                return

            if hasattr(noun, "is_map"):
                item_interactions.show_map(noun)

            if hasattr(noun, "event"):
                from eventRegistry import events
                outcome, moved_children = events.is_event_trigger(noun, "item_is_read")
                if moved_children:
                    print_moved_children(moved_children, noun, outcome)

            return

        else:
            look(format_tuple, input_dict)
            return

    print(f"You can't see a {assign_colour(noun)} to read.")


def eat(format_tuple, input_dict):
    logging_fn()
    noun_inst = get_noun(input_dict)

    verb = input_dict[0]["verb"]["str_name"]
    if hasattr(noun_inst, "can_consume"):
        print(f"You decide to {verb} the {assign_colour(noun_inst)}.")
        print("something something consequences")
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

    noun, noun_str, noun2, noun2_str = get_nouns(input_dict)
    dir_or_sem = get_dir_or_sem(input_dict)

    if noun and dir_or_sem and dir_or_sem in ("with", "using"):
        if noun2:
            print(f"You want to clean the {assign_colour(noun)} with the {assign_colour(noun2)}? Not implemented yet.")
            return
        elif get_location(input_dict):
            print(f"You want to clean {assign_colour(get_location(input_dict))} with {assign_colour(noun)}? Odd choice, and not one that's implemented yet.")

    print(f"Cannot process {input_dict} in def clean() End of function, unresolved. (Function not yet written)")


def burn(format_tuple, input_dict):
    logging_fn()

    noun, noun_str, noun2, noun2_str = get_nouns(input_dict)
    outcome = item_interactions.find_local_item_by_name(noun, noun_str, verb="burn")
    if isinstance(outcome, itemInstance):
        noun = outcome

    from config import require_firesource
    can_burn = False
    firesource_found = False

    if not has_and_true(noun, "can_burn") or hasattr(noun, "can_burn") and not noun.can_burn:
        print(f"The {assign_colour(noun)} can't burn, it seems.")
        return

    elif has_and_true(noun, "is_burned") and not hasattr(noun, "can_burn_twice"): # can_burn_twice -- something that became 'burned x' that can burn again to become ash.
        print(f"The {assign_colour(noun)} is already burned.")
        return

    if require_firesource:
        outcome = item_interactions.find_local_item_by_name(noun2, noun2_str, verb="fire_source")
        if isinstance(outcome, itemInstance):
            noun2 = outcome

        if noun2:
            dir_or_sem = get_dir_or_sem(input_dict)
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

    noun, _, noun2, _ = get_nouns(input_dict)
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
    noun, noun_str, noun2, noun2_str = get_nouns(input_dict)
    if not noun:
        return
    broken = None
    if not format_tuple.count("noun") == 2:
        if noun.smash_defence > 4:
            print(f"What do you want to break the {assign_colour(noun)} with?")
            return
        #assume the ground is hard. ground isn't properly set up yet so we'll assume for now.
        print(f"You smash the {assign_colour(noun)} on the ground.\n") # NOTE: added_printline
        broken = noun

    else:
        if noun2:
            dir_or_sem = get_dir_or_sem(input_dict)
            if dir_or_sem and dir_or_sem in ("with", "using", "on", "against"):
                for attack in ('smash', 'slice'):
                    if getattr(noun2, f"{attack}_attack") > getattr(noun, f"{attack}_defence"):
                        print(f"You {attack} the {assign_colour(noun)} with the {assign_colour(noun2)}, and it breaks.")
                        broken = noun#set_noun_attr(("is_broken", True), noun=noun)
                        break
                    elif getattr(noun, f"{attack}_attack") < getattr(noun2, f"{attack}_defence"):
                        print(f"You {attack} the {assign_colour(noun)} with the {assign_colour(noun2)}, but {assign_colour(noun2)} was weaker - {assign_colour(noun2)} breaks.")
                        broken = noun2#set_noun_attr(("is_broken", True), noun=noun_2)
                        break
                    elif getattr(noun, f"{attack}_attack") == getattr(noun2, f"{attack}_defence"):
                        print(f"You {attack} the {assign_colour(noun)} with the {assign_colour(noun2)}, but the {assign_colour(noun)} and the {assign_colour(noun2)} are evenly matched; nothing happens.")
                        return
    if broken:
        set_noun_attr(("is_broken", True), noun=broken)
        if hasattr(broken, "children") and broken.children:
            noun_children = set()
            for child in broken.children:
                noun_children.add(child)
    #NOTE: This move does not trigger the event trigger checks. If an item being removed from a container etc is a trigger, registry.move_item will not check it. So for now I do a manual line just to notify, but this is not a solution.
                if hasattr(child, "event") and child.event:
                    print(f"{child.name} is connected to an event: {child.event.name}")

            for child in noun_children:
                registry.move_item(inst=child, location=loc.current, old_container=broken, no_print=True)

            turn_cardinal(prospective_cardinal=loc.current, turning = False)
    print()
    print(f"Cannot process {input_dict} in def break_item() End of function, unresolved. (Function not yet written)")
    return

def check_key_lock_pairing(noun_1, noun_2):
    """Checks if noun_1 is a key, and if noun_2 is a matching key."""
    logging_fn()
    if hasattr(noun_1, "is_key") and hasattr(noun_2, "requires_key") and noun_1 == noun_2.requires_key:
        return 1
    return 0


def lock_unlock(format_tuple, input_dict, do_open=False, noun=None, noun2=None):
    logging_fn()

    key=None
    lock=None
    verb = get_verb(input_dict)
    if not noun or not noun2:
        noun, noun_str, noun2, noun2_str = get_correct_nouns(input_dict, verb="use")
    #print("lock_unlock: noun, noun_str, noun2, noun2_str: ", noun, noun_str, noun2, noun2_str)

    if len(format_tuple) == 2:
        print(f"{assign_colour(noun.name)} requires a key, no?")
        return

    if len(format_tuple) == 4:
        #print(f"Format is len 4: {format_tuple}")
        if noun2:
            accessible_1, _, _ = can_interact(noun)
            accessible_2, _, _ = can_interact(noun2)
            if accessible_1 and accessible_2:
                #print(f"{noun} and {noun2} are both accessible.")
                success = check_key_lock_pairing(noun, noun2)
                if success:
                    key = noun
                    lock = noun2

                else:
                    success = check_key_lock_pairing(noun2, noun)
                    if success:
                        key = noun2
                        lock = noun
                if key and lock:
                    print(f"KEY: {key}, LOCK: {lock}")
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
                    print(f"You can't open the {assign_colour(noun)} with {assign_colour(noun2)}")
                    return

            else:
                if not accessible_1:
                    print(f"There's no {assign_colour(noun)} here to unlock.")
                    return
                else:
                    if accessible_1 and not accessible_2:
                        print(f"You don't have a {assign_colour(noun2_str, colour="yellow")} to unlock the {assign_colour(noun)} with.")
                        return
                print(f"{noun} and/or {noun2} are not accessible: 1: {accessible_1}, 2: {accessible_2}")
        else:
            print(f"Not two nouns in {format_tuple}")

    else:
        print(f"Don't know what to do with {input_dict} in lock_unlock.")
        return


def print_children_in_container(noun_inst:itemInstance):
    """Should really just use the existing inventory list printer with noun_inst.children input list."""
    children = set()
    if hasattr(noun_inst, "children") and noun_inst.children:
        children = noun_inst.children
        for item in children:
            if "is_cluster" in item.item_type:
                if int(item.has_multiple_instances) > 1:
                    print(f"ITEM NICENAME IN PRINT CHILDREN: {item.nicename}")
                    print(f"ITEM NICENAMES IN PRINT CHILDREN: {item.nicenames}")

        print(f"\nThe {assign_colour(noun_inst)} contains:")
        children = ", ".join(col_list(children, nicename=True))
        if noun_inst.name == "matchbox":
            for child in noun_inst.children:
                print(f"Child: {child}, type: {type(child)}")
                print(f"VARS CHILDREN: {vars(child)}")
        print(f"  {children}")


def simple_open_close(format_tuple, input_dict):
    """The primary open/close function. Redirects to `use_item_w_item`"""
    logging_fn()

    if get_meta(input_dict) == "inventory":
        meta(format_tuple, input_dict)

    verb_inst = get_verb(input_dict)

    noun, noun_str, noun2, noun2_str = get_nouns(input_dict)

    if len(format_tuple) > 3:
        if ('verb', 'noun', 'direction', 'location') == format_tuple:
            location = get_location(input_dict)
            if (location == loc.inv_place or loc.inv_place.place):
                print("The location is actually the inventory.")
                if noun.location != loc.inv_place:
                    print(f"The {assign_colour(noun)} isn't in your inventory...")
                    return
                print("The item is in your inventory, continue.")
            elif location != loc.current and location != loc.current.place:
                print(f"You aren't at {assign_colour(location, colour="loc")}, so how can you open {assign_colour(noun)}?")
                return
        else:
            use_item_w_item(format_tuple, input_dict)
            return

    interactable, val, meaning = can_interact(noun) # succeeds if accessible
    #print("interactable, val, meaning: ", interactable, val, meaning)
    if not interactable:
        if val == 6:
            print(f"You can't open something you aren't nearby to...")#\n noun location: {noun.location}")
            return
        print(f"You can't do that right now.\n[{noun} / {meaning}]")
        return

    outcome = item_interactions.is_loc_ext(noun)
    if outcome:
        if noun2:
            test = item_interactions.is_loc_ext(noun, return_trans_obj=True)
            if test == noun2:
                noun = noun2
        else:
            print("Else from is_loc_ext in simple_open_closed: ", outcome)
            return

    if not hasattr(noun, "is_open"):
        print(f"You can't open the {assign_colour(noun)} (no hasattr(noun, 'is_open')).")
        return

    if verb_inst.name == "open":
        if not hasattr(noun, "can_be_opened") or (hasattr(noun, "can_be_opened") and noun.can_be_opened != True):
            print(f"You can't open the {assign_colour(noun)}; it doesn't look like something you can open.")
            return
            #print(f"meaning: {meaning}")
        if noun.is_open == True:
            print(f"{assign_colour(noun)} is already open.")
            return

        if hasattr(noun, "is_locked") and noun.is_locked == True:
            print(f"You can't open a locked {assign_colour(noun)}.")
            #open_close(format_tuple, input_dict)
            return

        if val in can_open_codes:
            print(f"You open the {assign_colour(noun)}.")
            set_noun_attr(("is_open", True), noun=noun)
            return
       # _, confirmed_container, reason_val, meaning  = registry.check_item_is_accessible(noun_inst)

        if val in in_container_codes and hasattr(noun, "contained_in"):#confirmed_container:
            print(f"You need to remove the {assign_colour(noun)} from the {assign_colour(noun.contained_in)} it's in, first.")
            return

        else:
            print(f"Cannot open {noun.name} because {meaning}.")
            return
        #print(f"reason_val: {reason_val}, meaning: {meaning}")

    else:
        if noun.is_open == False:
            print(f"The {assign_colour(noun)} is already closed.")
            return

        if hasattr(noun, "can_be_closed") and noun.can_be_closed == False:
            print(f"You try to close the {assign_colour(noun)}, but you can't.")
            return
        print(f"You close the {assign_colour(noun)}.")
        #print(f"noun.is_open now: {noun.is_open}")
        set_noun_attr(("is_open", False), noun=noun)
        #print(f"noun.is_open now: {noun.is_open}")
        return

def combine(format_tuple, input_dict):
    logging_fn()
    #if verb_noun_sem_noun, verb_noun_dir_noun, combine a+b
    #if verb_noun == what do you want to combine it with.
    noun, _, noun2, _ = get_nouns(input_dict)

    get_correct_nouns(input_dict)
    if not noun2:
        print(f"What do you want to combine with the {assign_colour(noun)}")
        return

    if "container" in noun2.item_type:
        #check relative sizes here; haven't implemente that anywhere yet.
        #assuming the sizes are suitable:
        put(format_tuple, input_dict) # might be a fair guess if b is a container?
        return

    print(f"You want to combine {assign_colour(noun)} and {assign_colour(noun2)}? Sounds good, but we don't do that yet...")

    #print(f"Cannot process {input_dict} in def combine() End of function, unresolved. (Function not yet written)")
    pass

def separate(format_tuple, input_dict):
    logging_fn()

    noun, _, noun2, _ = get_nouns(input_dict)
    if not noun:
        return

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

def move(format_tuple, input_dict):
    logging_fn()

    noun, _, noun2, _ = get_nouns(input_dict)
    if get_location(input_dict) and get_dir_or_sem(input_dict): # so if it's 'move to graveyard', it just treats it as 'go to'.
        if noun:
            print(f"This probably isn't a simply 'move to graveyard', seeing as we have {noun} here. Not written yet, sorry.")
            return
        go(format_tuple, input_dict)
        return

    if noun and noun2:
        dir_or_sem = get_dir_or_sem(input_dict)
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

    noun, noun_str, noun2, noun2_str = get_nouns(input_dict)

    added_to_inv = False

    outcome = item_interactions.find_local_item_by_name(noun, verb="take", current_loc=loc.current, hidden_cluster=True)
    #print(f"[OUTCOME from def take: `{outcome}`]")
    if isinstance(outcome, itemInstance):
        noun = outcome
    else:
        if outcome == None:
            logging_fn(f"Going to print error from def take `{input_dict}`")
            print_failure_message(noun=noun_str, verb="take")
            return

    def can_take(noun):
        logging_fn()
        added_to_inv = False

        container, reason_val, meaning = registry.run_check(noun)

        if reason_val not in (0, 3, 4, 5, 8):
            for item, value in input_dict.items():
                if 'noun' in value:
                    text = input_dict[item]["noun"].get("text")
            print(f"Sorry, you can't take a {assign_colour(text)} right now.")
            return 1, None
            #print(f"Reason code: {reason_val}")
        elif reason_val == 5:
            print(f"The {assign_colour(noun)} {is_plural_noun(noun)} already in your inventory.")
            return 1, None # return none so it doesn't run the pick up check again

        else:
            if hasattr(noun, "can_pick_up") and noun.can_pick_up:
                if reason_val in (3, 4):
                    outcome = registry.move_from_container_to_inv(noun, parent=container)
                    added_to_inv = outcome
                    #print("added to inv, returning.")
                    return 0, added_to_inv
                elif reason_val == 0:
                    outcome = registry.move_item(noun, location = loc.inv_place)
                    if outcome in loc.inv_place.items:
                        #print("Outcome is in inventory. (line 1480)")
                        return 0, outcome
                    if noun in loc.inv_place.items:
                        #print("noun_inst is in inventory. line 1483")
                        added_to_inv = noun
                        return 0, added_to_inv
                print(f"{noun} failed to be processed, not reasonval 3, 4, 5. reason_val: {reason_val}/{meaning}")
            else:
                print(f"You can't pick up the {assign_colour(noun)}.")
                return 1, added_to_inv
        print("Failed in can_take, returning defaults.")
        return 0, noun

    dir_or_sem = get_dir_or_sem(input_dict)
    location = get_location(input_dict)
    if format_tuple in (("verb", "noun"), ("verb", "direction", "noun")):
        cannot_take, added_to_inv = can_take(noun)
        if cannot_take and hasattr(noun, "can_consume"):
            print(f"\nDid you mean to consume the {assign_colour(noun)}? ")
            return

    elif dir_or_sem in ("in", "at") and location:
        if location == loc.current or location == loc.current.place:
            cannot_take, added_to_inv = can_take(noun)

    elif format_tuple == (("verb", "noun", "direction", "noun")): ## will later include scenery. Don't know how that's going to work yet.
        verb_str = input_dict[0]["verb"]["str_name"]
        if verb_str in ("take", "remove", "separate", "get"):
            dir_inst = get_dir_or_sem(input_dict)
            if dir_inst not in ("and", "from"):
                print(f"dir_inst is {dir_inst}; was expecting 'from' or 'and'. May need to adjust take function.")

            container_inst = noun2
            if "battery" in noun.item_type and hasattr(container_inst, "takes_batteries") and container_inst.takes_batteries and container_inst.has_batteries:
                print(f"You can take the batteries from the {assign_colour(container_inst)}. (Though it's not actually scripted yet.)")

            container, reason_val, reason = registry.run_check(noun)
            #print(f"REASON: {reason_val} / {reason}")
            if reason_val not in (0, 3, 4):
                #print(f"Cannot take {noun_inst.name}.")
                #print(f"Reason code: {reason_val}")
                #print_failure_message(verb="take", noun=noun)
                if reason_val == 5:
                    print(f"{assign_colour(noun)} is already in your inventory.")
                    return
                print(f"Sorry, you can't take the {assign_colour(noun)} right now.")
                return
            else:
                if container == container_inst and reason_val in (3, 4):
                    output_noun = registry.move_from_container_to_inv(noun, parent=container)
                    if output_noun in loc.inv_place.items:
                        added_to_inv = output_noun
                    else:
                        print("Tried to add {assign_colour(noun_inst)} to inventory, but something must have gone wrong.")
                        traceback_fn()
                else:
                    print(f"The {assign_colour(noun)} doesn't seem to be in {container_inst.name}.")

    else:
        print(f"Cannot process {input_dict} in def take() End of function, unresolved.")
        return

    if added_to_inv:
        if isinstance(added_to_inv, itemInstance):
            if added_to_inv != noun:
                noun = added_to_inv
        outcome, moved_children = events.is_event_trigger(noun, reason = "item_in_inv")
        if not outcome:
            print(f"The {assign_colour(noun)} {is_plural_noun(noun)} now in your inventory.")
        return

def put(format_tuple, input_dict, location=None):
    logging_fn()
    action_word = "You put"

    noun, _, noun2, _ = get_nouns(input_dict)
    sem_or_dir = get_dir_or_sem(input_dict)

    if noun2:
        if hasattr(noun2, "contained_in") and noun == noun2.contained_in:
            print(f"Cannot put {assign_colour(noun)} in {assign_colour(noun2)}, as {assign_colour(noun2)} is already inside {assign_colour(noun)}. You'll need to remove it first.")
            return
        if noun == noun2:
            print(f"You cannot put the {assign_colour(noun)} in itself.")
            return
        if sem_or_dir in ("in", "to", "into", "inside") and len(format_tuple) == 4:
            if hasattr(noun, "contained_in") and noun2 == noun.contained_in:
                print(f"The {assign_colour(noun)} is already in {assign_colour(noun2)}")
                return
            registry.move_item(noun, new_container=noun2, no_print=True)

            if noun in loc.inv_place.items or noun in registry.by_location[loc.inv_place]:
                exit(f"{assign_colour(noun)} still in inventory, something went wrong. Exiting.")
            else:
                text = smart_capitalise(f"{action_word} the {assign_colour(noun)} {sem_or_dir} the {assign_colour(noun2)}")
                print(text)
            return

    else:
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

    noun, _, noun2, _ = get_nouns(input_dict)

    if not noun:
        print("What do you want to throw?")
        return
    if len(format_tuple) == 2:
        print(f"Where do you want to throw the {assign_colour(noun)}?")
        return
    dir_or_sem = get_dir_or_sem(input_dict)

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
    noun, _, noun2, _ = get_nouns(input_dict)
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
                        if noun.ext_location == loc.current.place:
                            enter(format_tuple, input_dict, noun)
                            return
                    else:
                        print("No description here. Should be one eventually.")
                        return

    if noun2:
        dir_or_sem = get_dir_or_sem(input_dict)
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
    noun, noun_str, noun2, _ = get_nouns(input_dict)
    #noun = verb_requires_noun(input_dict, "drop", local=True)
    if isinstance(noun, str):
        print("Noun is not an instance obj.")
        if noun == "assumed_noun":
            noun = noun_str
    if not noun:
        print("What do you want to drop?")
        return

    outcome = item_interactions.find_local_item_by_name(noun=noun, access_str="drop_subject") # item being dropped (drop_target may be later if dropping into container etc.)
    #print(f"[OUTCOME from def drop: `{outcome}`]")
    if outcome and isinstance(outcome, itemInstance):
        #print_yellow(f"Found noun from find_local_item_by_name: {outcome}. Original: {noun}")
        noun = outcome
    else:
        outcome = print_failure_message(noun=noun_str, verb="drop")
        return

    if len(input_dict) == 3:
        direction = get_dir_or_sem(input_dict)
        if noun and direction and (direction == "here" or direction in down_words):
            input_dict.pop(2, None)

    if len(input_dict) == 2:
        container, reason_val, meaning = registry.run_check(noun)
        #print(f"reason val: {reason_val}, meaning: {meaning}, for item: {noun}")
        if reason_val == 5:
            registry.move_item(noun, location = loc.current)
            #registry.drop(noun)

        elif reason_val == 3:
            print(f"You can't drop the {assign_colour(noun)}; you'd need to get it out of the {assign_colour(container)} first.")
            return

        else:
            print(f"You can't drop the {assign_colour(noun)}; you aren't holding it.")
            return

    elif len(input_dict) == 4:
        dir_or_sem = get_dir_or_sem(input_dict)
        #item_to_place, direction, container_or_location = three_parts_a_x_b(input_dict)
        #print(f"item_to_place: {item_to_place}, direction: {direction}, dir type: {type(direction)}")
        if dir_or_sem in ["in", "into", "on", "onto", "at"]:
            if get_location(input_dict):
                if get_location(input_dict) != loc.current:
                    print(f"You can't drop the {assign_colour(noun)} at {assign_colour(get_location(input_dict))} because you aren't there.")
                    return

            container, reason_val, meaning = registry.run_check(noun)
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
            triggered, moved_children = events.is_event_trigger(noun, reason = "item_not_in_inv")
            if moved_children:
                print_moved_children(moved_children, noun, triggered)
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
    actor_noun, noun_str, target_noun, noun2_str = get_correct_nouns(input_dict, verb="use", access_str=None, access_str2=None)

    dir_or_sem = get_dir_or_sem(input_dict)

    verb = get_verb(input_dict)

    if not target_noun:
        print(f"No second noun: {format_tuple} should not be in use_item_w_item function. Check routing.")
        return

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

    print(f"Failed use_item_w_item: FORMAT TUPLE: {format_tuple}")
    print(f"Cannot process {input_dict} in def use_item_w_item() End of function, unresolved. (Function partially written but doesn't do anything.)")

def use_item(format_tuple, input_dict):
    logging_fn()

    if len(format_tuple) == 4:
        use_item_w_item(format_tuple, input_dict)
        return

    noun = verb_requires_noun(input_dict, "use", local=True)
    if "map" in noun.name:
        item_interactions.show_map(noun)
        return

    print(f"Cannot process {input_dict} in def use_item() End of function, unresolved. (Function not yet written)")

def wait(format_tuple, input_dict):

    timeblock, num = get_timeblocks(input_dict, verb="wait")

    if not get_noun(input_dict):
        from interactions.player_movement import update_loc_data
        from set_up_game import game
        beforetime = game.time
        export = update_loc_data(loc.current, loc.current, timeblocks = timeblock)
        aftertime = game.time
        if export:
            if num:
                text = f"{num} {aftertime}s later"
            else:
                extra = "the next "
                text = f"{extra}{aftertime}"
            extra2 = " You've been stood here a while..."
        else:
            text = aftertime
            extra2 = ""
        print(f"You stand around for a while, just letting time pass. \n\nIt was {beforetime}, now it's {text}.{extra2}")
        return

    print(f"This is the end of def wait(); what went wrong? Format: {format_tuple} // input dict: {input_dict}")
            #if export: # this is the "LATE MORNING OF DAY 10" text.
            #    from printing import print_yellow
            #    print_yellow(f"\n{export}")

def enter(format_tuple, input_dict, noun=None):
    logging_fn()

    location = get_location(input_dict)
    if not noun:
        if format_tuple == ("verb", "noun", "noun"):
            noun = get_noun(input_dict, 2)
        else:
            noun = get_noun(input_dict)


    if noun:
        if "transition" in noun.item_type:
            return move_through_trans_obj(noun, input_dict)

        if "loc_exterior" in noun.item_type:
            if noun.transition_objs:
                for item in noun.transition_objs:
                    return move_through_trans_obj(item, input_dict)

    if location or (not location and not noun and get_dir_or_sem(input_dict) and get_dir_or_sem(input_dict) in ("outside", "inside")):
        if not location:
            location = loc.current
        if hasattr(location, "transition_objs") and location.transition_objs:
            for item in location.transition_objs:
                return move_through_trans_obj(item, input_dict)

    else:
        print("enter else")
        return look(format_tuple, input_dict)

MOVE_UP = "\033[A"
print_extra_decorations = True

def make_foreline(new_str, input_str):
    diff = len(new_str) - len(input_str)
    new_str = f"\033[0;32m[\033[1;32m<  {input_str}  >\033[0;32m]"
    half = int(diff/2)
    leftovers = diff - (half + half) - 1 -2
    foreline = f"\033[0;32m" + " .-" + (f" " * (half-3)) + (" " * (len(input_str))) + (f" " * (half + leftovers)) + "-."
    #print(MOVE_UP, end='')
    print(MOVE_UP, end='')
    print(foreline) # Needs this little dance to print correctly whether it's user input or test. If I wasn't running the text commands I could just hardcode it directly at input.
    print()
    return f"\033[0;32m" + " '-" + (f" " * (half-2)) + (" " * (len(input_str))) + (f" " * (half + leftovers-1)) + "-'", new_str

def router(viable_format, inst_dict, input_str=None):
    logging_fn()

    verb_inst = None
    quick_list = []
    input_strings = []
    for v in inst_dict.values():
        for data in v.values():
            quick_list.append(data["str_name"])
            input_strings.append(data["text"])

    from config import print_input_str # This will probably be the default. Definitely don't need three options.
    if print_input_str:
        print(f"{MOVE_UP}", len(input_str) * " ")
        new_str = f"[<  {input_str}  >]"
        #print(f"{MOVE_UP}", end="")
        if print_extra_decorations:
            foreline, new_str = make_foreline(new_str, input_str)
        input_str = new_str
        if input_str:
            print(f'{MOVE_UP}\033[1;32m{input_str}\033[0m')
            if print_extra_decorations:
                print(foreline, "\033[0m")
            print()

        else:
            print(f'{MOVE_UP}\n\033[1;32m[[  {" ".join(input_strings)}  ]]\033[0m\n')
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
            if not registry.by_name.get(mentioned_loc.name): # currently only loc_exterior nouns share names with locations, so we skip those here.
                if mentioned_loc != loc.current and mentioned_loc != loc.current.place and mentioned_loc != loc.inv_place.place:
                    if func.__name__ not in can_be_not_local:
                        print(f"You want to {verb_inst.name} at {assign_colour(mentioned_loc)} but you aren't there...")
                        return
        response = func(format_tuple = viable_format, input_dict = inst_dict)
        return response
    except Exception as e:
        print(f"Failed to find the correct function to use for {verb_inst}: {e}")
