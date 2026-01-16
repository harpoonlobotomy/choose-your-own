import uuid
from pprint import pprint

standard = "standard"
static = "static"
can_pick_up = "can_pick_up"
container = "container"
event = "event"
trigger = "trigger"

type_defaults = { # gently ordered - will overwrite earlier attrs with later ones (eg 'is horizontal surface' for flooring with overwrite 'static''s.)
    "standard": {},
    "static": {"is_horizontal_surface": False, "is_vertical_surface": False, "can_examine": False, "breakable": False},
    "all_items": {"starting_location": None, "current_loc": None},
    "container": {"is_open": False, "can_be_closed": True, "can_be_locked": {"is_locked": True, "requires_key": None}},
    "can_pick_up": {"item_size": 0, "started_contained_in": None, "contained_in": None},
    "event": {"event": None, "event_type": {"item_triggered": {"event_key": None}}},
    "trigger": {"trigger_type": {"plot_advance": None}, "trigger_target": None, "is_exhausted": False},
    "flooring": {"is_horizontal_surface": True}
}

size = "item_size"

box_desc = "It's a box. Boxy box."

descriptions = {
    "box": box_desc,
    "locked box": box_desc,
    "cabinet": "A cabinet with something weird about it.",
    "elephant": "Big and grey and stompy."
}

test_items = {
    "box": {"item_type": set((container, can_pick_up)), "exceptions": {"can_be_locked": False}},
    "locked box": {"item_type": set((container, can_pick_up)), "exceptions": {}},#"starting_location": "east graveyard"}},
    "cabinet": {"item_type": set((static, event)), "exceptions": {"event_key": "box", "trigger_target": "box"}},
    "wall": {"item_type": set((static,)), "exceptions": {"is_vertical_surface": True}},
    "elephant": {"item_type": set((standard,)), "exceptions": {size:10}},
    "stone ground": {"item_type": set((static, "flooring")), "exceptions": {}}
}

## Do I want "exceptions": {"is_vertical_surface": True}
#or
#"item_type": set((static, "flooring") ??

locations = {"Graveyard": {"east": {"items": ["stone ground"]}, "west": {"items": ["stone ground"]}, "north": {"items": ["stone ground"]}, "south": {"items": ["stone ground"]}}, #, "headstones"
            "OtherPlace": {"east": {"items": None }, "west": {"items": None }, "north": {"items": None }, "south": {"items": None }},
            "Mermaid Grotto": {"east": {"items": None }, "west": {"items": None }, "north": {"items": None }, "south": {"items": None }}
            }

class testInstances:

    def __init__(self, definition_key, attr):

        #type_defaults["container"]["closed"]["locked"]
        self.id = self.id = str(uuid.uuid4())
        self.name = definition_key
        self.item_type = set(attr["item_type"])
        self.starting_location = None
        #print(f"attr item type: {attr["item_type"]}")
        #print(f"self.item_type: {self.item_type}")
        if "all_items" not in self.item_type:
            self.item_type.add("all_items")
        if test_items.get(self.name):
            item_types = test_items[self.name].get("item_type")
            for cat in item_types:
                if cat not in self.item_type:
                    self.item_type.add(cat)

        for item_type in type_defaults:
            if item_type in self.item_type:
        #print(f"self.item_types: {self.item_type}, type: {type(self.item_type)}")
        #for item_type in self.item_type:
                print(f"\n\n Item type: {item_type} for item {self.name}, id: {self.id}")
                #print(f"item_type: {item_type}, type: {type(item_type)}")
                for flag in type_defaults[item_type]:
                    print(f"\nFLAG: {flag}\n")
                    if isinstance(type_defaults[item_type][flag], dict):
                        if flag in attr["exceptions"]:
                        #f attr["exceptions"].get(flag):
                            setattr(self, flag, attr["exceptions"][flag])
                        else:
                            if flag == "exceptions":
                                print(f"Flag == exceptions and is a dict: {flag}")
                            else:
                                setattr(self, flag, type_defaults[item_type][flag])
                            for sub_flag in type_defaults[item_type][flag]:
                                if sub_flag in attr["exceptions"]:
                                #if attr["exceptions"].get(flag):
                                    setattr(self, sub_flag, attr["exceptions"][sub_flag])
                                else:
                                    setattr(self, sub_flag, type_defaults[item_type][flag][sub_flag])
                    else:
                        if flag == "exceptions":
                            print("Flg == exceptions")
                        elif attr.get("exceptions"):
                            if flag in attr["exceptions"]:
                                print(f"FLAG IN GET(EXCEPTIONS) not dict: {flag}")
                                print("attr['exceptions'][flag]: ", attr["exceptions"][flag])
                            #f attr["exceptions"].get(flag):
                                #if not flag == "starting_location":
                                #new_text = ( + "WOO" if isinstance(attr["exceptions"][flag], str) else attr["exceptions"][flag])
                                setattr(self, flag, attr["exceptions"][flag])
                                print(f"After setattr(self, flag, attr['exceptions'][flag] for  {self}: ", getattr(self, flag))
                            else:
                                setattr(self, flag, type_defaults[item_type][flag])
                        else:
                            #if not hasattr(self, flag):
                            #    setattr(self, flag, type_defaults[item_type][flag])
                            if item_type == "all_items" and flag == "starting_location": ## manually keep the location for location-based items when it might be overwritten by types otherwise. This is a bad solution though because why is it overwriting types anyway?  Or right, because it can't differentiate between types-data and inserted data.
                                # Oh, that's the advantage of using the exceptions. Yeah that makes sense why I put that in now. Okay. I can't use the exceptions for starting location though, can I?
                                #I mean why not.  Okay. Will look into it.
                                setattr(self, flag, attr[flag])

                            else:
                                setattr(self, flag, type_defaults[item_type][flag]) ## So with this we jsut overwrite in this case. So if I have two categories  that overwrite each other, this is where it does that (ie flooring overwrites the )

        print(f"INSTANCE CREATED: {self}")

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

        def init_single(item_name, item_entry):
            inst = testInstances(item_name, item_entry)
            self.instances.add(inst)
            self.by_name[inst.name] = inst

            #for item in test_items[inst.name]["exceptions"]:
            #print(f"test_items[inst.name]: {test_items[inst.name]}")
            #for item, v in test_items[inst.name].items():
            #    if item == "starting_location" or item == "exceptions":
            ##        print("item == starting location")
            #        continue
            #    if not hasattr(inst, item):
            #        setattr(inst, item, v)

            setattr(inst, "description", (descriptions.get(item_name) if descriptions.get(item_name) else f"It's a {item_name}"))

        if isinstance(test_items, dict):
            for item_name, item_entry in test_items.items():
                init_single(item_name, item_entry)

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
"""
# So I've just realised that these:
self.by_loc_cat[location][item_type][flag][sub_flag] = set()
never get populated.
So need to write a new function to add them in.
It can't be done at init, because the location data is a separate pass.
So, init all items, once done, init items to locations, then at that step add them to the relevant sets.
If relevant_tag != None, add the item to that set.
Is there any reason to only add them to end sequence?
As in,

if I have self.by_loc_cat[graveyard_east][container][closed][locked]
is there any reason not to add "ivory jar" to each of those that is true?
Right now those containers are just dicts with the end of the chain being sets, but I could just add "items: set()" to each dict level and add the item to each layer.

So instead of "ivory jar" being only in
self.by_loc_cat[graveyard_east][container][closed][locked].add(ivory_jar)
if would be
self.by_loc_cat[graveyard_east]["items"].add(ivory_jar)
self.by_loc_cat[graveyard_east][container]["items"].add(ivory_jar)
self.by_loc_cat[graveyard_east][container][closed]["items"].add(ivory_jar)
self.by_loc_cat[graveyard_east][container][closed][locked]["items"].add(ivory_jar)

Because there'll be times when I need all containers, or all closed (whether locked or not), etc.
But this seems extremely wasteful, especially at scale.

Perhaps there's a straightforward way to pull all children from all subsequent depths. So 'get all children of anything below graveyard_east/container'. Hm.

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
def init_testreg():

    #for loc in locations:
    #    testReg.set_loc_cat(loc)


    #print(testReg.by_loc_cat)

    #testReg.init_items(test_items, descriptions)
    #for item in testReg.instances:
        #pprint(vars(item))

    return
    #print(f"test by_name: {testReg.by_name}")
    for loc in locations:
        if loc != "Graveyard":
            continue
        for cardinal in locations[loc]:
            print(f"\n\nCARDINAL:: {cardinal}\n\n\n")
            if locations[loc][cardinal].get("items"):

                for item in locations[loc][cardinal]["items"]:
                    loc_items = {}
                    print(f"ITEM: {item}, cardinal/loc: {cardinal + " " + loc}")
                    #if item not in testReg.by_name:
                        #print(f"Item {item} not in by_name")
                    if not test_items.get(item):
                        loc_items[item] = test_items[item]
                    else:
                        loc_items[item] = ({"item_type": [static]})

                    if loc_items[item].get("exceptions"):
                        loc_items[item]["exceptions"].update({"starting_location": cardinal + " " + loc})
                    else:
                        loc_items[item]["exceptions"] = {"starting_location": cardinal + " " + loc}

                    #print(f"[NOT IN by_name: loc_items[item]: {loc_items[item]}")
                    #else:
                    #    #print("ELSE::::")
#
                    #    else:
                    #        #print(f"item: {item}, type: {type(item)}")
                    #        inst = testReg.by_name.get(item)
                    #        loc_items[item] = vars(inst)
                    #        loc_items[item]["exceptions"] = {}
#
                    #    if not loc_items[item].get("exceptions"):
                    #        loc_items[item]["exceptions"] = {}
                    #    loc_items[item]["exceptions"].update({"starting_location": cardinal + " " + loc})
                    #    loc_items[item]["starting_location"] = cardinal + " " + loc
                    #    loc_items[item].pop("id")
                    #    print(f"Found in by_name: loc_items[item]: {loc_items[item]}")


                    testReg.init_items(loc_items, descriptions)
if __name__ == "__main__":
    init_testreg()

    def get_loc_items(loc, cardinal=None):

        if cardinal == None:
            for cardinal in ("north", "south", "east", "west"):
                if locations[loc][cardinal].get("items"):
                    for item in locations[loc][cardinal]["items"]:
                        loc_items = {}
                        print(f"ITEM: {item}, cardinal/loc: {cardinal + " " + loc}")
                        if test_items.get(item):
                            loc_items[item] = test_items[item]
                        else:
                            loc_items[item] = ({"item_type": [static]})
                        loc_items[item]["starting_location"] = cardinal + " " + loc
                        testReg.init_items(loc_items, descriptions)

    get_loc_items("Graveyard")

    for item in testReg.instances:
        if item.name == "stone ground":
            #print(f"ITEM: {item.name}")
            from pprint import pprint
            pprint(vars(item))
            #exit()
"""
ITEM: stone ground
{'breakable': False,
 'can_examine': False,
 'current_loc': None,
 'description': "It's a stone ground",
 'exceptions': {'starting_location': 'south Graveyard'},
 'id': 'f17b9c4f-6c49-43ed-bd98-133fae7d1852',
 'is_horizontal_surface': False,
 'is_vertical_surface': False,
 'item_type': {'all_items', 'static'},
 'name': 'stone ground',
 'starting_location': 'north Graveyard'}

vs

ITEM: stone ground
{'description': "It's a stone ground",
 'exceptions': {},
 'id': 'f5641b8e-7e5d-4f74-a976-1da7c0810680',
 'item_type': {'static', 'all_items'},
 'name': 'stone ground',
 'starting_location': 'south Graveyard'}
"""
