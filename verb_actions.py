""" Receives format and input_dict from verb.membrane and forwards the data to a verb function, eg `def g`et, `def drop`, `def eat`."""

from interactions.meta_commands import yes_test
from logger import logging_fn, traceback_fn
from env_data import cardinalInstance, placeInstance, locRegistry as loc
from interactions import item_interactions
from interactions.player_movement import relocate
from itemRegistry import itemInstance, registry
from misc_utilities import assign_colour, col_list, generate_clean_inventory, has_and_true, is_plural_noun, look_around, smart_capitalise, print_failure_message
from printing import print_yellow
from verb_definitions import directions, semantics

can_open_codes = [0,1,5,8]
can_pickup_codes = [0,3,4]
in_container_codes = [3,4]
interactable_codes = [0,3,4,5,8]
can_drop_codes = [0, 3, 5]

#movable_objects = ["put", "take", "combine", "separate", "throw", "push", "drop", "set", "move"]

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
def in_types(noun:itemInstance, itemtype:str) -> bool:
    if itemtype in noun.item_type:
        return True
    return False

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

def set_noun_attr(*values, noun:itemInstance, event_type:str = None):
    """Sets the attr/val for each set in `values` to `noun`, while also checking `noun` and `values` in `is_event_trigger`."""
    logging_fn()
    """
    'noun' must be provided at `noun=  `, as it needs to be differentiated from *values
    """
    from eventRegistry import trigger_acts, events
    if hasattr(noun, "event") and getattr(noun, "event") and hasattr(noun, "is_event_key") and noun.is_event_key:
        print()
        outcome, moved_children = events.is_event_trigger(noun_inst = noun, reason = values, event_type = event_type)
        if moved_children:
            print_moved_children(moved_children, noun, values)
        if not outcome:
            print(MOVE_UP) # To add the extra line. Needed for unlocking key items, to avoid always adding another newline after unlocking.

    else:
        triggers = {}
        for item in trigger_acts:
            for k, v in trigger_acts[item].items():
                triggers[k] = v

        events.event_print(f"Values: {values}")
        for item_val in values:
            events.event_print(f"item_val in values: {item_val}")
            item, val = item_val
            #print(f"TRIGGERs: {triggers}")
            if item in triggers:
                #print(f"item in triggers: {item}")
                if val == triggers[item]:
                    events.event_print("Checking is_event_trigger")
                    outcome, moved_children = events.is_event_trigger(noun_inst = noun, reason = item_val, event_type = event_type)#values)
                    if moved_children:
                        print_moved_children(moved_children, noun, item)

            setattr(noun, item, val)

            if item in update_description_attrs:
                from itemRegistry import registry
                if hasattr(noun, "descriptions") and noun.descriptions:
                    registry.init_descriptions(noun)

def get_transition_noun(noun, format_tuple, input_dict, take_first=False, return_if_exterior = False):
    """Finds transition objects from `loc_exterion` nouns, returning the first transition object found."""
    logging_fn()
    local_items_list = registry.get_item_by_location(loc.current)
    #print(f"local items list: {local_items_list}")
    if isinstance(noun, list) and len(noun) == 1:
        noun = noun[0]

    if hasattr(noun, "is_loc_exterior"):
        if not hasattr(noun, "transition_objs") or (hasattr(noun, "transition_objs") and not noun.transition_objs):
            if loc.by_name.get(noun.name):
                location = loc.by_name[noun.name]
                if hasattr(location, "loc_exterior_items") and location.loc_exterior_items:
                    #print(f"Location {location.name} has exterior items: {location.loc_exterior_items}") ### I don't know it this ever applies...
                    if return_if_exterior:
                        return True
                #if hasattr(location, "transition_objs") and location.transition_objs:
                    #print(f"Location {location.name} has transition items: {location.transition_objs}")

        #print(f"noun is loc exterior: {vars(noun)}")
        if hasattr(noun, "transition_objs") and noun.transition_objs:
            #print("noun has transition objects")
            if isinstance(noun.transition_objs, itemInstance):
                noun = noun.transition_objs
                return noun

            else:
                if len(noun.transition_objs) == 1:
                    #print("1 noun.transition_objs")
                    for neW_noun in noun.transition_objs:
                        print(f"Single transition_objs: {neW_noun}\n")
                        #return neW_noun
                else:
                    print(f"More than one transition object for {noun}. Can't deal with this yet. Exiting.")
                    exit()
        else:
            #print(f"noun does not have transition nouns.")
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
                print(f"HAs loc item: {test_item}")
                if take_first:
                    return test_item
                if isinstance(test_item, str) and local_items_list:
                    for loc_item in local_items_list:
                        if loc_item.name == test_item:
                            noun = loc_item
                            return noun

                elif isinstance(test_item, itemInstance) and local_items_list:
                    if test_item in local_items_list:
                        noun = test_item
                        return noun
                    else:
                        for item in local_items_list:
                            if item.name == test_item.name:
                                return item

        return None


    return noun

def get_correct_nouns(input_dict, verb=None, access_str=None, access_str2=None, hold_error_messages=False):
    """
    Just a function to compile the getting of noun data so each one doesn't have to do it individually.
    Takes input_dict and optionally, verb, and returns {`noun`, `noun_str`, `noun_reason`, `noun2`, `noun2_str`, `noun2_reason`}.
    Uses default settings for the verb, so not all suitable for all usecases, but the vast majority.
    """
    logging_fn
    # Have added but not tested `access_str=None, access_str2=None`, to be able to specify access strings from the outside. This would expand it to basically all usecases.
    noun, noun_str, noun2, noun2_str = get_nouns(input_dict)
    if not noun and not noun_str and not noun2 and not noun2_str:
        return None, None, None, None, None, None # so it doesn't claim it can't find instances if there are just no nouns in the dict at all (eg 'look at graveyard')
    from verbRegistry import VerbInstance
    from npcRegistry import npcInstance
    if verb:
        if isinstance(verb, VerbInstance):
            verb = verb.name
    else:
        verb = get_verb(input_dict).name

    if noun:
        outcome = item_interactions.find_local_item_by_name(noun, verb=verb, access_str=access_str, current_loc=loc.current)
        if isinstance(outcome, itemInstance|npcInstance):
            noun = outcome
        else:
            if outcome == None and not hold_error_messages:
                noun=noun_str
                if not noun2:
                    logging_fn(f"Going to print error from def {verb} `{input_dict}`")
                    print_failure_message(noun=noun_str, verb=verb, init_dict=input_dict)
                    return None, noun_str, None, None, noun2_str, None
            #noun = None

    if noun2:
        outcome = item_interactions.find_local_item_by_name(noun2, verb=verb, access_str=access_str2, current_loc=loc.current)
        if outcome and isinstance(outcome, itemInstance|npcInstance):
            noun2 = outcome
        else:
            if outcome == None and not hold_error_messages:
                noun2 = noun2_str
                return None, None, None, None, None, None
            #noun2 = None
    if not isinstance(noun, itemInstance|npcInstance) or (noun2 and not isinstance(noun2, itemInstance|npcInstance)):
        logging_fn(f"Going to print error from def {verb} `{input_dict}`")
        print_failure_message(noun=noun, noun2=noun2, verb=verb, init_dict=input_dict)
        return None, None, None, None, None, None

    _, noun_reason, _ = registry.run_check(noun)
    _, noun2_reason, _ = registry.run_check(noun2)
    return noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason

def moved_item(item):

    if item and hasattr(item, "event") and item.event:
        from eventRegistry import events
        triggered, moved_children = events.is_event_trigger(noun_inst = item, reason = "item_not_in_inv")
        if moved_children:
            print_moved_children(moved_children, item, triggered)
        return triggered

def move_a_to_b(a:itemInstance, b:placeInstance|itemInstance, action:str=None, direction:str=None, current_loc = None):
    logging_fn() ## REPLACE WITH REGISTRY.MOVE_ITEM()
    #print(f"MOVE A TO B IN USE: {a} / {b}")
    location = None
    from itemRegistry import container_limit_sizes
   ## This is the terminus of any 'move a to b' type action. a must be an item instance, b may be an item instance (container-type) or a location.
    if not direction:
        if action == "dropping" or action == "you dropped the":
            direction = "at"
        else:
            if isinstance(b, itemInstance):
                direction = "in"
            else:
                direction = "to"
    if direction == "down":
        direction = "down here at the"
    if not action:
        action = "moving"

    if isinstance(a, itemInstance):
        if not b:
            b = loc.current
        if isinstance(b, cardinalInstance):
            if b == loc.current or b == loc.inv_place:
                a_origin = (a.location if a.location != loc.no_place and a.location != loc.inv_place else a.contained_in)
                item_interactions.add_item_to_loc(a, b)
                print(f"a.location after move: {a.location}, location should be {b}")
                if not moved_item(a) or b == loc.inv_place:
                    if b == loc.inv_place:
                        origin = ""
                        if a_origin:
                            if isinstance(a_origin, itemInstance):
                                origin = f"from the {assign_colour(a_origin)} "
                            else:
                                origin = f"from {assign_colour(a_origin, card_type="place_name")} "
                            text = smart_capitalise(f"{action} {assign_colour(a, nicename=True)} {origin}{direction} your inventory.")
                    else:
                        text = smart_capitalise(f"{action} {assign_colour(a)} {direction} {assign_colour(b, card_type = "place_name")}.")
                    print(text)
                return "yes"

        elif in_types(b, "container"): ## This won't work long term, currently the only option for move noun x noun is if hte second is a container. Not 'move noun towards noun', etc, which I want for later. No idea how to implement it, but for now I'm just noting it here.
            if not b.is_open:
                #print("b is not open")
                if b.is_locked:
                    return f"The {assign_colour(b)} seems to be locked."
                return f"The {assign_colour(b)} seems to be closed."

            #print(f"{b.name} is a container with size limit of {b.container_limits}.")
            if isinstance(b.container_limits, str):
                container_size = container_limit_sizes.get(b.container_limits)
            else:
                container_size = b.container_limits
            if isinstance(a, itemInstance) and hasattr(a, "item_size"):
                #print(f"{a.name} is an item with size {a.item_size}.")
                if isinstance(a.item_size, str):
                    item_size = container_limit_sizes.get(a.item_size)
                else:
                    item_size = a.item_size
                if item_size < container_size:
                    #print(f"{a.name} will fit in {b.name}")
                    if registry.move_item(a, new_container=b, no_print=True):
                        #print("After registry.move_item")
                        success = moved_item(a)
                        if not success:
                            return f"You {action} the {assign_colour(a)} {direction} the {assign_colour(b)}."
                        else:
                            if a in b.children:
                                return f"success: {success}"
                            print("after moved_item success, a not in b.children")

                else:
                    return f"The {assign_colour(a)} is too big to put inside the {assign_colour(b)}."

    elif isinstance(b, tuple):
        print(f"b is a tuple: {b} -- DOES THIS EVER HAPPEN? wHERE FROM?")
        if not current_loc:
            current_loc = loc.current.place
        if b[0] in current_loc:
            location = b[0]
            print(f"{action} {a.name} {direction} {b}")
            item_interactions.add_item_to_loc(a, b)
            moved_item(a)

        else:
            print("Can only move items to the location you're currently in.")

    elif isinstance(b, cardinalInstance):
        item_interactions.add_item_to_loc(a, b)
        moved_item(a)

    else:
        print(f"B is not an instance.. b: {b} type: {type(b)}")
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
            print("LOCATION")
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
                    continue
                verb_entry = entry
            if kind == "direction":
                if direction_entry != None:
                    continue
                direction_entry = entry

            if kind == "cardinal":
                if cardinal_entry != None:
                    continue
                cardinal_entry = entry
            if kind == "location":
                if location_entry != None:
                    continue
                location_entry = entry
            if kind == "semantic":
                if semantic_entry != None:
                    continue
                semantic_entry = entry

    return verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry


     #################################

## Simple 'get this element' functions. ##

def get_component(input_dict:dict, kind="noun", x_count=None, get_str=False) -> itemInstance|placeInstance|cardinalInstance|str:
    """ if get_str, dir_or_sem gets `str_name`. Everything else gets `text`. 'Number' has no instance option."""
    if kind in ("sem", "semantic", "dir", "direction"):
        kind = "dir_sem"
        text = "str_name"
    else:
        text = "text"

    str_only = ["number", "meta", "dir_sem"]
    counter = 0
    for data in input_dict.values():
        for kinds, entry in data.items():
            if kind in kinds:
                if x_count:
                    counter += 1
                    if counter == x_count:
                        if get_str or kind in str_only:
                            return entry[text]
                        return entry["instance"]
                else:
                    if get_str or kind in str_only:
                        return entry[text]
                    return entry["instance"]


def get_component_parts(input_dict:dict, kind="noun", x_count=None) -> itemInstance|placeInstance|cardinalInstance|str:
    """ Always returns `entry["instance"], entry[text]`. dir_or_sem gets `"str_name"`. Everything else gets `"text"`."""
    if kind in ("sem", "semantic", "dir", "direction"):
        kind = "dir_sem"
        text = "str_name"
    else:
        text = "text"

    #str_only = ["number", "meta", "dir_sem"]
    counter = 0
    for data in input_dict.values():
        for kinds, entry in data.items():
            if kind in kinds:
                if x_count:
                    counter += 1
                    if counter == x_count:
                        return entry["instance"], entry[text]
                else:
                    return entry["instance"], entry[text]

#def get_cardinal(input_dict:dict) -> itemInstance:
#    logging_fn()
#    for i, _ in enumerate(input_dict):
#        if input_dict[i].get("cardinal"):
#            return list(input_dict[i].values())[0]["instance"]

def get_verb(input_dict:dict, x_verb=None, get_str=False) -> itemInstance:
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
            if "direction" in kind or "semantic" in kind:
                if not x_val:
                    return entry["str_name"] # Changed to str_name so that compound_semantics are read correctly.

                sem_counter += 1
                if sem_counter == x_val:
                    return entry["str_name"]

def get_meta(input_dict:dict) -> str:
    """Returns `text` for the first `meta` entry in `input_dict`."""
    logging_fn()

    for data in input_dict.values():
        for kind, entry in data.items():
            if "meta" in kind:
                return entry["text"]


def item_attributes(format_tuple, input_dict):
    """Prints the vars for the first noun found in the input_dict. Not entirely useful, especially when meta {noun} exists."""
    inst_to_print = get_noun(input_dict)
    if not inst_to_print:
        inst_to_print = get_location(input_dict) # just in case I want location attributes instead

    from pprint import pprint
    pprint(vars(inst_to_print))
    print(f"Want to print other instances of {input_dict}?")
    if yes_test(f"Want to print other instances of {inst_to_print.name}?"):
        for item in registry.instances_by_name(inst_to_print.name):
            print("\n")
            pprint(vars(item))
            print()


##### Parts Parsing ########

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

def component(format_tuple:tuple, input_dict:dict, kind_str:str, return_str:bool=False, x_val:int=None):
    if kind_str in format_tuple:
        idx = format_tuple.index(kind_str)
        if x_val:
            idx = format_tuple.index(kind_str, idx) # start looking for index at previous index

        if return_str:
            return input_dict[idx][kind_str]["str_name"]

        if not input_dict[idx][kind_str]["instance"]:
            return input_dict[idx][kind_str]["text"]
        return input_dict[idx][kind_str]["instance"]

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

    if not isinstance(prospective_cardinal, cardinalInstance):
        print("turn_cardinal: prospective_cardinal is not cardinal_inst")
        traceback_fn()
        exit()

    if prospective_cardinal != loc.current:
        relocate(new_cardinal = prospective_cardinal)
    else:
        if turning:
            print(f"You're already facing the {assign_colour(loc.current, card_type="ern_name")}.")
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
        look(("verb", "semantic"), None)
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

        noun, noun_str, _, _, _, _, = get_correct_nouns(input_dict, verb="use")
        if not noun:
            noun = noun_str
        #noun = get_noun(input_dict)
        location = get_component(input_dict, kind="location")
        cardinal = get_component(input_dict, kind="cardinal")

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
            if not loc.current == noun.ext_location:
                door_open_text = f"Having made your way to the {noun.ext_location.ern_name}, " + door_open_text
            print(assign_colour(door_open_text, colour="enter_door", caps=True))
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
    cardinal = get_component(input_dict, kind="cardinal")

    noun_check, noun_str, _, _ = get_nouns(input_dict)

    if not noun:
        noun = noun_check

    if not noun:
        print("Not much to go on here, no noun, no location...")
    #print(f"VERB: {verb} // location: {location} // noun: {noun}")
    entry_words = ("enter", "go", "inside", "push") # adding 'push' so 'push door' also enters. Not sure if I want this though.
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
                if not cardinal:
                    cardinal = invert_cardinal_str(outside_location)
                return go_through_door(noun, open_door=True, destination = cardinal, inside_location = inside_location)

        if verb in leaving_words or verb == "go":
            if location and location != inside_location and location != inside_location.place:
                dir_or_sem = get_dir_or_sem(input_dict)
                if dir_or_sem and dir_or_sem == "to":
                    #print("go to > go through door")
                    if cardinal and isinstance(cardinal, cardinalInstance):
                        new_card = cardinal.name
                    elif cardinal and isinstance(cardinal, str):
                        new_card = cardinal
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

                if not cardinal:
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
            cardinal = get_component(input_dict, kind="cardinal")
            if cardinal:
                return relocate(new_cardinal=cardinal)
            else:
                #print() # was this necessary for spacing? I don't think so? #CHECK
                return relocate(new_location=get_component(input_dict, kind="location"))

    noun=None

    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    if (len(format_tuple) == 2 and (noun_entry or location_entry)) or (len(format_tuple) == 3 and (direction_entry and direction_entry["text"] in to_words)):
        #print(f"def go len2 or len3. Format tuple: {format_tuple}, dict: {input_dict}")
        noun = noun_entry["instance"] if noun_entry else None
        if location_entry and not location_entry["instance"] and location_entry["str_name"]:
            noun = registry.by_name.get(location_entry["str_name"])
            if noun:
                noun = next(iter(noun), None)
            else:
                from verb_membrane import membrane
                for comp_loc in membrane.compound_locations: # this should be done in the parser.
                    if location_entry["text"] in membrane.compound_locations[comp_loc]:
                        location_entry["str_name"] = comp_loc
                        location_entry["instance"] = loc.place_by_name(comp_loc)

                if membrane.compound_locations.get(location_entry["text"]):
                    location_entry["instance"] = membrane.compound_locations[location_entry["text"]]
            #print(f'registry.by_name.get(location_entry.get("str_name"): {registry.by_name.get(location_entry.get("str_name"))}')

        if not noun and location_entry and registry.by_name.get(location_entry.get("str_name")):
            #print("no noun but location with str_name that is a location")
            noun = registry.instances_by_name(location_entry.get("str_name"))
            noun = next(iter(noun), None)

        if noun and (in_types(noun, "transition") or in_types(noun, "loc_exterior")):
            #if location_entry and location_entry["instance"] == loc.current.place:
            if enter(format_tuple, input_dict, noun):
                return

    if (direction_entry and direction_entry["str_name"] in to_words and len(format_tuple) < 5) or (not direction_entry and len(format_tuple) < 4) or (direction_entry and not cardinal_entry and not location_entry):
        if location_entry and not cardinal_entry:
            location = location_entry["instance"]
            if location and location == loc.current.place:
                #print("location instance == loc.current.place")
                if input_dict[0].get("verb") and input_dict[0]["verb"]["str_name"] == "leave":
                    if enter(format_tuple, input_dict, noun=(noun if noun else None)):
                        return

                    print("You can't leave without a new destination in mind. Where do you want to go?")
                    return

            if location and hasattr(location, "transition_objs") and location not in ({}, None) and location.transition_objs and not no_noun:
                #print(f"hasattr location_entry[instance], transition_objs: {location.transition_objs}")
                for obj in location.transition_objs:
                    #print(f"OBJ: {obj}")
                    if obj.int_location.place in (loc.current, location):
                        return enter(format_tuple, input_dict, noun=obj)

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
                if get_noun(input_dict): # if direction == "in" vs "into" needs differentiation.
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


def look(format_tuple=None, input_dict=None, force_look=False): # force_look - stops 'read door' from turning into 'go to shed'.
    logging_fn()

    if not format_tuple or len(format_tuple) == 1 or (format_tuple == tuple(("verb", "semantic")) and (not input_dict or (input_dict and get_dir_or_sem(input_dict) == "around"))):
        print("first look around")
        from misc_utilities import look_around
        look_around()
        return

    if get_meta(input_dict) == "inventory":
        meta(format_tuple, input_dict)
        return

    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason= get_correct_nouns(input_dict, verb="look")


    if noun2:
        if not isinstance(noun2, itemInstance):
            print(f"Sorry, there's no `{noun2_str}` around here.")
            return
        if noun_reason in interactable_codes and noun2_reason in interactable_codes:
            if direction_entry:
                dir1 = direction_entry["text"]
                dir2 = get_dir_or_sem(input_dict, x_val=2)
            if dir2 and dir2 == "in":
                if in_types(noun2, "container"):
                    if not hasattr(noun, "contained_in") or not noun.contained_in or noun.contained_in != noun2:
                        print(f"There's no {assign_colour(noun)} in the {assign_colour(noun2.name)}.")
                    else:
                        item_interactions.look_at_item(noun, noun_entry)
                        return
            else:
                print(f"`{assign_colour(noun2, caps=True)}` isn't a container.")
            return

        else:
            if in_types(noun2, "container"):
                print(f"Idk what to do with this input, honestly {noun2} is a container but I'm confused. {format_tuple} // {input_dict}")
                return
            outcome = item_interactions.find_local_item_by_name(noun, noun_str)
            if isinstance(outcome, itemInstance):
                print(f"You have both the {assign_colour(noun)} and the {assign_colour(noun2)} to hand, but I'm not sure what you want to do with them.")
                return

    if len(format_tuple) == 2:
        if cardinal_entry != None:
            turn_cardinal(cardinal_entry["instance"], turning = False)

        elif direction_entry != None: # if facing north, turn east, etc.)
            intended_direction = direction_entry["str_name"]
            if intended_direction in ("left", "right"):
                turn_cardinal(intended_direction, turning=False)

        elif noun:
            if not isinstance(noun, itemInstance):
                print(f"No noun outcome from find_local_item_by_name in def look. Instead: {outcome}")
                return

            if hasattr(noun, "ext_location") and not force_look:
                if noun.ext_location.place == loc.current.place:
                    return turn_cardinal(noun.ext_location, turning = True)
            item_interactions.look_at_item(noun, noun_entry)
        elif location_entry:
            from misc_utilities import look_around
            look_around()
            return

    elif len(format_tuple) == 3:
        #print("len(format_tuple) == 3")
        if noun and format_tuple[1] == "direction":
            #print(f"NOUN before look_at_item: {noun}")
            return item_interactions.look_at_item(noun, noun_entry)

        if format_tuple[2] == "cardinal" and format_tuple[1] == "direction":
            return turn_cardinal(inst_from_idx(input_dict[2], "cardinal"), turning = False)

        if format_tuple[1] == "semantic" and semantic_entry["text"] == "for":
            return find(format_tuple, input_dict)

        if format_tuple[2] == "location" and format_tuple[1] == "direction":
            noun = registry.by_name.get(location_entry["str_name"])
            if noun:
                noun:itemInstance = iter(next(noun), None)#noun[0] # it's a set now
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
        print(f"Cannot process input in def look(): \n{format_tuple} \n{input_dict}")

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

def get_hours_until(time_str):
    import choices
    from set_up_game import game

    new_idx = choices.time_of_day.index(time_str)
    current_idx = choices.time_of_day.index(game.time)

    if new_idx > current_idx:
        new = new_idx - current_idx
    else:
        remainder = 24 - current_idx
        new = remainder + new_idx
    return new


def get_timeblocks(input_dict, verb:str, noun:itemInstance=None):

    if noun and hasattr(noun, "reading_time"): # so you can set custom reading times for when time may not have been given explicitly. 'read x for 3 hours' will overrule the reading_time, but means that if you just 'read note' it won't automatically take an hour. reading time of 0 is instant, no time passes.
        timeblock = noun.reading_time
    else:
        timeblock = 1
    sem = get_dir_or_sem(input_dict)
    sem2 = get_dir_or_sem(input_dict, 2)
    num = get_number(input_dict)

    if num == "0":
        print(f"You can't {verb} for no duration. Returning.")
        return
    if sem and sem2 and sem == "for":
        sem = sem2

    if sem2 and sem == "until":
        import choices
        if sem2 in choices.time_of_day:
            num = get_hours_until(sem2)
            sem = sem2 = "hours"

 # ^  make this bit a reusable fn.  v
    if ((sem and sem2 and sem == sem2) or not sem2):
        if sem in ["while", "hour", "hours"]:
            timeblock = int(num) if num else 1
            if timeblock == 0:
                timeblock == 1
            if verb == "read" and timeblock > 5:
                print("You can't read for that long, but a you sit down to read for a few hours.")
                timeblock = 4
        elif sem in ("day", "days"):
            if not num:
                timeblock = 24
            else:
                timeblock = int(num) * 24
            if verb == "read":
                print("You can't read for days at a time, but maybe for a few hours...")
                timeblock = 4

        ## TODO: At some point put a reasonable limit on how long you can read/wait for, or have a set of potential random interruptions. Assumedly there'll be tasks like learning information from a book you've read, and if you can just 'read for 12 hrs'. For now just limited to 4 hours (unless you specify 5 hrs, I've allowed that.)
    return timeblock, num

def read(format_tuple, input_dict):
    """Reads `description_details` for the noun in `input_dict` if found, otherwise directs to `def look`."""
    logging_fn()
    #verb_inst = get_verb(input_dict)
    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="look")
    #noun, noun_str, noun2, noun2_str = get_nouns(input_dict)

    if not noun and not noun_str:
        options = item_interactions.find_local_items_by_itemtype("books_paper", "all_local")
        if not options:
            print("What do you want to read?")
            return
        nouns = list(i for i in options if i.descriptions.get("details") and not hasattr(i, "is_map"))
        if not nouns:
            nouns = list(i for i in options if i.descriptions.get("details"))
        if not nouns:
            print("There's nothing here to read.")
            return

        if len(nouns) == 1:
            noun = nouns[0]
        else:
            noun = list(i for i in nouns if i.location == loc.inv_place)
            if noun:
                noun = noun[0]
            else:
                noun = nouns[0] # if no option in inventory, just take what you can find.

    if not noun:
        print("There's nothing here to read. (We should never hit this point. If this prints, fix whatever's wrong in def read(). Exiting.)")
        exit()

    if noun2:
        dir_or_sem = get_dir_or_sem(input_dict)
        if dir_or_sem and dir_or_sem in ("in", "with"):
            if dir_or_sem == "in":
                if in_types(noun2, "container") and noun.contained_in == noun2:
                    pass
                elif in_types(noun2, "container"):
                    print(f"{assign_colour(noun, caps=True)} isn't in the {noun2}.")
                    return
            print(f"I don't know how {assign_colour(noun2, nicename=True)} will help with the reading...\n")# (Add something here for testing. Magnifying glass or something. on_use_for_reading attr, something like that.)")
        else:
            print(f"{assign_colour(noun, caps=True)} and the {assign_colour(noun2)} are both present, but {assign_colour(noun2)} doesn't seem like it'll help with reading much.")


    if noun.descriptions and noun.descriptions.get("details"):
        to_print = None
        from set_up_game import game
        if noun.descriptions["details"].get("is_tested"):
            from rolling import roll_risk
            outcome = roll_risk()
            if hasattr(noun, "has_been_tested"):
                noun.has_been_tested = "failed"
            print(f"Outcome: {outcome}")
            if outcome > 1:
                test = noun.descriptions["details"].get("crit")
                if not test:
                    test = noun.descriptions["details"].get(1)
                if test:
                    to_print = test
                    noun.descriptions["details"] = ({"print_str": test})

                if hasattr(noun, "has_datapoint") and noun.has_datapoint.get("on_success"):
                    game.datapoints.update(noun.has_datapoint["on_success"])
                    print(f"GAME DATAPOINTS: {game.datapoints}")
                    #NOTE: have not accounted for various degrees of success here. Need to.
            else:
                test = noun.descriptions["details"].get("failure")
                if not test:
                    test = noun.descriptions["details"].get(4)
                if test:
                    to_print = test
                    if not hasattr(noun, "has_been_tested"):
                        noun.has_been_tested = True
        else:
            noun.has_been_tested = False
            if noun.descriptions['details'].get("from_inside") and hasattr(noun, "int_location") and noun.int_location == loc.current: # don't do it this way, make it programattic.
                to_print = noun.descriptions['details']["from_inside"]
            else:
                to_print = noun.descriptions["details"].get("print_str")
            if hasattr(noun, "has_datapoint") and noun.has_datapoint.get("on_read"):
                game.datapoints.update(noun.has_datapoint["on_read"])

        if to_print:
            timeblock, _ = get_timeblocks(input_dict, verb="read", noun=noun)

            from interactions.player_movement import update_loc_data

            beforetime = game.time
            _ = update_loc_data(loc.current, loc.current, timeblocks = timeblock)
            aftertime = game.time

            if noun.location == loc.inv_place:
                nountext = f"your {assign_colour(noun)}"
            else:
                nountext = f"a nearby {assign_colour(noun)}"

            settle_text = "You settle down to read"
            if hasattr(noun, "has_been_tested") and noun.has_been_tested == "failed":
                settle_text = "You decide to give it another try, settling down to read"
            print(f"{settle_text} {nountext} in the {loc.current.ern_name}.\n\n{assign_colour(to_print, "enter_door")}")
            if beforetime != aftertime:
                print(f"\nIt was {beforetime}, now it's {aftertime}.")
            return

        if hasattr(noun, "is_map"):
            item_interactions.show_map(noun)

        if hasattr(noun, "event"):
            from eventRegistry import events
            outcome, moved_children = events.is_event_trigger(noun_inst = noun, reason = "item_is_read")
            if moved_children:
                print_moved_children(moved_children, noun, outcome)
        if to_print:
            return
    print("[[def read():   Going to look from end of def read() ]]")
    look(format_tuple, input_dict, force_look=True)
    return


def eat(format_tuple, input_dict):
    logging_fn()
    noun_inst = get_noun(input_dict)

    verb = input_dict[0]["verb"]["str_name"]
    if not noun_inst:
        print("This doesn't seem like something you can eat...")
        return

    if hasattr(noun_inst, "can_consume") and noun_inst.can_consume:
        print(f"You decide to {verb} the {assign_colour(noun_inst)}.")
        if noun_inst.is_safe and not noun_inst.effect:
            print(f"You don't feel too unwell after consuming the {assign_colour(noun_inst)}. So that's nice.")
        elif noun_inst.effect:
            print(f"Eating this does... {noun_inst.effect}. Not implemented yet.")
        else:
            print("It generically hurts you. [Not is_safe and no effect, and not effect. Not safe and no effect? No HP implemented for now.]")
        registry.delete_instance(noun_inst)
        return
    else:
        print(f"This {assign_colour(noun_inst)} doesn't seem like something you can eat...")


def clean(format_tuple, input_dict):
    logging_fn()

    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use")
    if len(format_tuple) == 2:
        if format_tuple == tuple(("verb", "location")):
        #if "verb" in format_tuple and "location" in format_tuple:
            print(f"You want to clean the {assign_colour(get_location(input_dict))}? Not implemented yet.")
            return
        elif "noun" in format_tuple:
            if hasattr(noun, "is_dirty") and noun.is_dirty:
                print(f"You clean the {assign_colour(noun)}. How nice.")
                noun.is_dirty = False
                return
            print(f"The {assign_colour(noun)} seems pretty clean already.")
            return

    dir_or_sem = get_dir_or_sem(input_dict)

    if noun and dir_or_sem and dir_or_sem in ("with", "using"):
        if noun2:
            print(f"You want to clean the {assign_colour(noun)} with the {assign_colour(noun2)}? Not implemented yet.")
            return
        elif get_location(input_dict):
            print(f"You want to clean {assign_colour(get_location(input_dict))} with the {assign_colour(noun)}? Odd choice, and not one that's implemented yet.")

    print(f"Cannot process {input_dict} in def clean() End of function, unresolved. (Function not yet written)")


def burn(format_tuple, input_dict):
    logging_fn()

    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="burn", access_str2="fire_source")
    #noun, noun_str, noun2, noun2_str = get_nouns(input_dict)
    if noun_str and not noun and not noun_reason: # assume failure printed in get_correct_nouns
        return

    from config import require_firesource
    can_burn = False
    firesource_found = False

    if not noun:
        print("Can only burn things for now, not places.")
        return

    if not has_and_true(noun, "can_burn") or hasattr(noun, "can_burn") and not noun.can_burn:
        print(f"The {assign_colour(noun)} can't burn, it seems.")
        return

    elif has_and_true(noun, "is_burned") and not hasattr(noun, "can_burn_twice"): # can_burn_twice -- something that became 'burned x' that can burn again to become ash.
        print(f"The {assign_colour(noun)} is already burned.")
        return

    if require_firesource:
        if noun2:
            dir_or_sem = get_dir_or_sem(input_dict)
            if dir_or_sem in ("with", "using"):
                if in_types(noun2, "firesource"):
                    firesource_found = noun2
                else:
                    print(f"You can't set a fire with {assign_colour(noun2)}.")
                    return

    if not require_firesource or (require_firesource and firesource_found):
        print(f"You set fire to the {assign_colour(noun)}, using the {assign_colour(firesource_found)}." if require_firesource else f"You set fire to the {assign_colour(noun)}.")
        set_noun_attr(("is_burned", True), noun=noun, event_type = "state_change")
        return

    elif require_firesource:
        print(f"You don't have anything to burn the {assign_colour(noun)} with.")

def barricade(format_tuple, input_dict):

    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use")
    #noun, _, noun2, _ = get_nouns(input_dict)
    if not noun:
        print("Barricade what, exactly?")
        return
    if not noun2:
        print(f"What do you want to use to barricade the {assign_colour(noun)}?")
        return
    if in_types(noun, "door_window"):
        print(f"You want to barricade the window/door {assign_colour(noun)}. A valiant effort, I just haven't coded it yet.")


def break_item(format_tuple, input_dict):
    logging_fn()
    print_desc = False
    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use")
    #noun, noun_str, noun2, noun2_str = get_nouns(input_dict)
    verb = get_verb(input_dict, get_str=True)
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
                cant_be_broken = None
                for attack in ('smash', 'slice'):
                    if getattr(noun2, f"{attack}_attack") > getattr(noun, f"{attack}_defence"):
                        if has_and_true(noun, "can_break"):
                            print(f"You {attack} the {assign_colour(noun)} with the {assign_colour(noun2)}, and it breaks.")
                            broken = noun#set_noun_attr(("is_broken", True), noun=noun)
                            break
                        else:
                            cant_be_broken = noun
                    elif getattr(noun2, f"{attack}_attack") < getattr(noun, f"{attack}_defence"):
                        if has_and_true(noun2, "can_break"):
                            print(f"You {attack} the {assign_colour(noun)} with the {assign_colour(noun2)}, but the {assign_colour(noun2)} was weaker - {assign_colour(noun2)} breaks.")
                            broken = noun2#set_noun_attr(("is_broken", True), noun=noun_2)
                            break
                        else:
                            cant_be_broken = noun2
                    elif getattr(noun, f"{attack}_attack") == getattr(noun2, f"{attack}_defence") or (has_and_true(noun, "can_break") and has_and_true(noun2, "can_break")):
                        print(f"You {attack} the {assign_colour(noun)} with the {assign_colour(noun2)}, but the {assign_colour(noun)} and the {assign_colour(noun2)} are evenly matched; nothing happens.")
                        return
                if cant_be_broken:
                    if cant_be_broken == noun:
                        print(f"You try to {verb} the {assign_colour(noun)} with the {assign_colour(noun2)}, but it doesn't seem like the {assign_colour(noun)} can break.")
                    else:
                        print(f"You try to {verb} the {assign_colour(noun)} with the {assign_colour(noun2)}, but neither one breaks.")
                    return
    print()
    if broken:
        set_noun_attr(("is_broken", True), noun=broken, event_type = "state_change")
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
        return
    print(f"Cannot process {input_dict} in def break_item() End of function, unresolved. (Function not yet written)")
    return

def check_key_lock_pairing(noun_1:itemInstance, noun_2:itemInstance):
    """Checks if noun_1 is a key, and if noun_2 is a matching key."""
    logging_fn()
    print(f"check key lock pairings for {noun_1}, {noun_2} // noun_1.item_type: {noun_1.item_type} // noun2.requires_key:")
    if hasattr(noun_2, "requires_key"):
        print(noun_2.requires_key)
        if noun_1 in noun_2.requires_key:
            return 1
    #if in_types(noun_1, "key") and hasattr(noun_2, "requires_key") and noun_1 == noun_2.requires_key:
    #    return 1
    return 0


def lock_unlock(format_tuple, input_dict, do_open=False, noun=None, noun2=None):
    logging_fn()

    key=None
    lock=None
    verb = get_verb(input_dict, get_str=True)
    if not noun or not noun2:
        noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use")
    #print("lock_unlock: noun, noun_str, noun2, noun2_str: ", noun, noun_str, noun2, noun2_str)

    if len(format_tuple) == 2:
        print(f"The {assign_colour(noun.name)} requires a key, no?")
        return

    if len(format_tuple) == 4:
        #print(f"Format is len 4: {format_tuple}")
        if noun2:
            accessible_1, _, _ = can_interact(noun)
            accessible_2, _, _ = can_interact(noun2)
            if accessible_1 and accessible_2:
                print(f"{noun} and {noun2} are both accessible.")
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
                        if verb == "lock":
                            print(f"You use the {assign_colour(key)} to lock the {assign_colour(lock)}.")
                            set_noun_attr(("is_open", False), ("is_locked", True), noun=lock)
                            return
                        else:
                            print(f"You can't unlock the {assign_colour(lock)}; it's already unlocked.")
                            return

                    elif do_open:
                        print(f"You open {lock} with {key}? This doesn't work yet.")

                else:
                    print(f"You can't {verb} the {assign_colour(noun)} with the {assign_colour(noun2)}.")
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
        print(f"Don't know what to do with {input_dict} in lock_unlock.")
        return


def print_children_in_container(noun_inst:itemInstance):
    """Should really just use the existing inventory list printer with noun_inst.children input list."""
    children = set()
    if hasattr(noun_inst, "children") and noun_inst.children:
        children = noun_inst.children
        #for item in children:
            #if "is_cluster" in item.item_type:
                #if int(item.has_multiple_instances) > 1:
                    #print(f"ITEM NICENAME IN PRINT CHILDREN: {item.nicename}")
                    #print(f"ITEM NICENAMES IN PRINT CHILDREN: {item.nicenames}")

        print(f"\nThe {assign_colour(noun_inst)} contains:")
        to_print_children, _ = generate_clean_inventory(children, for_children=False)#True)
        #children = ", ".join(children)
        children = ", ".join(col_list(to_print_children, nicename=True, not_inv=children))
        #if noun_inst.name == "matchbox":
            #for child in noun_inst.children:
                #print(f"Child: {child}, type: {type(child)}")
                #print(f"VARS CHILDREN: {vars(child)}")
        print(f"  {children}")


def simple_open_close(format_tuple, input_dict):
    """The primary open/close function. Redirects to `use_item_w_item`"""
    logging_fn()

    if get_meta(input_dict) == "inventory":
        meta(format_tuple, input_dict)

    verb = get_verb(input_dict)

    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use")
    #noun, noun_str, noun2, noun2_str = get_nouns(input_dict)

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
        print(f"The {assign_colour(noun)} isn't something you can {verb.name}.")#You can't open the {assign_colour(noun)} (no hasattr(noun, 'is_open')).")
        return

    if verb.name == "open":
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
    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use")
    #noun, _, noun2, _ = get_nouns(input_dict)

    if not noun2:
        print(f"What do you want to combine with the {assign_colour(noun)}?")
        return

    if noun2 and "container" in noun2.item_type:
        #check relative sizes here; haven't implemente that anywhere yet.
        #assuming the sizes are suitable:
        put(format_tuple, input_dict) # might be a fair guess if b is a container?
        return

    print(f"You want to combine {assign_colour(noun)} and {assign_colour(noun2)}? Sounds good, but we don't do that yet...")

    #print(f"Cannot process {input_dict} in def combine() End of function, unresolved. (Function not yet written)")
    pass

def separate(format_tuple, input_dict):
    logging_fn()

    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use")
    #noun, _, noun2, _ = get_nouns(input_dict)
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
                return child
            for other_child in parent.children:
                if other_child.name == child.name:
                    return other_child

    child = is_one_a_child(noun, noun2)
    if not child:
        child = is_one_a_child(noun2, noun)
        if not child:
            print(f"Sorry, I can't figure out how to separate the {assign_colour(noun)} from the {assign_colour(noun2)}.")
            return

    if not move_a_to_b(child, b=loc.inv_place, action="Moved"):
        print(f"Could not move {child}.")


def move(format_tuple, input_dict):
    logging_fn()

    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use")
    #noun, _, noun2, _ = get_nouns(input_dict)
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

    if noun_entry and direction_entry["text"] == "on":
        charger, phone, outcome = check_item_charger_match(actor_noun=noun_entry["instance"])
        if phone:
            if phone.is_charged:
                if phone.is_on:
                    print(f"The {assign_colour(phone)} is already on.")
                print(f"You turn on the {assign_colour(phone)}.")
                set_noun_attr(("is_on", True), noun=phone, event_type = "electronics")
                return
            else:
                print(f"You can't turn on the {assign_colour(phone)}, it's not charged.")
                return
        else:
            print("This isn't an object you can turn on...")
            return

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

def battery_check(verb="", battery=None, device=None):
    """Returns a tuple, first for battery (True if is a battery item_type), second for device (device.takes_batteries if takes_batteries, so the calling fn can directly see the expected battery if present.)"""
    #'verb' is usually just the verb, but like access_str, will use it for specific checks, eg 'uses_battery' to check if an item takes batteries but isn't otherwise a container.
    from verbRegistry import VerbInstance
    if isinstance(verb, VerbInstance):
        verb = verb.name
    takes_battery = batt_is_batt = False
    #print(f"Verb: {verb} / battery: {battery}, device: {device}")
    if device:
        if has_and_true(device, "takes_batteries"):
            takes_battery = device.takes_batteries

    if verb == "takes_batteries": #return None # verb is 'takes_battery' here but really this should fail everything that doesn't take batteries immediately.
        return None, takes_battery

    if battery:
        if "battery" in battery.item_type:
            batt_is_batt = battery.name
    #print(f"batt is batt: {batt_is_batt}, takes battery: {takes_battery}")
    return batt_is_batt, takes_battery
    print("checking if takes_batteries == str")
    if isinstance(device.takes_batteries, str):
        print(f"device.takes_batteries; {device.takes_batteries}")
        if battery and battery.name != device.takes_batteries:
            print(f"if battery.name != device.takes_batteries:: {battery.name} != {device.takes_batteries}")
            return None
    else:
        print(f"if battery.name != 'battery':: {battery.name}")

        if battery and battery.name != "battery":
            print(f"if battery.name != 'battery':: {battery.name}")
            return None # if the battery isn't the generic kind, fail it. No specialty batteries in regular battery devices.

    if not (device and battery):
        print(f"Device: {device} // battery: {battery}.")
        return None

    if isinstance(verb, str) and verb == "take" or isinstance(verb, itemInstance) and verb.name == "take": # we want to remove the batteries from the device.
        print("verb == take")
        if device.has_batteries:
            print(f"if device.has_batteries:: {device.has_batteries}")
            print(f"You can take the {assign_colour(battery)} from the {assign_colour(device)}.")
            device.has_batteries = False
            return True
        return "none_to_take"

    if verb == "put":
        print("verb == put")
        if not device.has_batteries:
            print(f"You fit the {assign_colour(battery)} into the {assign_colour(device)} and click it in place.")
            device.has_batteries = battery
            return True
        print(f"The {assign_colour(device)} already has batteries.")
        return "has_batteries_already"

    print(f"End of battery check: {battery} // device {device}")

    """ ``new`` version that didn't work. Did not correctly stop a watch with existing battery from having a second battery added. Here because it might be better in some ways but it was 2am when I wrote it so it's probably just broken. See if there's anything useful.
def battery_check(verb="", battery=None, device=None):
    from verbRegistry import VerbInstance
    if isinstance(verb, VerbInstance):
        verb = verb.name
    #'verb' is usually just the verb, but like access_str, will use it for specific checks, eg 'uses_battery' to check if an item takes batteries but isn't otherwise a container.
    print(f"Verb: {verb} / battery: {battery}, device: {device}")
    if device and not hasattr(device, "takes_batteries"):
        print(f'if device and not hasattr(device, "takes_batteries"):: {device}')
        return None # verb is 'takes_battery' here but really this should fail everything that doesn't take batteries immediately.
    print("device and does take batteries")
    if device and verb == "takes_batteries":
        return True
    print("checking battery")
    if battery:
        if not "battery" in battery.item_type:
            print(f"battery and not 'battery' in battery.item_type:: {battery}")
            return None

    print("checking if takes_batteries == str")
    if device and isinstance(device.takes_batteries, str) or isinstance(device.takes_batteries, bool) and device.takes_batteries:
        print(f"device.takes_batteries; {device.takes_batteries}")
        if battery and battery.name != device.takes_batteries:
            print(f"if battery.name != device.takes_batteries:: {battery.name} != {device.takes_batteries}")
            return None
        else:# battery and battery.name == device.takes_batteries:
            if device.has_batteries and device.has_batteries == battery:
                if verb == "take":
                    print(f"You take the {assign_colour(battery)} from the {assign_colour(device)}.")
                    device.has_batteries = False
                    battery.in_use = False
                    return True
                elif verb == "put":
                    print(f"The {assign_colour(device)} already has batteries.")
                    return "has_batteries_already"
            elif device.has_batteries and device.has_batteries.name == battery.name:
                print(f"Device has batteries but a different instance: Battery: {battery} / battery being used: {device.has_batteries}")
            elif not device.has_batteries:
                if verb == "take":
                    return "none_to_take"
                elif verb == "put":
                    print(f"You fit the {assign_colour(battery)} into the {assign_colour(device)} and click it in place.")
                    device.has_batteries = battery
                    battery.in_use = True
                    return True

    if not (device and battery):
        print(f"Device: {device} // battery: {battery}.")
        return None

    print(f"End of battery check: {battery} // device {device}")
    """
def act_on_battery_device(verb, noun, noun2):
    """Returns `success`, `battery`, `device`. Makes sure the battery has the right name and isn't in use, that the device doesn't already have batteries, and makes reasonable simple substitutions. """

    device = battery = None
    from verbRegistry import VerbInstance
    if isinstance(verb, VerbInstance):
        verb = verb.name
    battery, device_takes_batteries = battery_check(verb, noun, noun2)
    if battery and device_takes_batteries: # some kind of match, accurate or not
        #print(f"BATTERY: {battery} // device_takes_batteries: {device_takes_batteries}")
        if hasattr(noun2, "has_batteries") and noun2.has_batteries:
            if verb == "put":
                print(f"The {assign_colour(noun2)} already has a {assign_colour(noun2.has_batteries)}.")
                return "already_has_batteries", noun2.has_batteries, noun2
            if verb == "take":
                if noun2.has_batteries == noun:
                    device = noun2
                    battery = noun
                elif noun2.has_batteries.name == noun.name:
                    device = noun2
                    battery = noun2.has_batteries # current batteries should always have correct location, so don't need to check.
                else:
                    outcome = item_interactions.find_local_item_by_name(noun2.has_batteries, verb="look", current_loc=loc.current)
                    if outcome and (outcome.name == battery or outcome.name in battery or battery in outcome.name):# and outcome.name == device_uses_battery:
                        battery = outcome
                        device = noun2
                    else:
                        print(f"No match found. Need to figure out what's wrong. noun: {noun} / battery: {battery} / noun2: {noun2} / device: {device}")
                        return None, None, None
                if isinstance(device, itemInstance) and isinstance(battery, itemInstance):
                    print(f"You take the {assign_colour(battery)} from the {assign_colour(device)}.")
                    device.has_batteries = None
                    battery.in_use = False
                    return "success", battery, device

        else:
            if verb == "take":
                return "none to take", noun, noun2

            if verb == "put":
                if noun2.takes_batteries == battery and noun.name == battery:
                    if not hasattr(noun, "in_use") or (hasattr(noun, "in_use") and not noun.in_use):
                        battery = noun
                        device = noun2

                elif battery in noun2.takes_batteries:
                    outcome = item_interactions.find_local_item_by_name(noun2.takes_batteries, verb="look", current_loc=loc.current)
                    if outcome and outcome.name == battery:# and outcome.name == device_uses_battery:
                        device = noun2
                        battery = outcome

                if isinstance(device, itemInstance) and isinstance(battery, itemInstance):
                    print(f"You fit the {assign_colour(battery)} into a compartment in the {assign_colour(device)} and click it into place.")
                    device.has_batteries = battery
                    battery.in_use = device
                    return "success", battery, device
    else:
        return None, None, None

def take(format_tuple, input_dict):
    from eventRegistry import events
    logging_fn()
    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict=input_dict, verb="take", access_str2="all_local", hold_error_messages=True)
    #print("noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason: ", noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason)
    if not isinstance(noun, itemInstance):
        print("Does it ever get here? I'd have thought it would print the failure message in parser before now.")
        if noun == None:
            if noun_reason == 9 and hasattr(get_noun(input_dict), "in_use"):
                noun = get_noun(input_dict)
                noun_reason = 0
                print(f"noun_reason: {noun_reason}")
            else:
                logging_fn(f"Going to print error from def take `{input_dict}`")
                print("error printing in def take at start because no noun inst")
                print_failure_message(noun=noun_str,noun2=(noun2 if noun2 else (noun2_str if noun2_str and not noun2_str == "assumed_noun" else None)), verb="take")
                return
    #get_nouns(input_dict)

    added_to_inv = False
    #print(f"[OUTCOME from def take: `{outcome}`]")

    def can_take(noun, reason_val):
        logging_fn()
        added_to_inv = False

        if noun:
            if noun_reason not in (0, 3, 4, 5, 8):
                theres_therere = is_plural_noun(noun, plural = "There're", singular="There's")
                print(f"{theres_therere} no {assign_colour(noun_str, colour="yellow")} around here to take.")
                return 1, None
            #print(f"Reason code: {reason_val}")
        if reason_val == 5:
            print(f"The {assign_colour(noun)} {is_plural_noun(noun)} already in your inventory.")
            return 1, None # return none so it doesn't run the pick up check again

        else:
            if hasattr(noun, "can_pick_up") and noun.can_pick_up:
                if hasattr(noun, "contained_in"):
                    container = noun.contained_in
                if reason_val in (3, 4) and container and (container.location == loc.current or container.location == loc.inv_place):
                    outcome = registry.move_from_container_to_inv(noun, parent=container)
                    added_to_inv = outcome
                    #print("added to inv, returning.")
                    return 0, added_to_inv
                elif reason_val == 0:
                    outcome = registry.move_item(noun, location = loc.inv_place)
                    #print(f"OUTCOME: {outcome} / noun: {noun}")
                    if outcome in loc.inv_place.items:
                        #print("Outcome is in inventory. (line 1480)")
                        return 0, outcome
                    if noun in loc.inv_place.items:
                        print("noun_inst is in inventory. line 1483")
                        added_to_inv = noun
                        return 0, added_to_inv
                print(f"{noun} failed to be processed, not reasonval 3, 4, 5. reason_val: {reason_val}")
            else:
                print(f"You can't pick up the {assign_colour(noun)}.")
                return 1, added_to_inv
        print("Failed in can_take, returning defaults.")
        return 0, noun

    #a_or_the = is_plural_noun(noun, plural = "any", singular="a")
    verb = get_verb(input_dict)
    dir_or_sem = get_dir_or_sem(input_dict)
    location = get_location(input_dict)

    theres_therere = is_plural_noun(noun, plural = "There're", singular="There's")
    doesnt_dont = is_plural_noun(noun, plural = "doesn't", singular="don't")
    isnt_arent = is_plural_noun(noun, plural = "isn't", singular="aren't")

    if format_tuple in (("verb", "noun"), ("verb", "direction", "noun")):

        cannot_take, added_to_inv = can_take(noun, noun_reason)
        if cannot_take and hasattr(noun, "can_consume"):
            print(f"\nDid you mean to consume the {assign_colour(noun)}? ")
            return

    elif dir_or_sem in ("in", "at", "from") and location:
        if location == loc.current or location == loc.current.place:
            cannot_take, added_to_inv = can_take(noun, noun_reason)

    elif format_tuple == (("verb", "noun", "direction", "noun")): ## will later include scenery. Don't know how that's going to work yet.
        verb_str = input_dict[0]["verb"]["str_name"]
        if verb_str in ("take", "remove", "separate", "get"):

            if noun2 and noun2_reason not in interactable_codes:
                print(f"{theres_therere} no {assign_colour(noun2_str, colour="yellow")} around here to {verb_str} from.")
                return
            if dir_or_sem not in ("and", "from", "out"): # `out` ie 'take x out of y'.
                print(f"dir_inst is {dir_or_sem}; was expecting 'from' or 'and'. May need to adjust take function.")
            if noun2_reason == 10 and noun_reason in interactable_codes: # <-- Should be checking it's the right one before this point. Though I guess I do get all the nouns from the proper check now, so it's likely enough.
                print(f"{theres_therere} no {assign_colour(noun2_str, colour="yellow")} to take the {assign_colour(noun)} from.")
                return

            if noun_reason not in can_pickup_codes and not hasattr(noun, "in_use"):
                if noun_reason == 5:
                    print(f"The {assign_colour(noun)} {is_plural_noun(noun)} already in your inventory.")
                    return
                if not has_and_true(noun, "can_pick_up"):
                    print(f"The {assign_colour(noun)} {isnt_arent} something you can pick up.")
                    return

            battery_name, device_takes_batteries = battery_check(verb, noun, noun2)
            if battery_name and device_takes_batteries:
                success, battery, device = act_on_battery_device(verb, noun, noun2)
                if success:
                    if success == "none to take":
                        print(f"The {assign_colour(device)} {doesnt_dont} have any {assign_colour(noun_str, colour="yellow")} to take.")
                        return
                    registry.move_item(battery, location=loc.inv_place)
                    return
            #else:
                #print(f"Not battery_name {battery_name} or not device_takes_batteries: {device_takes_batteries}")

                #if isinstance(battery, str):
                #    else: # shouldn't need to get local by name - the device knows what batteries it has.
                #        outcome = item_interactions.find_local_item_by_name(battery, verb="look", current_loc=loc.current)
                #        if outcome:# and outcome.name == device_uses_battery:
                #            battery = outcome
                #        else:
                #            print(f"Could not find suitable battery for {device}")

            container = noun.contained_in if hasattr(noun, "contained_in") else None
            if container and container != noun2 and container.name == noun2.name:
                _, container_reason, _ = registry.run_check(container)
                if container_reason in interactable_codes:
                    noun2 = container # if the noun is contained in a same-named container that is also accessable, use that container as noun2. If noun had correct container, noun and noun2 are now correct.

# Get child from parent if original child did not find parent -- assume original noun was similar item not in container, assume intent of item that is in a container when you say 'take it from container'.
            if not container: ## works for actual containers, irrelevant to batteries.
                if hasattr(noun2, "children") and noun2.children:
                    for child in noun2.children:
                        if child.name == noun.name:
                            print(f"Set noun to {child}; matching name, is child of {noun2}")
                            noun = child # if the container doesn't match the
                            container = noun2
                            _, noun_reason, _ = registry.run_check(noun)
                            break

            if container and container == noun2 and has_and_true(container, "children") and noun in container.children:
                if noun_reason in in_container_codes and noun2_reason in interactable_codes:
                    output_noun = registry.move_from_container_to_inv(noun, parent=container, no_print=False)
                    if output_noun in loc.inv_place.items:
                        added_to_inv = output_noun
                    else:
                        print(f"Tried to add {assign_colour(noun)} to inventory, but something must have gone wrong.")
                        traceback_fn()
                else:
                    print(f"Noun reason: {noun_reason} / noun2_reason: {noun2_reason}")

            else:
                print(f"The {assign_colour(noun)} {doesnt_dont} seem to be in the {assign_colour(noun2.name, colour="yellow")}.")

    else:
        print(f"Cannot process {input_dict} in def take() End of function, unresolved.")
        return

    if added_to_inv:
        if isinstance(added_to_inv, itemInstance):
            if added_to_inv != noun:
                noun = added_to_inv

        outcome, _ = events.is_event_trigger(noun_inst = noun, reason = "item_in_inv")
        if not outcome: # removed a newline from the next. If it causes issues, add it elsewhere, not here.
            print(f"The {assign_colour(noun)} {is_plural_noun(noun)} now in your inventory.")
        return

def put(format_tuple, input_dict, location=None):
    logging_fn()
    action_word = "You put"
    verb = get_verb(input_dict, get_str=True)
    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="drop", access_str="drop_subject", access_str2="drop_target", hold_error_messages=True) # to get inv items first
    #print(f"[def put] NOUN : {noun}")
    if noun2 and in_types(noun2, "container"):
        if noun2.children and noun in noun2.children:
            #print(f"Trying to drop something already in that container. {noun}")
            noun = None
    if not noun:
        noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="put", access_str=None, access_str2=None, hold_error_messages=True)
        #print(f"New noun: {noun}")
    sem_or_dir = get_dir_or_sem(input_dict)

    if not sem_or_dir and noun2:
        print("No sem_or_dir and noun2. Should I just set a default sem_or_dir? Thinking I basically need to try to conform input once we get to the early noun stage, to reduce if branching where I can. for now let's say 'on'.")
        sem_or_dir = "on"

    if (noun_str and noun2_str) and not (noun and noun2):
        if noun and not noun2 and noun_reason in interactable_codes:
            print(f"You can't see a {assign_colour(noun2_str, colour="yellow")} to put the {assign_colour(noun)} {sem_or_dir}.")
            return
        if noun2 and not noun and noun2_reason in interactable_codes:
            if "container" in noun2.item_type or battery_check(verb="takes_batteries", device = noun2):
                print(f"You don't have a {assign_colour(noun_str, colour='yellow')} to put {sem_or_dir} the {assign_colour(noun2)}.")
            else:
                print(f"You don't have a {assign_colour(noun_str, colour='yellow')}, and the {assign_colour(noun2)} couldn't hold it anyway.")
            return

    if noun and noun2:
        #print(f"noun and noun2: {noun}, {noun2}")
        if noun == noun2: # moved to the top so we don't bother testing the rest if true.
            print(f"You cannot put the {assign_colour(noun)} in itself.")
            return
        success, battery, device = act_on_battery_device("put", noun, noun2)
        if success:
            if success == "has_batteries_already":
                return
            registry.move_item(battery, location=loc.no_place, no_print=True)
            if hasattr(device, "has_batteries") and device.has_batteries == battery:
                #print(f"Device has batteries: {device} // {device.has_batteries}")
                registry.init_descriptions(device)
                moved = battery

        elif not hasattr(noun, "can_pick_up") or not noun.can_pick_up or noun_reason not in interactable_codes:
            print(f"You can't move the {assign_colour(noun)}.")
            return

        if hasattr(noun2, "is_scenery") or "flooring" in noun2.item_type and (not sem_or_dir or sem_or_dir in ("on", "onto")):
            if "flooring" in noun2.item_type:
                if noun.location != noun2.location:
                    if not noun.location == loc.inv_place:
                        noun = item_interactions.find_local_item_by_name(noun, verb="drop", current_loc=loc.current)
                    if noun:
                        moved = registry.move_item(noun, loc.current)
                        if not moved_item(moved):
                            text = smart_capitalise(f"{action_word} the {assign_colour(noun)} {get_dir_or_sem(input_dict)} the {noun2.name}.\n")
                            print(f"NOUN2: {noun2} / dir(noun2): {dir(noun2)}")
                            print(text)
                        return
                else:
                    print(f"The {assign_colour(noun)} is already {sem_or_dir} the {noun2.name}.\n")
                    return

        elif noun2_reason not in interactable_codes:
            print(f"You can't access the {assign_colour(noun2)} to put the {assign_colour(noun)} {sem_or_dir} it.")
            return

        elif hasattr(noun2, "contained_in") and noun == noun2.contained_in:
            print(f"Cannot put {assign_colour(noun)} in {assign_colour(noun2)}, as {assign_colour(noun2)} is already inside {assign_colour(noun)}. You'll need to remove it first.")
            return


        elif sem_or_dir in ("in", "to", "into", "inside") and len(format_tuple) == 4 or (len(format_tuple) == 6 and get_location(input_dict) == loc.current.place):

            if "container" in noun2.item_type:
                #print(f"The {assign_colour(noun)} is already in the {assign_colour(noun2)}")#print(f"Cannot put {assign_colour(noun)} in {assign_colour(noun2)}, as {assign_colour(noun)} is already inside {assign_colour(noun2)}. You'll need to remove it first.")
                if hasattr(noun, "contained_in") and noun2 == noun.contained_in:
                    if noun2 and "container" in noun2.item_type:
                        done=False
                        inv_items = registry.get_item_by_location(loc.inv_place)
                        if inv_items:
                            for item in inv_items:
                                if item.name == noun.name and item != noun:
                                    print(f"Item in loc.inv_place to use instead of noun: {item}")
                                    done=item
                                    break
                        if not done:
                            inv_items = registry.get_item_by_location(loc.current)
                            if inv_items:
                                for item in inv_items:
                                    if item.name == noun.name and item != noun:
                                        print(f"Item in loc.current to use instead of noun: {item}")
                                        done=item
                                        break
                        if not done:
                            print(f"The {assign_colour(noun)} is already in {assign_colour(noun2)}")
                            return
                        else:
                            noun = item
                direction = get_dir_or_sem(input_dict)
                #moved = registry.move_item(noun, new_container=noun2, no_print=True)
                success = move_a_to_b(noun, noun2, verb, direction=(direction if direction else "into"))
                #registry.move_item(noun, new_container=noun2, no_print=True)
                if success and isinstance(success, str): #hasattr(noun2, "is_open") and not noun2.is_open:
                    print(success)
                    return
                if noun in loc.inv_place.items or noun in registry.by_location[loc.inv_place]:
                    print(f"Outcome from move_a_to_b: {success} noun: {noun} / container: {noun2}")
                    exit(f"{assign_colour(noun)} still in inventory, something went wrong. Exiting.")
                #else:
                if not success:
                    text = smart_capitalise(f"{action_word} the {assign_colour(noun)} {sem_or_dir} the {assign_colour(noun2)}.")
                    print(text)
                return

    else:
        if sem_or_dir in down_words:
            print("if sem_or_dir in down_words: USING MOVE_A_TO_B")
            return move_a_to_b(a=noun, b=location, action=action_word, direction = sem_or_dir, current_loc=location)
            #moved = noun #return

        if len(format_tuple) == 5:
            a, sem_or_dir, b, sem_or_dir_2, c = five_parts_a_x_b_in_c(input_dict)
            if c == location:
                move_a_to_b(a=a, b=b, action=action_word, direction=sem_or_dir, current_loc=location)
                moved = a#return

    if moved:
        moved_item(moved)

    else:

        print(f"Noun: {noun} / noun2: {noun2}")
        print_failure_message(init_dict=input_dict, noun=noun, noun2=noun2, verb="put")
        #print(f"You can't put the {assign_colour(noun)} on the {assign_colour(noun2)}; I just haven't programmed it yet.")

def throw(format_tuple, input_dict):
    logging_fn()

    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use")

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
        move_a_to_b(noun, loc.current, "You throw the", ", leaving it at the")
        return

    if dir_or_sem in to_words and noun2:
        if hasattr(noun2, "is_scenery"):
            noun2_text = noun2.name
        else:
            noun2_text = f"{assign_colour(noun2)}"

        text = f"You throw the {assign_colour(noun)} at the {noun2_text}"
        if hasattr(noun2, "smash_defence") and hasattr(noun, "smash_attack"):
            if noun2.smash_defence < noun.smash_attack:
                if hasattr(noun2, "is_scenery"):
                    action = "cracks"
                else:
                    action = "breaks"
                print(f"{text}; the {noun2_text} {action} as the {assign_colour(noun)} hits it.") # TODO: custom breaking messages for obviously breakable things with [[]] or smth for the breaker obj name.
                if action != "cracks": # so we can't break floors. I might do it later but for that's just not an option.
                    set_noun_attr(("is_broken", True), noun=noun2, event_type = "state_change")
                return
            elif noun2.smash_defence >= noun.smash_attack:
                print(f"{text}; the {assign_colour(noun)} hits the {noun2_text}, but doesn't seem to damage it.")
                return
        if noun2.location != noun.location:
            print(f"{text}, and now there it sits.")
            registry.move_item(noun, location=noun2.location)
        return

    print(f"Cannot process {input_dict} in def throw() End of function, unresolved. (Function not yet written)")


def push(format_tuple, input_dict):
    logging_fn()

    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use")

    if "door_window" in noun.item_type:
        if hasattr(noun, "can_be_opened"):
            if noun.is_open:
                print(f"You push against the {assign_colour(noun)}, but it doesn't move much further.")
                return
            else:
                if hasattr(noun, "is_locked") and noun.is_locked:
                    print(f"You push against the {noun}, but it doesn't budge.")
                    return
                else:
                    print(f"You push against the {assign_colour(noun)}, and it opens just enough for you to slip inside.\n")
                    if noun.location == loc.current and hasattr(noun, "ext_location") and noun.ext_location == loc.current:
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

    noun, noun_str, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, access_str="drop_subject", access_str2="local_and_inv_containers_only")
    location = get_location(input_dict)
    if not noun and noun_str: # assume error printed in get_correct_nouns
        return
    print(f"Noun: {noun}")
    #noun, noun_str, noun2, _ = get_nouns(input_dict)
    #noun = verb_requires_noun(input_dict, "drop", local=True)
    if isinstance(noun, str):
        print("Noun is not an instance obj.")
        if noun == "assumed_noun":
            noun = noun_str
    if not noun and not noun_str:
        print("What do you want to drop?")
        return

    if not noun:
        print_failure_message(noun=noun_str, verb="drop", init_dict=input_dict)
        return

    if len(input_dict) == 3:
        direction = get_dir_or_sem(input_dict)
        if noun and direction and (direction == "here" or direction in down_words):
            input_dict.pop(2, None)

    if len(input_dict) == 2:
        print(f"reason val: {noun_reason}, for item: {noun}")
        if noun_reason == 6:
            loc_named = registry.get_item_by_location(loc.inv_place)
            loc_named = list((i for i in loc_named if i.name == noun.name) if loc_named else None)
            if loc_named:
                noun = loc_named[0]
                test = move_a_to_b(noun, loc.current, "drop")
                if test:
                    print(f"TEST: {test}")
        if noun_reason == 5:
        #container, reason_val, meaning = registry.run_check(noun)
        #if reason_val == 5:
            return move_a_to_b(noun, loc.current, "drop")
            #registry.move_item(noun, location = loc.current)
            #registry.drop(noun)
        elif noun_reason == 3:
            print(f"You can't drop the {assign_colour(noun)}; you'd need to get it out of the {assign_colour(noun.contained_in)} first.")
            return

        else:
            print(f"You can't drop the {assign_colour(noun)}; you aren't holding it.")
            return

    elif len(input_dict) == 4:
        dir_or_sem = get_dir_or_sem(input_dict)
        #item_to_place, direction, container_or_location = three_parts_a_x_b(input_dict)
        #print(f"item_to_place: {item_to_place}, direction: {direction}, dir type: {type(direction)}")
        if noun_reason in can_drop_codes and dir_or_sem in ["in", "into", "on", "onto", "at"]:
            print(f"Noun_reason: {noun_reason}")
            if noun2 and "container" in noun2.item_type and noun2_reason == 0:
                registry.move_item(noun, new_container=noun2)
            elif noun2 and hasattr(noun2, "is_scenery") and "flooring" in noun2.item_type:
                registry.move_item(noun, location=loc.current)

            elif location:
                print(f"Location: {location}")
                if location == loc.current.place:
                    registry.move_item(noun, location = loc.current)

                else:
                    print(f"You can't drop the {assign_colour(noun)} at {assign_colour(get_location(input_dict))} because you aren't there.")
                    return

            elif noun2 and hasattr(noun2, "int_location") and noun2.int_location == loc.current:
                registry.move_item(noun, location = loc.current) # for 'drop x in shed' in case it finds 'shed door'.

            else:
                print(f"Couldn't move {noun.name} because {noun_reason}")
        else:
            print(f"Cannot process {input_dict} in def drop(); 4 long but direction str is not suitable.")
            return

    if noun not in loc.inv_place.items:
        triggered = None
        if hasattr(noun, "event") and noun.event:
            from eventRegistry import events
            triggered, moved_children = events.is_event_trigger(noun_inst = noun, reason = "item_not_in_inv")
            if moved_children:
                print_moved_children(moved_children, noun, triggered)
            #print(f"Triggered: {triggered}")
        if not triggered:
            if loc.current.surfaces.get("flooring"):
                flooring = loc.current.surfaces['flooring'].name
            else:
                flooring = "ground"
            print(f"Dropped the {assign_colour(noun)} onto the {flooring} here at the {assign_colour(loc.current, card_type='ern_name')}.")
        return

    print(f"Cannot process {input_dict} in def drop() End of function, unresolved.")


def set_action(format_tuple, input_dict):
    logging_fn()
    verb = get_verb(input_dict)
    if verb.name == "set":
        #noun = verb_requires_noun(input_dict, "set", local=True)
        noun, nounstr, noun_reason, noun2, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="look")
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

def check_item_charger_match(actor_noun:itemInstance, target_noun:itemInstance=None) -> tuple[itemInstance|None, itemInstance|None, str|None]:
    """
    Checks whether a phone and charger object exist. Returns (`phone`, `object`, `outcome`), with `outcome` coming from this table:
    0 = phone and charger, neither in use.
    1 = phone and charger, being used together.
    2 = phone and charger, charger being used with something else
    3 = phone and charger, phone being charged with something else.
    4 = phone but no charger
    5 = charger but no phone
    6 = no charger and no phone
    """
    logging_fn()

    if "charger" in actor_noun.item_type:
        charger = actor_noun
    elif target_noun and "charger" in target_noun.item_type:
        charger = target_noun
    else:
        charger = None

    if target_noun and hasattr(target_noun, "can_be_charged") and target_noun != charger:
        phone = target_noun
    elif hasattr(actor_noun, "can_be_charged") and actor_noun != charger:
        phone = actor_noun
    else:
        phone = None # Note: May not always be a phone, but it's clear enough for now as to the intent and we shold use inst name for printing anyway.

    if not charger:
        if not phone:
            return None, None, 6
        return None, phone, 4
    if not phone:
        return charger, None, 5

    if charger.in_use:
        if charger.in_use == phone:
            return charger, phone, 1
        return charger, phone, 2

    if phone.is_charging:
        return charger, phone, 3

    return phone, charger, 0

def charge_electronics(format_tuple, actor_noun:itemInstance, target_noun:itemInstance):
    logging_fn()

    phone, charger, usage = check_item_charger_match(actor_noun, target_noun)

    if not charger:
        print(f"No charger amongst {actor_noun} or {target_noun}. Are you sure that's a charger?")
        return
    if not phone:
        print(f"No phone amongst {actor_noun} or {target_noun}. Are you sure that's a rechargeable item?")
        return

    if not phone.can_be_charged:
        print(f"You can't charge the {assign_colour(phone)}.")
        return
    if phone.is_charged:
        print(f"The {assign_colour(phone)} is already charged.")
        return

    if usage in (1, 2, 3):
        if usage == 1:
            print(f"The {assign_colour(charger)} is already charging the {assign_colour(phone)}")
        elif usage == 2:
            print(f"The {assign_colour(charger)} is already being used.")
        else:
            print(f"The {assign_colour(phone)} is already being charged.")
        return

    if charger.requires_powersource:
        if loc.current.place.electricity:
            print(f"You plug in the {assign_colour(charger)} and connect the phone. Now to wait a little while for it to charge.")
            if not phone.location == loc.current:
                registry.move_item(phone, location = loc.current)
            set_noun_attr(("is_charging", True), noun=phone, event_type = "electronics")
            setattr(charger, "in_use", phone)
            return
        else:
            print("There's nowhere here to plug the charger in; you need somewhere with power.")
            return
    #print(f"Charger: {charger} // phone: {phone} // phone.is_charged: {phone.is_charged} // charger.requires_powersource: {charger.requires_powersource}")

def use_item_w_item(format_tuple, input_dict):
    logging_fn()
    #print(f"Format list: {format_tuple}")
    #print(f"Length format list: {len(format_tuple)}")
    ## use x on y
    actor_noun, noun_str, actor_reason, target_noun, noun2_str, noun2_reason = get_correct_nouns(input_dict, verb="use", access_str=None, access_str2=None)

    dir_or_sem = get_dir_or_sem(input_dict)

    verb = get_verb(input_dict)
    verb_str = get_verb(input_dict, get_str=True)

    if not target_noun:
        #print(f"No second noun: {format_tuple} should not be in use_item_w_item function. Check routing.")
        return

    if format_tuple == (('verb', 'noun', 'direction', 'noun')) or format_tuple == (('verb', 'noun', 'semantic', 'noun')):
        if verb.name in ("use", "unlock", "lock", "open", "charge") and dir_or_sem and dir_or_sem in  ("on", "using", "with"):
            #print(f"use_item_w_item: verb name: `{verb.name}`, dir_or_sem is `{dir_or_sem}`, actor_noun: {actor_noun}, target_noun: {target_noun}")
            for noun in (actor_noun, target_noun):
                if verb_str == "charge" and has_and_true(noun, "can_be_charged") or "charger" in noun.item_type:
                    return charge_electronics(format_tuple, actor_noun, target_noun)
                if "key" in noun.item_type or hasattr(noun, "requires_key"):
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

    noun, _, reason_val, _, _, _ = get_correct_nouns(input_dict, verb="use")

    if "map" in noun.name: # do we want to have to keep the map on us? Yes, right? Should be droppable?
        if reason_val in interactable_codes:
            item_interactions.show_map(noun)
        else:
            print(f"You can't see the {assign_colour(noun)} right now.")
        return

    print(f"Cannot process {input_dict} in def use_item() End of function, unresolved. (Function not yet written)")

def wait(format_tuple, input_dict):

    timeblock, num = get_timeblocks(input_dict, verb="wait")

    sem = get_dir_or_sem(input_dict)
    sem2 = get_dir_or_sem(input_dict, 2)
    if sem2 == "until":
        import choices
        if sem2 in choices.time_of_day:
            num = get_hours_until(sem2)
            sem = sem2 = "hours"

    if not get_noun(input_dict):
        from interactions.player_movement import update_loc_data
        from set_up_game import game
        beforetime = game.time
        export = update_loc_data(loc.current, loc.current, timeblocks = timeblock)
        aftertime = game.time
        if export:
            if num:
                if sem == "days" or sem2 == "days":
                    text = f"{num} {aftertime}s later"
                else:
                    text = f"{num} hours later; {aftertime}"

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
    location_str = get_location(input_dict, get_str=True) # adding this to cope with 'shed door/shed' messes from the parser. Should fix it earlier but too afraid of breaking everything else.
    if location_str and not location:
        from verb_membrane import membrane
        for loc_name in membrane.compound_locations:
            if location_str in membrane.compound_locations[loc_name]:
                location = loc.by_name.get(loc_name)

    if not noun:
        if format_tuple == ("verb", "noun", "noun"):
            noun = get_noun(input_dict, 2)
        else:
            noun = get_noun(input_dict)

    if noun:
        if in_types(noun, "transition"):
            return move_through_trans_obj(noun, input_dict)

        if in_types(noun, "loc_exterior"):
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

def talk(format_tuple, input_dict):
    noun, noun_str, reason, _, _, _ = get_correct_nouns(input_dict)
    from npcRegistry import npcInstance
    if noun:
        if isinstance(noun, itemInstance):
            print(f"The {assign_colour(noun)} doesn't seem like it'll talk back.")
        elif isinstance(noun, npcInstance):
            import interactions.conversations
            interactions.conversations.start_conversation(noun)
            look_around()
            return
        else:
            print_failure_message(init_dict=input_dict)

MOVE_UP = "\033[A"
print_extra_decorations = True

def make_foreline(new_str, input_str, add_space=False):
    diff = len(new_str) - len(input_str)
    new_str = f"\033[0;32m[\033[1;32m<  {input_str}  >\033[0;32m]"
    half = int(diff/2)
    leftovers = diff - (half + half) - 1 -2
    foreline = f"\033[0;32m" + " .-" + (f" " * (half-3)) + (" " * (len(input_str))) + (f" " * (half + leftovers)) + "-."
    #print(MOVE_UP, end='')
    if add_space:
        print(MOVE_UP, end='')
        #foreline = " " + foreline
        print(foreline)
         # Needs this little dance to print correctly whether it's user input or test. If I wasn't running the text commands I could just hardcode it directly at input.
    else:
        print(MOVE_UP, end='')
        print(foreline) # Needs this little dance to print correctly whether it's user input or test. If I wasn't running the text commands I could just hardcode it directly at input.
    print()
    foreline = foreline.replace(".", "'")
    return foreline, new_str#f"\033[0;32m" + " '-" + (f" " * (half-2)) + (" " * (len(input_str))) + (f" " * (half + leftovers-1)) + "-'", new_str

def router(viable_format, inst_dict, input_str=None):
    logging_fn()

    verb_inst = verb_str = None
    quick_list = []
    input_strings = []
    for v in inst_dict.values():
        for data in v.values():
            quick_list.append(data["str_name"])
            input_strings.append(data["text"])

    from config import print_input_str # This will probably be the default. Definitely don't need three options.
    if print_input_str:
        print(f"{MOVE_UP}", len(input_str) * " ")# + "\n")
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
                verb_str = entry["str_name"] ## Fpr error messages where the verb found no instance, ie the format was not found so no instance arrived at. eg 'read south'.
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
        "open": simple_open_close,
        "close": simple_open_close,

        "talk": talk,
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
            if verb_inst == None and verb_str:
                if len(viable_format) in (1, 2) and list(inst_dict[1].keys())[0] in ("location", "cardinal"):
                    print(f"Sorry, you can't {assign_colour("read", colour='green')} a place.")
                else:
                    print(f"Sorry, you can't {verb_str} that.")
                return
            func = function_dict[verb_inst.name]

        if func != function_dict["go"] and get_location(inst_dict):
            mentioned_loc = get_location(inst_dict)
            if not registry.by_name.get(mentioned_loc.name): # currently only loc_exterior nouns share names with locations, so we skip those here.
                if mentioned_loc != loc.current and mentioned_loc != loc.current.place and mentioned_loc != loc.inv_place.place:
                    if func.__name__ not in can_be_not_local:
                        print(f"You want to {verb_inst.name} at the {assign_colour(mentioned_loc)} but you aren't there...")
                        return
        response = func(format_tuple = viable_format, input_dict = inst_dict)
        return response
    except Exception as e:
        print(f"Failed to find the correct function to use for {verb_inst}: {e}")
