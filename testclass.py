# Rename this to item_generation or something.

## Changing it so this class is just for generating new items. So perhaps the item dict is generated through here, checked, and the dict is sent over to itemRegistry?

# Or maybe add generate the items here entirely. Really not sure.

# Need to change it here a little. Instead of creating them one at a time, I want to collect the item_defs items, gen_items items, then batch create them. Maybe all item defs, all gen items? That doesn't matter so much I guess.

# I need to figure out where the loc items are going to be stored. Separate file or env_data.
# Well I guess there should to be two lists. One for the cardinal loc descriptions in env_data, and a separate list for simply added items. I think maybe that's the best way of doing it.

import uuid
from pprint import pprint
import printing

standard = "standard"
static = "static"
can_pick_up = "can_pick_up"
container = "container"
event = "event"
trigger = "trigger"

json_to_edit = "dynamic_data/generated_items.json"
json_primary = "dynamic_data/items_main.json"


CARDINALS = ["north", "east", "south", "west"]

import json

with open(json_primary, 'r') as file:
    item_defs = json.load(file)

def gen_print(text_input = ""):
    print_generated = False
    if print_generated:
        print(text_input)

def do_print(text_input = ""):
    print_things = False
    if print_things:
        print(text_input)

## Move these dicts to a json. Use this class to store those dicts + act from them.

type_defaults = { # gently ordered - will overwrite earlier attrs with later ones (eg 'is horizontal surface' for flooring with overwrite 'static''s.)
    "standard": {},
    "static": {"can_examine": False, "breakable": False},
    "all_items": {"starting_location": None, "current_loc": None, "alt_names": {}, "is_hidden": False},
    "container": {"is_open": False, "can_be_opened": True, "can_be_closed": True, "can_be_locked": True, "is_locked": True, "requires_key": False, 'starting_children': None, 'container_limits': 4, "name_no_children": None, "description_no_children": None},
    "key": {"is_key": True},
    "can_pick_up": {"can_pick_up": True, "item_size": 0, "started_contained_in": None, "contained_in": None},
    "event": {"event": None, "event_type": "item_triggered", "event_key": None, "event_item": None},
    "trigger": {"trigger_type": "plot_advance", "trigger_target": None, "is_exhausted": False},
    "flooring": {"is_horizontal_surface": True},
    "wall": {"is_vertical_surface": True},
    "food_drink": {"can_consume": True, "can_spoil": True, "is_safe": True, "effect": None},
    "fragile": {"broken_name": None, "flammable": False, "can_break": True},
    "electronics": {"can_be_charged": True, "is_charged": False, "takes_batteries": False, "has_batteries": False},
    "books_paper": {'print_on_investigate': True, 'flammable': True, 'can_read': True},
    "can_speak" : {'can_speak': True, 'speaks_common': True},
    "door_window": {"is_open": False, "can_be_opened": True, "can_be_closed": True, "can_be_locked": True, "is_locked": True, "requires_key": False}

    #{"special_traits: set("dirty", "wet", "panacea", "dupe", "weird", "can_combine")}, # aka random attr storage I'm not using yet
    #"exterior": {"is_interior": False} ## Can be set scene-wide, so 'all parts of 'graveyard east' are exterior unless otherwise mentioned'. (I say 'can', I mean 'will be when I set it up')
}## Removed all the interior dicts. They're not necessary and will actually get in the way - having the type defaults exposed is far more beneficial.

#location_defaults = { ## Oh, actually: use this `"Graveyard": {"east": {"items":  and add 'loc_tags' : ["dirty"]}` there. "locations" dict.
#    "graveyard": {"all_cardinals": ["dirty"]} ## to add tags per location. Won't be relevant often, but sometimes.
#}

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

def testing_t_defaults_against_item_defs(per_item=True, item_name=""):

    #print(f"all flags in type_default: {all_flags_in_type_default}")

    def_flags_in_t_def = set()
    all_def_flags = set()
    collected_per_item = {}
    from item_definitions import item_defs_dict
    for item, val in item_defs_dict.items():
        if item_name:
            if item != item_name:
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

descriptions = {
    "box": "It's a box. Boxy box.",
    "elephant": "Big and grey and stompy."
}

test_items = {
    #"everything": {"item_type": set((static, container, can_pick_up, event, trigger, "flooring"))},
    #"box": {"item_type": set((container, can_pick_up)), "exceptions": {"can_be_locked": False}},
    #"wall": {"item_type": set((static,)), "exceptions": {"is_vertical_surface": True}},
    #"elephant": {"item_type": set((standard,)), "exceptions": {size:10}},
    #"stone ground": {"item_type": set((static, "flooring"))}
}

#locations = {"Graveyard": {"east": {"items": ["stone ground", "grave", "dessicated skeleton"]}, "west": {"items": ["raven", "stone ground"]}, "north": {"items": ["stone ground"]}, "south": {"items": ["stone ground", "headstone"]}},
#            "OtherPlace": {"east": {"items": ["grandfather clock"]}, "west": {"items": ["birdbath"]}, "north": {"items": ["merry-go-round", "empty plastic cup"]}, "south": {"items": ["rocking chair"]}},
#            "Mermaid Grotto": {"east": {"items": ["comb", "trident", "wardrobe", "cabinet", "sandy ground"]}, "west": {"items": ["sandy ground"]}, "north": {"items": ["sandy ground"]}, "south": {"items": ["sandy ground"]}}
#            }
#
flag_keys = ("id", "name", "description", "current_loc", "is_open", "can_be_closed", "can_be_locked", "is_locked", "requires_key", "is_key", "can_pick_up", "can_examine", "breakable", "contained_in", "item_size", "item_type", "is_horizontal_surface", "is_vertical_surface", "event", "event_type", "item_triggered", "event_key", "trigger_target", "trigger_type", "plot_advance", "is_exhausted", "starting_location", "started_contained_in", "extra")

use_generated = False

def use_generated_items(input_=None):

    altered = False
    with open(json_to_edit, 'r') as file:
        gen_items = json.load(file)

    if not gen_items or gen_items == {}:
        return

    data_keys = list(gen_items)

    if input_ == None:
        keys = data_keys
    elif isinstance(input_, str):
        if gen_items.get(input_):
            print(f"Item found in generated_items: {gen_items.get(input_)}")
            entry = {}
            entry[input_] = gen_items[input_]
            return entry
        else:
            return None

    elif isinstance(input_, set|list|tuple):
        keys = set(i for i in input_)
    elif isinstance(input_, dict):
        keys = set(input_)

        for key in keys:
            if key in data_keys:
                print(f"JSON entry: \n{gen_items[key]}")
                print(f"Memory entry: \n{input_[key]}")
                print("Type 'm' to update the JSON with the memory entry, otherwise the JSON will be kept as-is.")
                test=input()
                if test == "m":
                    gen_items[key] = input_[key]
                    altered = True

    if altered:
        printing.print_red(f"Data keys: {data_keys}")
        printing.print_red(f"keys: {keys}")

        with open(json_to_edit, 'w') as file:
            json.dump(gen_items, file, indent=2)

    return gen_items

class testInstances:

    def clean_item_types(self, attr):

        if isinstance(attr, str):
            if "{" in attr:
                _, type_item = attr.split("{")
                type_item, _ = type_item.split("}")
                type_item = type_item.replace("'", "")
                parts = type_item.split(", ")
                self.item_type = self.item_type | set(parts)
                #for part in parts:
                #    if part != None:
                #        self.item_type.add(part)
            else:
                self.item_type.add(attr)

        elif isinstance(attr, set|list|tuple):
            do_print(f"ITEM set/list/tuple: {attr}")
            self.item_type = self.item_type | set(attr)
            #for item_type in attr:
            #    self.item_type.add(item_type)

    def get_item_types(self, attr):

        if attr.get("item_type"):
            self.clean_item_types(attr["item_type"])

        if test_items.get(self.name):
            item_types = test_items[self.name].get("item_type")
            self.clean_item_types(item_types)

        if "all_items" not in self.item_type:
            self.item_type.add("all_items")

    def __init__(self, definition_key, attr):

        self.id = str(uuid.uuid4())
        self.name = definition_key
        self.nicename = attr.get("nicename")
        if not self.nicename:
            if attr.get("name"):
                if attr.get("name").startswith("a "):
                    self.nicename = attr.get("name")
                else:
                    self.nicename = "a " + attr.get("name")
            else:
                if definition_key.startswith("a "):
                    self.nicename = definition_key
                else:
                    self.nicename = "a " + definition_key

        self.description = attr.get("description")

        if not self.description or self.description == None:
            test = item_defs.get(definition_key)
            if test:
                self.description = test
            else:
                test = use_generated_items(definition_key)
                if test:
                    self.description = test
                else:
                    test = descriptions.get(definition_key)
                    if test:
                        self.description = test

        if not self.description:
            printing.print_yellow(f"attr.get('description'): {attr.get('description')}\n  Item `{definition_key}` does not have a description, do you want to write one?. Enter it here, or hit enter to cancel.")
            while True:
                test=input()
                if test and test != "":
                    print("Is this correct? 'y' to accept this description, 'n' to try again or anything else to cancel.")
                    trial = test
                    new_test = input()
                    if new_test.lower() == "y":
                        self.description = trial
                        testReg.updated.add(self.id)
                        break
                    elif new_test.lower() == "n":
                        continue
                    else:
                        break
                else:
                    break

        #self.starting_location = None ## TODO change to current_loc once integrated to main script.
        #self.current_loc = None # TODO maybe change to just 'self.loc' and assume 'current'?

        self.item_type = set()
        self.get_item_types(attr)

        for item in attr:
            if item != "exceptions":
                if hasattr(self, item) and getattr(self, item) != None:
                    continue
                elif not hasattr(self, item) and attr[item] != None:
                    setattr(self, item, attr[item])

                elif hasattr(self, item) and getattr(self, item) == None:
                    if attr[item] != None:
                        setattr(self, item, attr[item])
                else:
                    setattr(self, item, None)

        if attr.get("exceptions"):
            for flag in attr.get("exceptions"):
                if isinstance(flag, dict):
                    for sub_flag in type_defaults[item_type][flag]:
                        if attr["exceptions"][flag].get(sub_flag) == None and type_defaults[item_type][flag].get(sub_flag) != None:
                            continue
                        if sub_flag in attr["exceptions"]: # does it ever nest this deeply anymore? Possibly. need to test.
                            setattr(self, sub_flag, attr["exceptions"][sub_flag])
                        else:
                            setattr(self, sub_flag, type_defaults[item_type][flag][sub_flag])
                else:
                    if attr["exceptions"].get(flag) == None and type_defaults[item_type].get(flag) != None:
                        continue
                    setattr(self, flag, attr["exceptions"][flag])

        for item_type in self.item_type:
            print(f"item type: {item_type}")
            for flag in type_defaults.get(item_type):
                if not hasattr(self, flag):
                    setattr(self, flag, type_defaults[item_type][flag])

        #if self.starting_location:
        #    self.current_loc = self.starting_location

        #if hasattr(self, "started_contained_in"):
        #    self.contained_in = self.started_contained_in

        if hasattr(self, "starting_children"):
            self.children = self.starting_children

        self.colour = None
        self.verb_actions = set() ## TODO: Will need to copy this mostly verbatim from itemRegistry.

        if hasattr(self, "print_on_investigate"):
            self.verb_actions.add("print_on_investigate")
            from item_definitions import detail_data
            details = self.name + "_details"
            details = details.replace(" ", "_")
            details_data = detail_data.get(details)
            if details_data:
                self.description_detailed = details_data
            else:
                print(f"No detailed description found for {self.name}, though it's supposed to be readable.")

    def __repr__(self):
        return f"<TestInstances {self.name} ({self.id})>"


class testRegistry:
    def __init__(self):

        self.instances = set()
        self.by_name = {}        # definition_key -> set of instances
        self.by_id = {}
        self.by_location = {}    # cardinalinst (when implemented, str for now), > instances
        self.temp_items = set()
        self.updated = set()

    def init_single(self, item_name, item_entry):
        do_print(f"[init_single] ITEM NAME: {item_name}")
        do_print(f"[init_single] ITEM ENTRY: {item_entry}")
        inst = testInstances(item_name, item_entry)
        self.instances.add(inst)
        self.by_name[inst.name] = inst
        self.by_id[inst.id] = inst

        return inst


    def init_items(self, item_data, name=None):

        do_print(f"ITEM_DATA START: {item_data}")
        do_print(f"init_items start: NAME: `{name}`")
        inst=None
        if isinstance(item_data, dict):
            if item_data.get("name"):
                do_print(f"init items DICT alternate, name: {name}, entry: {item_data}")
                if name:
                    item_name = name
                inst = self.init_single(item_name, item_data)

            else:
                do_print(f"init items DICT, name: {name}")
                if name:
                    if item_data.get(name):
                        item_entry = item_data[name]
                        item_name = name
                        inst = self.init_single(item_name, item_entry)
                        return inst

                for item_name, item_entry in item_data.items():
                    inst = self.init_single(item_name, item_entry)

        if not item_data and name:
            item_data = name

        if isinstance(item_data, str):
            item_entry = {}
            do_print(f"ITEM_DATA STR: {item_data}")
            do_print(f"init_items STR: name: {name}")

            if item_defs.get(item_data):
                do_print("from item defs")
                item_entry[item_data] = item_defs[item_data]
            elif test_items.get(item_data):
                do_print("from test items")
                item_entry[item_data] = test_items[item_data]
            elif use_generated_items(item_data):
                item_entry[item_data] = use_generated_items(item_data)
            else:
                do_print("item_type: [static]")
                item_entry[item_data] = ({"item_type": [static]})
            inst = self.init_single(item_data, item_entry[item_data])
            return inst

        return inst


    def new_item_from_str(self, item_name:str, input_str:str=None, loc_cardinal=None, partial_dict=None, in_container = False)->str|testInstances:
        if not input_str:
            print("\n")
            printing.print_green(f"Options: {list(type_defaults)}", invert=True)
            print(f"Please enter the default_types you want to assign to `{item_name}` (eg ' key, can_pick_up, fragile ' )")
            input_str = input()

        if not isinstance(input_str, str):
            print(f"new_item_from_str requires a string input, not {type(input_str)}")
            return


        if " " in input_str.strip():
            input_str = input_str.replace(",", "")
            parts = input_str.strip().split(" ")
            parts = set(i for i in parts if i != None and i in list(type_defaults))
            if len(parts) > 1:
                gen_print(f"Parts len >1 : {parts}, type: {type(parts)}")
                new_str = set(parts)
            else:
                new_str = set([parts])

        elif input_str in list(type_defaults):
            gen_print(f"Input str in type_defaults: {input_str}, type: {type(input_str)}")
            new_str = set([input_str])

        else:
            gen_print(f"No valid input [`{input_str}`]. Defaulting to item_type = ['static']")
            new_str = set(["static"])

        if not loc_cardinal:
            loc_cardinal = "graveyard north"

        print(f"loc_cardinal: {loc_cardinal}")

        if partial_dict and isinstance(partial_dict, dict):
            if partial_dict.get(item_name):
                new_item_dict[item_name] = partial_dict[item_name]
            elif partial_dict.get("name"):
                new_item_dict[item_name] = partial_dict
            else:
                print(f"Partial dict: Not sure how to use this format: {partial_dict}")
                exit()

            new_item_dict[item_name].update({"item_type": new_str})

        else:
            new_item_dict = {}
            new_item_dict[item_name] = ({"item_type": new_str})

        print(f"new_item_dict[item_name]: {new_item_dict[item_name]}")
        if in_container: ## testing this out.
            loc_cardinal = None
            "started_contained_in"
            new_item_dict[item_name].update({"started_contained_in": in_container}) # might have to be id/name? Not sure if instance will work here.



        new_item_dict[item_name]["starting_location"] = loc_cardinal

        print(f"new_item_from_str: \n {new_item_dict}, {item_name}\n\n")
        inst = self.init_items(new_item_dict, item_name)
        print(f"Inst after self.init_items(): {inst}, type: {type(inst)}")
        self.instances.add(inst)
        self.temp_items.add(inst)

        printing.print_green(text=vars(inst), bg=False, invert=True)
        return inst

    def add_to_gen_items(self, instance):
        print(f"Adding to {json_to_edit}: {instance.name}")

        key = instance.name
        entry = vars(instance)
        printing.printkind(key)
        printing.printkind(entry)

        pop_me = set()
        for header, item in entry.items():
            if header in ("starting_location", "current_loc", "id", "contained_in", "started_contained_in"): # listing the container variants because idk why the 'isinstance' below isn't working yet.
                pop_me.add(header)
            elif isinstance(item, set):
                entry[header] = str(item)
            elif isinstance(item, testInstances):
                pop_me.add(header)

        if pop_me:
            for header in pop_me:
                entry.pop(header)

        #print(f"Popped dict: {entry}")

        with open(json_to_edit, 'r') as file:
            data = json.load(file)
            data[key] = entry

        with open(json_to_edit, 'w') as file:
            json.dump(data, file, indent=2)

        print(f"\nEntry for {key} written to {json_to_edit}.\n")


    def create_item_by_name(self, item_name) -> testInstances:

        item = item_defs.get(item_name)

        if item:
            gen_print(f"item_by_name: \n {item}, name: {item_name}\n\n")
            inst = self.init_single(item_name, item)
            if inst:
                gen_print(f"\nGENERATED from item_defs entry: {inst}\n")
                return inst
            else:
                print(f"Failed to generate {item_name} from item_defs")

        else:
            gen_entry = use_generated_items(item_name)
            if gen_entry:
                inst = self.init_items(gen_entry, item_name)
                if inst:
                    gen_print(f"\nGENERATED from generated_entry: {inst}\n")
                    return inst
                else:
                    print(f"Failed to generate {item_name} from test_items")
            elif test_items.get(item_name):
                gen_print(f"`{item_name}` found in test_items.")
                inst = self.init_items(test_items[item_name], item_name)
                if inst:
                    gen_print(f"\nGENERATED from test_items: {inst}\n")
                    return inst
                else:
                    print(f"Failed to generate {item_name} from test_items")

        gen_print(f"No generated entry for {item_name}; continuing.\n")

        printing.print_red(f"Nothing found for item name `{item_name}` in item_by_name.", invert=True)
        printing.print_red("Please enter the desired type-default key(s) to create a new instance of that type.", invert=True)
        printing.print_green(f"\nOptions: {list(type_defaults)}")
        printing.print_red("Entering nothing will skip this process and no instance wil be created.\n", invert=True)

        test = input()

        if test:
            instance = self.new_item_from_str(item_name, test)
            if instance and isinstance(instance, testInstances):
                gen_print(f"Adding `{item_name}` to generated_items.json")
                self.add_to_gen_items(instance)
                gen_print(f"Done; returning instance `{instance}` from create_item_by_name.")
                return instance


    def find_item_by_name(self, item_name, inventory=False, local=False) -> testInstances:

        if isinstance(item_name, testInstances):
            return item_name

        items = self.by_name.get(item_name)

        if items != None:

            if inventory:
                if isinstance(items, testInstances) and items in inventory: # because sometimes it returns a single item, not a set.
                    return items
                for item in inventory:
                    if item in items:
                        return item

            if local:
                if isinstance(items, testInstances) and items in local.items: # because sometimes it returns a single item, not a set.
                    return items
                # check items at current loc
                for item in local.items: #not really like this, add the proper code here later.
                    if item in items:
                        return item

            if not inventory and not local: # written like this so it fails if we were looking for local items.
                if isinstance(items, testInstances):
                    return items
            #elif items != None:
                #return items[0]
                # turning off the 'return items[0], because that's probably never what we're going to want.
        else:
            if not inventory and not local: # written like this so it fails if we were looking for local items. If I'm looking for 'suitcase' locally, it shouldn't invent it. Really maybe the lookup shouldn't link to creation at all. Yeah actually this is true. create should always create.
            # Maybe some kind of loaded register, so it generates items when a new location is accessed and only then. Not sure about that.
                self.create_item_by_name(item_name)


    def clean_children(self):

        target_flags = ("contained_in", "requires_key", "event_key", "trigger_target")

        def cleaning_loop():

            # applies instances to children/keys/etc.
            itemlist = frozenset(self.by_id)
            #print(f"Itemlist: {itemlist}")
            for item_id in itemlist:
                item = self.by_id.get(item_id)
                #print(f"item by id: {item}")
                if not item:
                    print(f"Failed to get instance by id in cleaning_loop for instance ({item_id}).")
                    exit() # for now just hard quit if this ever happens, it definitely shouldn't.
                ## Use the item_indexed lookup for this instead. This is just temporary.
                if hasattr(item, "contained_in") and getattr(item, "contained_in") not in (False, None):
                    gen_print(f"Create_item_by_name for contained_in: {item}")
                    target_obj = self.create_item_by_name(getattr(item, "contained_in"))
                    if target_obj:
                        if hasattr(item, "started_contained_in") and item.started_contained_in == item.contained_in:
                            item.started_contained_in = target_obj
                        item.contained_in = target_obj
                    else:
                        print(f"Missing an instance for `{item.name}`'s  `contained_in`: {getattr(item, 'contained_in')}")
                        exit()

                if hasattr(item, "starting_children") and item.starting_children != None: # Could probably tie this up in the above loop, and viable child should have a viable parent. I guess this enables me to add the either as either parent or child and have it found, rather than always having to add it to one in particular. Esp with the item gen, that's nice.
                    gen_print(f"Create_item_by_name for starting_children: {item}")
        # Except, if the child already exists as an itemdef/gen_item entry, then it gets created twice and alignment gets messy.

                    gen_print(f"Item: {item}, item.starting_children: {item.starting_children}")
                    instance_children = []
                    if isinstance(item.starting_children, list|set|tuple):
                        for child in item.starting_children:
                            gen_print(f"create_item_by_name: {child}")
                            target_obj = self.create_item_by_name(child)
                            gen_print(f"target object after create_item_by_name from list: {target_obj}")
                            if target_obj:
                                instance_children.append(target_obj)
                        if len(instance_children) == len(item.starting_children):
                            gen_print(f"All children found/created as instances: {instance_children}")
                            item.starting_children = instance_children
                        else:
                            gen_print(f"Not all children found/made as instances. Str list:\n   {item.starting_children}\nInstance list:\n    {instance_children}")
                            exit() # again, right now hard exit if this ever fails. Need to see why if it does.
            # Was going to do keys here too, but I don't think I will. Maybe do those at runtime, they're not as widely relevant as children so maybe just do that identification when looked for? Though having said that, that means I have to be aware of whenever they might be checked for... Yeah I should do it here actually.
                    elif isinstance(item.starting_children, str):
                        target_obj = self.create_item_by_name(item.starting_children)
                        gen_print(f"target object after create_item_by_name with str: {target_obj}")
                        if target_obj:
                            item.starting_children = list(target_obj)
                        else:
                            print(f"Failed to find child for {item}'s {item.starting_children} (from str).")
                            exit()

                if hasattr(item, "requires_key") and not isinstance(getattr(item, "requires_key"), bool):
                    target_obj = self.create_item_by_name(item.requires_key)
                    if target_obj:
                        item.requires_key = target_obj
                    else:
                        print(f"Failed to find key for {item}'s {item.requires_key}.")
                        exit()

        starting_count = len(self.instances)

        try:
            cleaning_loop()
        except Exception as E:
            print(f"Exception: {E}")

        if len(self.instances) == starting_count:
            print("Huh, count is the same. This may or may not matter; only really matters if you were expecting a new item to be dynamically generated.")


testReg = testRegistry()

def get_loc_items_dict(loc=None, cardinal=None):

    json_primary = "dynamic_data/items_main.json"
    with open(json_primary, 'r') as file:
        item_defs = json.load(file)

    loc_data_json = "loc_data.json"
    with open(loc_data_json, 'r') as file:
        loc_dict = json.load(file)

    loc_items_dict = {}

    def get_cardinal_items(loc, cardinal):

        gen_items = use_generated_items()

        def from_single_cardinal(loc, cardinal):

            if not loc_dict.get(loc.lower()):
                print(f"Location {loc} not in env_data.")
                return
            if loc_dict[loc.lower()].get(cardinal):

                if loc_dict[loc.lower()][cardinal].get("item_desc"):
                    for item in loc_dict[loc.lower()][cardinal]["item_desc"]:
                        loc_item = {}
                        skip_add = False
                        if item != "generic":
                            if item_defs.get(item):
                                gen_print(f"`{item}` found in item_defs.")
                                loc_item[item] = item_defs.get(item)
                                loc_item[item].setdefault("exceptions", {}).update({"starting_location": cardinal + " " + loc})
                                inst = testReg.init_single(item, loc_item[item])
                                gen_print(f"\nINST GENERATED (item_dict by_cardinal): {vars(inst)}\n")
                            else:
                                if gen_items.get(item):
                                    gen_print(f"`{item}` found in generated_items.")
                                    loc_item[item] = gen_items[item]
                                    gen_print(f"GEN ITEMS {item}: {gen_items[item]}")
                                    skip_add = True
                                elif test_items.get(item):
                                    gen_print(f"`{item}` found in test_items.")
                                    loc_item[item] = test_items[item]
                                else:
                                    gen_print(f"Item {item} not found in item_defs, generating from blank.")
                                    loc_item[item] = ({"item_type": [static]})
                                    inst = testReg.new_item_from_str(item_name=item, loc_cardinal=(loc + " " + cardinal))
                                    continue

                                loc_item[item].update({"starting_location": cardinal + " " + loc})
                                loc_items_dict[loc][cardinal][item] = loc_item[item]
                                inst = testReg.init_single(item, loc_item[item])
                                if not skip_add:
                                    testReg.temp_items.add(inst)

        if cardinal == None:
            for cardinal in CARDINALS:
                loc_items_dict[loc][cardinal] = {}
                from_single_cardinal(loc, cardinal)
        else:
            loc_items_dict[loc][cardinal] = {}
            from_single_cardinal(loc, cardinal)

    if loc == None:
        for loc in loc_dict:
            loc_items_dict[loc] = {}
            get_cardinal_items(loc, cardinal)
    else:
        loc_items_dict[loc] = {}
        get_cardinal_items(loc, cardinal)


def add_confirms():
    print("ADD_CONFIRMS")
    from itemRegistry import registry
    confirmed_items = {}
    for item in registry.temp_items:
        if hasattr(item, "name"):
            confirmed_items[item.name] = item

    if confirmed_items or registry.updated:
        printing.print_red("The following item(s) have been updated or are new entries:")

        test_generated_items = True
        if confirmed_items:
            print(f"There are new items: {confirmed_items}")
            for item in confirmed_items:
                if test_generated_items:
                    print(f"Item name: {item}")
                    printing.print_red(f"If you want to add the {item} to generated_items, please type 'yes' after the item data is printed.", invert=True)
                    printing.print_green(text=f"Item data: {vars(confirmed_items[item])}",  invert=True)

                    test = input()
                    if test.lower() in ("y", "yes"):
                        print("\nItem confirmed.")
                        testReg.add_to_gen_items(confirmed_items[item])
                    else:
                        continue
                    print(f"Finished adding new items to {json_to_edit}")


        if testReg.updated:
            for inst in testReg.updated:
                if not inst in confirmed_items:
                    if isinstance(inst, testInstances):
                        testReg.add_to_gen_items(inst) # currently only does one at a time, would be better to batch it internally. Tomorrow.

                elif isinstance(inst, str):
                    if testReg.by_name.get(inst):
                        testReg.add_to_gen_items(testReg.by_name.get(inst)) # currently only does one at a time, would be better to batch it internally. Tomorrow.
            print(f"Finished adding updated items to {json_to_edit}.")

        printing.print_blue("\n.                      Fin.                       .", invert=True)
        print()

#add_confirms()

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

if __name__ == "__main__":

    def get_loc_items(loc=None, cardinal=None):

        json_primary = "dynamic_data/items_main.json"
        with open(json_primary, 'r') as file:
            item_defs = json.load(file)

        loc_data_json = "loc_data.json"
        with open(loc_data_json, 'r') as file:
            loc_dict = json.load(file)

        def get_cardinal_items(loc, cardinal):

            gen_items = use_generated_items()

            def from_single_cardinal(loc, cardinal):

                if not loc_dict.get(loc.lower()):
                    print(f"Location {loc} not in env_data.")
                    return
                if loc_dict[loc.lower()].get(cardinal):
                    if loc_dict[loc.lower()][cardinal].get("item_desc"):
                        for item in loc_dict[loc.lower()][cardinal]["item_desc"]:
                            loc_item = {}
                            skip_add = False
                            if item != "generic" and item != "no_items":
                                if item_defs.get(item):
                                    gen_print(f"`{item}` found in item_defs.")
                                    loc_item[item] = item_defs.get(item)
                                    loc_item[item].setdefault("exceptions", {}).update({"starting_location": cardinal + " " + loc})
                                    inst = testReg.init_single(item, loc_item[item])
                                    gen_print(f"\nINST GENERATED (item_dict by_cardinal): {vars(inst)}\n")
                                else:
                                    if gen_items.get(item):
                                        gen_print(f"`{item}` found in generated_items.")
                                        loc_item[item] = gen_items[item]
                                        gen_print(f"GEN ITEMS {item}: {gen_items[item]}")
                                        skip_add = True
                                    elif test_items.get(item):
                                        gen_print(f"`{item}` found in test_items.")
                                        loc_item[item] = test_items[item]
                                    else:
                                        gen_print(f"Item {item} not found in item_defs, generating from blank.")
                                        loc_item[item] = ({"item_type": [static]})
                                        inst = testReg.new_item_from_str(item_name=item, loc_cardinal=(loc + " " + cardinal))
                                        continue

                                    loc_item[item].setdefault("exceptions", {}).update({"starting_location": cardinal + " " + loc})
                                    inst = testReg.init_single(item, loc_item[item])
                                    if not skip_add:
                                        testReg.temp_items.add(inst)

            if cardinal == None:
                for cardinal in CARDINALS:
                    """
                    if locations[loc][cardinal].get("items"): ## This is just getting items from 'locations' dict here, not from the main dict. Will probably transition to only adding items to the loc entries there to avoid doubling up, but it is really convenient to add it elsewhere. Not sure.
                        for item_name in locations[loc][cardinal]["items"]:
                            skip_add = False
                            loc_item = {}
                            if item_defs.get(item_name):
                                gen_print(f"`{item_name}` found in item_defs.")
                                loc_item[item_name] = item_defs.get(item_name)
                                skip_add = True
                            elif gen_items.get(item_name):
                                gen_print(f"`{item_name}` found in generated_items.")
                                loc_item[item_name] = gen_items[item_name]
                                gen_print(f"GEN ITEMS {item_name}: {gen_items[item_name]}")
                                skip_add = True
                            elif test_items.get(item_name):
                                gen_print(f"`{item_name}` found in test_items.")
                                loc_item[item_name] = test_items[item_name]
                            else:
                                gen_print(f"Item {item_name} not found in item_defs, generating from blank.")
                                loc_item[item_name] = ({"item_type": [static]})
                                inst = testReg.new_item_from_str(item_name=item_name, loc_cardinal=(loc + " " + cardinal))
                                continue

                            loc_item[item_name].setdefault("exceptions", {}).update({"starting_location": cardinal + " " + loc})
                            #print("About to go to init_single:")
                            #print(f"item_name: {item_name}, loc_item: {loc_item}")
                            inst = testReg.init_single(item_name, loc_item[item_name])
                            gen_print(f"\nINST GENERATED: {vars(inst)}\n")
                            if not skip_add:
                                testReg.temp_items.add(inst)
                    """
                    from_single_cardinal(loc, cardinal)
            else:
                from_single_cardinal(loc, cardinal)

        if loc == None:
            for loc in loc_dict:
                get_cardinal_items(loc, cardinal)
        else:
            get_cardinal_items(loc, cardinal)

    get_loc_items()

    def main_test():

        gen_items = use_generated_items(input_=None)
        item = None
        get_loc_items()
        for item_name in test_items:
            if gen_items.get(item_name):
                print(f"gen_items item: {gen_items.get(item_name)}")
                item = gen_items.get(item_name)
            elif item_defs.get(item_name):
                print(f"Item from item_defs: {item_name}")
                item = item_defs.get(item_name)
            do_print(f"item_by_name: \n {item}, name: {item_name}\n\n")
            inst = testReg.init_items(item, item_name)
            if not item_defs.get(item_name):
                print(f"Item: {item_name} not yet in item_refs.")
                testReg.temp_items.add(inst)

            do_print(f"inst: {inst}")



        #inst = testReg.init_single(item_name, loc_item[item_name])
        #init_items(self, item_data)

        def print_ordered_vars(item):
            vars_dict = vars(item)

            temp_queue = dict()
            new_queue = dict()
            for item in vars_dict:
                print(f"\033[4;35;47mItem in vars dict: {item} // vars_dict[item]: {vars_dict[item]} \033[0m")
                temp_queue[item] = vars_dict[item]

            leftovers = list(i for i in list(temp_queue) if i not in flag_keys)

            for k in leftovers:
                val = vars_dict[k]
                if isinstance(val, dict):
                    if k == "alt_names" and not val:#5==1:
                        #print("Empty alt_names should be skipped")
                        continue
                    #elif k == "alt_names":
                    #    print(f"k == alt_names, val == : {val}")
                    else:
                        new_queue[k] = True
                else:
                    new_queue[k] = val

            for k in flag_keys:
                if k in temp_queue:
                    new_queue[k] = temp_queue[k]

            pprint(new_queue, sort_dicts=False)
            print("\n")

            if leftovers:
                printing.print_green(f"Leftovers: {leftovers}")
                print("\n")

        #print("\n::::::::ABOUT TO START CLEAN_CHILDREN::::::::\n")
        testReg.clean_children()

        #for item in testReg.instances:
        #    print_ordered_vars(item)


        def indexed_view(included=None, excluded=None):

            def clarify(group):
                if isinstance(group, set|list|tuple):
                    for flag_name in group:
                        if flag_name not in flag_keys:
                            print(f"Attribute name {flag_name} not in flag_keys. Consider adding it.")

    #main_test()

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

            #inst = testReg.new_item_from_item_defs(item, new_dict)

        return pick_item

    pick_item = None#get_types_from_flags()

    def clean_dict(named_item=pick_item):

        with open(json_to_edit, 'r') as file:
            data = json.load(file)

        changed = False
        for key, entry in data.items():
            if named_item:
                if key != named_item:
                    continue

            printing.printkind(key)
            printing.printkind(entry)

            pop_me = set()
            for header, item in entry.items():
                if header in ("starting_location", "current_loc", "id", "contained_in", "started_contained_in", "container", "dupe", "fragile"):
                    pop_me.add(header)
                    changed = True
                elif isinstance(item, set):
                    entry[header] = str(item)
                    changed = True
                elif isinstance(item, testInstances):
                    pop_me.add(header)
                    changed = True

                if header in ("is_key", "can_pick_up", 'is_charged', "fragile", "can_be_locked", 'is_locked') and entry[header] == None:
                    entry[header] = True
                    changed=True
                elif header == "description" and (entry[header] == "none yet" or entry[header] == None):
                    if "mag" in key:
                        key = key.replace("mag", "magazine")
                    entry[header] = f"It's a {key}"
                    changed=True

            if pop_me:
                for header in pop_me:
                    entry.pop(header)
                changed=True

        if changed:
            print("Write to file now?")
            test = input()
            if test in ("yes", "y"):

                with open(json_to_edit, 'w') as file:
                    json.dump(data, file, indent=2)
        else:
            print("No changes to JSON file.")

    clean_dict(named_item=pick_item)

    def edit_dict(named_item=pick_item):
        with open(json_to_edit, 'r') as file:
            data = json.load(file)
        update_primary = False
        update_all_primary = False
        update_data = None

        print("Do you want to add the changes made next to the primary items file?")
        test = input()
        if test in ("yes", "y"):
            update_primary = True
            with open(json_primary, 'r') as readfile:
                update_data = json.load(readfile)
            print("Do you want to update all automatically?")
            test = input()
            if test in ("yes", "y"):
                update_all_primary = True

# update_primary and not update_all_primary: separate dict with only selected entries being updated/added to the main dict.
# update_all_primary: add all new entries and all changes to the existing dict.

        for key, entry in data.items():
            if named_item:
                if key != named_item:
                    continue

            printing.printkind(key)
            printing.printkind(entry)
            from itemRegistry import ItemInstance

            pop_me = set()
            for header, item in entry.items():
                if header in ("starting_location", "current_loc", "id", "contained_in", "started_contained_in", "container", "dupe", "fragile"): # listing the container variants because idk why the 'isinstance' below isn't working yet.
                    pop_me.add(header)
                elif isinstance(item, set):
                    entry[header] = str(item)
                elif isinstance(item, ItemInstance):
                    pop_me.add(header)

                if header in ("is_key", "can_pick_up", 'is_charged', "fragile", "can_be_locked", 'is_locked') and entry[header] == None:
                    entry[header] = True
                elif header == "description" and entry[header] == "none yet":
                    if "mag" in key:
                        key = key.replace("mag", "magazine")
                    entry[header] = f"It's a {key}"

            if pop_me:
                for header in pop_me:
                    entry.pop(header)

        print("Write to generated item file now?")
        test = input()
        if test in ("yes", "y"):
            with open(json_to_edit, 'w') as file:
                json.dump(data, file, indent=2)


        if update_primary:
            for item in data:
                if update_all_primary:
                    update_data.setdefault(item, data[item])
                else:
                    if update_data.get(item):
                        print(f"Do you want to update {item}? Old: \n{update_data[item]}\n New: {data[item]}")
                        test = input()
                        if test in ("yes", "y"):
                            update_data[item] = data[item]
                    else:
                        update_data[item] = data[item]

            with open(json_primary, 'w') as file:
                json.dump(update_data, file, indent=2)
                print(f"Updated {json_primary}")

    #edit_dict()

    def make_location_data_json(): ## Will probably never need this again. Leaving it here for now anyway.

        ## "item_desc" == "item_desc" in old vers.
        #  "items:{}" == new, to replace 'locations' in testclass as the place to add simple items to locations (can be entirely new or referencing item_defs, doesn't matter. Only difference is they don't have location-specific descriptions and may or may not be player-visible.)
        from env_data import loc_dict

        ## Really, the dict in location_items could just be held in memory if I generated it each time. But it's a convenient way to have it to edit without having to deal with the main env_data file. Still feels wasteful though.

        # I mean... I could just have the dict here and reference /this/ from env_data. Save duplicating it. That would be better, right? I really don't know.

        loc_base = {}
    #    for place in loc_dict:
    #        loc_base.setdefault(place, {})
    #        print(f"PLACE: {place}")
    #        for cardinal in loc_dict[place]:
    #            if cardinal in CARDINALS and loc_dict[place][cardinal] != None:
    #                for entry in loc_dict[place][cardinal]:
    #                    print(f"ENTRY: {entry}")
    #                    if entry == "item_desc":
    #                        loc_base[place][cardinal] = loc_dict[place][cardinal]
#
        #print(f"loc_base: {loc_base}")

        # if you want to edit the final dictand not draw from the original in env_data:

        loc_items_json = "loc_data.json"
        with open(loc_items_json, 'r') as loc_items_file:
            loc_items = json.load(loc_items_file)
            # combine the entries if they already exist. Don't know if I need this at all, I'm probably just doing it initially here.
            # OR, automatically grab items from env_data's loc items in item_desc, and add them here. That's probably a good one.
            loc_dict = loc_items

        if loc_items:
            for place in loc_items:
                loc_base[place] = {}
                if place in loc_dict:
                    print(f"place: {place}")
                    for cardinal in loc_dict[place]:
                        if cardinal in CARDINALS and loc_dict[place][cardinal] != None:
                            print(f"cardinal: {cardinal}")
                        #loc_base[place][cardinal] = loc_dict[place][cardinal]
                            loc_base[place][cardinal] = {}
                            if loc_dict[place].get(cardinal):
                                for field in loc_dict[place].get(cardinal):
                                    #if "actions" in field:
                                    #    continue
                                    #if "item_desc" in field: # for now, until it's changed in env_data or that dict is removed entirely.
                                    #    loc_base[place][cardinal]["item_desc"] = loc_dict[place][cardinal].get(field)
                                    #    continue

                                    #if field in ("short_desc", "long_desc"):
                                    loc_base[place][cardinal][field] = loc_dict[place][cardinal].get(field)
                                    # just add everything. Should include item_state by default.

                                if not loc_dict[place][cardinal].get("items"):
                                    loc_base[place][cardinal]["items"] = {"": {"description": None, "is_hidden": False}} # empty template. Adding is_hidden here so I have a straightforward location-specific hidden flag, makes sense. Everything else can be from item gen or item_defs.
                                if not loc_dict[place][cardinal].get("alt_names"):
                                    loc_base[place][cardinal]["alt_names"] = []

                        elif cardinal == "descrip":
                            print(f"descrip: {loc_dict[place].get(cardinal)}")
                            loc_base[place][cardinal] = loc_dict[place][cardinal]

                        #if cardinal in loc_dict[place]:
                            #continue
                        #if loc_items[place].get(cardinal) in (None, {}):
                        #else:
                        #    loc_base[place][cardinal] = loc_items[place].get(cardinal)
                        #    if loc_items[place].get(cardinal) != None:
                        #        loc_base[place][cardinal] = loc_items[place].get(cardinal)
                                #print(f"Existing cardinal: {place} {cardinal}: {loc_items[place].get(cardinal)}")
                                #for part in loc_items[place][cardinal]:
                                #    print(f"PART: {part}")
                else:
                    print(f"Entry in JSON but not in env_data location: {place}")
                    loc_base.setdefault(place, {}).update(loc_items[place])

        #else:
            #print("Target JSON is empty. Writing loc_base to empty target JSON.")
        with open(loc_items_json, 'w') as loc_items_file:
            json.dump(loc_base, loc_items_file, indent=2)
        print(f"Written to {loc_items_json}")

    #make_location_data_json()



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
