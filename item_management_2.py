
import uuid


def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


class ItemInstance:
    """
    Represents a single item in the game world or player inventory.
    """
# definition_key, nicename, description, location, contained_in, item_size, primary_category, container_data)
    def __init__(self, definition_key, container_data, item_size, attr, counter):

        self.id = str(uuid.uuid4())  # unique per instance
        self.name = definition_key
        self.count_val = counter ## just for setup for matching the children to parents. Probably silly.
        self.nicename=attr["name"]
        self.description = attr["description"]
        self.starting_location = attr.get("starting_location")  # not used. Need to implement as the 'was originally encountered here' usecase.   # dict (game.place: cardinal) or None
        self.location = (attr.get("starting_location") if attr.get("starting_location") != None and not attr.get("contained_in") else None)  # starting location or None -- always none if 'contained_in'.
        self.colour = None

### FLAGS ###
 #     INITIAL FLAG MANAGEMENT

        self.flags = attr["flags"]      # any runtime flags (open/locked/etc)

        if "can_pick_up" in self.flags:
            self.can_pick_up=True
            self.item_size=item_size
            self.started_contained_in = attr.get("contained_in")  # parent instance id if inside a container
            if self.started_contained_in:
                self.contained_in=self.started_contained_in
        else:
            self.can_pick_up=False

        if "can_open" in self.flags:
            if "starts_open" in self.flags: # currently nothing uses this, but here to allow for it later.
                self.is_open = True
            else:
                self.is_open = False

        if "can_lock" in self.flags:
            if not "is_unlocked" in self.flags: # like 'starts_open', currently not used but here for later.
                self.is_locked = True
            else:
                self.is_locked = False
            self.needs_key = attr.get("key")

        if "can_be_charged" in self.flags:
            if "is_charged" in self.flags:
                self.is_charged == True
            else:
                self.is_charged == False

        if "print_on_investigate" in attr:
            self.description_detailed = attr.get("print_on_investigate")

###

        if container_data:
            description_no_children, name_children_removed, container_limits, starting_children = container_data
            self.description_no_children = description_no_children
            self.name_children_removed=name_children_removed
            self.container_limits=container_limits
            if starting_children:
                children_w_counter=[]
                for child in starting_children:
                    children_w_counter.append((child, counter))

            self.starting_children = starting_children ### This just adds the string name, not the id like it needs to.
            self.children = (list()) ## Maybe we create all instances first, then add 'children' afterwards, otherwise they won't be initialised yet.


    def __repr__(self):
        return f"<ItemInstance {self.name} ({self.id})>"


class LootRegistry:
    """
    Central manager for all item instances.
    Also keeps a location-indexed lookup for fast "what's here?" queries.
    """

    def __init__(self):
        self.instances = {}      # id -> ItemInstance
        self.by_location = {}    # (place, direction) -> set of instance IDs
        self.by_name = {}        # definition_key -> set of instance IDs
        self.by_category = {}        # category (loot value) -> set of instance IDs
        self.by_container = {}
        self.by_counter = {}
        self.inst_to_names_dict = {}
        self.is_container = True
    # -------------------------
    # Creation / deletion
    # -------------------------

    def create_instance(self, definition_key, attr, counter=None):

#### ALL ATTRS + FLAGS IN ALL CURRENT ITEMS:
#   all attr flags: {'flags', 'name', 'description', 'container_limits', 'description_no_children', 'name_children_removed', 'item_size', 'starting_children', 'special_traits', 'started_contained_in', 'starting_location', 'loot_type'}

#   Flag items: {'can_pick_up', 'dirty', 'fragile', 'dupe', 'flammable', 'locked', 'weird', 'container', 'can_read', 'can_open'}

        if "container" in attr["flags"]:
            container_data = (attr.get("description_no_children"), attr.get("name_children_removed"), attr.get("container_limits"), attr.get("starting_children"))
        else:
            container_data=None

        if "starting_location" in attr:
            primary_category="starting_location"
        else:
            primary_category="loot_type"

        location = attr.get("starting_location")

        inst = ItemInstance(definition_key, container_data, attr.get("item_size"), attr, counter)#nicename, primary_category, is_container, can_pick_up, description, location, contained_in, item_size, container_data)
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
        # if item starts inside container
        if attr.get("started_contained_in"):
            self.by_counter = {counter:inst} # just need to strip the counter thing, it never helped.

            parent_name =attr.get("started_contained_in")
            parent_obj_list = self.by_name.get(parent_name)#instances_by_name(self, parent)
            if parent_obj_list:
                if len(parent_obj_list)==1:
                    for prospective_parent in parent_obj_list:
                        #print(f"pros_parent_obj: {prospective_parent}")
                        #pros_parent_obj=self.instances.get(prospective_parent)
                        pros_children = prospective_parent.starting_children
                        if inst.name in pros_children:
                            inst.contained_in = prospective_parent
                            self.by_container[prospective_parent].add(inst) ## idk if this'll work.
                            #for child in pros_children:
                                #if child ==
                        #if child.id == inst.id:
                            #print(f"prospective parent: {prospective_parent}, type: {type(prospective_parent)} ")
                            #print(f"pros_parent_obj.id: {pros_parent_obj.id}")
                            #print(f"Added {inst.id} to parent {prospective_parent}: {self.by_container[prospective_parent]}")

### This section needs work. It's partially done but needs a rework.

                    #parent_inst=next(iter(parent_obj_list))
                    #print(f"Parent id (next): {parent_id}, type: {type(parent_id)}")
                    #inst.contained_in = parent_inst
                    #self.by_container[parent_inst].add(inst) ## idk if this'll work.
                    #print(f"Added {inst} to parent {pros_parent_obj}: {self.by_container[pros_parent_obj]}")
                else:
                    for prospective_parent in parent_obj_list:
                        #print("Prospective parent:  ", prospective_parent)
                        pros_parent_obj=self.instances.get(prospective_parent.id)
                        pros_children = pros_parent_obj.starting_children

### TODO: NEED TO DO SOMETHING HERE.

                        #if pros_children:
                        #    for child in pros_children:
                        #        print(child)

                        #self.by_container[parent_id]
                    #print(f"Child `{inst}` does not have a parent object (expecting {parent_name})")

            #print(f"Container obj: {pros_parent_obj}")
            #print(f" After adding children to containers:  ", self.by_container[pros_parent_obj])

        #print("FULL by_container:", registry.by_container)

        # Index by location ## Do this at the end, so can check container status - if in a container, don't add it to the location. Let it be in the container exclusively.
        if location:
            if not hasattr(inst, "contained_in"):
            #if not inst.contained_in: # should only exclude things currently in containers.
                location, cardinal = next(iter(location.items()))
                self.by_location.setdefault(location, {}).setdefault(cardinal, set()).add(inst)

        # Index by name
        self.by_name.setdefault(definition_key, list()).append(inst)

        return inst

    def update_containers(self, item_name, attr, counter2):
        #child_inst = self.instance_by_counter(counter2)

        # if item starts inside container
        if attr.get("started_contained_in"):
            child_inst = self.by_counter[counter2]
            parent_name =attr.get("started_contained_in")
            #print(f"Parent name: {parent_name}")
            parent_obj_list = self.by_name.get(parent_name)#instances_by_name(self, parent)
            if parent_obj_list:
                if len(parent_obj_list)==1:
                    for prospective_parent in parent_obj_list:
                        pros_parent_obj=self.instances.get(prospective_parent)

                        #print(f"pros parent obj: {pros_parent_obj}")
                        #print(f"pros parent obj id: {pros_parent_obj.id}, type: {type(pros_parent_obj.id)}")
                        #pros_children = pros_parent_obj.starting_children
                        if pros_children:
                            #print(f"Pros children: {pros_children}")
                            for child in pros_children:
                                #print("Child: ", child)
                                #if child.id == inst.id:
                                child_inst.contained_in = pros_parent_obj
                                container_list = self.instances_by_container(pros_parent_obj) ## idk if this'll work.
                                #print(f"container list: {container_list}, type: {type(container_list)}")
                                container_list.add(child.inst)

                                #print(f"Added {child_inst.id} to parent: {self.instances_by_container([container_list[0].id])}")

                    parent=next(iter(parent_obj_list))
                    #print(f"Parent obj list: {parent_obj_list}")
                    #print(f"parent_id: {parent_id}")
                    #self.instance_by_counter(parent_id)
                    #self.instance_by_container(parent_id)
                else:
                    for prospective_parent in parent_obj_list:
                        pros_parent_obj=self.instances.get(prospective_parent) ## changed these from obj.id to just  obj to match the others. This is largely untested
                        pros_children = pros_parent_obj.starting_children ## starting children is probably just strings at this point... currently I allow for it making one child obj, but not more t han that. Not sufficient...
                        if len(pros_children)==1:
                            if item_name in pros_children:
                                self.by_container[parent].add(child_inst) ## idk if this'll work.
                                #print(f"Added {child_inst.id} to parent: {self.by_container[parent_id]}")
            #else:
                        #self.by_container[parent_id]
                #print(f"Child `{child_inst.id}` does not have a parent object (expecting {parent_name})")



    def delete_instance(self, inst: ItemInstance):
        inst_id=inst.id
        inst = self.instances.pop(inst_id, None)
        if not inst:
            return

        # remove from location index
        if inst.location and inst.location in self.by_location:
            self.by_location[inst.location].discard(inst)
            if not self.by_location[inst.location]:
                del self.by_location[inst.location]

        # remove from name index
        self.by_name.get(inst.definition_key, set()).discard(inst)

    # -------------------------
    # Movement
    # -------------------------
    def move_item(self, inst:ItemInstance, place=None, direction=None, new_container=None, old_container=None):
        #children = None
        #if self.instances_by_container(inst):
        #    children = self.instances_by_container(inst)

        ## REMOVE FROM ORIGINAL LOCATION ##

        old_loc = inst.location
        if old_loc:
            location, cardinal = next(iter(old_loc.items()))
            if location in self.by_location:
                if cardinal in self.by_location.get(location):
                    #if children: ## blocking this out because there should not be children at locations once I'm done.
                    #    for child in children:
                    #        self.by_location[location][cardinal].discard(child)

                    self.by_location[location][cardinal].discard(inst)

                    if not self.by_location[location][cardinal]:
                        del self.by_location[location][cardinal]

        ## MOVE TO NEW LOCATION IF PROVIDED

        if place != None and direction != None:
            new_location = {place: direction} if place and direction else None
            inst.location = new_location

            if new_location:
                if not self.by_location.get(place):
                    temp_place = place.replace("a ", "")
                    if not self.by_location.get(temp_place):
                        print(f"Count not find location {place}, please check.")
                    else:
                        place = temp_place
                    if not self.by_location.get(place):
                        self.by_location.setdefault(place, {})#.setdefault(cardinal, set()).add(inst)
                self.by_location[place].setdefault(direction, set()).add(inst)


       #     if children and children is not None:
       #         for child in children:
       #             self.by_container[parent].remove(child)


        if old_container or new_container:
            return_text = []
            if hasattr(inst, "contained_in"): ## if a new container, remove from the old one, then add to the new.
                if old_container != None:
                    parent = old_container
                else:
                    parent = inst.contained_in
                if parent:
                    #print(f"Parent: {parent}")
                    #print(f"inst: {inst}")
                    #print("self.by_container[parent]: ", self.by_container[parent])
                # this errored during a random drop, adding the check.
                    self.by_container[parent].remove(inst)
                    inst.contained_in = None
                    return_text.append((f"Item `[child]` removed from old container `[parent]`", inst, parent))
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

        ### TODO:: Use this for location descriptions/items. Currently it's all manual, but I should be able to do a version that takes the listed items and presents them automatically.

        ## I want to add a 'picked up from'. Not implemented yet though.

    def move_from_container_to_inv(self, inst:ItemInstance, inventory:list, parent:ItemInstance=None) -> list:

        if parent == None:
            parent = inst.contained_in
        result = self.move_item(inst, old_container=parent)
        inventory.append(inst)
        return inventory, result


    # -------------------------
    # Lookup
    # -------------------------
    def get_instance_from_id(self, inst_id):
        return self.instances.get(inst_id)

    def get_item(self, inst_id): # is a dupe of the previous, but I have this all througout the existing script so may change to it and remove get_instance later. One or the other, but for the moment, both.
        return self.instances.get(inst_id)

    def instances_at(self, place, direction):

        #try:
        #    test = self.by_location[place]
#
        #except:
        #    if not self.by_category.get(place):
        #        if "a " in place:
        #            test_place = place.replace("a ", "") # the combo of these should fix all instances of a_/not a naming. If/when I add and 'an' start to a location name, will need to add 'an ' too.
        #            if self.by_category.get(test_place): ## wait why the fuck is this 'by category'? Why would a place be in a category???? How this this ever get results at all?
        #                place=test_place
        #        if not self.by_category.get(place):
        #            if self.by_category.get("a " + place):
        #                test_place = "a " + place
        #                if self.by_category.get(test_place):
        #                    place=test_place
#
        #        else:
        #            print(f"Location keys: `{self.by_location}`")
        #            if not self.by_category[place]:
        #                print(f"Location {place} has never had an item, so self.by_location fails. For now, just return.")
        #                exit()
        #                return None
        location = self.by_location.get(place)
        #print(f"location by default: location: {location}, raw place: {place}")
        if not location:
            no_a_place = place.split("a ")[1]
            #print(f"no a place: {no_a_place}")
            location = self.by_location.get(no_a_place)
            if location:
                place = no_a_place
            #print(f"location from no a place: {location}")
            if not location:
                a_place = "a " + place
                location = self.by_location.get(a_place)
                #print(f"Location with a place: {location}, a_place: {a_place}")
                if location:
                    place = a_place

        if self.by_location[place].get(direction): # check if the direction has been established yet.
            instance_list:list = [i for i in self.by_location[place].get(direction)] # if so, check if there are items there.
            if instance_list:
                return instance_list

    def instances_by_name(self, definition_key):
        return self.by_name.get(definition_key)# if self.by_name.get(definition_key) else None

    def instances_by_container(self, container):
        return [i for i in self.by_container.get(container, list())]

    def instances_by_category(self, category):
        return self.by_category.get(category, set())

    def instance_by_counter(self, counter_val):
        [self.instances[i] for i in self.by_counter[counter_val]]

    # -------------------------
    # Helpers
    # -------------------------
## From choices.py
    #def random_from(self, category: str):

    def random_from(self, selection):
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

    def describe(self, inst: ItemInstance, caps=False):

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
            description = smart_capitalise(description)

        if description:
            return description
        return "You see nothing special."

    def nicename(self, inst: ItemInstance):
        if "container" in inst.flags:
            children = self.instances_by_container(inst)
            if not children:
                print(f"no children present. name: {inst.name_children_removed}")
                return inst.name_children_removed


        if not inst:
            print("[NICENAME] No such item.")
            return None
        return inst.nicename

    def get_name(self, inst: ItemInstance):

        if not inst:
            print("[GET_NAME] No such item.")
            return None
        return inst.name



    def get_duplicate_details(self, inst, inventory_list):

        if isinstance(inst, ItemInstance):
            items = self.instances_by_name(inst.name)
        else:
            items = self.instances_by_name(inst) # gets all instances by that name (here, inst:str)

        if items:
            dupe_list = []
            for thing in inventory_list:
                if thing in items:
                    dupe_list.append(thing)

            return dupe_list
        print(f"{inst} not found in instances by name. {type(inst)}")


    def name_col(self, inst: ItemInstance, colour:str):

        #if not isinstance(inst, ItemInstance):
        inst.colour=colour
        #print(f"Assigning colour to instance: inst: {inst}, colour: {colour}, inst.colour: {inst.colour}") ## TODO: Maybe this should return the name pre-coloured. Would make sense.
        return inst.name

    def pick_up(self, inst, inventory_list, place=None, direction=None): ### could store place/direction in state

        if isinstance(inst, set) or isinstance(inst, list):
            inst=inst[0]
        #print(f"Pick_up: inst: {inst}, type: {type(inst)}")
        if not isinstance(inst, ItemInstance):
            item_list = self.instances_by_name(inst)
            inst = item_list[0] # arbitrarily pick the first one
            #print(f"pick_up id list: {item_list}")
            if not item_list:
                inst=self.get_instance_from_id(self, inst)

        if not inst:
            print("Failed to find inst in pick_up.")

        if not "can_pick_up" in inst.flags:
            return None, inventory_list

        if inst in inventory_list:
            #print("Item already in inventory. Creating new...") ## Not sure about this.
            from item_definitions import get_item_defs
            attr = get_item_defs(inst.name)
            inst = self.create_instance(inst.name, attr)

        #children = self.instances_by_container(inst) ## item just stays in the container if the container moves. Don't need any of this.
        #if children:
        #    for child in children:
        #        self.move_item(child, inst) ## adding inst here should keep it in the container.
                #inventory_list.append(child)

        self.move_item(inst) # removed place/direction, because surely if we're picking it up, it shouldn't be moved to where we are....
        inventory_list.append(inst)

        self.picked_up_from = {place:direction} # just temporarily, not in use yet. Needs formalising how it's going to work.
        return inst, inventory_list

    def get_actions_for_item(self, inst, inventory_list, has_children=None, has_multiple=None):

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
        for item in item_actions["from_flags"]:
            if item in inst.flags:
                if item == "can_read":
                    action_options.append("read") # can_read is the only one for now. There's really no need to separate contextual vs not...
                    # Also I should just have a dict that takes 'can_read' and returns 'read' etc. Eh.

        for potential_action in item_actions["contextual_actions"]:
            if potential_action in inst.flags:
                if potential_action == "can_pickup":
                    if inst not in inventory_list:
                        action_options.append("pick up")
                    else:
                        action_options.append("drop")
                elif potential_action == "can_open":
                    if potential_action.is_open: ## TODO: Add 'is_open' flag/make sure it's used when item opened/closed
                        action_options.append("close")
                    else:
                        action_options.append("open")
                elif potential_action == "can_combine":
                    requires = inst.flags["combine_with"]
                    print(f"Item {inst.name} requires: {requires}")
                    print("item management quitting.")
                    exit()
                    if requires in inventory_list:
                        action_options.append(f"combine") ## do I want to have 'combine with {requires}'? Maybe start with that and later allow 'combine x and y'. Don't want to make the decision for them. Maybe two lots of combine. A general combine option to just test things out, and a second one for prescribed combinations (eg dvd player + dvd)
                elif potential_action == "flammable":
                    from set_up_game import game
                    if game.has_fire: # true if have matches or if near fire (which is why I'm not just using the inventory to check for matches etc)
                        action_options.append("set alight")

            #self.needs_key = attr.get("key")
                elif potential_action == "can_lock":
                    if inst.is_locked: ## TODO: add 'unlocked' state to anything that can be locked. Need explicit active flag management.
                        lock_action = "unlock"
                    else:
                        lock_action = "lock"
                    key = inst.flags["key"]
                    if key in inventory_list:
                        action_options.append(lock_action)
                    else:
                        print("Locked but no key. Need to figure out how to deal w this. Maybe a few options depending on the item. If it has an obvious lock vs not etc.")
                elif potential_action == "can_be_charged":
                    if "is_charged" not in inst.flags:
                        inst.is_charged = False
                    else:
                        inst.is_charged = True

                    if not inst.is_charged:
                        charger = inst.flags["charger"]
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

        return action_options



    def drop(self, inst: ItemInstance, location, direction, inventory_list):
        if inst not in inventory_list:
            return None, inventory_list
        inventory_list.remove(inst)
        self.move_item(inst, place=location, direction=direction)
        return inst, inventory_list


# setup
registry = LootRegistry()
inventory = []

## create some items
#vase_def = {
#    "name": "glass jar with flowers",
#    "description": "A glass jar holding dried flowers.",
#    "starting_children": ["flowers_001"],
#    "flags": ["CONTAINER", "CAN_PICKUP"]
#}
#vase = registry.create_instance("glass_jar", vase_def, location=("graveyard", "east"))
#
## create location object
#graveyard_east = Location("graveyard_east")
#graveyard_east.add_item(vase.id)
#
## pick up
#registry.pick_up(vase.id, inventory) ## Thinking of holding the player inventory here, and getting it from here when needed, instead of holding it in the main game class.
#graveyard_east.remove_item(vase.id)
#
## drop
#registry.drop(vase.id, ("graveyard", "east"), inventory)
#graveyard_east.add_item(vase.id)
#
## look around
#for inst in registry.instances_at("graveyard", "east"):
#    print(f"You see {inst.definition_key} at the location.")
#
#
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


def initialise_registry():
    from item_definitions import get_item_defs
    counter=0
    for item_name, attr in get_item_defs().items():
        registry.create_instance(item_name, attr, counter)
        counter+=1


if __name__ == "__main__":

    initialise_registry()

