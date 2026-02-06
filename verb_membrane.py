


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

import pprint
from env_data import cardinalInstance, placeInstance
from eventRegistry import eventInstance
from itemRegistry import ItemInstance, registry
from logger import logging_fn
from printing import print_yellow
from verbRegistry import VerbInstance

movable_objects = ["put", "take", "combine", "separate", "throw", "push", "drop", "set", "move"]

flag_actions = {
    "can_pick_up": movable_objects,
    "flammable": ["burn", "set"],
    "dirty": "clean",
    "locked": "unlock",
    "can_be_locked": ["lock", "unlock"],
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

def check_noun_actions(noun_inst, verbname):

    #print(f"Verb inst name: {verbname}")
    #print(f"noun inst actions: {noun_inst.verb_actions}")
    if isinstance(verbname, VerbInstance):
        verbname = verbname.name
    if verbname in ("look", "use"): # always pass 'look'
        return noun_inst.name
    for action in noun_inst.verb_actions:
        if flag_actions.get(action):
            if verbname in flag_actions[action]:
                #print(f"{action}: Verb inst name in flag_actions for noun: ({noun_inst.name}): {verbname}")
                return noun_inst.name

    #print(f"Noun fails: {noun_inst}, verbname: {verbname}")

def get_noun_instances(dict_from_parser, viable_formats):

    def check_cardinals(entry, dict, format):

        from env_data import locRegistry
        loc_inst = None
        for _, dict_entry in dict.items():
            for k, v in dict_entry.items():
                if k == "location":
                    loc_inst = v.get("instance")
                    if not loc_inst:
                        #print(f"V: {v}")
                        loc_name = v.get("str_name")
                        #print(f"loc_name canonical: {loc_name}")
                        loc_inst = locRegistry.by_name[loc_name]

        if loc_inst == None:
            loc_inst = locRegistry.currentPlace
        card = entry['str_name']
        #print(f"locRegistry.cardinals[loc_inst]: {locRegistry.cardinals[loc_inst]}")

        card_inst = locRegistry.cardinals[loc_inst][card]
        dict_from_parser[idx][kind] = ({"instance": card_inst, "str_name": entry["str_name"]})
        return dict_from_parser

    #if len(viable_formats) != 1:
    #    print("More than one viable format. I can't handle that yet. Exiting.")
    #    print(viable_formats)
    #    exit()

    verb = None
    #print(f"dict_from_parser: {dict_from_parser}")
    if dict_from_parser:
        for data in dict_from_parser.values():
            for kind, entry in data.items():
                #print(f"kind: {kind}, entry: {entry}")
                if "verb" in kind:
                    verb = entry["instance"]
                    #print(f"Verb: {verb}")
                    #print(f"Verb type: {type(verb)}")
                    #print(f"Verb.name in get_noun_instances: `{verb.name}`")
                if "meta" in kind and verb == None:
                    verb = entry["instance"]
                    #print(f"meta Verb: {verb}")

        suitable_nouns = 0

        for idx, data in dict_from_parser.items():
            for kind, entry in data.items():

                #print(f"GET NOUN INSTANCES::: Kind: {kind}, entry: {entry}")
                if kind == "noun":
                    name = entry["str_name"]
                    noun_inst = registry.instances_by_name(name) ## NOTE: This won't hold for long. Different instances may have different attr.
                    if not noun_inst:
                        suitable_nouns -= 10
                        ### wait wtf it MAKES a new instance to check noun attr???
                        #NOTE cancelled this new item generation for now, I can't imagine why that was here tbh...
                        #if name in registry.item_defs:
                        #    noun_inst = registry.init_single(name, registry.item_defs[name])
                    #if not noun_inst:
                        print(f"No found ItemInstance for {entry}")
                    else:
                        #print(f"Noun inst: {noun_inst}")
                        if not isinstance(noun_inst, ItemInstance):
                            noun_inst = noun_inst[0]

                        noun_name = check_noun_actions(noun_inst, verb)
                        if noun_name:
                            dict_from_parser[idx][kind] = ({"instance": noun_inst, "str_name": name})
                            suitable_nouns += 1
                        else:
    ## NOTE: Added this here so all nouns pass even if they will fail later, which entirely removes the point of the allowed noun_actions. But, I can better tailor failure messages within each later action-fn. So I think I'm going with it for now.
                            dict_from_parser[idx][kind] = ({"instance": noun_inst, "str_name": name})
                            #print(f"You can't `{verb.name}` the {entry["str_name"]}")
                            suitable_nouns -= 10

                elif kind == "location":
                    from env_data import locRegistry
                    loc_name = entry["str_name"]
                    if locRegistry.place_by_name(loc_name):
                        dict_from_parser[idx][kind] = ({"instance": locRegistry.place_by_name(loc_name), "str_name": loc_name})

                elif kind == "direction": #Changing cardinals to their own specicial thing, can then ignore this part really.

                    dict_from_parser[idx][kind] = ({"instance": None, "str_name": entry["str_name"]})
                    # TODO: Make it more explicit (or at least, really really remember) that this is going to <cardinal> <current_location> unless stated otherwise.

                        #locRegistry.place_cardinals[place_instance_obj][cardinal_direction_str]
                elif kind == "cardinal":
                    #print(f"Kind is cardinal: {entry}")
                    dict_from_parser = check_cardinals(entry, dict_from_parser, viable_formats)

        #print(f"dict_from_parser in geT_noun_instances: {dict_from_parser}")
        return dict_from_parser
    return None

class Membrane:

    def __init__(self):

        from verb_definitions import get_verb_defs, directions, formats, combined_wordphrases, cardinals
        verb_defs_dict, verbs_set = get_verb_defs()

        self.key_verb_names = set(verb_defs_dict.keys())
        self.all_verb_names = verbs_set
        self.combined_wordphrases = combined_wordphrases

        from itemRegistry import registry
        self.nouns_list = list(registry.item_defs.keys())
        self.plural_words_dict = registry.plural_words

        from env_data import loc_dict
        self.locations = list(loc_dict.keys())

        compound_locs = {}
        for word in self.locations:
            compound_locs[word] = tuple(word.split())
        self.compound_locations = compound_locs
        self.directions = directions
        self.cardinals = set(cardinals) ## does membrane need these or not?

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

membrane = Membrane()

test_input_list = ["take the paperclip", "pick up the glass jar", "put the paperclip in the wallet", "place the dried flowers on the headstone", "go to the graveyard", "approach the forked tree branch", "look at the moss", "examine the damp newspaper", "read the puzzle mag", "read the fashion mag in the city hotel room", "open the glass jar", "close the window", "pry open the TV set", "smash the TV set", "break the glass jar", "clean the watch", "clean the severed tentacle", "mix the unlabelled cream with the anxiety meds", "combine the fish food and the moss", "eat the dried flowers", "consume the fish food", "drink the unlabelled cream", "burn the damp newspaper", "burn the fashion mag in a pile of rocks", "throw the pretty rock", "lob the pretty rock at the window", "chuck the glass jar into a pile of rocks", "drop the wallet", "discard the paper scrap with number", "remove the batteries from the TV set", "add the batteries to the mobile phone", "put the car keys in the plastic bag", "set the watch", "lock the window", "unlock the window", "shove the TV set", "move the headstone", "barricade the window with the TV set", "separate the costume jewellery", "investigate the exact thing", "observe the graveyard", "watch the watch", "go to a city hotel room", "leave the graveyard", "depart", "go", "go to the pile of rocks", "take the exact thing", "put the severed tentacle in the glass jar", "open the wallet with the paperclip", "read the mail order catalogue at the forked tree branch", "pick the moss", "pick the watch", "pick up moss", "throw anxiety meds", "put batteries into watch", "clean a pile of rocks"]

test_input_list = ["go west", "go north", "go to shed", "go north", "go to work shed", "go north", "go to shed door", "go to work shed door", "open door", "close door", "open shed door", "close shed door", "go into shed", "open door", "go into work shed", "go into work shed", "leave shed", "inventory", "drop mag", "take mag", "drop mag at church", "go into work shed", "open work shed door", "open door", "go into shed", "take map", "take key", "go to north graveyard", "use key on padlock", "lock padlock with key", "unlock padlock with key", "take padlock"]

test_input_list = ["logging_args", "go west", "open door", "enter shed", "take map", "take key", "go to north graveyard", "unlock padlock with key", "pick up padlock", "open gate"]

import json
class UserEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return str(iterable)

        if isinstance(o, ItemInstance|placeInstance|cardinalInstance|eventInstance|VerbInstance):
            return str(o)
        # Let the base class default method raise the TypeError
        return super().default(o)

input_outcome_dict = {}
to_json = False
def run_membrane(input_str=None):

    #if run_tests:
    #    def loop(input_str, i)
    def loop(input_str):
    #def loop(input_str):

        logging_fn()

        response = (None, None)

        while "logging" in input_str:
            if input_str != None and "logging" in input_str:
                from logger import logging_config
                logging_config["function_logging"] = not logging_config["function_logging"]
                if logging_config["function_logging"] == True:
                    print("Logging Enabled\n")
                else:
                    print("Logging Disabled\n")
                if "args" in input_str:
                    logging_config["args"] = not logging_config["args"]
                    if logging_config["args"] == True:
                        print("Args Printing Enabled\n")
                    else:
                        print("Args Printing Disabled\n")
                logging_fn()
                input_str = input()

        if input_str == None:
            input_str = input()

        try:
            from verbRegistry import Parser
            #print("Before input_parser")
            viable_format, dict_from_parser = Parser.input_parser(Parser, input_str)
            #print("After input_parser")
            if not viable_format:
                return None
            inst_dict = get_noun_instances(dict_from_parser, viable_format)
            #print("after get_noun_instances")
            if to_json:
                input_outcome_dict[(str(i) + " " + input_str)] = inst_dict
                import json
                test_file = "test_31_1_26.json"
            #try:
            #    for entry in input_outcome_dict:
            #        #print(f"ENTRY: {entry}")
            #        input_outcome_dict[entry]["OUTCOME"] = ""
            #except Exception as e:
            #    print(f"couldn't add 'outcome' to {entry}: {e}")
            #    if input_outcome_dict[entry] == None:
            #        input_outcome_dict[entry] = "OUTCOME:"
                with open(test_file, 'w') as file:
                    json.dump(input_outcome_dict, file, indent=2, cls=UserEncoder)
            #with open(test_file, 'w') as file:
            #    json.dump(input_outcome_dict, file, indent=2)
            #print(f"input_outcome_dict: ")
            #pprint.pprint(input_outcome_dict)

            if inst_dict:
                from verb_actions import router
                response = router(viable_format, inst_dict)
                if to_json:
                    test = input("Did it do what you wanted? Make notes here.\n")
                    if test:
                        input_outcome_dict[(str(i) + " " + input_str)] = inst_dict
                        input_outcome_dict[(str(i) + " " + input_str)].update({f"OUTCOME": test})

                return response
        except Exception as e:
            print(f"Failed parser: {e}")

    #from config import run_tests
    run_tests = False#True
    if run_tests:
        print("run tests on")
        from time import sleep
        test_inputs = test_input_list#["get scroll", "open scroll", "go to east graveyard", "get glass jar", "put glass jar in scroll", "put scroll in glass jar"]
        for i, input_str in enumerate(test_inputs):
            #input_outcome_dict[str(i, input_str)] = None
            #print_yellow(f"#    input str: `{input_str}`")
            loop(input_str)

            sleep(.05)

            print()
            if i == len(test_inputs)-1:
                run_tests = False

    else:
        #import json
        #test_file = "test_31_1_26.json"
        #with open(test_file, 'w') as file:
        #    json.dump(input_outcome_dict, file, indent=2)
        if run_tests:
            print(f"input_outcome_dict: ")
            pprint.pprint(input_outcome_dict)
            print("\n\n")

            print()
            exit("Exiting, please check JSON file.")
        #loop(input_str, i)
        loop(input_str)

