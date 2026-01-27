#player_movement

"""Right now, player movement is very very simple. But I want a way to track it in slightly more detail. So, this is that. Not so much the immediate tracking, as that's taken care of, but going places"""

from env_data import cardinalInstance, locRegistry as loc, placeInstance, get_loc_descriptions
from misc_utilities import assign_colour
from logger import logging_fn, traceback_fn
from eventRegistry import events

def new_relocate(new_location:placeInstance=None, new_cardinal:cardinalInstance=None):
    logging_fn()


    old_card = loc.current
    if old_card == new_cardinal:
        print(f"You're already at {assign_colour(loc.current, card_type="place_name")}")
        return


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

        if loc.currentPlace==prev_loc:
            print(f"loc.places[loc.current]: {loc.currentPlace.name}")
            print(f"You decided to stay at {assign_colour(loc.currentPlace.the_name, 'loc')} a while longer.")
        else:
            print(f"You make your way to {assign_colour(loc.currentPlace.the_name, 'loc')}. It's {game.time}, the weather is {game.weather}, and you're feeling {game.emotional_summary}.")
            if loc.currentPlace.visited:
                print(f"You've been here before... It was {loc.currentPlace.first_weather} the first time you came.")
                if loc.currentPlace.first_weather == game.weather:
                    print(weatherdict[game.weather].get("same_weather"))
            else:
                loc.currentPlace.visited = True # maybe a counter instead of a bool. Maybe returning x times means something. No idea what. Probably not.
                loc.currentPlace.first_weather = current_weather

    if new_location and not isinstance(new_location, placeInstance): ##TODO: chech if it's a viable placename str
        if isinstance(new_location, cardinalInstance):
            new_cardinal = new_location
        else:
            print("new_relocate requires new_location is a placeInstance.")
            print(f"It received: {new_location}, type: {type(new_location)}")#
            traceback_fn()
            exit()

    if not new_location and new_cardinal:
        new_location = new_cardinal.place

    #print(f"loc.current.place: {loc.current.place}")
    #print(f"new location: {new_location}")
    if events.travel_is_limited and not (new_location and new_location == loc.current.place):
        allowed_locations = events.check_movement_limits()
        #cannot_leave_loc = events.held_at.get("held_at_loc")
        #holding_event = events.held_at.get("held_by") # make held by a set, each event instance carries which locations it allows.
        if not allowed_locations.get(new_location.name):
            #print(f"Location {new_location} is allowed by location-limiting event {allowed_locations[new_location.name]}")
        #else:
            holding_event = list(allowed_locations[loc.currentPlace.name])[0]
            msg = events.play_event_msg("held", holding_event, print_txt=False)
            print(f"You want to go to the {assign_colour(new_location)}, but...\n         {assign_colour(msg, colour='event_msg')}")
            return

    if new_location and new_location == loc.current.place:
    #elif events.travel_is_limited and (new_location and new_location == loc.current.place):
        print(f"You're already in the {assign_colour(loc.current.place)}")
        get_loc_descriptions(place=loc.currentPlace)
        print(loc.current.description)
        return

    if new_location and isinstance(new_location, placeInstance) and not new_cardinal:
        new_card_inst = loc.by_cardinal_str(loc.current.name, new_location)
        if not new_card_inst.cardinal_data:
        #if not (hasattr(new_card_inst, new_card_inst.name) and getattr(new_card_inst, new_card_inst.name)):
            #print(f"This is not a viable direction for {new_location.name}")
            for card in new_location.cardinals:
                new_card_inst = new_location.cardinals.get(card)
                if new_card_inst.cardinal_data:
                    new_relocate(new_cardinal=new_card_inst)
                    return

        if new_card_inst:
            #print(f"NEW CARD INST: {new_card_inst}")
            #print(vars(new_card_inst))
            loc.set_current(loc = new_location, cardinal=new_card_inst)
        else:
            for card in new_location.cardinals:
                new_card_inst = (new_location.cardinals.get(card) if new_location.cardinals.get(card) else None)
                if new_card_inst and new_card_inst.cardinal_data:
                    loc.set_current(loc = new_location, cardinal=new_card_inst) # if just going from place to place, just pick the first viable cardinal silently.
                    break

    elif new_cardinal and isinstance(new_cardinal, cardinalInstance):

        if not new_cardinal.cardinal_data:
        #if not (hasattr(new_card_inst, new_card_inst.name) and getattr(new_card_inst, new_card_inst.name)):
            #print(f"This is not a viable direction for {new_location.name}")
            for card in new_location.cardinals:
                new_card_inst = new_location.cardinals.get(card)
                if new_card_inst.cardinal_data:
                    new_relocate(new_cardinal=new_card_inst)
                    return

            if new_cardinal.missing_cardinal:
                #print("new_cardinal.missing_cardinal")
                print(assign_colour(new_cardinal.missing_cardinal, "event_msg"))
                return

        if new_location:
            loc.set_current(loc = new_location, cardinal=new_cardinal)
        else:
           # new_cardinal = loc.by_cardinal_str(new_cardinal)
          #  if new_cardinal:
            loc.set_current(cardinal=new_cardinal)
           # else:
           #     for card in new_location.cardinals:
            #        new_card_inst = (new_location.cardinals.get(card) if new_location.cardinals.get(card) else None)
             #       if new_card_inst:
             #           loc.set_current(loc = new_location, cardinal=new_card_inst)


    print(f"You're now facing {assign_colour(loc.current, card_type="place_name")}\n")
    get_loc_descriptions(loc.currentPlace)
    if new_location:
        print(loc.current.place.overview)
    else:
        print(loc.current.description)
        #print(loc.current.long_desc)

    assert isinstance(loc.current, cardinalInstance)


def turn_around(new_cardinal):
    logging_fn()
    if not isinstance(new_cardinal, cardinalInstance):
        print(f"turn_around in player_movement requires cardinalInstance, but got type: {type(new_cardinal)}:")
        print(f"{new_cardinal}")
        traceback_fn()
        exit()
    if not new_cardinal.cardinal_data:
        if new_cardinal.missing_cardinal:
            print("new_cardinal.missing_cardinal")
            print(new_cardinal.missing_cardinal)
            return
    loc.set_current(loc=None, cardinal=new_cardinal)
    #print(f"loc.current_cardinal after turn_around: {loc.current}, type: {type(loc.current)}")
    print(f"You turn to face the {assign_colour(item=loc.current, card_type = "ern_name")}")
    get_loc_descriptions(place=loc.currentPlace)
    print(f"{loc.current.description}")

