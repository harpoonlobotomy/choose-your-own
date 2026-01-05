
### Interface between item_actions and the verbs.

from itemRegistry import ItemInstance


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


def put(noun, ):
    print("Put varies depending on the format.")
    """
    verb_noun_dir, verb_noun_sem_noun, verb_noun_dir_noun

    if <4, obj has to be in inventory (or similarly accessible), dir has to be nearby.
    Else:
        (depends on sem/dir. (Probably will always be dir, but plan for sem anyway))
        If 'in', 'inside', 'into' etc, noun2 has to be a container and size has to be appropriate.
        If 'on', really depends on the specific interaction - can't go by size alone, because you can put a sheet on an earring if you want, yknow?

        Specific things like 'across', 'in front of', etc. Not sure how to manage those yet but wanted to recognise them here.


    """



def drop(noun_name):

    print(f"Noun name: {noun_name}")
    print("This is the drop function.")
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

def check_noun_actions(noun_inst, verb_inst):

    print(f"Verb inst name: {verb_inst.name}")
    print(f"noun inst actions: {noun_inst.verb_actions}")
    #if verb_inst.name in noun_inst[0].verb_actions:
    for action in noun_inst.verb_actions:
        if flag_actions.get(action):
            if verb_inst.name in flag_actions[action]:
                print(f"{action}: Verb inst name in flag_actions for noun: ({noun_inst.name}): {verb_inst.name}")
                return noun_inst.name
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



def router(noun_inst=None, verb_inst=None, reformed_dict={}):

    noun_insts = []
    inst_dict = {}

    #if not (noun_inst and verb_inst):
    for idx, v in reformed_dict.items():
        #print("Missing at least one part.")
        #print(f"noun_inst: {noun_inst}, verb inst: {verb_inst}")
        print(f"Index: {idx}, v: {v}")
        for kind, content in reformed_dict[idx].items():
            inst_dict[idx] = content
            print(f"kind: {kind}, content: {content}")
            if kind == "verb" and verb_inst == None:
                from verb_membrane import v_actions
                verb_inst = v_actions.get_action_from_name(content)
            if kind == "noun":
                noun_insts.append(content)
    #else:
    #    print("Not missing any bits.")
    #    print(f"noun: {noun_inst}, verb: {verb_inst}")
    #    noun_insts.append(noun_inst)

    from item_definitions import item_defs_dict
    inventory =list(item_defs_dict.keys())

    if noun_insts:
        for noun in noun_insts:
            print(f"Noun in noun_insts: {noun}")
            from itemRegistry import registry
            if isinstance(noun, str):
                noun_inst = registry.instances_by_name(noun)[0]
            elif isinstance(noun, ItemInstance):
                noun_inst = noun
            #inst_dict[idx] = noun_inst

            #print(f"Noun inst: {noun_inst}, type: {type(noun_inst)}")
            ## can use this (that I forgot I set up previously apparently?)
           #    actions_from_registry = registry.get_actions_for_item(noun_inst, inventory)

            ## And there was a second way but I can't think of it. Too tired.
            ## Oh it was this:
            #print(f"noun inst actions: {noun_inst.verb_actions}") <--
            # slightly different lists, need to remove one of them or it's going to be confusing as hell later, if it isn't already.


    #        print(f"Actions from registry: {actions_from_registry}")
    #        print(f"noun inst: {noun}, verb inst: {verb_inst}")
            noun_name = check_noun_actions(noun_inst, verb_inst)
#
            function_dict = {
                "drop": drop,
                "put": put
            }

            if noun_name:
                func = function_dict[verb_inst.name]

                func(noun_name)
#from item_definitions import item_actions
#for item in item_actions:
    #print(f'"{item}": "",')
    #print(verb_name, verb_inst, reformed_dict)



