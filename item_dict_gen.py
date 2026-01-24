#item_dict_gen.py I just want to outsource the item def generation part and let itemRegistry just do the actual registration side.

import printing
from env_data import locRegistry as loc

CARDINALS = ["north", "east", "south", "west"]

global loc_items_dict
loc_items_dict = {}


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
    "can_open": {"is_open": False, "can_be_opened": True, "can_be_closed": True, "can_be_locked": True, "is_locked": True, "requires_key": False}

    #{"special_traits: set("dirty", "wet", "panacea", "dupe", "weird", "can_combine")}, # aka random attr storage I'm not using yet
    #"exterior": {"is_interior": False} ## Can be set scene-wide, so 'all parts of 'graveyard east' are exterior unless otherwise mentioned'. (I say 'can', I mean 'will be when I set it up')
}

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
#NOTE: REMOVE THIS LATER.
#     ***************************************
from env_data import initialise_placeRegistry
initialise_placeRegistry()
#     ***************************************

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
        #print(f"get_type_tags requires a set. This: {new_str} is type {type(new_str)}")
    for category in new_str:
        if category not in type_defaults:
            print(f"Category `{category}` not in type_defaults.")
            exit()
        for flag in type_defaults[category]:
            if flag not in item_dict: # so it doesn't overwrite any custom flag in a loc item entry
                item_dict[flag] = type_defaults[category][flag]

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
    new_item_dict["item_type"] = new_str # wouldn't be here if it had item types already.

    new_item_dict = get_type_tags(new_str, new_item_dict)

    return new_item_dict


import json
json_primary = "dynamic_data/items_main.json" # may break things
with open(json_primary, 'r') as file:
    item_defs = json.load(file)

json_to_edit = "dynamic_data/generated_items.json"
#with open(json_to_edit, 'r') as file:
#    gen_items = json.load(file)
gen_items = {} # not currently using the actual file, just for temp storage.

def get_item_data(item_name, incoming_data=None): # note: no locations here for the minute. This is pure item-def building using available item details from loc_data + item+gen_defs. Use these as bases for instancing the items in itemReg.

    if not incoming_data:
        incoming_data = {}

    cleaned_dict = {}

    if isinstance(incoming_data, str):
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
    if not item_data:
        item_data = item_def_from_str(item_name)

    for field in item_data:
        if incoming_data.get(field):
            print(f"Incoming data for {field}: {incoming_data[field]}, item_data for {field}: {item_data[field]}")
            if field == "description" and item_data[field] != None:
                cleaned_dict[field] = item_data[field] # use generic descriptions where possible. Maybe change this later, idk.
            else:
                cleaned_dict[field] = incoming_data[field]
        else:
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

    for field in ("started_contained_in", "contained_in", "starting_location", "current_loc"):
        if field in cleaned_dict:
            cleaned_dict.pop(field)

    generator.item_defs[item_name] = cleaned_dict

    return cleaned_dict


def find_children(item, item_dict):

    if item_dict.get("starting_children") and item_dict["starting_children"] != None:
        generator.has_children[item] = item_dict

        for child in item_dict["starting_children"]:
            if not child in generator.item_defs:
                #print("Child does not exist in item_defs.")
                get_item_data(child)
            #else:
                #print(f"Child exists. {generator.item_defs[child]}")

    if item_dict.get("requires_key") and item_dict["requires_key"] != None:
        generator.requires_key[item] = item_dict
        required_keyname = item_dict["requires_key"]
        if not isinstance(required_keyname, str):
            print(f"Required key name is not a string: {required_keyname}. Hard exit.")
            exit()
        else:
            #print(f"{item} requires the key: {required_keyname}")
            if not generator.item_defs.get(required_keyname):
                #print(f"Key {required_keyname} doesn't exist in itemdefs yet. Creating the def.")
                get_item_data(required_keyname)
            #else:
                #print(f"{required_keyname} already exists in the item_defs.")

    ## I think that's fine. I'm very unlikely to ever say 'this is a child of x' without putting it in x, or say 'this is the key to 'y' without saying 'y needs this key'. This is better for now I think.
    # Either way, the itemReg is the one that figures out if an /instance/ is correctly matched. This is just making sure the data is available, separately.
"""
def clean_relationships(self): # not children anymore,  that's elsewhere. Right now just keys, will expand to events once there are events to clean.

    #print(f":: Clean children:: ")
    target_flags = ("contained_in", "requires_key", "event_key", "trigger_target")

    def cleaning_loop():

        # applies instances to children/keys/etc.
        itemlist = frozenset(self.by_id)

        for item_id in itemlist:
            item = self.by_id.get(item_id)

            if not item:
                print(f"Failed to get instance by id in cleaning_loop for instance ({item_id}).")
                exit() # for now just hard quit if this ever happens, it definitely shouldn't.

            if hasattr(item, "requires_key") and not isinstance(getattr(item, "requires_key"), bool):
                if isinstance(item.requires_key, ItemInstance):
                    continue
                key_found = False
                for maybe_key in registry.keys:
                    if hasattr(maybe_key, "unlocks") and getattr(maybe_key, "unlocks"):
                        continue # so a key will only be assigned to one lock, which I want for now. maybe change this later.
                    #print(f"MAYBE KEY: {maybe_key}")
                    if maybe_key.name == getattr(item, "requires_key"):
                        #print(f"Maybe {maybe_key} is the key to {item}")
                        #print(f"\n\nkey vars: {vars(maybe_key)}\n lock vars: {vars(item)}\n\n")
                        if hasattr(maybe_key, "is_key_to") and maybe_key.is_key_to == item.name:
                            #print(f"maybe_key.is_key_to: {maybe_key.is_key_to}, item.name: {item.name}")
                            #
                            print(f"Assigning {maybe_key} to {item}.")
                            self.locks_keys[item] = maybe_key
                            self.locks_keys[maybe_key] = item
                            item.requires_key = maybe_key
                            setattr(maybe_key, "unlocks", item) ## NOTE: This isn't implemented anywhere, try to remember. inst.unlocks == inst of the lock it opens.
                            #print(f"Lock: {maybe_key.unlocks}")
                            #print(f"Key: {item.requires_key}")
                            key_found = True

                if not key_found:
                    if generator.item_defs.get(getattr(item, "requires_key")):
                        target_obj = self.init_single(getattr(item, "requires_key"), generator.item_defs.get(getattr(item, "requires_key")))
                        all_item_names_generated.append((item, "generate key from item_defs"))
                        print(f"No target_obj from item defs for {item}, looking for {getattr(item, "requires_key")}")
                    else:
                        target_obj = use_generated_items(getattr(item, "requires_key"))
                        if not target_obj:
                            print(f"No target_obj from item defs or generated, for {item}, looking for {getattr(item, "requires_key")}")
                            target_obj = new_item_from_str(item_name=getattr(item, "requires_key"))
                            all_item_names_generated.append(({getattr(item, "requires_key")}, "generate key from str"))
                        else:
                            print(f"generated key from generated items but no actual instance I think: {target_obj}")

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
        print()#"Huh, count is the same. This may or may not matter; only really matters if you were expecting a new item to be dynamically generated.")
"""
def get_items_from_card(loc, cardinal, loc_data):

    desc_items = {}
    other_items = {}
    added = set()

    loc_items_dict.setdefault(loc, {}).setdefault(cardinal, {})

    if loc_data.get("item_desc"):
        for item in loc_data["item_desc"]:
            # Assume only one. If multiple, need to figure something else out.
            desc_items[item] = loc_data["item_desc"]

    if loc_data.get("items"):
        for item in loc_data["items"]:
            other_items[item] = loc_data["items"]

    for item in other_items:
        if item == "" or item == "generic":
            continue
        if item in desc_items:
            if item in added:
                # treat as non-match
                print("This item was already added, but there's another one. I can't deal with this.")
            else:
                added.add(item)
            print(f"Item in both lists: {item}")
            item_desc = desc_items[item].get(item)
            item_attr = other_items[item].get(item)
#            if "[[]]" in item_desc:
            if item_desc:
                item_attr["description"] = item_desc
            loc_items_dict[loc][cardinal][item] = item_attr
        else:
            loc_items_dict[loc][cardinal][item] = other_items[item].get(item)
        get_item_data(item, loc_items_dict[loc][cardinal][item])
        #loc_items_dict[loc][cardinal][item]
        #generator.assign_item_to_loc(loc, cardinal, item)

    for item in desc_items:
        if not item in other_items and item != "" and item != "generic":
            loc_items_dict[loc][cardinal][item] = desc_items[item].get(item)
            # Should get item data here, maybe. We're just adding what's in generated/item_defs. Only downside is it won't update if an item is made but not added to generated right away. But we're not generating anything here, so that's alright actually.
            get_item_data(item, loc_items_dict[loc][cardinal][item])
            #generator.item_defs[item] = item_data#loc_items_dict[loc][cardinal][item]
            #generator.assign_item_to_loc(loc, cardinal, item)




def get_loc_items_dict(loc=None, cardinal=None):

    import json

    loc_data_json = "loc_data.json"
    with open(loc_data_json, 'r') as file:
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
            def get_item_data(item, item_state_dict, gen_items, loc_items_dict, loc, cardinal):
                loc_item = {}
                skip_add = False

                if item in name_to_inst_tmp:
                    return loc_items_dict

                if item != "generic":

                    card_inst = locRegistry.by_cardinal_str(cardinal_str=cardinal, loc=loc.lower())
                    setattr(card_inst, "item_state", item_state_dict)

                    if registry.item_defs.get(item):
                        print(f"`{item}` found in item_defs.")
                        loc_item[item] = registry.item_defs.get(item)
                        loc_item[item]["starting_location"] = card_inst
                        if item_state_dict and item_state_dict.get(item):
                            for k, v in item_state_dict[item].items():
                                loc_item[item][k] = v

                        inst = registry.init_single(item, loc_item[item])
                        all_item_names_generated.append((item, "item_defs"))
                        print("\n\n")
                        printing.print_red(inst)
                        printing.print_red(inst.location)
                        print("\n\n")
                        #print(f"\nINST GENERATED (item_dict by_cardinal): {vars(inst)}\n")
                        name_to_inst_tmp[item] = inst
                        #if containers and item in containers:

                        if item_state_dict and item_state_dict != None:# #### NO, because this will run every fucking item.
                            if item_state_dict.get(item) and item_state_dict[item].get("contained_in"):
                                if not registry.child_parent.get(inst):
                                    registry.child_parent[inst] = item_state_dict[item]["contained_in"]

                    else:
                        if gen_items and gen_items.get(item):
                            #print(f"`{item}` found in generated_items.")
                            loc_item[item] = gen_items[item]
                            #print(f"GEN ITEMS {item}: {gen_items[item]}")
                            skip_add = True
                        else:
                            print(f"Item {item} not found in item_defs, generating from blank.")
                            loc_item[item] = {}
                            if item_state_dict and item_state_dict.get(item):
                                for k, v in item_state_dict[item].items():
                                    loc_item[item][k] = v
                            inst = item_def_from_str(item_name=item, loc_cardinal=card_inst,partial_dict=loc_item[item]) # added partial_dict, it should have been here before.
                            all_item_names_generated.append((item, "item_from_str"))
                            print("\n\n")
                            printing.print_red(inst)
                            printing.print_red(inst.location)
                            print("\n\n")
                            name_to_inst_tmp[item] = inst
                            if loc_item.get("item"):
                                registry.item_defs[item] = loc_item[item]

                            if not skip_add:
                                registry.temp_items.add(inst)
                            return loc_items_dict

                        loc_item[item].update({"starting_location": card_inst})
                        loc_items_dict[loc][cardinal][item] = loc_item[item]
                        if item_state_dict and item_state_dict.get(item):
                            for k, v in item_state_dict[item].items():
                                loc_item[item][k] = v
                        inst = registry.init_single(item, loc_item[item])
                        all_item_names_generated.append((item, "from_gen"))

                        if loc_item.get("item"):
                            registry.item_defs[item] = loc_item[item]
                        print("\n\n")
                        printing.print_red(inst)
                        printing.print_red(inst.location)
                        print("\n\n")
                        name_to_inst_tmp[item] = inst
                        if not skip_add:
                            registry.temp_items.add(inst)

                return loc_items_dict

            def get_children_data(item, containers, loc, cardinal):
                if item in containers:
                    #print(f"Item in containers: `{item}`")
                    for child_inst in registry.child_parent:
                        if isinstance(registry.child_parent[child_inst], str):
                            if registry.child_parent[child_inst] == item:
                                #print("registry.child_parent[child_inst] == item:")
                                #print(f"registry.child_parent[child_inst] = {registry.child_parent[child_inst]}\n Item: {item}")
                                #print(f"name_to_inst_tmp: {name_to_inst_tmp}")
                                if name_to_inst_tmp.get(item):
                                #if loc_item.get(item):
                                    inst = name_to_inst_tmp[item]#loc_item.get(item).get("instance")
                                #print(f"Inst(should be container): {inst}")
                                    if inst:
                                        registry.child_parent[child_inst] = inst # At this point, don't actually need the registry dict anymore.
                                        child_inst.contained_in = inst
                                        #print(f"CHILD INST VARS: {vars(child_inst)}")
                                        if not hasattr(inst, "children"):
                                            inst.children = set()
                                        inst.children.add(child_inst)
                                        #print(f"PARENT INST VARS: {vars(inst)}")
                                    else:
                                        print(f"Failed to get inst from  loc_item.get(item): {item}")
                                        print(f"Failed to get inst from  loc_item.get(item): {loc_items_dict[loc.lower()][cardinal].get(item)}") ## Probably failed because loc_item doesn't exist here; it only appeared to if the previous if/else succeeded.

            if not loc_dict.get(loc.lower()):
                print(f"Location {loc} not in env_data.")
                return name_to_inst_tmp

            if loc_dict[loc.lower()].get(cardinal):
                if loc_dict[loc.lower()][cardinal].get("item_desc") or loc_dict[loc.lower()][cardinal].get("items"): ## need to generalise this a bit so I can reuse most of the following for .("items") as well, not just item_desc entries. (item desc are included in scene descriptions if relevant, items are just there.)

                    registry.child_parent = dict() ## Reset it every loc_card, so it doesn't add items from one location to containers in another just because the name matches.
                    item_state_dict = loc_dict[loc.lower()][cardinal].get("items")
                    from env_data import locRegistry
                    card_inst = locRegistry.by_cardinal_str(cardinal_str=cardinal, loc=loc.lower())
                    setattr(card_inst, "item_state", item_state_dict)
                    # ugh this is tricky. Because once they're instances the connection is less clear. I guess it's not really, but for some reason my brain thinks it is.
                    #I think it's because once it's active, maybe some other object gets brought to the scene before you evaluate. There's not really any other way to do it though, right?
                    #Or I guess I could mark it to a dict, then add the instance once it's generated. (So like, 'this is the padlock inst that goes to a gate in graveyard north'. idk)

        # unrelated, did just think of a way to mix up location descriptions. For each place, have some words/phrases etc that can be intermittedly (but once used, consistently) for items for particular locations. So inside a crypt might be 'dusty, dry, etc etc (but better than that, few-word phrases etc) that are randomly sprinkled into item descriptions. So 'an ivory jar' can become 'a dusty ivory jar' because it's in the crypt, but it's still generated from the same base item. Just mark where these flavour words will be (like [[]] and PPP/EEE in scene descrips), Not sure but could be good.
                    containers = set()
                    if item_state_dict and item_state_dict != None:# #### NO, because this will run every fucking item.
                        for stateitem in item_state_dict.keys(): # for loop separately so it's not limited by which one happens to be processed first (only getting names here for containers, inst only matters for child_parent.)
                        #if item_state_dict.get(item):
                            if item_state_dict[stateitem].get("contained_in"):
                                #print(f"stateitem: {stateitem} // item_state_dict[stateitem].get('contained_in'): {item_state_dict[stateitem].get("contained_in")}")
                                containers.add(item_state_dict[stateitem]["contained_in"])

                    if loc_dict[loc.lower()][cardinal].get("item_desc"):
                        for item in loc_dict[loc.lower()][cardinal]["item_desc"]:
                            if item == "":
                                continue

                            loc_items_dict = get_item_data(item, item_state_dict, gen_items, loc_items_dict, loc, cardinal)

                    if loc_dict[loc.lower()][cardinal].get("items"):
                        for item in loc_dict[loc.lower()][cardinal]["items"]:
                            if item == "":
                                continue

                            loc_items_dict = get_item_data(item, item_state_dict, gen_items, loc_items_dict, loc, cardinal)


                    if loc_dict[loc.lower()][cardinal].get("item_desc"):
                        for item in loc_dict[loc.lower()][cardinal]["item_desc"]: # at least the loop here means it doesn't loop over everything entirely twice, it only checks for potential relevancy once so places with no item_desc are omitted from that point on.
                            if item != "generic" and item != "":
                                get_children_data(item, containers, loc.lower(), cardinal)

                    if loc_dict[loc.lower()][cardinal].get("items"):
                        for item in loc_dict[loc.lower()][cardinal]["items"]:
                            if item != "generic" and item != "":
                                get_children_data(item, containers, loc.lower(), cardinal)

                    #print(f"CHILD PARENT DICT: {registry.child_parent}")

            return name_to_inst_tmp
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

    #registry.clean_relationships()
#
    #if registry.new_parents and registry.new_parents != None: # in case something slipped by, this should never be needed though.
    #    registry.generate_children_for_parent()


get_loc_items_dict(loc=None, cardinal=None)
counter = 0
while True and counter < 10:
    print("Checking for children: ")
    keys = list(generator.item_defs)
    key_len = len(keys)
    for item in keys:
        find_children(item, generator.item_defs[item])
    new_key_len = len(list(generator.item_defs))
    counter += 1
    if key_len == new_key_len:
        break

#print(generator.item_defs)
def serialise_item_defs():
    for item, field in generator.item_defs.items():
        for k, v in field.items():
            if isinstance(v, set):
                generator.item_defs[item][k] = str(v) # hate that I'm making this a string but the sets aren't serialisable for json apparently.
                #print(f"k: {k}, type: {type(k)}")
                #print(f"v: {generator.item_defs[item][k]}, type: {type(generator.item_defs[item][k])}")
        #print(f"item {item}, field: {field}, type: {type(field)}")
        #print(f"item {item}, field: {field}, type: {type(item[field])}")

update_gen_items = True
if update_gen_items:
    serialise_item_defs()
    with open(json_to_edit, 'w') as file:
        json.dump(generator.item_defs, file, indent=2)
