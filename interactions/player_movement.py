#player_movement

"""Right now, player movement is very very simple. But I want a way to track it in slightly more detail. So, this is that. Not so much the immediate tracking, as that's taken care of, but going places"""

from env_data import cardinalInstance, locRegistry as loc, placeInstance
from misc_utilities import assign_colour
from logger import logging_fn, traceback_fn

def new_relocate(new_location:placeInstance=None, new_cardinal:cardinalInstance=None):
    logging_fn()

    assert isinstance(loc.current, cardinalInstance)

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

    if new_location and not isinstance(new_location, placeInstance):
        print("new_relocate requires new_location is a placeInstance.")
        print(f"It received: {new_location}, type: {type(new_location)}")#
        traceback_fn()
        exit()

    if new_location and isinstance(new_location, placeInstance) and not new_cardinal:
        new_card_inst = loc.by_cardinal(loc.current.name, new_location)
        loc.set_current(loc = new_location, cardinal=new_card_inst)

    elif new_cardinal and isinstance(new_cardinal, cardinalInstance):
        if new_location:
            loc.set_current(loc = new_location, cardinal=new_cardinal)
        else:
            new_cardinal = loc.by_cardinal(new_cardinal)
            loc.set_current(cardinal=new_cardinal)

    print(f"You're now facing {assign_colour(loc.current)}")
    if new_location:
        print(loc.current.place.overview)
    else:
        print(loc.current.long_desc)

    assert isinstance(loc.current, cardinalInstance)


def turn_around(new_cardinal):
    logging_fn()
    if not isinstance(new_cardinal, cardinalInstance):
        print(f"turn_around in player_movement requires cardinalInstance, but got type: {type(new_cardinal)}:")
        print(f"{new_cardinal}")
        traceback_fn()
        exit()
    loc.set_current(loc=None, cardinal=new_cardinal)
    #print(f"loc.current_cardinal after turn_around: {loc.current}, type: {type(loc.current)}")
    print(f"You turn to face the {assign_colour(item=loc.current, card_type = "ern_name")}")
    print(f"{loc.current.long_desc}")

