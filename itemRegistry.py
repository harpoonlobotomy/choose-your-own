
from env_data import cardinalInstance, placeInstance, locRegistry as loc
from logger import logging_fn, traceback_fn
import printing
import config

global all_item_names_generated, all_items_generated
all_item_names_generated = list()
all_items_generated = set()

CARDINALS = config.cardinals_list

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
#"descriptions": {"if_locked": ""}
print("Item registry is being run right now.")

type_defaults = {
    "standard":
        {f"descriptions": {"generic": None}, "nicenames": {"generic": ""}, "can_break": True, "slice_defence": 5, "smash_defence": 5, "slice_attack": 5, "smash_attack": 5,},
    "static":
        {"can_break": False},
    "can_open":
        {"is_open": False, "can_be_opened": True, "can_be_closed": True},
        "descriptions":
            {"is_open": ""},
        "nicenames": {
            "is_open": None},
    "can_lock":
        {"can_be_locked": True, "is_locked": True, "requires_key": False, "descriptions": {"is_locked": ""}},
    "container":
        {"is_open": False, "can_be_opened": True, "can_be_closed": True, "can_be_locked": True, "is_locked": False, "requires_key": False, 'starting_children': None, 'container_limits': 4, "children_type_limited": False, "can_be_added_to": True, "children": None,
         "nicenames": {
            "starting_children_only": "",
            "any_children": "",
            "no_children": ""},
        "descriptions": {
            "starting_children_only": "",
            "any_children": "",
            "no_children": "",
            "open_starting_children_only": "",
            "open_any_children": "",
            "open_no_children": ""}},
    "key":
        {"is_key_to": None},
    "can_pick_up":
        {"can_pick_up": True, "item_size": 1},
    "event":
        {"event": None, "is_event_key": False},
    "trigger":
        {"trigger_type": "plot_advance", "trigger_target": None, "is_exhausted": False},
    "flooring":
        {"is_horizontal_surface": True, "slice_defence": 10, "smash_defence": 10},
    "wall":
        {"is_vertical_surface": True, "slice_defence": 10, "smash_defence": 10},
    "food_drink":
        {"can_consume": True, "can_spoil": True, "is_spoiled": False, "is_safe": True, "effect": None},
    "fragile":
        {"is_broken": False, "slice_defence": 1, "smash_defence": 1, "description": {"is_broken": None}},
    "flammable":
        {"can_burn": True, "is_burned": False, "description": {"is_burned": None}},
    "books_paper":
        {'print_on_investigate': True, 'flammable': True, 'is_burned': False, 'can_read': True, 'material_type': 'paper', "smash_defence": 9, "slice_defence": 3},
    "electronics":
        {"requires_powered_location": False, "can_be_charged": True, "is_charging":False, "is_charged": False, "takes_batteries": True, "has_batteries": False, "is_on": False},
    "battery": {"can_be_charged": True, "is_charged": True, "in_use": False},
    "living": {"can_die": True, "age": "average"},
    "can_speak" :
        {'can_speak': True, 'speaks_common': True, "knows_about": None, "speech_traits": [], "languages_spoken": ["common"], "test_styling": []},
    "transition":
        {"is_transition_obj": True, "int_location": None, "ext_location": None},
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
    "digital": {"is_not_physical": True},
    "charger": {"requires_powersource": True, "in_use": False}
}

    #{"special_traits: set("dirty", "wet", "panacea", "dupe", "weird", "can_combine")}, # aka random attr storage I'm not using yet
    #"exterior": {"is_interior": False} ## Can be set scene-wide, so 'all parts of 'graveyard east' are exterior unless otherwise mentioned'. (I say 'can', I mean 'will be when I set it up')

material_type = {
    "generic": {"on_break": f"broken [[item_name]]"},
    "glass": {"on_break": "broken glass shard"},
    "paper": {"on_break": "torn [[item_name]]", "on_burn": "ash pile"},
    "fabric": {"on_break": "torn [[item_name]]"},
    "ceramic": {"on_break": "broken ceramic shard"},
    "already_broken": {None: None}
}

material_msgs = {
    "generic": "it crumples into a broken echo of its former self.",
    "glass": "it shatters into a clutter of glass shards",
    "paper": "it is torn, left a shadow of its former self.",
    "fabric": "it is torn, left a shadow of its former self.",
    "ceramic": "it shatters into a clutter of ceramic shards",
    "already_broken": "it can't be broken any further.",
    "already_burned": "it can't be burned any further."
    }


plant_type = ["tuber", "legume", "arctic carrot"]

# failure = <10, success = 10-19, crit = 20.


class itemInstance:
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


    def clean_item_types(self, attr) -> set[str]:

        self.item_type = attr

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

    def set_itemtype_attrs(self:"itemInstance", attr:dict): # just here for linting except for container.

        self.is_hidden:bool = attr["is_hidden"] if attr.get("is_hidden") else False
        self.can_break:bool = attr["can_break"] if attr.get("can_break") else False
        if self.can_break or attr.get("is_broken"):
            self.is_broken = attr.get("is_broken", False)

        self.slice_attack = attr.get("slice_attack", 5) ## 11 is entirely unbreakable
        self.slice_defence = (attr.get("slice_defence", 5) if not self.can_break else 11)
        self.smash_attack = attr.get("smash_attack", 5)
        self.smash_defence = (attr.get("smash_defence", 5) if not self.can_break else 11)

        self.details:dict[str, str]|None = attr.get("details")
        self.has_datapoint:dict[str, dict[str:str]]|None = attr.get("has_datapoint", False)
        self.not_in_loc_desc:bool = attr.get("not_in_loc_desc", False)

        if "flammable" in self.item_type:
            self.can_burn = attr.get("can_burn", True,)
            self.is_burned = attr.get("is_burned", False)

        if "container" in self.item_type:
            self.children:set[itemInstance] = set()
            #self.starting_children:set[itemInstance] = set()
            self.starting_children:set[itemInstance] = (set(attr.get("starting_children")) if attr.get("starting_children") else None)
            if self.starting_children:
                registry.new_parents.add(self.id)
            self.can_be_added_to = attr.get("can_be_added_to", True)
            self.children_type_limited = attr.get("children_type_limited", False)
            self.container_limits = attr.get("container_limits", 5)
            self.print_children_as_list = attr.get("print_children_as_list", False)
            self.verb_actions.add("is_container")
            registry.by_container[self] = set()

        if "can_pick_up" in self.item_type:
            self.contained_in:itemInstance = attr.get("contained_in", None)
            self.can_pick_up = attr.get("can_pick_up", False)
            self.item_size = attr.get("item_size", 1)

        if "books_paper" in self.item_type:
            self.print_on_investigate = attr.get("print_on_investigate", True)
            self.flammable = attr.get("flammable", True)
            self.is_burned = attr.get("is_burned", False)
            self.can_read = attr.get("can_read", False)

        if attr.get("loot_type"):
             self.loot_type = attr["loot_type"]

        if "key" in self.item_type:
            self.is_key_to:set[itemInstance] = set((attr.get("is_key_to"),)) if attr.get("is_key_to") else None
            self.unlocks:set[itemInstance] = set((attr.get("unlocks"),)) if attr.get("unlocks") else None

        if "can_lock" in self.item_type or "container" in self.item_type:
            self.can_be_locked = attr["can_be_locked"]
            self.is_locked = attr["is_locked"]
            self.requires_key:set[itemInstance] = set((attr["requires_key"],)) if attr["requires_key"] else None
            self.key_is_placed_elsewhere = attr.get("key_is_placed_elsewhere")

        if "can_open" in self.item_type or "container" in self.item_type:
            self.can_be_opened = attr["can_be_opened"]
            self.is_open = attr["is_open"]
            self.can_be_closed = attr["can_be_closed"]

        if "electronics" in self.item_type: # still wondering if these should be in a dict or not. This is fine for now.
            self.requires_powered_location:bool = attr.get("requires_powered_location")
            self.can_be_charged:bool = attr.get("can_be_charged")
            self.is_charging:bool = attr.get("is_charging")
            self.is_charged:bool = attr.get("is_charged")
            self.takes_batteries:bool = attr.get("takes_batteries")
            self.has_batteries:itemInstance = attr.get("has_batteries")
            self.is_on:bool = attr.get("is_on")

        if "battery" in self.item_type:
            self.can_be_charged:bool = attr.get("can_be_charged")
            self.is_charged:bool = attr.get("is_charged")
            self.in_use:itemInstance|bool = attr.get("in_use")
            if hasattr(self, "can_be_charged"):
                self.verb_actions.add("can_charge")

        if "charger" in self.item_type:
            self.requires_powersource: bool = attr.get("requires_powersource")
            self.in_use:itemInstance|bool = attr.get("in_use")

        if "transition" in self.item_type:
            self.int_location = attr.get("int_location")
            self.ext_location = attr.get("ext_location")

        if "is_cluster" in self.item_type:
            self.has_multiple_instances:str = attr.get("has_multiple_instances")
            self.single_identifier:str = attr.get("single_identifier")
            self.plural_identifier:str = attr.get("plural_identifier")

        if "transition" in self.item_type:
            self.is_transition_obj:bool = attr.get("is_transition_obj")
            self.int_location:cardinalInstance = attr.get("int_location")
            self.ext_location:cardinalInstance = attr.get("ext_location")

        if "loc_exterior" in self.item_type:
            self.is_loc_exterior:bool = attr.get("is_loc_exterior")
            self.transition_objs:set[itemInstance] = attr.get("transition_objs", set())
            #self.has_door:bool = attr.get("has_door")

        if "door_window" in self.item_type:
            self.is_door = attr.get("is_door", False)
            self.is_window = attr.get("is_window", False)
            self.is_other = attr.get("is_other", False)

        if "random_loot" in self.item_type or "starting_loot" in self.item_type:
            self.loot_type = attr.get("loot_type")
            if not self.loot_type and "starting_loot" in self.item_type:
                self.loot_type = "starting_loot"


    def __init__(self, definition_key:str, attr:dict):
        #print(f"\n\n@@@@@@@@@@@@@@@@@ITEM {definition_key} in INIT ITEMINANCE@@@@@@@@@@@@@@@\n\n")
        #print(f"definition_key: {definition_key}, attr: {attr}")
        import uuid
        self.id = str(uuid.uuid4())  # unique per instance
        self.short_id = self.id.split("-")[-1]
        self.material_type:str = "generic"
        self.on_break:str = "generic"

         #     INITIAL FLAG MANAGEMENT
        #print(f"VARS before attributes are assigned: {vars(self)}")
        self.verb_actions:set[str] = set()
        for attribute in ("can_pick_up", "can_be_opened", "print_on_investigate", "can_be_locked"):
            if attr.get(attribute): # should this apply the value too? For some, it's false.
                self.verb_actions.add(attribute)

        self.item_type = self.clean_item_types(attr["item_type"])
        self.set_itemtype_attrs(attr)

        self.name:str = definition_key
        self.print_name = self.name
        self.nicenames:dict[str, str] = attr.get("nicenames", dict({"generic": self.name}))

        self.nicename:str = self.nicenames.get("generic")
        if not self.nicename:
            for entry in self.nicenames:
                self.nicename = self.nicenames[entry]
                break # entirely arbirary. Need to rejig the description-selection function to do nicenames too.

        self.colour:str = None
        self.descriptions:dict[str, str] = attr.get("descriptions")

        self.description:str = attr.get("description") # will be initd shortly, depending on item conditions. Use default if found for simple objects with no alt names.
        #print(f"Name: {self.name} // self.description in init: {self.description}")
        self.starting_location:dict = attr.get("starting_location") # currently is str

        self.location:cardinalInstance = loc.no_place
        from eventRegistry import eventInstance
        self.event:eventInstance = None
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

        if hasattr(self, "is_hidden") and self.is_hidden:
            self.set_hidden()

        for attribute in attr: # want to remove this and do it intentionally instead.
            if not hasattr(self, attribute):
                #if attribute in ["can_read", "can_burn", "is_burned", "item_size", "print_on_investigate", "slice_attack", "slice_defence", "smash_attack", "smash_defence", "flammable", "on_burn", "exceptions"]:
                setattr(self, attribute, attr[attribute])
                #else:
                    #print(f"ATTR MISSING FROM SELF for {self.name}: {attribute}")
                    #print(f"self.item_type: {self.item_type}")



    def __repr__(self):
        #print("self.colour: ", self.colour)

        #item = f"\033[30;44m<eventInst {self.name} ..{self.short_id}>\033[0m"
        event = self.event if hasattr(self, "event") else None
        if event:
            event = f"'{event.name}' ID:{event.short_id} state: {event.state}"
        if self.colour:
            if not hasattr(self, "code"):
                from tui.colours import Colours
                self.code = getattr(Colours, self.colour.upper())
        if hasattr(self, "code"):
            item = f"\033[{self.code + 10}m{self.name} ID:{self.short_id}\033[0m"
        else:
            item = f"{self.name} ID:{self.short_id}"


        text = f"<ItemInst [{item}] [{(f'\033[32mContainer: {self.contained_in}\033[0m') if hasattr(self, 'contained_in') and self.contained_in else (f'loc: {self.location.place_name}') if self.location else ''}] [event:{event}] {(f"[clusters: {self.has_multiple_instances}]" if hasattr(self, 'has_multiple_instances') else '')}>"
        #if self.colour and config.coloured_repr:
            #if not hasattr(self, "code"):
                #from tui.colours import Colours
                #self.code = getattr(Colours, self.colour.upper())
            #coloured_text = f"\033[{self.code + 10}m{text}"
        #else:
            #coloured_text=text
        #return coloured_text + "\033[0m"
        return text + "\033[0m"
        #return f"<ItemInstance {self.name} / ({self.id}) / {self.location.place_name} / {self.event if hasattr(self, "event") else ''}/ {(self.has_multiple_instances if hasattr(self, 'has_multiple_instances') else '')}>"


class itemRegistry:
    """
    Central manager for all item instances.
    Also keeps a location-indexed lookup for fast "what's here?" queries.
    """

    def __init__(self):

        self.instances:set[itemInstance] = set()
        self.by_id: dict[str, itemInstance] = {}    # id -> ItemInstance
        self.by_location: dict[cardinalInstance, set[itemInstance]] = {}  # (cardinalInstance) -> set of itemInstances
        self.by_name: dict[str, set[itemInstance]] = {}        # definition_key -> set, of itemInstances Why is this a list but the others are sets?
        self.by_alt_names:dict[str, str] = {}

        self.by_category = {}        # category (loot value) -> set of instance IDs
        self.by_container:dict[itemInstance] = {}

        self.plural_words = {}

        self.temp_items = set()

        self.new_parents = set() ## new_parents, ID is added to all containers. Then after initial generation, force a parent/child check.
        self.child_parent = {} # just for storing the parings, for comparing child/parents directly when midway through the generation to keep things straight.

        self.keys:set[itemInstance] = set()

        self.locks_keys:dict[itemInstance, set[itemInstance]] = {}

        self.item_defs: dict[str: dict] = {}

        self.transition_objs:set[itemInstance] = set()
        self.door_open_strings = ["the door creaks, but allows you to head [[inside]].", "the door creaks slightly as you make your way [[inside]].", "you open the door and make your way [[inside]].", "you open the door and head [[inside]]."]
    # -------------------------
    # Creation / deletion
    # -------------------------

    def add_transition_objs(self, inst:itemInstance):

        if "transition" in inst.item_type:
            #print(f"TRANSITION ITEM: {inst.name}")
            ## This is for transition objects like doors, NOT loc_exterior instances.
            int_location = loc.by_cardinal_str(inst.int_location)
            ext_location = loc.by_cardinal_str(inst.ext_location)

            if not hasattr(int_location, "transition_objs"):
                setattr(int_location, "transition_objs", set())
            int_location.transition_objs.add(inst)
            if inst.name in int_location.transition_objs:
                int_location.transition_objs.remove(inst.name)

            if inst.name in int_location.place.transition_objs:
                int_location.place.transition_objs[inst] = int_location
                int_location.place.transition_objs.pop(inst.name)


            if not hasattr(ext_location, "transition_objs"):
                setattr(ext_location, "transition_objs", set())
            ext_location.transition_objs.add(inst)
            if inst.name in ext_location.transition_objs:
                ext_location.transition_objs.remove(inst.name)

            if inst.name in ext_location.place.transition_objs:
                ext_location.place.transition_objs[inst] = ext_location
                ext_location.place.transition_objs.pop(inst.name)

            inst.int_location = int_location # adding it back in case int_loc was str previously.
            inst.ext_location = ext_location

            setattr(int_location, "location_entered", False)
            setattr(ext_location, "location_entered", False)
            inst.is_transition_obj = True

    def init_single(self, item_name:str, item_entry:dict = None, apply_location:bool = False) -> itemInstance:
        """Generate an ItemInstance from `item_name`. If no item_entry is provided, it will use `item_defs[item_name]`.\n\n `apply_location` if given should be a `cardinalInstance` object, or a string suitable for `by_cardinal_str`. This is use to place the new item directly in a given location."""
        #print(f"\n\n[init_single] ITEM NAME: {item_name}")
        #print(f"[init_single] ITEM ENTRY: {item_entry}\n\n")
        if not item_entry:
            if self.item_defs.get(item_name):
                item_entry = self.item_defs[item_name]
            else:
                print(f"No item entry provided for `{item_name}` and no entry found in registry.item_defs. Cannot build without knowing what it is.")
                exit()
        inst = itemInstance(item_name, item_entry)
        all_items_generated.add(inst)
        self.instances.add(inst)

        self.item_defs[item_name] = item_entry

        if not self.by_name.get(inst.name):
            self.by_name[inst.name] = set()
        self.by_name[inst.name].add(inst)
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

        if not hasattr(inst, "is_scenery"): # exclude floors/walls
            if location:
                if not hasattr(inst, "contained_in") or inst.contained_in == None:
                    if isinstance(location, cardinalInstance):
                        cardinal_inst = location
                    else:
                        cardinal_inst = loc.by_cardinal_str(location)
                    self.by_location.setdefault(cardinal_inst, set()).add(inst)
                    inst.location = cardinal_inst

            if apply_location:
                #basically just for godmode add item
                if not isinstance(apply_location, cardinalInstance):
                    apply_location = loc.by_cardinal_str(apply_location)
                self.by_location.setdefault(apply_location, set()).add(inst)
                inst.location = apply_location

            if item_entry.get("alt_names"):
                for altname in item_entry.get("alt_names"):
                    self.by_alt_names[altname] = item_name

        if hasattr(inst, "starting_children") and getattr(inst, "starting_children"):
            self.new_parents.add(inst.id)
            registry.generate_children_for_parent(parent=inst)

        if "key" in inst.item_type:
            self.keys.add(inst)

        self.instances.add(inst)

        self.init_descriptions(inst)
        self.add_transition_objs(inst)

        #if inst.name == "broken glass shard":
        #    print(vars(inst))
        return inst

    def get_item_from_defs(self, item_name):

        if item_name in list(self.item_defs):
            inst = self.init_single(item_name, self.item_defs[item_name])
            all_item_names_generated.append((inst, "get_item_from_defs"))
            return inst


    def delete_instance(self, inst: itemInstance):
        """Removes an instance from:
             * itemRegistry.by_location
             * locRegistry.inv_place.items if present
             * from any container it's in
             * membrane.plural_words_dict if applicable
             * and finally, from itemRegistry.instances"""
        if inst.location and inst.location in self.by_location and inst in self.by_location[inst.location]:
            self.by_location[inst.location].remove(inst)
            print(f"remove from inst.location: {inst.location}")
            if inst.location == loc.inv_place:
                loc.inv_place.items.remove(inst)


        inst.location = loc.no_place
        if hasattr(inst, "contained_in"):
            container = inst.contained_in
            if hasattr(container, "children"):
                container.children.remove(inst)
            inst.contained_in = None
        self.by_name.get(inst.name, list()).remove(inst)

        if " " in inst.name and not self.by_name.get(inst.name): # don't remove from plural words if there are other instances with the same name.
            from verb_membrane import membrane
            if membrane.plural_words_dict.get(inst.name):
                membrane.plural_words_dict.pop(inst.name)
        inst = self.instances.remove(inst)
        if not inst:
            return
        print(f"Inst was not deleted entirely: {inst}")

    def item_def_by_attr(self, attr_str="", loot_type=None, open=None, locked=None):

        if open or locked:
            items = (i for i in self.item_defs if "container" in i.get("item_type"))

        if attr_str:
            items = (i for i in self.item_defs if hasattr(i, attr_str))

        if loot_type:
            items = list()
            for item, vals in self.item_defs.items():
                if "loot_type" in vals and loot_type in vals.get("loot_type"):
                    items.append(item)
        return items

    def items_by_attr(self, attr_str="", loot_type=None, open=None, locked=None, location=None):
        """Not used currently. May redo and use again, or just remove entirely."""
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

    def generate_children_for_parent(self, parent=None):
        """Generates child itemInstances for the given parent from parent.starting_children."""
        logging_fn()

        def get_children(parent:itemInstance):

            instance_children = []
            instance_count = 0
            if isinstance(parent.starting_children, str):
                temp = []
                temp.append(parent.starting_children)
                parent.starting_children = temp

            if parent.starting_children == None:
                return
            if parent.starting_children != None and isinstance(parent.starting_children, list|set|tuple):
                multiples = 1
                for child in parent.starting_children:
                    if "[[" in child:
                        multiples = child.split("[[")[1]
                        multiples = int(multiples.replace("]]", ""))
                        child = child.split("[[")[0].strip()

                    def find_or_make_children(child, parent, instance_count, instance_children):
                        target_child = None
                        if isinstance(child, itemInstance):
                            instance_children.append(child)
                            instance_count += 1
                            parent.children.add(child) # changed from 'target_child' here and next line. Not sure why there was the distinction.
                            child.contained_in = parent
                            return instance_count, instance_children

                        if child in self.item_defs:
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

                        return instance_count, instance_children

                    for _ in range(0,multiples):
                        instance_count, instance_children = find_or_make_children(child, parent, instance_count, instance_children)

                if len(instance_children) == len(parent.starting_children):
                    parent.starting_children = instance_children
                    registry.new_parents.remove(parent.id)
                elif multiples > 1 and len(instance_children) == (len(parent.starting_children) + multiples - 1):
                    parent.starting_children = instance_children
                    registry.new_parents.remove(parent.id)

                else:
                    if (len(instance_children) + len(registry.child_parent) == len(parent.starting_children)) or (len(parent.starting_children) == instance_count):
                        registry.new_parents.remove(parent.id)
                    else:
                        exit(f"Not all children found/made as instances. Str list:\n   {parent.starting_children}\nInstance list:\n    {instance_children}\nchild/parent dict: {registry.child_parent}") # again, right now hard exit if this ever fails. Need to see why if it does.

        if parent:
            get_children(parent)

        else:
            if registry.new_parents and registry.new_parents != None:
                for parent in registry.new_parents:
                    if isinstance(parent, str):
                        parent = registry.by_id.get(parent)
                    get_children(parent)

    def clean_relationships(self):
        """Aligns 'requires_key' and 'unlocks' attributes with their respective partners, replacing the item name with an instance where possible."""
        def cleaning_loop():

            itemlist = frozenset(self.by_id)

            for item_id in itemlist:
                item = self.by_id.get(item_id)

                if not item:
                    exit(f"Failed to get instance by id in cleaning_loop for instance ({item_id}).")

                key_found = False
                if hasattr(item, "requires_key") and item.requires_key and not isinstance(getattr(item, "requires_key"), bool):
                    #print(f"item.requires key at start: {item.requires_key}")
                    if isinstance(item.requires_key, itemInstance):
                        continue
                    for maybe_key in registry.keys:
                        #print(f"maybe_key in registry.keys: {maybe_key}")
                        #if hasattr(maybe_key, "unlocks") and getattr(maybe_key, "unlocks"):
                        #    print(f"maybe_key unlocks: {maybe_key.unlocks}")
                        #    continue
                        #print(f"item.requires_key: {item.requires_key}")
                        if maybe_key.name in item.requires_key:
                            #for key in item.requires_key:
                                #print(f"Item in requires_key (instance in set): {key}")
                            #print(f"maybe_key.name == item.requires_key: {maybe_key.name} // {key}")
                            if (hasattr(maybe_key, "is_key_to") and maybe_key.is_key_to) or not (hasattr(maybe_key, "is_key_to") and maybe_key.is_key_to):
                                if hasattr(maybe_key, "is_key_to") and maybe_key.is_key_to:
                                    lock_match = True
                                    for lock in maybe_key.is_key_to:
                                         if lock != item.name:
                                            continue
                                         lock_match = True
                                    if not lock_match:
                                        continue
                                #print("is_key_to etc succeeds")
                                for a in (maybe_key, item):
                                    self.locks_keys.setdefault(a, set())

                                self.locks_keys[item].add(maybe_key)
                                self.locks_keys[maybe_key].add(item)
                                item.requires_key = self.locks_keys[item]#maybe_key
                                setattr(maybe_key, "unlocks", self.locks_keys[maybe_key])
                                key_found = True
                                #print(f"key_found True: {maybe_key} // item: {item}")
                                break
                            else:
                                #print(f"item {item} failed the is_key_to check with maybe_key: {maybe_key}.")
                                if hasattr(maybe_key, "is_key_to"):
                                    print(f"maybe key is_key_to: {maybe_key.is_key_to}")
                                    if maybe_key.is_key_to:
                                        print(f"maybe_key.is_key_to is true: {maybe_key.is_key_to}")
                                        exit()
                    if not key_found:
                        for key in item.requires_key:
                            if not isinstance(key, str):
                                continue
                            if self.item_defs.get(key):
                                print(f"Not key_found, init_single 'requires_key: {item.requires_key}")
                                target_obj = self.init_single(key, self.item_defs.get(key))
                                all_item_names_generated.append((target_obj, "generate key from item_defs"))
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

        try:
            cleaning_loop()
        except Exception as E:
            print(f"Exception: {E}")


    def run_check(self, inst:itemInstance) -> tuple[itemInstance|None, int, str]: ## replaced check_item_is_accessible with this, as all check_item_is_accessible did was run this. Previously it used to do noun selection, but it doesn't any more.
        """
        Checks the current state of the given itemInstance, returning (the instance's container if found, the reason_val, and the meaning string for that reason.)\n
        ### Reason_val: meaning --\n
        0: "accessible"\n
        1: "in a closed local/accessible container"\n
        2: "in a locked local/accessible container"\n
        3: "in an open container in your inventory"\n
        4: "in an open container accessible locally, can pick up but not drop"\n
        5: "in inventory"\n
        6: "not at current location"\n
        7: "other error, investigate"\n
        8: "is a location exterior"\n
        9: "item is hidden" (must be discovered somehow, not shown in general 'look around' views.)\n
        10: "not an instance"
        """
        logging_fn()
        from misc_utilities import is_item_in_container, accessible_dict
        confirmed_container = None
        reason = 7
        meaning = "other error, investigate"
        from npcRegistry import npcInstance
        if not inst or not isinstance(inst, itemInstance|npcInstance):
            return None, 10, accessible_dict[10]

        if inst.is_hidden == True:
            if hasattr(inst, "has_multiple_instances") and inst.has_multiple_instances == 0:
                pass
            else:
                if hasattr(inst, "has_multiple_instances"):
                    print(f"hidden inst multiple instance count: {inst.has_multiple_instances}")

                print("INST is_hidden in run_check; not a singleton multiple_instances.")
                return None, 9, accessible_dict[9]

        if "battery" in inst.item_type:
            #device_using_battery = inst.in_use
            if inst.in_use and isinstance(inst.in_use, itemInstance):
                return None, 9, accessible_dict[9] # Originally returned the device inst, but it breaks things later. So we treat as invisible, then check 'if this thing is invisible, is it a battery' afterwards.

        container = is_item_in_container(inst)
        #print(f"inst: {inst}")
        if inst.location == loc.inv_place and not container:
            reason = 5
            meaning = accessible_dict[reason]
            return None, reason, meaning

        if container:
            print(f"container: {container}")
            if container.location == loc.inv_place:
                confirmed_container = container
                if hasattr(confirmed_container, "is_open") and not confirmed_container.is_open:
                    #print(f"confirmed_container {confirmed_container} is_closed, apparently.")
                    reason = 1
                elif (hasattr(confirmed_container, "is_locked") and getattr(confirmed_container, "is_locked")):
                    reason = 2
                else:
                    reason = 3
            elif container.location == loc.current:
                confirmed_container = container
                if hasattr(confirmed_container, "is_open") and not confirmed_container.is_open:
                    #print(f"[run_check] Container {confirmed_container.name} is closed by is_open flag.")
                    reason = 1
                elif hasattr(confirmed_container, "is_locked") and getattr(confirmed_container, "is_locked"):
                    #print(f"[run_check] Container {confirmed_container} is locked.")
                    reason = 2
                else:
                    reason = 4
            else:
                reason = 6

        else:
            if inst.location == loc.current:
                reason = 0
            else:
                if inst.location == loc.inv_place:
                    reason = 5
                else:
                    if hasattr(inst, "is_transition_obj") and inst.is_transition_obj:
                        if hasattr(inst, "int_location") and (inst.int_location ==  loc.current or inst.ext_location == loc.current):
                            reason = 0 ## treat it as local whether we're inside or outside
                        else:
                            reason = 6

                    elif hasattr(inst, "is_loc_exterior") and inst.location.place == loc.current.place:
                        reason = 8

                    else:
                        reason = 6

        meaning = accessible_dict[reason]

        return confirmed_container, reason, meaning


    def set_print_name(self, inst:itemInstance, new_print_name:str):
        """Sets inst.print_name to the given string, and updates instance descriptions before returning."""
        logging_fn()
        inst.print_name = new_print_name
        self.init_descriptions(inst)

    def get_parent_details(self, inst:itemInstance, old_container:itemInstance, new_container:itemInstance)->tuple[itemInstance, bool, itemInstance]:
        """Gets current parent/container of itemInstance, and prepares the new_container (if given) with .children."""
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

    def generate_alt_state_item(self, item_name:str, noun:itemInstance, state_change:bool) -> dict:
        """Generates the item_def for an altered version of an existing item, based on a specified state change (eg 'is_burned', 'is_broken').\n\nUsed for permanent replacement of one instance with another, not a simple attribute/value change."""
        logging_fn()
        #print(f"\nITEM NAME: {item_name} // NOUN: {noun} // in generate_alt_state_items\n")
        item_def = self.item_defs.get(noun.name)
        if not item_def:
            print(f"No item def found for {noun.name}.")
            exit()
        new_name = item_name.replace("[[item_name]]", noun.name)
        import copy
        new_def = copy.deepcopy(item_def)
        #print(f"NEW_DEF: {new_def}")
        if not new_def:
            print(f"NO NEWDEF in generate_alt_state_item. Itemdef: {item_def}")
        for k, v in new_def.items():
            #print(f"k: {k}, v: {v}, v.type: {type(v)}")
            if noun.name in k:
                k = k.replace(noun.name, new_name)
            if isinstance(v, bool|int):
                new_def[k] = v

            elif isinstance(v, dict):
                for val, val2 in v.items():
                    #print(f"val, val2: {val}, {val2} // noun.name: {noun.name} // new_name: {new_name}")
                    if isinstance(val, str):
                        if noun.name in val:
                            val = val.replace(noun.name, new_name)
                            v[val] = val2
                        if noun.name in val2:
                            val2 = val2.replace(noun.name, new_name)
                            v[val] = val2

            else:
                if isinstance(v, str) and noun.name in v:
                    v = v.replace(noun.name, new_name)
                new_def[k] = v

        if "broken" in state_change:
            new_def["is_broken"] = True
        if "burned" in state_change:
            new_def["is_burned"] = True

        new_def["starting_location"] = noun.location

        return new_def

    def combine_clusters(self, shard:itemInstance, target: (cardinalInstance|itemInstance)):
        """For combining cluster items when dropped at a location. Will attempt to merge the 'shard' (instance in inventory) with any existing cluster instance of the same type.\n\n The shard is assigned .is_hidden=True and remains in this place to be picked up again later, while the cluster it merged with gains its cluster value.\n\nIf no cluster exists, the shard is dropped like a regular item."""
        logging_fn()
        target_is_location = False
        if isinstance(target, cardinalInstance):
            target_is_location = True

        #actually the below isn't always bad, if we're in a location we can say 'put moss in jar' without picking it up first and then this will trigger.
        if shard.location != loc.inv_place and shard.location != loc.no_place:
            if not target_is_location:
                if target.location == loc.current:
                    print("moving from compound to a container, that's okay.")
            else:
                print(f"\n{shard} is not in inv_place OR NO_PLACE. This is bad, how are we combining if not removing from inventory?\n\n\n")
        #print(f"Start of combine_clusters: shard: {shard} // target: {target}")
        if not target_is_location and shard.has_multiple_instances == 1:
            print("shard has multiple instances of 1")
            return shard, "no_local_compound" # returning so it can be added to the container. No merging in containers. Not sure if I want to combine multiples inside containers or not, but for now we just treat them the same way as inventory.
        print("TARGET: {target}")
        if target_is_location and target == loc.inv_place:
            if hasattr(shard, "contained_in") and shard.contained_in:
                print(f"moving {shard} from container to inv")
                return shard, "no_local_compound"



        compound_target = None
        print(f"TARGET: {target}")
        from interactions.item_interactions import get_correct_cluster_inst
        if isinstance(target, itemInstance):
            compound_target = get_correct_cluster_inst(shard, shard.name, local_items=None, local_only = True, access_str = "drop_target", allow_hidden=False, priority="plural")
            print(f"Compound target first try: {compound_target}")

        if not compound_target:
            compound_target = get_correct_cluster_inst(shard, shard.name, local_items=None, local_only = True, access_str = "drop_target", allow_hidden=True, priority="plural")
            print(f"Compound target second try: {compound_target}\n")

        if not compound_target:
            from printing import print_yellow
            print_yellow("No compound target")
            return shard, "no_local_compound"

        if compound_target == shard:
            if shard.has_multiple_instances > 1:
                shard_loc = str(shard.location.place_name)
                shard, compound_target = self.separate_cluster(shard, origin=loc.current, origin_type="location")
                print(f"compound_target: {compound_target} // shard: {shard}")
                if not target_is_location:
                    if shard_loc != loc.inv_place.place_name and shard_loc != loc.no_place.place_name:
                        compound_target.location = loc.by_cardinal_str(shard_loc)
                        if compound_target in loc.inv_place.items:
                            loc.inv_place.items.remove(compound_target)
                        if compound_target in self.by_location[loc.inv_place]:
                            self.by_location[loc.inv_place].remove(compound_target)
                        self.by_location[compound_target.location].add(compound_target)
                return shard, compound_target
            else:
                return shard, "no_local_compound"
        print(f"Compound target: {compound_target} // shard: {shard}")

        if not hasattr(shard, "has_multiple_instances") or not hasattr(compound_target, "has_multiple_instances") or shard.name != compound_target.name:
            return False, False

        total_instances = shard.has_multiple_instances + compound_target.has_multiple_instances
        compound_target.has_multiple_instances = total_instances
        shard.has_multiple_instances = 0
        #if self.by_location.get(shard.location):
            #f shard in self.by_location[shard.location]:
                #self.by_location[shard.location].remove(shard)
        shard.location = target
        registry.by_location[target].add(shard)
        setattr(shard, "is_hidden", True) # switching these up, so we do drop the shard, but leave it invisible at the target location.
        #if shard in self.by_location[loc.inv_place]:
            #self.by_location[loc.inv_place].remove(shard)
        #else:
            #print(f"{shard} was not in by_location[loc.inv_place].")
        #if shard in loc.inv_place.items:
            #loc.inv_place.items.remove(shard)
        #else:
            #print(f"{shard} was not in by_location[loc.inv_place].")

        total_instances = shard.has_multiple_instances + compound_target.has_multiple_instances
        #print("total_instances: ", total_instances, "inst.has_multiple_instances: ", shard.has_multiple_instances, "+ inst_at_target: ", compound_target.has_multiple_instances)
        compound_target.has_multiple_instances = total_instances
        shard.has_multiple_instances = 0
        print(f"AT END OF COMBINE_CLUSTERS: Compound_target: {compound_target} // shard: {shard}\n")
        return shard, compound_target

    def separate_cluster(self, compound_inst:itemInstance, origin:itemInstance|cardinalInstance, origin_type:str):
        """To select the correct cluster instance to pick up,  and/or separate a single instance from a multiple-value cluster.\n\nEnsures the total value of the cluster is maintained, so a source is not infinite but limited to the starting value of has_multiple_instances of the initial cluster item."""
        ## PICKING UP FROM CLUSTER IN LOCATION/CONTAINER
        logging_fn()
        if not hasattr(compound_inst, "has_multiple_instances"):
            return False, None

        from interactions.item_interactions import find_local_item_by_name
        if isinstance(compound_inst, itemInstance):
            noun=compound_inst
        else:
            print(f"Separate_cluster has a compound_inst that is not an inst: {compound_inst}")
            exit()

        if hasattr(noun, "has_multiple_instances") and noun.has_multiple_instances in (0, 1):
            shard = noun ## we assume it's correct and don't check again.
            ## but we do need compound_noun to say where it 'came' from.
            if isinstance(origin, itemInstance) and not "is_cluster" in origin.item_type and "container" in origin.item_type:
                print("Taking from a container. Don't need to find compound_inst if we're taking from a container.")
            compound_test = find_local_item_by_name(noun=noun, verb="take", access_str = "pick_up", current_loc = loc.current, priority = "plural")
            if compound_test:
                compound_inst = compound_test
        else:
            shard = None
            if registry.by_location.get(loc.current):
                local_items = registry.get_item_by_location()
                if local_items:
                    singletons = list(i for i in local_items if i.name == noun.name and i.has_multiple_instances == 0)

                    if singletons:
                        #print(f"SINGLETONS: {singletons}")
                        shard = singletons[0]

            if not shard:

            #else:
                local_item = find_local_item_by_name(noun=noun, verb="take", access_str = "pick_up", current_loc = loc.current, hidden_cluster=True)
                if local_item and hasattr(noun, "has_multiple_instances") and noun.has_multiple_instances == 0:
                    shard = local_item
                #print(f"Shard is local_item: {shard}. noun.has_multiple_instances: {noun.has_multiple_instances}")
                else:
                    #print(f"Shard is not local_item: {local_item}. noun.has_multiple_instances: {local_item.has_multiple_instances}")
                    new_def = registry.item_defs.get(compound_inst.name)
                    if origin_type == "location":
                        new_def["exceptions"] = {"starting_location": origin}

                    shard = registry.init_single(compound_inst.name, new_def)
                    all_item_names_generated.append((shard, "separate_cluster"))

        #print(f"shard:  {shard} //  cluster {compound_inst}")
        if origin_type == "location":
            if compound_inst not in self.by_location[origin] and compound_inst != shard:
                print(f"For some reason the compound instance isn't already at {origin}")
                self.by_location[origin].add(compound_inst)
            if shard in self.by_location[origin]:
                self.by_location[origin].remove(shard)

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
                #print(f"No multiple_instances item in {origin}")
                container.children.add(compound_inst)

            if existing_contained_item:
                compound_inst = existing_contained_item

            shard.location = loc.no_place
        else:
            print(f"No origin? {shard} // critical failure.")
            exit()

        starting_instance_count = compound_inst.has_multiple_instances
        compound_inst.has_multiple_instances = starting_instance_count - 1
        shard.has_multiple_instances = 1
        #print("compound_inst.has_multiple_instances: ", compound_inst.has_multiple_instances)
        #print("shard.has_multiple_instances: ", shard.has_multiple_instances)
        shard.location = loc.inv_place
        loc.inv_place.items.add(shard)
        self.by_location[loc.inv_place].add(shard)
        setattr(shard, "is_hidden", False)
        #print(f"AT END OF SEPARATE_CLUSTERS: Compound_target: {compound_inst} // shard: {shard}\n")
        #print(f"returning {shard}")
        return compound_inst, shard # <- separated, new_singular

    # -------------------------
    # Movement
    # -------------------------

    def move_cluster_item(self, inst:itemInstance, location:cardinalInstance=None, new_container:itemInstance=None, old_container:itemInstance=None)->itemInstance:
        """Move a cluster-type item from A-B. Uses preset preferences to determine best option for subject/target, and uses combine_cluster and separate_cluster as needed for the operation."""

        old_loc = inst.location
        parent, was_in_container, new_container = self.get_parent_details(inst, old_container, new_container)

        if new_container and isinstance(new_container, itemInstance) and inst.has_multiple_instances in (0, 1):
            inst.location = loc.no_place
            loc.no_place.items.add(inst)
            new_container.children.add(inst)
            inst.contained_in = new_container
            if was_in_container:
                print(f"was in container: {was_in_container} / parent; {parent} / parent.children: {parent.children}")
                inst.contained_in = None
                parent.children.remove(inst)
                return inst, None

        if hasattr(inst, "contained_in") and inst.contained_in and location and location == loc.inv_place:
            print(f"Was contained in and going to inv_place: {inst}")
            return inst, "process_as_normal"

        from misc_utilities import has_and_true
        if has_and_true(inst, "contained_in"):
            inst.contained_in = None

        is_drop = True

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
            printing.print_yellow(f"going to combine_clusters. Shard: {inst}, target: {target}")
            shard, compound_target = self.combine_clusters(inst, target)
            printing.print_yellow(f"After combine_clusters: Shard: {shard} // compound target: {compound_target}")
            if compound_target == "no_local_compound":
                print("no local compound, returning shard from move_cluster_item")
                return shard, "process_as_normal"
            if compound_target.has_multiple_instances == 0: # This'll never happen in is_drop... #DETELEME later.
                print(f"Compound_target {compound_target} is exhausted, removing from everywhere. compound_target.has_multiple_instances == 0 in itemReg.")
                exit()

            from testing_coloured_descriptions import init_loc_descriptions
            init_loc_descriptions(loc.current.place, loc.current)

            self.init_descriptions(compound_target)
            return shard, None

        origin = (parent if was_in_container else old_loc)
        #if isinstance(origin, itemInstance) and not "is_cluster" in origin.item_type and "container" in origin.item_type:
        success, shard = self.separate_cluster(inst, origin=origin, origin_type="container" if was_in_container else "location")
        print(f"origin: {origin} // shard: {shard}")
        if not success:
            print(f"separate cluster failed. Reported shard: {shard}, original inst: {inst}, origin: {origin}")
            exit()
        if success and isinstance(success, itemInstance):
            if hasattr(success, "has_multiple_instances"):
                if success.has_multiple_instances == 0:
                    print(f"Success ({success}) has multiple instances of 0 and will be removed.")
                    self.delete_instance(success)
                self.init_descriptions(success)
                from testing_coloured_descriptions import init_loc_descriptions
                init_loc_descriptions(loc.current.place, loc.current)

        return shard, None

    def clear_parent_and_old_loc(self, inst:itemInstance, old_container:itemInstance, new_container:itemInstance, new_location:cardinalInstance, old_loc:cardinalInstance,  updated:set=set()):
        print(f"old_container: {old_container} / new_container: {new_container} / location: {new_location}")
        if old_container:
            # moved from old_container to location
            updated.add(old_container)
            from misc_utilities import has_and_true
            if new_container and (has_and_true(inst, "contained_in") and inst.contained_in != new_container) or not has_and_true(inst, "contained_in"):
                inst.contained_in = new_container
                if inst not in new_container.children:
                    new_container.children.add(inst)
                updated.add(new_container)
            if old_container and has_and_true(old_container, "children") and inst in old_container.children:
                old_container.children.remove(inst)
                updated.add(old_container)


        if old_loc and old_loc != loc.no_place:
            if self.by_location.get(old_loc):
                if inst not in self.by_location[old_loc]:
                    print(f"Inst has a location but isn't in by_location for old_loc. FIX THIS. old_loc: {old_loc}")
                else:
                    self.by_location[old_loc].discard(inst)
                #f old_loc == inst.location:
                if new_location:
                    inst.location = new_location
                elif new_container:
                    inst.location = loc.no_place
                    inst.contained_in = new_container
                    new_container.children.add(inst)
                print(f"Removed {inst} from {old_loc}. Current location for inst is {inst.location}")

            if old_loc == loc.inv_place:
                if inst in loc.inv_place.items:
                    if self.by_location.get("inv_place") and inst in self.by_location.get(loc.inv_place):
                        self.by_location[loc.inv_place].remove(inst)
                    loc.inv_place.items.remove(inst)
                if inst.location == loc.inv_place:
                    inst.location = loc.no_place ## We don't add items to by_location for no_place, this is purely so the location data can be printed in print lines.
        return updated

    def move_item(self, inst:itemInstance, location:cardinalInstance=None, new_container:itemInstance=None, old_container:itemInstance=None, no_print=False, simple_move = False)->itemInstance:
        """Moves an itemInstance from its current location to a new 'location'. The new location can be the player inventory, a cardinalInstance or a container object. Updates item descriptions when complete."""
        logging_fn()
        from misc_utilities import assign_colour
        updated = set()
        if location and isinstance(location, str) and location == "current":
            location = loc.current

        old_loc = inst.location

        if "is_cluster" in inst.item_type and not simple_move: # added 'simple move' for certain event inits where move_cluster_items gets really confused. It's a workaround.
            #print(f"INST going to move_cluster_item: {inst}")
            outcome, other = self.move_cluster_item(inst, location, new_container, old_container)
            #print(f"inst: {inst}, outcome: {outcome} // other: {other}")
            updated.add(outcome)
            updated.add(inst)
            if other != "process_as_normal":
                #print("outcome, old_container, new_container, location, old_loc, updated: ", outcome, old_container, new_container, location, old_loc, updated)
                print("Not process as normal. All moves need to be done already.")
                updated = self.clear_parent_and_old_loc(outcome, old_container, new_container, location, old_loc, updated)
                for item in updated:
                    self.init_descriptions(item)
                return outcome
            inst = outcome
            old_loc = inst.location

        was_in_container = False # using this as a check to see if the cluster should use old_loc or parent.

        ## REMOVE FROM ORIGINAL LOCATION ##
        """if old_loc and old_loc != None:
            if self.by_location.get(old_loc):
                if inst not in self.by_location[old_loc]:
                    print(f"Inst has a location but isn't in by_location for old_loc. FIX THIS. old_loc: {old_loc}")
                else:
                    self.by_location[old_loc].discard(inst)

            if old_loc == loc.inv_place:
                if inst in loc.inv_place.items:
                    loc.inv_place.items.remove(inst)
                inst.location = loc.no_place ## We don't add items to by_location for no_place, this is purely so the location data can be printed in print lines."""
        if not old_container:
            if hasattr(inst, "contained_in") and inst.contained_in and (not new_container or not new_container == inst.contained_in):
                old_container = inst.contained_in
        updated = self.clear_parent_and_old_loc(inst, old_container, new_container, location, old_loc, updated)

        ## MOVE TO NEW LOCATION IF PROVIDED
        if location != None:
            if not self.by_location.get(location):
                self.by_location[location] = set()
            inst.location = location
            self.by_location[location].add(inst)

        return_text = []
        if old_container or new_container or hasattr(inst, "contained_in"):
            #print(f"old_container: {old_container} // new_container: {new_container}")
            #updated = self.clear_parent_and_old_loc(inst, old_container, new_container, location, old_loc, updated)
            parent, was_in_container, new_container = self.get_parent_details(inst, old_container, new_container)
            if parent and was_in_container:
                return_text.append((f"Item `[{inst}]` removed from old container `[{parent}]`", inst, parent))
                if not no_print:
                    print(f"You remove the {assign_colour(inst)} from the {assign_colour(parent)}.\n")

            if new_container:
                new_container.children.add(inst) # Added this, it wasn't adding items as children to containers.
                inst.contained_in = new_container
                updated.add(new_container)

                return_text.append((f"Added [{inst}] to new container [{new_container}]", inst, new_container))
                if not no_print:
                    print(f"Added {assign_colour(inst)} to {assign_colour(new_container)}.")
                print(f"Added {inst} to new container. Is it in any locations?")
                for location in registry.by_location:
                    if inst in registry.by_location[location]:
                        print(f"INST IS IN {location}")
                inst.location = loc.no_place

            else:
                inst.contained_in = None

        for item in updated:
            self.init_descriptions(item)

        if location == loc.inv_place:
            location.items.add(inst)

        from testing_coloured_descriptions import init_loc_descriptions
        init_loc_descriptions(loc.current.place, loc.current) # update even if moving to inv, so it can update the removal. Though it seemed to already...?
        return inst

    def move_from_container_to_inv(self, inst:itemInstance, parent:itemInstance=None, no_print=False) -> itemInstance:
        """Simply ensures that a suitable parent is available before sending the itemInstance and parent to `move_item`."""
        logging_fn()
        if parent == None:
            parent = inst.contained_in
        result = self.move_item(inst, location = loc.inv_place, old_container=parent, no_print=no_print)
        return result


    # -------------------------
    # Lookup
    # -------------------------
    def get_instance_from_id(self, inst_id:str)->itemInstance:
        logging_fn()
        return self.by_id.get(inst_id)


    def get_item_by_location(self, loc_cardinal:cardinalInstance=None)->set[itemInstance]:
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
            #items = set(i for i in self.instances if i.location == loc_cardinal)
            #return items
            items_at_cardinal = self.by_location.get(loc_cardinal)
            if items_at_cardinal:
                items = set(i for i in items_at_cardinal) # so adding to it in local_items doesn't add to the actual by_location entry
                return items


    def instances_by_name(self, definition_key:str)->set:
        logging_fn()

        if not isinstance(definition_key, str):
            if isinstance(definition_key, list):
                definition_key = definition_key[0]

        if self.by_name.get(definition_key):
            return self.by_name.get(definition_key)

        elif self.by_alt_names.get(definition_key): # why does alt_names not store the instance directly?
            if isinstance(self.by_alt_names[definition_key], str):
                return self.by_name.get(self.by_alt_names.get(definition_key))

            return set((self.by_alt_names[definition_key],)) # allows for npcInstances without having to add them to itemReg directly.

    def instances_by_container(self, container:itemInstance)->list:
        logging_fn()
        return [i for i in self.by_container.get(container, list())]


    def instances_by_category(self, category:str):
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

    def describe(self, inst: itemInstance, caps:bool=False)->str:
        logging_fn()
        if not hasattr(inst, "description"):
            return "You see nothing special."

        registry.init_descriptions(inst)
        description = inst.description

        #print(f"inst: {inst} // description: {description}")
        if caps:
            from misc_utilities import smart_capitalise
            description = smart_capitalise(description)

        if "[[]]" in description:
            description = description.replace("[[]]", f"{inst.print_name}")
        if description:
            #print(f"description in describe: {description}")
            return description


    def init_descriptions(self, inst: itemInstance):
        """Generate or update itemInstance descriptions, as well as nicenames, based on container/child status, plural cluster instances, item state, etc."""
        logging_fn()
        from misc_utilities import has_and_true
        description = None
        starting_children_only = False

        if self.by_alt_names.get(inst.name) and (not hasattr(inst, "descriptions") or not inst.descriptions):
            inst.descriptions = self.item_defs.get(self.by_alt_names.get(inst.name)).get("descriptions")

        if not inst.descriptions and inst.description:
            print(f"Not inst.descriptions. inst.description: {inst.description}")
            return
        #if not hasattr(inst, "nicenames"):
        #    inst.nicenames = {} # need to properly update nicenames here, not just instances.

        if inst.descriptions:
            from npcRegistry import npcInstance
            if isinstance(inst, npcInstance) and not inst.encountered:
                description = inst.descriptions.get("npc_introduction")
            else:
                for entry, val in inst.descriptions.items():
                    if val and isinstance(val, str) and "[[choose" in val:
                        from misc_utilities import choose_option
                        inst.descriptions[entry] = choose_option(val, inst)

                    if entry == "details":
                        for detail in inst.descriptions[entry]:
                            val = inst.descriptions[entry][detail]
                            if val and isinstance(val, str) and "[[choose" in val:
                                from misc_utilities import choose_option
                                inst.descriptions[entry][detail] = choose_option(val, inst)
                    #if val and val != "":
                        #description = inst.descriptions[entry]

            if not description and not inst.descriptions.get("generic"):
                a_or_an = "a" if not inst.name.lower().startswith("a") else "an"
                description = f"It's {a_or_an} {inst.name}."
                inst.descriptions["generic"] = description

        def get_if_open(inst:itemInstance, label:str, do_not_add_children_to_description=False) ->str:
            description = None
            if has_and_true(inst, "is_open"):
                description = inst.descriptions.get(f"open_{label}")
                if not description and label != "no_children":
                    if not do_not_add_children_to_description:
                        description = f"A {inst.name}, containing "
                    else:
                        description = f"A {inst.name}."
            else:
                description = inst.descriptions.get(label)
            if description and description != "":
                return description
            #if has_and_true(inst, label): # how would this work? Containers don't have 'item.starting_children_only' attr...
                #getattr(inst.descriptions, f"open_{label}")
                    #description = getattr(inst.descriptions, f"open_{label}")
                #else:
                    #description = getattr(inst.descriptions, label)

        if "container" in inst.item_type and not "electronics" in inst.item_type:
            if inst.print_children_as_list:
                do_not_add_children_to_description = True
            else:
                do_not_add_children_to_description = False
            if has_and_true(inst, "children") and inst.children:
                test = None
                if has_and_true(inst, "starting_children"):
                    starting_children_only = True
                    for child in inst.children:
                        if not child in inst.starting_children or has_and_true(child, "hidden"):
                            starting_children_only = False
                    if len(inst.starting_children) > len(inst.children):
                        starting_children_only = False
                    if starting_children_only:
                        test = get_if_open(inst, "starting_children_only", do_not_add_children_to_description)
                        if test:
                            description = test
                if not test:
                    long_desc = []
                    from testing_coloured_descriptions import compile_long_desc
                    from misc_utilities import assign_colour
                    if_open = get_if_open(inst, "any_children", do_not_add_children_to_description)
                    if if_open and not do_not_add_children_to_description:
                        long_desc.append(get_if_open(inst, "any_children"))
                        testing = True
                        if testing:#not ((hasattr(inst, "print_children_as_list") and inst.print_children_as_list) or not hasattr(inst, "print_children_as_list")):
                            for child in inst.children:
                                long_desc.append(assign_colour(child, nicename=True))
                                #print(f"long_desc with child: {long_desc}")
                        description = compile_long_desc(long_desc)
                    if inst.nicenames.get("any_children"):
                        inst.nicename = inst.nicenames.get("any_children")

            else:
                if not has_and_true(inst, "children") and get_if_open(inst, "no_children"):
                    description = get_if_open(inst, "no_children")
                if inst.nicenames.get("no_children"):
                    inst.nicename = inst.nicenames.get("no_children")
        #print(f"{inst.name}: Description after child check etc: {description}")

        if "electronics" in inst.item_type:
            if inst.is_charged:
                if inst.is_locked:
                    if inst.descriptions.get("is_locked") and inst.descriptions["is_locked"] != "":
                            description = inst.descriptions["is_locked"]
                elif inst.descriptions.get("is_charged") and inst.descriptions["is_charged"] != "":
                    description = inst.descriptions["is_charged"]

            elif inst.descriptions.get("has_batteries") and hasattr(inst, "has_batteries") and inst.has_batteries:
                    description = inst.descriptions["has_batteries"]

        if not description:
            if not hasattr(inst, "descriptions") or not inst.descriptions:
                inst.descriptions = {}
                inst.descriptions["generic"] = f"It's a {inst.name}"
                description = inst.descriptions["generic"]

            elif has_and_true(inst, "is_broken") and inst.descriptions.get("is_broken"):
                description = inst.descriptions["is_broken"]

            elif has_and_true(inst, "is_burned") and inst.descriptions.get("is_burned"):
                description = inst.descriptions["is_burned"]

            elif has_and_true(inst, "is_open") and inst.descriptions.get("is_open"):
                description = inst.descriptions["is_open"]

            elif inst.descriptions.get("is_singular") and inst.has_multiple_instances == 1:
                description = inst.descriptions["is_singular"]
            elif inst.descriptions.get("is_plural") and inst.has_multiple_instances > 1:
                description = inst.descriptions["is_plural"]

            elif inst.descriptions.get("generic"):
                description = inst.descriptions["generic"]
                #inst.description = description # only update inst at the end

        if inst.descriptions.get("from_inside") and hasattr(inst, "int_location") and loc.by_cardinal_str(inst.int_location) == loc.current:
            description = inst.descriptions["from_inside"]
        ## Update nicenames ##
        if hasattr(inst, "has_multiple_instances"):
            if inst.nicenames.get("is_singular") and inst.has_multiple_instances == 1:
                inst.nicename = inst.nicenames["is_singular"]
            if inst.nicenames.get("is_plural") and inst.has_multiple_instances > 1:
                inst.nicename = inst.nicenames["is_plural"]

        if description:
            if "[[choose" in description:
                from misc_utilities import choose_option
                description = choose_option(description, inst)

            inst.description = description

    """def get_duplicate_details(self, inst, inventory_list):
        logging_fn()

        if isinstance(inst, itemInstance):
            items = self.instances_by_name(inst.name)
        else:
            items = self.instances_by_name(inst)

        if items:
            dupe_list = []
            for thing in inventory_list:
                if thing in items:
                    dupe_list.append(thing)

            return dupe_list
        print(f"{inst} not found in instances by name. {type(inst)}")"""

    def register_name_colour(self, inst:itemInstance, colour:str)->str:
        """Assigns `colour` to `inst`, and returns `inst.print_name`."""
        logging_fn()

        inst.colour=colour

        return inst.print_name

    """def pick_up(self, inst:str|itemInstance, location=None, starting_objects=False) -> tuple[itemInstance, list]:
        Remnant of an old script. Will be replaced with a separate generation for starting items.
        logging_fn()

        item_name = None
        if isinstance(inst, str):
            item_name = inst

        elif isinstance(inst, set) or isinstance(inst, list):
            print("THIS SHOULD NEVER HAPPEN. DEF PICK_UP SHOULD ONLY EVER GET AN INSTANCE.")
            inst = next(iter(inst), None)

        if location == None:
            location = loc.current

        if not isinstance(inst, itemInstance):
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
        if isinstance(new_inst, itemInstance) and new_inst != inst:
            print(f"Picked up {new_inst} instead of {inst}.")
            inst = new_inst
        return inst"""

    """def drop(self, inst: itemInstance):
         Replace this with a direct link to {self.move_item(inst, location = loc.current)} instead.
        logging_fn()

        if self.move_item(inst, location = loc.current):
            return inst"""


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


def new_item_from_str(item_name:str, input_str:str=None, loc_cardinal:cardinalInstance|str=None, partial_dict:dict=None, in_container=None)->str|itemInstance:
    """Generates an item def entry from item_name and, if given, input_str an a partial dict. Input_str should be a list of item_type categories to be assigned to the item. If loc_cardinal is None, items will be generated in a default location.\n\n`init_single` will be run with this new item def."""

    if partial_dict:
        if partial_dict.get(item_name):
            partial_dict = partial_dict[item_name]
        if partial_dict.get("item_type"):
            input_str = partial_dict["item_type"]

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
        if isinstance(input_str, list):
            input_str = " ".join(input_str)
        else:
            print(f"new_item_from_str requires a string input, not {type(input_str)}: {input_str}")
            return

    if " " in input_str.strip():
        input_str = input_str.replace(",", "")
        parts = input_str.strip().split(" ")
        parts = list(i for i in parts if i != None and i in list(type_defaults))
        #print(f"PARTS: {parts}, type: {type(parts)}")
        if len(parts) > 1:
            #print(f"Parts len >1 : {parts}, type: {type(parts)}")
            new_str = list(parts)
        else:
            new_str = list([parts])

    elif input_str in type_defaults:
        print(f"Input str in type_defaults: {input_str}, type: {type(input_str)}")
        new_str = list([input_str])

    else:
        print(f"No valid input [`{input_str}`]. Defaulting to item_type = ['static']")
        new_str = list(["static"])

    if not loc_cardinal:
        loc_cardinal = "graveyard north"

    if partial_dict and isinstance(partial_dict, dict):
        #print("elif partial_dict.get('name'): Not sure this'll work any more now I've renamed it to 'nicename'.")
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

    registry.item_defs[item_name] = new_item_dict
    inst = registry.init_single(item_name, new_item_dict)
    all_item_names_generated.append((inst, "new_item_from_str"))
    registry.temp_items.add(inst)

    print(f"inst: {inst} / inst.location: {inst.location}")

    if in_container:
        setattr(inst, "in_container", in_container)
        inst.location = loc.no_place
        in_container.children.add(inst)
    #if registry.temp_items:
    #    from edit_item_defs import add_new_item
    #    add_new_item(item_name, new_item_dict)

    #print(f"\nend of new_item_from_str for {inst}")
    #printing.print_green(text=vars(inst), bg=False, invert=True)
    return inst

def apply_loc_data_to_item(item, item_data, loc_data):
    """For generating items named in `loc_data` entries, and applying those location-specific attributes/values/traits on top of the general item data from item_defs to generate a new itemInstance in `init_single`."""
    if loc_data and isinstance(loc_data, dict):
        for field in loc_data:
            if field == item:
                for attr in loc_data[field]:
                    if attr == "descriptions":
                        continue
                    if attr == item:
                        continue
                    else:
                        item_data[attr] = loc_data[field][attr] #Turning this off breaks int_location. not sure how it makes it stay a string whhen it's a string in loc_dict too... I don't understand.
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

    if loc_data and loc_data.get("generate_multiples"): # not cluster objects, just multiple instances of the same archetype in one location.
        #print(f"Need to make multiple of this: {item}: {item_data['generate_multiples']}")
        for _ in range(1, item_data['generate_multiples']):
            #print(f"Number in range: {number}")
            inst = registry.init_single(item, item_data)

    all_item_names_generated.append((inst, "apply_loc_data_to_item"))

    #if hasattr(inst, "requires_key") and getattr(inst, "requires_key"): # TODO remove this bit once tested
        #if not hasattr(registry, "requires_key"):
            #registry.requires_key = []
        #registry.requires_key.append(inst) # requires_key isn't used, I think.
    return inst


def init_loc_items(place=None, cardinal=None):
    """Initialises all items in `loc_data` if no place/cardinal are provided. If place/cardinal are provided, only initalises those specific locations.\nAfter initialisation, runs `registry.clean_relationships`"""
    from item_dict_gen import generator, excluded_itemnames
    from env_data import locRegistry

    registry.alt_names = generator.alt_names
    loc_dict = locRegistry.loc_data
    loc_items_dict = {}

    if config.parse_test:
        everything_entry = loc_dict["everything"]
        everything_entry["north"]["items"] = list(registry.item_defs)
        north_everything = loc.by_cardinal_str("north everything")

    def add_floors_walls():

        flooring = "floor"
        wall = "wall"
        from interactions.player_movement import get_viable_cardinal
        for place in loc.places:
            for card in place.cardinals:
                if card == loc.no_place or card == loc.inv_place:
                    continue
                test_cardinal, success = get_viable_cardinal(card, place=place)
                if success:
                    if registry.get_item_by_location(test_cardinal):
                        for item in registry.get_item_by_location(test_cardinal):
                            if "flooring" in item.item_type: # in case I've added an actual piece of scenery, like the wall on the outside of the shed.
                                test_cardinal.surfaces["flooring"] = item
                                continue
                    test_cardinal.surfaces = loc_dict[place.name][card].get("surfaces") if loc_dict[place.name][card].get("surfaces") else {"flooring": set(), "walls": set()}
                    if test_cardinal.surfaces.get("flooring"):
                        if isinstance(test_cardinal.surfaces["flooring"], str):
                            flooring = test_cardinal.surfaces["flooring"]
                        elif test_cardinal.surfaces["flooring"] == False:
                            flooring = None
                        else:
                            flooring = "floor"
                    else:
                        flooring = "none_given"

                    if flooring:
                        if flooring in ("floor", "none_given"):
                            if place.placewide_surfaces and place.placewide_surfaces.get("flooring"):
                                flooring = place.placewide_surfaces["flooring"]
                            if flooring == "none_given":
                                continue # if none given and no global, do nothing.
                        inst = registry.init_single(flooring, apply_location=False)
                        all_item_names_generated.append((inst, "init_loc_items flooring"))
                        if hasattr(inst, "location") and inst.location != loc.no_place:
                            registry.by_location.get(inst.location).pop(inst) # These scenery items shouldn't show up as local objects. We don't find the wall when looking around, it's just /there/. Not sure if this is how I want to keep doing it but it'll do for now. Maybe not even no_place but just 'None', will see.
                        inst.location = test_cardinal
                        #TODO: Set this up for walls too.
                        setattr(inst, "is_scenery", True) # not implemented anywhere yet.
                        test_cardinal.surfaces["flooring"] = inst
# TODO do the same for walls.

    def get_cardinal_items(place, cardinal):
        name_to_inst_tmp = {}

        def from_single_cardinal(place, cardinal, name_to_inst_tmp):

            if isinstance(place, placeInstance):
                place = place.name
            if isinstance(cardinal, cardinalInstance):
                cardinal = cardinal.name

            if not loc_dict.get(place.lower()):
                return name_to_inst_tmp

            def create_base_items(place=None, cardinal=None, loc_data:dict={}):
                matched = {}

                if place == None:
                    place = loc.currentPlace
                if cardinal == None:
                    cardinal = loc.current # why get card_inst separately when it'll just output immediately anyway.
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
                        # turning this off, because I already do that in item_dict_gen. I shouldn't be doing it again, surely.

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

    add_floors_walls()

    registry.clean_relationships()


def initialise_itemRegistry():
    """Initialises itemRegistry, generates all registry.by_location places and cardinals, initialises the item_dict from item_dict_gen (template item defs without instance/location data). Then generates all loc_data items in `init_loc_items`, and creates the plural words dict and assigns transitional objects."""
    from item_dict_gen import init_item_dict, generator
    registry.by_location = generator.by_location # if an item has no locations, is not in this dict?

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

    registry.plural_words = plural_word_dict

    """for obj in registry.instances: # should be able to delete this entirely now.
        if hasattr(obj, "is_loc_exterior"):
            location = loc.place_by_name(obj.name)
            if hasattr(location, "transition_objs") and location.transition_objs:
                if not hasattr(obj, "transition_objs") or not isinstance(obj.transition_objs, set):
                    obj.transition_objs = set()
                for item in location.transition_objs:
                    obj.transition_objs.add(item)"""
    return

if __name__ == "__main__":

    from env_data import initialise_placeRegistry
    initialise_placeRegistry()
    initialise_itemRegistry()
