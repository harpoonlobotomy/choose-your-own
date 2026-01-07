
### Interface between item_actions and the verbs.

from itemRegistry import ItemInstance, registry
from verb_definitions import directions

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


in_words = ["in", "inside", "into", "within", "to"]
down_words = ["down"]



#### Fundamental Operations ####

def get_current_loc():

    from set_up_game import game
    location = game.place
    cardinal = game.facing_direction
    return location, cardinal

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
            current_loc = get_current_loc()
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
            current_loc = get_current_loc()

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

    print(len(input_dict))
    if len(input_dict) == 2:
        return (2, list(input_dict[1].values())[0]) # could be 'leave loc', 'drop item', 'get item', 'talk person' etc.

    elif len(input_dict) == 3:
        return 3, three_parts_a_x_b(input_dict)

    elif len(input_dict) == 4:
        return 4, three_parts_a_x_b(input_dict)


##############################

#######################
#func(format_list, input_dict, location)

def look(format_list, input_dict, location=None):

    if len(format_list) == 2:
        print(f"You look at the {list(input_dict.keys())[1]}")

def go(format_list, input_dict, location=None):

    if len(format_list) == 3:
        if format_list[1] == "to":
            if location not in get_current_loc():
                destination = location
                print(f"Leaving {get_current_loc} and going to {destination}")
        elif format_list[1] == "from":
            if location not in get_current_loc():
                print("Cannot leave a place you are not in.")

def put(format_list, input_dict, location=None):
    print("Put varies depending on the format.")

    action_word = "putting"
    if not location:
        current_loc = get_current_loc()

    print(f"Input dict: {input_dict}")
    count, parts = get_elements(input_dict)

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



    """
    verb_noun_dir, verb_noun_sem_noun, verb_noun_dir_noun, "verb_noun_dir_dir_noun" #put paperclip down on table

    if <4, obj has to be in inventory (or similarly accessible), dir has to be nearby.
    Else:
        (depends on sem/dir. (Probably will always be dir, but plan for sem anyway))
        If 'in', 'inside', 'into' etc, noun2 has to be a container and size has to be appropriate.
        If 'on', really depends on the specific interaction - can't go by size alone, because you can put a sheet on an earring if you want, yknow?

        Specific things like 'across', 'in front of', etc. Not sure how to manage those yet but wanted to recognise them here.


    """

def drop(format_list, input_dict, location):

    action_word = "dropping"
    print("This is the drop function.")

    if location == None:
        location = get_current_loc()

    if len(input_dict) == 2:
        print(f"location: {location}")
        move_a_to_b(a=list((input_dict)[1].values())[0], b=location, action=action_word)

    if len(input_dict) == 4:
        item_to_place, direction, container_or_location = three_parts_a_x_b(input_dict)

        if direction in ["in", "into", "on", "onto"]:
            move_a_to_b(a=item_to_place, b=container_or_location, action=action_word, direction=direction)


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

def get():
    print()

def open_thing(format_list, input_dict, location=None):

    print("Open thing.")


def burn():

    print()


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


def pick_up(format_list, input_dict, location):

    object_inst = None
    if len(format_list) == 2:
        object_inst = two_parts_a_b(input_dict)

        if object_inst:
            print(f"Put {object_inst.name} in your inventory.")


def use(format_list, input_dict, location):
    print("For simple verb-noun dispersal")


def router(viable_formats, inst_dict):

    #print(f"Dict for output: {inst_dict}")
    location = None

    for data in inst_dict.values():
        for kind, entry in data.items():
            #kinds.append(kind)
            if kind == "verb":
                verb_inst = entry
            if kind == "location":
                current_loc = get_current_loc()
                if entry in current_loc:
                    print(f"Current location is the location listed: {entry}/{current_loc}")
                    location = current_loc
                else:
                    if verb_inst.name != "go":
                        print(f"Current location {current_loc} is not the location listed: {entry}")



    #print(f"kinds: {kinds}")
    if len(viable_formats) > 1:
        print("More than one viable format. Wut?")
    #print("Format: ", viable_formats[0])

    function_dict = {
        "drop": drop,
        "put": put,
        "take": pick_up,
        "go": go,
        "leave": go,
        "look": look,
        "read": look, # will make this 'read' later.
        "open": open_thing,
        "use_item": use
    }

    move_player = ["verb_only", "verb_dir_loc", "verb_loc"]

    use_item = ["verb_noun_dir", "verb_noun"]

    use_item_with_item = ["verb_noun_sem_noun", "verb_noun_dir_noun"]

    move_item_in_space = ["verb_noun_dir"]

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

    if verb_inst.name in use_item_w_item_funcs:
        func = function_dict["put"]

    elif verb_inst.name in move_player:
        func = function_dict["go"]

    elif verb_inst.name in item_actions:
        func = function_dict["use_item"]

    else:
        func = function_dict[verb_inst.name]

    noun_counter = viable_formats[0].count("noun")
    if noun_counter:
        for i, word_type in enumerate(viable_formats[0]):
            #print(f"inst_dict: {inst_dict}")
            if word_type == "noun":
                print(f"NOUN INDEX: {i} [[{inst_dict[i].values()}]]")
            #print(inst_dict[noun_index].values())


    #func(format_list = viable_formats[0], input_dict = inst_dict, location = location)
    #func(format_list, input_dict, location)
#from item_definitions import item_actions
#for item in item_actions:
    #print(f'"{item}": "",')
    #print(verb_name, verb_inst, reformed_dict)



