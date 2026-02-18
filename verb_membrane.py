#I like the idea of the verb-word-objects being different from the verb-action-objects. One's grammatical, one's an action-driver. With the third that is actually a list of functions for specific verbs.

### input_membrane, now.
# Takes the raw input.
# Sends it to verbRegistry.
# Gets the format and the dict back.
# Checks the nouns are viable for the verb.
# Then sends the format and dict onward to verb_actions.

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
    def check_cardinals(entry, dictionary, format):

        from env_data import locRegistry
        loc_inst = None
        for _, dict_entry in dictionary.items():
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
        dictionary[idx][kind] = ({"instance": card_inst, "str_name": entry["str_name"], "text": entry["text"]})
        return dictionary

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
                #print(f"GET NOUN INSTANCES::: Kind: {kind}, entry: {entry}\n")
                if kind == "noun":
                    name = entry["str_name"]
                    if name == "assumed_noun":
                        if entry.get("instance"):
                            print(f"entry[instance]: {entry["instance"]}")

                        dict_from_parser[idx][kind] = ({"instance": "assumed_noun", "str_name": entry["str_name"], "text": entry["text"]})
                        error = ("assumed_noun", (idx, kind))
                    else:
                        noun_inst = registry.instances_by_name(name) ## NOTE: This won't hold for long. Different instances may have different attr.
                        if not noun_inst:
                            suitable_nouns -= 10
                            ### wait wtf it MAKES a new instance to check noun attr???
                            #NOTE cancelled this new item generation for now, I can't imagine why that was here tbh...
                            #if name in registry.item_defs:
                            #    noun_inst = registry.init_single(name, registry.item_defs[name])
                        #if not noun_inst:
                            dict_from_parser[idx][kind] = ({"instance": "4", "str_name": entry["str_name"], "text": entry["text"]})
                            error = ("assumed_noun", (idx, kind))
                        else:
                            #print(f"Noun inst: {noun_inst}")
                            if not isinstance(noun_inst, ItemInstance):
                                if len(noun_inst) > 1:
                                    loc_found = False
                                    from env_data import locRegistry
                                    for noun in noun_inst:
                                        if noun.location == locRegistry.current:
                                            noun_inst = noun
                                            loc_found = True
                                            break
                                    if not loc_found: # just take the first if none are local.
                                        noun_inst = noun_inst[0]
                                else:
                                    noun_inst = noun_inst[0]
                            dict_from_parser[idx][kind] = ({"instance": noun_inst, "str_name": name, "text": entry["text"]})

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
                    #print(f"LOC NAME from str_name IN LOCATION: {loc_name}")
                    if locRegistry.place_by_name(loc_name):
                        dict_from_parser[idx][kind] = ({"instance": locRegistry.place_by_name(loc_name), "str_name": loc_name, "text": entry["text"]})

                elif kind == "direction": #Changing cardinals to their own specicial thing, can then ignore this part really.

                    dict_from_parser[idx][kind] = ({"instance": None, "str_name": entry["str_name"], "text": entry["text"]})
                    # TODO: Make it more explicit (or at least, really really remember) that this is going to <cardinal> <current_location> unless stated otherwise.

                        #locRegistry.place_cardinals[place_instance_obj][cardinal_direction_str]
                elif kind == "cardinal":
                    #print(f"Kind is cardinal: {entry}")
                    dict_from_parser = check_cardinals(entry, dict_from_parser, viable_formats)

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

        from env_data import loc_dict
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

        from itemRegistry import registry
        from env_data import locRegistry

        inventory = registry.get_item_by_location(locRegistry.inv_place)
        current_loc_items = registry.get_item_by_location(locRegistry.current)
        #print(f"current_loc_items: {current_loc_items}")
        local_named = set()
        local_items = {}
        if inventory:
            for item in inventory:
                local_named.add(item.name)
                local_items[item.name] = item
        if current_loc_items:
            for item in current_loc_items:
                local_named.add(item.name)
                local_items[item.name] = item

        for item, inst in registry.by_alt_names.items():
            #print(f"alt_names: item: {item} / inst: {inst}")
            if inst in local_items:
                local_named.add(item)
                #print(f"inst `{inst}` in local_items.values()")
                local_items[item] = local_items[inst]
                #print(f"local_items[item] for {item}: {local_items[item]}")

        # Need to add transition items if current is exit/entrance:
        if registry.transition_objs.get(locRegistry.current.place):
            print(f"registry.transition_objs.get(locRegistry.current.place): {registry.transition_objs.get(locRegistry.current.place)}")
            local_named.add(registry.transition_objs[locRegistry.current].name)
            print(f"Added transition object to local_named: `{registry.transition_objs[locRegistry.current].name}`")
            local_items[item.name] = registry.transition_objs[locRegistry.current]

        self.local_nouns = local_named
        self.local_dict = local_items
        #print(f"local nouns: {self.local_nouns}")

membrane = Membrane()

def add_item(input_str):
    from env_data import locRegistry

    if " add " in input_str:
        splitstr = input_str.split(" add ")
        input_str = splitstr[-1]

    if input_str in registry.item_defs:
        print(f"registry.item_defs[test]: {registry.item_defs[input_str]}")
        created_item = registry.init_single(input_str, registry.item_defs[input_str])
    else:
        print(f"No item named `{input_str}`. Do you want to create a new item?")
        new_test = input("y/yes for yes, anything else to return.")
        if new_test not in ("y", "yes"):
            print("Returning.")
            return
        from itemRegistry import new_item_from_str
        created_item = new_item_from_str(input_str, input_str=None, loc_cardinal=locRegistry.current.place_name)

    registry.move_item(created_item, location=locRegistry.current)
    from testing_coloured_descriptions import init_loc_descriptions
    init_loc_descriptions(locRegistry.current)

    print(f"Generated item ``{created_item}``.")


def immediate_commands(input_str):
    from env_data import locRegistry
    print_yellow(f"IMMEDIATE COMMAND: {input_str}")
    if input_str.startswith("godmode") and input_str != "godmode":
        if " add " in input_str:
            add_item(input_str)

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

    if input_str == "print all events":
        all_events = []
        for event in eventRegistry.events.events:
            all_events.append(event)
        print(f"\nALL EVENTS: {all_events}")

    if "god" in input_str:
        where = input('"add" or "add item" to add an item. "move" to force move an item to a location.')
        if where in ("add", "add item", "add_item"):
            input_str = input("Enter <item_name> to spawn an item at your location. This is the only option at present.\n")

            if input_str == "":
                print("Nothing entered; returning")
                return input()
            if input_str in registry.item_defs:
                print(f"registry.item_defs[test]: {registry.item_defs[input_str]}")
                created_item = registry.init_single(input_str, registry.item_defs[input_str])
            else:
                print(f"No item named `{input_str}`. Do you want to create a new item?")
                new_test = input("y/yes for yes, anything else to return.")
                if new_test not in ("y", "yes"):
                    print("Returning.")
                    return input()
                from itemRegistry import new_item_from_str
                created_item = new_item_from_str(input_str, input_str=None, loc_cardinal=locRegistry.current.place_name)
            registry.move_item(created_item, location=locRegistry.current)
            print(f"Generated item ``{created_item}``.")

        elif "move" in where:
            itemname = input("Enter name of item you wish to move.")
            item = registry.by_name.get(itemname)
            if not item:
                print(f"No item by the name {itemname}, returning.")
                return input()
            if isinstance(item, list):
                for inst in item:
                    input_str = input(f"Do you want to move item {inst}?")
                    if input_str in ("y", "yes"):
                        item = inst
                        break
            else:
                if isinstance(item, ItemInstance):
                    item = item

            new_loc_str = input("Enter the name of the location, as <location>, <cardinal location> or 'current'.")
            if new_loc_str == "current":
                location = locRegistry.current
            else:
                location = locRegistry.by_cardinal_str(new_loc_str)
            if not location:
                print(f"No location found from `{new_loc_str}`, returning.")
            else:
                registry.move_item(item, location=location)
                print(f"Moved item: {item}")
                print(f"New location: {item.location}")

        #created_item = registry.init_single(test, apply_location=locRegistry.current)

    print_yellow("Exiting immediate_commands.\n")
    return

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
        return super().default(o)

from notes_and_scribbles.test_commands import input_command_list

input_outcome_dict = {}
import config
to_json = config.parser_tests_output_to_json

def run_membrane(input_str=None, run_tests=False):
    logging_fn()

    if input_str and input_str == "exit":
        print("input_str is exit at top of run_membrane")
        return "exit"

    def loop(input_str):

        logging_fn()

        def log(): # leaving it here but disabled, just useful to test obj counts as things expand. # Add log_objects to config at some point.
            import gc
            objs = len(gc.get_objects())
            from mem_checker import log_objects
            log_objects(objs, input_str, run_tag="full_mem_test")
        #log()

        immediate_command = ["print local items", "print inventory items", "print named items", "print current events", "print all events", "godmode", "god mode"]
        while input_str == None or input_str == "":
            input_str = input("\n")
            if input_str in immediate_command or input_str.startswith("godmode"):
                immediate_commands(input_str)
                input_str = input()
        #print(f"\ninput_STR:::: {input_str}\n")
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

        if input_str == "exit":
            print(f"Returning after logging: exit")
            return "exit"
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
                message, idx_kind = error
                if isinstance(error, str):
                    if error == "No dict_from_parser":
                        # print this if you need to, but in general, don't.
                        #print(f"Error: {error}")
                        return None
                if "assumed_noun" in message or "non_local noun" in message:
                    from misc_utilities import print_failure_message
                    print_failure_message(input_str, message, idx_kind, inst_dict, viable_format)
                    return None
                else:
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

                with open(test_file, 'w') as file:
                    json.dump(input_outcome_dict, file, indent=2, cls=UserEncoder)

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
        from time import sleep
        test_inputs = input_command_list
        for i, input_str in enumerate(test_inputs):

            print()
            test = loop(input_str)
            if test == "exit":
                return "exit"

            sleep(.05)
            #input("Press any key to continue to next.")
            if i == len(test_inputs)-1:
                config.run_tests = False
                #run_tests = False
            else:
                print()

    else:
        test = loop(input_str)
        if test == "exit":
            print("Loop test at end == exit, returning `exit`.")
            return "exit"

