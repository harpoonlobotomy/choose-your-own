#player_movement

"""Right now, player movement is very very simple. But I want a way to track it in slightly more detail. So, this is that. Not so much the immediate tracking, as that's taken care of, but going places"""

from env_data import cardinalInstance, locRegistry as loc, placeInstance
from misc_utilities import assign_colour
from logger import logging_fn, traceback_fn

def new_relocate(new_location:placeInstance=None, new_cardinal:cardinalInstance=None):
    logging_fn()
    #if new_location:
    #    print(f"New location.name: {new_location.name}")
    #if new_cardinal:
    #    print(f"New cardinal.name: {new_cardinal.name}")

    if new_location and not isinstance(new_location, placeInstance):
        print("new_relocate requires new_location is a placeInstance.")
        print(f"It received: {new_location}, type: {type(new_location)}")#
        traceback_fn()
        exit()

    if new_location and isinstance(new_location, placeInstance):
        if not new_cardinal:
            current_card = loc.current_cardinal.name
            new_card_inst = loc.by_cardinal(current_card, new_location)
        loc.set_current(cardinal=new_card_inst)

    if new_cardinal and isinstance(new_cardinal, cardinalInstance):
        loc.set_current(cardinal=new_cardinal)

    print(f"You're now facing {assign_colour(loc.current_cardinal)}")
    if new_location:
        print(loc.current.overview)
    else:
        print(loc.current_cardinal.long_desc)


def turn_around(new_cardinal):
    logging_fn()
    if not isinstance(new_cardinal, cardinalInstance):
        print(f"turn_around in player_movement requires cardinalInstance, but got type: {type(new_cardinal)}:")
        print(f"{new_cardinal}")
        traceback_fn()
        exit()
    loc.set_current(loc=None, cardinal=new_cardinal)
    print(f"loc.current_cardinal after turn_around: {loc.current_cardinal}, type: {type(loc.current_cardinal)}")
    print(f"You turn to face the {assign_colour(item=loc.current_cardinal, card_type = "ern_name")}")
    print(f"{loc.current_cardinal.long_desc}")

