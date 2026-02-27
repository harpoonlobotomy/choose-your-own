#player_movement

"""Right now, player movement is very very simple. But I want a way to track it in slightly more detail. So, this is that. Not so much the immediate tracking, as that's taken care of, but going places"""

from env_data import cardinalInstance, locRegistry as loc, placeInstance, get_loc_descriptions
from logger import logging_fn, traceback_fn
from eventRegistry import events

def get_viable_cardinal(cardinal_inst=None, place:placeInstance=None) -> tuple[(cardinalInstance, int)]: # 0 == match, 1 == had to find an alt
    """Returns the first viable cardinal for a given location based on the input cardinal. Used for locations that have less than 4 cardinals to ensure an available cardinal is chosen. Returns {cardinalInstance, val}, where val is 1 for an immediate result (ie the given cardinal is a viable destination.)"""
    from env_data import cardinalInstance
    if cardinal_inst and isinstance(cardinal_inst, cardinalInstance):
        if hasattr(cardinal_inst, "cardinal_data") and cardinal_inst.cardinal_data != None and cardinal_inst.cardinal_data.get("item_desc"):
            #print('cardinal_inst.cardinal_data.get("item_desc"): {cardinal_inst.cardinal_data.get("item_desc")}')
            return cardinal_inst, 1

        else:
            #print(f"No item desc, {cardinal_inst} is not a viable cardinal. Need a better way of doing this tho.")
            for card in cardinal_inst.place.cardinals:
                #print(f"CARD: {card}")
                #if cardinal_inst.place.cardinals.get(card) and getattr(cardinal_inst.place.cardinals[card].cardinal_data, "item_desc"):
                if cardinal_inst.place.cardinals.get(card) and cardinal_inst.place.cardinals[card].cardinal_data.get("item_desc"):
                    #print(f"Next viable cardinal: {cardinal_inst.place.cardinals[card]}")
                    return cardinal_inst.place.cardinals[card], 0
    if place:
        if cardinal_inst and isinstance(cardinal_inst, str):
            cardinal = place.cardinals.get(cardinal_inst)
            if hasattr(cardinal, "cardinal_data") and cardinal.cardinal_data != None and cardinal.cardinal_data.get("item_desc"):
                return cardinal, 1

        for card in place.cardinals:
            if place.cardinals.get(card) and place.cardinals[card].cardinal_data.get("item_desc"):
                if not cardinal_inst:
                    return place.cardinals[card], 1
                return place.cardinals[card], 0


def check_loc_card(to_loc:placeInstance, to_card:cardinalInstance=None):

    is_same_loc = False
    is_same_card = False

    if to_card and not to_loc:
        to_loc = to_card.place

    if to_loc and to_loc == loc.current.place:
        is_same_loc = True

    if to_card and to_card == loc.current:
        is_same_card = True

    if not to_card and not to_loc:
        print(f"End of check_loc_card, no location or cardinal from `location`: `{to_loc}` or `cardinal`:  `{to_card}`")
        exit(code="Exiting because reason given above.")
    return is_same_loc, is_same_card


def relocate(new_location:placeInstance=None, new_cardinal:cardinalInstance=None):
    logging_fn()
    from misc_utilities import assign_colour

    def update_loc_data(prev_loc:placeInstance, new_cardinal:cardinalInstance, print_txt = False):

        from misc_utilities import assign_colour
        from set_up_game import game
        from choices import time_of_day
        from env_data import weatherdict
        import random
        new_location = new_cardinal.place
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

        if new_location==prev_loc:
            if print_txt:
                print(f"You decided to stay at {assign_colour(loc.current.place.the_name, 'loc')} a while longer.\n")
        else:
            if print_txt:
                print(f"You make your way to {assign_colour(new_location.the_name, 'loc')}. It's {game.time}, the weather is {game.weather}, and you're feeling {game.emotional_summary}.")
            if not new_location.visited:
                new_location.visited = True # maybe a counter instead of a bool. Maybe returning x times means something. No idea what. Probably not.
                new_location.first_weather = current_weather
            else:
                if print_txt:
                    print(f"You've been here before... It was {new_location.first_weather} the first time you came.")
                    if new_location.first_weather == game.weather:
                        print(weatherdict[game.weather].get("same_weather"))

            events.update_timed_events(new_cardinal) # Sending cardinal so events have the data they need.
        if not new_cardinal.visited:
            new_cardinal.visited = True

    if new_location and isinstance(new_location, cardinalInstance) and not new_cardinal:
        new_cardinal = new_location
        new_location = new_cardinal.place

    if new_cardinal:
        if isinstance(new_cardinal, str):
            test = loc.by_cardinal_str(new_cardinal, new_location)
            if test and isinstance(test, cardinalInstance):
                new_cardinal = test
        if not isinstance(new_cardinal, cardinalInstance):
            print(f"[ERROR]: new_cardinal in def relocate() is not cardinalInstance: {new_cardinal}. Exiting.")
            exit()

    if not new_cardinal:
        print("No new cardinal given.")

    if not new_location:
        new_location = new_cardinal.place

    is_same_loc, is_same_card = check_loc_card(new_location, new_cardinal)

    if (is_same_card or not new_cardinal) and is_same_loc:
        print(f"You're already at {assign_colour(loc.current, card_type="place_name")}")
        return
    #print(f"new_relocate: TRAVEL_IS_LIMITED?: {events.travel_is_limited}")
    if events.travel_is_limited and not (new_location and new_location == loc.current.place):
        allowed_locations = events.check_movement_limits()
        if not allowed_locations.get(new_location.name):
            holding_event = list(allowed_locations[loc.current.place.name])[0]
            msg = events.play_event_msg("held", holding_event, print_txt=False)
            print(f"You want to go to the {assign_colour(new_location)}, but...\n      {assign_colour(msg, colour='event_msg')}")
            return

    if new_cardinal and isinstance(new_cardinal, cardinalInstance):
        test_cardinal, success = get_viable_cardinal(new_cardinal)
        #print(f"new cardinal: {new_cardinal} // value: {success}")
        if not success:
            if hasattr(test_cardinal.place, "missing_cardinal"):
                print(assign_colour(test_cardinal.place.missing_cardinal, "event_msg"))
            else:
                print(assign_colour("There's nothing over that way.", colour="event_msg"))

            if new_cardinal.cardinal_data or new_cardinal.place == loc.current.place: # separated new_ from test_ so it tests if the expected location will be chosen, and prints based on that, not just loc.current (which may not be where we 'turn back' to, or for times where you're turning within the current loc.)
                print(assign_colour("\n    You decide to turn back.\n", colour="event_msg"))
            else:
                print(assign_colour("\n    You turn around, taking in your surroundings.\n", colour="event_msg"))
            new_cardinal = test_cardinal

    if new_location and isinstance(new_location, placeInstance) and not new_cardinal:
        new_cardinal = loc.current.name
        print("new cardinal")
        new_card_inst = loc.by_cardinal_str(new_cardinal, new_location.name)
        print(f"new card inst: {new_card_inst}")
        if not new_card_inst.cardinal_data:
            for card in new_location.cardinals:
                new_card_inst = new_location.cardinals.get(card)
                if new_card_inst.cardinal_data:
                    new_cardinal = new_card_inst
                    break
        #update_loc_data(loc.current.place, new_card_inst)
        if new_card_inst:
            new_cardinal = new_card_inst
        else:
            for card in new_location.cardinals:
                test = (new_location.cardinals.get(card) if new_location.cardinals.get(card) else None)
                if test and test.cardinal_data.get("item_desc"):
                    new_cardinal = test
                    break
                    #loc.set_current(loc = new_location, cardinal=new_card_inst) # if just going from place to place, just pick the first viable cardinal silently.



    update_loc_data(loc.current.place, new_cardinal)
    if new_cardinal.place != loc.current.place:
        from misc_utilities import in_loc_facing_card
        print(f"You're now in {in_loc_facing_card(new_cardinal)}\n")

    if new_location != loc.current.place:
        get_loc_descriptions(new_location, new_cardinal)
        loc.set_current(cardinal=new_cardinal)
        from itemRegistry import registry
        items = registry.get_item_by_location(loc.current)
        print(f"ITEMS: {items}")
        if items:
            for item in items:
                if hasattr(item, "event") and item.event and item.event.state == 1:
                    print(f"Item {item} has current event: {item.event}")
        print(loc.current.place.overview)
        print(f"\n{loc.current.description}")
    else:
        loc.set_current(cardinal=new_cardinal)
        get_loc_descriptions(loc.current.place, loc.current)
        from itemRegistry import registry
        if registry.by_location.get(loc.current):
            items = registry.get_item_by_location(loc.current)
        print(f"You're facing the {assign_colour(loc.current, card_type="place_name")}.\n\n{loc.current.description}")
        #print(loc.current.description)


    assert isinstance(loc.current, cardinalInstance)
    return 1
