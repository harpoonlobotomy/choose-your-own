# Choose your own adventure

import random
from pprint import pprint
import choices
import locations
from choices import loot

"""
Sample start:
Starting items: ['paperclip', 'puzzle magazine']

Starting game:
{'blind': True,
 'full': False,
 'hp': 5,
 'in love': True,
 'overwhelmed': True,
 'sad': False,
 'tired': True}

"""

def test_for_weird():

    if game.weirdness:
        value = random.randrange(0, 5)
        if value in (0, 1):
            game.w_value = 0
        else:
            game.w_value = 1

def set_inventory():

    #print(f"weird value: {game.w_value}")
    if game.w_value != 0:
        game.inventory = ["severed tentacle"]
        game.weirdness = True # what's the point of both weirdness and w_value? I guess w_value allows for severity later on.

    return

def loadout(): # for random starting items, game, etc (could be renamed

    game.inventory.append((loot.random_from("mags")))

    starting_items = loot.get_full_category("starting")
    #print(f"starting items: {starting_items}, type: {type(starting_items)}")
    k = random.randint(3, 6) # no check to make sure starting items contains enough to fulfil this. Probably should be.
    temp_inventory = random.sample(starting_items, k)
    for item in temp_inventory:
        game.inventory.append(item)
    if len(game.inventory) >= game.volume:
        to_drop = random.randint(0, len(game.inventory)-1)
        game.inventory.pop(to_drop)

    hp = random.randrange(4, 8)
    game.player.update({"hp":hp})
    game.emotional_summary = calc_emotions()

def calc_emotions():
    counter = 0

    for attr in choices.emotion_table:
        val = random.randint(-1,1)
        game.player[attr] = int(val)
        if game.player[attr] > 0:
            counter += 1

    if game.player["in love"]:
        counter -= 3
    #print(f"{game.player}")
    #print(f"emotional counter: {counter}")
    if counter in (-1, 0, 1):
        return "pretty okay overall"
    if counter >1:
        return "bit stressed"
    if counter <1:
        return "doing quite well"

def load_world():
    from env_data import weatherdict
    game.place = random.choice((game.loc_list))#"your home", "the city centre", "a small town", "the nature reserve", "the back alley", "a hospital", "a friend's house", "graveyard"))
    game.time = random.choice(choices.time_of_day)
    game.pops = random.choice(("few", "many"))
    weatherlist = list(weatherdict.keys())
    game.weather = random.choice((weatherlist))#"fine", "stormy", "thunderstorm", "raining", "a heatwave", "perfect", "cloudy"))
    game.bad_weather = weatherdict[game.weather].get("bad_weather")

    return game.place

def init_game():

    for attr in ["blind", "tired", "full", "sad", "overwhelmed", "in love"]: # options to be randomised at gamestart
        game.player.update({attr: random.choice((True, False))})

    test_for_weird()
    set_inventory()
    choices.set_choices()
    loadout()
    load_world()


def set_up(weirdness, bad_language, player_name): # skip straight to init_game to skip print
    game.weirdness = weirdness
    game.bad_language = bad_language
    game.playername = player_name
    game.facing_direction = random.choice(("north", "east", "south", "west"))
    init_game()
    #print(f"Player name: {player_name}")
    #print(f"Starting items: {game.inventory}")
    #print("Starting game:")
    #pprint(game.player)
    #print(f"Starting location: {game.place}")
    return game

class game:
    weirdness = False
    bad_language = False
    show_rolls = False
    w_value = 0
    checks = {
        "inventory_on": False,
        "play_again": False
    }
    inventory = ["paperclip"]
    playername = "Test"
    player = {
        "hp": 5,
        "tired": 0,
        "full": 0,
        "sad": 0,
        "overwhelmed": 0,
        "encumbered": 0,
        "blind": False,
        "in love": False,
        "inventory_management": True
        }

    emotional_summary = None

    place = "home"
    time = "morning"
    pops = "few"
    weather = "fine"
    bad_weather = False

    facing_direction = "north"

    currency = choices.currency
    carrier = choices.carrier
    volume = choices.volume

    loc_list = list(locations.descriptions.keys())

#set_up(weirdness, bad_language, player_name)

