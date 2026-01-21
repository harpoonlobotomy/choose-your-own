
from time import sleep
import uuid

from env_data import cardinalInstance, placeInstance
from logger import logging_fn, traceback_fn
from env_data import locRegistry as loc

print("Item registry is being run right now.")
#sleep(.5)


class ItemInstance:
    """
    Represents a single item in the game world or player inventory.
    """

    def __init__(self, definition_key:str, attr:dict):
        print(f"definition_key: {definition_key}, attr: {attr}")
        #print(f"Init in item instance is running now. {definition_key}")
        self.id = str(uuid.uuid4())  # unique per instance
        self.name:str = definition_key
        self.nicename:str = attr.get("name")
        print(f"ATTR: {attr}")
        self.item_type = attr["item_type"] ## have it here and/or in the registry. I guess both? covers the 'is_container' thing neatly enough.
        self.colour = None
        self.description:str = attr.get("description")
        self.starting_location:dict = attr.get("starting_location") # currently is styr
        self.verb_actions = set()
        self.contained_in = None
        self.location:cardinalInstance = None

        if attr.get("alt_names"):
            self.alt_names = set(i for i in attr.get("alt_names"))
        else:
            self.alt_names = None

 #     INITIAL FLAG MANAGEMENT

        for attribute in ("can_pick_up", "can_be_opened", "print_on_investigate", "can_be_locked"):
            if hasattr(self, attribute):
                    self.verb_actions.add(attribute)
        #    self.started_contained_in = attr.get("contained_in")  # parent instance id if inside a container
        #    if self.started_contained_in:
        #        self.contained_in = self.started_contained_in ## do this later like testclass does
        #else:
        #    self.can_pick_up=False

            #self.needs_key = attr.get("key")
#
            #if "needs_key_to_lock" in self.flags:
            #    self.needs_key_to_lock = (attr.get("key") if attr.get("key") else True)

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
             ### This just adds the string name, not the id like it needs to.
            #self.children = list() ## Maybe we create all instances first, then add 'children' afterwards, otherwise they won't be initialised yet. Currently this works because I've listed the parents first in the item defs.

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

    # -------------------------
    # Creation / deletion
    # -------------------------

    def init_single(self, item_name, item_entry): ## Will replace create_instance directly.
        print(f"[init_single] ITEM NAME: {item_name}")
        print(f"[init_single] ITEM ENTRY: {item_entry}")
        inst = ItemInstance(item_name, item_entry)
        self.instances.add(inst)
        self.by_name[inst.name] = inst
        self.by_id[inst.id] = inst

        return inst

    def create_instance(self, definition_key, attr):
        logging_fn()



#        if "starting_location" in attr:
#            primary_category="starting_location"
#        else:
#            primary_category="loot_type"


        inst = ItemInstance(definition_key, attr)#nicename, primary_category, is_container, can_pick_up, description, location, contained_in, item_size, container_data)

        self.instances.add(inst)
        self.by_id[inst.id] = inst

        loot_type = attr.get("loot_type")

        if loot_type: # Works with multiple categories now. So, starting loot also has a value. Currently it's always added, it doesn't remove something from the pool just because it was in the starting loot. May need to reevaluate, but functions okay for now.

            if isinstance(loot_type, list):
                for option in loot_type:
                    self.by_category.setdefault(option, set()).add(inst)
            else:
                self.by_category.setdefault(loot_type, set()).add(inst)

        #if attr.get("started_contained_in"):
#
        #    parent_name =attr.get("started_contained_in")
        #    parent_obj_list = self.instances_by_name(parent_name) # TODO: I've cut a lot of the comments from this section. Still needs a rework though.
        #    if parent_obj_list:
        #        for prospective_parent in parent_obj_list:
        #            #print(f"Prospective parent: {prospective_parent}")
        #            pros_children = prospective_parent.starting_children
        #            if inst.name in pros_children:
        #                if not inst in self.instances_by_container(prospective_parent):
        #                    inst.contained_in = prospective_parent
        #                    self.by_container[prospective_parent].add(inst)
        #                else:
        #                    continue # if already there, try another prospective parent. Don't know if this'll work on not yet.


        # Index by location ## Do this at the end, so can check container status - if in a container, don't add it to the location. Let it be in the container exclusively.
        location = attr.get("starting_location")

        if location:
            if not hasattr(inst, "contained_in") or inst.contained_in == None:
                #print(f"Item {inst.name} has a location.")
                from env_data import locRegistry as loc
                cardinal_inst = loc.by_cardinal_str(location)
                #print(f"CARDINAL INST IF LOCATION: {cardinal_inst}, {cardinal_inst.name}")
                self.by_location.setdefault(cardinal_inst, set()).add(inst)
                #print(f"SELF.BY_LOCATION: {self.by_location}")
                inst.location = cardinal_inst
                #print(f"self.location: {inst.location}, self.location.place_name: {inst.location.place_name}")
    ## above is wrong, need to rewrite. Too braindead today.

        # Index by name
        self.by_name.setdefault(definition_key, list()).append(inst)

        if attr.get("alt_names"):
            for altname in attr.get("alt_names"):
                self.by_alt_names[altname] = definition_key

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
        #}

        confirmed_inst = None
        confirmed_container = None
        reason_val = 7

        def run_check(inst):
            confirmed_inst = None
            confirmed_container = None
            reason = 7

            from set_up_game import game
            inventory_list = game.inventory
            local_items_list = self.get_item_by_location(loc.current)
            container, inst = is_item_in_container(inst, inventory_list)

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
                    print("No items at this location.")

            if container:
                if container in inventory_list:
                    confirmed_container = container
                    if confirmed_container:
                        if (hasattr(confirmed_container, "is_closed") and getattr(confirmed_container, "is_closed")):
                            reason = 1
                        elif (hasattr(confirmed_container, "is_locked") and getattr(confirmed_container, "is_locked")):
                            reason = 2
                        else:
                            reason = 3
                else:
                    confirmed_container = in_local_items_list(container, local_items_list)
                    if confirmed_container:
                        if hasattr(confirmed_container, "is_open") and confirmed_container.is_open == False: # only is_open exists, I think.
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
            return inst, confirmed_container, reason_val, meaning

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
                    self.by_container[parent].remove(inst)
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

        items_at_cardinal = None

        if isinstance(loc_cardinal, cardinalInstance):
            items_at_cardinal = self.by_location.get(loc_cardinal)

        if items_at_cardinal:
            return items_at_cardinal


    def instances_by_name(self, definition_key:str)->list:
        logging_fn()

        if self.by_name.get(definition_key):
            return self.by_name.get(definition_key)

        elif self.by_alt_names.get(definition_key):
            print(f"self.by_alt_names.get(definition_key): {self.by_alt_names.get(definition_key)}")
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

        if "container" in inst.flags:
            #print(f"Container in inst.flags: {inst}")
            children = self.instances_by_container(inst)
            #print(f"children: {children}")
            if not children:
                if hasattr(inst, "description_no_children") and inst.description_no_children != None:
                    description = inst.description_no_children # works now. If it's a container with no children, it prints this instead.
                # still need to make it non-binary but that can happen later. This'll do for now.

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
            else:
                inst = item_list[0]

            if not item_list:
                inst=self.get_instance_from_id(self, inst)

        if not inst:
            print("Failed to find inst in pick_up.")

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
            from item_definitions import get_item_defs
            attr = get_item_defs(inst.name)
            inst = self.create_instance(inst.name, attr)

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

#if __name__ == "__main__":

    #inventory = []

    #def get_all_flags():
    #    all_attr_flags=set()
    #    flag_items=set()
    #    from item_definitions import get_item_defs
    #    for item_name, attr in get_item_defs.items():
    #        for item_name, data in attr.items():
    #            all_attr_flags.add(item_name)
    #            if item_name == "flags":
    #                for item in data:
    #                    flag_items.add(item)
    #    print(f"all attr flags: {all_attr_flags}")
    #    print(f"Flag items: {flag_items}")
#
    #get_flags=False
    #if get_flags:
    #    get_all_flags()


def initialise_itemRegistry():

    from env_data import initialise_placeRegistry
    initialise_placeRegistry()

    import json
    json_primary = "dynamic_data/items_main.json"
    with open(json_primary, 'r') as file:
        item_defs = json.load(file)

    #from item_definitions import get_item_defs
    registry.complete_location_dict()
    plural_word_dict = {}
    #print("Running `initialise_itemRegistry`.")
    for item_name, attr in item_defs.items():
        registry.create_instance(item_name, attr)
        if len(item_name.split()) > 1:
            plural_word_dict[item_name] = tuple(item_name.split())

    registry.add_plural_words(plural_word_dict)

    print(f"Plural words: {registry.plural_words}")

initialise_itemRegistry()
