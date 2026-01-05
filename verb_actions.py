
### Interface between item_actions and the verbs.

from itemRegistry import ItemInstance, registry

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

##### Parts Parsing ########

def four_parts_a_x_b(input_dict):

    from verb_definitions import directions
    if list(input_dict[2].values())[0] in directions:
        a = list(input_dict[1].values())[0]
        sem_or_dir = list(input_dict[2].values())[0]
        b = list(input_dict[3].values())[0]

        return a, sem_or_dir, b

def get_elements(input_dict) -> tuple:
### I don't think this is actually better than each one just doing 'if len(), because it still has to evaluate the number afterwards to unpack it, no?

    if len(input_dict) == 2:
        return (2, list(input_dict[1].values())[0]) # could be 'leave loc', 'drop item', 'get item', 'talk person' etc.

    elif len(input_dict) == 3:
        print("I can't think of an example right now.")

    elif len(input_dict) == 4:
        return 4, four_parts_a_x_b(input_dict)


##############################


#### Fundamental Operations ####

def get_current_loc():

    from set_up_game import game
    location = game.place
    cardinal = game.facing_direction
    return location, cardinal

def move_a_to_b(a, b, action=None, direction=None):

    from item_definitions import container_limit_sizes
   ## This is the terminus of any 'move a to b' type action. a must be an item instance, b may be an item instance (container-type) or a location.
    if not direction:
        direction = "to"
    if not action:
        action = "moving"

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
        from env_data import dataset as locations
        if b[0] in locations:
            print(f"B[0]: {b[0]}")
            print(f"{action} {a.name} {direction} {b}")


    else:
        location = None
        print("B is not an instance.")
        from env_data import dataset as locations
        if b in list(locations):
            print(f"B is a location: {b}")
            location = b
        elif "a " + b in list(locations):
            print(f"B is a location: {b}")
            location = "a " + b
        if location:
            print(f"{action} {a.name} {direction} {b}")



#######################

def put(input_dict):
    print("Put varies depending on the format.")

    count, parts = get_elements(input_dict)




    """
    verb_noun_dir, verb_noun_sem_noun, verb_noun_dir_noun

    if <4, obj has to be in inventory (or similarly accessible), dir has to be nearby.
    Else:
        (depends on sem/dir. (Probably will always be dir, but plan for sem anyway))
        If 'in', 'inside', 'into' etc, noun2 has to be a container and size has to be appropriate.
        If 'on', really depends on the specific interaction - can't go by size alone, because you can put a sheet on an earring if you want, yknow?

        Specific things like 'across', 'in front of', etc. Not sure how to manage those yet but wanted to recognise them here.


    """


def drop(input_dict):

    #print(f"Noun name: {noun_name}")
    print("This is the drop function.")
    if len(input_dict) == 4:
        item_to_place, direction, container_or_location = four_parts_a_x_b(input_dict)
        if direction in ["in", "into", "on", "onto"]:
            move_a_to_b(a=item_to_place, b=container_or_location, action="dropping", direction=direction)

    if len(input_dict) == 2:
        if isinstance(list((input_dict)[1].values())[0], ItemInstance):
            location = get_current_loc()
            print(f"location: {location}")
            move_a_to_b(a=list((input_dict)[1].values())[0], b=location, action="dropping")

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

def put(noun_name):
    print("This is the noun_name in 'def put():")
    print(f"        **[[{noun_name}]]**")

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



def router(viable_formats, inst_dict):



    print(f"Dict for output: {inst_dict}")

    for data in inst_dict.values():
        for kind, entry in data.items():
            if kind == "verb":
                verb_inst = entry

    function_dict = {
        "drop": drop,
        "put": put
    }

    func = function_dict[verb_inst.name]

    func(inst_dict)
#from item_definitions import item_actions
#for item in item_actions:
    #print(f'"{item}": "",')
    #print(verb_name, verb_inst, reformed_dict)



