# loot.name_col(item) == adding col to class
# assign_colour(text) == to print w colour

import choices
import env_data
from misc_utilities import assign_colour, col_list, col_text
from set_up_game import load_world, set_up, init_settings
from choices import choose, loc_loot
import random
from locations import run_loc, places, descriptions
from env_data import placedata_init, p_data
from pprint import pprint

from item_management_2 import ItemInstance, registry

user_prefs = r"D:\Git_Repos\Choose_your_own\path_userprefs.json"
run_again = False

yes = ["y", "yes"]
no = ["n", "no", "nope"]
night = ["midnight", "late evening", "night", "pre-dawn"]

import time

def slowLines(txt, speed=0.1):
    print(txt)
    time.sleep(speed)

def slowWriting(txt, speed=0.001): # remove a zero to set it to regular speed again.
    for c in str(txt):
        print(c, end='', flush=True)
        time.sleep(speed * random.uniform(0.2, 2))
    print()

def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s

def separate_loot(item):

    #to take an item which has children and make it into two parts.
    "children"
    entry = loc_loot.get_item(item)
    if entry:
        if entry.get('children'):
            for child in entry['children']:
                game.inventory.append(child)
                print(f"{child} separated from {item}")

def print_inventory():

    for item in game.inventory:
        if isinstance(item, ItemInstance):
            slowWriting(f"    {assign_colour(item)}") ### I kinda prefer it like this, line by line.
        elif isinstance(item, str):
            slowWriting(f"    {assign_colour(item)}")
        ## Might do a version of that where it makes 5 row columns, instead of just a singular long list.

def get_inventory_names():
    game.inventory_names = []
    for item in game.inventory:
        game.inventory_names.append(item.name)

def from_inventory_name(test):
    list_index=game.inventory_names.index(test)
    if list_index is not None:
        test=game.inventory[list_index]
        return test

def do_inventory():
    done=False
    slowWriting("INVENTORY: ")
    while done == False:
        print_inventory()
        get_inventory_names()
        test=option(game.inventory_names, print_all=True, none_possible=True, preamble="To examine an item more closely, type it here, otherwise hit 'enter' to continue.", inventory=True)
        #test = user_input()
        #print(f"Test: {test}")
        if not test or test=="" or test==None:
            done=True
            return test
        while True:
            if test and test in game.inventory_names:
                    #places[game.place].first_weather = game.weather
                # needs to be looking in [name].values().get("inv_name")

                test=from_inventory_name(test)
                ## need to get item instance from name, but maybe from index instead to allow for muultiple instances of same name. Done, I think.

                desc = registry.describe(test, caps=True)
                if desc and desc != "" and desc != f"[DESCRIBE] No such item: {test}":
                    slowWriting((f"Description: {col_text(desc, "description")}"))
                else:
                    print(f"Failed to describe from registry. Investigate. Data: {test}")
                    exit()
                    desc = loc_loot.describe(test, caps=True)
                    if desc and desc != "":
                        if test.colour != None:
                            colour = test.colour
                        else:
                            colour = "description"
                        slowWriting((f"Description: {col_text(desc, colour)}"))
                    else:
                        slowWriting(f"Not much to say about the {test}.")

                print()
            else:
                break

def god_mode():

    attr_dict={
        "time":choices.time_of_day,
        "weather":list(env_data.weatherdict.keys())
    }
    print("God mode: set game.[] parameters during a playthrough. For a print of all game.[] parameters, type 'game_all. Otherwise, just type the change you wish to make.")
    while True:
        text=input()
        if "game_all" in text:
            print("Trying to print all attr of 'game' class: ")
            attributes = [attr for attr in dir(game)
              if not attr.startswith('__')]
            print(f"attributes: {attributes}")
        if "print" in text:
            text=text.replace("print ", "")
            obj = getattr(game, text)
            if type(obj) == str:
                obj = attr_dict.get(obj)
            print(obj)
        if "game." in text:
            textstart, value=text.split("=")
            print(f"Text: {text}, textstart: {textstart}, value: {value}")
            if textstart in ("game.time", "game.weather", "game.place"):
                try:
                    if "time" in textstart:
                        game.time=value
                        print(f"{textstart} has been set: game.time: {game.time}")
                    if "weather" in textstart:
                        game.weather=value
                        print(f"{textstart} has been set: game.weather: {game.weather}")
                    if "place" in textstart:
                        game.place=value
                        print(f"{textstart} has been set: {assign_colour(game.place, 'loc')}")
                except Exception as e:
                    print(f"Cannot set {text}: {e}.")
        if "done" in text or text == "":
            print("Returning to game with changes made.")
            break

def user_input():
    text = input()
    if text.lower() == "godmode":
        print("Allowing input to set parameters. Please type 'done' or hit enter on a blank line when you're finished.")
        god_mode()
        print()
        return "done"
    if text.lower() == "help":
        print()
        slowWriting(f"  Type the (highlighted) words to progress, 'i' for 'inventory', 'd' to describe the environment, 'settings' to set some settings - that's about it.")
        print()
        return "done"
    if text.lower()== "settings":
        print()
        print("Settings:")
        init_settings(manual=True)
        print()
        return "done"
    if text.lower() == "stats":
        print()
        print(f"    weird: {game.weirdness}. location: {assign_colour(game.place, 'loc')}. time: {game.time}. weather: {game.weather}. checks: {game.checks}")
        get_inventory_names()
        print(f"    inventory: {game.inventory_names}, carryweight: {game.carryweight}")
        pprint(f"    {game.player}")
        print()
        return "done"
    if text.lower() == "i":
        print()
        do_inventory()
        print()
        return "inventory_done"
    if text.lower() == "d":
        loc_data = p_data[game.place]
        print(f"{text}: Describe location.")
        slowWriting(f"[{smart_capitalise(game.place)}]  {loc_data.overview}")
        obj = getattr(p_data[game.place], game.facing_direction)
        slowWriting(f"  You're facing {game.facing_direction}. {obj}\n")
        print()
#        print(f"{[game.place]}:{places[game.place].description}")#{descriptions[game.place].get('description')}")
        print()
        text=None # clear text to stop it picking 'dried flowers' after `describe location` runs.
        return "done"
    if text.startswith("drop "):
        print(f"Text starts with drop: {text}")
        textparts=text.split()[1:]
        print(f"textparts: {textparts}, len: {len(textparts)}")
        if len(textparts) > 1:
            textparts = " ".join(textparts[0:])
        else:
            textparts = textparts[0]
        item = registry.instances_by_name(textparts)
        print(f"Item: {item}, type: {type(item)}")
        if item:
            item=item[0]
            print(f"Sending item to drop: {item}")
            drop_loot(item)
        return "drop_done"
    if text and text.lower() in ("exit", "quit", "stop", "q"):
        # Should add the option of saving and returning later.
        print("Okay, bye now!")
        exit()
    else:
        return text

def option(*values, no_lookup=None, print_all=False, none_possible=True, preamble=None, inventory=False):

    values = [v for v in values if v is not None]
    # none_possible=True == "if blank input, consider it a viable return". I didn't need this before but I'm going to see if it fixes it.
    option_chosen = False
    #print(f"Values: {values}m len(values): {len(values)}")
    def get_formatted(values):
        if inventory:
            values = game.inventory ## force use the actual inventory instead of the list values.

        values = [v for v in values if v is not None]
        formatted = []
        for i, v in enumerate(values):
            if isinstance(v, (list, tuple)):
                if print_all:
                    v=col_list(v)
                    formatted.append(f"{', '.join(v)}")
                else:
                    formatted.append(f"{assign_colour(v[0])}") # add the first one as the 'label', use the rest as list later. ## NOTE: Just changed this, might break things.
            else:
                formatted.append(f"{assign_colour(v, i)}")
        return values, formatted

    values, formatted=get_formatted(values)
    while option_chosen != True:
        if inventory:
             values, formatted=get_formatted(values)
        if preamble:
            slowWriting(preamble)
        if len(formatted) > 1 and not inventory:
            slowWriting(f"    {', '.join(formatted[:-1])} or {formatted[-1]}") # this formatting is good visually, so don't change it before  this. The delineation here is preferable.
        elif len(formatted) > 1 and inventory:
            slowWriting(f"    {', '.join(formatted)}") # this formatting is good visually, so don't change it before  this. The delineation here is preferable.
        else:
            slowWriting(f"    {formatted[0]}")

        if no_lookup:
            return

        clean_values=[]
        if type(values) in (list, tuple, set):
            for value in values:
                if type(value) == str:
                    clean_values.append(value)
                elif isinstance(value, ItemInstance):
                    clean_values.append(value.name)
                else:
                    for value_deeper in value:
                        if type(value_deeper) == str:
                            clean_values.append(value_deeper) # I cannot imagine another layer of nesting here.

        test=user_input()
        if test in ("inventory_done", "description_done", "drop_done"): # testing this as an escape for post-Inventory management
            if test == "drop_done":
                get_inventory_names()
                values=game.inventory
            continue ## here, it loops. Which is usually good, but if I've dropped, it doesn't refresh the inventory and reprints the pre-dropped list.
        if none_possible and test=="":
            return None
        #print(f"Test: {test}")
        if not test or test == "":
            if test is None:
                return None

        if test.isdigit(): # if you type 1, it returns the first option, etc
            while test.isdigit():
                index = int(test)
                if 1 <= index <= len(clean_values):
                    test = clean_values[index - 1]
                    print(f"\033[1A{assign_colour(f'Chosen: ({test})', 'yellow')}")
                    return test
                print(f"{test} is not a valid option, please try again.")
                test=user_input()

        for v in clean_values:
            returning=None
            if len(test) == 1 and test.lower() == v[0].strip().lower():
                returning = v
            elif v.lower() == test.lower():
                returning = v
            elif v.lower().startswith("a ") or v.startswith("a "):
                if v.lower().startswith("a "):
                    new_v = v[2:] # this is 'everything after the first two, right?
                elif v.lower().startswith("an "):
                    new_v = v[3:]
                if test.lower() == v.strip().lower() or test.lower() == new_v.strip().lower():
                    returning = v
            else:
                if len(test) > 2 and test.lower() == choose.get(v.lower()):
                    returning = v

            if returning:
                print(f"\033[1A{assign_colour(f'Chosen: ({returning})', 'yellow')}")
                #print(f"\033[1A  Chosen: ({returning})")
                return returning

        if test in no:
            return no
        if test in yes:
            return yes

def roll_risk(rangemin=None, rangemax=None):

    # I want to make this variable. So I can weight it.
    min = 1
    max = 20 # this will do but isn't what I really want.
    if rangemin:
        min = rangemin
    if rangemax:
        max = rangemax

    results = [
    ((1, 4), "INJURY", 1),
    ((5, 11), "MINOR SUCCESS", 2),
    ((12, 18), "GREATER SUCCESS", 3),
    ((19, 20), "GREATEST SUCCESS!", 4)
    ]

    roll = random.randint(min, max)
    for r, msg, val in results:
        if r[0] <= roll <= r[1] or roll in r: #("if roll is between first and second part of the tuple, or is in the tuple itself", y?)  # supports both singletons and ranges
            if game.show_rolls:
                slowWriting(f"Roll: {roll}\n{msg}")
            return val

def outcomes(state, activity):
    item = None
    very_negative = ["It hurts suddenly. This isn't good...", f"You suddenly realise, your {assign_colour(item)} is missing. Did you leave it somewhere?[ NAME SHOULD BE COLOURED ]"]
    negative = [f"Uncomfortable, but broadly okay. Not the worst {activity} ever", f"Entirely survivable, but not much else to say about this {activity}.", f"You did a {activity}. Not much else to say about it really."]
    positive = [f"Honestly, quite a good {activity}", f"One of the better {activity}-based events, it turns out."]
    very_positive = [f"Your best {activity} in a long, long time."]

    outcome_table = {
        1: very_negative,
        2: negative,
        3: positive,
        4: very_positive
    }

    outcome = random.choice((outcome_table[state]))
    if "is missing. Did" in outcome: # should only run when dropping actually happens.
        if not game.inventory:
            dropped = "everything" # in case everything's already gone?
        else:
            dropped = random.choice((game.inventory))
            places[game.place].items.append(dropped) # stored in this location, can find it again later.
        item = dropped

    return outcome ## better? Not sure.

def drop_loot(named=None, forced_drop=False):
    get_inventory_names()
    #newlist = [x for x in game.inventory]
    if forced_drop: ## TODO: Set a limit on this so only value-based loot can be dropped.
        test = random.choice((game.inventory))
        #TODO: update location for test.
        newlist = [x for x in game.inventory if x is not test]
        game.inventory = newlist
        return
    if named:
        test=named
    else:
        if len(game.inventory) < 1:
            slowWriting("You don't have anything to drop!")
        #slowWriting("[[ Type the name of the object you want to leave behind ]]")
        #print(game.inventory)
        test = option(game.inventory_names, print_all=True, preamble="[Type the name of the object you want to leave behind]", inventory=True)
        #while test not in game.inventory and test not in ("done", "exit", "quit"):
        #    slowWriting("Type the name of the object you want to leave behind.")
        #    test = user_input()
    if test in game.inventory_names or isinstance(test, ItemInstance):
        if isinstance(test, ItemInstance):
            item_test=test

        else:
            print(f"Test in inventory names: {test}")
            item_test=from_inventory_name(test)

        game.inventory.remove(item_test)
        game.inventory_names.remove(item_test.name)
        print(f"test from inventory name: {test}")
        #print(f"test: {test}")
        # TODO: update location for test

        #print(f"newlist: {newlist}")
        #if isinstance(test, ItemInstance):
        #    test=test.name
        slowWriting(f"Dropped {assign_colour(test)}.")


    #print(f"game.inventory: {game.inventory}, named: {named}")
    slowWriting("Load lightened, you decide to carry on.")
    if game.checks["inventory_asked"] == False:
        slowWriting("[[ Psst. Hey. Type 'secret' for a secret hidden option, otherwise type literally anything else. ]]")
        game.player["inventory_asked"] = True
        test = user_input()
        if test == "secret":
            #slowWriting("Hey so... not everyone loves inventory management. So I'll give you the option now - do you want to turn it off and carry without limitation?")
            #slowWriting("         (yes) or (no)")
            #test = user_input()
            test=option("yes", "no", preamble="Hey so... not everyone loves inventory management. So I'll give you the option now - do you want to turn it off and carry without limitation?")
            if test in yes:
                game.player["inventory_management"] = False
                #slowWriting("Do you want to update this for future runs too?")
                update_settings_json=option("yes", "no", preamble="Do you want to update this for future runs too?")
                if update_settings_json in yes:
                    import json
                    with open("settings.json") as f:
                        data = json.load(f)
                        inventory_state=data["no_inv"]
                        if inventory_state == False and 'yes' in test: ## need to switch these around, currently have 'inventory management = true' == 'no_inv = False'. Should be equivalent for both.
                            data["no_inv"] = True
                        elif inventory_state != False and not 'yes' in test:
                            data["no_inv"] = False

                    with open("settings.json", "w+") as f:
                        json.dump(data, f)
                print("Settings updated. Returning.")

    get_inventory_names()
    print()

def switch_the(text, replace_with=""): # remember: if specifying the replace_with string, it must end with a space. Might just add that here actually...
    if isinstance(text, list):
        if len(text) == 1:
            text=text[0]
            text=text.name
        else:
            print("Trying to `switch_the`, but text is a list with more than one item.")
            exit()
    if isinstance(text, ItemInstance):
        text=text.name
    for article in ("a ", "an "):
        if text.startswith(article):# in text:
            if replace_with != "":
                #print(f"replace with isn't blank: `{replace_with}`")
                if replace_with[-1] != " ":
                    #print(f"replace with doesn't end with a space: `{replace_with}`")
                    replace_with = replace_with + " "
                    #print(f"replace with should now have a space: `{replace_with}`")
            text = text.replace(article, replace_with) # added 'replace with' so I can specify 'the' if needed. Testing.


    if replace_with == "" or replace_with == None: # should only trigger if neither article is in the text. This might need testing.
        text = "the "+ text # so I can add 'the' in front of a string, even if it doesn't start w 'a' or 'an'.
    return text

def move_item_any(item):
    game.inventory.append(item)
    slowWriting(f"[[ `{assign_colour(item)}` added to inventory.")

def get_loot(value=None, random=True, named="", message:str=None):
    item=None
    carryweight = game.carryweight
    #print(f"in get_loot: value: {value}, random: {random}, named: {named}, message: {message}")
    if named != "" and value == None: # don't add value for location items.
        print(f"Named in get_loot, about to go to pick_up_test: `{named}`, type: {type(named)}")
        if isinstance(named, str):
            item = registry.instances_by_name(named)
            if isinstance(item, list) and len(item) == 1:
                item=item[0]
        elif isinstance(named, ItemInstance):
            item = named
        print(f"item: {item}, type: {type(item)}")

        #pickup_test=loc_loot.pick_up_test(named) #should I test for get_item first? Probably no point. No.
        #if pickup_test == "No such item.":
        #    print("Not a location object.")
        #elif pickup_test == "Can pick up":
        #    #print("Can be picked up. Will let it continue, obj should get picked up.")
        #    item=named
        #elif pickup_test == "Cannot pick up": # is a positive failure - it was found, so is a loc item.
        #    print("Cannot be picked up. Print a message about how it can't be picked up. Maybe one per item for variation.")
        #    return None
        if not item:
            print(f"Failed to check pickupability. Count not get item instance. named: {named}.")

        #if not item:
        #    test_item = loot.get_item(named)
        #    if test_item:
        #        print("Item found in regular loot tables. Continuing.")
        #        item=test_item
        #if loc_loot.pick_up_test(named): # should this be negative or positive? More things to look at but not pick up, or the inverse?
        #    item = named

    elif random:
        #print(f"value: {value}")
        item = registry.random_from(value)
        print(f"Item: {item}, type: {type(item)}")
    else:
        print("Not random and no name given. This shouldn't happen, but defaulting to random.")
        print(f"value: {value}")
        item = registry.random_from(value)
    if isinstance(item, str):
        item = registry.instances_by_name(named)
        if isinstance(item, list):# and len(item) == 1: ## always pick first of the list for now
            item=item[0]
    #print(f"Item: {item}")
    if message:
        message = message.replace("[item]", assign_colour(item, None, nicename=registry.nicename(item)))
        message = message.replace("[place]", game.place)
        slowWriting(message)
    #item = loot.get_item(item)
    if item:
        _, game.inventory = registry.pick_up(item, game.inventory, game.place, game.facing_direction)
        slowWriting(f"{assign_colour(item)} added to inventory.")
    #move_item_any(item)

### drop random item if inventory full // not sure if I hate this. ###
    if len(game.inventory) > carryweight:
        print()
        #switched = switch_the(item, 'the ')
        test = option(f"drop", "ignore", preamble=f"It looks like you're already carrying too much. If you want to pick up {assign_colour(item, None, nicename=registry.nicename(item), switch=True)}, you might need to drop something - or you can try to carry it all.")
        if test in ("ignore", "i"):
            slowWriting("Well alright. You're the one in charge...")

            if game.player["encumbered"]: # 50/50 chance to drop something if already encumbered and choose to ignore
                outcome = roll_risk()
                if outcome in (1, 2):
                    #print(f"Forced to drop something.") #TODO: remove this later.
                    drop_loot(forced_drop=True) # force drop something.
                    print("You feel a little lighter all of a sudden...") ## does not add the item to the location yet. Have to do that.
            if len(game.inventory) > game.carryweight:
                game.player["encumbered"] = True
            else:
                game.player["encumbered"] = False

        else:
            slowWriting("You decide to look in your inventory and figure out what you don't need.")
            drop_loot()
    print()
    return item

def have_a_rest():
    slowWriting("You decide to take it easy for a while.")
    # can do things like read a book, check phone if you have them, daydream (roll for it), etc.
    print()
    slowWriting("But after a while, you decide to get up anyway.")
    look_around()

def get_hazard():
    inside = getattr(p_data[game.place], "inside")
    if inside:
        options = choices.trip_over["any"] + choices.trip_over["inside"]
    else:
        options = choices.trip_over["any"] + choices.trip_over["outside"]
    hazard = random.choice(options)
    return hazard

def relocate(need_sleep=None):
    options = []

    current_loc = game.place
    current_weather = game.weather

    times_of_day = choices.time_of_day
    time_index=times_of_day.index(game.time)
    new_time_index=time_index + 1 # works
    if new_time_index == len(times_of_day):
        new_time_index=0
    game.time=times_of_day[new_time_index]

    weather_options = list(env_data.weatherdict)
    weather_index=weather_options.index(game.weather)
    weather_variance=random.choice([int(-1), int(1)])
    new_weather_index=weather_index + int(weather_variance)
    if new_weather_index == len(weather_options):
        new_weather_index=0
    game.weather=weather_options[new_weather_index]

    while len(options) < 3:
        new_place = random.choice((game.loc_list))
        if new_place not in options: # and new_place != current_loc <- turn on when I don't want current loc as an option anymore.
            options.append(new_place)

    new_location = option(options, print_all=True, preamble="Please pick your destination:")
    if new_location in options:
        game.place=new_location
        load_world(relocate=True)

    if game.place==current_loc:
        print(f"You decided to stay at {switch_the(game.place, 'the')} a while longer.")
    else:
        slowWriting(f"You make your way to {assign_colour(game.place, 'loc')}. It's {game.time}, the weather is {game.weather}, and you're feeling {game.emotional_summary}.")
        if places[game.place].visited:
            slowWriting(f"You've been here before... It was {places[game.place].first_weather} the first time you came.")
            if places[game.place].first_weather == game.weather:
                print(places[game.place].same_weather)
        else:
            places[game.place].visited = True # maybe a counter instead of a bool. Maybe returning x times means something. No idea what. Probably not.
            places[game.place].first_weather = current_weather

    if need_sleep:
        decision = option("rest", "look", preamble="You're getting exhausted. You can look around if you like but the sleep deprivation's getting to you.")
        if decision == "rest":
            if places[game.place].inside == False:
                sleep_outside()
            else:
                sleep_inside()
        else:
            look_around(status="exhausted")
    else:
        look_around()

def sleep_outside():
    if getattr(p_data[game.place], "nature"):
        slowWriting("You decide to spend a night outside in nature.")
    else:
        slowWriting(f"You decide to spend a night outside in {assign_colour(switch_the(game.place, "the "), 'loc')}.")
    if not game.bad_weather:
        slowWriting("Thankfully, the weather isn't terrible at least.")
        slowWriting("You sleep until morning.")
        the_nighttime()
    else:
        slowWriting(f"Unfortunately, it's {game.weather}")
        slowWriting("You can weather it out (no pun intended) or try a last minute relocation - what do you do?")
        decision = option("stay", "move")
        if decision == "stay":
            risk = roll_risk()
            outcome = outcomes(risk, "sleep")
            slowWriting(outcome)
            slowWriting("Something else happens here. Who knows what. Interactive dream scene.")
            the_nighttime()
        else:
            relocate(need_sleep=True)

def sleep_inside():
    slowWriting(f"Deciding to hunker down in {assign_colour(switch_the(game.place, "the "), 'loc')} for the night, you find the comfiest spot you can and try to rest.")
    risk = roll_risk(10, 21)
    outcome = outcomes(risk, "sleep")
    slowWriting(outcome)
    the_nighttime()

def the_nighttime():
    print()
    slowWriting("Finally asleep, you dream deeply.")
    slowWriting("  ...")
    print()
    slowWriting("    ...")
    print()
    slowWriting("       ...")
    print()
    slowWriting("Imagine a dream here. Something meaningful...")
    slowWriting("And/or wild animals if sleeping outside, and/or people, and/or ghosts/monster vibes if weird.")
    new_day()

def look_around(status=None):
    item = None
    place = game.place
    time = game.time
    weather = game.weather

    def look_dark():
        if ("torch" or "phone" or "matchstick") not in game.inventory:
            if descriptions[place].get("electricity"):
                test=option("yes", "no", preamble="It's dark, but you can try to find a light switch if you want.")
                if test in yes:
                    outcome = roll_risk()
                    if outcome in (1, 2):
                        slowWriting("Try as you might, you can't find a lightswitch...")
                    else:
                        slowWriting("The light flickers on - you can see.")
                        look_light(reason="electricity")

            test=option("yes", "no", preamble=f"It's too dark to see much of anything in {assign_colour(switch_the(game.place, "the "), 'loc')}, and without a torch or some other light source, you might trip over something. Do you want to keep looking?")
            if test in yes:
                slowWriting("Determined, you peer through the darkness.")
                outcome = roll_risk()
                if outcome == 1:
                    slowWriting("OW! You roll your ankle pretty badly.")
                    if len(game.inventory) < 4:
                        item = get_loot(1, random=True, message=f"It's only a minor injury, sure, but damn it stings. You did find [item] while facefirst in the middle of [place], though.")
                        #slowWriting(f"It's only a minor injury, sure, but damn it stings. You did find {item} while facefirst in the middle of {place}, though.") # don't need these two lines. Need to combine them into just the loot message..
                    if game.w_value:
                        ("You see something shimmer slightly off in a bush, but by the time you hobble over, whatever it was has vanished.")
                if outcome == 2:
                    hazard = get_hazard()
                    item = get_loot(1, random=True, message=f"Narrowly avoiding tripping over {hazard}, you find [item]. Better than nothing, but probably all you'll find until there's more light.") # want options for the poorly lit hazard part.
                    # game.carrier_size compared to item.size? Can I be bothered?
                if outcome in (3,4):
                    item = get_loot(2, random=True, message=f"Once your eyes adjust a bit, you manage to make out more shapes than you expected - you find [item].")
            if test in no:
                slowWriting("Thinking better of it, you decide to keep the advanced investigations until you have more light. What now, though?")
            test = option("stay", "go", preamble=f"You could stay and sleep in {assign_colour(switch_the(game.place, "the "), 'loc')} until morning, or go somewhere else to spend the wee hours. What do you do?")
            if test in ("sleep", "stay"):
                if places[game.place].inside == False:
                    sleep_outside()
                else:
                    sleep_inside()
            else:
                slowWriting(f"Keeping in mind that it's {time} and {weather}, where do you want to go?")
                relocate()

        else:
            slowWriting("Using your torch, you see things. Probably. I haven't written this yet. How do you have a torch?!?")

    def look_light(reason=None):
        skip_intro=False
        if reason == "turning" or reason == "skip_intro":
            skip_intro=True
        elif reason == None:
            reason = "the sun"
        if skip_intro==False: # if there are no other reason to skip intro, can just combine the above into one 'if/else'.
            slowWriting(f"Using the power of {reason}, you're able to look around {assign_colour(switch_the(game.place, "the "), 'loc')} without too much fear of a tragic demise.")
        obj = getattr(p_data[game.place], game.facing_direction)
        #print(f"\n{obj}\n")
        print(f"\n  You're facing {assign_colour(game.facing_direction)}. {obj}\n") # description
        if obj == None or obj == "None":
            print("This description hasn't been written yet... It should have some ")
        remainders = list(x for x in game.cardinals if x is not game.facing_direction)
        #print(f"Directions to look: {remainders}")
        potential = choices.location_loot[game.place].get(game.facing_direction)
        if potential:
            #print(f"Interactable items: {list(potential.keys())}") # this is not defined per facing_direction. Needs to be.
        #slowWriting(f"You can look around more, or try to interact with the environment:")
            potential=list(potential.keys())
        else:
            potential=None
        text=None
        while not text:
            text=option(remainders, "leave", potential, no_lookup=None, print_all=True, preamble="You can look around more, leave, or try to interact with the environment:")

        if text == "leave":
            slowWriting(f"You decide to move on from {assign_colour(switch_the(game.place, "the "), 'loc')}")
            relocate()
        if text in remainders:
            game.facing_direction=text
            look_light("turning") # run it again, just printing the description of where you turned to.
        if text != "" and text is not None:
            if text in obj or text in potential:
                #print(f"Text: {text}, obj: {obj}")
                if text in list(potential):
                #for option_entry in options: ## 'if text in options', surely?
                #    if text in option_entry: # this gets 'television' if I type 'e'. Not working...
                    #print(f"text just before get_item: {text}")
                    #print(f"loc loot: {loc_loot}")
                    #print(f"text: {text}")
                    #item_entry = getattr(loc_loot[game.place][game.facing_direction], text)
                    item_entry = registry.instances_by_name(text)
                    item_entry = item_entry[0] ## TODO: Fix this, it's always defaulting to the first one and it shouldn't, will break dupes when they're introduced.
                    #item_entry = registry.get_item(text)
                    #print(f"item entry: {item_entry}")
                    if item_entry:
                        print(f"{registry.describe(item_entry, caps=True)}")
                        #print("What do you want to do? [Investigate] item, [take] item, [leave] it alone.") # Do I want to list the options like this, or just try to make a megalist of what options may be chosen and work from that?
                        decision=option("investigate", "take", "leave", preamble=f"What do you want to do with {assign_colour(text, switch=True)} - investigate it, take it, or leave it alone?")
                        #print(f"text after decision: {text}")
                        #decision=user_input()
                        if decision.lower()=="investigate":
                            print("Nothing here yet.")
                        elif decision.lower()=="take":
                            #print(f"text in decision lower == take: {text}")
                                ## Might have to change how I do this. Currently, flowers + jar are listed separately from each other, but when picked up are one unit.
                                # Maybe I need to rename the glass jar, if children, glass jar with flowers, otherwise just glass jar when they're separated.
                            picked_up = get_loot(value=None, random=True, named=text, message=None)
                            #if picked_up:
                            #    if text not in game.inventory:
                            #        game.inventory.append(text) # doing this here, so the children aren't added, but are part of the main object.
                            #    #print(f"To set location: {picked_up}, {assign_colour(game.place, 'loc')}, {game.facing_direction}")
                            #    set_items:list = loc_loot.set_location(picked_up, game.place, game.facing_direction, picked_up=True) ## I'm dong this inside get loot too. Shouldn't need todo this, it's silly. ## also it breaks if inventory isn't in local loot immediately.
                            #    for item_name in set_items:
                            #        #print(f"Full list before: {choices.location_loot[game.place][game.facing_direction]}")
                            #        #print("testing: choices.location_loot[game.place][game.facing_direction].pop(picked_up)")
                            #        choices.location_loot[game.place][game.facing_direction].pop(item_name)
                                    #print(f"Full list after: {choices.location_loot[game.place][game.facing_direction]}")
                            #    print("[Find the loot taking function that already exists, make sure the item is removed from the list here.]") # does the current loot table allow for 'already picked up'? I don't think it does. Need to do that.
                        elif decision.lower()=="leave":
                            print(f"You decide to leave the {assign_colour(text)} where you found it.")
                        # this should loop, not just kick you out and relocate you immediately.
                    else:
                        print(f"No entry in loc_loot for {item_entry}")
                else:
                    print(f"Could not find what you're looking for. The options: {potential}")
                    #for item in options:
                    #    item_entry = loc_loot.get_item(item)
                    #    print(f"item_entry: {item_entry}")
            #print("You've typed something that's in the location description. Sadly I haven't written anything else yet...")
                #else:
        #slowWriting() # list of cardinals except the one you're looking in already.
                    #print(f"txt is not in remainders or in options: {text}")
    # Not adding anything else here for "leave" because the default route currently is relocate anyway. If this changes:: Must have 'relocate' option for "leave" entry.
        slowWriting("Unfortunately I haven't written anything here yet. Maybe just... go somewhere else?")
        slowWriting(f"Keeping in mind that it's {time} and {weather}, where do you want to go?")
        relocate()

    if status == "exhausted" and time not in night:
        slowWriting("Stumbling, you're going to hurt yourself even if it's nice and bright. Haven't written it yet though.")
        look_dark() # new one for this with light variation. Maybe 'looking' should be a class... It's going to be a major part of it....

## ==== Actual start here ===

    inside = getattr(p_data[game.place], "inside")
    if inside:
        add_text="outside " # just so it says 'with the weather outside raining, instead of 'with the weather raining'. Either way it's a poorly constructed sentence though.
    else:
        add_text=""
    slowWriting(f"With the weather {add_text}{game.weather}, you decide to look around the {game.facing_direction} of {assign_colour(switch_the(game.place, 'the '), 'loc')}.")
    if time in night:
        slowWriting(f"It's {game.time}, so it's {random.choice(choices.emphasis["low"])} dark.") # trying a bit more variation in the benign text.
        look_dark()
    else:
        if places[game.place].sub_places:
            for sub_place in places[game.place].sub_places:
                print(f"[[[[  sub_place: {sub_place}  ]]]]") # this has never printed.
        else:
            look_light("skip_intro")

def new_day():
    #print("You wake up ")
    if game.loop==False:
        decision = option("yes", "no", preamble="Keep looping?")
        if decision in no:
            slowWriting("Hope you had fun? Not sure really what this is, but thank you.")
            exit()

    game.checks["play_again"]
    game.time = random.choice(["pre-dawn", "early morning", "mid-morning"]) # sometime in the morning, we awaken.
    inner_loop()

def describe_loc():
    ## Needs to also describe weather here.
    loc_data = p_data[game.place]
    slowWriting(f"You take a moment to take in your surroundings. {loc_data.overview}")
    test=option(game.cardinals, "go", print_all=True, preamble="Pick a direction to investigate, or go elsewhere?")
    if test in game.cardinals:
        game.facing_direction = test
        look_around()
    else:
        slowWriting(f"You decide to leave {assign_colour(switch_the(game.place, 'the '), 'loc')}")
        relocate()

def inner_loop():

    slowWriting(f"You wake up in {assign_colour(game.place, 'loc')}, right around {game.time}. You find have a bizarrely good sense of cardinal directions; how odd.")
    places[game.place].visited = True
    places[game.place].first_weather = game.weather

    slowWriting(f"`{game.playername}`, you think to yourself, `is it weird to be in {assign_colour(game.place, 'loc')} at {game.time}, while it's {game.weather}?`")
    print()
    describe_loc()

    test=option("stay", "go", preamble="What do you want to do? Stay here and look around, or go elsewhere?")
    if test in ("stay, look"):
        slowWriting("You decide to look around a while.")
        look_around()
    else:
        relocate()

def intro():

    #First run setup
    # ascii from https://patorjk.com/software/taag/#p=display&f=Big+Money-ne&t=paths&x=none&v=4&h=4&w=80&we=false
    print("\n")
    slowLines("                          /================================ #")
    slowLines("                         /                                  #")
    slowLines("   # ===================/     /$$     /$$                   #")
    slowLines("   #                         | $$    | $$                   #")
    slowLines("   #     /$$$$$$   /$$$$$$  /$$$$$$  | $$$$$$$   /$$$$$$$   #")
    slowLines("   #    /$$__  $$ |____  $$|_  $$_/  | $$__  $$ /$$_____/   #")
    slowLines(r"   #   | $$  \ $$  /$$$$$$$  | $$    | $$  \ $$|  $$$$$$    #")
    slowLines(r"   #   | $$  | $$ /$$__  $$  | $$ /$$| $$  | $$ \____  $$   #")
    slowLines("   #   | $$$$$$$/|  $$$$$$$  |  $$$$/| $$  | $$ /$$$$$$$/   #")
    slowLines(r"   #   | $$____/  \_______/   \___/  |__/  |__/|_______/    #")
    slowLines("   #   | $$                                                 #")
    slowLines("   #   | $$       /======================================== #")
    slowLines("   #   |__/      /")
    slowLines("   #            /")
    slowLines("   # ==========/")
    print("\n")
    print("To play: ")
    print("Type the words in parentheses, or select by number")
    print("    eg: for [[  (stay) or (go))  ]], '1' would choose 'stay'.")

def run():

    print("\n \n")
    global game
    run_loc()
    placedata_init()
    rigged=True # this one's just for the name/intro skip, doesn't affect weather etc.
    if rigged:
        playernm = "Testbot"
    else:
        intro()
        print()
        slowWriting("What's your name?")
        playernm = input() # is not 'user_input' because we don't want the inventory actions available until game is initialised.
    game = set_up(weirdness=True, bad_language=True, player_name=playernm)
    ## set starting inventory colours now
    col_list(game.inventory)

    print()
    slowWriting("[[ Type 'help' for controls and options. ]]")
    print()
    inner_loop()

#run() # uncomment me to actually play again.




def test():
    import os
    os.system("cls") ##<-- run this first to get the ansi to work later

    game = set_up(weirdness=True, bad_language=True, player_name="A")
    from tui_elements import run_tui_intro
    tui_placements, player_name = run_tui_intro() # Hopefully use tui_placements to directly print to the printable area, instead of having to reroute each part manually.

    if player_name:
        game.playername = player_name

    world = (game.place, game.weather, game.time, game.day_number)
    player = (game.player, game.carryweight, game.playername)

    from tui_elements import add_infobox_data, print_text_from_bottom_up, print_commands

    tui_placements = add_infobox_data(tui_placements, print_data = True, backgrounds = False, inventory=game.inventory, playerdata=player, worldstate=world)
    print_commands(backgrounds=False)
    print_text_from_bottom_up(None, input_text=" ")

    from tui_update import update_playerdata, update_worlddata

    update_playerdata(tui_placements, hp_value=8, carryweight_value=17)

    update_worlddata(tui_placements, weather="perfect", time_of_day="midday", location="a graveyard")

    print(f"\033[5B", end='')

test()

"""
tui_ placements: (values for fullscreen at 16/12/25)
'inv_start': (7, 11),
'inv_end': (12, 125),
'playerdata_start': (7, 132),
'playerdata_end': (12, 175),
'worldstate_start': (7, 182),
'worldstate_end': (12, 226),
'input_line': 57,
'text_block_start': (21, 22),
'text_block_end': (53, 215),
'commands_start': (15, 23),
'commands_end': (16, 215),
'cols': 237, 'rows': 64,
'spacing': 3,
'no_of_spacers': 16,
'linelength': 188,
'line_str': '
'up_lines': [18, 54],
'printable_lines': [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53],
'inv_positions': [(0, 7), (0, 42), (0, 77), (1, 7), (1, 42), (1, 77), (2, 7), (2, 42), (2, 77), (3, 7), (3, 42), (3, 77), (4, 7), (4, 42), (4, 77)],
'playerdata_positions': [(1, 14), (2, 19), (4, 5), (5, 10)],
'worldstate_positions': [(1, 24), (2, 15), (3, 19), (4, 36)]}
"""
