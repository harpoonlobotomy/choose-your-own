# Choose your own adventure

import random
from env_data import locRegistry as loc
from itemRegistry import registry, new_item_from_str
import choices
from logger import logging_fn
import misc_utilities


def test_for_weird():

    if game.weirdness:
        value = random.randrange(0, 5)
        if value in (0, 1):
            game.w_value = 0
        else:
            game.w_value = 1

def set_inventory():

    if game.w_value != 0:
        instances = registry.by_name.get("severed tentacle")
        if not instances:
            from item_dict_gen import generator
            item_dict = generator.item_defs.get("severed tentacle")
            instance = new_item_from_str(item_name="severed tentacle", loc_cardinal=(loc.inv_place), partial_dict=item_dict)
            if instance:
                loc.inv_place.items.add(instance)
        else:
            instance = registry.move_item(instances[0], location = loc.inv_place)

        game.weirdness = True

def loadout():

    set_inventory()
    paperclip_inst = registry.get_item_from_defs("paperclip")
    registry.move_item(paperclip_inst, location=loc.inv_place)
    #paperclip_list = registry.instances_by_name("paperclip")

    #registry.pick_up(paperclip_inst, starting_objects=True)

    ### Need to get list of item def entries with 'magazine'
    magazines = registry.item_def_by_attr(loot_type="magazine")
    #print(f"MAGAZINES: {magazines}")
    mag_choice = random.choice(magazines)
    instances = registry.instances_by_name(mag_choice)
    if not instances:
        from item_dict_gen import generator
        item_dict = generator.item_defs.get(mag_choice)
        instance = new_item_from_str(item_name=mag_choice, loc_cardinal=(loc.inv_place), partial_dict=item_dict)
        if instance:
            loc.inv_place.items.add(instance)
    else:
        instance = registry.move_item(instances[0], location = loc.inv_place)

    game.carryweight = 12

    starting_items = registry.instances_by_category("starting") ## starting items ==

    if game.carryweight-3 > 5:
        k = random.randint(5, game.carryweight-3) # changed to set max at game.carryweight, so I don't need to pop them later.
        if k > int(len(starting_items)):
            k=len(starting_items)
        temp_inventory = random.sample(list(starting_items), k)
        for item in temp_inventory:
            if item == None:
                continue
            registry.move_item(item, location=loc.inv_place)

def calc_emotions():
    counter = 0

    for attr in choices.emotion_table:
        if attr == "encumbered":
            game.player[attr] = 0
            continue
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
    logging_fn()
    textline = "Starting load_world in set_up_game.py"
    print(textline)
    from misc_utilities import underline_central
    underline_central(textline)

    from env_data import weatherdict

    rigged = False#True
    rig_weather = "perfect"
    rig_time = "midnight"

    if loc.currentPlace != None:
        loc.last_loc = loc.currentPlace

    if rigged:
        loc.set_current(new_loc)
        game.time=rig_time
        game.weather=rig_weather

    elif not relocate:
        game.time = random.choice(choices.time_of_day)
        weatherlist = list(weatherdict.keys())
        game.weather = random.choice(weatherlist)
        if not new_loc:
            new_loc = (random.choice(list(loc.places.values())))

    if new_loc:
        loc.set_current(new_loc)

    return loc.currentPlace


def init_game():

    game.player.update({"hp":random.randrange(4, 8)})
    game.emotional_summary = calc_emotions()
    import config

    test_for_weird()
    #choices.set_choices()
    load_world(new_loc=config.starting_location_str) # always start at graveyard
    #initialise_itemRegistry()
    loadout() ## move loadout after load_world to allow for time_management to run first. Testing...
    #print("Initial inventory:: ", game.inventory)

def set_up(weirdness, bad_language, player_name): # skip straight to init_game to skip print
    game.weirdness = weirdness
    game.bad_language = bad_language
    game.playername = player_name
    game.facing_direction = random.choice(list(misc_utilities.cardinal_cols.keys()))
    game.painting = random.choice(choices.paintings)
    init_game()

    return game

class game:
    map_item = None
    weirdness = False
    bad_language = False
    show_rolls = False
    w_value = 0
    text_speed=1
    luck=1
    loop=True

    checks = {
        "inventory_asked":False,
        "inventory_on": False,
        "play_again": False
    }
    #inventory_names = list()
    playername = "Test"
    player = {
        "hp": 5,
        "blind": False,
        "in love":False,
        "inventory_management": True,
        "inventory_asked": False ## Just so it only asks once per playthrough.
        }

    if player.get("full"):
        player.update({"hungry":-1})

    emotional_summary = None

    import config
    place = config.starting_location_str
    time = "mid-morning"
    #pops = "few"
    weather = "fine"
    bad_weather = False

    has_fire = False

    facing_direction = config.starting_facing_direction

    currency = choices.currency
    carrier = choices.carrier
    carryweight = choices.carryweight
    painting = "a ship in rough seas"
    cardinals = ["north", "south", "east", "west"]

    #from env_data import locRegistry
    #loc_list = list(locRegistry.places.values()) # just run it directly from loc within the game as needed.
    day_number=1

    last_loc = config.starting_location_str # just here to keep the persistence if things get distracted during a scene change

#set_up(weirdness, bad_language, player_name)

if __name__ == "__main__":
    set_up(weirdness=True, bad_language=True, player_name="Testing")
