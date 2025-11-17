# locations - location management + setup

# should remove descriptions from here and just get them from end_data.
# Trouble is I can't import env_data here, because then it gets  recursive and angry.

descriptions = { # just going to pick 3 and do those first.
    #"your home": {"description": "It's a house. It's okay.", "inside": True,
    #    "electricity": True, "nature": False, "details": place_data.your_home},
    #"the city centre": {"description": None, "inside":False,
    #    "electricity": True, "nature": False, "details": },
       "a city hotel room": {"description": None, "inside":True,
            "electricity": True, "nature": False, "parent": "the city centre"},#, "details": place_data.a_city_hotel_room},
    #    "park": {"description": None, "inside":False,
    #        "electricity": False, "nature": True, "details": },
    #"a small town": {"description": None, "inside": False,
    #    "electricity": True, "nature": False, "details": },
    #    "hotel": {"description": None, "inside": True,
    #        "electricity": True, "nature": False, "details": },
    #    "park": {"description": None, "inside":True,
    #        "electricity": False, "nature": True, "details": },
    #    "the back alley": {"description": None, "inside":False,
    #        "electricity": False, "nature": False, "details": },
    #"the nature reserve": {"description": None, "inside": False,
    #    "electricity": False, "nature": True, "children": ["ranger station", "up a tree", "temporary shelter"], "details": },
    #    "ranger station": {"description": None, "inside":True,
    #        "electricity": True, "nature": False, "details": },
        "a forked tree branch": {"description": None, "inside":False,
            "electricity": False, "nature": True, "parent": "the nature reserve"},#, "details": place_data.up_a_tree},
        #"temporary shelter": {"description": None, "inside":True,
        #    "electricity": False, "nature": True, "details": },
    #"a hospital": {"description": None, "inside":True,
    #    "electricity": True, "nature": False, "details": },
    #"a friend's house": {"description": None, "inside": True,
    #    "electricity": True, "nature": False, "details": },
    "a graveyard": {"description": None, "inside":False,
        "electricity": False, "nature": False, "parent": None}#, "details": place_data.a_graveyard}
}

template2 = { # the full layout, not currently in use.
    "your home": {
    },
    "the city centre": {
        "a hotel": {},
        "a park": {},
        "a back alley": {}
    },
    "a small town": {
        "a hotel": {},
        "a park": {}
    },
    "a nature reserve": {
        "a ranger station": {},
        "a forked tree branch": {},
        "a temporary shelter": {}
    },
    "a hospital": {},
    "a friend's house": {},
    "a graveyard": {}
    }

template = {
    "a graveyard": {},
    "a city hotel room": {},
    "a forked tree branch": {}
}

class Place: # had a lot of help with this part. Barely understand classes yet.
    def __init__(self, name):
        self.name = name
        self.visited = False
        self.items = []
        self.first_weather = None
        for attr, value in descriptions.get(name, {}).items():
            setattr(self, attr, value)
        else:
            self.description = f"What is there to say about {name}? Not much, really."
        self.sub_places = {} # does having it like this mean it'll wipe every time I access it?

    def visit(self):
        self.visited = True

    def add_item(self, item):
        self.items.append(item)

def build_places(template):
    places = {}
    for name, subdict in template.items():
        if name in ("inside"):
            continue
        place = Place(name)
        # Recursively build sub-places
        place.sub_places = build_places(subdict)
        places[name] = place
        #place.description = env_data.dataset.get(name)
    return places

def run_loc():
    places = build_places(template)
    return places

places = run_loc()
#places = {}
#nature_reserve = Place("The Nature Reserve", container=places)
#Place("Ranger Station", container=nature_reserve.sub_places)
#Place("Up a Tree", container=nature_reserve.sub_places)

#nature_reserve = Place("The Nature Reserve")
#nature_reserve.sub_places["ranger station"] = Place("Ranger Station")
#nature_reserve.sub_places["up a tree"] = Place("Up a Tree")
#nature_reserve.sub_places["temporary shelter"] = Place("Temporary Shelter")


