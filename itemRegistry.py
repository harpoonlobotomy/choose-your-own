
import random
import uuid

from env_data import cardinalInstance, placeInstance, locRegistry as loc
from logger import logging_fn, traceback_fn
import printing

global all_item_names_generated, all_items_generated
all_item_names_generated = list()
all_items_generated = set()

CARDINALS = ["north", "east", "south", "west"]

####### item_size CATEGORIES ############

SMALL_FLAT_THINGS = "small_flat_things"
A_FEW_MARBLES = 'a_few_marbles'
SMALLER_THAN_APPLE = 'smaller_than_apple'
PALM_SIZED = 'palm_sized'
SMALLER_THAN_BASKETBALL = 'smaller_than_basketball'
BIGGER_THAN_BASKETBALL = 'bigger_than_basketball'

container_limit_sizes = {
    SMALL_FLAT_THINGS: 1,
    A_FEW_MARBLES: 2,
    SMALLER_THAN_APPLE: 3,
    PALM_SIZED: 4,
    SMALLER_THAN_BASKETBALL: 5,
    BIGGER_THAN_BASKETBALL: 6
}

print("Item registry is being run right now.")

type_defaults = {
    "standard":
        {f"descriptions": {"generic": None}, "nicenames": {}, "slice_defence": 5, "smash_defence": 5, "slice_attack": 5, "smash_attack": 5,},
    "static":
        {"can_examine": False, "can_break": False},
    #"all_items": {"starting_location": None, "current_loc": None, "alt_names": {}, "is_hidden": False},
    "can_open":
        {"is_open": False, "can_be_opened": True, "can_be_closed": True},
        "descriptions":
            {"if_closed": "", "if_open": ""},
        "nicenames": {
            "if_closed": None, "if_open": None},
    "can_lock":
        {"can_be_locked": True, "is_locked": True, "requires_key": False},
    "container":
        {"is_open": False, "can_be_opened": True, "can_be_closed": True, "can_be_locked": True, "is_locked": True, "requires_key": False, 'starting_children': None, 'container_limits': 4, "children_type_limited": False, "can_be_added_to": True, "children": None,
         "nicenames": {
            "starting_children_only": "",
            "any_children": "",
            "no_children": ""},
        "descriptions": {
            "starting_children_only": "",
            "any_children": "",
            "no_children": ""}},
    "key":
        {"is_key": True, "is_key_to": None},
    "can_pick_up":
        {"can_pick_up": True, "item_size": 1},
    "event":
        {"event": None, "event_type": "item_triggered", "is_event_key": None},
    "trigger":
        {"trigger_type": "plot_advance", "trigger_target": None, "is_exhausted": False},
    "flooring":
        {"is_horizontal_surface": True},
    "wall":
        {"is_vertical_surface": True},
    "food_drink":
        {"can_consume": True, "can_spoil": True, "is_spoiled": True, "is_safe": True, "effect": None},
    "fragile":
        {"is_broken": False, "slice_threshold": 1, "smash_threshold": 1},
    "flammable":
        {"is_burned": False},
    "books_paper":
        {'print_on_investigate': True, 'flammable': True, 'is_burned': False, 'can_read': True},
    "electronics":
        {"can_be_charged": True, "is_charged": False, "takes_batteries": True, "has_batteries": False},
    "battery": {"can_be_charged": True, "is_charged": True},
    "can_speak" :
        {'can_speak': True, 'speaks_common': True},
    "transition":
        {"is_transition_obj": True, "enter_location": None, "exit_to_location": None},
    "loc_exterior":
        {"is_loc_exterior":True, "transition_objs": None, "has_door": False},
    "door_window":
        {"is_door": False, "is_window": False, "is_other": False},
    "random_loot": {
        "loot_type": None},
    "starting_loot": {
        "loot_type": "starting_loot"},
    "is_cluster": {
        "has_multiple_instances": 2, "single_identifier": None, "plural_identifier": None},
    "firesource": {"firesource": True},
    "data_noun": {"is_not_physical": True}

    #{"special_traits: set("dirty", "wet", "panacea", "dupe", "weird", "can_combine")}, # aka random attr storage I'm not using yet
    #"exterior": {"is_interior": False} ## Can be set scene-wide, so 'all parts of 'graveyard east' are exterior unless otherwise mentioned'. (I say 'can', I mean 'will be when I set it up')
}

plant_type = ["tuber", "legume", "arctic carrot"]

detail_data = { #moved this from item_definitions.

# failure = <10, success = 10-19, crit = 20.
"paper_scrap_details": {"is_tested": True, "failure": "The last three digits are 487, but the rest are illegible.", "success": "It takes you a moment, but the number on the paper is `07148 718 487'. No name, though.", "crit": "The number is `07148 718 487. Looking closely, you can see a watermark on the paper, barely visible - `Vista Continental West`. Do you know that name?"},

"scroll_details": {"is_tested": True, "failure": "Unrolling the scroll, pieces of it fall to dust in your hands.", "crit": "You carefully unroll the scroll, and see a complex drawing on the surface - you've seen something like it in a book somewhere..."},

"puzzle_mag_details": {"is_tested":False, "print_str": "A puzzle magazine. Looks like someone had a bit of a go at one of the Sudoku pages but gave up. Could be a nice way to wait out a couple of hours if you ever wanted to."},

"fashion_mag_details": {"is_tested":False, "print_str": "A glamourous fashion magazine, looks like it's a couple of years old. Not much immediate value to it, but if you wanted to kill some time it'd probably be servicable enough."},

"gardening_mag_details": {"is_tested":False, "print_str": f"A gardening magazine, featuring the latest popular varieties of {random.choice(plant_type)} and a particularly opinionated think-piece on the Organic vs Not debate. Could be a decent way to wait out a couple of hours if you ever wanted to."},

"mail_order_catalogue_details": {"is_tested":False, "print_str": "A mail order catalogue, with the reciever's address sticker ripped off. Clothes, homegoods, toys, gadgets - could be a nice way to wait out a couple of hours if you ever wanted to."},

"local_map_details": {"is_tested":False, "print_str": "A dated but pretty detailed map of the local area. Could be good for finding new places to go should you have a destination in mind."},

"damp_newspaper": {"is_tested":True, 1: "Despite your best efforts, the newspaper is practically disintegrating in your hands. You make out something about an event in ballroom, but nothing beyond that..", 3: "After carefully dabbing off as much of the mucky water and debris as you can, you find the front page is a story about the swearing in of a new regional governor, apparenly fraught with controversy.", 4: "Something about a named official and a contraversy from years ago where a young man went missing in suspicious circumstances."} ## no idea where this would go, but I need some placeholder text so here it is.
}

class ItemInstance:
    """
    Represents a single item in the game world or player inventory.
    """
    def set_hidden(self): # so the noun won't be considered for picking up etc outside of whatever un-hiddening act I come up with.
        # I don't know if I need this anymore? Probably keep it for now though...
        self.held_verb_actions = self.verb_actions
        self.verb_actions = set()

    def end_hidden(self):

        self.verb_actions = self.held_verb_actions
        self.held_verb_actions = set()


    def clean_item_types(self, attr):


        if isinstance(self.item_type, str):
            if isinstance(attr, str):
                if attr == self.item_type:
                    self.item_type = set()
                else:
                    attr = attr + " " + self.item_type
                    self.item_type = set()
            elif isinstance(attr, set):
                attr.add(self.item_type)
                self.item_type = set()

        elif isinstance(self.item_type, list):
            #print(f"self.item_type was a list: {self.item_type}")
            temp = self.item_type
            self.item_type = set()
            for item in temp:
                self.item_type.add(item)

        if isinstance(attr, str):
            #print(f"cleaning itemtypes: `{attr}` (type: {type(attr)}), existing: {self.item_type} type: {type(self.item_type)}")
            if "{" in attr:
                _, type_item = attr.split("{")
                type_item, _ = type_item.split("}")
                type_item = type_item.replace("'", "")
                parts = type_item.split(", ")
                #self.item_type = self.item_type | set(parts)
                for part in parts:
                    if part != None and part not in self.item_type:
                        self.item_type.add(part)
                        #print(f"self.item_types: {self.item_type}")
            else:
                self.item_type.add(attr)

        elif isinstance(attr, set|list|tuple):
            #print(f"ITEM set/list/tuple: {attr}")
            #self.item_type = self.item_type | set(attr)
            for item_type in attr:
                self.item_type.add(item_type)

        # removed this section again; fixed item_dict_gen to actually have all the flags it needs initially. Now itemReg only has to get the formatting right and find the instances where relevant..

        return self.item_type


    def __init__(self, definition_key:str, attr:dict):
        #print(f"\n\n@@@@@@@@@@@@@@@@@ITEM {definition_key} in INIT ITEMINANCE@@@@@@@@@@@@@@@\n\n")
        #print(f"definition_key: {definition_key}, attr: {attr}")
        self.id = str(uuid.uuid4())  # unique per instance
        for attribute in attr:
            setattr(self, attribute, attr[attribute])

        self.name:str = definition_key
        self.print_name = self.name
        if not attr.get("nicenames"):
            self.nicename = f"a {self.name}"
        else:
            self.nicename:str = attr["nicenames"].get("generic")
            if not self.nicename:
                for entry in attr["nicenames"]:
                    self.nicename = attr["nicenames"][entry]
                    break # entirely arbirary. Need to rejig the description-selection function to do nicenames too.
        self.is_transition_obj = False
        self.item_type = self.clean_item_types(attr["item_type"])
        self.colour = None
        self.descriptions:dict = attr.get("descriptions") # dict of different descriptions for different item states.
        """
Note on descriptions: if self.descriptions, will have different descriptions depending on type, flags. Will automate it with a dict later (which flags determine which description options). Not sure yet if all items will always have descriptions, or or simple objects with no alternate names will only ever have 'description' and use that always. Will allow for self.description as-is for now.
        """
        self.description:str = attr.get("description") # will be initd shortly, depending on item conditions. Use default if found for simple objects with no alt names.
        #print(f"Name: {self.name} // self.description in init: {self.description}")
        self.starting_location:dict = attr.get("starting_location") # currently is styr
        self.verb_actions = set()

        self.location:cardinalInstance = loc.no_place
        self.event = None
        self.is_event_key = False

        if attr.get("exceptions"):
            if attr["exceptions"].get("starting_location"):
                if isinstance(attr["exceptions"]["starting_location"], cardinalInstance):
                    self.location = attr["exceptions"]["starting_location"]
                    self.starting_location = attr["exceptions"]["starting_location"]

        if attr.get("alt_names"):
            self.alt_names = set(i for i in attr.get("alt_names"))
        else:
            self.alt_names = None

 #     INITIAL FLAG MANAGEMENT
        #print(f"VARS before attributes are assigned: {vars(self)}")
        for attribute in ("can_pick_up", "can_be_opened", "print_on_investigate", "can_be_locked"):
            if hasattr(self, attribute):
                    self.verb_actions.add(attribute)

        if hasattr(self, "can_be_charged"):
            self.verb_actions.add("can_charge")

        if "print_on_investigate" in attr:
            self.verb_actions.add("print_on_investigate")

            details = self.name + "_details"
            details = details.replace(" ", "_")

            self.description_detailed = detail_data.get(details)

        if "container" in self.item_type:
            self.verb_actions.add("is_container")
            registry.by_container[self] = set()
            if hasattr(self, "starting_children"):
                registry.new_parents.add(self.id)

        if hasattr(self, "is_hidden") and self.is_hidden:
            self.set_hidden()

        if hasattr(self, "enter_location"):
            self.enter_location = loc.place_by_name(self.enter_location)
            #print(f"self.enter_location: {self.enter_location}")
            setattr(self.enter_location, "entry_item", self)
            setattr(self.enter_location, "location_entered", False)
            self.is_transition_obj = True

        if hasattr(self, "exit_to_location"):
            self.exit_to_location = loc.by_name.get(self.exit_to_location)
            setattr(self.exit_to_location, "exit_item", self)

    def __repr__(self):
        return f"<ItemInstance {self.name} / ({self.id}) / {self.location.place_name} / {self.event if hasattr(self, "event") else ''}/ {(self.has_multiple_instances if hasattr(self, 'has_multiple_instances') else '')}>"


class itemRegistry:
    """
    Central manager for all item instances.
    Also keeps a location-indexed lookup for fast "what's here?" queries.
    """

    def __init__(self):
        #print(f"Init in lootregistry is running now.") ## it only seems to be running once.
        #sleep(1)

        self.instances = set()  # CHANGE: Is now a set.
        self.by_id = {}    # id -> ItemInstance
        self.by_location = {}  # (cardinalInstance) -> set of instances
        self.by_name = {}        # definition_key -> set of instances
        self.by_alt_names = {} # less commonly used variants. Considering just adding them to 'by name' though, I can't imagine it matters if they're alt or original names... # changed mind, nope. Not duplicating them randomly for no good reason. Just an alt:name lookup.

        self.by_category = {}        # category (loot value) -> set of instance IDs
        self.by_container = {}

        self.plural_words = {}

        self.temp_items = set()
        self.updated = set()

        self.new_parents = set() ## new_parents, ID is added to all containers. Then after initial generation, force a parent/child check.
        self.child_parent = {} # just for storing the parings, for comparing child/parents directly when midway through the generation to keep things straight.

        self.contained_in_temp = set() # This was for items that will be contained in something (by inst.contained_in) but not registered yet in case the container itself hasn't been inited yet. so was probably intending to add a loop at the end to put all the contained objs in their containers once everything was instanced.

        self.event_items = {}
        self.keys = set()

        self.locks_keys = {}

        self.item_defs = {}#item_defs

    # -------------------------
    # Creation / deletion
    # -------------------------

    def init_single(self, item_name, item_entry = None):
        #print(f"\n\n[init_single] ITEM NAME: {item_name}")
        #print(f"[init_single] ITEM ENTRY: {item_entry}\n\n")
        if not item_entry:
            if self.item_defs.get(item_name):
                item_entry = self.item_defs[item_name]
            else:
                print(f"No item entry provided for `{item_name}` and no entry found in registry.item_defs. Cannot build without knowing what it is.")
                exit()
        inst = ItemInstance(item_name, item_entry)
        all_items_generated.add(inst)
        self.instances.add(inst)

        self.item_defs[item_name] = item_entry

        if not self.by_name.get(inst.name):
            self.by_name[inst.name] = []
        self.by_name[inst.name].append(inst)
        self.by_id[inst.id] = inst

        loot_type = item_entry.get("loot_type")

        if loot_type:
            if isinstance(loot_type, list):
                for option in loot_type:
                    self.by_category.setdefault(option, set()).add(inst)
            else:
                self.by_category.setdefault(loot_type, set()).add(inst)

        location = item_entry.get("starting_location")
        if not location and not hasattr(inst, "contained_in") and item_entry.get("exceptions"):
            location = item_entry.get("exceptions").get("starting_location")

        if location:
            if isinstance(location, cardinalInstance):
                inst.location = location
                self.by_location.setdefault(location, set()).add(inst)

            elif not hasattr(inst, "contained_in") or inst.contained_in == None:
                cardinal_inst = loc.by_cardinal_str(location)
                self.by_location.setdefault(cardinal_inst, set()).add(inst)
                inst.location = cardinal_inst


        if item_entry.get("alt_names"):
            for altname in item_entry.get("alt_names"):
                self.by_alt_names[altname] = item_name

        if hasattr(inst, "starting_children") and getattr(inst, "starting_children"):
            #print(f"INST {inst} has starting children: {inst.starting_children}")
            self.new_parents.add(inst.id)
            registry.generate_children_for_parent(parent=inst)

        if hasattr(inst, "is_key"):
            self.keys.add(inst)

        self.instances.add(inst)

        self.init_descriptions(inst)

        return inst

    def get_item_from_defs(self, item_name):

        if item_name in list(self.item_defs):
            inst = self.init_single(item_name, self.item_defs[item_name])
            all_item_names_generated.append((inst, "get_item_from_defs"))
            return inst


    def delete_instance(self, inst: ItemInstance):
        print(f"Deleting inst: {inst}")
        if inst.location and inst.location in self.by_location:
            self.by_location[inst.location].remove(inst)

            if inst.location == loc.inv_place:
                loc.inv_place.items.remove(inst)

        inst.location = loc.no_place
        if hasattr(inst, "contained_in"):
            container = inst.contained_in
            container.children.remove(inst)
            inst.contained_in = None
        self.by_name.get(inst.name, list()).remove(inst)

        inst = self.instances.remove(inst)
        if not inst:
            return
        print(f"Still inst: {inst}")

    def item_def_by_attr(self, attr_str="", loot_type=None, open=None, locked=None):

        if open or locked:
            items = (i for i in self.item_defs if "container" in i.get("item_type"))
#            if container is not None and item.container is not container:
#                continue
#            if open is not None and item.is_open != open:
#                continue
#            if locked is not None and item.is_locked != locked:
#                continue
        if attr_str:
            items = (i for i in self.item_defs if hasattr(i, attr_str))

        if loot_type:
            items = list()
            for item, vals in self.item_defs.items():
                if "loot_type" in vals and loot_type in vals.get("loot_type"):
                    items.append(item)
             #yield items
        return items

    def items_by_attr(self, attr_str="", loot_type=None, open=None, locked=None, location=None):

        if location:
            items = self.by_location[location]

        if open or locked:
            items = (i for i in self.instances if "container" in i.item_type)

        if attr_str:
            items = (i for i in self.instances if hasattr(i, attr_str))

        if loot_type:
            print(f"Loot type: {loot_type}")
            print(f"i for i in self.instances if hasattr(i, 'loot_type'): {(i for i in self.instances if hasattr(i, 'loot_type'))}")
            items = (i for i in self.instances if hasattr(i, "loot_type") and loot_type in i.loot_type)

        #yield items
        return items

    def get_local_items(self, include_inv = False, by_name = None):
        logging_fn()
        local_items = set()
        includes_inv = False

        location_items = self.by_location.get(loc.current)
        print(f"location items in get_local_items: {location_items}")
        if location_items:
            local_items = local_items | set(location_items)

        if include_inv and loc.inv_place.items:
            local_items = local_items | loc.inv_place.items
            includes_inv = True

        if by_name:
            from misc_utilities import get_inst_list_names
            if by_name in get_inst_list_names(local_items):
                #print("get local items by name.")
                local_items = list(local_items)
                local_items = set(i for i in local_items if i.name == by_name)
                print(f"\nlocal items by name (should only include items by name `{by_name}`): {local_items}")
            else:
                return None
        return local_items#, includes_inv #not that useful perhaps. Anywhere it matters I'd need the lists separately, so maybe we leave this off.

    def generate_children_for_parent(self, parent=None):
        logging_fn()

        def get_children(parent:ItemInstance):

            #print("for child in parent.starting_children")
            instance_children = []
            instance_count = 0
            target_child = None
            if isinstance(parent.starting_children, str):
                temp = []
                temp.append(parent.starting_children)
                parent.starting_children = temp

            if parent.starting_children == None:
                #print(f"parent.starting_children None: {parent.starting_children}")
                return
            #print(f"parent.starting_children not == None: {parent.starting_children}")
            if parent.starting_children != None and isinstance(parent.starting_children, list|set|tuple):
                #print(f"for child in parent.starting_children: {parent.starting_children}")

                for child in parent.starting_children:
                    #print(f"CHILD: {child}")
                    def find_or_make_children(child, parent, instance_count, instance_children):

                        if isinstance(child, ItemInstance):
                            instance_children.append(child)
                            instance_count += 1
                            parent.children.add(target_child)
                            target_child.contained_in = parent
                            return instance_count, instance_children

                        if child in self.item_defs:
                            if hasattr(self, "alt_names") and self.alt_names.get(child):
                                #child = self.by_alt_names[child]
                                new_child = self.alt_names[child] # what is this for. This isn't doign anything.
                                #print(f"TARGET CHHILD: {child} # new_child: {new_child}")
                            #print(f"BY alt names: {self.alt_names}")
                            target_child = self.init_single(child, self.item_defs[child])
                            all_item_names_generated.append((target_child, "generate_child from item_defs"))
                        else:
                            target_child = use_generated_items(child)
                            if not target_child:
                                #print(f"No target child, calling new_item_from_str for child {child} and parent {parent}")
                                target_child = new_item_from_str(item_name=child, in_container=parent)
                                all_item_names_generated.append((child, "generate_child item_from_str"))

                        if target_child:
                            instance_children.append(target_child)
                            target_child.contained_in = parent
                            if not hasattr(parent, "children") or parent.children == None:
                                parent.children = set()
                            parent.children.add(target_child)
                            target_child.contained_in = parent

                        #exit()
                        return instance_count, instance_children

                    instance_count, instance_children = find_or_make_children(child, parent, instance_count, instance_children)

                if len(instance_children) == len(parent.starting_children):
                    parent.starting_children = instance_children
                    registry.new_parents.remove(parent.id)
                else:
                    if (len(instance_children) + len(registry.child_parent) == len(parent.starting_children)) or (len(parent.starting_children) == instance_count):
                        registry.new_parents.remove(parent.id)
                    else:
                        exit(f"Not all children found/made as instances. Str list:\n   {parent.starting_children}\nInstance list:\n    {instance_children}\nchild/parent dict: {registry.child_parent}") # again, right now hard exit if this ever fails. Need to see why if it does.
        # Was going to do keys here too, but I don't think I will. Maybe do those at runtime, they're not as widely relevant as children so maybe just do that identification when looked for? Though having said that, that means I have to be aware of whenever they might be checked for... Yeah I should do it here actually.
        if parent:
            get_children(parent)

        else:
            if registry.new_parents and registry.new_parents != None:
                for parent in registry.new_parents:
                    if isinstance(parent, str):
                        parent = registry.by_id.get(parent)
                    get_children(parent)


    def clean_relationships(self):

        def cleaning_loop():

            itemlist = frozenset(self.by_id)

            for item_id in itemlist:
                item = self.by_id.get(item_id)

                if not item:
                    exit(f"Failed to get instance by id in cleaning_loop for instance ({item_id}).")

                if hasattr(item, "requires_key") and not isinstance(getattr(item, "requires_key"), bool):
                    if isinstance(item.requires_key, ItemInstance):
                        continue
                    key_found = False
                    for maybe_key in registry.keys:
                        if hasattr(maybe_key, "unlocks") and getattr(maybe_key, "unlocks"):
                            continue

                        if maybe_key.name == getattr(item, "requires_key"):
                            if hasattr(maybe_key, "is_key_to") and maybe_key.is_key_to == item.name:

                                self.locks_keys[item] = maybe_key
                                self.locks_keys[maybe_key] = item
                                item.requires_key = maybe_key
                                setattr(maybe_key, "unlocks", item)
                                key_found = True

                    if not key_found:
                        if self.item_defs.get(getattr(item, "requires_key")):
                            target_obj = self.init_single(getattr(item, "requires_key"), self.item_defs.get(getattr(item, "requires_key")))
                            all_item_names_generated.append((item, "generate key from item_defs"))
                            if not target_obj:
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
                            item.requires_key = target_obj # added this, should make it more bilateral.
                            setattr(target_obj, "unlocks", item)
                        else:
                            exit(f"Failed to find key for {item}'s {item.requires_key}.")

        #starting_count = len(self.instances)
        try:
            cleaning_loop()
        except Exception as E:
            print(f"Exception: {E}")

        #if len(self.instances) == starting_count:
            #print()#"Huh, count is the same. This may or may not matter; only really matters if you were expecting a new item to be dynamically generated.")


    def check_item_is_accessible(self, inst:ItemInstance) -> tuple[ItemInstance|None, int]:
        logging_fn()
        from misc_utilities import is_item_in_container, accessible_dict

        #accessible_dict = { ## just for printing, for my own sake because my memory is broken
        #    0: "accessible",
        #    1: "in a closed local/accessible container",
        #    2: "in a locked local/accessible container",
        #    3: "in an open container in your inventory",
        #    4: "in an open container accessible locally, can pick up but not drop",
        #    5: "in inventory",
        #    6: "not at current location",
        #    7: "other error, investigate",
        #    8: "is a location exterior"
        #    9: "item is hidden" (must be discovered somehow, not shown in general 'look around' views.)
        #   10: "item is transitional, treat as local."
        #}

        #   10: "item is transitional" # may be in another location, but is treated as if local. (Really this is just '0', but I've written it here so I might remember.)

        confirmed_inst = None
        confirmed_container = None
        reason_val = 7

        def run_check(inst):
            confirmed_inst = None
            confirmed_container = None
            reason = 7
            meaning = "other error, investigate"

            if hasattr(inst, "is_hidden") and inst.is_hidden == True:
                return inst, None, 9, accessible_dict[9]

            #from set_up_game import game
            inventory_list = loc.inv_place.items# game.inventory # using place instead of game.inventory for item storage. Not sure how I feel about it yet but trying it out.

            local_items_list = self.get_item_by_location(loc.current)
            #print(f"Local_items_list in run_check: {local_items_list}")
            container, inst = is_item_in_container(inst)

            if inst in inventory_list and not container:
                confirmed_inst = inst
                reason = 5
                meaning = accessible_dict[reason]
                return confirmed_inst, None, reason, meaning

            def in_local_items_list(inst, inst_list):
                temp_inst = None
                if inst_list:
                    if isinstance(inst_list, list|set|tuple):
                        if inst in inst_list:
                            temp_inst = inst
                    else:
                        if isinstance(inst_list, ItemInstance):
                            if inst_list == inst:
                                temp_inst = inst
                    return temp_inst
                else:
                    #print("No items at this location.")
                    return None

            if container:
                if container in inventory_list:
                    confirmed_container = container
                    if (hasattr(confirmed_container, "is_closed") and getattr(confirmed_container, "is_closed")):
                        reason = 1
                    elif (hasattr(confirmed_container, "is_locked") and getattr(confirmed_container, "is_locked")):
                        reason = 2
                    else:
                        reason = 3
                else:
                    confirmed_container = in_local_items_list(container, local_items_list)
                    if confirmed_container:
                        if hasattr(confirmed_container, "is_open") and confirmed_container.is_open == False:
                            print(f"Container {confirmed_container.name} is closed by is_open flag.")
                            reason = 1
                        elif hasattr(confirmed_container, "is_locked") and getattr(confirmed_container, "is_locked"):
                            print(f"Container {confirmed_container} is locked.")
                            reason = 2
                        else:
                            reason = 4
                    else:
                        reason = 6
            else:
                confirmed_inst = in_local_items_list(inst, local_items_list)
                if confirmed_inst:
                    reason = 0
                else:
                    if inst in inventory_list:
                        confirmed_inst = inst
                        reason = 5
                    else:
                        if hasattr(inst, "is_transition_obj"):
                            if hasattr(inst, "enter_location") and hasattr(inst, "enter_location") and inst.enter_location ==  loc.current.place:
                                reason = 0
                            else:
                                reason = 6
                        elif hasattr(inst, "is_loc_exterior") and inst.location.place == loc.current.place:
                            reason = 8

                        else:
                            reason = 6

            meaning = accessible_dict[reason]

            if confirmed_inst:
                #print(f"inst: {inst} / meaning: {meaning}")
                return confirmed_inst, confirmed_container, reason, meaning

            #print(f"not confirmed inst: {inst} / meaning: {meaning}, item vars: {vars(inst)}")
            return None, confirmed_container, reason, meaning

        #if not isinstance(inst, ItemInstance):
        #    if isinstance(inst, str) and inst != None:
        #        named_instances = self.instances_by_name(inst)
        #        if named_instances:
        #            for item in named_instances:
        #                confirmed_inst, confirmed_container, reason_val, meaning = run_check(item)

        confirmed_inst, confirmed_container, reason_val, meaning = run_check(inst)

        if confirmed_inst != None:
            return confirmed_inst, confirmed_container, reason_val, meaning

        return inst, confirmed_container, reason_val, meaning

    def set_print_name(self, inst:ItemInstance, new_print_name:str):
        logging_fn()
        inst.print_name = new_print_name

    def get_parent_details(self, inst, old_container, new_container)->tuple[ItemInstance, bool, ItemInstance]:
        was_in_container = False
        parent = None
        if hasattr(inst, "contained_in"):
            #print(f"inst.contained in: {inst}.{inst.contained_in}")
            if old_container != None:
                parent = old_container
            else:
                parent = inst.contained_in
            if parent:
                was_in_container = True
        if new_container:
            if not hasattr(new_container, "children") or new_container.children == None:
                new_container.children = set()

        return parent, was_in_container, new_container


    def combine_clusters(self, shard:ItemInstance, target: (cardinalInstance|ItemInstance)):
        ## DROPPING TO CLUSTER IN LOCATION/CONTAINER
        logging_fn()
        target_is_location = False
        if isinstance(target, cardinalInstance):
            target_is_location = True

        if shard.location != loc.inv_place:
            print(f"\n{shard} is not in inv_place. This is bad, how are we combining if not removing from inventory?\n\n\n")
        # get cluster:
        if target_is_location:
            local_items = self.get_local_items()
            local_named = list()
            if local_items:
                print(f"All local items in combine_clusters: ({local_items})")
                for item in local_items:
                    if item.name == shard.name:
                        local_named.append(item)
                        print(f"ITEM in named cluster list: {item}, name: {item.name}, has_multiple_instances: {(item.has_multiple_instances if hasattr(item, 'has_multiple_instances') else 'no has_multiple_instances')}")
                print(f"Local named: {local_named}")
                if local_named and len(local_named) > 1:
                    print(f"Multiple items in cluster with name {shard.name}. This should not be possible, as I should be combining with the first one found and then returning that one, so I should never get to a point where there's more than one. Cluster list: {local_items}. Incoming inst is {shard}")
                elif local_named:
                    compound_target = list(local_named)[0]
                    total_instances = shard.has_multiple_instances + compound_target.has_multiple_instances
                    compound_target.has_multiple_instances = total_instances
                    shard.has_multiple_instances = 0
                    shard.location = loc.no_place
                    if shard in self.by_location[loc.inv_place]:
                        self.by_location[loc.inv_place].remove(shard)
                    else:
                        print(f"{shard} was not in by_location[loc.inv_place].")
                    if shard in loc.inv_place.items:
                        loc.inv_place.items.remove(shard)
                    else:
                        print(f"{shard} was not in by_location[loc.inv_place].")
                    return shard, compound_target

            print(f"No local items by the name `{shard.name}`")
            return shard, "no_local_compound"


        if not hasattr(shard, "has_multiple_instances") or not hasattr(compound_target, "has_multiple_instances"):
            return False, False

        if shard.name != compound_target.name:
            return False, False

        if shard.has_multiple_instances > 1:
            print(f"How can the inst I want to combine has multiple instances? This should not be possible, I can't move from loc to loc if not loc.inv_place so it should be coming from inv, this singular. {shard}: has_multiple_instances: {shard.has_multiple_instances}")
            exit()
            return False, False
        total_instances = shard.has_multiple_instances + compound_target.has_multiple_instances
        print("total_instances: ", total_instances, "inst.has_multiple_instances: ", shard.has_multiple_instances, "+ inst_at_target: ", compound_target.has_multiple_instances)
        compound_target.has_multiple_instances = total_instances
        shard.has_multiple_instances = 0

        print(f"Combined clusters. New instance count: {total_instances}")
        return shard, compound_target

    def separate_cluster(self, compound_inst:ItemInstance, origin, origin_type:str):
        ## PICKING UP FROM CLUSTER IN LOCATION/CONTAINER
        logging_fn()
        print(f"ORIGIN: {origin}")
        if not hasattr(compound_inst, "has_multiple_instances"):
            return False, None

        new_def = registry.item_defs.get(compound_inst.name)
        if origin_type == "location":
            new_def["exceptions"] = {"starting_location": origin}

        shard = registry.init_single(compound_inst.name, new_def)
        print(f"New inst {shard} generated from cluster {compound_inst}")
        # checks #
        if origin_type == "location":
            print(f"Origin type loc, origin: {origin}")
            #if new_inst.location != origin:
            #    print(f"Failed to set location for new cluster instance. Expected {origin}, got {new_inst.location}.")
            #    exit() # catastropic failure.
            #print(f"new inst location set at {inst.location}")
            #self.by_location[singular_inst.location].add(singular_inst) # should not be adding the singular, this is what is being removed and added to inv.
            if compound_inst not in self.by_location[origin]:
                print(f"For some reason the compound instance isn't already at {origin}")
                self.by_location[origin].add(compound_inst)
            if shard in self.by_location[origin]:
                print(f"singular in {origin}")
                self.by_location[origin].remove(shard)
            else:
                print(f"singular not in {origin}")


        elif origin_type == "container":
            existing_contained_item = None
            container = origin
            if "container" not in container.item_type:
                print(f"Container {container} is not a container...")
                return False, None
            for item in container.children:
                if item.name == compound_inst.name:
                    existing_contained_item = item
                    break
            if not existing_contained_item:
                print(f"No multiple_instances item in {origin}")
                container.children.add(compound_inst)

            if existing_contained_item:
                compound_inst = existing_contained_item

            shard.location = loc.no_place
            #print(f"New inst {new_inst} contained in {new_inst.contained_in}, expecting {origin}, location: {new_inst.location} (should be 'None')")

        else:
            print(f"No origin? {shard} // critical failure.")
            exit()

        starting_instance_count = compound_inst.has_multiple_instances
        #print(f"starting instance count: {starting_instance_count}")
        compound_inst.has_multiple_instances = starting_instance_count - 1
        shard.has_multiple_instances = 1  #No wait. Need to check if there's an instance at the destination before I do this. Will do that first. #no wait no wait - this is putting something back where it was removed to. That check does need to happen but earlier in move_item, not here.
        #print(f"Ending counts: original inst: {inst.has_multiple_instances}, new inst: {new_inst.has_multiple_instances}")
        #generate a new item (new_inst) with multiple_instances = inst.multiple_instances -1
        # add new_inst to old_loc/old_container
        # reduce inst.multiple_instances by 1
        # update descriptions for inst and new_inst.
        ## so: The original is the thing picked up, important so that the check to make sure it arrived in the inventory still passes. The new one is left behind.
        print("compound_inst.has_multiple_instances: ", compound_inst.has_multiple_instances)
        print("shard.has_multiple_instances: ", shard.has_multiple_instances)
        shard.location = loc.inv_place
        loc.inv_place.items.add(shard)
        self.by_location[loc.inv_place].add(shard)
        print(f"returning {shard}")
        return compound_inst, shard # <- separated, new_singular

    # -------------------------
    # Movement
    # -------------------------

    def move_cluster_item(self, inst:ItemInstance, location:cardinalInstance=None, new_container:ItemInstance=None, old_container:ItemInstance=None)->ItemInstance:

        old_loc = inst.location
        parent, was_in_container, new_container = self.get_parent_details(inst, old_container, new_container)

        is_drop = "unconfirmed"

        if location == loc.inv_place:
            is_drop = False

        if is_drop:
            target = None
            if location:
                target = location
            if new_container:
                target = new_container
            if not target:
                print(f"No target: in move_cluster_items for {inst}, but no location or new_container was given.")
            # The following only applies if move to location. Need to also get the logic in for containers.
            shard, compound_target = self.combine_clusters(inst, target)
            if compound_target == "no_local_compound":
                return shard, "process_as_normal"
            print(f"original inst: {inst}, location: {inst.location}\nShard: {shard}, location: {shard.location}\nCompound target: {compound_target}, location: {compound_target.location}")
            print("moving shard from inv to current loc, if cluster at current loc, combine shard w cluster and remove shard from inv and instances.")
            if compound_target.has_multiple_instances == 0:
                print(f"Compound_target {compound_target} is exhausted, removing from everywhere.")

                self.delete_instance(compound_target)
                from testing_coloured_descriptions import init_loc_descriptions
                init_loc_descriptions(loc.current.place, loc.current)
            if isinstance(shard, ItemInstance) and isinstance(compound_target, ItemInstance):
                self.delete_instance(shard)
            self.init_descriptions(compound_target)
            return shard, None
        #original:
            """if "is_cluster" in inst.item_type:
                print("is cluster and location is not none.")
                if self.get_local_items(by_name=inst.name):
                    print(f"there are local items with this name: {self.get_local_items(by_name=inst.name)}.")
                    if location != loc.inv_place: ## == am dropping, so combine inst with local cluster.
                        print(f"location is not inv place. Need to add {inst} to local cluster if found.")
                #print("is cluster, passed first get_local_items")
                        print(f"list(self.get_local_items(by_name=inst.name))[0]: {list(self.get_local_items(by_name=inst.name))[0]}")
                        singular_inst, combined_inst = self.combine_clusters(inst)
                        print(f"AFTER COMBINE_CLUSTER: \n Original inst: {inst}, location: {inst.location}\n Singular inst: {singular_inst}, location: {singular_inst.location}\nCombined inst: {combined_inst}, location: {combined_inst.location}\n")
                        if combined_inst:
                            print(f"Combined inst: {combined_inst}, location: {combined_inst.location}")
                            print(f"Original inst: {inst}, location: {inst.location}")
                            #print(f"Combined_inst: {combined_inst}")
                            done = combined_inst
                            updated.add(combined_inst)
                            if inst in self.by_location[location]:
                                self.by_location[location].remove(inst)
                            inst.location = loc.no_place
                            if inst in loc.inv_place.items:
                                loc.inv_place.items.remove(inst)"""

        print("if not drop, assume pick up - we have a cluster in a location, need to separate a shard, add it to inv, and adjust cluster counts accordingly.")
        # Need parents etc. eeeeh.
        origin = (parent if was_in_container else old_loc)
        success, shard = self.separate_cluster(inst, origin=origin, origin_type="container" if was_in_container else "location")
        if not success:
            print(f"separate cluster failed. Reported shard: {shard}, original inst: {inst}, origin: {origin}")
            exit()
        if success and isinstance(success, ItemInstance):
            if hasattr(success, "has_multiple_instances"):
                if success.has_multiple_instances == 0:
                    self.delete_instance(success)
    # original:
        """if "is_cluster" in inst.item_type: # holy shit, it seems to work. Dropping a glass shard to a location where one already exists makes them combine, but picking them up keeps them separate. And referring to them by sing/plur works in all tests I've tried so far. Sheeeeit.
            separated = False
            print(f"Item {inst} is cluster.")
            if not done:
                #print("Not done, probably wasn't dropping from inv to loc.")
                separated, single_inst = self.separate_cluster(inst, origin=parent if was_in_container else old_loc, origin_type="container" if was_in_container else "location")
                #print(f"inst: {inst}, new_cluster: {new_cluster}")
                if separated:
                #print("inst separated")
                    updated.add(single_inst)
                    updated.add(inst)
                    done = single_inst
                    print(f"Done (new single): {done}, old cluster: {inst}")

            if inst.has_multiple_instances == 0:
                print(f"This instance [{inst}] has no multiples left; deleting.")
                #if done:
                if inst in updated:
                    updated.remove(inst)
                    #print(f"removed {inst} from updated")
                #print(f"inst: {inst}, vars: {vars(inst)}")
                if inst in self.instances:
                    self.delete_instance(inst)
                    print(f"delted {inst} from instances")"""
        return shard, None #second part is just for notes in case of 'treat as normal' or whatever string I wrote earlier. #or whatever is the correct output for the case. Likely

    def move_item(self, inst:ItemInstance, location:cardinalInstance=None, new_container:ItemInstance=None, old_container:ItemInstance=None, no_print=False)->ItemInstance:
        logging_fn()
        from misc_utilities import assign_colour

        if "is_cluster" in inst.item_type:
            outcome, other = self.move_cluster_item(inst, location, new_container, old_container)
            ## outcome == whichever instance should be passed back to verb_actions/event tracking.
            # If picking up, should be the new singular_inst. If dropping, should be the original inst that was added to the compound.
            if other != "process_as_normal":
                return outcome

        # so there are no cluster items being processed from here on out. So I need to make sure that everything done here is also done there.
        """
        remove inst from original location, set to loc.no_place after recording old_loc. If old_loc == loc.inv_place, remove from inv_place.items.
        """
        updated = set()
        was_in_container = False # using this as a check to see if the cluster should use old_loc or parent.

        ## REMOVE FROM ORIGINAL LOCATION ##
        old_loc = inst.location
        if old_loc and old_loc != None:
            if self.by_location.get(old_loc):
                if inst not in self.by_location[old_loc]:
                    print("Inst has a location but isn't in by_location. FIX THIS.")
                else:
                    self.by_location[old_loc].discard(inst)

            if old_loc == loc.inv_place:
                if inst in loc.inv_place.items:
                    loc.inv_place.items.remove(inst)
                inst.location = loc.no_place ## We don't add items to by_location for no_place, this is purely so the location data can be printed in print lines.

        ## MOVE TO NEW LOCATION IF PROVIDED
        if location != None:
            if not self.by_location.get(location):
                self.by_location[location] = set()

            inst.location = location
            self.by_location[location].add(inst)

        return_text = []
        if old_container or new_container or hasattr(inst, "contained_in"):
            parent, was_in_container, new_container = self.get_parent_details(inst, old_container, new_container)
            if parent and was_in_container:
                #print(f"parent.children: {parent.children}")
                parent.children.remove(inst)
                #print(f"parent.children: {parent.children} (should be removed now)")

                return_text.append((f"Item `[{inst}]` removed from old container `[{parent}]`", inst, parent))
                if not no_print:
                    print(f"Removed {assign_colour(inst)} from {assign_colour(parent)}.")
                updated.add(parent)

            if new_container:
                new_container.children.add(inst) # Added this, it wasn't adding items as children to containers.
                inst.contained_in = new_container
                updated.add(new_container)

                return_text.append((f"Added [{inst}] to new container [{new_container}]", inst, new_container))
                print(f"Added {assign_colour(inst)} to {assign_colour(new_container)}.")
            else:
                inst.contained_in = None

        for item in updated:
            self.init_descriptions(item)

        if location == loc.inv_place:
            location.items.add(inst)

        return inst

    def move_from_container_to_inv(self, inst:ItemInstance, parent:ItemInstance=None) -> ItemInstance:
        logging_fn()
        if parent == None:
            parent = inst.contained_in
        result = self.move_item(inst, location = loc.inv_place, old_container=parent)
        return result


    # -------------------------
    # Lookup
    # -------------------------
    def get_instance_from_id(self, inst_id:str)->ItemInstance:
        logging_fn()

        return self.instances.get(inst_id)


    def get_item_by_location(self, loc_cardinal:cardinalInstance=None)->list:
        logging_fn()

        if loc_cardinal == None:
            loc_cardinal = loc.current

        elif isinstance(loc_cardinal, str):
            loc_cardinal = loc.by_cardinal_str(loc_cardinal)

        elif isinstance(loc_cardinal, placeInstance):
            print(f"Loc_cardinal in get_item_by_location is a Place: {loc_cardinal}")
            traceback_fn()
            return

        if isinstance(loc_cardinal, cardinalInstance):
            items_at_cardinal = self.by_location.get(loc_cardinal)
            if items_at_cardinal:
                return items_at_cardinal


    def instances_by_name(self, definition_key:str)->list:
        logging_fn()

        if not isinstance(definition_key, str):
            if isinstance(definition_key, list):
                definition_key = definition_key[0]
        if self.by_name.get(definition_key):
            return self.by_name.get(definition_key)

        elif self.by_alt_names.get(definition_key):
            return self.by_name.get(self.by_alt_names.get(definition_key))

        #print(f"self.by_alt_names: {self.by_alt_names}")

    def instances_by_container(self, container:ItemInstance)->list:
        logging_fn()
        return [i for i in self.by_container.get(container, list())]


    def instances_by_category(self, category):
        logging_fn()
        return self.by_category.get(category, set())


    # -------------------------
    # Helpers
    # -------------------------

    def random_from(self, selection:int|str)->list:
        logging_fn()
        import random
        loot_table = {
            1: "minor_loot",
            2: "medium_loot",
            3: "great_loot",
            4: "special_loot"
        }

        """Pick a random item name from a category (int or str)."""
        if isinstance(selection, int):
            category = loot_table[selection]
        else:
            category = selection
        items = list(self.by_category.get(category, set()))

        return random.choice(items)# if items else "No Items (RANDOM_FROM)"

    def describe(self, inst: ItemInstance, caps=False)->str:
        logging_fn()

        if not hasattr(inst, "description"):
            return "You see nothing special."

        description = inst.description

        if caps:
            from misc_utilities import smart_capitalise
            description = smart_capitalise(description)

        if "[[]]" in description:
            description = description.replace("[[]]", f"{inst.print_name}")
        if description:
            return description


    def init_descriptions(self, inst: ItemInstance):
        logging_fn()
        from misc_utilities import has_and_true
        orig_description = inst.description
        #print(f"orig_description: {orig_description}")
        description = None
        starting_children_only = False

        if self.alt_names.get(inst.name):
            descriptions = self.item_defs.get(self.alt_names.get(inst.name)).get("descriptions")
            #if descriptions:
                #print(f"Descriptions from alt_names: {descriptions}")
                #print(f"inst.descriptions: {inst.descriptions}")
            if not hasattr(inst, "descriptions") or not inst.descriptions:
                inst.descriptions = descriptions

        if not inst.descriptions and inst.description:
            #print(f"inst.description: {inst.description}")
            return

        def get_if_open(inst:ItemInstance, label:str):

            if has_and_true(inst, label):
                #getattr(inst.descriptions, f"open_{label}")
                description = inst.descriptions.get(f"open_{label}")
                #description = getattr(inst.descriptions, f"open_{label}")
            else:
                description = inst.descriptions.get(label)
                #description = getattr(inst.descriptions, label)

            if not description:
                return None

            return description

        if "container" in inst.item_type:

            if has_and_true(inst, "children") and has_and_true(inst, "starting_children"):
                starting_children_only = True
                for child in inst.children:
                    if not child in inst.starting_children or has_and_true(child, "hidden"):
                        starting_children_only = False

            if starting_children_only:
                test = get_if_open(inst, "starting_children_only")
                #print(f"TEST: {test}")
                if test:
                    description = test

            elif hasattr(inst, "children") and inst.children:
                long_desc = []
                from testing_coloured_descriptions import compile_long_desc
                from misc_utilities import assign_colour
                if_open = get_if_open(inst, "any_children")
                if if_open:
                    long_desc.append(get_if_open(inst, "any_children"))

                    for child in inst.children:
                        long_desc.append(assign_colour(child, nicename=True))
                        #print(f"long_desc with child: {long_desc}")

                    description = compile_long_desc(long_desc)

            else:
                if not has_and_true(inst, "children") and get_if_open(inst, "no_children"):
                    description = get_if_open(inst, "no_children")

        if not description:
            #print(f"Not description: {inst.name}, description: {description} // descriptions: {inst.descriptions}")
            if hasattr(inst, "descriptions"):
                if not inst.descriptions:
                    inst.descriptions = {}
                    inst.descriptions["generic"] = f"It's a {inst.name}"
                    inst.description = inst.descriptions["generic"]
                    return
                if has_and_true(inst, "is_open") and inst.descriptions.get("if_open"):
                    description = inst.descriptions["if_open"]

                elif hasattr(inst, "is_open") and not getattr(inst, "is_open") and inst.descriptions.get("if_closed"):
                    description = inst.descriptions["if_closed"]

                if inst.descriptions.get("if_singular") and inst.has_multiple_instances == 1:
                    #print(f"IF SINGULAR: {inst.descriptions["if_singular"]}")
                        #print("if_singular desc in init_descriptions")
                        description = inst.descriptions["if_singular"]
                if inst.descriptions.get("if_plural") and inst.has_multiple_instances > 1:
                    #print(f"IF plural: {inst.descriptions["if_plural"]}")
                        #print("if_plural desc in init_descriptions")
                        description = inst.descriptions["if_plural"]

                elif inst.descriptions.get("generic"):
                    description = inst.descriptions["generic"]
                    inst.description = description

        ## Update nicenames ##
        if inst.nicenames.get("if_singular") and inst.has_multiple_instances == 1:
            #print(f"IF SINGULAR: {inst.descriptions["if_singular"]}")
                #print("if_singular nicename in init_descriptions")
                inst.nicename = inst.nicenames["if_singular"]
        if inst.nicenames.get("if_plural") and inst.has_multiple_instances > 1:
            #print(f"IF plural: {inst.descriptions["if_plural"]}")
                #print("if_plural nicename in init_descriptions")
                inst.nicename = inst.nicenames["if_plural"]


        if description:
            #print(f"DESCRIPTION: {description}")
            inst.description = description
            return

        if orig_description:
            return

        print(f"At the end of init_descriptions, no description found for {inst}: {description}")

    def nicename(self, inst: ItemInstance):
        logging_fn()

        if "container" in inst.item_type:
            if inst.children:
                if hasattr(inst, "starting_children") and inst.starting_children:
                    if inst.children == inst.starting_children:
                        return inst.nicename
                return inst.name_any_children

            if not inst.children:
                return inst.name_children_removed

        # often it just uses nicename directly and doesn't pass through this function. Need to update the nicenames when I update the descriptions.
        if inst.nicenames.get("if_singular") and inst.has_multiple_instances == 1:
            #print(f"IF SINGULAR: {inst.descriptions["if_singular"]}")
                print("if_singular nicename in def nicename()")
                inst.nicename = inst.nicenames["if_singular"]
        if inst.nicenames.get("if_plural") and inst.has_multiple_instances > 1:
            #print(f"IF plural: {inst.descriptions["if_plural"]}")
                print("if_plural nicename in def nicename()")
                inst.nicename = inst.nicenames["if_plural"]
        if not inst:
            print("[NICENAME] No such item.")
            return None

        return inst.nicename

    def get_name(self, inst: ItemInstance):
        logging_fn()

        if not inst:
            print("[GET_NAME] No such item.")
            return None
        return inst.name



    def get_duplicate_details(self, inst, inventory_list):
        logging_fn()

        if isinstance(inst, ItemInstance):
            items = self.instances_by_name(inst.name)
        else:
            items = self.instances_by_name(inst)

        if items:
            dupe_list = []
            for thing in inventory_list:
                if thing in items:
                    dupe_list.append(thing)

            return dupe_list
        print(f"{inst} not found in instances by name. {type(inst)}")


    def register_name_colour(self, inst:ItemInstance, colour:str)->str:
        logging_fn()

        inst.colour=colour

        return inst.print_name

    def pick_up(self, inst:str|ItemInstance, location=None, starting_objects=False) -> tuple[ItemInstance, list]:
        logging_fn()

        item_name = None
        if isinstance(inst, str):
            item_name = inst

        if isinstance(inst, set) or isinstance(inst, list):
            inst=inst[0]

        if location == None:
            location = loc.current

        if not isinstance(inst, ItemInstance):
            item_list = self.instances_by_name(inst)
            if item_list and location != loc.current:
                local_items = self.get_item_by_location(location)
                for item in item_list:
                    if local_items:
                        if item in local_items or starting_objects: # hardcode 'allow starting objects regardless'.
                            inst = item
                            break
                    elif starting_objects:
                        inst = item
                        break

            elif item_list and item_list != None:
                inst = item_list[0]

            inst = self.get_item_from_defs(inst)

        if not inst:
            if item_name:
                item = item_name
            loc_card = location.place_name
            print(f"No inst, so calling new_item_from_str for item {item}")
            from item_dict_gen import generator
            item_dict = generator.item_defs.get(item)
            print(f"ITEM DICT: {item_dict}")
            inst = new_item_from_str(item_name=item, loc_cardinal=(loc_card), partial_dict=item_dict) # TODO: replace these with place instances, this is just temp
            print("Failed to find inst in pick_up, generating from str..")

        if not starting_objects and not hasattr(inst, "can_pick_up"):
            print(f"[[Cannot pick up {inst.name} (according to inst.flags)]]")
            print(f"inst.flags: {inst.flags}")
            return None

        # if inst in loc.inv_place.items: ## TODO: Add a check so this only applies to items that can be duplicated. Though really those that can't should not still remain in the world when picked up... so the problem lies in the original pick up in that case, not the dupe.
        #     #print("Item already in inventory. Creating new...") ## Not sure about this.
        #     attr = self.item_defs.get(inst.name)
        #     inst = self.init_single(inst.name, attr)

        new_inst = self.move_item(inst, location = loc.inv_place)

        if not hasattr(self, "starting_location"): # so it only updates once, instead of being the 'last picked up at'. Though that could be useful tbh. Hm.
            self.starting_location = {location} # just temporarily, not in use yet. Needs formalising how it's going to work.
        if isinstance(new_inst, ItemInstance) and new_inst != inst:
            print(f"Picked up {new_inst} instead of {inst}.")
            inst = new_inst
        return inst

    def drop(self, inst: ItemInstance):
        logging_fn()
        #inventory_list = loc.inv_place.items
#
        #if inst not in inventory_list:
        #    print(f"{inst} not in inventory, cannot drop.")
        #    return None, inventory_list
        #inventory_list.remove(inst)
        self.move_item(inst, location = loc.current)
        return inst#, inventory_list


    def complete_location_dict(self):
        logging_fn()

        for placeInstance in loc.places:
            for cardinal in loc.cardinals[placeInstance]:
                self.by_location.setdefault(cardinal, set())


    def get_action_flags_from_name(self, name):
        print(f"get flag for this name: {name}")
        inst = self.instances_by_name(name)
        print(f"Inst: {inst}")
        flag_actions = inst[0].verb_actions
        print(f"flag actions: {flag_actions}")
        return inst


    def add_plural_words(self, plural_words_dict):
        self.plural_words = plural_words_dict

registry = itemRegistry()


def use_generated_items(input_=None):
    import json

    json_to_edit = "dynamic_data/generated_items.json"

    with open(json_to_edit, 'r') as file:
        gen_items = json.load(file)

    if not gen_items or gen_items == {}:
        return

    altered = False

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


def new_item_from_str(item_name:str, input_str:str=None, loc_cardinal=None, partial_dict=None)->str|ItemInstance:

    if partial_dict:
        if partial_dict.get(item_name):
            partial_dict = partial_dict[item_name]

    new_item_dict = {}

    if item_name == "":
        print('Item name is `""` .')
        print(f"item_name: {item_name}, input_str: {input_str}, loc_cardinal: {loc_cardinal}, partial_dict: {partial_dict}")

    if partial_dict.get("item_type"):
        input_str = partial_dict["item_type"]
    if not input_str:
        print("\n")
        printing.print_green(f"Options: {list(type_defaults)}", invert=True)
        print(f"Please enter the default_types you want to assign to `{item_name}` (eg ' key, can_pick_up, fragile ' )")
        input_str = input()

    if not isinstance(input_str, str):
        if isinstance(input_str, list):
            input_str = " ".join(input_str)
        else:
            print(f"new_item_from_str requires a string input, not {type(input_str)}: {input_str}")
            return

    if " " in input_str.strip():
        input_str = input_str.replace(",", "")
        parts = input_str.strip().split(" ")
        parts = set(i for i in parts if i != None and i in list(type_defaults))
        print(f"PARTS: {parts}, type: {type(parts)}")
        if len(parts) > 1:
            print(f"Parts len >1 : {parts}, type: {type(parts)}")
            new_str = set(parts)
        else:
            if isinstance(parts, set):
                new_str = parts
            else:
                new_str = set([parts])

    elif input_str in list(type_defaults):
        print(f"Input str in type_defaults: {input_str}, type: {type(input_str)}")
        new_str = set([input_str])

    else:
        print(f"No valid input [`{input_str}`]. Defaulting to item_type = ['static']")
        new_str = set(["static"])

    if not loc_cardinal:
        loc_cardinal = "graveyard north"

    if partial_dict and isinstance(partial_dict, dict):
        print("elif partial_dict.get('name'): Not sure this'll work any more now I've renamed it to 'nicename'.")
        if partial_dict.get(item_name):
            new_item_dict = partial_dict[item_name]
        elif partial_dict.get("name"):
            new_item_dict = partial_dict
        elif partial_dict.get("item_type") and partial_dict["item_type"] == ["static"]:
                print(f"Not sure why this is here `{partial_dict}` but ignoring.")
                new_item_dict = {}
        else:
            new_item_dict = partial_dict

        new_item_dict["item_type"] = new_str

    else:
        new_item_dict["item_type"] = new_str

    new_item_dict["exceptions"] = {"starting_location": loc_cardinal}

    inst = registry.init_single(item_name, new_item_dict)
    all_item_names_generated.append((inst, "new_item_from_str"))
    registry.temp_items.add(inst)

    #print(f"\nend of new_item_from_str for {inst}")
    printing.print_green(text=vars(inst), bg=False, invert=True)
    return inst

def apply_loc_data_to_item(item, item_data, loc_data):

    if loc_data and isinstance(loc_data, dict):
        for field in loc_data:
            if field == item:
                #print(f"loc_data: {loc_data} // field: {field}")
                for attr in loc_data[field]:
                    if attr == item:
                        continue
                    else:
                        item_data[attr] = loc_data[field][attr]
            else:
                item_data[field] = loc_data[field]

    else:
        if isinstance(loc_data, list): # will only ever be Everything.
            item_data["starting_location"] = "north everything"


    if item_data.get("description"):
        #print(f"item_data description: {item_data["description"]}")
        if "[[]]" in item_data["description"]:
            item_data["description"] = item_data["description"].replace("[[]]", item)


    if loc_data and isinstance(loc_data, dict) and loc_data.get("starting_location"):

        item_data["starting_location"] = loc_data["starting_location"]

    inst = registry.init_single(item, item_data)

    all_item_names_generated.append((inst, "apply_loc_data_to_item"))
    if hasattr(inst, "starting_children") and getattr(inst, "starting_children"):
        if not hasattr(registry, "check_for_children"):
            registry.check_for_children = []
        registry.check_for_children.append(inst)

    if hasattr(inst, "requires_key") and getattr(inst, "requires_key"):
        if not hasattr(registry, "requires_key"):
            registry.requires_key = []
        registry.requires_key.append(inst)

    return inst


def init_loc_items(place=None, cardinal=None):

    from item_dict_gen import generator, excluded_itemnames
    import json
    registry.alt_names = generator.alt_names
    import config
    with open(config.loc_data, 'r') as file:
        loc_dict = json.load(file)

    loc_items_dict = {}

    if config.parse_test:
        everything_entry = loc_dict["everything"]
        #print(f"Everything entry: {everything_entry}")
        everything_entry["north"]["items"] = list(registry.item_defs)
        #print(f"Everything entry: {everything_entry}")
        #print(f"Everything entry north items: {everything_entry["north"]["items"]}")

        north_everything = loc.by_cardinal_str("north everything")

    def get_cardinal_items(place, cardinal):
        name_to_inst_tmp = {}

        def from_single_cardinal(place, cardinal, name_to_inst_tmp):

            if isinstance(place, placeInstance):
                place = place.name
            if isinstance(cardinal, cardinalInstance):
                cardinal = cardinal.name

            if not loc_dict.get(place.lower()):
                return name_to_inst_tmp

            def create_base_items(place=None, cardinal=None, loc_data={}):
                matched = {}

                if place == None:
                    place = loc.currentPlace
                if  cardinal == None:
                    cardinal = loc.current
                card_inst = loc.by_cardinal_str(cardinal, place)

                if loc_data.get("item_desc"):
                    for item in loc_data["item_desc"]:
                        if item == None or item == "" or item in excluded_itemnames:
                            continue
                        item_data = generator.item_defs.get(item)
                        if item_data:
                            #print(f"ITEM DATA: {item_data}")
                            if not item_data.get("description"): ## only overwrite the item description if there isn't one written. Use location-descrip in location name, but item descrip in item descriptions. This works for now, might need to change it later. Not sure.
                                if item_data.get("descriptions"):
                                    for entry in item_data["descriptions"]:
                                        #print(f"Entry: {entry} / {item_data["descriptions"][entry]}")
                                        item_data["description"] = item_data["descriptions"][entry]
                                        break
                                else:
                                    #print(f"No item data description for {item}")
                                    item_data["description"] = loc_data["item_desc"].get(item)
                        item_data["starting_location"] = card_inst
                        apply_loc_data_to_item(item, item_data, loc_data["items"].get(item))

                if loc_data.get("items"):
                    #print(f"loc_data.get('items'): {loc_data["items"]}")
                    for item in loc_data["items"]:
                        if item == None or item == "" or item in excluded_itemnames:
                            continue
                        if loc_data.get("item_desc") and item in loc_data["item_desc"]:
                            if not matched.get(item):
                                #print(f"Already found a match for {item}, will process as new.")
                            #else:
                                matched[item] = 1
                                continue

                        item_data = generator.item_defs.get(item)
                        item_data["starting_location"] = card_inst
                        apply_loc_data_to_item(item, item_data, loc_data["items"])

            if loc_dict[place.lower()].get(cardinal):
                if loc_dict[place.lower()][cardinal].get("item_desc") or loc_dict[place.lower()][cardinal].get("items"):
                    create_base_items(place.lower(), cardinal, loc_dict[place.lower()][cardinal])

            return name_to_inst_tmp

        if cardinal == None:
            for cardinal in CARDINALS:
                name_to_inst_tmp = from_single_cardinal(place, cardinal, name_to_inst_tmp)
        else:
            name_to_inst_tmp = from_single_cardinal(place, cardinal, name_to_inst_tmp)

    if config.parse_test:
        get_cardinal_items(north_everything.place, north_everything)

        for item in registry.instances:
            if hasattr(item, "location") and item.location != None and item.location != north_everything:
                registry.move_item(item, north_everything)

    if not config.parse_test:
        if place == None:
            for place in loc_dict:
                loc_items_dict[place] = {}
                get_cardinal_items(place, cardinal)
        else:
            loc_items_dict[place] = {}
            get_cardinal_items(place, cardinal)

    registry.clean_relationships()

    #I'm not convinced the next lines are necessary, as generate_children_for_parent runs immediately. Surely it's one or the other, not both.
    #if registry.new_parents and registry.new_parents != None:
    #    registry.generate_children_for_parent()


def initialise_itemRegistry():

    registry.complete_location_dict()

    from item_dict_gen import init_item_dict
    registry.item_defs = init_item_dict()


    init_loc_items()

    plural_word_dict = {}

    for item_name in registry.item_defs.keys():
        if len(item_name.split()) > 1:
            plural_word_dict[item_name] = tuple(item_name.split())
        if registry.item_defs[item_name].get("alt_names"):
            for alt_name in registry.item_defs[item_name]["alt_names"]: # Had never added alt_names to plural_words. Oops.
                if len(alt_name.split()) > 1:
                    plural_word_dict[alt_name] = tuple(alt_name.split())

    for obj in registry.instances:
        if hasattr(obj, "is_loc_exterior"):
            location = loc.place_by_name(obj.name)
            if hasattr(location, "entry_item"):
                if not hasattr(obj, "transition_objs") or not isinstance(obj.transition_objs, set):
                    obj.transition_objs = set()
                obj.transition_objs.add(location.entry_item)

    registry.add_plural_words(plural_word_dict)

    return registry.event_items

if __name__ == "__main__":

    from env_data import initialise_placeRegistry
    initialise_placeRegistry()

    initialise_itemRegistry()
