
import uuid


def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


class ItemInstance:
    """
    Represents a single item in the game world or player inventory.
    """
# definition_key, nicename, description, location, contained_in, item_size, primary_category, container_data)
    def __init__(self, definition_key, container_data, can_pick_up, item_size, attr, counter):

        #print(f"definition key: {definition_key}, attr:")
        #print(attr)
        ##print(definition_key, nicename, primary_category, is_container, can_pick_up, description, location, contained_in, item_size, container_data)
        #if primary_category == "starting_location": # optional, use name instead of ID number for unique items. Pros and cons. Will probably cut this later.
        #    self.id = definition_key
        #else:
        self.id = str(uuid.uuid4())  # unique per instance
        self.name = definition_key
        self.count_val = counter ## just for setup for matching the children to parents. Probably silly.
        self.nicename=attr["name"]
        self.description = attr["description"]
        self.starting_location = attr.get("starting_location")     # dict (game.place: cardinal) or None
        self.location = (attr.get("starting_location") if not attr.get("contained_in") and not (attr.get("starting_location") == None)
        else None)  # starting location or None
        self.colour = None
        if can_pick_up:
            self.item_size=item_size

        self.flags = attr["flags"]      # any runtime flags (open/locked/etc)

        if can_pick_up:
            self.item_size=item_size
            self.started_contained_in = attr.get("contained_in")  # parent instance id if inside a container
            if self.started_contained_in:
                self.contained_in=self.started_contained_in

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
    # -------------------------
    # Creation / deletion
    # -------------------------

    def create_instance(self, definition_key, attr, counter=None):#nicename, primary_category, is_container, can_pick_up, description, location, contained_in, item_size, container_data):


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

        if "can_pick_up" in attr["flags"]:
            can_pick_up=True
        else:
            can_pick_up=False

        location = attr.get("starting_location")

        inst = ItemInstance(definition_key, container_data, can_pick_up, attr.get("item_size"), attr, counter)#nicename, primary_category, is_container, can_pick_up, description, location, contained_in, item_size, container_data)
        self.instances[inst.id] = inst

        # Index by location
        if location:
            location, cardinal = next(iter(location.items()))
            self.by_location.setdefault(location, {}).setdefault(cardinal, set()).add(inst)

        loot_type = attr.get("loot_type")

        if loot_type:
            self.by_category.setdefault(loot_type, set()).add(inst)

        if container_data:
            self.by_container.setdefault(inst, set())

        # if item starts inside container
        if attr.get("started_contained_in"):
            self.by_counter = {counter:inst}

            parent_name =attr.get("started_contained_in")
            parent_obj_list = self.by_name.get(parent_name)#instances_by_name(self, parent)
            if parent_obj_list:
                if len(parent_obj_list)==1:
                    for prospective_parent in parent_obj_list:
                        pros_parent_obj=self.instances.get(prospective_parent.id)
                        pros_children = pros_parent_obj.starting_children
                        if inst.name in pros_children:
                            inst.contained_in = pros_parent_obj
                            self.by_container[pros_parent_obj].add(inst) ## idk if this'll work.
                            #for child in pros_children:
                                #if child ==
                        #if child.id == inst.id:
                            #print(f"prospective parent: {prospective_parent}, type: {type(prospective_parent)} ")
                            #print(f"pros_parent_obj.id: {pros_parent_obj.id}")
                            #print(f"Added {inst.id} to parent {prospective_parent}: {self.by_container[prospective_parent]}")


                    #parent_id=next(iter(parent_obj_list))
                    #print(f"Parent id (next): {parent_id}, type: {type(parent_id)}")
                    #inst.contained_in = parent_id
                    #self.by_container[parent_id].add(inst.id) ## idk if this'll work.
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
    def move_item(self, inst:ItemInstance, place=None, direction=None, new_container=None):

        old_loc = inst.location
        if old_loc:
            location, cardinal = next(iter(old_loc.items()))
            if location in self.by_location:
                if cardinal in self.by_location.get(location):
                            ## syntax is wrong here. location is initialised as #self.by_location.setdefault(location, {}).setdefault(cardinal_key, set()).add(inst)
                    self.by_location[location][cardinal].discard(inst)
                if not self.by_location[location][cardinal]:
                    del self.by_location[location][cardinal]

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

        inst.contained_in = new_container ## 'inventory' should be a container. ## This should remove its container status just because 'new_container' is none by default, so 'move' with zero data added should just remove from container.

        ### TODO:: Use this for location descriptions/items. Currently it's all manual, but I should be able to do a version that takes the listed items and presents them automatically.

    def move_from_container_to_inv(self, inst:ItemInstance, inventory):

        parent = inst.contained_in
        self.by_container[parent].remove(inst)
        self.move_item(inst)
        inventory.append(inst)



    # -------------------------
    # Lookup
    # -------------------------
    def get_instance_from_id(self, inst_id):
        return self.instances.get(inst_id)

    def get_item(self, inst_id): # is a dupe of the previous, but I have this all througout the existing script so may change to it and remove get_instance later. One or the other, but for the moment, both.
        return self.instances.get(inst_id)

    def instances_at(self, place, direction):

        try:
            location = self.by_category[place]

        except:
            if not self.by_category.get(place):
                if "a " in place:
                    test_place = place.replace("a ", "") # the combo of these should fix all instances of a_/not a naming. If/when I add and 'an' start to a location name, will need to add 'an ' too.
                    if self.by_category.get(test_place):
                        place=test_place
                if not self.by_category.get(place):
                    if self.by_category.get("a " + place):
                        test_place = "a " + place
                        if self.by_category.get(test_place):
                            place=test_place

                else:
                    print(f"Location keys: `{self.by_location}`")
                    if not self.by_category[place]:
                        print(f"Location {place} has never had an item, so self.by_location fails. For now, just return.")
                        exit()
                        return None

        if self.by_location[place].get(direction): # check if the direction has been established yet.
            instance_list:list = [i for i in self.by_location[place].get(direction)] # if so, check if there are items there.
            if instance_list:
                return instance_list

    def instances_by_name(self, definition_key):
        return self.by_name.get(definition_key)# if self.by_name.get(definition_key) else None

    def instances_by_container(self, container):
        return [i for i in self.by_container.get(container, set())]

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

        """Convenience method to return a formatted description."""
        if caps:
            description = smart_capitalise(inst.description)
        else:
            description = inst.description
        if description:
            return description
        return "You see nothing special."

    def nicename(self, inst: ItemInstance):
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
            print("Item cannot be picked up.")
            return None, inventory_list

        if inst in inventory_list:
            #print("Item already in inventory. Creating new...") ## Not sure about this.
            from item_definitions import get_item_defs
            attr = get_item_defs(inst.name)
            inst = self.create_instance(inst.name, attr)


        self.move_item(inst, place, direction)
        inventory_list.append(inst)
        #print("INVENTORY LIST:: ", inventory_list) ## always add the ID, not instance or name, to the inventory. Make it prinable elsewhere.

        ## Note: I don't understand why we use id everywhere instead of instance itself. The first step of almost every function is getting the instance from the id anyway.
        return inst, inventory_list

    def drop(self, inst: ItemInstance, location, direction, inventory_list):
        if inst not in inventory_list:
            return None
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
    #(self, definition_key, item_def, nicename=None, description=None, location=None, contained_in=None, item_size=None, is_container=None, container_data=None)
    ## Just pass through attr here, figure out he details internally. Saves me having to change the func sig 100 times.
    #registry.create_instance("glass_jar", vase_def, location=("graveyard", "east"))

get_flags=False
if get_flags:
    get_all_flags()


def initialise_registry():
    from item_definitions import get_item_defs
    counter=0
    for item_name, attr in get_item_defs().items():
        registry.create_instance(item_name, attr, counter)#attr["name"], primary_category, is_container, can_pick_up, attr["description"], attr["starting_location"] or None, attr.get("contained_in") or None, attr["item_size"], container_data)
        counter+=1

    #print("FULL by_location:", registry.by_location)
#
    #exit()
    #counter=0
    #for item_name, attr in get_item_defs().items():
    #    registry.update_containers(item_name, attr, counter)
    #    counter+=1

# This section is meant for adding children to containers after all instances are created, but it doesn't work yet.
   #for item_name, attr in get_item_defs().items():
   #    for flag in attr["flags"]:
   #        if flag == "container":
   #            instance = registry.instances_by_name(item_name)
   #            for thing in instance:
   #                #print(f"Thing: {thing}")
   #                container_instances = registry.instances_by_container(thing.id)
   #                #print("Container instances: ", container_instances)

    #print("FULL by_container:", registry.by_container)
    #print("FULL by_category:", registry.by_category)


if __name__ == "__main__":

    initialise_registry()

