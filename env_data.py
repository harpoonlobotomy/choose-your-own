#env_data - the extensive writings for specific environ details

## Rules: One direction is always the exit.

from locations import places

# a little section for weather. This is a weird, environment-data file. idk.
weatherdict = {
"fine": {"same_weather": "Huh, it's still nice here. Nice.", "bad_weather": False, "temp": "fine"},
"stormy": {"same_weather": "Is this storm going on forever?", "bad_weather": True, "temp": "cold"},
"thunderstorm": {"same_weather": "I didn't know thunder went on this long.", "bad_weather": True, "temp": "cold"},
"raining": {"same_weather": "I wonder if this is the same rain...", "bad_weather": True, "temp": "cold"},
"a heatwave": {"same_weather": "Still... so... hot...", "bad_weather": True, "temp": "hot"},
"perfect": {"same_weather": "Such nice weather, still!", "bad_weather": False, "temp": "fine"},
"cloudy": {"same_weather": "Are those the same clouds?", "bad_weather": False, "temp": "fine"}
}

"""
    "template": {
        "descrip": "You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences",
        "n_desc": "The entrace gates are",
        "e_desc": "a variety of headstones",
        "s_desc": "a mausoleum",
        "w_desc": "what looks like a work shed of some kind",

        "exitwall": "north",

        "north": "You can leave through the large wrought-iron gates to the north. They're imposing but run-down; this cemetary doesn't get as much love as it could.",
        "north_weird": "You can leave through the large wrought-iron gates to the north. They're imposing - creaking constantly, and they seem to loom over you even from a distance.",
        "north_actions": leave_options,

        "south": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
        "south_weird": None,
        "south_actions": None,

        "east": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
        "east_weird": None,
        "east_actions": None,

        "west": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
        "west_weird": None,
        "west_actions": None
    }
"""



leave_options = str("'leave', 'stay', preamble='Do you want to leave, or stay?'")


dataset = {
    "a city hotel room": {"description": None, "inside":True,
            "electricity": True, "nature": False},

    "a forked tree branch": {"description": None, "inside":False,
            "electricity": False, "nature": True},

    "a graveyard": {
        "descrip": "You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences",
        "n_desc": "The entrace gates are",
        "e_desc": "a variety of headstones",
        "s_desc": "a mausoleum",
        "w_desc": "what looks like a work shed of some kind",
        "exitwall": "north",
        "north": "You can leave through the large wrought-iron gates to the north. They're imposing but run-down; this graveyard doesn't get as much love as it could.",
        "north_weird": "You can leave through the large wrought-iron gates to the north. They're imposing - creaking constantly, and they seem to loom over you even from a distance.",
        "north_actions": leave_options,
        "south": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
        "south_weird": None,
        "south_actions": None,
        "east": "You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, dried flowers left long ago.", # details here depending on weather. if raining, the dried flowers are saturated and heavy. If sunny, they're crispy, etc.
        "east_weird": None,
        "east_actions": None,
        "west": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
        "west_weird": None,
        "west_actions": None
    }
}
#"overview": "{descrip}. {n_desc} to the north. To the east is {e_desc}, to the south is {s_desc}, and to the west is {w_desc}."

class place_data:

    def __init__(self, name):
        self.name = name

        for attr, value in dataset.get(name, {}).items():
            #print(f"name: {name}, attr: {attr}, value: {value}")
            setattr(self, attr, value)
        if dataset[name].get("descrip"):
            self.overview = f"{dataset[name]["descrip"]}.\n \n{self.n_desc} to the north. To the east is {self.e_desc}, to the south is {self.s_desc}, and to the west is {self.w_desc}."

        for cardinal in ("north", "south", "east", "west"):
            cardinal_data = dataset[name].get(cardinal)
            w_cardinal = dataset[name].get(cardinal + "_weird") # I need to figure out a better way of implementing the 'weird' things. Or just not implement it at all. Or always implement it. Why even allow for it not to be weird? I'm still of mixed minds on that. For now it's broadly ignored while I set up the basics. Maybe should just put it on hold for now until the structure's built up more. idk.
            if w_cardinal == None:
                w_cardinal = cardinal_data
                setattr(self, cardinal + "_weird", w_cardinal)
            setattr(self, cardinal, cardinal_data)
            cardinal_actions = dataset[name].get(cardinal + "_actions")
            if not cardinal_actions or cardinal_actions == None:
                cardinal_actions = leave_options # use the defaults if none.

def placedata_init():
    p_data = {}
    for name in places.keys():
        place = place_data(name)
        p_data[name] = place
    return p_data

#from locations import run_loc
#from pprint import pprint
#places = run_loc()
p_data = placedata_init()

#print(p_data["a graveyard"].north)
