##REDUX VERSION, don't know if it's better or not yet.


import uuid

class ItemInstance:
    """
    Represents a single item in the game world or player inventory.
    """

    def __init__(self, definition_key, item_def, location=None, contained_in=None):
        self.id = str(uuid.uuid4())  # unique per instance
        self.definition_key = definition_key
        self.location = location       # tuple (place, direction) or None
        self.contained_in = contained_in  # parent instance id if inside a container
        self.children = []            # list of child instance IDs
        self.state_flags = set()      # any runtime flags (open/locked/etc)

        # Prepopulate children if definition has starting_children
        starting_children = item_def.get("starting_children", [])
        self.children = list(starting_children)

    def __repr__(self):
        return f"<ItemInstance {self.definition_key} ({self.id})>"


class LootRegistry:
    """
    Central manager for all item instances.
    Also keeps a location-indexed lookup for fast "what's here?" queries.
    """

    def __init__(self):
        self.instances = {}      # id -> ItemInstance
        self.by_location = {}    # (place, direction) -> set of instance IDs
        self.by_name = {}        # definition_key -> set of instance IDs

    # -------------------------
    # Creation / deletion
    # -------------------------
    def create_instance(self, definition_key, item_def, location=None, cardinal=None, contained_in=None):
        inst = ItemInstance(definition_key, item_def, location, cardinal, contained_in)
        self.instances[inst.id] = inst

        # Index by location
        if location:
            self.by_location.setdefault(location, set()).add(inst.id)

        # Index by name
        self.by_name.setdefault(definition_key, set()).add(inst.id)

        return inst

    def delete_instance(self, inst_id):
        inst = self.instances.pop(inst_id, None)
        if not inst:
            return

        # remove from location index
        if inst.location and inst.location in self.by_location:
            self.by_location[inst.location].discard(inst_id)
            if not self.by_location[inst.location]:
                del self.by_location[inst.location]

        # remove from name index
        self.by_name.get(inst.definition_key, set()).discard(inst_id)

    # -------------------------
    # Movement
    # -------------------------
    def move_item(self, inst_id, new_location=None, new_container=None):
        inst = self.instances[inst_id]

        # Update location
        old_location = inst.location
        old_cardinal = inst.cardinal

        if old_location and old_location in self.by_location:
            self.by_location[old_location].discard(inst_id)
            if not self.by_location[old_location]:
                del self.by_location[old_location]

        inst.location = new_location
        inst.contained_in = new_container ## 'inventory' should be a container.

        if new_location:
            self.by_location.setdefault(new_location, set()).add(inst_id)

    # -------------------------
    # Lookup
    # -------------------------
    def get_instance(self, inst_id):
        return self.instances.get(inst_id)

    def instances_at(self, place, direction):
        return [self.instances[i] for i in self.by_location.get((place, direction), set())]

    def instances_by_name(self, definition_key):
        return [self.instances[i] for i in self.by_name.get(definition_key, set())]

    # -------------------------
    # Helpers
    # -------------------------
    def pick_up(self, inst_id, inventory_list):
        inst = self.instances[inst_id]
        self.move_item(inst_id, new_location=None)
        inventory_list.append(inst_id)
        return inst

    def drop(self, inst_id, location_tuple, inventory_list):
        if inst_id not in inventory_list:
            return None
        inventory_list.remove(inst_id)
        self.move_item(inst_id, new_location=location_tuple)
        return self.instances[inst_id]



class Location:
    """
    Lightweight scaffolding for locations.
    Maintains items present and simple state like visited/weather.
    """

    def __init__(self, name):
        self.name = name
        self.visited = False
        self.weather_last_seen = None
        self.items_here = set()  # store instance IDs

    def add_item(self, inst_id):
        self.items_here.add(inst_id)

    def remove_item(self, inst_id):
        self.items_here.discard(inst_id)


# setup
registry = LootRegistry()
inventory = []

# create some items
vase_def = {
    "name": "glass jar with flowers",
    "description": "A glass jar holding dried flowers.",
    "starting_children": ["flowers_001"],
    "flags": ["CONTAINER", "CAN_PICKUP"]
}
vase = registry.create_instance("glass_jar", vase_def, location=("graveyard", "east"))

# create location object
graveyard_east = Location("graveyard_east")
graveyard_east.add_item(vase.id)

# pick up
registry.pick_up(vase.id, inventory)
graveyard_east.remove_item(vase.id)

# drop
registry.drop(vase.id, ("graveyard", "east"), inventory)
graveyard_east.add_item(vase.id)

# look around
for inst in registry.instances_at("graveyard", "east"):
    print(f"You see {inst.definition_key} at the location.")
