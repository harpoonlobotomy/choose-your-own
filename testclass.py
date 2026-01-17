from email.iterators import typed_subpart_iterator
import uuid
from pprint import pprint
from itemRegistry import ItemInstance
import printing
from dynamic_data import generated_items

temp_items = generated_items.test_items

standard = "standard"
static = "static"
can_pick_up = "can_pick_up"
container = "container"
event = "event"
trigger = "trigger"

confirmed_items = {}

type_defaults = { # gently ordered - will overwrite earlier attrs with later ones (eg 'is horizontal surface' for flooring with overwrite 'static''s.)
    "standard": {},
    "static": {"can_examine": False, "breakable": False}, # removed [["is_horizontal_surface": False, "is_vertical_surface": False]] becaue I'm not going to be searching for the lack of horizontal surfaces...
    "all_items": {"starting_location": None, "current_loc": None},
    "container": {"is_open": False, "can_be_closed": True, "can_be_locked": True, "is_locked": True, "requires_key": False},
    "key": {"is_key": True},
    "can_pick_up": {"can_pick_up": True, "item_size": 0, "started_contained_in": None, "contained_in": None},
    "event": {"event": None, "event_type": "item_triggered", "event_key": None},
    "trigger": {"trigger_type": "plot_advance", "trigger_target": None, "is_exhausted": False},
    "flooring": {"is_horizontal_surface": True},
    "wall": {"is_vertical_surface": True}#,
    #"exterior": {"is_interior": False} ## Can be set scene-wide, so 'all parts of 'graveyard east' are exterior unless otherwise mentioned'. (I say 'can', I mean 'will be when I set it up')
}## Removed all the interior dicts. They're not necessary and will actually get in the way - having the type defaults exposed is far more beneficial.

def testing_t_defaults_against_item_defs():

    all_flags_in_type_default = set()
    for type in type_defaults:
        for flag in type_defaults[type]:
            all_flags_in_type_default.add(flag)

    print(f"all flags in type_default: {all_flags_in_type_default}")

    def_flags_in_t_def = set()
    all_def_flags = set()
    from item_definitions import item_defs_dict
    for item, val in item_defs_dict.items():
        for flag, content in val.items():
            if flag == "" or flag == None:
                continue
            if flag == "flags":
                for flagname in content:
                    if flagname in all_flags_in_type_default:
                        def_flags_in_t_def.add(flagname)
                    else:
                        all_def_flags.add(flagname)
            else:
                if flag in all_flags_in_type_default:
                    def_flags_in_t_def.add(flag)
                else:
                    all_def_flags.add(flag)

    print(f"Flags matching in type_default: {def_flags_in_t_def}")
    print(f"Flags in item_defs but not default_types: {all_def_flags - all_flags_in_type_default}")

"""
all flags in type_default: {'event_type', 'starting_location', 'is_open', 'current_loc', 'can_pick_up', 'breakable', 'can_be_locked', 'trigger_target', 'can_be_closed', 'started_contained_in', 'requires_key', 'can_examine', 'is_exhausted', 'is_vertical_surface', 'item_size', 'contained_in', 'event_key', 'is_horizontal_surface', 'is_key', 'is_locked', 'trigger_type', 'event'}

Flags matching in type_default: {'is_key', 'starting_location', 'item_size', 'is_locked', 'started_contained_in', 'can_pick_up'}

Flags in item_defs but not default_types: {'can_combine', '', 'can_open', 'is_charged', 'alt_names', 'is_hidden', 'key', 'dupe', 'print_on_investigate', 'special_traits', 'needs_key_to_lock', 'starting_children', 'container', 'fragile', 'loot_type', 'description', 'name', 'panacea', 'container_limits', 'dirty', 'description_no_children', 'takes_batteries', 'can_consume', 'flammable', 'name_children_removed', 'combine_with', 'weird', 'can_remove_from', 'is_closed', 'can_read', 'can_lock'}

So, I need to figure out which of these need to be just in a item.flags.get() situation vs those which need to be properly attributed. Something like takes_batteries is the former, dirty (or 'is_dirty' as it'll be corrected) is probably the latter but iffy, while 'description_no_children' can just go to container-type.

Basically I want to quickly write something to look at the existing flags and generate a new item defs dict using those new tags in line with the new class, and reusing as many elements as possible.

First, planning grouping.

('key') and ('container') are default_types already, so if an item has that flag it has to have that default_type regardless. " 'description', 'name'," are taken care of elsewhere too. (Not currently included in the default_type, but in the item init)

('can_open', 'needs_key_to_lock', 'starting_children', 'container_limits', 'description_no_children', 'name_children_removed','is_closed', 'can_lock')
These are all the ones that should be under container, but I need to clear them out/rename them, etc.

Maybe a 'books_paper' type, for 'can_read', 'flammable' defaults.
books_paper = ('print_on_investigate', 'flammable', 'can_read')

(is_hidden) should apply to anything can_pick_up probably, they're the most likely category to be hidden. Or maybe just add it as a mass flag in all_items.

('can_combine') will be implemented later once I have some actual item combinations (in the sense of 'take a and b and they're a different combined object, c', not just containers.)

('loot_type') might need to be renamed but should keep its current function.

('can_be_charged', 'is_charged', 'takes_batteries') should be in an 'electronics' default_type.

('alt_names', 'special_traits') should be added to everything by default.

('fragile') should be its own type, with 'broken_name: <brokenname>' connecting it to the 'broken variant' of the item if it has one. Maybe 'damageable' is a more accurate word for it, for things that can burn, break, etc. It's a bad word but more accurate. Will think on a better alternative.

('dupe') isn't implemented at all yet I don't think. I don't think there's much of a need for it as the instances system works like that by default now. If I have 5x paperclips in a location it should just create 5 instances. Will have to check if that works in the new class, it'll need adjusting if not.

('panacea') is a special tag, not implemented yet but I like the idea of it. For now put it in 'special traits ={}'; not used for anything but keeping it there so I remember to use it later.

('dirty') probably won't be a default_type flag, though maybe a location-type one. Need to implement location-types (so, 'dirty alleyway' applies 'dirty' to the things in it, 'mermaid grotto' makes things wet, etc. Not sure how/if it'll be used but I have the 'clean' verb in verbreg so might as well have a conceptual use for it.)

('can_consume'), as above for 'dirty'. Although maybe... 'food_drink' category? can_consume, 'can_spoil', 'effect' (ie gain/lose health, etc), is_safe:bool. Mm, I like that.

('weird') I'm probably just going to leave out. Or maybe just add it to special_traits. I really like the idea of a layered experience, where depending on xyz things are different on a game-tone level, but it's double the work and I just want to get the basics running again for now.

"""


#testing_t_defaults_against_item_defs()

size = "item_size"
box_desc = "It's a box. Boxy box."

descriptions = {
    "box": box_desc,
    "locked box": box_desc,
    "cabinet": "A cabinet with something weird about it.",
    "elephant": "Big and grey and stompy."
}

test_items = {
    "everything": {"item_type": set((static, container, can_pick_up, event, trigger, "flooring"))},
    "earring": {"item_type": set((can_pick_up,)), "exceptions": {"started_contained_in": "box"}},
    "box": {"item_type": set((container, can_pick_up)), "exceptions": {"can_be_locked": False}},
    #"gold key": {"item_type": set(("key",)), "exceptions": {"starting_location": "some other place"}},
    "locked box": {"item_type": set((container, can_pick_up)), "exceptions": {"requires_key": "gold key", "starting_location": "east graveyard"}},
    "cabinet": {"item_type": set((static, event)), "exceptions": {"can_examine": True, "event_key": "box", "trigger_target": "box"}},
    "wall": {"item_type": set((static,)), "exceptions": {"is_vertical_surface": True}},
    "elephant": {"item_type": set((standard,)), "exceptions": {size:10}},
    "stone ground": {"item_type": set((static, "flooring"))}
}

## Do I want "exceptions": {"is_vertical_surface": True}
#or
#"item_type": set((static, "flooring") ??

locations = {"Graveyard": {"east": {"items": ["stone ground", "grave"]}, "west": {"items": ["stone ground"]}, "north": {"items": ["stone ground"]}, "south": {"items": ["stone ground", "headstones"]}},
            "OtherPlace": {"east": {"items": ["everything", "grandfather clock"]}, "west": {"items": ["birdbath"]}, "north": {"items": "merry-go-round"}, "south": {"items": "rocking chair"}},
            "Mermaid Grotto": {"east": {"items": ["sandy ground"]}, "west": {"items": ["sandy ground"]}, "north": {"items": ["sandy ground"]}, "south": {"items": ["sandy ground"]}}
            }

flag_keys = ("id", "name", "description", "current_loc", "is_open", "can_be_closed", "can_be_locked", "is_locked", "requires_key", "is_key", "can_pick_up", "can_examine", "breakable", "contained_in", "item_size", "item_type", "is_horizontal_surface", "is_vertical_surface", "event", "event_type", "item_triggered", "event_key", "trigger_target", "trigger_type", "plot_advance", "is_exhausted", "starting_location", "started_contained_in", "extra")

use_generated = True
 ## just a shortcut for a min while I test TODO remember to delete later
gen_items = {}

def use_generated_items(input_=None):

    import json
    json_file = "dynamic_data/generated_items.json"
    with open(json_file, 'r') as file:
        data = json.load(file)
    data_keys = list(data)
    global gen_items
    gen_items = data

    if input_ == None:
        keys = data_keys
    elif isinstance(input_, str):
        keys = set((input_,))
        print(f"data[input_]:")
        print(f"{data[input_]}")
        entry = {}
        entry[input_] = data[input_]
        return entry

    elif isinstance(input_, set|list|tuple):
        keys = set(i for i in input_)
    elif isinstance(input_, dict):
        keys = set(input_)

        for key in keys:
            if key in data_keys:
                print(f"JSON entry: \n{data[key]}")
                print(f"Memory entry: \n{input_[key]}")
                print("Type 'm' to update the JSON with the memory entry, otherwise the JSON will be kept as-is.")
                test=input()
                if test == "m":
                    data[key] = input_[key]

    printing.print_red(f"Data keys: {data_keys}")
    printing.print_red(f"keys: {keys}")

    #with open(json_file, 'w') as file:
    #    json.dump(data, file, indent=2)

class testInstances:

    def __init__(self, definition_key, attr):

        self.id = self.id = str(uuid.uuid4())
        self.name = definition_key
        #print(f"ATTR: {attr}")
        for attribute in attr:
            if attribute == "item_type":
                item = attr[attribute]
                if isinstance(item, str):
                    #print(f"ATTRIBUTE: {item}")
                    _, item = item.split("{")
                    item, _ = item.split("}")
                    #print(f"ATTRIBUTE: {item}")
                    item = item.replace("'", "")
                    parts = item.split(", ")
                    attr["item_type"] = set(parts)

        self.item_type = set(attr["item_type"])
        self.starting_location = None
        self.current_loc = None

        if "all_items" not in self.item_type:
            self.item_type.add("all_items")
        if test_items.get(self.name):
            item_types = test_items[self.name].get("item_type")
            for cat in item_types:
                if cat not in self.item_type:
                    self.item_type.add(cat)

        for item_type in type_defaults:
            #print(f"item type in type_defaults: {item_type}")
            if item_type in self.item_type:
                #print(f"This item_type is in self.item_type: {item_type}")

                for flag in type_defaults[item_type]:
                    #print(f"Flag `{flag}` in item type `{item_type}` for `{self.name}`. Flag type: {type(type_defaults[item_type][flag])}")
                    setattr(self, flag, type_defaults[item_type][flag])
           # else:
                #print(f"This item type is not in self.item_type: {item_type}")
                #print(f"self.item_types: {self.item_type}, type: {self.item_type}")

        for item in attr:
            if item != "exceptions":
                if not hasattr(self, item):
                    setattr(self, item, attr[item])

        if attr.get("exceptions"):
            #print(f"EXCEPTIONS for `{self.name}`. `{attr.get("exceptions")}`")
            for flag in attr.get("exceptions"):
                if isinstance(flag, dict):
                    for sub_flag in type_defaults[item_type][flag]:
                        if sub_flag in attr["exceptions"]:
                            setattr(self, sub_flag, attr["exceptions"][sub_flag])
                        else:
                            setattr(self, sub_flag, type_defaults[item_type][flag][sub_flag])
                else:
                    setattr(self, flag, attr["exceptions"][flag])

        if self.starting_location:
            self.current_loc = self.starting_location

        if hasattr(self, "started_contained_in"):
            self.contained_in = self.started_contained_in

        #printing.print_yellow(f"SELF: {vars(self)}")
        #print(f"INSTANCE CREATED: {self}")

    def __repr__(self):
        return f"<ItemInstance {self.name} ({self.id})>"

class testRegistry:
    def __init__(self):

        self.instances = set()
        self.by_name = {}        # definition_key -> set of instances
        self.by_id = {}
        self.by_location = {}    # cardinalinst (when implemented, str for now), > instances
        self.temp_items = set() # just exists as a place to live for dynamic item generation so it doesn't mess with for loops. Should be empty, only used temporarily and then cleared (contents added to self.instances) after the current loop.
        self.confirmed_items = {} # as above, will probably merge them later.
        self.updated = set() # again, can probably be merged with the above. Doesn't need to be part of this class at all, it's purely here for convenience because I'm tired.

    def init_single(self, item_name, item_entry):
        inst = testInstances(item_name, item_entry)
        self.instances.add(inst)
        self.by_name[inst.name] = inst
        self.by_id[inst.id] = inst

        if not descriptions.get(item_name):
            if not item_entry.get("description") or item_entry.get("description") == f"It's a {item_name}":
                printing.print_yellow(f"Item `{item_name}` does not have a description, do you want to write one?. Enter it here, or hit enter to cancel.")
                while True:
                    test=input()
                    if test and test != "":
                        print("Is this correct? 'y' to accept this description, 'n' to try again or nothing to cancel.")
                        trial = test
                        new_test = input()
                        if new_test == "y":
                            descriptions[item_name] = trial
                            self.updated.add(inst)
                            break

                    elif test == "":
                        break
            elif item_entry.get("description") and item_entry.get("description") != f"It's a {item_name}":
                descriptions[item_name] = item_entry.get("description")

        setattr(inst, "description", (descriptions.get(item_name) if descriptions.get(item_name) else f"It's a {item_name}"))
        return inst


    def init_items(self, item_data):

        if isinstance(item_data, dict):
            for item_name, item_entry in item_data.items():
                inst = self.init_single(item_name, item_entry)

        elif isinstance(item_data, str):
            item_entry = {}
            #item_entry[item] = ({"item_type": [static]})
            if test_items.get(item):
                item_entry[item] = test_items[item]
            else:
                item_entry[item] = ({"item_type": [static]})

            #print(f"item_entry: {item_entry[item]}")
            inst = self.init_single(item_data, item_entry[item])

        return inst

    def new_item_from_str(self, item_name:str, input_str:str=None)->str|testInstances:

        if not input_str:
            print(f"Please enter the default_types you want to assign to `{item_name}`")
            input_str = input()

        if not isinstance(input_str, str):
            print(f"new_item_from_str requires a string input, not {type(input_str)}")
            return

        if input_str == "" or input_str == None:
            print(f"Blank input skin, returning {item_name} unchanged. No instance created.")
            return input_str

        if " " in input_str.strip():
            parts = input_str.strip().split(" ")
            parts = (i for i in parts if i != None and i in list(type_defaults))
            new_str = set(parts)

        elif input_str in list(type_defaults):
            new_str = set((input_str))

        else:
            print(f"Input is not valid: {input_str}")
            return item_name

        new_item_dict = {}
        new_item_dict[item_name] = ({"item_type": new_str})
        ## this will have live locations later, for now just spoofing it ## TODO don't forget to updat this once env_data is plugged in.
        new_item_dict[item_name]["exceptions"] = {"starting_location": "graveyard north"}

        inst = self.init_items(new_item_dict)
        self.instances.add(inst)
        self.temp_items.add(inst)

        printing.print_green(text=vars(inst), bg=False, invert=True)
        return inst

    def add_to_gen_items(self, instance):
        #print(f"Temp items: {temp_items}")
        key = instance.name
        entry = vars(instance)
        #temp_items.update(entry)
        printing.printkind(key)
        printing.printkind(entry)

        pop_me = set()
        for header, item in entry.items():
            if header in ("starting_location", "current_loc", "id", "contained_in", "started_contained_in"): # listing the container variants because idk why the 'isinstance' below isn't working yet.
                pop_me.add(header)
            elif isinstance(item, set):
                entry[header] = str(item)
            elif isinstance(item, ItemInstance):
                pop_me.add(header)

        if pop_me:
            for header in pop_me:
                entry.pop(header)

        print(f"Popped dict: {entry}")

        import json
        json_file = "dynamic_data/generated_items.json"
        with open(json_file, 'r') as file:
            print(f"KEY: {key}")
            data = json.load(file)
            data[key] = entry

        with open(json_file, 'w') as file:
            json.dump(data, file, indent=2)
        #generated_items.test_items[key] = (entry)
        #print(f"Temp items: {generated_items.test_items}")

    def item_by_name(self, item_name) -> testInstances:

        if isinstance(item_name, testInstances):
            return item_name

        items = self.by_name.get(item_name)
        if isinstance(items, testInstances):
            return items
    # later, disambiguate. For now, cheat and just take the first.
        elif items != None:
            return items[0]


        if use_generated:
            generated_entry = use_generated_items(item_name)
            if generated_entry:
                inst = self.init_items(generated_entry)
                if inst:
                    print(f"\nGENERATED: {inst}\n")
                    printing.print_yellow("Are you happy with this item?")
                    pprint(f"VARS: {vars(inst)}")
                    test = input()
                    if test in ("y", "yes"):
                        self.confirmed_items[item_name] = inst
                    return inst
                else:
                    print(f"Failed to generate instance from {generated_entry}")
            else:
                print(f"No generated entry for {item_name}; continuing.\n")

        printing.print_red(f"\nNothing found for item name `{item_name}` in def item_by_name.", invert=True)
        printing.print_red("Do you want to create a new instance with this name?", invert=True)
        printing.print_red("please enter ' <type_default_key> ' to create a new instance of that type now.", invert=True)
        printing.print_green(f"Options: {list(type_defaults)}")
        printing.print_red("Entering nothing will skip this process.\n", invert=True)

        test = input()

        if test:
            instance = self.new_item_from_str(item_name, test)
            if instance and isinstance(instance, testInstances):
                self.temp_items.add(instance)
                self.add_to_gen_items(instance)
                return instance
            else:
                print(f"Failed to create instance for {item_name}. Returning item_name instead.")
                return item_name
        else:
            print("Returning string instead.")
            return item_name

    def clean_children(self):

        target_flags = ("contained_in", "requires_key", "event_key", "trigger_target")

        def cleaning_loop():
            itemlist = frozenset(self.by_id)
            for item_id in itemlist:
                item = self.by_id.get(item_id)
                for flag in target_flags:
                    if hasattr(item, flag) and getattr(item, flag) not in (False, None):
                        target_obj = self.item_by_name(getattr(item, flag))
                        if target_obj:
                            if flag == "contained_in":
                                if hasattr(item, "started_contained_in") and item.started_contained_in == item.contained_in:
                                    item.started_contained_in = target_obj
                            setattr(item, flag, target_obj)

                        else:
                            print(f"Missing an instance for `{item.name}`'s  `{flag}`: {getattr(item, flag)}")

        starting_count = len(self.instances)

        #try:
        cleaning_loop()
        #except Exception as E:
        #    print(f"Exception: {E}")

        if len(self.instances) == starting_count:
            print("Huh, count is the same.")


    def edit_item(self, instance):
        if not isinstance(instance, testInstances):
            if isinstance(instance, str):
                print("Edit item needs an Instance object. Will attempt to find by name.")
                instance = self.item_by_name(instance)
                if not isinstance(instance, testInstances):
                    print(f"Could not find item {instance} by name.")

            else:
                print(f"I can't do anything with an instance of type {type(instance)}. Cannot process {instance}")
                return

        #self.new_item_from_str(self, item_name, input_str=None)

testReg = testRegistry()
"""
indexed view:
def items_in(container=None, *, open=None, locked=None):
    for item in self.by_location[graveyard_east]:
        if container is not None and item.container is not container:
            continue
        if open is not None and item.is_open != open:
            continue
        if locked is not None and item.is_locked != locked:
            continue
        yield item

for i in items_in(container=True, open=True):
    ...

So indexed view is definitely what I need. The duplication and even deep nesting is just going to be messy.

    """
#def init_testreg():

### Okay so I need to apply defaults first, guaranteed, then apply exceptions. I think that's why event_key is failing.


if __name__ == "__main__":
    #init_testreg()

    def get_loc_items(loc, cardinal=None):
        """
        Now currently, items are stored and they tell env_data where they live. It does make more sense to place them via location not via the item itself.

        I think I want to have a separate dict for it, like I have here in my test setup. Otherwise I have to double-back through all the items anyway to add instances
        """
        if cardinal == None:
            for cardinal in ("north", "south", "east", "west"):
                if locations[loc][cardinal].get("items"):
                    for item_name in locations[loc][cardinal]["items"]:
                        loc_item = {}
                        if test_items.get(item_name):
                            loc_item[item_name] = test_items[item_name]
                        elif gen_items.get(item_name):
                            loc_item[item_name] = gen_items.get(item_name)
                        else:
                            loc_item[item_name] = ({"item_type": [static]})

                        loc_item[item_name].setdefault("exceptions", {}).update({"starting_location": cardinal + " " + loc})
                        inst = testReg.init_single(item_name, loc_item[item_name])# definition_key, attr
                        #testReg.init_items(loc_item)# doing one at a time otherwise different loc items will overwrite

    use_generated_items(input_=None)

    for item in test_items:
        if gen_items.get(item):
           print(f"gen_items item: {gen_items.get(item)}")
           temp = {}
           temp[item] = gen_items.get(item)
           item = temp
        testReg.init_items(item)

    #get_loc_items("Graveyard")

    def print_ordered_vars(item):
        vars_dict = vars(item)

        temp_queue = dict()
        new_queue = dict()
        for item in vars_dict:
            #print(f"\033[4;35;47mItem in vars dict: {item} \033[0m")
            temp_queue[item] = vars_dict[item]

        leftovers = list(i for i in list(temp_queue) if i not in flag_keys)

        for k in leftovers:
            val = vars_dict[k]
            if isinstance(val, dict):
                new_queue[k] = True
            else:
                new_queue[k] = val

        for k in flag_keys:
            if k in temp_queue:
                new_queue[k] = temp_queue[k]

        pprint(new_queue, sort_dicts=False)
        print("\n")

        if leftovers:
            printing.print_green(leftovers)
            print("\n")


    testReg.clean_children()
    #for item in testReg.instances:
    #    print_ordered_vars(item)


    def indexed_view(included=None, excluded=None):

        def clarify(group):
            if isinstance(group, set|list|tuple):
                for flag_name in group:
                    if flag_name not in flag_keys:
                        print(f"Attribute name {flag_name} not in flag_keys. Consider adding it.")


    if testReg.confirmed_items or testReg.updated:
        printing.print_red("The following item(s) have been confirmed for future use:")

        test_generated_items = True
        if confirmed_items:
            for item in confirmed_items:
                if test_generated_items:
                    print(f"Item name: {item}")
                    printing.print_green(text=f"Item data: {vars(confirmed_items[item])}",  invert=True)
                    printing.print_red("If you want to confirm them as permanent items, please type 'yes' after the item data is printed.", invert=True)

                    test = input()
                    if test.lower() == "yes":
                        print("Item confirmed. Will add this to the permanent document.")
                        testReg.add_to_gen_items(confirmed_items[item])
                    else:
                        continue

        if testReg.updated:
            for inst in testReg.updated:
                testReg.add_to_gen_items(inst) # currently only does one at a time, would be better to batch it internally. Tomorrow.



"""
#def items_in(container=None, *, open=None, locked=None):
#    for item in self.by_location[graveyard_east]:
#        if container is not None and item.container is not container:
#            continue
#        if open is not None and item.is_open != open:
#            continue
#        if locked is not None and item.is_locked != locked:
#            continue
#        yield item
#
#for i in items_in(container=True, open=True):
#    ...
#
"""
