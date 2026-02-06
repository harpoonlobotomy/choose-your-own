#env_data - the extensive writings for specific environ details

## Rules: One direction is always the exit.

#from locations import places

from logger import logging_fn, traceback_fn
import json, config
with open(config.loc_data, 'r') as loc_data_file:
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

leave_options = str("'leave', 'stay', preamble='Do you want to leave, or stay?'")

global all_cardinals
all_cardinals = set()
import uuid

class cardinalInstance:
    def __init__(self, cardinal, loc):
        from misc_utilities import cardinal_cols
        self.id = str(uuid.uuid4())
        self.name = cardinal # "east"
        self.place_name = cardinal + " " + loc.name # eg "east graveyard"        },
        self.ern_name = cardinal + "ern " + loc.name # eg "eastern graveyard"
        self.in_loc_facing_card = f"the {loc.name}, facing {self.name}"
        self.place = loc
        self.alt_names = (loc_dict[loc.name].get("alt_names") if loc_dict[loc.name].get("alt_names") else None)

        self.colour = cardinal_cols.get(self.name)

        self.cardinal_data = loc_dict[self.place.name].get(cardinal)
        self.missing_cardinal = loc_dict[self.place.name].get("missing_cardinal")
        setattr(self, cardinal, self.cardinal_data)

        self.cardinal_actions = (loc_dict[self.place.name][cardinal].get("actions") if loc_dict[self.place.name].get(cardinal) else None)
        if not self.cardinal_actions or self.cardinal_actions == None:
            self.cardinal_actions = leave_options

        self.by_placename = {}
        all_cardinals.add(self)

        if loc_dict[self.place.name].get(self.name) and loc_dict[self.place.name][self.name].get("items"):
            #print(f"{self.place_name} loc has items.")
            for item in loc_dict[self.place.name][self.name]["items"]:
                if loc_dict[self.place.name][self.name]["items"][item].get("item_type"):
                    if "loc_exterior" in loc_dict[self.place.name][self.name]["items"][item]["item_type"]:
                        if not hasattr(self, "loc_exterior_items"):
                            self.loc_exterior_items = set()
                        self.loc_exterior_items.add(item) # TODO should do this a different way, because this doesn't use the instance, only the name.
                    if "transition" in loc_dict[self.place.name][self.name]["items"][item]["item_type"]:
                        if not hasattr(self, "transition_objs"):
                            self.transition_objs = dict()
                        self.transition_objs[item] = {"enter_location": loc_dict[self.place.name][self.name]["items"][item].get("enter_location"), "exit_to_location": (loc_dict[self.place.name][self.name]["items"][item].get("exit_to_location") if loc_dict[self.place.name][self.name]["items"][item].get("exit_to_location") != self.name else self)}

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
        self.overview = None
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
            setattr(self, attr, value)

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
        self.current = None # cardinal instance
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
        logging_fn()
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
                return

        elif loc:
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
                self.currentPlace = loc
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
        logging_fn()
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
        #logging_fn()
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

        cardinal_inst = locRegistry.cardinals[loc][cardinal_str]
        return cardinal_inst


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

    if reset_current:
        locRegistry.set_current(place)
    return place

def initialise_placeRegistry():

    for name in loc_dict.keys():
        place = add_new_loc(name)

        if hasattr(place, "transition_objs"):
            for item in place.transition_objs:
                enter_location = place.transition_objs[item].get("enter_location")
                exit_to_location = place.transition_objs[item].get("exit_to_location")
                if not enter_location:
                    print(f"No enter location found for {place} transition object {item}")
                    exit()
                if not exit_to_location:
                    print(f"No exit_to location found for {place} transition object {item}")
                    exit()
                for loc in (enter_location, exit_to_location):
                    if isinstance(loc, str):
                        loc_inst = locRegistry.place_by_name(loc)
                        if loc == enter_location:
                            place.transition_objs[item]["enter_location"] = loc_inst
                        else:
                            place.transition_objs[item]["exit_to_location"] = loc_inst

                target_place = enter_location
                if not hasattr(target_place, "transition_objs"):
                    target_place.transition_objs = dict()

                    target_place.transition_objs[item] = {}
                    target_place.transition_objs[item][enter_location] = target_place
                    target_place.transition_objs[item][exit_to_location] = place

                else:
                    print(f"Target place transition objects: {target_place.transition_objs}")


def get_descriptions(place:placeInstance):

    from testing_coloured_descriptions import loc_descriptions
    description_dict = loc_descriptions(place)
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


def get_loc_descriptions(place=None):

    if place == None:
        for place in locRegistry.places:
            get_descriptions(place)
            return
    if place and isinstance(place, cardinalInstance):
        place = place.place
    elif place and isinstance(place, str):
        place - locRegistry.place_by_name(place)

    if place and isinstance(place, placeInstance):
        get_descriptions(place)


if "__main__" == __name__:

    initialise_placeRegistry()
    get_loc_descriptions()
    locRegistry.set_current("graveyard")
