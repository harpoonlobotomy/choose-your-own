


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

   #exit()

def get_noun_instances(dict_from_parser):

    def check_noun_actions(noun_inst, verb_inst):

        #print(f"Verb inst name: {verb_inst.name}")
        #print(f"noun inst actions: {noun_inst.verb_actions}")
        for action in noun_inst.verb_actions:
            if flag_actions.get(action):
                if verb_inst.name in flag_actions[action]:
                    #print(f"{action}: Verb inst name in flag_actions for noun: ({noun_inst.name}): {verb_inst.name}")
                    return noun_inst.name

    verb = None
    #print(f"dict_from_parser: {dict_from_registry}")
    for data in dict_from_parser.values():
        for kind, entry in data.items():
            print(f"kind: {kind}, entry: {entry}")
            if "verb" in kind:
                verb = entry["instance"]
                #print(f"Verb: {verb}")
                #print(f"Verb type: {type(verb)}")
                print(f"Verb.name in get_noun_instances: `{verb.name}`")

    suitable_nouns = 0

    for idx, data in dict_from_parser.items():
        for kind, entry in data.items():
            #  dict_from_registry[i]={item: {"instance":verb, "str_name":item_name}}

            print(f"GET NOUN INSTANCES::: Kind: {kind}, entry: {entry}")
            if kind == "noun":
                name = entry["str_name"]
                noun_inst = registry.instances_by_name(name)
                if not noun_inst:
                    suitable_nouns -= 10
                    print(f"No found ItemInstance for {entry}")
                else:
                    #print(f"Noun inst: {noun_inst}")
                    noun_name = check_noun_actions(noun_inst[0], verb)
                    if noun_name:
                        dict_from_parser[idx][kind] = ({"instances": noun_inst[0], "str_name": name})
                        suitable_nouns += 1
                    else:
                        print(f"You can't {verb.name} the {entry}")
                        suitable_nouns -= 10

            elif kind == "location":
                from env_data import places
                loc_name = entry["str_name"]
                if places.get(loc_name):
                    dict_from_parser[idx][kind] = ({"instances": places[loc_name], "str_name": loc_name})


    if suitable_nouns >= 0 or verb.name == "look":
        print(f"All nouns ({suitable_nouns}) are suitable for this verb ({verb.name}). Sending onward.")

    else:
        print(f"At least one noun from dict nouns does not match this verb: {verb.name}")

    return dict_from_parser

class Membrane:
    ## To hold the general dicts/lists etc as a central point, so verbRegistry and itemRegistry can get data from item_definitions/verb_definitions from here instead of directly. Also other custom data, like the formats-by-type dict etc.
    # So to clarify: itemRegistry is all item objects, and currently has item actions but those will be moved out.
    # verbRegistry is really just for parsing, but the parsing is format + verb based so the name can stay I guess.
    # membrane will hold the disparate dicts from item defs and verb defs that are required for the later stage of parsing, and to distribute from the main scripts to the parser + side scripts.


    ## So - maybe I run Membrane first, use that to init verbR and itemR. Do all that separate to any parsing, just set it all up. /Then/ after that, membrane is the interface between input and all the background processes.


    def __init__(self):

        from item_definitions import item_defs_dict#, item_actions
        from verb_definitions import get_verb_defs, directions, formats, combined_wordphrases

        verb_defs_dict, verbs_set = get_verb_defs()

        self.key_verb_names = set(verb_defs_dict.keys())
        self.all_verb_names = verbs_set
        self.combined_wordphrases = combined_wordphrases

        self.nouns_list = list(item_defs_dict.keys()) ## prev. 'nouns_list'
        #self.item_action_options = item_actions ### Is this ever used? I think only for get_item_actions in itemregistry, not here. Use the instance flags instead, that's what they're for.

        from env_data import dataset
        self.locations = list(dataset.keys())
        from itemRegistry import registry

        self.plural_words_dict = registry.plural_words
        print(self.plural_words_dict)
        compound_locs = {}
        for word in self.locations:
            compound_locs[word] = tuple(word.split())
        self.compound_locations = compound_locs
        self.directions = directions

        def get_format_sublists(all_formats):

            sublists = {
                "location_only": ["verb_only", "verb_loc", "verb_dir", "verb_dir_loc"],
                "single_nouns": ["verb_noun", "verb_dir_noun", "verb_noun_dir", "verb_noun_dir_loc"],
                "two_nouns": ["verb_noun_noun", "verb_noun_dir_noun", "verb_noun_dir_dir_noun", "verb_noun_dir_noun_dir_loc", "verb_noun_sem_noun", "verb_dir_noun_sem_noun"]
            }
            def get_format_sublist(format_list):
                temp_list = []
                for format in format_list:
                    temp_list.append(all_formats[format])
                return temp_list

            new_format_dict = {}
            for name, list in sublists.items():
                new_format_dict[name] = get_format_sublist(list)

            return new_format_dict

        self.formats = formats
        self.format_sublists = get_format_sublists(formats)



membrane = Membrane()

test_input_list = ["take the paperclip", "pick up the glass jar", "put the paperclip in the wallet", "place the dried flowers on the headstone", "go to the graveyard", "approach the forked tree branch", "look at the moss", "examine the damp newspaper", "read the puzzle mag", "read the fashion mag in the city hotel room", "open the glass jar", "close the window", "pry open the TV set", "smash the TV set", "break the glass jar", "clean the watch", "clean the severed tentacle", "mix the unlabelled cream with the anxiety meds", "combine the fish food and the moss", "eat the dried flowers", "consume the fish food", "drink the unlabelled cream", "burn the damp newspaper", "burn the fashion mag in a pile of rocks", "throw the pretty rock", "lob the pretty rock at the window", "chuck the glass jar into a pile of rocks", "drop the wallet", "discard the paper scrap with number", "remove the batteries from the TV set", "add the batteries to the mobile phone", "put the car keys in the plastic bag", "set the watch", "lock the window", "unlock the window", "shove the TV set", "move the headstone", "barricade the window with the TV set", "separate the costume jewellery", "investigate the exact thing", "observe the graveyard", "watch the watch", "go to a city hotel room", "leave the graveyard", "depart", "go", "go to the pile of rocks", "take the exact thing", "put the severed tentacle in the glass jar", "open the wallet with the paperclip", "read the mail order catalogue at the forked tree branch", "pick the moss", "pick the watch", "pick up moss", "throw anxiety meds", "put batteries into watch", "clean a pile of rocks"]

def run_membrane(input_str):

    from verbRegistry import Parser
    viable_formats, dict_from_parser = Parser.input_parser(Parser, input_str)

    inst_dict = get_noun_instances(dict_from_parser)
    from verb_actions import router
    print(f"inst_dict going to router: {inst_dict}")
    #exit()
    router(viable_formats, inst_dict)


#input_str = "drop the paperclip in glass jar"
input_str = "put batteries into watch"
#
#membrane, membrane_data = initialise_membrane()


if __name__ == "__main__":


# failed: "wipe the window with the damp newspaper", "push the pile of rocks", "pull the forked tree branch",



    if test_input_list:
        for i, input_str in enumerate(test_input_list):
            run_membrane(input_str)
            print(f"\nThat was number {i}\n")
    else:
        run_membrane(input_str)
    #run_membrane(input_str)
