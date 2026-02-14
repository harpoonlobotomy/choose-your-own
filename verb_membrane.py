


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
import eventRegistry
from itemRegistry import ItemInstance, registry
from logger import logging_fn
from printing import print_yellow
from verbRegistry import VerbInstance

MOVE_UP = "\033[A"
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

combine_parts = {("put", "into"), ("add", "to"), ("a", "while")# thinking about this for more specific matching. Not sure. Idea is 'put x into y' == explicitly y is a container.
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

    error = None
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
            loc_inst = locRegistry.current.place
        card = entry['str_name']
        #print(f"locRegistry.cardinals[loc_inst]: {locRegistry.cardinals[loc_inst]}")

        card_inst = locRegistry.cardinals[loc_inst][card]
        dict_from_parser[idx][kind] = ({"instance": card_inst, "str_name": entry["str_name"], "text": entry["text"]})
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
                requires_noun = False
                #print(f"GET NOUN INSTANCES::: Kind: {kind}, entry: {entry}")
                if kind == "noun":
                    requires_noun = True
                    noun_name = None
                    name = entry["str_name"]
                    noun_inst = registry.instances_by_name(name) ## NOTE: This won't hold for long. Different instances may have different attr.
                    if not noun_inst:
                        suitable_nouns -= 10
                        ### wait wtf it MAKES a new instance to check noun attr???
                        #NOTE cancelled this new item generation for now, I can't imagine why that was here tbh...
                        #if name in registry.item_defs:
                        #    noun_inst = registry.init_single(name, registry.item_defs[name])
                    #if not noun_inst:
                        dict_from_parser[idx][kind] = ({"instance": noun_inst, "str_name": entry["str_name"], "text": entry["text"]})
                        error = (f"No found ItemInstance for {entry}", (idx, kind))
                    else:
                        #print(f"Noun inst: {noun_inst}")
                        if not isinstance(noun_inst, ItemInstance):
                            noun_inst = noun_inst[0]
                        noun_name = name
                        dict_from_parser[idx][kind] = ({"instance": noun_inst, "str_name": name, "text": entry["text"]})
                        #noun_name = check_noun_actions(noun_inst, verb)
                        #if noun_name:
                        #    dict_from_parser[idx][kind] = ({"instance": noun_inst, "str_name": name, "text": entry["text"]})
                        #    suitable_nouns += 1
                        #else:
    ## NOTE: Added this here so all nouns pass even if they will fail later, which entirely removes the point of the allowed noun_actions. But, I can better tailor failure messages within each later action-fn. So I think I'm going with it for now.
                          #  dict_from_parser[idx][kind] = ({"instance": noun_inst, "str_name": name, "text": entry["text"]})
                          #  #print(f"You can't `{verb.name}` the {entry["str_name"]}")
                          #  suitable_nouns -= 10
                    if noun_inst and "is_cluster" in noun_inst.item_type:
                        from env_data import locRegistry
                        #TODO HERE.
                        if hasattr(noun_inst, "has_multiple_instances") and hasattr(noun_inst, "single_identifier") and hasattr(noun_inst, "plural_identifier"):
                            #print("Cluster has identifiers.")
                            if noun_inst.plural_identifier in entry["text"]:
                                #and noun_inst.has_multiple_instances > 1:
                                ## REMINDER: This is not to set the name, that is a biproduct. It's to find the correct instance if there is one.
                                local_named_items = registry.get_local_items(include_inv=True, by_name=noun_inst.name)
                                if local_named_items:
                                    print(f"Found more than one local item with name {noun_inst.name}. Checking input text for plural identifier `{noun_inst.plural_identifier}` to identify the correct one.")
                                    for item in local_named_items:
                                        if item.has_multiple_instances > 1:
                                            noun_inst = item
                                            registry.set_print_name(noun_inst, noun_inst.plural_identifier)
                                            break

                            elif noun_inst.single_identifier in entry["text"]:
                                local_named_items = registry.get_local_items(include_inv=True, by_name=noun_inst.name)
                                if local_named_items:
                                    for item in local_named_items:
                                        if item.has_multiple_instances == 1:
                                            noun_inst = item
                                            registry.set_print_name(noun_inst, noun_inst.single_identifier)
                                            break

                            dict_from_parser[idx][kind] = ({"instance": noun_inst, "str_name": noun_inst.name, "text": entry["text"]})

                elif kind == "location":
                    from env_data import locRegistry
                    loc_name = entry["str_name"]
                    if locRegistry.place_by_name(loc_name):
                        dict_from_parser[idx][kind] = ({"instance": locRegistry.place_by_name(loc_name), "str_name": loc_name, "text": entry["text"]})

                elif kind == "direction": #Changing cardinals to their own specicial thing, can then ignore this part really.

                    dict_from_parser[idx][kind] = ({"instance": None, "str_name": entry["str_name"], "text": entry["text"]})
                    # TODO: Make it more explicit (or at least, really really remember) that this is going to <cardinal> <current_location> unless stated otherwise.

                        #locRegistry.place_cardinals[place_instance_obj][cardinal_direction_str]
                elif kind == "cardinal":
                    #print(f"Kind is cardinal: {entry}")
                    dict_from_parser = check_cardinals(entry, dict_from_parser, viable_formats)

                if requires_noun == True: # Not sure this'll ever come up, as a thing will likely fail at the initial parser stage. Maybe delete this later.
                    if not noun_name:
                        print(f"{MOVE_UP}\033[1;31m[ Couldn't find anything to do with the input `{name}`, sorry. ]\033[0m")
                    requires_noun = False
        #print("About to return dict_from_parser, error")
        return dict_from_parser, error
    #print("About to return dict_from_parser, error")
    return None, "No dict_from_parser"

class Membrane:

    def __init__(self):

        from verb_definitions import get_verb_defs, directions, formats, combined_wordphrases, cardinals
        verb_defs_dict, verbs_set = get_verb_defs()

        self.key_verb_names = set(verb_defs_dict.keys())
        self.all_verb_names = verbs_set
        self.combined_wordphrases = combined_wordphrases

        from env_data import loc_dict, locRegistry
        self.locations = list(loc_dict.keys())

        self.nouns_list = list(registry.item_defs.keys())
        #plural_word_dict = {}
#
        #for item_name in self.nouns_list:
        #    if len(item_name.split()) > 1:
        #        plural_word_dict[item_name] = tuple(item_name.split())
#
        self.plural_words_dict = registry.plural_words

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

    def get_local_nouns(self):

        from set_up_game import game
        from itemRegistry import registry
        from env_data import locRegistry

        #inventory = game.inventory
        #print(f"inventory: {inventory}")
        #print(f"locRegistry.current: {locRegistry.current}")
        inventory = registry.get_item_by_location(locRegistry.inv_place)
        current_loc_items = registry.get_item_by_location(locRegistry.current)
        #print(f"current_loc_items: {current_loc_items}")
        local_named = set()
        if inventory:
            for item in inventory:
                local_named.add(item.name)
        if current_loc_items:
            for item in current_loc_items:
                local_named.add(item.name)
        self.local_nouns = local_named
        #print(f"local nouns: {self.local_nouns}")

membrane = Membrane()
# excluded for not being relevant right now. "go to the graveyard", , "go to a city hotel room", "go to the pile of rocks", "approach the forked tree branch"


def immediate_commands(input_str):
# immediate_commands = ["print local items", "print inventory items", "print named items"]
    print_yellow(f"IMMEDIATE COMMAND: {input_str}")
    from env_data import locRegistry
    if input_str == "print local items":
        local_items = registry.by_location.get(locRegistry.current)
        print(f"LOCAL ITEMS:\n{local_items}\n")

    if input_str == "print inventory items":
        inv_items = locRegistry.inv_place.items
        print(f"INV_PLACE.ITEMS:\n{inv_items}\n")
        inv_items_2 = registry.by_location.get(locRegistry.inv_place)
        print(f"\nBY_LOCATION[LOC.INV_PLACE]:\n{inv_items_2}\n")

    if input_str == "print named items":
        item_name = input("Entry name here:  ")
        initial_names = registry.by_name.get(item_name)
        print(f"BY_ALT_NAME[NAME]:\n{initial_names}\n")
        alt_names = registry.by_alt_names.get(item_name)
        print(f"BY_ALT_NAME[NAME]:\n{alt_names}\n")

    if input_str == "print current events":
        current_by_inst_state = []
        for event in eventRegistry.events.events:
            if event.state == 1:
                current_by_inst_state.append(event)
        current_by_event_by_state = []
        for event in eventRegistry.events.event_by_state(1):
            current_by_event_by_state.append(event)
        print(f"\nevent_by_state(1):\n{current_by_event_by_state}\n\nevent.state == 1:\n{current_by_inst_state}\n")


    print_yellow("Exiting immediate_commands.\n")
    input_str = input()
    return input_str






test_input_list = ["take the paperclip", "take the paperclip", "pick up the glass jar", "put the paperclip in the wallet", "place the dried flowers on the headstone", "look at the moss", "examine the damp newspaper", "read the puzzle mag", "read the fashion mag in the city hotel room", "open the glass jar", "close the window", "pry open the TV set", "smash the TV set", "break the glass jar", "clean the watch", "clean the severed tentacle", "mix the unlabelled cream with the anxiety meds", "combine the fish food and the moss", "eat the dried flowers", "consume the fish food", "drink the unlabelled cream", "burn the damp newspaper", "burn the fashion mag in the graveyard", "throw the pretty rock", "lob the pretty rock at the window", "chuck the glass jar into the glass jar", "drop the wallet", "discard the paper scrap with number", "remove the batteries from the TV set", "add the batteries to the mobile phone", "put the car keys in the plastic bag", "set the watch", "lock the window", "unlock the window", "shove the TV set", "move the headstone", "barricade the window with the TV set", "separate the costume jewellery", "investigate the exact thing", "observe the graveyard", "watch the watch", "leave the graveyard", "depart", "go", "take the exact thing", "put the severed tentacle in the glass jar", "open the wallet with the paperclip", "read the mail order catalogue at the forked tree branch", "pick the moss", "pick the watch", "pick up moss", "throw anxiety meds", "put batteries into watch", "clean a glass jar"]

#test_input_list = ["go west", "go north", "go to shed", "go north", "go to work shed", "go north", "go to shed door", "go to work shed door", "open door", "close door", "open shed door", "close shed door", "go into shed", "open door", "go into work shed", "go into work shed", "leave shed", "inventory", "drop mag", "take mag", "drop mag at church", "go into work shed", "open work shed door", "open door", "go into shed", "take map", "take key", "go to north graveyard", "use key on padlock", "lock padlock with key", "unlock padlock with key", "take padlock", "go to city hotel room", "find tv set", "look at tv set"]

test_input_list = ["go west", "open door", "enter shed", "take map", "take key", "go to north graveyard", "look at gate", "unlock padlock with key", "look at gate", "pick up padlock", "go to city hotel room", "find tv set", "go to east graveyard", "take jar", "logging args", "break jar"]

#test_input_list = ["go east", "take glass jar", "break jar", "pick up glass shard", "drop glass shard", "go west", "open door", "enter shed", "take map", "read map"]
test_input_list = ["east graveyard", "take moss", "take moss", "take moss"]
#test_input_list = ["logging args", "take stick", "approach the forked tree branch", "look around"]

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
        elif isinstance(o, set):
            return list(o)
        # Let the base class default method raise the TypeError
        return super().default(o)

input_outcome_dict = {}
import config
to_json = config.parser_tests_output_to_json

def run_membrane(input_str=None, run_tests=False):
    #if run_tests:
    #    def loop(input_str, i)
    def loop(input_str):
    #def loop(input_str):

        logging_fn()
        while input_str == None or input_str == "":
            input_str = input("\n")

        immediate_command = ["print local items", "print inventory items", "print named items", "print current events"]
        print(f"\ninput_STR:::: {input_str}\n")
        if input_str in immediate_command:
            while input_str in immediate_command:
                input_str = immediate_commands(input_str)
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


        try:
            from verbRegistry import Parser
            #print("Before input_parser")
            try:
                viable_format, dict_from_parser = Parser.input_parser(Parser, input_str)
                #print(f"After input_parser\n{dict_from_parser}")
                if not viable_format:
                    return None
            except Exception as e:
                print(f"Failed to run input_parser: {e}")

            try:
                inst_dict, error = get_noun_instances(dict_from_parser, viable_format)
            except Exception as e:
                print(f"Failed get_noun_instances: {e}")

            logging_fn(f"error: {error} // inst_dict: {inst_dict}")
            if error:
                if isinstance(error, str):
                    print(f"Error: {error}")
                    return None
                print(f"ERROR: {error}")
                message, idx_kind = error
                idx, kind = idx_kind
                print(f"inst_dict[idx][kind]: {inst_dict[idx][kind]}")
                text = inst_dict[idx][kind].get("text")
                canonical = inst_dict[idx][kind].get("str_name")
                if canonical and " " in canonical:
                    not_found = list()
                    parts = canonical.split()
                    print(f"PARTS: {parts}")
                    if parts:
                        for part in parts:
                            if part in input_str:
                                not_found.append(part)
                    if not_found:
                        text = " ".join(not_found)


                print(f"Nothing found here by the name \033[1;33m`{text}`\033[0m.")
                return None

            if not inst_dict:
                print(f"{MOVE_UP}\033[1;31m[ Couldn't find anything to do with the input `{input_str}`, sorry. ]\033[0m")
                return None
            #print("after get_noun_instances")
            if to_json:
                input_outcome_dict[(str(i) + " " + input_str)] = inst_dict
                import json
                test_file = "test_10_2_26_2.json"
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
            try:
                if inst_dict:
                    from verb_actions import router
                    response = router(viable_format, inst_dict, input_str)
                    if to_json:
                        test = input("Did it do what you wanted? Make notes here.\n")
                        if test:
                            inst_dict.update({f"OUTCOME": test})
                            input_outcome_dict[(str(i) + " " + input_str)] = inst_dict

                    return response
            except Exception as e:
                print(f"Failed to send to process in router correctly: {e}")
        except Exception as e:
            print(f"Failed parser: {e}")

    if run_tests:
        #print("run tests on")
        from time import sleep
        test_inputs = test_input_list#["get scroll", "open scroll", "go to east graveyard", "get glass jar", "put glass jar in scroll", "put scroll in glass jar"]
        for i, input_str in enumerate(test_inputs):
            #input_outcome_dict[str(i, input_str)] = None
            #print_yellow(f"#    input str: `{input_str}`")
            print()
            loop(input_str)

            sleep(.05)
            #input("Press any key to continue to next.")

            if i == len(test_inputs)-1:
                config.run_tests = False
                #run_tests = False
            else:
                print()

    else:
        #import json
        #test_file = "test_31_1_26.json"
        #with open(test_file, 'w') as file:
        #    json.dump(input_outcome_dict, file, indent=2)
        #loop(input_str, i)
        print(f"Starting new loop with input_str: {input_str}")
        loop(input_str)

