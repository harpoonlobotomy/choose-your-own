


### So the idea for this is, the verbRegistry identifies parts and figures out what the active verb is. Then it sends the command here, where it's processed according to that parsed data.

## I kinda want to have this in a separate script from the pure 'def move():' type functions.

#Maybe I should move this section into the verbRegistry, and then direct it to this script which just holds the verb actions themselves, not the registry.
# idk I like the idea of the verb-word-objects being different from the verb-action-objects. One's grammatical, one's an action-driver. With the third that is actually a list of functions for specific verbs.

### input_membrane, now.
# Takes the raw input.
# Sends it to verbRegistry.
# Gets the format and the dict back.
# Checks the nouns are viable for the verb.
# Then sends the format and dict onward to verb_actions.

from itemRegistry import initialise_registry, registry

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

null_words = set(("with", "plus", "the", "at"))

from itemRegistry import registry

def get_noun_instances(dict_from_registry):

    def check_noun_actions(noun_inst, verb_inst):

        #print(f"Verb inst name: {verb_inst.name}")
        #print(f"noun inst actions: {noun_inst.verb_actions}")
        for action in noun_inst.verb_actions:
            if flag_actions.get(action):
                if verb_inst.name in flag_actions[action]:
                    #print(f"{action}: Verb inst name in flag_actions for noun: ({noun_inst.name}): {verb_inst.name}")
                    return noun_inst.name

    nouns = set()
    verb = None

    for data in dict_from_registry.values():
        for kind, entry in data.items():
            if kind == "verb":
                verb = entry
                print(f"Verb: `{verb.name}`")

    suitable_nouns = 0

    for idx, data in dict_from_registry.items():
        for kind, entry in data.items():
            #print(f"Kind: {kind}, entry: {entry}")
            if kind == "noun":
                noun_inst = registry.instances_by_name(entry)
                if not noun_inst:
                    suitable_nouns -= 10
                    print(f"No found ItemInstance for {entry}")
                else:
                    noun_name = check_noun_actions(noun_inst[0], verb)
                    if noun_name:
                        dict_from_registry[idx][kind] = noun_inst[0]
                        suitable_nouns += 1
                    else:
                        print(f"You can't {verb.name} the {entry}")
                        suitable_nouns -= 10

    if suitable_nouns >= 1:
        print(f"All nouns ({nouns}) are suitable for this verb ({verb.name}). Sending onward.")

    else:
        print(f"At least one noun from `{nouns} does not match this verb: {verb.name}")
    #print(dict_from_registry)

    return dict_from_registry


def initialise_membrane():

    from item_definitions import item_actions, item_defs_dict
    from verb_definitions import get_verb_defs, directions
    from verbRegistry import initialise_verbRegistry
    from itemRegistry import initialise_registry

    initialise_verbRegistry() ## HAVE to make sure this runs before running the parser.
    initialise_registry()

    membrane = {}

    verb_defs_dict, _ = get_verb_defs()
    nouns_list = list(item_defs_dict.keys())
    membrane["key_verb_names"] = set(verb_defs_dict.keys())
    membrane["item_action_options"] = item_actions


    from env_data import dataset
    membrane["locations"] = list(dataset.keys())
    membrane["directions"] = directions

    membrane_data = nouns_list, membrane["locations"], directions

    return membrane, membrane_data ## 'membrane' for use in this script, 'membrane_data' for verbRegistry.


def run_membrane(input_str):

    from verbRegistry import Parser

    print(f"\nTEST STRING: `{input_str}`")

    viable_formats, dict_from_registry = Parser.input_parser(Parser, input_str, membrane_data)

    inst_dict = get_noun_instances(dict_from_registry)

    from verb_actions import router
    router(viable_formats, inst_dict)


input_str = "drop the paperclip in the graveyard"



membrane, membrane_data = initialise_membrane()

if __name__ == "__main__":

    run_membrane(input_str)
