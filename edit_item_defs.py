import uuid
from pprint import pprint
from itemRegistry import ItemInstance
from misc_utilities import assign_colour
import printing

standard = "standard"
static = "static"
can_pick_up = "can_pick_up"
container = "container"
event = "event"
trigger = "trigger"

confirmed_items = {}

import json
gen_items_file = "dynamic_data/generated_items.json"

##  !! container limits come from container_limit_sizes in item defs

# ! 'description_no_children', 'name_children_removed'  -- I really should use the dynamic description system here too. Whenever something is added/removed to/from a container, update the description. I'll add them wholecloth for now but really want to change this.

# 'description_no_children' == description_no_children
# 'name_children_removed' == name_no_children  ### Both of these two are updated at the name/description stage, not type_defaults.

# 'needs_key_to_lock' = requires_key,
# 'can_lock' == "can_be_locked"
# 'is_closed == 'is_open:False'
#
## Removed all the interior dicts. They're not necessary and will actually get in the way - having the type defaults exposed is far more beneficial.

from itemRegistry import type_defaults

all_flags_in_type_default = set() # temporarily putting this out here.
for cat_type in type_defaults:
    all_flags_in_type_default.add(cat_type)
    for flag in type_defaults[cat_type]:
        all_flags_in_type_default.add(flag)

def check_flag(item_types:set=set(), flag:str="", get_single=True):

    print(f"ITEM_TYPES in check_flag: {item_types}")
    if flag in all_flags_in_type_default:
        for typename in type_defaults:
            if flag in type_defaults[typename]:
                item_types.add(typename)
                if get_single:
                    print(f"Returning typename {typename}")
                    return typename, 1
        if not get_single:
            print(f"returning item_types: {item_types}")
            return item_types, 1
    return None, 0

def check_all_flags_present():

    import json
    json_primary = "dynamic_data/items_main.json" # may break things
    with open(json_primary, 'r') as file:
        item_defs_dict = json.load(file)
    missing_tags = {}

    for item in item_defs_dict:
        missing_tags[item]={}

        item_types = item_defs_dict[item].get("item_type")

        if not item_types:
            print(f"{item} does not have item_type field.")
            continue

        item_types = item_types.replace(",", "")
        item_types = item_types.replace("'", "")
        item_types = item_types.replace("{", "")
        item_types = item_types.replace("}", "")

        if " " in item_types.strip():
                parts = item_types.strip().split(" ")
                print(f"PARTS: {parts}")
                parts = list(i for i in parts if i != None and i in list(type_defaults))

                if len(parts) > 1:
                    print(f"Parts len >1 : {parts}, type: {type(parts)}")
                    new_str = set(parts)
                else:
                    new_str = set()
                    new_str.add(parts[0])
                    print(f"NEW_STR: {new_str}")
                    #new_str = set([parts])
                #new_str = set(parts)
                print(f"NEW_STR: {new_str}, len: {len(new_str)}")

        elif item_types in list(type_defaults):
            print(f"Input str in type_defaults: {item_types}, type: {type(item_types)}")
            new_str = set([item_types])

        else:
            print(f"No item types for {item} after string processing.")
            continue

        item_types = new_str

        for def_type in item_types:
            print(f"DEF TYPE: {def_type}")
            type_tags = type_defaults.get(def_type)
            for tag in type_tags:
                if not item_defs_dict[item].get(tag):
                    missing_tags[item][tag]=type_defaults[def_type].get(tag)

    print("Missing tags per item: ")
    from pprint import pprint
    pprint(missing_tags)

    for item, field in item_defs_dict.items():
        if missing_tags.get(item):
            for attr in missing_tags[item]:
                item_defs_dict[item][attr] = missing_tags[item][attr]
        #for attr in item_defs_dict[item].get(field):
        #    if missing_tags.get(item) and missing_tags[item].get(list(field)[0]):
        #        item_defs_dict[item].update(field = missing_tags[item][field])

    #print("Updated dict: ")
    #from pprint import pprint
    #pprint(item_defs_dict)

    test=input()
    if test in ("y", "yes"):
        with open(gen_items_file, 'w') as file: ##NOTE: Currently puts it in generated instead so I can check, later just do it directly back to items_main.
            json.dump(item_defs_dict, file, indent=2)

#check_all_flags_present()

def testing_t_defaults_against_item_defs(per_item=True, item_name=""):

    def_flags_in_t_def = set()
    all_def_flags = set()
    collected_per_item = {}

    import json
    json_primary = "dynamic_data/items_main.json" # may break things
    with open(json_primary, 'r') as file:
        item_defs_dict = json.load(file)

    #from item_definitions import item_defs_dict
    for item, val in item_defs_dict.items():
        if item_name:
            if item != item_name:
                #print(f"Item {item} is not {item_name}")
                continue
        if per_item:
            collected_per_item[item] = {}
        for flag, content in val.items():
            print(f"FLAG: {flag} // CONTENT: {content}")
            value = None
            if flag == "" or flag == None:
                continue
            if flag == "flags":
                for flagname in content:
                    if per_item:
                        if flagname in all_flags_in_type_default:
                            return_item, success = check_flag(flag=flagname, get_single=True)
                            print(f"RETURN ITEM: {return_item}")
                            if success:
                                value = type_defaults[return_item].get(flagname)
                                if value:
                                    collected_per_item[item][flagname]=value
                                    print(f"collected_per_item[item][flagname]: {collected_per_item[item][flagname]}")
                            if not value:
                                value = item_defs_dict[item].get(flagname)
                                if not value:
                                    print(f"Failed to get value for {flagname}")
                                else:
                                    collected_per_item[item][flagname]=value

                        if not value and not item_defs_dict[item].get(flagname):
                            print(f"flagname {flagname} not in all_flags_in_type_default.\nEntering value of None\n ")
                            #if not value:
                            collected_per_item[item][flagname]=None
                        else:
                            if item_defs_dict[item].get(flagname):
                                collected_per_item[item][flagname]=item_defs_dict[item].get(flagname)
                    else:
                            def_flags_in_t_def.add(flagname)
                            all_def_flags.add(flagname)
            else:
                if per_item:
                    collected_per_item[item][flag]=content
                else:
                    if flag in all_flags_in_type_default:
                        def_flags_in_t_def.add(flag)
                    else:
                        all_def_flags.add(flag)

        if per_item:
            print(f"ITEM FLAGS for {item}: {collected_per_item[item]}")

    if per_item:
        return collected_per_item
    else:
        print(f"Flags matching in type_default: {def_flags_in_t_def}")
        print(f"Flags in item_defs but not default_types: {all_def_flags - all_flags_in_type_default}")
        return all_flags_in_type_default


use_generated = False
 ## just a shortcut for a min while I test TODO remember to delete later
gen_items = {}


class tempDatastore:

    def __init__(self, item_data):
        self.item_defs:dict = item_data
        self.updated_defs = {}

        self.flags_to_amend = set()
        self.temp_items = set()
        self.confirmed_items = {}
        self.updated = set()

item_defs = r"ref_files\items_main.json"
with open(item_defs, 'r') as file:
    item_data = json.load(file)

testReg = tempDatastore(item_data)

"""
indexed view:
def items_in(container=None, *, open=None, locked=None):
    for item in self.by_location[graveyard_east]:
        if container is not None and item.container is not container:
            continue
        if open is not None and item.is_open != open:
            continue
        if locked is not None and item.is_locked != locked:
            continue
        yield item

for i in items_in(container=True, open=True):
    ...

So indexed view is definitely what I need. The duplication and even deep nesting is just going to be messy.

    """
#def init_testreg():

### Okay so I need to apply defaults first, guaranteed, then apply exceptions. I think that's why event_key is failing.


if __name__ == "__main__":
    #init_testreg()
    """
    def get_loc_items(loc, cardinal=None):

        Now currently, items are stored and they tell env_data where they live. It does make more sense to place them via location not via the item itself.

        I think I want to have a separate dict for it, like I have here in my test setup. Otherwise I have to double-back through all the items anyway to add instances

        if cardinal == None:
            for cardinal in ("north", "south", "east", "west"):
                if locations[loc][cardinal].get("items"):
                    for item_name in locations[loc][cardinal]["items"]:
                        loc_item = {}
                        if test_items.get(item_name):
                            loc_item[item_name] = test_items[item_name]
                        elif gen_items.get(item_name):
                            loc_item[item_name] = gen_items.get(item_name)
                        else:
                            loc_item[item_name] = ({"item_type": [static]})

                        loc_item[item_name].setdefault("exceptions", {}).update({"starting_location": cardinal + " " + loc})
                        inst = testReg.init_single(item_name, loc_item[item_name])# definition_key, attr
                        #testReg.init_items(loc_item)# doing one at a time otherwise different loc items will overwrite

    def main_test():
        #use_generated_items(input_=None)

        for item in test_items:
            if gen_items.get(item):
                print(f"gen_items item: {gen_items.get(item)}")
            temp = {}
            temp[item] = gen_items.get(item)
            item = temp
            testReg.init_items(item)

        #get_loc_items("Graveyard")

        def print_ordered_vars(item):
            vars_dict = vars(item)

            temp_queue = dict()
            new_queue = dict()
            for item in vars_dict:
                #print(f"\033[4;35;47mItem in vars dict: {item} \033[0m")
                temp_queue[item] = vars_dict[item]

            leftovers = list(i for i in list(temp_queue) if i not in flag_keys)

            for k in leftovers:
                val = vars_dict[k]
                if isinstance(val, dict):
                    new_queue[k] = True
                else:
                    new_queue[k] = val

            for k in flag_keys:
                if k in temp_queue:
                    new_queue[k] = temp_queue[k]

            pprint(new_queue, sort_dicts=False)
            print("\n")

            if leftovers:
                printing.print_green(leftovers)
                print("\n")


        testReg.clean_children()
        #for item in testReg.instances:
        #    print_ordered_vars(item)


        def indexed_view(included=None, excluded=None):

            def clarify(group):
                if isinstance(group, set|list|tuple):
                    for flag_name in group:
                        if flag_name not in flag_keys:
                            print(f"Attribute name {flag_name} not in flag_keys. Consider adding it.")


    def get_types_from_flags(itemname=""):

### This whole thing is so abysmally messy. Too tired to see why it's not working so I'm just throwing shit at the wall in case it fixes it. Going to have to stop and come back tomorrow.

        renames = {}

        pick_item = "scroll"

        all_flags_in_type_default = testing_t_defaults_against_item_defs(per_item=False, item_name="scroll")
        flags_dict = testing_t_defaults_against_item_defs(per_item=True, item_name="scroll")
        new_dict = {}
        for item, item_dict in flags_dict.items():
            if pick_item:
                if item != pick_item:
                    continue
            item_types = set()
            new_dict[item] = {"exceptions": {}}
            for flag in item_dict.keys():
                test, success = check_flag(item_types, flag)
                if test:
                    if isinstance(test, set):
                        item_types = test
                    elif isinstance(test, str):
                        item_types.add(test)
                if success:
                    new_dict[item]["exceptions"].update({flag: item_dict[flag]})
                if not success:
                    if renames.get(flag):
                        print(f"renames.get({flag}): {renames.get(flag)}")
                        item_types, success = check_flag(item_types, renames.get(flag))
                        print(f"Renames test: {item_types}, {success}")
                        if success:
                            item_type, success = check_flag(item_types, renames.get(flag), get_single=True)
                            print(f"flag: ::: {flag}")
                            if not item_dict.get(flag):
                                item = type_defaults[item_type].get(flag)
                                print(f"val: ::: {item}")
                            else:
                                item = item_dict.get(flag)
                                print(f"val: ::: {item}")
                            print(f"item_dict.get({renames.get(flag)}): {item_dict.get(flag)}")
                            new_dict[item][renames.get(flag)] = item_dict.get(flag)
                        if not success:
                            print(f"Flag not in all flags in default_types: {flag}")
                    else:
                        new_dict[item][flag] = item_dict[flag]
            #print(f"Item type: {type(item)}, val type: {type(item_dict)}")
            new_dict[item]["item_type"] = item_types

            print(f"Item: {item}, item_types: {item_types}")
            # end with this:

            inst = testReg.new_item_from_item_defs(item, new_dict)
            print(f"INST: {inst}")
            testReg.confirmed_items[item] = inst

        return pick_item

    #pick_item = get_types_from_flags()



    def add_confirms():

        print(f"testReg.confirmed_items: {testReg.confirmed_items}")
        print(f"testReg.temp_items: {testReg.temp_items}")
        if testReg.confirmed_items or testReg.updated:
            printing.print_red("The following item(s) have been confirmed for future use:")

            test_generated_items = True
            if testReg.confirmed_items:
                print(f"There are confirmed items: {testReg.confirmed_items}")
                for item in testReg.confirmed_items:
                    if test_generated_items:
                        print(f"Item name: {item}")
                        printing.print_red("If you want to confirm them as permanent items, please type 'yes' after the item data is printed.", invert=True)
                        printing.print_green(text=f"Item data: {vars(testReg.confirmed_items[item])}",  invert=True)

                        test = input()
                        if test.lower() in ("y", "yes"):
                            print("Item confirmed. Will add this to the permanent document.")
                            testReg.add_to_gen_items(testReg.confirmed_items[item])
                        else:
                            continue

            if testReg.updated:
                for inst in testReg.updated:
                    testReg.add_to_gen_items(inst) # currently only does one at a time, would be better to batch it internally. Tomorrow.

    #add_confirms()

    def edit_dict(named_item=""):

        with open(gen_items_file, 'r') as file:
            data = json.load(file)

        print("Do you want to change a particular field?")
        printing.print_blue(f"Fields: {all_flags_in_type_default}", invert=True)
        use_dict_vals = False
        limited_field = set()
        no_ask = False

        print("Enter the field name, or nothing to continue with all fields.\n")
        test=input()
        if test != "":
            if " " in test:
                test_parts = test.split(" ")
                for i in test_parts:
                    if i != None:
                        limited_field.add(i)
            else:
                limited_field.add(test)
            print(f"Fields limited to {limited_field}\n")

        print("Do you want to retrieve dict values? Enter anything to confirm, else nothing")
        test=input()
        if test != "":
            from item_definitions import item_defs_dict
            use_dict_vals = True
        else:
            test=None

        for key, entry in data.items():

            update_dict=False

            if named_item:
                if key != named_item:
                    continue

            printing.printkind(key)

            def test_input(entry, pop_me, header, item, input_str):

                item = str(item)

                if header == "item_size":
                    from item_definitions import container_limit_sizes
                    print(f"Size options: {container_limit_sizes}")

                if input_str == header:
                    pop_me.add(header)

                print(f"Is `{input_str}` what you want to replace `{item}` with? Enter 'no' to cancel, or enter to accept change.")
                while True:
                    new_test=input()
                    if new_test == "" or new_test in new_test in ("yes", "y"):
                        entry[header] = input_str
                        altered = True
                        break
                    if new_test in ("no", "n"):
                        altered = False
                        break
                    else:
                        print("Enter something else, or nothing to cancel and continue.")

                return pop_me, altered

            def get_from_dict(key, header, ):

                if item_defs_dict.get(key):
                    if item_defs_dict[key].get(header):
                        dict_val = item_defs_dict[key][header]
                        print(f"Do you want to replace \033[32m{entry[header]}\033[0m with \033[33m{dict_val}\033[0m?")
                        test = input()
                        if test in ("y", "yes"):
                            entry[header] = dict_val
                            altered = True
                            return altered

            def cleanup(pop_me):
                if pop_me:
                    for header in pop_me:
                        entry.pop(header)

            pop_me = set()

            for header, item in entry.items():
                if limited_field:
                    if header not in limited_field:
                        continue

                print(f"HEADER: {header} / ITEM: {item}")
                if use_dict_vals:
                    print()
                    altered = get_from_dict(key, header)
                    if altered:
                        update_dict=True

                else:
                    print()
                    print(f"Do you want to change {assign_colour(f"`{header}`: `{item}`", "location")}? Type 'remove' to remove the key {header}, or your desired change to `{item}`. Enter nothing to skip. Enter 'dict' to fetch the entry from item_defs. Enter 'end' to end now.")

                    test=input()
                    if test == "":
                        continue
                    elif test == "dict":
                        altered = get_from_dict(key, header)
                    elif test == "end":
                        break
                    else:
                        pop_me, altered = test_input(entry, pop_me, header, item, test)
                        print("entry[header]: ", entry[header])

                    if altered:
                        update_dict=True

                    if header in ("starting_location", "current_loc", "id", "contained_in", "started_contained_in", "container", "dupe", "fragile"):
                        pop_me.add(header)
                    elif isinstance(item, set):
                        entry[header] = str(item)
                    elif isinstance(item, ItemInstance):
                        pop_me.add(header)

                    if header in ("is_key", "can_pick_up", 'is_charged', "can_be_locked", 'is_locked') and entry[header] == None:
                        entry[header] = True
                    elif header == "description" and entry[header] == "none yet":
                        if "mag" in key:
                            key = key.replace("mag", "magazine")
                        entry[header] = f"It's a {key}"


            cleanup(pop_me)

            if update_dict and not no_ask:
                print(f"Updated dict: {entry}")
                print("\n Do you want to continue? Enter 'no' to stop or nothing to continue.")
                test=input()
                if test.lower() in ("n", "no"):
                    break
                print("Do you want me to stop asking?")
                test=input()
                if test in ("y", "yes"):
                    no_ask=True

        if update_dict:
            print("Write to file now?")
            test = input()
            if test in ("yes", "y"):
                with open(gen_items_file, 'w') as file:
                    json.dump(data, file, indent=2)
        else:
            print("No changes to update. Ending.")

    #edit_dict()

    def add_gen_to_main(): # Will now (optionally) clear gen_items.
        items_main = "dynamic_data/items_main.json"
        to_add = set()
        to_delete = set()
        with open(items_main, 'r') as main_file:
            main_data = json.load(main_file)
        with open(gen_items_file, 'r') as file:
            data = json.load(file)

        add_all_new = False
        print("Do you want to automatically add any new items?")
        test = input()
        if test == "y":
            add_all_new = True

        #for loc in data:
        for item in data:
            if main_data.get(item):
                if main_data[item] == data[item]:
                    print(f"Item `{item}`is identical to that in main. Do you want to remove it from gen_items?")
                    test = input()
                    if test in ("yes", "y"):
                        to_delete.add(item)
                else:
                    print(f"Item `{item}` already in main dict. Replace?\n Existing in main: {main_data[item]}, Gen version: {data[item]}")
                    test = input()
                    if test == "y":
                        to_add.add(item)
                    print("Do you want to remove the item from gen_items?")
                    test = input()
                    if test == "y":
                        to_delete.add(item)
            else:
                if add_all_new:
                    to_add.add(item)
                else:
                    print(f"Item `{item}` not in main. Enter 'y' to add it.")
                    test = input()
                    if test == "y":
                        to_add.add(item)

        if to_add or to_delete:
            if to_add:
                for item_name in to_add:
                    main_data[item_name] = data[item_name]
                    to_add.add(item)

                print(f"About to add ({to_add}) to the main file. Enter anything to abort:")
                test = input()
                if test == "" or test == None:
                    with open(items_main, 'w') as main_file:
                        json.dump(main_data, main_file, indent=2)

                print("Do you want to remove these items from the gen_items file?")
                test = input()
                if test in ("y", "yes"):
                    for item_name in to_add:
                        data.pop(item_name)
                with open(gen_items_file, 'w') as file:
                    json.dump(data, file, indent=2)

            if to_delete:
                for item_name in to_delete:
                    if data.get(item_name):
                        data.pop(item_name)
                with open(gen_items_file, 'w') as file:
                    json.dump(data, file, indent=2)
        else:
            print("Nothing to add, all entries in main dict and/or no changes made.")
    """

def get_all_default_flags(item):

    item_def_flags = []
    default_flags = set()
    types = set()

    new_dict = {}

    item_def = testReg.item_defs.get(item)
    #print(f"\nitem: {item}")
    #for tag in item_def.keys():
    #    item_def_flags.append(tag)
    #print(f"total_flags: {item_def_flags}")


    from item_dict_gen import item_type_descriptions

    description_dict = {}

    from itemRegistry import type_defaults
    if item_def.get("item_type"):
        attr = item_def.get("item_type")
        if isinstance(attr, str):
            if "{" in attr:
                _, type_item = attr.split("{")
                type_item, _ = type_item.split("}")
                type_item = type_item.replace("'", "")
                parts = type_item.split(", ")
                #self.item_type = self.item_type | set(parts)
                for part in parts:
                    if part != None:
                        types.add(part)
            else:
                print(f"Is string but no", r"'{'", " ?")
            item_def["item_type"] = types

        for def_type in types:
            flags = type_defaults.get(def_type)

            for flag, val in flags.items():
                if flag in item_def:
                    continue
                item_def[flag] = val


            if item_type_descriptions.get(def_type):
                description_dict = item_type_descriptions[def_type]
            
            if item_def.get("descriptions"):
                for entry in description_dict.keys():
                    if entry not in item_def["descriptions"]:
                        item_def["descriptions"].update({entry: ""})
            else:
                item_def["descriptions"] = description_dict

    #print(f"item_def: {item_def}")

def flags_not_in_default(item):

    ignored_flags = ["nicename", "item_type", "descriptions", "nicenames"]
    all_flags = set()
    for def_type in testReg.item_defs[item].get("item_type"):
        flags = set(type_defaults.get(def_type))
        if not flags:
            print(f"{def_type} not in type_defaults.")
            exit()
        all_flags = all_flags | flags
    #print(f"FLAGS: {all_flags}")

    flags_to_check = list()

    for attr in list(testReg.item_defs[item]):
        if attr not in ignored_flags and attr not in all_flags:
            if not testReg.item_defs[item][attr]:
                testReg.item_defs[item].pop(attr)
            else:
                flags_to_check.append(attr)

    flags_to_really_check = set()
    if flags_to_check:
        for flag in flags_to_check:
            if flag == "loot_type":
                if testReg.item_defs[item][flag] == "starting_loot":
                    testReg.item_defs[item]["item_type"].add("starting_loot")
                else:
                    testReg.item_defs[item]["item_type"].add("random_loot")
            elif flag == "key" and testReg.item_defs[item].get('requires_key') == False:
                testReg.item_defs[item]["requires_key"] = testReg.item_defs[item]["key"]
                testReg.item_defs[item].pop("key")

            elif flag == "has_multiple_instances":
                testReg.item_defs[item]["item_type"].add("is_cluster")

            elif flag == "description" and not hasattr(testReg.item_defs[item], "descriptions"):
                testReg.item_defs[item]["descriptions"] = {"generic": f"{testReg.item_defs[item]["description"]}"}
                testReg.item_defs[item].pop("description")
            elif flag == "flammable":
                testReg.item_defs[item]["item_type"].add("flammable")
            elif flag == "is_key_to":
                testReg.item_defs[item]["item_type"].add("key")
            else:
                testReg.flags_to_amend.add(flag)
                #flags_to_really_check.add(flag)
    #for flag in all_flags:
    #    if flag not in item_defs:
    #        print(f"Flag {flag} not in item defs for `{item}`, despite being in item type defaults.")
    #if flags_to_really_check:
        #print(f"\n\nFlags to check in {item} defs:\n{flags_to_really_check}\n{testReg.item_defs[item]}")

def update_ref_file(json_file):

    import json
    with open(json_file, 'w') as file:
        json.dump(testReg.item_defs, file, indent=2)

json_file = r"dynamic_data\temp_defs.json"

def serialise_item_defs():
    for item, field in testReg.item_defs.items():
        for k, v in field.items():
            if isinstance(v, set):
                testReg.item_defs[item][k] = list(v)


def order_dict():
    testReg.item_defs = dict(sorted(testReg.item_defs.items()))


def fix_flags():
    for item in testReg.item_defs:
        get_all_default_flags(item)

        flags_not_in_default(item)

generated_file = r"ref_files\generated_items.json"
order_dict()
update_ref_file(generated_file)

fix_flags()



serialise_item_defs()
order_dict()
update_ref_file(json_file)
print(testReg.flags_to_amend)
