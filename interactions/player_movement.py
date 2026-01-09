#player_movement

"""Right now, player movement is very very simple. But I want a way to track it in slightly more detail. So, this is that. Not so much the immediate tracking, as that's taken care of, but going places"""

from env_data import cardinalInstance, locRegistry as loc, placeInstance

def new_relocate(new_location=None, new_cardinal=None): #redoing this now
    print("new_relocate")
    if new_location and not isinstance(new_location, placeInstance):
        print("new_relocate requires new_location is a placeInstance.")
        print(f"It received: {new_location}, type: {type(new_location)}")
        exit()
    print(new_location)
    print(new_location.name)

    if isinstance(new_location, str):
        new_location = loc.by_name(new_location)

    if isinstance(new_location, placeInstance):
        loc.set_current(loc=new_location)

    if new_cardinal:
        print(new_location)
        print(new_location.name)
        loc.set_current(cardinal=new_location)
        print(f"You're now facing {loc.current_cardinal.place_name}")


    print(f"You're now facing {loc.current_cardinal.place_name}")
    print(loc.current.description)


def turn_around(new_cardinal):
    if not isinstance(new_cardinal, cardinalInstance):
        print("turn_around in player_movement requires cardinalInstance, but got:")
        print(f"{new_cardinal}, type: {type(new_cardinal)}")
        exit()
    print(f"You turn to face the {new_cardinal.ern_name}")
    loc.set_current(loc=None, cardinal=new_cardinal)
    print(new_cardinal.long_desc)

