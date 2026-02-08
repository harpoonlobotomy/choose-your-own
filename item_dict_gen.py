#item_dict_gen.py I just want to outsource the item def generation part and let itemRegistry just do the actual registration side.

import printing
from env_data import locRegistry as loc

CARDINALS = ["north", "east", "south", "west"]
excluded_itemnames = ["generic", "no_items", "no_starting_items"]


item_type_descriptions = {
"container": {
    "starting_children_only": "",
    "any_children": "",
    "no_children": "",
    "open_starting_children_only": "",
    "open_any_children": "",
    "open_no_children": ""
    },
"can_open": {
    "if_open": "",
    "if_closed": ""
    },
"fragile": {
    "if_broken": "",
    },
"food_drink": {
    "if_spoiled": ""
    }
}


global loc_items_dict
loc_items_dict = {}

from itemRegistry import type_defaults

class itemGenerator:
    def __init__(self):
        self.item_defs = {}
        self.is_child = {"child": {}, "parent": {}} # really should just have child:parent, but that won't include locations etc. Doesn't work.
        self.has_children = {"parent": {}, f"children": {}} # item + def
        self.requires_key = {"lock": {}, "key": {}}
        self.is_key = {"key": {}, "lock": {}} # again - these two have a lot of redundant info but I want to start here.
        self.by_location = {} # not using this at all currently. May delete later.

    def complete_location_dict(self):

        for placeInstance in loc.places:
            for cardinal in loc.cardinals[placeInstance]:
                self.by_location.setdefault(cardinal, set())

    def assign_item_to_loc(self, location, cardinal, item):
        card = loc.by_cardinal_str(cardinal, location)
        if not self.by_location.get(card):
            self.by_location[card] = list()

        self.by_location[card].append(item)

generator = itemGenerator()

generator.complete_location_dict()

def clean_item_types(attr):
    item_types = set()
    if isinstance(attr, str):
        if "{" in attr:
            _, type_item = attr.split("{")
            type_item, _ = type_item.split("}")
            type_item = type_item.replace("'", "")
            parts = type_item.split(", ")
            for part in parts:
                if part != None and part not in item_types:
                    item_types.add(part)
        else:
            item_types.add(attr)

    elif isinstance(attr, set|list|tuple):
        for item_type in attr:
            item_types.add(item_type)

    return item_types

def get_type_tags(new_str, item_dict):

    if not isinstance(new_str, set):
        new_str = clean_item_types(new_str)

    for category in new_str:
        if category not in type_defaults:
            print(f"Category `{category}` not in type_defaults.")
            exit()

        for flag, val in type_defaults[category].items():
            if flag not in item_dict: # so it doesn't overwrite any custom flag in a loc item entry
                item_dict[flag] = val

    return item_dict


def item_def_from_str(item_name:str, item_dict=None):

    if item_dict:
        new_item_dict = item_dict
    else:
        new_item_dict = {}

    if item_name == "":
        print("No item name given.")
        exit()

    print("\n")
    printing.print_green(f"Options: {list(type_defaults)}", invert=True)
    print(f"Please enter the default_types you want to assign to `{item_name}` (eg ' key, can_pick_up, fragile ' )")
    input_str = input()

    if " " in input_str.strip():
        input_str = input_str.replace(",", "")
        parts = input_str.strip().split(" ")
        parts = set(i for i in parts if i != None and i in list(type_defaults))
        print(f"PARTS: {parts}, type: {type(parts)}")
        if isinstance(parts, set):
            new_str = parts
        else:
            if len(parts) > 1:
                new_str = set(parts)
            else:
                new_str = set([parts])

    elif input_str in list(type_defaults):
        print(f"Input str in type_defaults: {input_str}, type: {type(input_str)}")
        new_str = set([input_str])

    else:
        print(f"No valid input [`{input_str}`]. Defaulting to item_type = ['static']")
        new_str = set(["static"])

    if not new_item_dict.get("name"):
        new_item_dict["name"] = item_name
    new_item_dict["item_type"] = new_str

    new_item_dict = get_type_tags(new_str, new_item_dict)

    return new_item_dict


import json
json_primary = "ref_files/items_main.json" # may break things
with open(json_primary, 'r') as file:
    item_defs = json.load(file)

json_to_edit = "ref_files/generated_items.json"
#with open(json_to_edit, 'r') as file:
#    gen_items = json.load(file)
gen_items = {} # not currently using the actual file, just for temp storage.

def get_item_data(item_name, incoming_data=None): # note: no locations here. This is pure item-def building using available item details from loc_data + item+gen_defs. Use these as bases for instancing the items in itemReg.

    if not incoming_data:
        incoming_data = {}

    cleaned_dict = {}

    if isinstance(incoming_data, str):
        print(f"Incoming data == str: {incoming_data}")
        # assume it's a description from items_desc, because what else would it be.
        incoming_data = {"description": incoming_data}

    item_data = None
    if item_name in generator.item_defs:
        item_data = generator.item_defs[item_name] # maybe should just return this immediately?
        printing.print_green(f"Item already found in generator: {item_name}.")
    if item_name in item_defs:
        item_data = item_defs[item_name]

    elif item_name in gen_items:
        item_data = gen_items[item_name]

    else:
        print(f"{item_name} not in item_defs or gen_items")

    if not item_data:
        item_data = item_def_from_str(item_name)

    for field in item_data:
        cleaned_dict[field] = item_data[field]

    for field in incoming_data:
        if not cleaned_dict.get(field):
            cleaned_dict[field] = incoming_data[field]

    if cleaned_dict.get("item_type"):
        cleaned_dict = get_type_tags(cleaned_dict.get("item_type"), cleaned_dict)
    else:
        print(f"Somehow an established item does not have item_types: {item_name}")
        cleaned_dict = item_def_from_str(item_name, cleaned_dict)
        cleaned_dict = get_type_tags(cleaned_dict.get("item_type"), cleaned_dict)

    #for field in ("started_contained_in", "contained_in", "starting_location", "current_loc"):
    #    if field in cleaned_dict:
    #        cleaned_dict.pop(field)

    generator.item_defs[item_name] = cleaned_dict
    return cleaned_dict


def find_children(item, item_dict):

    if item_dict.get("starting_children") and item_dict["starting_children"] != None:
        generator.has_children[item] = item_dict

        for child in item_dict["starting_children"]:
            if not child in generator.item_defs:
                get_item_data(child)

    if item_dict.get("requires_key") and item_dict["requires_key"] != None:
        generator.requires_key[item] = item_dict
        required_keyname = item_dict["requires_key"]
        if not isinstance(required_keyname, str):
            print(f"Required key name is not a string: {required_keyname}. Hard exit.")
            exit()
        else:
            if not generator.item_defs.get(required_keyname):
                get_item_data(required_keyname)

    ## I think that's fine. I'm very unlikely to ever say 'this is a child of x' without putting it in x, or say 'this is the key to 'y' without saying 'y needs this key'. This is better for now I think.
    # Either way, the itemReg is the one that figures out if an /instance/ is correctly matched. This is just making sure the data is available, separately.

def get_items_from_card(loc, cardinal, loc_data):

    desc_items = {}
    other_items = {}
    added = set()

    loc_items_dict.setdefault(loc, {}).setdefault(cardinal, {})

    if loc_data.get("item_desc"):
        for item in loc_data["item_desc"]:
            if item == "" or item in excluded_itemnames:
                continue
            # Assume only one. If multiple, need to figure something else out.
            desc_items[item] = loc_data["item_desc"]

    if loc_data.get("items"):
        for item in loc_data["items"]:
            if item == "" or item in excluded_itemnames:
                continue
            other_items[item] = loc_data["items"]

    for item in other_items:
        print(f"item: {item}")
        if item == None or item == {}:
            continue
        if item in desc_items:
            if item in added:
                print("This item was already added, but there's another one. I can't deal with this.")
            else:
                added.add(item)
            #print(f"Item in both lists: {item}")
            item_desc = desc_items[item].get(item)
            item_attr = other_items[item].get(item)

            if item_desc and not item_attr.get("description"):
                item_attr["description"] = item_desc

            loc_items_dict[loc][cardinal][item] = item_attr
        else:
            loc_items_dict[loc][cardinal][item] = other_items[item].get(item)

        print(f"item in other_items: {loc_items_dict[loc][cardinal][item]}")
        get_item_data(item, loc_items_dict[loc][cardinal][item])

    for item in desc_items:
        if not item in other_items and item != "" and item not in excluded_itemnames:
            loc_items_dict[loc][cardinal][item] = desc_items[item].get(item)
            # Should get item data here, maybe. We're just adding what's in generated/item_defs. Only downside is it won't update if an item is made but not added to generated right away. But we're not generating anything here, so that's alright actually.
            print(f"item in desc_items dict_gen: {loc_items_dict[loc][cardinal][item]}")
            get_item_data(item, loc_items_dict[loc][cardinal][item])

def get_loc_items_dict(loc=None, cardinal=None):

    import json, config
    with open(config.loc_data, 'r') as file:
        loc_dict = json.load(file)

    def get_cardinal_items(loc, cardinal):

        def from_single_cardinal(loc, cardinal):

            if not loc_dict.get(loc.lower()):
                print(f"Location {loc} not in env_data.")
                return

            if loc_dict[loc.lower()].get(cardinal):
                if loc_dict[loc.lower()][cardinal].get("item_desc") or loc_dict[loc.lower()][cardinal].get("items"): ## need to generalise this a bit so I can reuse most of the following for .("items") as well, not just item_desc entries. (item desc are included in scene descriptions if relevant, items are just there.)

                    get_items_from_card(loc, cardinal, loc_dict[loc.lower()][cardinal])

        """
        # unrelated, did just think of a way to mix up location descriptions. For each place, have some words/phrases etc that can be intermittedly (but once used, consistently) for items for particular locations. So inside a crypt might be 'dusty, dry, etc etc (but better than that, few-word phrases etc) that are randomly sprinkled into item descriptions. So 'an ivory jar' can become 'a dusty ivory jar' because it's in the crypt, but it's still generated from the same base item. Just mark where these flavour words will be (like [[]] and PPP/EEE in scene descrips), Not sure but could be good.
        """
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

def get_all_other_items():

    for item in item_defs:
        if item in generator.item_defs:
            continue
        get_item_data(item, item_defs[item])

def init_item_dict():

    get_loc_items_dict(loc=None, cardinal=None)
    get_all_other_items() # just ensures that every item in item_defs is covered.

    counter = 0
    while True and counter < 10:
        print(f"Checking for children: round {counter}")
        keys = list(generator.item_defs)
        key_len = len(keys)
        for item in keys:
            find_children(item, generator.item_defs[item])
        new_key_len = len(list(generator.item_defs))
        counter += 1
        if key_len == new_key_len:
            print("All children found.")
            break

    def serialise_item_defs():
        for item, field in generator.item_defs.items():
            for k, v in field.items():
                if isinstance(v, set):
                    generator.item_defs[item][k] = str(v) # hate that I'm making this a string but the sets aren't serialisable for json apparently.
                    #print(f"k: {k}, type: {type(k)}")
                    #print(f"v: {generator.item_defs[item][k]}, type: {type(generator.item_defs[item][k])}")
            #print(f"item {item}, field: {field}, type: {type(field)}")
            #print(f"item {item}, field: {field}, type: {type(item[field])}")


    update_gen_items = False # This should be changed, I shouldn't be turning the actual dict to all strings, itemReg just has to turn it back again and that's the priority. If I want to output to generated, do it to a new dict.
    if update_gen_items:
        serialise_item_defs()
        with open(json_to_edit, 'w') as file:
            json.dump(generator.item_defs, file, indent=2)

    return generator.item_defs


if __name__ == "__main__":
    #NOTE: REMOVE THIS LATER. Once it's instated within the initialisation process.
    #     ***************************************
    from env_data import initialise_placeRegistry
    initialise_placeRegistry()
    #     ***************************************

    init_item_dict()
