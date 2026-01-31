#player_movement

"""Right now, player movement is very very simple. But I want a way to track it in slightly more detail. So, this is that. Not so much the immediate tracking, as that's taken care of, but going places"""

from env_data import cardinalInstance, locRegistry as loc, placeInstance, get_loc_descriptions
from misc_utilities import assign_colour
from logger import logging_fn, traceback_fn
from eventRegistry import events

def get_viable_cardinal(cardinal_inst:cardinalInstance): # 0 == match, 1 == had to find an alt

    if hasattr(cardinal_inst, "cardinal_data") and cardinal_inst.cardinal_data != None and cardinal_inst.cardinal_data.get("item_desc"):
        #print('cardinal_inst.cardinal_data.get("item_desc"): {cardinal_inst.cardinal_data.get("item_desc")}')
        return cardinal_inst, 0
    else:

        #print(f"No item desc, {cardinal_inst} is not a viable cardinal. Need a better way of doing this tho.")
        for card in cardinal_inst.place.cardinals:
            #print(f"CARD: {card}")
            #if cardinal_inst.place.cardinals.get(card) and getattr(cardinal_inst.place.cardinals[card].cardinal_data, "item_desc"):
            if cardinal_inst.place.cardinals.get(card) and cardinal_inst.place.cardinals[card].cardinal_data.get("item_desc"):
                #print(f"Next viable cardinal: {cardinal_inst.place.cardinals[card]}")
                return cardinal_inst.place.cardinals[card], 1


def check_loc_card(location, cardinal):
    to_loc = None
    to_card = None
    is_same_loc = False
    is_same_card = False

    if location:
        if isinstance(location, placeInstance):
            to_loc = location
        elif isinstance(location, str):
            test = loc.by_name.get(location)
            if test:
                to_loc = test

    if cardinal:
        if isinstance(cardinal, cardinalInstance):
            to_card = cardinal
        elif isinstance(cardinal, cardinalInstance):
            test = loc.by_cardinal_str(cardinal, to_loc)
            if test:
                to_card = test

    if to_card and not to_loc:
        to_loc = to_card.place

    if to_loc and to_loc == loc.current.place:
        is_same_loc = True

    if to_card and to_card == loc.current:
        is_same_card = True

    if not to_card and not to_loc:
        print(f"End of check_loc_card, no location or cardinal from {location}, {cardinal}")
        exit(code="Exiting because reason given above.")
    return to_loc, to_card, is_same_loc, is_same_card


def new_relocate(new_location:placeInstance=None, new_cardinal:cardinalInstance=None):
    logging_fn()

    def update_loc_data(prev_loc, new_location):
        from set_up_game import game
        from choices import time_of_day
        from env_data import weatherdict
        import random

        current_weather = game.weather

        time_index=time_of_day.index(game.time)
        new_time_index=time_index + 1 # works
        if new_time_index == len(time_of_day):
            new_time_index=0
        game.time=time_of_day[new_time_index]

        weather_options = list(weatherdict)
        weather_index=weather_options.index(game.weather)
        weather_variance=random.choice([int(-1), int(1)])
        new_weather_index=weather_index + int(weather_variance)
        if new_weather_index == len(weather_options):
            new_weather_index=0
        game.weather=weather_options[new_weather_index]
        game.bad_weather = weatherdict[game.weather].get("bad_weather")

        if loc.current.place==prev_loc:
            print(f"loc.places[loc.current]: {loc.current.place.name}")
            print(f"You decided to stay at {assign_colour(loc.current.place.the_name, 'loc')} a while longer.")
        else:
            print(f"You make your way to {assign_colour(loc.current.place.the_name, 'loc')}. It's {game.time}, the weather is {game.weather}, and you're feeling {game.emotional_summary}.")
            if loc.current.place.visited:
                print(f"You've been here before... It was {loc.current.place.first_weather} the first time you came.")
                if loc.current.place.first_weather == game.weather:
                    print(weatherdict[game.weather].get("same_weather"))
            else:
                loc.current.place.visited = True # maybe a counter instead of a bool. Maybe returning x times means something. No idea what. Probably not.
                loc.current.place.first_weather = current_weather

    to_loc, to_card, is_same_loc, is_same_card = check_loc_card(new_location, new_cardinal)

    if is_same_card and is_same_loc:
        print(f"You're already at {assign_colour(loc.current, card_type="place_name")}")
        return

    if events.travel_is_limited and not (to_loc and to_loc == loc.current.place):
        allowed_locations = events.check_movement_limits()

        if not allowed_locations.get(to_loc.name):
            holding_event = list(allowed_locations[loc.current.place.name])[0]
            msg = events.play_event_msg("held", holding_event, print_txt=False)
            print(f"You want to go to the {assign_colour(to_loc)}, but...\n      {assign_colour(msg, colour='event_msg')}")
            return

    elif is_same_loc:
        print(f"You're already in the {assign_colour(loc.current.place)}")
        if is_same_card or not new_cardinal:
            return
        turn_around(new_cardinal)
        return

    if new_location and isinstance(new_location, placeInstance) and not new_cardinal:
        new_cardinal = loc.current.name
        new_card_inst = loc.by_cardinal_str(loc.current.name, new_location)
        if not new_card_inst.cardinal_data:
            for card in new_location.cardinals:
                new_card_inst = new_location.cardinals.get(card)
                if new_card_inst.cardinal_data:
                    break

        if new_card_inst:
            loc.set_current(loc = new_location, cardinal=new_card_inst)
        else:
            for card in new_location.cardinals:
                new_card_inst = (new_location.cardinals.get(card) if new_location.cardinals.get(card) else None)
                if new_card_inst and new_card_inst.cardinal_data.get("item_desc"):
                    loc.set_current(loc = new_location, cardinal=new_card_inst) # if just going from place to place, just pick the first viable cardinal silently.
                    break

    elif new_cardinal and isinstance(new_cardinal, cardinalInstance):

        if not new_cardinal.cardinal_data:
        #if not (hasattr(new_card_inst, new_card_inst.name) and getattr(new_card_inst, new_card_inst.name)):
            print(f"This {new_cardinal} is not a viable direction for {new_cardinal.place}")
            if new_cardinal.place.missing_cardinal:
                #print("new_cardinal.missing_cardinal")
                print(assign_colour(new_cardinal.missing_cardinal, "event_msg"))
            for card in new_location.cardinals:
                new_card_inst = new_location.cardinals.get(card)
                if new_card_inst.cardinal_data:
                    print(f"new_card_inst: {new_card_inst}")
                    turn_around(new_cardinal)
                    #new_relocate(new_cardinal=new_card_inst)
                    return

        if new_location:
            loc.set_current(loc = new_location, cardinal=new_cardinal)
        else:
            loc.set_current(cardinal=new_cardinal)

    from misc_utilities import in_loc_facing_card
    print(f"You're now in {in_loc_facing_card(loc.current)}\n")
    get_loc_descriptions(loc.current.place)

    if new_location:
        print(loc.current.place.overview)
    else:
        print(loc.current.description)

    assert isinstance(loc.current, cardinalInstance)
    return 1

def turn_around(new_cardinal):

    logging_fn()
    if not isinstance(new_cardinal, cardinalInstance):
        print(f"turn_around in player_movement requires cardinalInstance, but got type: {type(new_cardinal)}:")
        print(f"{new_cardinal}")
        traceback_fn()
        exit()

    cardinal, alt_match = get_viable_cardinal(new_cardinal)
    if alt_match:
        if cardinal.place.missing_cardinal:
            print(assign_colour(new_cardinal.missing_cardinal, "event_msg"))
            return
    loc.set_current(loc=None, cardinal=cardinal)
    print(f"You turn to face the {assign_colour(loc.current, card_type="place_name")}")
    get_loc_descriptions(place=loc.current.place)
    print(f"{loc.current.description}")

