#env_data - the extensive writings for specific environ details

from logger import logging_fn, traceback_fn
import json, config
with open(config.loc_data, 'r') as loc_data_file:
    loc_dict = json.load(loc_data_file)

cardinals_list = ["north", "south", "east", "west"]

weatherdict = {
"a heatwave": {"same_weather": "Still... so... hot...", "bad_weather": True, "temp": "hot"},
"fine": {"same_weather": "Huh, it's still nice here. Nice.", "bad_weather": False, "temp": "fine"},
"perfect": {"same_weather": "Such nice weather, still!", "bad_weather": False, "temp": "fine"},
"cloudy": {"same_weather": "Are those the same clouds?", "bad_weather": False, "temp": "fine"},
"raining": {"same_weather": "I wonder if this is the same rain...", "bad_weather": True, "temp": "cold"},
"stormy": {"same_weather": "Is this storm going on forever?", "bad_weather": True, "temp": "cold"},
"a thunderstorm": {"same_weather": "I didn't know thunder went on this long.", "bad_weather": True, "temp": "cold"},
}

global all_cardinals
all_cardinals = set()
import uuid

class cardinalInstance:
    """
    Instances of location's cardinal directions. PlaceInstances may have up to four, but will always have at least one.\n
    Holds various 'name' options ('east', 'east graveyard', 'eastern graveyard', 'the graveyard, facing east'), refers back to the location that holds it via cardinal.place, and stores colour and description data.
    """
    def __init__(self, cardinal, loc):
        from misc_utilities import cardinal_cols
        self.id = str(uuid.uuid4())
        self.name:str = cardinal # "east"
        self.place_name:str = cardinal + " " + loc.name # eg "east graveyard"        },
        self.ern_name:str = cardinal + "ern " + loc.name # eg "eastern graveyard"
        self.in_loc_facing_card:str = f"the {loc.name}, facing {self.name}"
        self.place:placeInstance = loc
        self.alt_names:list|None = (loc_dict[loc.name].get("alt_names") if loc_dict[loc.name].get("alt_names") else None)

        if (self.place_name == config.inv_loc_str or self.place_name == config.no_place_str):
            self.items = set() # purely for my own convenience. Maybe a bad idea but going to do it anyway for now.

        self.description:str|None = None
        self.colour = cardinal_cols.get(self.name)

        self.cardinal_data = loc_dict[self.place.name].get(cardinal)
        self.missing_cardinal:str = loc_dict[self.place.name].get("missing_cardinal")
        setattr(self, cardinal, self.cardinal_data)

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
                            self.transition_objs = set() # changed from a dict. Might have to change it back.
## Also just in general the transition_objs needs work. Far too much duplication.
                        self.transition_objs.add(item)
                            #self.transition_objs = dict()
                        self.place.transition_objs[item] = {
                            "int_location": loc_dict[self.place.name][self.name]["items"][item].get("int_location"),
                            "ext_location": (loc_dict[self.place.name][self.name]["items"][item].get("ext_location") if loc_dict[self.place.name][self.name]["items"][item].get("ext_location") != self.name else self)}

        self.visited = False # Same as .placeInstances have, not tracked in route but used for directing some descriptions etc.

    def __repr__(self):
        return f"<cardinalInstance {self.place_name} ({self.id})>"

class placeInstance:
    """
    placeInstances hold data for any given location, including descriptive data, cardinals, etc.

    Special places include locRegistry.inv_place and .no_place, which are used for inventory items and hidden/contained or otherwise secreted items' 'item.location' respectively.
    """
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
        self.transition_objs = {}

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
    """
    Registry of all location data. .places holds the instances. .cardinals holds [placeInstance_obj][cardinal_str] == cardinalInstance.

    inv_place and no_place are meta locations.
    """

    def __init__(self):

        self.places = set()
        self.by_name = {}
        self.by_alt_name = {}
        self.route = list() # store everywhere you go for a game, in order. Could be interesting to use later.
        self.last_loc:placeInstance = None # used for history tracking, just track place, not card.
        self.cardinals = {} # locRegistry.cardinals[place_instance_obj][cardinal_direction_str]
        self.current:cardinalInstance = None # cardinal instance
        self.currentPlace:placeInstance = None
        self.inv_place:cardinalInstance = None
        self.no_place:cardinalInstance = None


    def add_cardinals(self, locationInstance) -> dict:
        """ Propagates the place.cardinals dict"""
        cardinals_dict = dict()

        for card in cardinals_list:
            cardinal_inst = cardinalInstance(card, locationInstance)
            cardinals_dict[card] = cardinal_inst

        locationInstance.cardinals=cardinals_dict

        # placeInstance.name = {"south": southInstance, "north": northInstance, etc}
        return cardinals_dict

    def set_current(self, loc=None, cardinal=None):
        """ Sets locRegistry.current, and checks against locRegistry.currentPlace to see if it should add the new location to route."""
        logging_fn()
        #print(f"set current: loc: {loc}, cardinal: {cardinal}")
        if cardinal and isinstance(cardinal, cardinalInstance):
            if not cardinal.visited:
                cardinal.visited = True
            if cardinal == self.current:
                return
            if not loc:
                loc = cardinal.place

        if loc and not cardinal:
            if not isinstance(loc, placeInstance):
                loc = self.place_by_name(loc)
            if not self.current:
                print("env_data/ No current_cardinal, defaulting to 'north'.")
                current_card = config.starting_facing_direction
            else:
                current_card = self.current.name
            from interactions.player_movement import get_viable_cardinal
            cardinal, success = get_viable_cardinal(current_card, place=loc)

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
                    loc.visit() ## could just use route above... Might get long though.
                return

        elif loc:
            if not self.current:
                print("env_data/ No current_cardinal, defaulting to 'north'.")
                current_card = config.starting_facing_direction
            else:
                current_card = self.current.name
            if isinstance(loc, str):
                # TODO: Set up by_cardinal_str here, don't add a bunch of new string parsers.
                loc_test = self.by_name[loc]
                if isinstance(loc_test, placeInstance):
                    loc = loc_test
                else:
                    print(f"Failed to find instance for {loc}")
                    traceback_fn()

            if isinstance(loc, placeInstance) and not cardinal:
                self.currentPlace = loc

                new_card = self.cardinals[self.currentPlace][current_card]
                self.current = new_card
                self.currentPlace = loc
                self.route.append(loc)
                loc.visit()

            elif isinstance(loc, cardinalInstance):
                self.current = loc
                if loc.place != self.currentPlace:
                    self.currentPlace = loc.place
                    self.route.append(loc)
                    loc.place.visit()

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
                    cardinal.place.visit()
                self.current = cardinal
                #print("self.current_cardinal.name: ", cardinal.place_name)

    def place_by_name(self, loc_name):
        logging_fn()

        if loc_name == "inventory":
            loc_name = config.inv_loc_str
            loc_name = loc_name.replace(f"{config.key_dir} ", "")
            print(f"loc_name: {loc_name}, type: {type(loc_name)}")

        loc_inst = self.by_name.get(loc_name.lower())
        if not loc_inst:
            loc_inst = self.by_alt_name.get(loc_name)

        if isinstance(loc_inst, placeInstance):
            return loc_inst

        print(f"loc name: {loc_name} / self.by_name: {self.by_name} // LOC INST: {loc_inst}, type: {type(loc_inst)}")
        print(f"Failed to get placeInstance for {loc_name}. Please investigate. Exiting from env_data.")
        from logger import traceback_fn
        traceback_fn()
        exit()


    def by_cardinal_str(self, cardinal_str:str|dict, loc=None) -> cardinalInstance:
        """Used to get the cardinalInstance from a string, with or without separate 'loc'. cardinal_str can be a dict (but this is not regularly used anymore) or more often, a string in the form 'graveyard east'. 'east graveyard' will also be found. If no location is found, it will take the cardinal str and apply it to the current location (eg `east` will return the cardinalInstance for '{currentPlace} east')."""
        #logging_fn()
        str_loc = None
        if isinstance(cardinal_str, dict):
            loc, cardinal_str = next(iter(cardinal_str.items()))
        elif isinstance(cardinal_str, str):
            if " " in cardinal_str:
                [str_loc, cardinal_str2] = cardinal_str.rsplit(" ", 1)
                if not self.by_name.get(str_loc):
                    [cardinal_str2, str_loc] = cardinal_str.split(" ", 1)
                cardinal_str = cardinal_str2
                if str_loc and not loc:
                    loc = str_loc

        if loc == None:
            loc = self.currentPlace
        elif isinstance(loc, str):
            loc = self.place_by_name(loc)
        elif isinstance(loc, placeInstance):
            loc = loc

        if str_loc and str_loc != loc.name:
            print(f"Cardinal gives a different location than the given loc: {str_loc} // {loc}")

        cardinal_inst = locRegistry.cardinals[loc][cardinal_str]
        return cardinal_inst


locRegistry = placeRegistry()

def add_new_loc(name, reset_current=False):
    """Add a new placeInstance to placeRegistry, using the data from the loc defs file."""
    place = placeInstance(name)

    if loc_dict[name].get("alt_names"):
        for altname in loc_dict[name]["alt_names"]:
            locRegistry.by_alt_name[altname]=place
    locRegistry.places.add(place)
    locRegistry.by_name[name] = place

    locRegistry.cardinals[place] = locRegistry.add_cardinals(place)

    if reset_current:
        locRegistry.set_current(place)
    return place

def initialise_placeRegistry():
    """Initial placeRegistry initialisation using loc_dict. Generates instances, applies cardinals to places, and adds transitional objects to cardinals."""
    for name in loc_dict.keys():
        place = add_new_loc(name)

    for place in locRegistry.places:
        name = place.name
        for card in place.cardinals:
            cardinal = place.cardinals[card]

            if hasattr(cardinal, "transition_objs") and cardinal.transition_objs:
                for item in cardinal.transition_objs:
                    #item_data = loc_dict[name][card]["items"].get(item)
                    int_location = ext_location = None
                    if cardinal.place.transition_objs.get(item):
                        int_location = cardinal.place.transition_objs[item].get("int_location")
                        ext_location = cardinal.place.transition_objs[item].get("ext_location")

                    if not int_location:
                        print(f"No enter location found for {cardinal} transition object {item}")
                        exit()
                    if not ext_location:
                        print(f"No exit_to location found for {cardinal} transition object {item}")
                        exit()
                    for loc in (int_location, ext_location):
                        if isinstance(loc, str):
                            card_inst = locRegistry.by_cardinal_str(cardinal_str=loc)
                            if loc == int_location:
                                cardinal.place.transition_objs[item]["int_location"] = card_inst
                            else:
                                cardinal.place.transition_objs[item]["ext_location"] = card_inst

                    target_place = locRegistry.by_cardinal_str(cardinal_str=int_location)
                    if target_place and isinstance(target_place, cardinalInstance):
                        target_place = target_place.place

                    if not hasattr(target_place, "transition_objs") or (hasattr(target_place, "transition_objs") and not target_place.transition_objs):
                        target_place.transition_objs = dict()

                        target_place.transition_objs[item] = {}
                        target_place.transition_objs[item][int_location] = target_place
                        target_place.transition_objs[item][ext_location] = cardinal

                    else:
                        print(f"Target card transition objects: {target_place.transition_objs}")

    from config import starting_location_str, no_place_str, inv_loc_str
    locRegistry.set_current(starting_location_str)
    locRegistry.no_place = locRegistry.by_cardinal_str(no_place_str)
    locRegistry.inv_place = locRegistry.by_cardinal_str(inv_loc_str)


def get_descriptions(place:placeInstance, cardinal:cardinalInstance=None):
    """Generate location descriptions for the given placeInstance (+ optional cardinalInstance) combination. Applies both placeInstance.overview and cardinalInstance.description."""
    from testing_coloured_descriptions import loc_descriptions
    description_dict = loc_descriptions(place, cardinal)
    place.overview = description_dict.get(place.name).get("overview")
    if not isinstance(place.overview, str):
        place.overview = list(place.overview)[0]
    if not place.overview:
        print("Failed to get self.overview.")
        print(f"Did this part work at least? ``{description_dict.get(place.name)}``")

    CARDINALS = ["north", "east", "south", "west"]
    for card in CARDINALS:
        if locRegistry.cardinals[place].get(card) and isinstance(locRegistry.cardinals[place].get(card), cardinalInstance):
            card_inst = locRegistry.cardinals[place].get(card)
            if description_dict[place.name].get(card):
                card_inst.description = description_dict[place.name].get(card)


def get_loc_descriptions(place=None, cardinal=None):
    """Used for generating location descriptions en masse. Without place and cardinal data provided, will generate descriptions all cardinals for all places.\nOnly to run without place and cardinal at initialisation."""
    logging_fn(f"{place}, {cardinal}")

    if place == None:
        for place in locRegistry.places:
            get_descriptions(place)
            return
    if place and isinstance(place, cardinalInstance):
        place = place.place
    elif place and isinstance(place, str):
        place - locRegistry.place_by_name(place)

    if place and isinstance(place, placeInstance):
        if cardinal and isinstance(cardinal, cardinalInstance):
            #print("get_descriptions with cardinal:")
            get_descriptions(place, cardinal)
        else:
            get_descriptions(place)


if "__main__" == __name__:

    initialise_placeRegistry()
    get_loc_descriptions()
    locRegistry.set_current("graveyard")
