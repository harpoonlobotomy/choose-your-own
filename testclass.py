import uuid
from pprint import pprint

standard = "standard"
static = "static"
can_pick_up = "can_pick_up"
container = "container"
event = "event"
trigger = "trigger"

type_defaults = {
    "container": {"is_open": False, "can_be_closed": True, "can_be_locked": {"is_locked": True, "requires_key": None}},
    "can_pick_up": {"item_size": 0, "started_contained_in": None, "contained_in": None},
    "static": {"is_horizontal_surface": False, "is_vertical_surface": False, "can_examine": False, "breakable": False},
    "event": {"event": None, "event_type": {"item_triggered": {"event_key": None}}},
    "trigger": {"trigger_type": {"plot_advance": None}, "trigger_target": None, "is_exhausted": False},
    "standard": {},
    "all_items": {"starting_location": None, "current_loc": None}
}

size = "item_size"

box_desc = "It's a box. Boxy box."

descriptions = {
    "box": box_desc,
    "locked_box": box_desc,
    "cabinet": "A cabinet with something weird about it.",
    "elephant": "Big and grey and stompy."
}

test_items = {
    "box": {"item_type": set((container, can_pick_up)), "exceptions": {"can_be_locked": {}}},
    "locked_box": {"item_type": set((container, can_pick_up)), "exceptions": {"starting_location": "east graveyard"}},
    "cabinet": {"item_type": set((static, event)), "exceptions": {"event_key": "box", "trigger_target": "box"}},
    "wall": {"item_type": set((static,)), "exceptions": {"is_vertical_surface": True}},
    "elephant": {"item_type": set((standard,)), "exceptions": {size:10}}
}

locations = {"East Graveyard": {"east": {"items": ["stone ground"]}, "west": {"items": ["stone ground"]}, "north": {"items": ["stone ground", "headstones"]}, "south": {"items": ["stone ground"]}},
            "OtherPlace": {"east": {"items": None }, "west": {"items": None }, "north": {"items": None }, "south": {"items": None }},
            "Mermaid Grotto": {"east": {"items": None }, "west": {"items": None }, "north": {"items": None }, "south": {"items": None }}
            }

class testInstances:

    def __init__(self, definition_key, attr):

        #type_defaults["container"]["closed"]["locked"]
        self.id = self.id = str(uuid.uuid4())
        self.name = definition_key
        self.item_type = set(attr["item_type"])
        print(f"attr item type: {attr["item_type"]}")
        print(f"self.item_type: {self.item_type}")
        if "all_items" not in self.item_type:
            self.item_type.add("all_items")

        print(f"self.item_types: {self.item_type}, type: {type(self.item_type)}")
        for item_type in self.item_type:
            print(f"item_type: {item_type}, type: {type(item_type)}")
            for flag in type_defaults[item_type]:
                if isinstance(type_defaults[item_type][flag], dict):
                    if flag in attr["exceptions"]:
                    #f attr["exceptions"].get(flag):
                        setattr(self, flag, attr["exceptions"][flag])
                    else:
                        setattr(self, flag, type_defaults[item_type][flag])
                        for sub_flag in type_defaults[item_type][flag]:
                            if sub_flag in attr["exceptions"]:
                            #if attr["exceptions"].get(flag):
                                setattr(self, sub_flag, attr["exceptions"][sub_flag])
                            else:
                                setattr(self, sub_flag, type_defaults[item_type][flag][sub_flag])
                else:
                    if attr.get("exceptions"):
                        if flag in attr["exceptions"]:
                        #f attr["exceptions"].get(flag):
                            setattr(self, flag, attr["exceptions"][flag])
                        else:
                            setattr(self, flag, type_defaults[item_type][flag])

    def __repr__(self):
        return f"<ItemInstance {self.name} ({self.id})>"

class testRegistry:
    def __init__(self):

        self.instances = set()
        self.by_name = {}        # definition_key -> set of instance IDs
        self.standard = set() ## should these be dicts by name? Hm.
        self.containers = set() ## Maybe these categories shouldn't be here, actually. Maybe they
        self.triggers = set()
        # I can't think of a case where I'd need these to be global categories. When will I ever need  a set of all containers world-wide? anything that isn't explicitly location-based will surely have the itemInstance already...

        # so the above three are for all items in those categories, unilaterally. by_loc_cat is functionally duplicating that information but categorised into location-specific categories. I imagine that's what'll be useful in practice, eg:
        # checking if there any triggers in the scene, to check if anything needs to update (weak example)
        # checking for local open containers: self.by_loc_cat>containers>is_open
        # oh that's interesting. Expansive dict chain of location>type>is_open... Maybe. Not sure.
        self.by_loc_cat = dict()
        #self.by_loc_cat["standard"].setdefault(self.is_open, dict())  # (cardinalInstance) -> (item_type) > set of instances

#        self.by_loc_cat["east graveyard"]["container"]["open"] = "glass_jar_obj"
#        self.by_loc_cat["east graveyard"]["container"]["closed"]["locked"] = "ivory_chest"

    def init_items(self, test_items, descriptions):
        for item_name, item_entry in test_items.items():
            inst = testInstances(item_name, item_entry)
            self.instances.add(inst)
            self.by_name[inst.name] = inst

            #for item in test_items[inst.name]["exceptions"]:
            for item, v in test_items[inst.name]["exceptions"].items():
                print(f"item: {item}")
                #for k, v in item.items():
                    #itemrint(f"k: {k}, v: {v}")
                if not hasattr(inst, item):
                    print(f"item not in self: {item} / inst: {inst}")
                    setattr(inst, item, v)

            setattr(inst, "description", (descriptions.get(item_name) if descriptions.get(item_name) else f"It's a {item_name}"))


    def set_loc_cat(self, location):


        self.by_loc_cat[location] = {}
        for item_type in type_defaults:
            self.by_loc_cat[location][item_type] = {}
            #print(f"item_type: {item_type}")
            for flag in type_defaults[item_type]:
                #print(f"flag: {flag}")
                if isinstance(type_defaults[item_type][flag], dict):
                    self.by_loc_cat[location][item_type][flag]={}
                    for sub_flag in type_defaults[item_type][flag]:
                        #print(f"sub_flag: {sub_flag}")
                        self.by_loc_cat[location][item_type][flag][sub_flag] = set()#type_defaults[item_type][flag][sub_flag]
                else:
                    self.by_loc_cat[location][item_type][flag] = set()#type_defaults[item_type][flag]


testReg = testRegistry()




def init_testreg():

    for loc in locations:
        testReg.set_loc_cat(loc)


    print(testReg.by_loc_cat)

    testReg.init_items(test_items, descriptions)
    for item in testReg.instances:
        pprint(vars(item))


    print(f"test by_name: {testReg.by_name}")
    for loc in locations:
        for cardinal in locations[loc]:
            if locations[loc][cardinal].get("items"):
                for item in locations[loc][cardinal]["items"]:
                    loc_items = {}
                    if item not in testReg.by_name:
                        print(f"Item {item} not in by_name")
                        loc_items[item] = ({"item_type": [static], "exceptions": {"starting_location": cardinal + " " + loc}})
                    else:
                        print("ELSE::::")
                        if test_items.get(item):
                            loc_items[item] = test_items[item]
                        else:
                            print(f"item: {item}, type: {type(item)}")
                            inst = testReg.by_name.get(item)
                            loc_items[item] = vars(inst)
                            loc_items[item]["exceptions"] = {}

                            print(f"loc_items[item]: {loc_items[item]}")
                        loc_items[item]["exceptions"].update({"starting_location": cardinal + " " + loc})

                        print(f"exceptions: ", loc_items[item]["exceptions"])

                    testReg.init_items(loc_items, descriptions)
                    print("print vars::: ")
                    pprint(vars(testReg.by_name.get(item)))

init_testreg()
for item in testReg.instances:
    from pprint import pprint
    pprint(vars(item))
