#env_data - the extensive writings for specific environ details

## Rules: One direction is always the exit.

#from locations import places

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
loc_dict = {
    ## Could roll for descriptions. Not always different, but would be interesting. Functionally a perception check.
    # I could do stats... like, for looking for things etc. Actual perception checks, instead of mostly luck based.
    "city hotel room": {"descrip": "You're in a 'budget' hotel room; small but pleasant enough, at least to sleep in. The sound of traffic tells you you're a couple of floors up at least, and the carpet is well-trod", "inside":True,
            "electricity": True, "nature": False,
            "north": {"short_desc": "There's a queen-size bed, simple but clean looking,",
                      "long_desc": f"The bed looks nice enough - nothing fancy, but not a disaster either. Two pillows, a spare blanket at the foot of the bed. There's a small bedside drawer to each side, and a painting above the bed.",
                    "weird": "You think you could leave through the large wrought-iron gates to the north. They're imposing - creaking constantly, and they seem to loom over you even from a distance.",
                    "actions": leave_options,},
            "east": {"short_desc": "a television and two decent sized windows overlooking the city",
                    "long_desc": "Against the wall is a large television, sitting between two decent sized windows overlooking the city. The curtains are drawn.", # details here depending on weather. if raining, the dried flowers are saturated and heavy. If sunny, they're crispy, etc. Not close to implementing that yet.
                    "weird": None,
                    "actions": None,},
            "south": {"short_desc": "a door, likely to a bathroom",
                      "long_desc": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
                    "weird": None,
                    "actions": None},
            "west": {"short_desc": "the door out of the room, likely to the hallway",
                    "west": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
                    "west_weird": None,
                    "west_actions": None},
            "exitwall": "west",
            },

    "forked tree branch": {"descrip": "None yet...", "inside":False,
            "electricity": False, "nature": True,
            "north": {"short_desc": "The entrace gates are",
                "long_desc": "You think you could leave through the large wrought-iron gates to the north. They're imposing but run-down; this graveyard doesn't get as much love as it could.",
                "weird": "You think you could leave through the large wrought-iron gates to the north. They're imposing - creaking constantly, and they seem to loom over you even from a distance.",
                "actions": leave_options,
                },
            "east": {"short_desc": "a variety of headstones",
                "long_desc": "You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, dried  left long ago.", # details here depending on weather. if raining, the dried flowers are saturated and heavy. If sunny, they're crispy, etc. Not close to implementing that yet.
                "weird": None,
                "east_actions": None,
                },
            "south": {"short_desc": "a mausoleum",
                "long_desc": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
                "weird": None,
                "actions": None,
                },
            "west": {
                "short_desc": "what looks like a work shed of some kind",
                "long_desc": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
                "weird": None,
                "actions": None
                },
            "exitwall": "north",
            },

    "graveyard": {
        "descrip": "You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences",
        "inside": False, "electricity": False, "nature": True,
        "north": {"short_desc": "The entrance gates are",
                "long_desc": "You think you could leave through the large wrought-iron gates to the north. They're imposing but run-down; this graveyard doesn't get as much love as it could.",
                "weird": "You think you could leave through the large wrought-iron gates to the north. They're imposing - creaking constantly, and they seem to loom over you even from a distance.",
                "actions": leave_options,
                },
        "east": {"short_desc": "a variety of headstones",
                "long_desc": "You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, dried  left long ago.", # details here depending on weather. if raining, the dried flowers are saturated and heavy. If sunny, they're crispy, etc. Not close to implementing that yet.
                "weird": None,
                "east_actions": None,
                },
        "south": {"short_desc": "a mausoleum",
                "long_desc": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
                "weird": None,
                "actions": None,
                },
        "west": {
                "short_desc": "what looks like a work shed of some kind",
                "long_desc": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
                "weird": None,
                "actions": None
                },
        "exitwall": "north",
            },
    "pile of rocks": {
        "descrip": "Pile of rocks.",
        "inside": False, "electricity": False, "nature": True,
        "north": {"short_desc": "The",
                "long_desc": "You",
                },
        "east": {"short_desc": "a",
                "long_desc": "You",
                },
        "south": {"short_desc": "a",
                "long_desc": "There",
                },
        "west": {
                "short_desc": "what",
                "long_desc": "There",
                },
        "exitwall": "north",
            }
        }


class cardinalInstance:
    def __init__(self, cardinal, loc):
        self.name = cardinal# + " " + place.name # eg "east graveyard"
        self.place_name = cardinal + " " + loc.name # eg "east graveyard"        },
        self.ern_p_name = cardinal + "ern " + loc.name # eg "east graveyard"
        self.place = loc
        self.short_desc = loc_dict[loc.name][cardinal].get("short_desc")
        self.long_desc = loc_dict[loc.name][cardinal].get("long_desc")

        self.cardinal_data = loc_dict[self.place.name].get(cardinal)
        self.w_cardinal = loc_dict[self.place.name][cardinal].get("weird")
        if self.w_cardinal == None:
            self.w_cardinal = self.cardinal_data
            setattr(self, "weird", self.w_cardinal)
        setattr(self, cardinal, self.cardinal_data)
        self.cardinal_actions = loc_dict[self.place.name][cardinal].get("actions")
        if not self.cardinal_actions or self.cardinal_actions == None:
            self.cardinal_actions = leave_options


class placeInstance:

    def __init__(self, name):

        self.name = name
        self.a_name = "a " + name
        self.the_name = "the " + name
        self.visited = False
        self.first_weather = None
        self.description = loc_dict.get(name, {}).get("descrip")
        self.current_loc = None
        self.colour = None ## assign like items on first
        self.cardinals = {}

        for attr, value in loc_dict.get(name, {}).items():
            setattr(self, attr, value)

        for attr in ("inside", "electricity", "nature"):
            value = loc_dict[name].get(attr)
            setattr(self, attr, value) # might work?

    def set_scene_descrip(self, name, loc):
        if loc_dict[name].get("descrip"):
            from misc_utilities import assign_colour
            self.overview = f"{loc_dict[name]["descrip"]}.{"\033[0m"} \n{self.cardinals["north"].short_desc} to the {assign_colour("north")}. To the {assign_colour("east")} is {self.cardinals["east"].short_desc}, to the {assign_colour("south")} is {self.cardinals["south"].short_desc}, and to the {assign_colour("west")} is {self.cardinals["west"].short_desc}."
#
    def visit(self):
        self.visited = True


class placeRegistry:

    def __init__(self):

        self.places = set()
        self.by_name = {}
        self.route = list() # store everywhere you go for a game, in order. Could be interesting to use later.
        self.current = None
        self.last_loc = None
        self.cardinals = {} # locRegistry.place_cardinals[place_instance_obj][cardinal_direction_str]
        self.current_cardinal = None # Not sure if I want to use this, or keep it in game.facing_direction. This might make more sense, keep it centralised? Not sure.

    def add_cardinals(self, loc):
        cardinals_dict = dict()

        for card in cardinals_list:
            cardinal_inst = cardinalInstance(card, loc)
            cardinals_dict[card] = cardinal_inst

        return cardinals_dict

    def set_current(self, loc=None, cardinal=None):
        # will  loc be a string or a loc instance? idk.
        #print(f"set_current. \nloc: {loc}, cardinal: {cardinal}")
        if loc:
            if isinstance(loc, str):
                loc_test = self.by_name[loc]
                if isinstance(loc_test, placeInstance):
                    loc = loc_test
                    self.current = loc

            if isinstance(loc, placeInstance): # this should run after the previous, no? Though the previous should never actually run, it should always be a placeInstance.
                print(f"loc.name: {loc.name}")
                self.current = loc
                print("self.current: ", self.current)
            self.route.append(loc)
            #print(f"Set loc.current to {loc.name}")

            if isinstance(loc, cardinalInstance):
                self.current_cardinal = loc
                #print(f"self.current_cardinal set to {loc.name}")

        if cardinal: ## cardinal setting always operates on current loc. If loc and cardinal have both changed, loc should be set first. Can't 'move to west graveyard' by moving west first, then going to graveyard.
            if isinstance(cardinal, str):
                cardinal = self.cardinals[self.current][cardinal]

            if isinstance(cardinal, cardinalInstance):
                self.current_cardinal = cardinal
        if loc and not cardinal:
            if not self.current_cardinal:
                print("self.cardinals: ", self.cardinals)
                current_card = "north"
            else:
                current_card = self.current_cardinal.name
            new_card = self.cardinals[self.current][current_card]
            self.current_cardinal = new_card

    def place_by_name(self, loc_name):
        if loc_name.startswith("a "):
            loc_name = loc_name.replace("a ", "")
        if loc_name.startswith("the "):
            loc_name = loc_name.replace("the ", "")

        loc_inst = self.by_name[loc_name]
        if isinstance(loc_inst, placeInstance):
            return loc_inst
        print(f"LOC INST: {loc_inst}, type: {type(loc_inst)}")
        print(f"Failed to get item instance for {loc_name}. Please investigate. Exiting from env_data.")
        exit()

    def show_name(self, loc, text=""):
        if text and text != "":
            print(text)
        if isinstance(loc, placeInstance):
            print(f"Instance: {loc}")
            print(f"Name: {loc.name}")
            if loc == self.current:
                print("NOTE: is current place.")
            else:
                print("NOTE: is not current place.")
        else:
            print("[Is not an instance.]")
            print(loc)

    def by_cardinal(self, cardinal_str, loc=None):
        if loc == None:
            loc = self.current
        cardinal_inst = locRegistry.cardinals[loc][cardinal_str]
        return cardinal_inst



locRegistry = placeRegistry()


def initialise_placeRegistry():

    for name in loc_dict.keys():
        place = placeInstance(name)
        locRegistry.places.add(place)
        locRegistry.by_name[name] = place
        locRegistry.cardinals[place] = locRegistry.add_cardinals(place)
        ## add cardinals to place instance so it's directly referable.
        cardinals_dict = {}
        for card in cardinals_list:
            cardinal_inst = cardinalInstance(card, place)
            cardinals_dict[card] = cardinal_inst
        place.cardinals=cardinals_dict
        locRegistry.set_current(place)
        place.set_scene_descrip(name, place)



if "__main__" == __name__:

    initialise_placeRegistry()
    #for loc in locRegistry.places:
    #locRegistry.add_place_cardinals()

    locRegistry.set_current("graveyard")
    #print(locRegistry.by_cardinal("north").place_name) ## This works. Really like this.

    place = locRegistry.place_by_name("graveyard")
    #for cardinal in locRegistry.place_cardinals[place]: ## this all works currently.
    #    print(f"place_cardinal: {cardinal}, type: {type(cardinal)}")
    #    print(locRegistry.place_cardinals[place][cardinal])
    #
    place_cardinals = locRegistry.cardinals[place]
    #for card in place_cardinals:
    #    print("place_cardinals[card]: ", place_cardinals[card])
    #
    print(place_cardinals["east"].place_name) ## works, prints "east graveyard"
    place = place_cardinals["east"].place ## returns graveyard instance
    print(place.name) ## works, prints "east graveyard"
    #
    print("place.cardinals['north'].long_desc: ", place.cardinals["north"].long_desc) ## this works now with the cardinal instances
    print(place.overview) # and this is working again.
