
from time import sleep
import uuid

from env_data import cardinalInstance, placeInstance
from logger import logging_fn, traceback_fn
from env_data import locRegistry as loc

print("Item registry is being run right now.")
sleep(.5)


def get_card_inst_from_strings(location):
    from env_data import locRegistry as loc
    if not isinstance(location, cardinalInstance):
        location_str, card_str = next(iter(location.items())) # strings from dict
        place = loc.place_by_name(location_str)
        cardinal_inst = loc.by_cardinal(cardinal_str=card_str, loc=place)
    else:
        cardinal_inst = location
    print(f"Cardinal_inst: {cardinal_inst}")
    print(f"Cardinal_inst.name: {cardinal_inst.name}")

    #self.by_location.setdefault(location, {}).setdefault(cardinal, set()).add(inst)
    #registry.by_location_inst[cardinal_inst] = inst
    return cardinal_inst

class ItemInstance:
    """
    Represents a single item in the game world or player inventory.
    """

    def __init__(self, definition_key:str, container_data:list, item_size:str, attr:dict):
        #print(f"Init in item instance is running now. {definition_key}")
        self.id = str(uuid.uuid4())  # unique per instance
        self.name:str = definition_key
        self.nicename:str = attr["name"]
        self.description:str = attr["description"]
        self.starting_location:dict = attr.get("starting_location")  # switching over to make this the 'discovered at' attr.
        self.colour = None
        self.verb_actions = set()
        self.in_container:bool = False
        self.in_inventory:bool = False
        self.location:cardinalInstance = None

        #if attr.get("starting_location" and attr.get("starting_location") != None and not attr.get("contained_in")):
        #    from env_data import locRegistry as loc
        #    cardinal_str, location_str = attr.get("starting_location")
        #    print(f"CARDINAL STR, location str: {cardinal_str}, {location_str}")
        #    cardinal_inst = loc.by_cardinal(cardinal_str=cardinal_str, loc=location_str)
        #    print(f"CARDINAL INST FOR STARTING LOCATION: {cardinal_inst}, {cardinal_inst.name}")
        #    self.location = cardinal_inst  # starting location or None -- always none if 'contained_in'.

        #self.location = (attr.get("starting_location") if attr.get("starting_location") != None and not attr.get("contained_in") else None)  # starting location or None -- always none if 'contained_in'.
### FLAGS ###
 #     INITIAL FLAG MANAGEMENT

        self.flags = attr["flags"]      # any runtime flags (open/locked/etc)

        if "can_pick_up" in self.flags:
            self.can_pick_up = True
            self.verb_actions.add("can_pick_up")
            self.item_size = item_size
            self.started_contained_in = attr.get("contained_in")  # parent instance id if inside a container
            if self.started_contained_in:
                self.contained_in = self.started_contained_in
            else:
                self.contained_in = None
        else:
            self.can_pick_up=False

        if "can_open" in self.flags:
            self.verb_actions.add("can_open")
            if "starts_open" in self.flags: # currently nothing uses this, but here to allow for it later.
                self.is_open = True
            else:
                self.is_open = False

        if "can_lock" in self.flags:
            self.verb_actions.add("can_lock")
            if not "is_unlocked" in self.flags: # like 'starts_open', currently not used but here for later.
                self.is_locked = True
            else:
                self.is_locked = False
            self.needs_key = attr.get("key")

        if "can_be_charged" in self.flags:
            self.verb_actions.add("can_charge")
            if "is_charged" in self.flags:
                self.is_charged = True
            else:
                self.is_charged = False

        if "print_on_investigate" in attr:
            self.verb_actions.add("print_on_investigate")
            self.description_detailed = attr.get("print_on_investigate")

###

        if container_data:
            self.verb_actions.add("is_container")
            description_no_children, name_children_removed, container_limits, starting_children = container_data
            self.description_no_children = description_no_children
            self.name_children_removed=name_children_removed
            self.container_limits=container_limits
            if starting_children:

                self.starting_children = starting_children ### This just adds the string name, not the id like it needs to.
            self.children = (list()) ## Maybe we create all instances first, then add 'children' afterwards, otherwise they won't be initialised yet. Currently this works because I've listed the parents first in the item defs.

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

        self.instances = {}      # id -> ItemInstance

        self.by_location = {}  # (cardinalInstance) -> set of instance IDs
        self.by_name = {}        # definition_key -> set of instance IDs
        self.by_category = {}        # category (loot value) -> set of instance IDs
        self.by_container = {}
        self.inst_to_names_dict = {}
        self.is_container = bool(True) ## This must be wrong. idk. I tried something else earlier and it didn't work.
        self.plural_words = {}

    # -------------------------
    # Creation / deletion
    # -------------------------

    def create_instance(self, definition_key, attr):
        logging_fn()

        if "container" in attr["flags"]:
            container_data = (attr.get("description_no_children"), attr.get("name_children_removed"), attr.get("container_limits"), attr.get("starting_children"))
        else:
            container_data=None

#        if "starting_location" in attr:
#            primary_category="starting_location"
#        else:
#            primary_category="loot_type"

        location = attr.get("starting_location")

        inst = ItemInstance(definition_key, container_data, attr.get("item_size"), attr)#nicename, primary_category, is_container, can_pick_up, description, location, contained_in, item_size, container_data)
        self.instances[inst.id] = inst
        self.attributes = attr

        loot_type = attr.get("loot_type")

        if loot_type: # Works with multiple categories now. So, starting loot also has a value. Currently it's always added, it doesn't remove something from the pool just because it was in the starting loot. May need to reevaluate, but functions okay for now.

            if isinstance(loot_type, list):
                for option in loot_type:
                    self.by_category.setdefault(option, set()).add(inst)
            else:
                self.by_category.setdefault(loot_type, set()).add(inst)

        if container_data:
            self.is_container=True
            self.by_container.setdefault(inst, set())
        else:
            self.is_container=False

        if attr.get("started_contained_in"):

            parent_name =attr.get("started_contained_in")
            parent_obj_list = self.instances_by_name(parent_name) # TODO: I've cut a lot of the comments from this section. Still needs a rework though.
            if parent_obj_list:
                for prospective_parent in parent_obj_list:
                    print(f"Prospective parent: {prospective_parent}")
                    pros_children = prospective_parent.starting_children
                    if inst.name in pros_children:
                        if not inst in self.instances_by_container(prospective_parent):
                            inst.contained_in = prospective_parent
                            self.by_container[prospective_parent].add(inst)
                            inst.in_container = True
                        else:
                            continue # if already there, try another prospective parent. Don't know if this'll work on not yet.


        # Index by location ## Do this at the end, so can check container status - if in a container, don't add it to the location. Let it be in the container exclusively.
        if location:
            if not hasattr(inst, "contained_in") or inst.contained_in == None:
                #print(f"Item {inst.name} has a location.")
                cardinal_inst = get_card_inst_from_strings(location)
                #print(f"CARDINAL INST IF LOCATION: {cardinal_inst}, {cardinal_inst.name}")
                self.by_location.setdefault(cardinal_inst, set()).add(inst)
                #print(f"SELF.BY_LOCATION: {self.by_location}")
                inst.location = cardinal_inst
                #print(f"self.location: {inst.location}, self.location.place_name: {inst.location.place_name}")
    ## above is wrong, need to rewrite. Too braindead today.

        # Index by name
        self.by_name.setdefault(definition_key, list()).append(inst)

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
        self.by_name.get(inst.definition_key, set()).discard(inst)


    def check_item_is_accessible(self, inst:ItemInstance) -> tuple[ItemInstance|None, int]:
        logging_fn()
        from misc_utilities import is_item_in_container
        # func to check that an item to be picked up is actually eligible to be picked up #
        accessible_dict = { ## just for printing, for my own sake because my memory is broken
            0: "accessible",
            1: "in container but inaccessable (locked/closed)",
            2: "in inventory",
            3: "not at current location",
            4: "other error, investigate",
            5: "in a container but accessible locally, can pick up but not drop",
            6: "in a container, accessible and in your inventory, can drop, pick up == separate"
        }

        confirmed_inst = None
        confirmed_container = None
        reason_val = 4

        def run_check(inst):
            confirmed_inst = None
            confirmed_container = None
            reason = 4

            from set_up_game import game
            inventory_list = game.inventory
            local_items_list = self.get_item_by_location(loc.current)
            container, inst = is_item_in_container(inst, inventory_list)

            if inst in inventory_list and not container:
                confirmed_inst = inst
                reason = 2
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
                        #print(f"Confirmed container: {confirmed_container}")
                        if (hasattr(confirmed_container, "is_closed") and getattr(confirmed_container, "is_closed")) or (hasattr(confirmed_container, "is_locked") and getattr(confirmed_container, "is_locked")):
                            #print(f"Container {confirmed_container} is locked.")
                            #print(f"Container.name {confirmed_container.name}")
                            reason = 1
                        else:
                            #print("confirmed container is not locked or closed")
                            reason = 6
                else:
                    confirmed_container = in_local_items_list(container, local_items_list)
                    if confirmed_container:
                        #print(f"Confirmed container locally, not in inventory: {confirmed_container}")
                        if (hasattr(confirmed_container, "is_closed") and getattr(confirmed_container, "is_closed")) or (hasattr(confirmed_container, "is_locked") and getattr(confirmed_container, "is_locked")):
                            #print(f"Container {confirmed_container} is locked.")
                            #print(f"Container.name {confirmed_container.name}")
                            reason = 1
                        else:
                            reason = 5
                    else:
                        reason = 3
            else:
                confirmed_inst = in_local_items_list(inst, local_items_list)
                if confirmed_inst:
                    reason = 0
                else:
                    if inst in inventory_list:
                        confirmed_inst = inst
                        reason = 2
                    else:
                        reason = 3

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

        #if reason_val == 0:
        #    print("REASON VAL:: Accessible item. continue with action.")
        #elif reason_val == 1:
        #    print("REASON VAL:: Item is in a container that is closed and/or locked.")
        #elif reason_val == 2:
        #    print("REASON VAL:: ITEM IS IN INVENTORY ALREADY.")
        #elif reason_val == 3:
        #    print("REASON VAL:: Item is not at the current location or on your person.")

        if confirmed_inst != None:
            return inst, confirmed_container, reason_val, meaning

        #print(f"Could not find confirmed instance for {inst}")
        return inst, confirmed_container, reason_val, meaning


    # -------------------------
    # Movement
    # -------------------------
    def move_item(self, inst:ItemInstance, location:cardinalInstance=None, new_container:ItemInstance=None, old_container:ItemInstance=None)->list:
        logging_fn()

        ## REMOVE FROM ORIGINAL LOCATION ##
        old_loc = inst.location
        #print(f"old_loc: {old_loc}")
        if old_loc and old_loc != None:
            #print(f"old_loc.palce_name: {old_loc.place_name}")
            #print(f"self.by_location: {self.by_location}")
            if self.by_location.get(old_loc):
                #print(f"self.by_location has old_loc: {self.by_location}")
                self.by_location[old_loc].discard(inst)
                #print(f"self.by_location should not have old_loc anymore: {self.by_location}")
                inst.location = None # remove location from item itself, will be added below if needed.

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

        if old_container or new_container or hasattr(inst, "contained_in"): # check if it's in a container even if I don't specify one in the fn call.
            return_text = []
            if hasattr(inst, "contained_in"): ## if a new container, remove from the old one, then add to the new.
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
                    self.by_container[new_container].add(inst)
                    return_text.append((f"Added [child] to new container [new_container]", inst, new_container))
            if return_text:
                return return_text
#        if inst.contained_in:
  #          if children and children is not None:
  #              for child in children:
  #                  self.by_container[new_container].add(child) ## Wait no. They should stay in their current container, iths the container itself being moved. So they stay in a container. It makes it recursive to potentially infinity without checks. Need to rework this but just testing as-is.
  # ## I don't know ## these all get moved separately because child items are shown separately in the location list. If this changes and you only see the contents when they're separated or being investigated, then these should no longer be moved with their parent.


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
            loc_cardinal = loc.by_cardinal(loc_cardinal)

        elif isinstance(loc_cardinal, placeInstance):
            print(f"Loc_cardinal in get_item_by_location is a Place: {loc_cardinal}")
            traceback_fn()

        items_at_cardinal = None

        if isinstance(loc_cardinal, cardinalInstance):
            items_at_cardinal = self.by_location.get(loc_cardinal)

        if items_at_cardinal:
            return items_at_cardinal


    def instances_by_name(self, definition_key:str)->list:
        logging_fn()
        if self.by_name.get(definition_key):
            return self.by_name.get(definition_key)
        #print(f"Cound not find instance for `{definition_key}` in by_name: \n{self.by_name}")

    def instances_by_container(self, container:ItemInstance)->list:
        logging_fn()
        return [i for i in self.by_container.get(container, list())]

    def instances_by_category(self, category):
        logging_fn()
        return self.by_category.get(category, set())

    # -------------------------
    # Helpers
    # -------------------------
## From choices.py
    #def random_from(self, category: str):

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

    def describe(self, inst: ItemInstance, caps=False)->str:
        logging_fn()

        description = inst.description
        if "container" in inst.flags:
            #print(f"Container in inst.flags: {inst}")
            children = self.instances_by_container(inst)
            #print(f"children: {children}")
            if not children:
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

    def get_actions_for_item(self, inst, inventory_list, has_children=None, has_multiple=None):
        logging_fn()

        inventory_list = []
        from misc_utilities import from_inventory_name
        from item_definitions import item_actions
        if isinstance(inst, ItemInstance):
            inst_name=inst
        elif isinstance(inst, str):
            instance = from_inventory_name(inventory_list, inst)
            if instance:
                inst_name = instance.name
            else:
                print(f"Inst was str but not in inventory: {inst}")
                exit()
        else:
            print(f"No usable item given for get_actions_for_item: `{inst}`, type: {type(inst)}")

        action_options = []
        for item in item_actions:
            #print(f"item: {item}")
            if not isinstance(item, str):
                item = item.name
            #print(f"item: {item}")
            if item in inst.flags:
                if item == "can_read":
                    action_options.append("read") # can_read is the only one for now. There's really no need to separate contextual vs not...
                    # Also I should just have a dict that takes 'can_read' and returns 'read' etc. Eh.
                if item == "can_pickup":
                    if inst not in inventory_list:
                        action_options.append("pick up")
                    else:
                        action_options.append("drop")
                elif item == "can_open":
                    if inst.is_open: ## TODO: Add 'is_open' flag/make sure it's used when item opened/closed
                        action_options.append("close")
                    else:
                        action_options.append("open")
                elif item == "can_combine":
                    print(f"inst.flags: {inst.flags}")
                    if "combine_with" in inst.flags:

                        requires = inst.flags["combine_with"]
                        if isinstance(requires, list):
                            print(f"item {inst.name} can combine with: {requires} (list)")
                        else:
                            print(f"Item {inst.name} requires: {requires}")
                        #print("item management quitting.")
                        #exit()
                        if requires in inventory_list:
                            action_options.append(f"combine") ## do I want to have 'combine with {requires}'? Maybe start with that and later allow 'combine x and y'. Don't want to make the decision for them. Maybe two lots of combine. A general combine option to just test things out, and a second one for prescribed combinations (eg dvd player + dvd)
                elif item == "flammable":
                    from set_up_game import game
                    if game.has_fire: # true if have matches or if near fire (which is why I'm not just using the inventory to check for matches etc)
                        action_options.append("set alight")

            #self.needs_key = attr.get("key")
                elif item == "can_lock":
                    if inst.is_locked: ## TODO: add 'unlocked' state to anything that can be locked. Need explicit active flag management.
                        lock_action = "unlock"
                    else:
                        lock_action = "lock"
                    key = inst.flags["key"]
                    if key in inventory_list:
                        action_options.append(lock_action)
                    else:
                        print("Locked but no key. Need to figure out how to deal w this. Maybe a few options depending on the item. If it has an obvious lock vs not etc.")
                elif item == "can_be_charged":
                    if "is_charged" not in inst.flags:
                        inst.flags["is_charged"] = False
                    else:
                        inst.flags["is_charged"] = True

                    if not inst.flags["is_charged"]:
                        charger = inst.flags["charger"] ## This is scrappy. Needs going over again.
                        if charger in inventory_list:
                            action_options.append(charger)

        if "pick up" not in action_options and "drop" not in action_options:
            if "loot_type" in self.attributes:
                if inst in inventory_list:
                    action_options.append("drop")
                else:
                    action_options.append("pick up")

        if "print_on_investigate" in inst.flags:
            action_options.append("investigate closer")

        children = None
        if has_children:
            children = has_children
        else:
            #print(f"has_children from sender func: {has_children}") # backup check in case the first isn't included. Streamline it later for less fallback alternatives.
            if "container" in inst.flags:
                children = self.instances_by_container(inst)

        if children:
            #print(f"children after checking inst.flags: {children}")
            for child in children:
                action_options.append(f"remove {child.name}")

        if "container" in inst.flags or children != None:
            action_options.append("add to") # just the option to add something to this container.

        action_options.append("continue")
        return action_options


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
        from misc_utilities import cardinal_cols
        for placeInstance in loc.places:
            for cardinal in loc.cardinals[placeInstance]:
                #print(f"cardinal: {cardinal}")
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
inventory = []


def get_all_flags():
    all_attr_flags=set()
    flag_items=set()
    from item_definitions import get_item_defs
    for item_name, attr in get_item_defs.items():
        for item_name, data in attr.items():
            all_attr_flags.add(item_name)
            if item_name == "flags":
                for item in data:
                    flag_items.add(item)
    print(f"all attr flags: {all_attr_flags}")
    print(f"Flag items: {flag_items}")

get_flags=False
if get_flags:
    get_all_flags()


def initialise_itemRegistry():
    from item_definitions import get_item_defs
    registry.complete_location_dict()
    plural_word_dict = {}
    #print("Running `initialise_itemRegistry`.")
    for item_name, attr in get_item_defs().items():
        registry.create_instance(item_name, attr)
        if len(item_name.split()) > 1:
            plural_word_dict[item_name] = tuple(item_name.split())

    registry.add_plural_words(plural_word_dict)

