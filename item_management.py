## New version that hopefully fits better with what I need.
# (Includes my existing LootTable class)


"""
loot_table.py
A backwards-compatible LootTable with lightweight instance support.

Usage summary:
- Load your item_definitions (flat dict) and create LootTable(defs).
- Use loot.get_item(name) to access static definition (same as before).
- Create instances with loot.create_instance(def_name) (or let convenience
  methods auto-create instances).
- Methods like nicename(), describe(), set_location() accept either:
    - the original definition name (e.g. "glass jar") OR
    - an instance id (e.g. "glass jar_a1b2c3")
- game.inventory may temporarily remain a list of strings; helper functions
  allow gradual migration to instance-aware inventories.
"""

import uuid
import copy
from typing import Dict, Any, Optional, List, Tuple, Union

# ---------------------
# ItemInstance
# ---------------------
class ItemInstance:
    """
    Lightweight runtime item instance.
    - id: unique instance id (for unique world items this may equal def key)
    - definition_key: key into item_definitions
    - location: tuple (place, direction) if placed in world, else None
    - contained_in: parent instance id if inside container
    - children: list of instance ids contained inside this item
    - flags: dynamic runtime flags (set)
    - attrs: dictionary for any dynamic attributes (name overrides, text_col, etc.)
    """
    def __init__(self, instance_id: str, definition_key: str):
        self.id = instance_id
        self.definition_key = definition_key
        self.location: Optional[Tuple[str, str]] = None
        self.contained_in: Optional[str] = None
        self.children: List[str] = []
        self.flags = set()
        self.attrs: Dict[str, Any] = {}  # arbitrary dynamic attributes

    def __repr__(self):
        return f"<ItemInstance {self.id} ({self.definition_key})>"

# ---------------------
# ItemRegistry
# ---------------------
class ItemRegistry:
    """
    Stores all ItemInstance objects and simple operations to create/delete/lookup
    Instances are stored as ItemInstance objects keyed by instance id.
    """
    def __init__(self):
        self.instances: Dict[str, ItemInstance] = {}
        self._counter = 0

    def _gen_id(self, base: str) -> str:
        # produce stable-ish short ids: base + '_' + uuid6-ish
        self._counter += 1
        short = uuid.uuid4().hex[:6]
        safe_base = base.replace(" ", "_")
        return f"{safe_base}_{short}"

    def create(self, definition_key: str, instance_id: Optional[str] = None) -> ItemInstance:
        if instance_id is None:
            instance_id = self._gen_id(definition_key)
        if instance_id in self.instances:
            raise ValueError(f"Instance id {instance_id} already exists")
        inst = ItemInstance(instance_id, definition_key)
        self.instances[instance_id] = inst
        return inst

    def delete(self, instance_id: str) -> None:
        inst = self.instances.get(instance_id)
        if not inst:
            return
        # detach from parent
        if inst.contained_in:
            parent = self.instances.get(inst.contained_in)
            if parent and instance_id in parent.children:
                parent.children.remove(instance_id)
        # detach children (do not delete them automatically)
        for child_id in list(inst.children):
            child = self.instances.get(child_id)
            if child:
                child.contained_in = None
        del self.instances[instance_id]

    def get(self, instance_id: str) -> Optional[ItemInstance]:
        return self.instances.get(instance_id)

    def find_instances_by_def(self, def_key: str) -> List[ItemInstance]:
        return [i for i in self.instances.values() if i.definition_key == def_key]

    # helper to attach/detach children
    def add_child(self, parent_id: str, child_id: str) -> None:
        parent = self.get(parent_id)
        child = self.get(child_id)
        if not parent or not child:
            raise ValueError("Invalid parent or child id")
        # detach child from previous container/location
        if child.contained_in:
            prev_parent = self.get(child.contained_in)
            if prev_parent and child_id in prev_parent.children:
                prev_parent.children.remove(child_id)
        child.contained_in = parent_id
        child.location = None
        if child_id not in parent.children:
            parent.children.append(child_id)

    def remove_child(self, parent_id: str, child_id: str) -> None:
        parent = self.get(parent_id)
        child = self.get(child_id)
        if not parent or not child:
            return
        if child_id in parent.children:
            parent.children.remove(child_id)
        child.contained_in = None

    def move_to_location(self, instance_id: str, location: Optional[Tuple[str, str]]) -> None:
        inst = self.get(instance_id)
        if not inst:
            raise ValueError(f"No instance {instance_id}")
        inst.location = location
        if location is not None:
            inst.contained_in = None

# ---------------------
# LootTable (backwards-compatible wrapper)
# ---------------------
class LootTable:
    """
    Backwards-compatible LootTable that also manages instances.
    Initialize with item_definitions (flat dict).
    """
    def __init__(self, item_definitions: Dict[str, Dict[str, Any]], name: str = "LootTable"):
        self.name = name
        # store a deep copy to avoid accidental mutation of the original input
        self.definitions: Dict[str, Dict[str, Any]] = copy.deepcopy(item_definitions)
        self.registry = ItemRegistry()
        # Build a quick lookup by name
        self.by_name = {}  # maps definition key -> normalized entry
        self._build_lookup()
        # optional location index caching for convenience
        # locations: dict place -> direction -> list of instance ids (populated by user code if needed)
        self.locations: Dict[str, Dict[str, List[str]]] = {}

    # ---------------------
    # Loader / Lookup
    # ---------------------
    def _build_lookup(self) -> None:
        """
        Normalize definitions into by_name with sensible defaults.
        Fields guaranteed to be present:
         - name (string)
         - description (string)
         - flags (list)
         - Either "starting_location" OR "item_type"
        """
        for key, data in self.definitions.items():
            entry = dict(data)  # shallow copy
            entry.setdefault("name", key)
            entry.setdefault("description", entry.get("description", f"A {entry['name']}."))
            entry.setdefault("flags", entry.get("flags", []))
            # support either 'starting_children' or 'children' names
            if "starting_children" in entry:
                entry.setdefault("starting_children", entry.get("starting_children", []))
            else:
                entry.setdefault("starting_children", entry.get("children", []))
            # canonicalize optional fields used by your engine:
            entry.setdefault("description_no_children", entry.get("description_no_children"))
            entry.setdefault("name_children_removed", entry.get("name_children_removed"))
            entry.setdefault("container_limits", entry.get("container_limits"))
            entry.setdefault("item_size", entry.get("item_size"))
            # keep original key for backreferences
            entry["_def_key"] = key
            self.by_name[key] = entry

    # ---------------------
    # Definition access (same as original API)
    # ---------------------
    def get_item(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Return the static definition for a given definition-key (name).
        Note: this is the same as your old loot.get_item(name).
        """
        return self.by_name.get(name)

    def get_full_category(self, selection: str):
        # Basic implementation: return list of defs in a category if the field exists
        items = [k for k, v in self.by_name.items() if v.get("category") == selection]
        return items

    def random_from(self, selection):
        import random
        items = []
        if isinstance(selection, int):
            # if selection is int, try to interpret as index? keep simple:
            all_keys = list(self.by_name.keys())
            return random.choice(all_keys) if all_keys else None
        else:
            if selection in self.by_name:
                items = [selection]
            else:
                # assume selection is a category name
                items = [k for k, v in self.by_name.items() if v.get("loot_type") == selection or v.get("category") == selection]
        return random.choice(items) if items else None

    # ---------------------
    # Describe / nicename (backwards-compatible)
    # ---------------------
    def describe(self, name_or_instance: Union[str, ItemInstance], caps: bool = False) -> str:
        """
        Return a formatted description. Accepts either a definition key or an instance id or ItemInstance.
        If instance id is passed, uses its definition and state to choose description.
        """
        inst = None
        if isinstance(name_or_instance, ItemInstance):
            inst = name_or_instance
        elif isinstance(name_or_instance, str):
            # could be instance id or definition name
            inst = self.registry.get(name_or_instance)
        if inst:
            # instance-aware description: check children state
            defn = self.get_item(inst.definition_key)
            if not defn:
                return f"[DESCRIBE] No definition found for instance {inst.id}"
            # if has children, use normal description; if empty and def has description_no_children use that
            if inst.children:
                text = defn.get("description") or defn.get("name")
            else:
                text = defn.get("description_no_children") or defn.get("description") or defn.get("name")
        else:
            # treat name_or_instance as definition key
            defn = self.get_item(name_or_instance)
            if not defn:
                return f"[DESCRIBE] No such item: {name_or_instance}"
            text = defn.get("description")
        if caps:
            return smart_capitalise(text)
        return text

    def nicename(self, name_or_instance: Union[str, ItemInstance]) -> Optional[str]:
        """
        Return display name. Accepts definition key, instance id, or ItemInstance.
        """
        inst = None
        if isinstance(name_or_instance, ItemInstance):
            inst = name_or_instance
        elif isinstance(name_or_instance, str):
            inst = self.registry.get(name_or_instance)
        if inst:
            defn = self.get_item(inst.definition_key)
            if not defn:
                return inst.definition_key
            # dynamic naming: if children removed, prefer name_children_removed when present
            if not inst.children and defn.get("name_children_removed"):
                return defn.get("name_children_removed")
            # else return definition 'name'
            return defn.get("name", inst.definition_key)
        else:
            # treat input as definition key
            defn = self.get_item(name_or_instance)
            if not defn:
                return None
            return defn.get("name")

    # ---------------------
    # Instance creation & helpers
    # ---------------------
    def create_instance(self, def_key: str, instance_id: Optional[str] = None,
                        place_location: Optional[Tuple[str, str]] = None,
                        spawn_children: bool = True) -> str:
        """
        Create an instance for a definition key.
        - If the def_key corresponds to a unique world item that should be
          single, you might want to pass instance_id=def_key to keep it stable.
        - spawn_children: will create instances for starting_children and
          attach them into this instance.
        Returns the instance id.
        """
        if def_key not in self.by_name:
            raise KeyError(f"No such definition: {def_key}")
        # if instance_id is None and the definition looks like a world-unique item
        # you may want stable id: caller can pass instance_id=def_key
        inst = self.registry.create(def_key, instance_id=instance_id)
        # initial flags reflect definition flags (copy)
        for f in (self.by_name[def_key].get("flags") or []):
            inst.flags.add(f)
        # set display attrs from definition if present
        if self.by_name[def_key].get("text_col") is not None:
            inst.attrs["text_col"] = self.by_name[def_key].get("text_col")
        # children
        starting_children = self.by_name[def_key].get("starting_children", []) or []
        if spawn_children and starting_children:
            for child_def in starting_children:
                child_inst = self.create_instance(child_def)
                self.registry.add_child(inst.id, child_inst)
        # set initial location if provided
        if place_location:
            self.registry.move_to_location(inst.id, place_location)
        else:
            # if definition contains starting_location, set it
            starting_loc = self.by_name[def_key].get("starting_location")
            if starting_loc:
                # starting_loc expected as tuple (place, dir)
                self.registry.move_to_location(inst.id, starting_loc)
        return inst.id

    def create_instances_from_starting(self) -> List[str]:
        """
        Create instances for all definitions that have 'starting_location' defined.
        Returns list of created instance ids.
        """
        created = []
        for def_key, defn in self.by_name.items():
            if defn.get("starting_location"):
                # create with instance id equal to def_key for stable reference
                inst_id = self.create_instance(def_key, instance_id=def_key, place_location=defn["starting_location"])
                created.append(inst_id)
        return created

    # ---------------------
    # Location & container operations
    # ---------------------
    def set_location(self, name_or_instance: str, place: str, cardinal: str, picked_up: bool = False) -> List[str]:
        """
        Backwards-compatible set_location. Accepts a definition name or an instance id.
        Returns a list of instance ids that were set (parent + children).
        If passed a definition name and there is no instance yet, it will create one.
        If picked_up True, it marks instance as not in world (location=None) and caller
        is expected to add it to the inventory list.
        """
        to_set = []
        # Determine instance id(s)
        # If name_or_instance refers to an existing instance id -> use that
        inst = self.registry.get(name_or_instance)
        if inst:
            instance_ids = [inst.id] + inst.children.copy()
        else:
            # treat as definition key: create instance if none exists
            defn = self.get_item(name_or_instance)
            if not defn:
                return []
            # create a new instance with stable id equal to def key if it's a starting item,
            # otherwise create auto id
            instance_id = name_or_instance if defn.get("starting_location") else None
            inst_id = self.create_instance(name_or_instance, instance_id=instance_id,
                                           place_location=(place, cardinal) if not picked_up else None)
            inst = self.registry.get(inst_id)
            instance_ids = [inst_id] + inst.children.copy()

        for iid in instance_ids:
            i = self.registry.get(iid)
            if not i:
                continue
            if picked_up:
                # detach from world (inventory is external)
                self.registry.move_to_location(iid, None)
            else:
                self.registry.move_to_location(iid, (place, cardinal))
            to_set.append(iid)
        return to_set

    def pick_up(self, name_or_instance: str, inventory_list: List[Union[str, ItemInstance]]) -> Optional[str]:
        """
        Convenience: pick up an item (definition name or instance id).
        - If passed a definition name and no instance exists in world, it creates one.
        - Adds instance id into inventory_list (caller-managed).
        Returns instance id or None.
        """
        inst = self.registry.get(name_or_instance)
        if not inst:
            # create an instance (do not place it in world)
            inst_id = self.create_instance(name_or_instance)
            inst = self.registry.get(inst_id)
        # Remove from any location / parent
        inst.location = None
        if inst.contained_in:
            parent = self.registry.get(inst.contained_in)
            if parent and inst.id in parent.children:
                parent.children.remove(inst.id)
            inst.contained_in = None
        # Add to inventory_list (we store instance ids)
        # allow inventory to contain either strings or instance objects; normalize later
        inventory_list.append(inst.id)
        return inst.id

    def drop(self, instance_or_name: str, place: str, cardinal: str, inventory_list: List[Union[str, ItemInstance]]) -> Optional[str]:
        """
        Drop an item from inventory into a place/direction.
        instance_or_name can be an instance id or a definition-name (old-style).
        The function will try to find / create the instance, remove it from inventory_list,
        and set its location.
        Returns instance id dropped or None.
        """
        # find instance in registry or inventory
        inst = None
        if self.registry.get(instance_or_name):
            inst = self.registry.get(instance_or_name)
        else:
            # maybe inventory holds the instance id; search inventory_list
            for it in inventory_list:
                if isinstance(it, ItemInstance):
                    if it.id == instance_or_name or it.definition_key == instance_or_name:
                        inst = it
                        break
                elif isinstance(it, str):
                    # could be instance id or def name
                    if self.registry.get(it) and it == instance_or_name:
                        inst = self.registry.get(it)
                        break
                    if it == instance_or_name:
                        # it's a plain string (def name); create instance for drop
                        inst_id = self.create_instance(it)
                        inst = self.registry.get(inst_id)
                        break
        if not inst:
            return None
        # remove from inventory_list (match by id or def-name)
        removed = False
        for idx, it in enumerate(list(inventory_list)):
            if isinstance(it, ItemInstance):
                if it.id == inst.id:
                    inventory_list.pop(idx); removed = True; break
            elif isinstance(it, str):
                if it == inst.id or it == inst.definition_key:
                    inventory_list.pop(idx); removed = True; break
        # set location
        self.registry.move_to_location(inst.id, (place, cardinal))
        return inst.id

    # ---------------------
    # Utility / debug
    # ---------------------
    def debug_print_registry(self) -> None:
        print("=== LOOT: Definitions ===")
        for k, v in self.by_name.items():
            print(f"{k}: name={v.get('name')}, flags={v.get('flags')}")
        print("\n=== LOOT: Instances ===")
        for iid, inst in self.registry.instances.items():
            print(f"{iid}: def={inst.definition_key}, loc={inst.location}, parent={inst.contained_in}, children={inst.children}, flags={sorted(list(inst.flags))}, attrs={inst.attrs}")

    def debug_print_location_index(self) -> None:
        print("=== Locations index (user-managed) ===")
        for place, dirs in self.locations.items():
            print(f"{place}:")
            for d, items in dirs.items():
                print(f"  {d}: {items}")

    # ---------------------
    # Inventory helpers (for transition)
    # ---------------------
    def inventory_get_instance_ids(self, inventory_list: List[Union[str, ItemInstance]]) -> List[str]:
        """Return a list of instance ids present in inventory_list (convert strings where possible)."""
        ids = []
        for it in inventory_list:
            if isinstance(it, ItemInstance):
                ids.append(it.id)
            elif isinstance(it, str):
                # could be instance id or def name. Prefer instance id if exists
                if self.registry.get(it):
                    ids.append(it)
                else:
                    # try to find an instance of this def in inventory or registry
                    found = None
                    for inst in self.registry.find_instances_by_def(it):
                        if inst and inst.id not in ids:
                            found = inst.id
                            break
                    if found:
                        ids.append(found)
                    else:
                        # not present as instance; leave the def-name as placeholder
                        # but still return the def-name so callers can handle it
                        ids.append(it)
        return ids

    def inventory_get_names(self, inventory_list: List[Union[str, ItemInstance]]) -> List[str]:
        """Return display names for inventory items (safe for mixed-type inventories)."""
        names = []
        for it in inventory_list:
            if isinstance(it, ItemInstance):
                names.append(self.nicename(it))
            elif isinstance(it, str):
                # if it's an instance id:
                inst = self.registry.get(it)
                if inst:
                    names.append(self.nicename(inst))
                else:
                    # treat as definition key
                    defn = self.get_item(it)
                    if defn:
                        names.append(defn.get("name"))
                    else:
                        # unknown string possibly user input - pass through
                        names.append(it)
        return names

# ---------------------
# Small helper function used by describe() to capitalise
# ---------------------
def smart_capitalise(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]

# ---------------------
# End of module
# ---------------------
