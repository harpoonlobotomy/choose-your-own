## I'm not really sure what the identify of this particular script is in the new version. It used to be the core of everything because it held the loops, but the loops aren't used anymore...

from misc_utilities import assign_colour, col_list, get_inst_list_names, do_print, do_input

from set_up_game import set_up
from choices import time_of_day

from itemRegistry import registry

from logger import logging_fn

from verb_membrane import run_membrane

from env_data import locRegistry as loc


user_prefs = r"D:\Git_Repos\Choose_your_own\path_userprefs.json"
run_again = False

yes = ["y", "yes"]
no = ["n", "no", "nope"]

clear_screen = False

def do_clearscreen():
    if clear_screen:
        print("Should not print this, clear_screen == False.")#system("cls")
        exit()

def slowLines(txt, speed=0.1, end=None, edit=False):
    if isinstance(txt, str) and txt.strip=="":
        edit=True
    do_print(text=txt, end=end, do_edit_list=edit)

def do_print(txt, speed=0.001, end=None, edit=False): # Just keeping this here for now as a way to maintain that once, these calls were different from the line prints.
    print(txt)

def get_visited_map():

    for place_obj in loc.places:
        if place_obj.visited:
            do_print(f"Visited {place_obj.name}. \n {assign_colour(f'Description: {place_obj.overview}', "b_yellow")}")
            for cardinal in loc.cardinals[place_obj]:
                cardinal_inst = loc.cardinals[place_obj][cardinal]
                items = get_items_at_here(place=cardinal_inst, print_list=False, return_coloured=True)
                if items:
                    items = ", ".join(items)
                    print(f"Items at {cardinal_inst.place_name}: {items}")

    do_print("\nEnd of Past Visits.")


def get_items_at_here(print_list=False, return_coloured=True, place=loc.current) -> list: # default to current_cardinal as place, otherwise you have to state what you want.

    instance_objs_at = (registry.get_item_by_location(place))
        #print(f"Instance objs at: {instance_objs_at}")

    #if not instance_objs_at:
    #    print(f"There are no items at {place.place_name}")

    to_print_list = []
    coloured_list = []
    if instance_objs_at:
        for item in instance_objs_at:
            to_print_list.append(item.name)
        coloured_list = col_list(to_print_list)

    if coloured_list:
        if print_list:
            print(coloured_list)
        if return_coloured:
            return coloured_list
    return to_print_list


def god_mode():
    from env_data import weatherdict
    attr_dict={
        "time":time_of_day,
        "weather":list(weatherdict.keys())
    }

    slowLines("God mode: set game.[] parameters during a playthrough. For a print of all game.[] parameters, type 'game_all. Otherwise, just type the change you wish to make.")

    while True:
        text=do_input()
        if "game_all" in text:
            attributes = [attr for attr in dir(game)
              if not attr.startswith('__')]
            do_print(f"attributes: {attributes}")
        if "print" in text:
            text=text.replace("print ", "")
            obj = getattr(game, text)
            if type(obj) == str:
                obj = attr_dict.get(obj)
            do_print(obj)

        if "game." in text:
            textstart, value=text.split("=")
            do_print(f"Text: {text}, textstart: {textstart}, value: {value}")
            if textstart in ("game.time", "game.weather", "game.place"):
                try:
                    if "time" in textstart:
                        game.time=value
                        do_print(f"{textstart} has been set: game.time: {game.time}")
                    if "weather" in textstart:
                        game.weather=value
                        do_print(f"{textstart} has been set: game.weather: {game.weather}")
                    if "place" in textstart:
                        game.place=value
                        do_print(f"{textstart} has been set: {assign_colour(game.place, 'loc')}")
                except Exception as e:
                    do_print(f"Cannot set {text}: {e}.")
        if "done" in text or text == "":
            #if text == "":
                #do_print(assign_colour(f"(Chosen: <NONE>) [god_mode]", "yellow"))
            do_print("Returning to game with changes made.")
            break


def user_input():
    text = do_input()

    if text != None:
        text=text.strip()

    if text.lower() == "stats":
        do_print(f"    weird: [{game.weirdness}]. location: [{assign_colour(loc.currentPlace.name, 'loc')}]. time: [{game.time}]. weather: [{game.weather}]. checks: {game.checks}")
        inventory_names = get_inst_list_names(game.inventory)
        do_print(f"    inventory: {inventory_names}, inventory weight: [{len(inventory_names)}], carryweight: [{game.carryweight}]")
        do_print(f"    Player data: {game.player}")
        do_print()

    if text and text.lower() == "show visited":
        get_visited_map()
        text = None

    else:
        return text

def option(preamble=None):
    logging_fn()

    if preamble:
        print(preamble)
    print("\n")
    test=user_input()

    run_membrane(test)


def inner_loop(speed_mode=False):
    logging_fn()

    loc.currentPlace.visited = True
    loc.currentPlace.first_weather = game.weather

    while True:
        test=option()

def run():
    import config
    config.enable_tui = False
    #sleep(5) ## just pauses at a black screen, previous text already removed.
    global loc
    from env_data import locRegistry as loc
    #do_clearscreen()
    playernm = ""

    test_mode=True

    if test_mode:
        playernm = "Testbot"
    else:
        print()
        print("What's your name?")
        while  playernm == "":
            playernm = do_input()

    global game
    game = set_up(weirdness=True, bad_language=True, player_name=playernm)

    map_items = registry.instances_by_name("local map")
    print(f"MAP ITEMS: {map_items}")
    if map_items:
        for map in map_items:
            game.map_item = map
            setattr(map, "is_map", True)
            print(f"game.map_items: {game.map_item}")
            break
    if not test_mode:
        print("[[ Type 'help' for controls and options. ]]")
    print()
    print(f"You wake up in {assign_colour(loc.currentPlace.a_name, 'loc')}, right around {game.time}. You find have a bizarrely good sense of cardinal directions; how odd.")
    print(f"`{game.playername}`, you think to yourself, `is it weird to be in {assign_colour(loc.currentPlace.the_name, 'loc')} at {game.time}, while it's {game.weather}?`")
    print()
    from misc_utilities import look_around
    look_around()
    inner_loop(speed_mode=test_mode)
