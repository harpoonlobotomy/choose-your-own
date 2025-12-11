# Choose your own adventure

import random
import env_data
from item_management_2 import initialise_registry, registry
import locations
import choices
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


    #print(f"Registry after initialise: {registry.instances}")
    #print(f"weird value: {game.w_value}")
    if game.w_value != 0:
        registry.pick_up("severed tentacle", game.inventory, is_id=False)
        print(f"back after item management: game.inventory :: {game.inventory}")
        game.weirdness = True # what's the point of both weirdness and w_value? I guess w_value allows for severity later on.

    return

def loadout(): # for random starting items, game, etc (could be renamed
    ##
#        something like this being used maybe  , exclude_none=True
    paperclip = registry.instances_by_name("paperclip")[0].id
    print(f"Paperclip: {paperclip}")

    _, game.inventory = registry.pick_up(paperclip, game.inventory)
    _, game.inventory = registry.pick_up(registry.random_from("magazine"), game.inventory)

    print(f"Game inventory after managizine added: {game.inventory}")
    starting_items = registry.instances_by_category("starting") ## starting items == list of instances
    #print(f"starting items: {starting_items}, type: {type(starting_items)}")
    k = random.randint(5, game.carryweight-1) # changed to set max at game.carryweight, so I don't need to pop them later.
    if k > len(starting_items):
        k=len(starting_items)
    print(f"random int from 3_to_game.vol: {k}, game.carryweight: {game.carryweight}")
    print(f"starting_items: {starting_items}")
    temp_inventory = random.sample(starting_items, k)
    for item in temp_inventory:
        if item == None:
            continue
        game.inventory.append(item.id)

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

def load_world(relocate=False, rigged=False, new_loc=None):

    from env_data import weatherdict
    rigged = False#True
    rig_place = "a graveyard"
    rig_weather = "perfect"
    rig_time = "midday"

    if rigged:
        game.time=rig_time
        game.place=rig_place
        game.weather=rig_weather
    else:
        if not relocate:
            game.time = random.choice(choices.time_of_day) ## should only be random at run start, not relocation.
            weatherlist = list(weatherdict.keys())
            game.weather = random.choice(weatherlist)#"fine", "stormy", "thunderstorm", "raining", "cloudy", "perfect", "a heatwave"))
            game.place = random.choice((game.loc_list))#"your home", "the city centre", "a small town", "the nature reserve", "the back alley", "a hospital", "a friend's house", "graveyard"))

    if game.place != None:
        game.last_loc = game.place
    #game.pops = random.choice(("few", "many"))
    game.bad_weather = weatherdict[game.weather].get("bad_weather")

    return game.place

def set_text_speed():
    print("[Default test printing speed is 1. 0.1 is very slow, 2 is very fast.]")
    while True:
        text=input()
        if text=="":
            print("Keeping current text speed.")
            return
        try:
            new_text_speed=float(text)
        except:
            print("Please enter a number between 0.1 and 2, or hit 'enter' to keep default.")
        if new_text_speed:
            if 0.1<=new_text_speed<=2:
                return new_text_speed
            else:
                print("Please enter a text speed between 0.1 and 2.0")

def set_luck():
    print("Note: The game is calibrated to the default luck value (1). Reducing this value makes the game harder, while increasing the value makes it easier.")
    print("Please enter the luck value (from 0.1 to 2):")
    while True:
        text=input()
        if text=="":
            print("Keeping current luck value.")
            return
        try:
            new_luck=float(text)
        except:
            print("Please enter a number between 0.1 and 2, or hit 'enter' to keep default.")
        if new_luck:
            if 0.1<=new_luck<=2:
                return new_luck
            else:
                print("Please enter a luck value between 0.1 and 2.0")

def init_settings(manual=False):
    need_update=False
    import json
    with open("settings.json") as f:
        data = json.load(f)

    if data["initialised"] and not manual:
        game.text_speed = data["text_speed"]
        game.luck=data["luck"]
        game.loop=data["loop"]
    else:
        if not manual:
            print("First time setup:")
        print(f"To change text speed, enter a number (0.1 to 2), or hit enter to continue with current speed ({game.text_speed}). Default is (1)")
        new_speed=set_text_speed()
        if new_speed != None and new_speed != game.text_speed:
            game.text_speed=new_speed
            data["text_speed"]=new_speed # note: don't forget to write to the json again.
            need_update=True
        print(f"Text speed set to {game.text_speed}. To change luck value, enter a number (0.1 to 2), or hit enter to continue with current luck value ({game.luck}). Default is (1).")
        new_luck=set_luck()
        if new_luck != None and new_luck != game.luck: ## need a version of this that works for in-game setings update too.
            game.luck=new_luck
            data["luck"]=new_luck
            need_update=True # not needed here as we have to update the initialised setting regardless, else it'll run this every time..
        print(f"Luck value set to {game.luck}.")
        if not manual:
            print("These settings can be changed later by typing 'settings' in-game.")
        data["initialised"] = True
        if (manual and need_update) or not manual: #not sure if this is right.
            with open("settings.json", "w+") as f:
                json.dump(data, f)
            print("Settings updated. Returning.")





def init_game():

    for attr in ["blind", "tired", "full", "sad", "overwhelmed", "in love"]: # options to be randomised at gamestart
        game.player.update({attr: random.choice((True, False))})

    init_settings()
    test_for_weird()
    #choices.set_choices()
    load_world()
    initialise_registry()
    set_inventory()
    loadout() ## move loadout after load_world to allow for time_management to run first. Testing...
    print("Initial inventory:: ", game.inventory)

def set_up(weirdness, bad_language, player_name): # skip straight to init_game to skip print
    game.weirdness = weirdness
    game.bad_language = bad_language
    game.playername = player_name
    game.facing_direction = random.choice(("north", "east", "south", "west"))
    game.painting = random.choice(choices.paintings) # new, testing. Only needed for city hotel room at present. May update later if more locations. Nice to have semi-randomised location aspects.
    #print(f"game.painting: {game.painting}")
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
    text_speed=1
    luck=1
    loop=True

    checks = {
        "inventory_on": False,
        "play_again": False
    }
    inventory = list()
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

    inv_colours = {(i for i in inventory): None}
    emotional_summary = None

    place = "home"
    time = "morning"
    #pops = "few"
    weather = "fine"
    bad_weather = False

    facing_direction = "north"

    currency = choices.currency
    carrier = choices.carrier
    carryweight = choices.carryweight
    painting = "a ship in rough seas"
    cardinals = ["north", "south", "east", "west"]
    loc_list = list(locations.descriptions.keys())

    colour_counter = 0

    last_loc = "a graveyard" # just here to keep the persistence if things get distracted during a scene change

#set_up(weirdness, bad_language, player_name)

if __name__ == "__main__":
    set_up(weirdness=True, bad_language=True, player_name="Testing")
