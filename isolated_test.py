## I'm not really sure what the identify of this particular script is in the new version. It used to be the core of everything because it held the loops, but the loops aren't used anymore...

from misc_utilities import assign_colour

from set_up_game import set_up, game
from choices import time_of_day

from itemRegistry import registry

from logger import logging_fn

from verb_membrane import run_membrane

from env_data import locRegistry as loc


user_prefs = r"D:\Git_Repos\Choose_your_own\path_userprefs.json"
run_again = False

yes = ["y", "yes"]
no = ["n", "no", "nope"]

#system("cls")

def option():
    logging_fn()

    from config import run_tests
    end_loop = run_membrane(run_tests=run_tests)
    if end_loop == "exit":
        return "exit"


def inner_loop(speed_mode=False):
    logging_fn()

    loc.currentPlace.visited = True
    loc.currentPlace.first_weather = game.weather

    while True:
        test=option()
        if test == "exit":
            return test

def run():
    import config
    config.enable_tui = False
    #sleep(5) ## just pauses at a black screen, previous text already removed.
    #do_clearscreen()
    playernm = ""

    test_mode=config.test_mode

    if test_mode:
        playernm = "Testbot"
    else:
        print()
        print("What's your name?")
        while  playernm == "":
            playernm = input()

    game = set_up(weirdness=True, bad_language=True, player_name=playernm)

    map_items = registry.instances_by_name("local map")
    if map_items:
        for map in map_items:
            game.map_item = map
            setattr(map, "is_map", True)

            break
    if not test_mode:
        print("[[ Type 'help' for controls and options. ]]")

    print(f"\nYou wake up in {assign_colour(loc.currentPlace.a_name, 'loc')}, right around {game.time}. You find have a bizarrely good sense of cardinal directions; how odd.")
    print(f"`{game.playername}`, you think to yourself, `is it weird to be in {assign_colour(loc.currentPlace.the_name, 'loc')} at {game.time}, while it's {game.weather}?`\n")
    from misc_utilities import look_around
    look_around()
    print()
    result = inner_loop(speed_mode=test_mode)
    return result
