#player_movement

"""Right now, player movement is very very simple. But I want a way to track it in slightly more detail. So, this is that. Not so much the immediate tracking, as that's taken care of, but going places"""

from env_data import cardinalInstance, locRegistry as loc, placeInstance

def new_relocate(new_location:placeInstance=None, new_cardinal:cardinalInstance=None): #redoing this now
    print("[PLAYER MOVEMENT:: <new_relocate>]")
    if new_location:
        print(f"New location.name: {new_location.name}")
    if new_cardinal:
        print(f"New cardinal.name: {new_cardinal.name}")

    if new_location and not isinstance(new_location, placeInstance):
        print("new_relocate requires new_location is a placeInstance.")
        print(f"It received: {new_location}, type: {type(new_location)}")
        exit()

    if new_location and isinstance(new_location, placeInstance):
        loc.set_current(loc=new_location)

    if new_cardinal and isinstance(new_cardinal, cardinalInstance):
        loc.set_current(cardinal=new_cardinal)

    print(f"You're now facing {loc.current_cardinal.place_name}")
    if new_location:
        print(loc.current.overview)
    else:
        print(loc.current_cardinal.long_desc)


def turn_around(new_cardinal):
    #print("[PLAYER MOVEMENT:: <turn_around>]")
    if not isinstance(new_cardinal, cardinalInstance):
        print(f"turn_around in player_movement requires cardinalInstance, but got type: {type(new_cardinal)}:")
        print(f"{new_cardinal}")
        exit()
    loc.set_current(loc=None, cardinal=new_cardinal)
    print(f"You turn to face the {loc.current_cardinal.ern_name}")
    print(f"{loc.current_cardinal.long_desc}")

