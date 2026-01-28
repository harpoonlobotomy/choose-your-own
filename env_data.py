#env_data - the extensive writings for specific environ details

## Rules: One direction is always the exit.

#from locations import places

from logger import traceback_fn

import json
loc_data_json = "loc_data.json"
with open(loc_data_json, 'r') as loc_data_file:
    loc_dict = json.load(loc_data_file)

cardinals_list = ["north", "south", "east", "west"]
# a little section for weather. This is a weird, environment-data file. idk.
weatherdict = {
"a heatwave": {"same_weather": "Still... so... hot...", "bad_weather": True, "temp": "hot"},
"fine": {"same_weather": "Huh, it's still nice here. Nice.", "bad_weather": False, "temp": "fine"},
"perfect": {"same_weather": "Such nice weather, still!", "bad_weather": False, "temp": "fine"},
"cloudy": {"same_weather": "Are those the same clouds?", "bad_weather": False, "temp": "fine"},
"raining": {"same_weather": "I wonder if this is the same rain...", "bad_weather": True, "temp": "cold"},
"stormy": {"same_weather": "Is this storm going on forever?", "bad_weather": True, "temp": "cold"},
"a thunderstorm": {"same_weather": "I didn't know thunder went on this long.", "bad_weather": True, "temp": "cold"},
}

"""
    "template": {
        "descrip": "You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences",
        "inside":True, "electricity": True, "nature": False
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

#import random
# {random.choice(paintings)} # I don't have 'game' imported here, so I need to do this elsewhere. Can't just use 'game.painting' directly.

#   {self.n_desc} to the north. To the east is {self.e_desc}, to the south is {self.s_desc}, and to the west is {self.w_desc}."

#"overview": "{descrip}. {n_desc} to the north. To the east is {e_desc}, to the south is {s_desc}, and to the west is {w_desc}."

# n_desc is now short_desc
#loc_dict = {
##    ## Could roll for descriptions. Not always different, but would be interesting. Functionally a perception check.
##    # I could do stats... like, for looking for things etc. Actual perception checks, instead of mostly luck based.
#    "city hotel room": {"descrip": "You're in a 'budget' PPPhotel roomEEE; small but pleasant enough, at least to sleep in. The sound of traffic tells you you're a couple of floors up at least, and the carpet is well-trod", "inside":True,
#            "alt_names": ["hotel room"],
#            "electricity": True, "nature": False,
#            "north": {"short_desc": "There's a queen-size bed, simple but clean looking,",
#                      "long_desc": f"The bed looks nice enough - nothing fancy, but not a disaster either. Two pillows, a spare blanket at the foot of the bed. There's a small bedside drawer to each side, and a painting above the bed.",
#                    "actions": leave_options,},
#            "east": {"short_desc": "a television and two decent sized windows overlooking the city",
#                    "long_desc": "Against the wall is a large television, sitting between two decent sized windows overlooking the city. The curtains are drawn.", # details here depending on weather. if raining, the dried flowers are saturated and heavy. If sunny, they're crispy, etc. Not close to implementing that yet.
#                    "actions": None,},
#            "south": {"short_desc": "a door, likely to a bathroom",
#                      "long_desc": "There's a door, lightly sun-yellowed. Nondescript; fair to assume it's a bathroom door.",
#                    "actions": None},
#            "west": {"short_desc": "the door out of the room, likely to the hallway",
#                    "long_desc": "There's a standard hotel room door, with the fire escape route poster on the back and an empty coat hook.",
#                    "actions": None},
#            "exitwall": "west",
#            },
#
#    "forked tree branch": {"descrip": "You've climbed up a gnarled old tree to a PPPforked tree branchEEE, and found a relatively safe place to sit in its broad branches.", "inside":False,
#            "alt_names": ["gnarled old tree", "forked branch"],
#            "electricity": False, "nature": True,
#            "north": {"short_desc": "The northern tree parts are ",
#                "long_desc": "This is the north part of a tree...",
#                "actions": leave_options,
#                },
#            "east": {"short_desc": "an eastern tree part",
#                "long_desc": "This is the east of a forked tree. Not sure what's here. Maybe a bird's nest..", # details here depending on weather. if raining, the dried flowers are saturated and heavy. If sunny, they're crispy, etc. Not close to implementing that yet.
#                "east_actions": None,
#                },
#            "south": {"short_desc": "a southern tree part",
#                "long_desc": "South of a tree. Should probably be the exit.",
#                "actions": None,
#                },
#            "west": {
#                "short_desc": "what looks like a a western tree part",
#                "long_desc": "West of the tree. Maybe a very nice view...",
#                "actions": None
#                },
#            "exitwall": "north",
#            },
#
#    "graveyard": {
#        "descrip": "You see a rather poorly kept PPPgraveyardEEE - smaller than you might have expected given the scale of the gate and fences",
#        "inside": False, "electricity": False, "nature": True,
#        "north": {"short_desc": "The entrance gates are",
#                "long_desc": "You think you could leave through the large wrought-iron gates to the north. They're imposing but run-down; this graveyard doesn't get as much love as it could.",
#                "long_desc_dict": {"generic" : "There's a high fence surrounding the hallowed ground, heavy wrought-iron keeping the spirits in.", "gate": "large wrought-iron [[]],  imposing but run-down,", "padlock": "an old dark-metal [[]] on a chain holding the gate closed."},
#                ## NOTE: Add text for 'is not present' somewhere. The alt text for when things change.
#                "actions": leave_options,
#                },
#        "east": {"short_desc": "a variety of headstones",
#                "long_desc": "You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, with dried flowers left long ago.", # details here depending on weather. if raining, the dried flowers are saturated and heavy. If sunny, they're crispy, etc. Not close to implementing that yet.
#                "long_desc_dict": {"generic" :"You see a variety of headstones, most quite worn and decorated by ",
#                              "moss": "clumps of [[]]",
#                              "glass jar": f"a [[]] being used as a vase in front of one of the headstones",
#                              "dried flowers": "some [[]] left long ago"},
#                "east_actions": None,
#                },
#        "south": {"short_desc": "a mausoleum",
#                "long_desc": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
#                "actions": None,
#                },
#        "west": {
#                "short_desc": "what looks like a work shed of some kind",
#                "long_desc": "There's a work shed, with a wheelbarrow outside and a large padlock on the door.",
#                "actions": None
#                },
#        "exitwall": "north",
#            },
#    "pile of rocks": {
#        "descrip": "PPPPile of rocksEEE.",
#        "inside": False, "electricity": False, "nature": True,
#        "north": {"short_desc": "The",
#                "long_desc": "You",
#                },
#        "east": {"short_desc": "a",
#                "long_desc": "You",
#                },
#        "south": {"short_desc": "a",
#                "long_desc": "There",
#                },
#        "west": {
#                "short_desc": "what",
#                "long_desc": "There",
#                },
#        "exitwall": "north",
#            },
#    "shrine": {
#        "descrip": "Sheltered from the rain you see a small PPPshrineEEE, built into the underhang of a cliff face.",
#        "inside": False, "electricity": False, "nature": True,
#        "north": {"short_desc": "A wooden shrine, with aged fabric flags and various trinkets",
#                "long_desc": "The shrine itself is fragile looking, with candles still not burnt down entirely.",# There are scrolls on the main surface, and two jars; one on the desk, and the other on the ground beside it.",
#                },
#        "east": {"short_desc": "a small 'interior' wall of the underhang",
#                "long_desc": "The underhang's east wall is damp with spray from the waterfall outside, but otherwise unremarkable",
#                },
#        "south": {"short_desc": "open air",
#                "long_desc": "The sky and fields beyond; nothing much to do here except leave.",
#                },
#        "west": None,
#        "exitwall": "south",
#            }
#        }
#
global all_cardinals
all_cardinals = set()
import uuid

class cardinalInstance:
    def __init__(self, cardinal, loc):
        from testing_coloured_descriptions import format_descrip
        self.id = str(uuid.uuid4())
        self.name = cardinal # "east"
        self.place_name = cardinal + " " + loc.name # eg "east graveyard"        },
        self.ern_name = cardinal + "ern " + loc.name # eg "eastern graveyard"
        self.in_loc_facing_card = f"the {loc.name}, facing {self.name}"
        self.place = loc
        self.alt_names = (loc_dict[loc.name].get("alt_names") if loc_dict[loc.name].get("alt_names") else None)
        #self.short_desc = (loc_dict[loc.name][cardinal].get("short_desc") if loc_dict[loc.name].get(cardinal) else None)
        #self.description = format_descrip(d_type="item_desc", location=loc, cardinal=cardinal)#None#(loc_dict[loc.name][cardinal].get("long_desc") if loc_dict[loc.name].get(cardinal) else None)
        self.colour = None

        self.cardinal_data = loc_dict[self.place.name].get(cardinal)
        self.missing_cardinal = loc_dict[self.place.name].get("missing_cardinal")
        setattr(self, cardinal, self.cardinal_data)

        self.cardinal_actions = (loc_dict[self.place.name][cardinal].get("actions") if loc_dict[self.place.name].get(cardinal) else None)
        if not self.cardinal_actions or self.cardinal_actions == None:
            self.cardinal_actions = leave_options

        self.by_placename = {}
        all_cardinals.add(self)

    def __repr__(self):
        return f"<cardinalInstance {self.place_name} ({self.id})>"

class placeInstance:

    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.a_name = "a " + name
        self.the_name = "the " + name
        self.alt_names = {}
        self.visited = False
        self.first_weather = None
        self.description = None#loc_dict.get(name, {}).get("descrip")
        #print(f"self.description: {self.description}\n")
        self.current_loc = None
        self.colour = None ## assign like items on first
        self.cardinals = {}

        for attr, value in loc_dict.get(name, {}).items():
            if attr == "alt_names":
                continue

            else:
                setattr(self, attr, value)

        for attr in ("inside", "electricity", "nature"):
            value = loc_dict[name].get(attr)
            setattr(self, attr, value) # might work?

    #def set_scene_descrip(self, name, loc):
    #    ## place.set_scene_descrip(name, place) ## <- calls here
    #    if loc_dict[name].get("descrip"):
    #        from misc_utilities import assign_colour
    #    ## I need to amend this for whether each part exists or not...
    #        if self.cardinals.get("west").short_desc != None: # hardcoded for the moment. TODO: Make this dynamic. Or I guess account for any missing version? But better if it's dynamic. Maybe a check for how many parts there are and then generate based on that?
    #            self.overview = f"{loc_dict[name]["descrip"]}.{"\033[0m"} \n{self.cardinals["north"].short_desc} to the {assign_colour("north")}. To the {assign_colour("east")} is {self.cardinals["east"].short_desc}, to the {assign_colour("south")} is {self.cardinals["south"].short_desc}, and to the {assign_colour("west")} is {self.cardinals["west"].short_desc}."
    #        else:
    #            self.overview = f"{loc_dict[name]["descrip"]}.{"\033[0m"} \n{self.cardinals["north"].short_desc} to the {assign_colour("north")}. To the {assign_colour("east")} is {self.cardinals["east"].short_desc}, and to the {assign_colour("south")} is {self.cardinals["south"].short_desc}."
    #        return self.overview

    def visit(self):
        self.visited = True

    def __repr__(self):
        return f"<placeInstance {self.name} ({self.id})>"

class placeRegistry:

    def __init__(self):

        self.places = set()
        self.by_name = {}
        self.by_alt_name = {}
        self.route = list() # store everywhere you go for a game, in order. Could be interesting to use later.
        self.last_loc = None # used for history tracking, just track place, not card.
        self.cardinals = {} # locRegistry.cardinals[place_instance_obj][cardinal_direction_str]
        self.current = None # Not sure if I want to use this, or keep it in game.facing_direction. This might make more sense, keep it centralised? Not sure.
        self.currentPlace = None

    def add_cardinals(self, locationInstance):
        cardinals_dict = dict()

        for card in cardinals_list:
            cardinal_inst = cardinalInstance(card, locationInstance)
            cardinals_dict[card] = cardinal_inst

        locationInstance.cardinals=cardinals_dict

        # placeInstance.name = {"south": southInstance, "north": northInstance, etc}
        return cardinals_dict

    def set_current(self, loc=None, cardinal=None):
        #print(f"set current: loc: {loc}, cardinal: {cardinal}")

        if loc and cardinal:
            if isinstance(loc, placeInstance) and isinstance(cardinal, cardinalInstance):
                if loc != cardinal.place:
                    print(f"Trying to set location to {loc.name} and cardinal to {cardinal.place_name}; this doesn't work...")
                    traceback_fn()
                    return

                self.current = cardinal
                self.currentPlace = loc
                if cardinal.place != self.currentPlace:
                    self.currentPlace = cardinal.place
                    self.route.append(loc)
                #print(f"Set self.current to {cardinal}, self.currentPlace to {loc}")
                return

        if loc:
            if isinstance(loc, str):
                loc_test = self.by_name[loc]
                if isinstance(loc_test, placeInstance):
                    loc = loc_test
                else:
                    print(f"Failed to find instance for {loc}")
                    traceback_fn()

            if isinstance(loc, placeInstance) and not cardinal:
                self.currentPlace = loc
                if not self.current:
                    print("No current_cardinal, defaulting to 'south'.")
                    current_card = "south"
                else:
                    current_card = self.current.name
                new_card = self.cardinals[self.currentPlace][current_card]
                self.current = new_card
                #print(f"loc.name: {loc.name}")
                self.currentPlace = loc
                #print("self.current: ", self.current)
                self.route.append(loc)

            if isinstance(loc, cardinalInstance):
                self.current = loc
                if loc.place != self.currentPlace:
                    self.currentPlace = loc.place
                    self.route.append(loc)

            assert isinstance(self.current, cardinalInstance)
            return
                #print(f"self.current_cardinal set to {loc.name}")

        if cardinal:
            if isinstance(cardinal, str):
                cardinal = self.cardinals[self.currentPlace][cardinal]

            if isinstance(cardinal, cardinalInstance):
                #print(f"before setting current: cardinal.name: {cardinal.place_name}")
                self.current = cardinal
                if cardinal.place != self.currentPlace:
                    self.currentPlace = cardinal.place
                    self.route.append(cardinal.place)
                self.current = cardinal
                #print("self.current_cardinal.name: ", cardinal.place_name)

    def place_by_name(self, loc_name):

        #print(f"Loc name in place_by_name: {loc_name}")
        loc_inst = self.by_name.get(loc_name.lower())
        if not loc_inst:
            loc_inst = self.by_alt_name.get(loc_name)

        if isinstance(loc_inst, placeInstance):
            #print(f"loc_inst in place_by_name: {loc_inst}")
            #print(f"loc_inst.name in place_by_name: {loc_inst.name}")
            return loc_inst

        print(f"self.by_name: {self.by_name}")
        print(f"by_alt_name: {self.by_alt_name}")
        print(f"LOC INST: {loc_inst}, type: {type(loc_inst)}")
        print(f"Failed to get placeInstance for {loc_name}. Please investigate. Exiting from env_data.")
        exit()

    def show_name(self, loc, text=""):
        if text and text != "":
            print(text)
        if isinstance(loc, placeInstance):
            print(f"Instance: {loc}")
            print(f"Name: {loc.name}")
            if loc == self.currentPlace:
                print("NOTE: is current place.")
            else:
                print("NOTE: is not current place.")
        else:
            print("[Is not an instance.]")
            print(loc)


    def by_cardinal_str(self, cardinal_str:str|dict, loc=None) -> cardinalInstance:

        if isinstance(cardinal_str, dict):
            loc, cardinal_str = next(iter(cardinal_str.items()))
        elif isinstance(cardinal_str, str):
            if " " in cardinal_str:
                [loc, cardinal_str2] = cardinal_str.rsplit(" ", 1)
                if not self.by_name.get(loc):
                    [cardinal_str2, loc] = cardinal_str.split(" ", 1)
                cardinal_str = cardinal_str2


        if loc == None:
            loc = self.currentPlace
        elif isinstance(loc, str):
            loc = self.place_by_name(loc)

        #print(f"by cardinal str: cardinal_str: {cardinal_str}, loc: {loc}")
        cardinal_inst = locRegistry.cardinals[loc][cardinal_str]
        return cardinal_inst

    #def get_card_inst_from_strings(self, location): ## by_cardinal_str instead! I don't think anything else called this.
#
    #    if not isinstance(location, cardinalInstance):
    #        location_str, card_str = next(iter(location.items())) # strings from dict
    #        place = self.place_by_name(location_str)
    #        cardinal_inst = self.by_cardinal_str(cardinal_str=card_str, loc=place)
    #    else:
    #        cardinal_inst = location
#
    #    return cardinal_inst


locRegistry = placeRegistry()

def add_new_loc(name, reset_current=True):

    place = placeInstance(name)

    if loc_dict[name].get("alt_names"):
        #print(f"loc_dict[name] for {name} has alt names: {loc_dict[name].get("alt_names")}")
        for altname in loc_dict[name]["alt_names"]:
            locRegistry.by_alt_name[altname]=place
    locRegistry.places.add(place)
    locRegistry.by_name[name] = place
    #print(f"loc_dict[name]::::: {loc_dict[name]}")

    locRegistry.cardinals[place] = locRegistry.add_cardinals(place)
    ## add cardinals to place instance so it's directly referable.
    #cardinals_dict = {}
    #for card in cardinals_list:
    #    cardinal_inst = cardinalInstance(card, place)
    #    cardinals_dict[card] = cardinal_inst
    #place.cardinals=cardinals_dict
    if reset_current:
        locRegistry.set_current(place)

def initialise_placeRegistry():

    for name in loc_dict.keys():
        add_new_loc(name)

        #place.set_scene_descrip(name, place)

def get_descriptions(place):

    from testing_coloured_descriptions import loc_descriptions
    description_dict = loc_descriptions(place) ## now for now I might do this once and reuse it, but practically, we want to regenerate it at each call in case something's changed. For now just implementation is a fine goal.
    place.overview = description_dict.get(place.name).get("overview")
    if not isinstance(place.overview, str):
        place.overview = list(place.overview)[0]
    if not place.overview:
        #print(f"SELF OVERVIEW IN ENV_DATA: {place.overview}")
    #else:
        print("Failed to get self.overview.")
        print(f"Did this part work at least? ``{description_dict.get(place.name)}``")
    #print(f"place.overview::::: {place.overview}")
    CARDINALS = ["north", "east", "south", "west"]
    for card in CARDINALS:
        if locRegistry.cardinals[place].get(card) and isinstance(locRegistry.cardinals[place].get(card), cardinalInstance):
            card_inst = locRegistry.cardinals[place].get(card)
            card_inst.description = description_dict[place.name].get(card)
            #print(f"Card inst description {place.name}, {card}: {card_inst.description}")
            #print(f"VARS: \n{vars(card_inst)}\n\n")
            #print(f"PLACE VARS: {vars(place)}")

def get_loc_descriptions(place=None):
    if place == None:
        for place in locRegistry.places:
            #print(f"PLACE IN PLACES : {place}")
            get_descriptions(place)
    elif place and isinstance(place, placeInstance):
        get_descriptions(place)
    elif place and isinstance(place, str):
        place - locRegistry.place_by_name(place)
        get_descriptions(place)



if "__main__" == __name__:

    initialise_placeRegistry()
    get_loc_descriptions()
    locRegistry.set_current("graveyard")
    #place = locRegistry.place_by_name("graveyard")

    #place_cardinals = locRegistry.cardinals[place]

    #print(place_cardinals["east"].place_name)
    #place = place_cardinals["east"].place
    #print(place.name)
    #print("place.cardinals['north'].long_desc: ", place.cardinals["north"].long_desc)
    #print(place.overview)
