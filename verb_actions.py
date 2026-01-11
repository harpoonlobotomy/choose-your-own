
### Interface between item_actions and the verbs.

import time
from choose_a_path_tui_vers import item_interaction
from env_data import cardinalInstance, locRegistry as loc
from interactions import item_interactions
from interactions.player_movement import new_relocate, turn_around
from itemRegistry import ItemInstance, registry
from misc_utilities import generate_clean_inventory
from set_up_game import game
from verb_definitions import directions, formats

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
to_words = ["to", "towards", "at"] ## these two (< + ^) are v similar but have some exclusive uses, so keeping them separately makes sense here.
down_words = ["down"]


#### Fundamental Operations ####

def get_current_loc():

    from env_data import locRegistry
    location = locRegistry.current
    cardinal = locRegistry.current_cardinal
    return location, cardinal

def is_loc_current_loc(location=None, cardinal=None):

    current_location, current_cardinal = get_current_loc()
    if location and location == current_location:
        return 1, current_location, current_cardinal
    if not location and cardinal: ## so it can check if the facing direction is current without needing location.
        if cardinal == current_cardinal:
            return 1, current_location, current_cardinal
    return 0, current_location, current_cardinal # 0 if not matching. Always returns current.

def move_a_to_b(a, b, action=None, direction=None, current_loc = None):

    from item_definitions import container_limit_sizes
   ## This is the terminus of any 'move a to b' type action. a must be an item instance, b may be an item instance (container-type) or a location.
    if not direction:
        direction = "to"
    if not action:
        action = "moving"

    if isinstance(a, ItemInstance):
        if not isinstance(b, ItemInstance):
            print("B is not an instance. move a to b requires two things: What is the second item? (pass for now.)")
            return None

    if isinstance(b, ItemInstance):
        if hasattr(b, "container_limits"):
            print(f"{b.name} is a container with capacity {b.container_limits}.")
            container_size = container_limit_sizes.get(b.container_limits)
            if isinstance(a, ItemInstance):
                if hasattr(a, "item_size"):
                    print(f"{b.name} is an item with size {a.item_size}.")
                    item_size = container_limit_sizes.get(a.item_size)
                    if item_size < container_size:
                        print(f"{a.name} will fit in {b.name}")
                        print(f"{action} {a} {direction} {b}")

    elif isinstance(b, tuple):
        print(f"b is a tuple: {b}")
        if not current_loc:
            current_loc, _ = get_current_loc() ## this may pick up cardinals accidentally. Changing to break the tuple. Might break things.
        if b[0] in current_loc:
            print(f"{action} {a.name} {direction} {b}")

        else:
            print("Can only move items to the location you're currently in.")
        #if b[0] in locations:
        #    print(f"B[0]: {b[0]}")
        #    print(f"{action} {a.name} {direction} {b}")


    else:
        location = None
        print("B is not an instance.")
        if not current_loc:
            current_loc, current_card = get_current_loc()

        if b in current_loc:
            print(f"B is the current location: {b}")
            location = b
        elif "a " + b in current_loc:
            print(f"B is the current location: {b}")
            location = "a " + b

        if location:
            print(f"{action} {a.name} {direction} {b}")
        else:
            print(f"Failed to move `{a}` to `{b}`.")
            print(f"Reason: `{b}` is not the current location.")

def check_lock_open_state(noun_inst, check_open = True, check_locked=True):

    is_open = is_locked = False
    print("Check the item registry for status.")

    return is_open, is_locked

def get_entries_from_dict(input_dict):

    direction_entry = None
    cardinal_entry = None
    location_entry = None
    semantic_entry = None

    #get the values from the dict for location+cardinal right at the start.

    for idx in input_dict.values():
        for kind, entry in idx.items():
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

    return direction_entry, cardinal_entry, location_entry, semantic_entry

"""
okay so something like this:

    if len(format_tuple) == 2:
        if format_tuple == tuple(("verb", "location")):
to disperse parts around within functions. So if '

Maybe it returns an int, and that int is what drives the per-function expansion. I think that works. Avoid counting lengths over and over etc. Going to import the formats dict values from verb_definitions and use that.

"""
def check_against_formats(format_tuple):

    #all_formats_list = [i for i in formats.values()]
    #print(f"formats list: {all_formats_list}")
        ### LOCATION ONLY ###
    for format in ["verb_only", "verb_loc", "verb_dir", "verb_dir_loc"]:
        pass



#################################


##### Parts Parsing ########

def two_parts_a_b(input_dict):
    return list(input_dict[1].values())[0]

    #                                 0      1      2    3
def three_parts_a_x_b(input_dict): # put paperclip in glass jar

    #if list(input_dict[2].values())[0] in directions:
        a = list(input_dict[1].values())[0]
        sem_or_dir = list(input_dict[2].values())[0]
        b = list(input_dict[3].values())[0]

        return a, sem_or_dir, b

                                  #       0          1        2   3        4        5
def five_parts_a_x_b_in_c(input_dict): # `drop the paperclip in glass jar in the graveyard`

    if list(input_dict[2].values())[0] in directions:
        a = list(input_dict[1].values())[0]
        sem_or_dir = list(input_dict[2].values())[0]
        b = list(input_dict[3].values())[0]
        sem_or_dir_2 = list(input_dict[4].values())[0]
        c = list(input_dict[5].values())[0]

        return a, sem_or_dir, b, sem_or_dir_2, c

def get_elements(input_dict) -> tuple:
    ## This is only useful if there's some other check going on. Otherwise it should just be per item, I think.
### I don't think this is actually better than each one just doing 'if len(), because it still has to evaluate the number afterwards to unpack it, no?

    if len(input_dict) == 2:
        return 2, list(input_dict[1].values()) # could be 'leave loc', 'drop item', 'get item', 'talk person' etc.

    elif len(input_dict) == 3:
        return 3, three_parts_a_x_b(input_dict)

    elif len(input_dict) == 4:
        return 4, three_parts_a_x_b(input_dict)


def inst_from_idx(dict_entry, kind_str, return_str=False):
    if return_str:
        return dict_entry[kind_str]["str_name"]

    return dict_entry[kind_str]["instance"]

##############################
#from interactions.player_movement import new_relocate
            #new_relocate(details)
# little bits, the finer end points that things resolve to.

def turn_cardinal(prospective_cardinal, turning = True):

    if isinstance(prospective_cardinal, dict):
        test = prospective_cardinal.get("cardinal")
        if test:
            prospective_cardinal = test.get("instance")
        else:
            test = prospective_cardinal.get("instance")
            if test:
                prospective_cardinal = test

    if isinstance(prospective_cardinal, str):
        prospective_cardinal = loc.by_cardinal(prospective_cardinal)

    #print(f"prospective cardinal going to loc test: {prospective_cardinal}")
    bool_test, _, _ = is_loc_current_loc(None, prospective_cardinal)
    if not bool_test:
        turning_to = prospective_cardinal
        #print(f"turning_to: {turning_to}, type: {type(turning_to)}") ## Shouldn't have this, should be able to use this function for just turning.
        #print(f"You turn to the {turning_to.ern_name}")
        turn_around(turning_to)
        #return "new_cardinal", turning_to
    else:
        #print(f"Prospective cardinal: {prospective_cardinal}")
        #print(f"Prospective cardinal.name: {prospective_cardinal.name}")
        if turning:
            print(f"You're already already facing the {prospective_cardinal.ern_name}.")
        print(prospective_cardinal.long_desc)
        return "no_change", None


#######################
#func(format_tuple, input_dict, location)

#def sample(format_tuple, input_dict):
#    pass
#
def meta(format_tuple, input_dict):
    print("meta function in verb_actions")
    generate_clean_inventory(will_print=True, coloured=True)
    print("Doesn't actually do anything yet, but should be a way to route inventory-type commands when user_input isn't in use.") ## it's hacky, but works, I think.

def go(format_tuple, input_dict): ## move to a location/cardinal/inside

    current_loc, current_card = get_current_loc()

    direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    if (direction_entry and direction_entry["str_name"] in to_words and len(format_tuple) < 5) or (not direction_entry and len(format_tuple) < 4):
        if location_entry and not cardinal_entry:
            new_relocate(new_location=location_entry["instance"])

        elif cardinal_entry and not location_entry:
            turn_cardinal(cardinal_entry["instance"])

        else:
            new_relocate(new_location=location_entry["instance"], new_cardinal = cardinal_entry["instance"])



    elif input_dict[1]["direction"]["str_name"] in in_words:
        print(f"Can {input_dict[1]["direction"]["str_name"]} be entered?")
        print("This isn't done yet.")

    elif format_tuple[1] == "from":
        if location_entry and location_entry["instance"] != current_loc():
            print("Cannot leave a place you are not in.")


def leave(format_tuple, input_dict):
    #verb_only, verb_loc = go
    # verb_noun_dir_noun = movw item to container/surface
    print("LEAVE FUNCTION")
    pass


def look(format_tuple, input_dict):
    print("LOOK FUNCTION")

    direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    if len(format_tuple) == 2:
        if semantic_entry != None and input_dict[1]["sem"]["str_name"] == "around":
            print(loc.current.overview)
            print(f"You're facing {loc.current_cardinal.name}. {loc.current_cardinal.long_desc}")

        elif cardinal_entry != None:
            turn_cardinal(cardinal_entry["instance"], turning = False)

        elif direction_entry != None: # if facing north, turn east, etc.)
            intended_direction = direction_entry["str_name"]
            if intended_direction in ("left", "right"):
                current_facing = loc.current_cardinal.name
                turning_dict = {
                    "north":0,
                    "east":1,
                    "south":2,
                    "west":3
                }

                #left = 1
                #right = -1
                if intended_direction == "left":
                    new_int = int((turning_dict[current_facing] + 1)%4)
                else:
                    new_int = int((turning_dict[current_facing] - 1)%4) ## will this wrap around to go from 0 to 3?

                for k, v in turning_dict.items():
                    if v == new_int:
                        turn_cardinal(k)

        elif format_tuple[1] == "noun":
            item_interactions.look_at_item(inst_from_idx(input_dict[1], "noun"))


    elif len(format_tuple) == 3:
        if format_tuple[2] == "noun" and format_tuple[1] == "direction":
            item_interactions.look_at_item(inst_from_idx(input_dict[2], "noun"))

    else:
        print(f"format list len 2, no idea what's happening: {format_tuple}, input_dict")


def read(format_tuple, input_dict):
    print("read FUNCTION")
    #verb_noun if noun is can_read
    # verb_noun_dir_loc as above, but noun may more likely be scenery
    # and now I realise I haven't accounted for scenery at all. Hm.
    pass

def eat(format_tuple, input_dict):
    print("eat FUNCTION")
    # verb_noun = eat noun if noun == edible, or maybe let them try if it isn't.
    pass

    """
    verb_noun_dir, verb_noun_sem_noun, verb_noun_dir_noun, "verb_noun_dir_dir_noun" #put paperclip down on table

    if <4, obj has to be in inventory (or similarly accessible), dir has to be nearby.
    Else:
        (depends on sem/dir. (Probably will always be dir, but plan for sem anyway))
        If 'in', 'inside', 'into' etc, noun2 has to be a container and size has to be appropriate.
        If 'on', really depends on the specific interaction - can't go by size alone, because you can put a sheet on an earring if you want, yknow?

        Specific things like 'across', 'in front of', etc. Not sure how to manage those yet but wanted to recognise them here.


    """

def clean(format_tuple, input_dict):
    print("clean FUNCTION")
    print(f"format list: {format_tuple}, type: {type(format_tuple)}, length: {len(format_tuple)}")
    if len(format_tuple) == 2:
        if format_tuple == tuple(("verb", "location")):
        #if "verb" in format_tuple and "location" in format_tuple:
            print("You want to clean the ")
    # verb_noun == clean item
    # verb_noun_sem_noun == clean item with item
    # verb_loc == clean location (not sure how useful but worth a custom response at least)
    pass

def burn(format_tuple, input_dict):
    print("burn FUNCTION")
    # for all burn items = require fire source, noun1 must be flammable.
    # verb_noun == burn item
    # verb_noun_sem_noun == noun2 must be flammable
    # verb_noun_dir_loc as 'burn item' but with location needlessly added.
    pass

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

def break_item(format_tuple, input_dict):
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


def un_lock(format_tuple, input_dict):
    print("un_lock FUNCTION")
    ## Use same checks for lock and unlock maybe? Not sure.
    #verb_noun == lock if noun does not require key to lock (padlock etc)
    # verb_noun_sem_noun lock noun w noun2 if noun2 is correct key and in inventory
    pass

def open_close(format_tuple, input_dict):
    print("open_close FUNCTION")
    # like un_lock, maybe use this for open and close both, not sure yet.
    # They have the same checks is the thing. So maybe they just diverge at the end, with open/close sub-functions internally.

    # verb_noun == open noun if noun can be opened, may be obj or door/etc
    # verb_noun_sem_noun open noun w something (open window with stick, open cabinet w prybar)
    pass


def combine(format_tuple, input_dict):
    #if verb_noun_sem_noun, verb_noun_dir_noun, combine a+b
    #if verb_noun == what do you want to combine it with.
    print("COMBINE FUNCTION")
    pass

def separate(format_tuple, input_dict):
    #if verb_noun_sem_noun, verb_noun_dir_noun, combine a+b
    #if verb_noun == what do you want to combine it with.
    print("SEPARATE FUNCTION")
    pass

def combine_and_separate(format_tuple, input_dict):

    print(f"length of format list: {len(format_tuple)}")

def move(format_tuple, input_dict):

    direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)
    if location_entry: # so if it's 'move to graveyard', it just treats it as 'go to'.
        go(format_tuple, input_dict, location_entry["instance"])
        return

    print("move FUNCTION")
    # verb_noun = move item (to where? maybe context.)
    # verb_noun_dir = move item left, move item away
    # verb_noun_dir_noun == move item away from thing ## 'away from' is a combined_phrase, so only one 'dir'.

    pass

def turn(format_tuple, input_dict):

    direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict(input_dict)

    print("TURN FUNCTION")
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
        new_cardinal_str = invert_cardinals[loc.current_cardinal.name]
        new_cardinal = loc.by_cardinal(new_cardinal_str)
        turn_cardinal(new_cardinal)




    #return "new_cardinal", new_cardinal

def take(format_tuple, input_dict):
    print("take FUNCTION")
    if format_tuple in (("verb", "noun"), ("verb", "direction", "noun")):

        noun_idx = format_tuple.index("noun")
        noun_inst = inst_from_idx(input_dict[noun_idx], "noun")
        #print(f"format_tuple[noun_idx]: {format_tuple[noun_idx]}")
        #print(f"input_dict[noun_idx] inst_from_idx: {noun_inst}")

        confirmed_inst = registry.check_item_is_accessible(noun_inst)
        if confirmed_inst:
            print(f"Noun inst {confirmed_inst.name} can be accessed.")
            registry.pick_up(confirmed_inst, inventory_list=game.inventory)
    # verb_noun == pick up noun
    # verb_dir_noun == pick up noun
    # verb_noun_sem_noun pick up noun with noun (eg something hot with a thick glove)
    # verb_noun_dir_noun == take ball from bag
    # verb_noun_dir_noun_dir_loc == take ball from bag at location (if loc == cur_loc)
    pass

def pick_up(format_tuple, input_dict): # should be 'take'

    object_inst = None
    if len(format_tuple) == 2:
        object_inst = two_parts_a_b(input_dict)

        if object_inst:
            print(f"Put {object_inst.name} in your inventory.")


def put(format_tuple, input_dict, location=None):
    print("Put varies depending on the format.")
    print(f"Format list: {format_tuple}")
    action_word = "putting"
    if not location:
        current_loc, current_card = get_current_loc()

    print(f"Input dict: {input_dict}")
    count, parts = get_elements(input_dict)

    noun_count = format_tuple.count("noun")
    print(f"Length of parts: {len(parts)}")
    print(f"Parts: {parts}")
    if noun_count == 2:
        print(f"Noun count: {noun_count}")
        print(f"2 nouns for this put verb: {input_dict}") # `mix the unlabelled cream with the anxiety meds`
        exit()

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

    print("AFTER PARTS")
def put(format_tuple, input_dict):
    print("put FUNCTION")
    # verb_noun_dir == put paper down
    # verb_noun_dir_noun = leave pamplet on table
    # verb_noun_dir_noun_dir_loc == leave pamplet on table at location (again, useless.)
    pass

def throw(format_tuple, input_dict):
    print("throw FUNCTION")
    # verb_noun == where do you want to throw it (unless context),
    # verb_noun_dir == throw ball up (check if 'dir' makes sense)
    # verb_noun_dir_noun  == throw ball at tree
    pass

def push(format_tuple, input_dict):
    print("push FUNCTION")
    # verb_noun == to move things out the way in general
    # verb_noun_dir == #push box left
    # verb_noun_dir_noun == push box away from cabinet
    pass

def drop(format_tuple, input_dict):

    action_word = "dropping"
    print("This is the drop function.")

    if location == None:
        location, current_card = get_current_loc() # don't know if separating the tuple is making life harder for myself here...

    if len(input_dict) == 2:
        print(f"location: {location}")
        move_a_to_b(a=list((input_dict)[1].values())[0], b=location, action=action_word)

    if len(input_dict) == 4:
        item_to_place, direction, container_or_location = three_parts_a_x_b(input_dict)

        if direction in ["in", "into", "on", "onto"]:
            move_a_to_b(a=item_to_place, b=container_or_location, action=action_word, direction=direction)

def drop(format_tuple, input_dict):
    print("drop FUNCTION")
    # verb_noun = move noun to current loc
    # verb_noun_dir_noun = move noun to container/surface,
    # verb_noun_dir_loc == drop item to current loc (if loc == current loc)
    # verb_noun_dir_noun_dir_loc == drop item in container at graveyard (if loc== current loc)
    pass

def set_action(format_tuple, input_dict):
    print("set_action FUNCTION")
    # verb_noun_dir == set item down == drop
    # verb_noun_dir_noun == set item on fire if noun2 == 'fire' == burn
    # verb_dir_noun_sem_noun set on fire with item
    pass



def use_item(format_tuple, input_dict):
    print("use_item FUNCTION")
    print(f"format_tuple = {format_tuple}")
    print("For simple verb-noun dispersal")
    pass


def use_item_w_item(format_tuple, input_dict):
    print("use_item_w_item FUNCTION")
    print(f"Format list: {format_tuple}")
    print(f"Length format list: {len(format_tuple)}")



def router(viable_format, inst_dict):

    verb_inst = None
    #print(f"Viable formats at start of router: {viable_format}.")
    quick_list = []
    for v in inst_dict.values():
        for data in v.values():
            quick_list.append(data["str_name"])

    print(f'\n\033[1;32m[[  {" ".join(quick_list)}  ]]\033[0m\n')

    print(f"Dict for output: {inst_dict}")
    location = None

    for data in inst_dict.values():
        for kind, entry in data.items():
            print(f"kind: {kind}, entry: {entry}")
            #kinds.append(kind)
            if kind == "verb":
                verb_inst = entry["instance"]
            if kind == "meta" and verb_inst == None:
                verb_inst = entry["str_name"]

    function_dict = {
        "meta": meta,
        "go": go,
        "leave": go,

        "look": look,

        "read": read,
        "eat": eat,
        "clean": clean,
        "burn": burn,
        "break": break_item,

        "lock": un_lock,
        "unlock": un_lock,
        "open": open_close,
        "close": open_close,

        "combine": combine,
        "separate": separate,

        "move": move,
        "turn": turn,
        "take": take,#pick_up,
        "put": put,
        "throw": throw,
        "push": push,
        "drop": drop,
        "set": set_action
        #"use_item": use_item,
        #"use_item_w_item": use_item_w_item
    }

    #move_player = ["verb_only", "verb_dir_loc", "verb_loc"]
    #use_item = ["verb_noun_dir", "verb_noun"]
    #use_item_with_item = ["verb_noun_sem_noun", "verb_noun_dir_noun"]
    #move_item_in_space = ["verb_noun_dir"]

    no_noun_actions = [
        "verb_only",
        "verb_loc",
        "verb_dir"
        "verb_dir_loc",
        ]

    single_item_actions = [
        "verb_noun",
        "verb_dir_noun",
        "verb_noun_dir",
        "verb_noun_dir_loc"
        ]

    two_noun_actions = [
        "verb_noun_noun",
        "verb_noun_dir_noun",
        "verb_noun_dir_dir_noun",
        "verb_noun_dir_noun_dir_loc",
        "verb_noun_sem_noun",
        "verb_dir_noun_sem_noun"
        ]

  #  "verb_noun": (verb, noun),
  #  "verb_loc": (verb, location),
  #  "verb_dir_loc": (verb, direction, location), # go to graveyard
  #  "verb_sem_loc": (verb, sem, location), # throw ball up
  #  "verb_noun_noun": (verb, noun, noun), # can't think of any examples.
  #  "verb_dir_noun": (verb, direction, noun), # 'look at watch'
  #  "verb_noun_dir": (verb, noun, direction), # throw ball up
  #  "verb_noun_dir_noun": (verb, noun, direction, noun), # push chest towards door
  #  "verb_noun_dir_dir_noun": (verb, noun, direction, direction, noun), # put paperclip down on table
  #  "verb_noun_dir_noun_dir_loc": (verb, noun, direction, noun, direction, location), # put paperclip in glass jar in graveyard
  #  "verb_noun_dir_loc": (verb, noun, direction, location), # drop paperclip at graveyard #only works if you're in the graveyard, identical in function to 'drop paperclip' while at graveyard.
  #  "verb_noun_sem_noun": (verb, noun, sem, noun),
  #  "verb_dir_noun_sem_noun": (verb, direction, noun, sem, noun)

    move_player = ["go", "leave"]

    use_item_w_item_funcs = ["combine", "separate", "unlock", "lock", "clean"]

    item_actions = ["put", "move", "drop", "burn", "throw", "push", "read", "open", "close", "break", "take", "eat", "look", "set"]

    #if verb_inst.name in use_item_w_item_funcs:
    #    func = function_dict["use_item_w_item"]

    #elif verb_inst.name in move_player:
    #    func = function_dict["go"]

    #elif verb_inst.name in item_actions:
    #    func = function_dict["use_item"]

    #else:
    if isinstance(verb_inst, str):
        func = function_dict["meta"]
    else:
        func = function_dict[verb_inst.name]


    response = func(format_tuple = viable_format, input_dict = inst_dict)

    #print("Leaving router.")

    return response
    #time.sleep(.5)

