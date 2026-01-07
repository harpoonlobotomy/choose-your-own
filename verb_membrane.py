


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

from itemRegistry import registry

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

null_words = set(("a", "plus", "the", "at"))

combine_sems = ["into", "with", "to", "and"]

combine_parts = {("put", "into"), ("add", "to") # thinking about this for more specific matching. Not sure. Idea is 'put x into y' == explicitly y is a container.
}


def get_noun_instances(dict_from_registry):

    def check_noun_actions(noun_inst, verb_inst):

        #print(f"Verb inst name: {verb_inst.name}")
        #print(f"noun inst actions: {noun_inst.verb_actions}")
        for action in noun_inst.verb_actions:
            if flag_actions.get(action):
                if verb_inst.name in flag_actions[action]:
                    #print(f"{action}: Verb inst name in flag_actions for noun: ({noun_inst.name}): {verb_inst.name}")
                    return noun_inst.name

    verb = None
    #print(f"dict_from_registry: {dict_from_registry}")
    for data in dict_from_registry.values():
        for kind, entry in data.items():
            #print(f"kind: {kind}, entry: {entry}")
            if "verb" in kind:
                verb = entry
                #print(f"Verb: {verb}")
                #print(f"Verb type: {type(verb)}")
                #print(f"Verb: `{verb.name}`")

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
                    #print(f"Noun inst: {noun_inst}")
                    noun_name = check_noun_actions(noun_inst[0], verb)
                    if noun_name:
                        dict_from_registry[idx][kind] = noun_inst[0]
                        suitable_nouns += 1
                    else:
                        print(f"You can't {verb.name} the {entry}")
                        suitable_nouns -= 10


    if suitable_nouns >= 1 or verb.name == "look":
        print(f"All nouns ({suitable_nouns}) are suitable for this verb ({verb.name}). Sending onward.")

    else:
        print(f"At least one noun from dict nouns does not match this verb: {verb.name}")

    return dict_from_registry


def initialise_membrane():

    from item_definitions import item_actions, item_defs_dict
    from verb_definitions import get_verb_defs, directions
    from verbRegistry import initialise_verbRegistry
    from itemRegistry import initialise_itemRegistry

    initialise_verbRegistry() ## HAVE to make sure this runs before running the parser.
    ### Re: initialising these, I really need to just run all the initialisers in set_up_game, all at once so they're done regardless of what step happens next. Do that soon.
    initialise_itemRegistry()


    membrane = {}

    verb_defs_dict, verbs_set = get_verb_defs()
    nouns_list = list(item_defs_dict.keys())
    membrane["key_verb_names"] = set(verb_defs_dict.keys())
    membrane["item_action_options"] = item_actions
    print(f"\n\nVERBS LIST: \n\n{verbs_set}")
    print(f"\n\nNOUNS LIST: \n\n{nouns_list}")

    from env_data import dataset
    membrane["locations"] = list(dataset.keys())
    membrane["directions"] = directions
    print(f"\n\nLOCATIONS: \n\n{membrane["locations"]}\n\n")

    membrane_data = nouns_list, membrane["locations"], directions

    return membrane, membrane_data ## 'membrane' for use in this script, 'membrane_data' for verbRegistry. ## Well that was the series, but I'm not using membrane at all. Really need to figure this out.
    #Honestly maybe membrane should hold the full dicts etc that multiple scripts need, so I'm always grabbing it from the same place. Currently I'm grabbing whatever from whereever, it's not ideal.


def run_membrane(input_str):

    from verbRegistry import Parser, initialise_verbRegistry

    initialise_verbRegistry

    print(f"\nTEST STRING: `{input_str}`")

    viable_formats, dict_from_registry = Parser.input_parser(Parser, input_str, membrane_data)

    inst_dict = get_noun_instances(dict_from_registry)

    from verb_actions import router
    router(viable_formats, inst_dict)


#input_str = "drop the paperclip in glass jar"
input_str = "put batteries into watch"

membrane, membrane_data = initialise_membrane()

if __name__ == "__main__":

    test_input_list = ["take the paperclip", "pick up the glass jar", "put the paperclip in the wallet", "place the dried flowers on the headstone", "go to the graveyard", "approach the forked tree branch", "look at the moss", "examine the damp newspaper", "read the puzzle mag", "read the fashion mag in the city hotel room", "open the glass jar", "close the window", "pry open the TV set", "smash the TV set", "break the glass jar", "clean the watch", "clean the severed tentacle", "mix the unlabelled cream with the anxiety meds", "combine the fish food and the moss", "eat the dried flowers", "consume the fish food", "drink the unlabelled cream", "burn the damp newspaper", "burn the fashion mag in a pile of rocks", "throw the pretty rock", "lob the pretty rock at the window", "chuck the glass jar into a pile of rocks", "drop the wallet", "discard the paper scrap with number", "remove the batteries from the TV set", "add the batteries to the mobile phone", "put the car keys in the plastic bag", "set the watch", "lock the window", "unlock the window", "shove the TV set", "move the headstone", "barricade the window with the TV set", "separate the costume jewellery", "investigate the exact thing", "observe the graveyard", "watch the watch", "go to a city hotel room", "leave the graveyard", "depart", "go", "go to the pile of rocks", "take the exact thing", "put the severed tentacle in the glass jar", "open the wallet with the paperclip", "read the mail order catalogue at the forked tree branch", "pick the moss", "pick the watch", "pick up moss", "throw anxiety meds", "put batteries into watch", "clean a pile of rocks"]

# failed: "wipe the window with the damp newspaper", "push the pile of rocks", "pull the forked tree branch",

    if test_input_list:
        for i, input_str in enumerate(test_input_list):
            run_membrane(input_str)
            print(f"\nThat was number {i}\n")
    else:
        run_membrane(input_str)
    #run_membrane(input_str)
