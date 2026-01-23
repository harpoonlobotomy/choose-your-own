import uuid
from pprint import pprint
from itemRegistry import ItemInstance
from item_definitions import item_defs_dict
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
type_defaults = { # gently ordered - will overwrite earlier attrs with later ones (eg 'is horizontal surface' for flooring with overwrite 'static''s.)
    "standard": {},
    "static": {"can_examine": False, "breakable": False},
    "all_items": {"starting_location": None, "current_loc": None, "alt_names": {}, "is_hidden": False},
    "container": {"is_open": False, "can_be_opened": True, "can_be_closed": True, "can_be_locked": True, "is_locked": True, "requires_key": False, 'starting_children': None, 'container_limits': 4, "name_no_children": None, "description_no_children": None},
    "key": {"is_key": True},
    "can_pick_up": {"can_pick_up": True, "item_size": 0, "started_contained_in": None, "contained_in": None},
    "event": {"event": None, "event_type": "item_triggered", "event_key": None},
    "trigger": {"trigger_type": "plot_advance", "trigger_target": None, "is_exhausted": False},
    "flooring": {"is_horizontal_surface": True},
    "wall": {"is_vertical_surface": True},
    "food_drink": {"can_consume": True, "can_spoil": True, "is_safe": True, "effect": None},
    "fragile": {"broken_name": None, "flammable": False, "can_break": True},
    "electronics": {"can_be_charged": True, "is_charged": False, "takes_batteries": False, "has_batteries": False},
    "books_paper": {'print_on_investigate': True, 'flammable': True, 'can_read': True},

    #{"special_traits: set("dirty", "wet", "panacea", "dupe", "weird", "can_combine")}, # aka random attr storage I'm not using yet
    #"exterior": {"is_interior": False} ## Can be set scene-wide, so 'all parts of 'graveyard east' are exterior unless otherwise mentioned'. (I say 'can', I mean 'will be when I set it up')
}## Removed all the interior dicts. They're not necessary and will actually get in the way - having the type defaults exposed is far more beneficial.

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
            skip_tags = ("contained_in", "current_loc", "started_contained_in", "starting_location")
            for tag in type_tags:
                if not tag in skip_tags and not item_defs_dict[item].get(tag):
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

check_all_flags_present()

def testing_t_defaults_against_item_defs(per_item=True, item_name=""):


    print(f"all flags in type_default: {all_flags_in_type_default}")

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

#testing_t_defaults_against_item_defs(per_item=True)

size = "item_size"
box_desc = "It's a box. Boxy box."

descriptions = {
    "box": box_desc,
    "locked box": box_desc,
    "cabinet": "A cabinet with something weird about it.",
    "elephant": "Big and grey and stompy."
}

test_items = {
    "everything": {"item_type": set((static, container, can_pick_up, event, trigger, "flooring"))},
    "earring": {"item_type": set((can_pick_up,)), "exceptions": {"started_contained_in": "box"}},
    "box": {"item_type": set((container, can_pick_up)), "exceptions": {"can_be_locked": False}},
    #"gold key": {"item_type": set(("key",)), "exceptions": {"starting_location": "some other place"}},
    "locked box": {"item_type": set((container, can_pick_up)), "exceptions": {"requires_key": "gold key", "starting_location": "east graveyard"}},
    "cabinet": {"item_type": set((static, event)), "exceptions": {"can_examine": True, "event_key": "box", "trigger_target": "box"}},
    "wall": {"item_type": set((static,)), "exceptions": {"is_vertical_surface": True}},
    "elephant": {"item_type": set((standard,)), "exceptions": {size:10}},
    "stone ground": {"item_type": set((static, "flooring"))}
}

locations = {"Graveyard": {"east": {"items": ["stone ground", "grave"]}, "west": {"items": ["stone ground"]}, "north": {"items": ["stone ground"]}, "south": {"items": ["stone ground", "headstones"]}},
            "OtherPlace": {"east": {"items": ["everything", "grandfather clock"]}, "west": {"items": ["birdbath"]}, "north": {"items": "merry-go-round"}, "south": {"items": "rocking chair"}},
            "Mermaid Grotto": {"east": {"items": ["sandy ground"]}, "west": {"items": ["sandy ground"]}, "north": {"items": ["sandy ground"]}, "south": {"items": ["sandy ground"]}}
            }

flag_keys = ("id", "name", "description", "current_loc", "is_open", "can_be_closed", "can_be_locked", "is_locked", "requires_key", "is_key", "can_pick_up", "can_examine", "breakable", "contained_in", "item_size", "item_type", "is_horizontal_surface", "is_vertical_surface", "event", "event_type", "item_triggered", "event_key", "trigger_target", "trigger_type", "plot_advance", "is_exhausted", "starting_location", "started_contained_in", "extra")

use_generated = False
 ## just a shortcut for a min while I test TODO remember to delete later
gen_items = {}


        #generated_items.test_items[key] = (entry)
        #print(f"Temp items: {generated_items.test_items}")



class tempDatastore:

    def __init__(self):
        self.temp_items = set()
        self.confirmed_items = {}
        self.updated = set()

testReg = tempDatastore()
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

    def get_loc_items(loc, cardinal=None):
        """
        Now currently, items are stored and they tell env_data where they live. It does make more sense to place them via location not via the item itself.

        I think I want to have a separate dict for it, like I have here in my test setup. Otherwise I have to double-back through all the items anyway to add instances
        """
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

        renames = {
            'description_no_children': "description_no_children",
            'name_children_removed': "name_no_children" ,
            'needs_key_to_lock': "requires_key",
            'can_lock': "can_be_locked",
            'is_closed': "is_open",
            'can_open': "can_be_opened"
        }

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

    #add_gen_to_main()
"""
#def items_in(container=None, *, open=None, locked=None):
#    for item in self.by_location[graveyard_east]:
#        if container is not None and item.container is not container:
#            continue
#        if open is not None and item.is_open != open:
#            continue
#        if locked is not None and item.is_locked != locked:
#            continue
#        yield item
#
#for i in items_in(container=True, open=True):
#    ...
#
"""
