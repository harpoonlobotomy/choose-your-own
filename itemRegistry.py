
import uuid

from env_data import cardinalInstance, placeInstance
from logger import logging_fn, traceback_fn
from env_data import locRegistry as loc
import printing

global all_item_names_generated, all_items_generated
all_item_names_generated = list()
all_items_generated = set()

CARDINALS = ["north", "east", "south", "west"]

print("Item registry is being run right now.")

type_defaults = {
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

class ItemInstance:
    """
    Represents a single item in the game world or player inventory.
    """
    def set_hidden(self): # so the noun won't be considered for picking up etc outside of whatever un-hiddening act I come up with.

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

        #for item_type in self.item_type:
        #    print(f"{self}  ITEM TYPE: {item_type}")
        #    for flag in type_defaults.get(item_type):
        #        if not hasattr(self, flag):
        #            setattr(self, flag, type_defaults[item_type][flag])

        return self.item_type


    def __init__(self, definition_key:str, attr:dict):
        #print(f"\n\n@@@@@@@@@@@@@@@@@ITEM {definition_key} in INIT ITEMINSTANCE@@@@@@@@@@@@@@@\n\n")
        #print(f"definition_key: {definition_key}, attr: {attr}")
        #print(f"Init in item instance is running now. {definition_key}")
        self.id = str(uuid.uuid4())  # unique per instance
        for attribute in attr:
            #print(f"ATTRIBUTE: {attribute}, value: {attr[attribute]}")
            setattr(self, attribute, attr[attribute])
        self.name:str = definition_key
        self.nicename:str = attr.get("name")
        #print(f"ATTR: {attr}")
        self.item_type = self.clean_item_types(attr["item_type"])#attr["item_type"] ## have it here and/or in the registry. I guess both? covers the 'is_container' thing neatly enough.

        self.colour = None
        self.description:str = attr.get("description")
        self.starting_location:dict = attr.get("starting_location") # currently is styr
        self.verb_actions = set()
        self.location:cardinalInstance = None
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

            from item_definitions import detail_data
            details = self.name + "_details"
            details = details.replace(" ", "_")
            details_data = detail_data.get(details)

            self.description_detailed = details_data

###
        if "container" in self.item_type:
            self.verb_actions.add("is_container")
            if hasattr(self, "starting_children"):
                registry.new_parents.add(self.id)

        if hasattr(self, "is_hidden") and self.is_hidden:
            self.set_hidden()
            #self.children = list() ## Maybe we create all instances first, then add 'children' afterwards, otherwise they won't be initialised yet. Currently this works because I've listed the parents first in the item defs.

        if hasattr(self, "enter_location"):
            self.enter_location = loc.by_name.get(self.enter_location)

    def __repr__(self):
        return f"<ItemInstance {self.name} ({self.id})>"


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

        self.contained_in_temp = set() # not sure what this one was even for...

        self.event_items = {}
        self.keys = set()

        self.locks_keys = {}

        import json
        json_primary = "dynamic_data/items_main.json" # may break things
        with open(json_primary, 'r') as file:
            item_defs = json.load(file)

        self.item_defs = item_defs

    # -------------------------
    # Creation / deletion
    # -------------------------

    def init_single(self, item_name, item_entry): ## Will replace create_instance directly.
        #print(f"[init_single] ITEM NAME: {item_name}")
        #print(f"[init_single] ITEM ENTRY: {item_entry}")
        inst = ItemInstance(item_name, item_entry)
        all_items_generated.add(inst)
        self.instances.add(inst)

        self.item_defs[item_name] = item_entry

        if not self.by_name.get(inst.name):
            self.by_name[inst.name] = []
        self.by_name[inst.name].append(inst)
        #self.by_name[inst.name] = inst
        self.by_id[inst.id] = inst

        loot_type = item_entry.get("loot_type")

        if loot_type: # Works with multiple categories now. So, starting loot also has a value. Currently it's always added, it doesn't remove something from the pool just because it was in the starting loot. May need to reevaluate, but functions okay for now.

            if isinstance(loot_type, list):
                for option in loot_type:
                    self.by_category.setdefault(option, set()).add(inst)
            else:
                self.by_category.setdefault(loot_type, set()).add(inst)

        location = item_entry.get("starting_location")
        if not location and not hasattr(inst, "contained_in") and item_entry.get("exceptions"):
            location = item_entry.get("exceptions").get("starting_location")

        if location:
            #print(f"Location for instance {self}, {item_name}, {location}")
            if isinstance(location, cardinalInstance):
                inst.location = location
                self.by_location.setdefault(location, set()).add(inst)

            elif not hasattr(inst, "contained_in") or inst.contained_in == None:
                #print(f"Item {inst.name} has a location: {location}.")
                from env_data import locRegistry as loc
                cardinal_inst = loc.by_cardinal_str(location)
                #print(f"CARDINAL INST IF LOCATION: {cardinal_inst}, {cardinal_inst.name}")
                self.by_location.setdefault(cardinal_inst, set()).add(inst)
                #print(f"SELF.BY_LOCATION: {self.by_location}")
                inst.location = cardinal_inst


        if item_entry.get("alt_names"):
            for altname in item_entry.get("alt_names"):
                self.by_alt_names[altname] = item_name

        if hasattr(inst, "starting_children") and inst.starting_children != None:
            #print("HAS ATTR STARTING_CHILDREN")
            self.new_parents.add(inst.id)
            registry.generate_children_for_parent(parent=inst) ## moved this to within init_single
            #print(f"Generated children for {item_name}")

        if hasattr(inst, "contained_in") and inst.contained_in != None:
            #print(f"{inst.name}:: inst.contained_in: {inst.contained_in}")
            self.contained_in_temp.add(inst)

        if hasattr(inst, "event"):
            for key in ("event_key", "event_item"):
                if not hasattr(inst, key):
                    setattr(inst, key, None)
            self.event_items[inst.name] = {"event_name": inst.event, "event_key": inst.event_key, "event_item": inst.event_item, "item": inst}

        #for item_type in inst.item_type:
        #    #print(f"{inst}  ITEM TYPE: {item_type}")
        #    for flag in type_defaults.get(item_type):
        #        if not hasattr(inst, flag):
        #            setattr(inst, flag, type_defaults[item_type][flag])

        #if "key" in inst.item_type:
        #    setattr(inst, "key", True)

        if hasattr(inst, "is_key"):
            self.keys.add(inst)

        return inst

    def get_item_from_defs(self, item_name):

        if item_name in list(self.item_defs):
            inst = self.init_single(item_name, self.item_defs[item_name])
            all_item_names_generated.append((inst, "get_item_from_defs"))
            return inst


    def delete_instance(self, inst: ItemInstance):
        inst_id=inst.id
        inst = self.instances.pop(inst_id, None)
        if not inst:
            return

        # remove from location index
        if inst.location and inst.location in self.by_location:
            self.by_location[inst.location].discard(inst)
           # if not self.by_location_inst[inst.location]:
           #     del self.by_location_inst[inst.location]

        # remove from name index
        self.by_name.get(inst.name, list()).remove(inst)

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
#            if container is not None and item.container is not container:
#                continue
#            if open is not None and item.is_open != open:
#                continue
#            if locked is not None and item.is_locked != locked:
#                continue
        if attr_str:
            items = (i for i in self.instances if hasattr(i, attr_str))

        if loot_type:
            print(f"Loot type: {loot_type}")
            print(f"i for i in self.instances if hasattr(i, 'loot_type'): {(i for i in self.instances if hasattr(i, 'loot_type'))}")
            items = (i for i in self.instances if hasattr(i, "loot_type") and loot_type in i.loot_type)

        #yield items
        return items

        #for i in items_in(container=True, open=True):
        #    ...

    #def get_parents(eslf):


        #if hasattr(child, "contained_in"): ## determined before it's sent here, don't check again
        """
        get parent name from contained_in
    ## this is likely coming from loc_data ##
    # As such, do we get the loc_data entry?
    No, bring it into the function directly, we'll have attr. Just need to make sure item_state is included in attr at init. should be already.
        Oh but attr only has this item's data. I need all of it. Shite...

        Maybe we only run this after get_children is done, so then if there' no parentage established we can add it. Based on location; if  {"padlock": {"contained_in": "gate"} and there's only one gate and it's a container, that inst is the parent inst. But still, need the location.

        I could attached 'item_state' whole to the cardinal? Eh doesn't solve it. I'm just thinking ahead if we have multiple of the same item/container but maybe I just need to avoid that and rejig later if I need to.
        """

    def generate_children_for_parent(self, parent=None):
            #
        def get_children(parent:ItemInstance):
            #print(f"parent: {parent}, item.starting_children: {parent.starting_children}")
            instance_children = []
            instance_count = 0
            target_child = None
            if isinstance(parent.starting_children, list|set|tuple):
                for child in parent.starting_children:
                    if isinstance(child, ItemInstance):
                        instance_count += 1
                        continue
                    if registry.child_parent.get(child):
                        if registry.child_parent[child] == parent.name:
                            #print("Child/parent pair already exists, skipping.")
                            continue
                    #print(f"create child by init_single: {child}")
                    if child in self.item_defs:
                        target_child = self.init_single(child, self.item_defs[child])
                        all_item_names_generated.append((target_child, "generate_child from item_defs"))
                    else:
                        target_child = use_generated_items(child)
                        if not target_child:
                            print(f"No target child, calling new_item_from_str for child {child} and parent {parent}")
                            target_child = new_item_from_str(item_name=child, in_container=parent)
                            all_item_names_generated.append((child, "generate_child item_from_str"))
                            # untested. Previously it just failed if not in item_defs.

                    #target_child = self.create_item_by_name(child)
                    #print(f"target child after create_item_by_name from list: {target_child}")
                    if target_child:
                        instance_children.append(target_child)
                        target_child.contained_in = parent
                        #print(f"target_child.contained_in = parent: {target_child.contained_in}")
                        if not hasattr(parent, "children"):
                            parent.children = set()
                        parent.children.add(target_child)
                        #print(f"parent.children: {parent.children}")
                        #exit()
                if len(instance_children) == len(parent.starting_children):
                    #print(f"All children found/created as instances: {instance_children}")
                    parent.starting_children = instance_children
                    #print(f"Removing {parent.name} from new_parents because instance children == len starting children.")
                    #print(f"REGISTRY.new_parents before remove attempt: {registry.new_parents}")
                    registry.new_parents.remove(parent.id)
                    #print(f"REGISTRY.new_parents after remove attempt: {registry.new_parents}\n")
        ## NOTE: new_parents  WORKS HERE. Wss present, now removed.
                else:
                    if (len(instance_children) + len(registry.child_parent) == len(parent.starting_children)) or (len(parent.starting_children) == instance_count):
                        #print("All children found or already parented to this parent.")
                        #print(f"REGISTRY.new_parents before remove attempt: {registry.new_parents}")
                        registry.new_parents.remove(parent.id)
                    else:
                        print(f"Not all children found/made as instances. Str list:\n   {parent.starting_children}\nInstance list:\n    {instance_children}\nchild/parent dict: {registry.child_parent}")
                        exit() # again, right now hard exit if this ever fails. Need to see why if it does.
        # Was going to do keys here too, but I don't think I will. Maybe do those at runtime, they're not as widely relevant as children so maybe just do that identification when looked for? Though having said that, that means I have to be aware of whenever they might be checked for... Yeah I should do it here actually.
            elif isinstance(parent.starting_children, str):
                if parent.starting_children in self.item_defs:
                    target_child = self.init_single(parent.starting_children, self.item_defs[parent.starting_children])
                    all_item_names_generated.append((parent.starting_children, "generate_child from item_defs"))
                else:
                    target_child = use_generated_items(parent.starting_children)
                    if not target_child:
                        print(f"No target child, calling new_item_from_str for child {child.starting_children} and parent {parent}")
                        target_child = new_item_from_str(item_name=parent.starting_children, in_container=parent)
                        all_item_names_generated.append((parent.starting_children, "generate_child from str"))
                    else:
                        print(f"Generated target child from generated_items but didn't actually make an instance, I think: {target_child}")
                #target_child = self.create_item_by_name(parent.starting_children)
                #print(f"target object after create_item_by_name with str: {target_child}")
                if target_child:
                    parent.starting_children.append(target_child)
                    target_child.contained_in = parent
                    if not hasattr(parent, "children"):
                        parent.children = set()
                    parent.children.add(target_child)
                    #print(f"Removing parent {parent.name} from new_parents because starting children was string and was inited.")
                    #print(f"REGISTRY.new_parents before remove attempt: {registry.new_parents}")
                    registry.new_parents.remove(parent.id)

                else:
                    print(f"Failed to find child for {parent}'s {parent.starting_children} (from str).")
                    exit()
            return registry.child_parent

        if parent:
            get_children(parent)

        else:
            if registry.new_parents and registry.new_parents != None:
                for parent in registry.new_parents:
                    if isinstance(parent, str):
                        parent = registry.by_id.get(parent)
                    get_children(parent)


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
                                #print(f"Assigning {maybe_key} to {item}.")
                                self.locks_keys[item] = maybe_key
                                self.locks_keys[maybe_key] = item
                                item.requires_key = maybe_key
                                setattr(maybe_key, "unlocks", item) ## NOTE: This isn't implemented anywhere, try to remember. inst.unlocks == inst of the lock it opens.
                                #print(f"Lock: {maybe_key.unlocks}")
                                #print(f"Key: {item.requires_key}")
                                key_found = True

                    if not key_found:
                        if self.item_defs.get(getattr(item, "requires_key")):
                            target_obj = self.init_single(getattr(item, "requires_key"), self.item_defs.get(getattr(item, "requires_key")))
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
        #    8: "in container but only technically (eg padlock in door)" (can look/interact with, but not move/pick/up/drop)
        #    9: "item is hidden" (must be discovered somehow, not shown in general 'look around' views.)
        #}

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

            from set_up_game import game
            inventory_list = game.inventory

            local_items_list = self.get_item_by_location(loc.current)
            container, inst = is_item_in_container(inst, inventory_list)

            if inst in inventory_list and not container: # if in inv, can't be hidden. # Though that doesn't matter, if discovered it should lose the is_hidden:True anyway. so check that first.
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
                    print("No items at this location.")

            if container:
                if container in inventory_list:
                    confirmed_container = container
                    if confirmed_container:
                        if (hasattr(confirmed_container, "ownership_container")):
                            reason = 8
                        if (hasattr(confirmed_container, "is_closed") and getattr(confirmed_container, "is_closed")):
                            reason = 1
                        elif (hasattr(confirmed_container, "is_locked") and getattr(confirmed_container, "is_locked")):
                            reason = 2
                        else:
                            reason = 3
                else:
                    confirmed_container = in_local_items_list(container, local_items_list)
                    if confirmed_container:
                        if (hasattr(confirmed_container, "ownership_container")):
                            reason = 8
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
                print(f"Confirmed_inst in local items: {confirmed_inst}")
                if confirmed_inst:
                    reason = 0
                else:
                    if inst in inventory_list:
                        confirmed_inst = inst
                        reason = 5
                    else:
                        reason = 6

            meaning = accessible_dict[reason]

            if confirmed_inst:
                return confirmed_inst, confirmed_container, reason, meaning

            return None, confirmed_container, reason, meaning # Not sure if container should be None or Container here. Container for hints, 'None' for clearer parsing out of the function.

        if not isinstance(inst, ItemInstance):
            if isinstance(inst, str) and inst != None:
                named_instances = self.instances_by_name(inst)
                if named_instances:
                    for item in named_instances:
                        confirmed_inst, confirmed_container, reason_val, meaning = run_check(item)

        else:
            confirmed_inst, confirmed_container, reason_val, meaning = run_check(inst)

        if confirmed_inst != None:
            return confirmed_inst, confirmed_container, reason_val, meaning

        return inst, confirmed_container, reason_val, meaning


    # -------------------------
    # Movement
    # -------------------------

    def move_item(self, inst:ItemInstance, location:cardinalInstance=None, new_container:ItemInstance=None, old_container:ItemInstance=None)->list:
        logging_fn()

        ## REMOVE FROM ORIGINAL LOCATION ##
        old_loc = inst.location
        if old_loc and old_loc != None:
            if self.by_location.get(old_loc):
                self.by_location[old_loc].discard(inst)
                inst.location = None

        ## MOVE TO NEW LOCATION IF PROVIDED
        if location != None:
            if not isinstance(location, cardinalInstance):
                print(f"move_item requires location to be cardinalInstance. Recieved `{location}` of type `{type(location)}`.")
                traceback_fn()
                exit()
            inst.location = location
            if not self.by_location.get(location):
                self.by_location[location] = set()
            self.by_location[location].add(inst)

        if old_container or new_container or hasattr(inst, "contained_in"):
            return_text = []
            if hasattr(inst, "contained_in"):
                if old_container != None:
                    parent = old_container
                else:
                    parent = inst.contained_in
                if parent:
                    parent.children.remove(inst)
                    inst.contained_in = None
                    return_text.append((f"Item `[child]` removed from old container `[parent]`", inst, parent))

        ## Should this be one tab over? Probably. Otherwise it'll fail if the obj was not previously contained, no?
            if new_container:
                inst.contained_in = new_container
                print(f"inst.contained_in (move_item): {inst.contained_in}")
                self.by_container[new_container].add(inst)
                return_text.append((f"Added [child] to new container [new_container]", inst, new_container))
            if return_text:
                return return_text

    def move_from_container_to_inv(self, inst:ItemInstance, inventory:list, parent:ItemInstance=None) -> tuple[list,list]:
        logging_fn()
        if parent == None:
            parent = inst.contained_in
        result = self.move_item(inst, old_container=parent)
        inventory.append(inst)
        return inventory, result


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
            #print(f"items_at_cardinal: {items_at_cardinal}, type: {type(items_at_cardinal)}")
            if items_at_cardinal:
                return items_at_cardinal


    def instances_by_name(self, definition_key:str)->list:
        logging_fn()

        if not isinstance(definition_key, str):
            if isinstance(definition_key, list):
                definition_key = definition_key[0]
        if self.by_name.get(definition_key):
            #print(f"self.by_name.get(definition_key): {self.by_name.get(definition_key)}")
            return self.by_name.get(definition_key)

        elif self.by_alt_names.get(definition_key):
            #print(f"self.by_alt_names.get(definition_key): {self.by_alt_names.get(definition_key)}")
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
            1: "minor_loot",   ## Keeping this here temporarily until I update it properly.
            2: "medium_loot",
            3: "great_loot",
            4: "special_loot"
        }

        """Pick a random item name from a category (int or str)."""
        if isinstance(selection, int):
            category = loot_table[selection]
        else:
            category = selection
        items = list(self.by_category.get(category, set())) # should this still be a list?

        return random.choice(items)# if items else "No Items (RANDOM_FROM)"

    def describe(self, inst: ItemInstance, caps=False, colour_instances=False)->str:
        logging_fn()

        description = inst.description

        if "container" in inst.item_type:
            #print(f"Container in inst.flags: {inst}")
            all_children = True
            if hasattr(inst, "children") and getattr(inst, "starting_children"):
                for child in inst.starting_children:
                    if child in inst.children:
                        print(f"Child {child.name} is present in parent {inst.name}.")
                    else:
                        all_children = False
            #children = self.instances_by_container(inst)
            if not all_children:
            #if not children:
                if hasattr(inst, "description_no_children") and inst.description_no_children != None:
                    description = inst.description_no_children # works now. If it's a container with no children, it prints this instead.
                # still need to make it non-binary but that can happen later. This'll do for now.

        if hasattr(inst, "is_open") and inst.is_open == True:
            if hasattr(inst, "if_open_description"):
                description = inst.if_open_description
        """Convenience method to return a formatted description."""
        if caps:
            from misc_utilities import smart_capitalise
            description = smart_capitalise(description)

        if description:
            return description



        return "You see nothing special."

    def nicename(self, inst: ItemInstance):
        logging_fn()
        if "container" in inst.flags:
            children = self.instances_by_container(inst)
            if not children:
                #print(f"no children present. name: {inst.name_children_removed}")
                return inst.name_children_removed

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
        #logging_fn()

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

        return inst.name

    def pick_up(self, inst:str|ItemInstance, inventory_list=None, location=None, starting_objects=False) -> tuple[ItemInstance, list]: ## location == cardinalInstance
        logging_fn()

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
            loc_card = location.place_name
            print(f"No inst, so calling new_item_from_str for item {item}")
            inst = new_item_from_str(item_name=item, loc_cardinal=(loc_card)) # TODO: replace these with place instances, this is just temp
            print("Failed to find inst in pick_up, generating from str..")

        if not starting_objects and not hasattr(inst, "can_pick_up"):
            print(f"[[Cannot pick up {inst.name} (according to inst.flags)]]")
            print(f"inst.flags: {inst.flags}")
            return None, inventory_list

        #if not starting_objects:
        #    local_items = self.get_item_by_location(location)
        #    if local_items:
        #        if inst not in local_items:
        #            print(f"[[Cannot pick up {inst.name} (not at current location)]]")
        #            return None, inventory_list
        #    else:
        #        print(f"[[Cannot pick up {inst.name} (not at current location) (no items at {loc.current.place_name})]]")
        #        return None, inventory_list


        if inst in inventory_list: ## TODO: Add a check so this only applies to items that can be duplicated. Though really those that can't should not still remain in the world when picked up... so the problem lies in the original pick up in that case, not the dupe.
            #print("Item already in inventory. Creating new...") ## Not sure about this.
            attr = self.item_defs.get(inst.name)
            inst = self.init_single(inst.name, attr)

        self.move_item(inst)
        inventory_list.append(inst)

        if not hasattr(self, "starting_location"): # so it only updates once, instead of being the 'last picked up at'. Though that could be useful tbh. Hm.
            self.starting_location = {location} # just temporarily, not in use yet. Needs formalising how it's going to work.

        return inst, inventory_list

    def drop(self, inst: ItemInstance, inventory_list):
        logging_fn()
        #print("inventory_list")
        if inst not in inventory_list:
            return None, inventory_list

        inventory_list.remove(inst)
        #print("inventory_list")
        self.move_item(inst, loc.current)
        return inst, inventory_list


    def complete_location_dict(self):

        logging_fn()
        from env_data import locRegistry as loc
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

# setup
registry = itemRegistry()

if __name__ == "__main__":

    from env_data import initialise_placeRegistry

    initialise_placeRegistry()

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
        #print(f"partial_dict before: {partial_dict}")
        if partial_dict.get(item_name):
            partial_dict = partial_dict[item_name]
        #print(f"partial_dict after: {partial_dict}")

    new_item_dict = {}

    if item_name == "":
        print('Item name is `""` .')
        print(f"item_name: {item_name}, input_str: {input_str}, loc_cardinal: {loc_cardinal}, partial_dict: {partial_dict}")

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
        if partial_dict.get(item_name):
            new_item_dict = partial_dict[item_name]
        elif partial_dict.get("name"):
            new_item_dict = partial_dict
        elif partial_dict.get("item_type") and partial_dict["item_type"] == ["static"]:
                print(f"Not sure why this is here `{partial_dict}` but ignoring.")
                new_item_dict = {}
        else:
            new_item_dict = partial_dict
            #print(f"Partial dict: Not sure how to use this format: {partial_dict}")
                #exit()

        new_item_dict["item_type"] = new_str

    else:
        new_item_dict["item_type"] = new_str

    new_item_dict["exceptions"] = {"starting_location": loc_cardinal}

    #print(f"new_item_from_str: \n {new_item_dict}, {item_name}\n\n")
    inst = registry.init_single(item_name, new_item_dict)
    all_item_names_generated.append((inst, "new_item_from_str"))
    #print(f"Inst after self.init_items(): {inst}, type: {type(inst)}")
    registry.instances.add(inst)
    registry.temp_items.add(inst)

    print(f"\nend of new_item_from_str for {inst}")
    printing.print_green(text=vars(inst), bg=False, invert=True)
    return inst

def apply_loc_data_to_item(item, item_data, loc_data):

    #print(f"\n\nApplying loc data to item: {item}, item data: ``{item_data}``, loc data: ``{loc_data}``")
    if loc_data:
        for field in loc_data:
            if field == item:
                #print(f"FIELD: {field}")
                for attr in loc_data[field]:
                    if attr == item:
                        continue
                    else:
                        item_data[field] = loc_data[field][attr]
            else:
                item_data[field] = loc_data[field] # just always apply loc_data, right? It should overrule always. I think. Shit.
    if item_data.get("description"):
        if "[[]]" in item_data["description"]:
            item_data["description"] = item_data["description"].replace("[[]]", item)

    if loc_data and loc_data.get("starting_location"):
        #print(f"STarting location for {item}: {loc_data["starting_location"]}, ty[e: {type(loc_data["starting_location"])}]")
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


def get_loc_items(loc=None, cardinal=None):

    from item_dict_gen import generator, excluded_itemnames
    import json

    loc_data_json = "loc_data.json"
    with open(loc_data_json, 'r') as file:
        loc_dict = json.load(file)

    loc_items_dict = {}
    from env_data import locRegistry

    def get_cardinal_items(loc, cardinal):

        name_to_inst_tmp = {}

        def from_single_cardinal(loc, cardinal, name_to_inst_tmp):
            #print(f"name_to_inst_tmp: {name_to_inst_tmp}")

            if not loc_dict.get(loc.lower()):
                print(f"Location {loc} not in env_data.")
                return name_to_inst_tmp

            def create_base_items(loc=None, cardinal=None, loc_data={}):

                matched = {}

                if loc == None:
                    loc = locRegistry.currentPlace
                if  cardinal == None:
                    cardinal = locRegistry.current
                card_inst = locRegistry.by_cardinal_str(cardinal, loc)

                 # may need to remove later if in a container, but do this for now by default.

                if loc_data.get("item_desc"):
                    for item in loc_data["item_desc"]:
                        if item == None or item == "" or item in excluded_itemnames:
                            continue
                        item_data = generator.item_defs.get(item)
                        if not item_data:
                            print(f"Item {item} not in generator? : {item_data}")
                            print("generator.item_defs: ", generator.item_defs, "\n\n")
                        item_data["description"] = loc_data["item_desc"].get(item)
                        item_data["starting_location"] = card_inst
                        inst = apply_loc_data_to_item(item, item_data, loc_data["items"].get(item)) # maybe this should be inside an init func. Or maybe not.
                        #print(f"GENERATED INST: {inst}")



                if loc_data.get("items"):
                    for item in loc_data["items"]:
                        if item == None or item == "" or item in excluded_itemnames:
                            continue
                        if loc_data.get("item_desc") and item in loc_data["item_desc"]:
                            if matched.get(item):
                                print(f"Already found a match for {item}, will process as new.")
                            else:
                                matched[item] = 1
                                continue

                        item_data = generator.item_defs.get(item)
                        item_data["starting_location"] = card_inst
                        inst = apply_loc_data_to_item(item, item_data, loc_data["items"])
                        ### NOTE: Above inits the instance.
                        #print(f"GENERATED INST: {inst}")


            if loc_dict[loc.lower()].get(cardinal):
                if loc_dict[loc.lower()][cardinal].get("item_desc") or loc_dict[loc.lower()][cardinal].get("items"):

                    create_base_items(loc.lower(), cardinal, loc_dict[loc.lower()][cardinal])

            return name_to_inst_tmp

        if cardinal == None:
            for cardinal in CARDINALS:
                loc_items_dict[loc][cardinal] = {}
                name_to_inst_tmp = from_single_cardinal(loc, cardinal, name_to_inst_tmp)
        else:
            loc_items_dict[loc][cardinal] = {}
            name_to_inst_tmp = from_single_cardinal(loc, cardinal, name_to_inst_tmp)

    if loc == None:
        for loc in loc_dict:
            loc_items_dict[loc] = {}
            get_cardinal_items(loc, cardinal)
    else:
        loc_items_dict[loc] = {}
        get_cardinal_items(loc, cardinal)

    registry.clean_relationships()

    if registry.new_parents and registry.new_parents != None: # in case something slipped by, this should never be needed though.
        registry.generate_children_for_parent()

def initialise_itemRegistry():

    registry.complete_location_dict()
    from env_data import initialise_placeRegistry
    initialise_placeRegistry()
    #     ***************************************
    from item_dict_gen import init_item_dict
    init_item_dict()
### NOTE: Need to cull a heap from itemReg, because it no longer needs to access the item def JSONs and build the item defs itself. What it does need to do is go through loc_data and create the required instances, using the item defs built by item_dict_gen. That's all it needs to focus on. Getting those relationships right and /only generating the instances it needs to/.

    get_loc_items()

    plural_word_dict = {}

    for item_name in registry.item_defs.keys():
        if len(item_name.split()) > 1:
            printing.print_blue(f"split name: {item_name}")
            plural_word_dict[item_name] = tuple(item_name.split())
    registry.add_plural_words(plural_word_dict)

    return registry.event_items

