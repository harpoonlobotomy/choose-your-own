## 8/12/25 gippity entirely. Will change it later once the migraine moves on.

"""
✅ ItemInstance + ItemRegistry Skeleton

This version:

Assumes item_definitions is already loaded from JSON.
Provides safe methods for:
creating items
moving them
inserting/removing children
updating location/contained_in
deleting
basic state flag handling
Does NOT enforce validation rules yet (capacity, accepted types), but leaves hooks for them.
"""


# ============================================================
# ItemInstance
# ============================================================

class ItemInstance:
    """
    Runtime representation of an item that exists somewhere in the world.
    """
    def __init__(self, instance_id, definition_key):
        self.id = instance_id
        self.definition_key = definition_key

        # Only one of these is active at a time:
        self.location = None          # e.g. ("graveyard", "east")
        self.contained_in = None      # parent item instance_id if inside something

        # Children stored as instance_ids
        self.children = []

        # Arbitrary dynamic state flags – can be expanded later
        self.state_flags = set()

    # --------------------------------------------------------
    # Basic helpers
    # --------------------------------------------------------

    def is_in_world(self):
        return self.location is not None

    def is_in_container(self):
        return self.contained_in is not None

    def add_flag(self, flag):
        self.state_flags.add(flag)

    def remove_flag(self, flag):
        self.state_flags.discard(flag)

    def has_flag(self, flag):
        return flag in self.state_flags

    # --------------------------------------------------------

    def __repr__(self):
        return f"<ItemInstance {self.id} ({self.definition_key})>"



"""
============================================================
ItemRegistry
============================================================

This object stores ALL ItemInstances, and provides movement + containment logic.
"""

class ItemRegistry:
    """
    Holds all ItemInstances.
    Responsible for creating, deleting, and managing relationships.
    """
    def __init__(self):
        self.instances = {}
        self._id_counter = 0   # used for generating duplicate-item IDs

    # --------------------------------------------------------
    # ID generator
    # --------------------------------------------------------

    def _generate_id(self, prefix):
        self._id_counter += 1
        return f"{prefix}_{self._id_counter:05d}"

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    def create(self, definition_key, instance_id=None):
        """
        Create a new ItemInstance.
        If instance_id is None, a new generated ID is used.
        """
        if instance_id is None:
            instance_id = self._generate_id(definition_key)

        if instance_id in self.instances:
            raise ValueError(f"Instance ID already exists: {instance_id}")

        inst = ItemInstance(instance_id, definition_key)
        self.instances[instance_id] = inst
        return inst

    # --------------------------------------------------------
    # DELETE
    # Only if item is lost permanently - item is destroyed, money is spent, item is replaced with something else (transformed)
    # --------------------------------------------------------

    def delete(self, instance_id):
        """
        Delete an item and remove it from parents/locations.
        Caller must update location lists externally.
        """
        inst = self.instances.get(instance_id)
        if not inst:
            return

        # Remove from parent children list if needed
        if inst.contained_in:
            parent = self.instances.get(inst.contained_in)
            if parent:
                parent.children = [c for c in parent.children if c != instance_id]

        # Remove children references (does not delete them automatically)
        for child_id in inst.children:
            child = self.instances.get(child_id)
            if child:
                child.contained_in = None

        del self.instances[instance_id]

    # --------------------------------------------------------
    # LOOKUP
    # --------------------------------------------------------

    def get(self, instance_id):
        return self.instances.get(instance_id)

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    def add_child(self, parent_id, child_id):
        """
        Attach child item to parent.
        Does not enforce capacity yet.
        """
        parent = self.get(parent_id)
        child = self.get(child_id)

        if not parent or not child:
            raise ValueError("Invalid parent or child ID.")

        # Remove from previous container or location
        self._detach_from_world(child)

        parent.children.append(child_id)
        child.contained_in = parent_id

    def remove_child(self, parent_id, child_id):
        parent = self.get(parent_id)
        child = self.get(child_id)

        if not parent or not child:
            return

        if child_id in parent.children:
            parent.children.remove(child_id)
            child.contained_in = None

    # --------------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------------

    def _detach_from_world(self, inst):
        """
        Clears location or container, but does NOT update the location list.
        Caller is responsible for removing it from the location dict externally.
        """
        inst.location = None
        inst.contained_in = None

    def move_to_location(self, instance_id, location_tuple):
        """
        Move the item into a world location (room + direction).
        e.g. ("graveyard", "east")
        """
        inst = self.get(instance_id)
        if not inst:
            raise ValueError(f"No item with ID {instance_id}")

        # Remove from container, previous location
        self._detach_from_world(inst)

        inst.location = location_tuple

    def move_to_inventory(self, instance_id):
        """
        Just marks it as not in world, not in container.
        Your actual inventory list is stored elsewhere.
        """
        inst = self.get(instance_id)
        if not inst:
            raise ValueError(f"No item with ID {instance_id}")

        self._detach_from_world(inst)


"""
## to put in the working script to get display name.

def get_display_name(item_instance, item_definitions):
    definition = item_definitions[item_instance.definition_key]
    base_name = definition["name"]

    if item_instance.children:
        return base_name + " (with something inside)"  # stub

    return base_name

"""
