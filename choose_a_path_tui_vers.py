# loot.name_col(item) == adding col to class
# assign_colour(text) == to print w colour

import choices
import env_data
from misc_utilities import assign_colour, col_list
from set_up_game import load_world, set_up, init_settings
from choices import choose, loc_loot
import random
from locations import run_loc, places, descriptions
from env_data import placedata_init, p_data
from pprint import pprint
import time

from item_management_2 import ItemInstance, registry

from tui_elements import run_tui_intro
from tui_elements import add_infobox_data, print_commands
from tui_update import update_infobox, update_text_box

print("Importing choose_a_path_tui_vers.py")

user_prefs = r"D:\Git_Repos\Choose_your_own\path_userprefs.json"
run_again = False

END="\x1b[0m"
RESET = "\033[0m"
HIDE = "\033[?25l"
SHOW = "\033[?25h"

yes = ["y", "yes"]
no = ["n", "no", "nope"]
night = ["midnight", "late evening", "night", "pre-dawn"]


def slowLines(txt, speed=0.1, end=None, edit=False):
    update_text_box(to_print=txt, end=False, edit_list=edit)
    update_text_box(to_print="  ", end=False)

def do_input():

    print(SHOW, end='')
    text=input()
    print(HIDE, end='')
    do_print(assign_colour)
    update_text_box(to_print=[f"{assign_colour(f'Chosen: ({text})', 'yellow')}", " "])
    return text

def do_print(text=None, end=None, edit_list=False):
    if text==None:
        text=" "
    slowLines(txt=text, speed=0.1, end=end, edit=edit_list)

def slowWriting(txt, speed=0.001, end=None): # remove a zero to set it to regular speed again.

    update_text_box(to_print=txt, end=end)
    update_text_box(to_print="  ")


def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s

def separate_loot(item):

    entry = loc_loot.get_item(item)
    if entry:
        if entry.get('children'):
            for child in entry['children']:
                game.inventory.append(child)
                do_print(f"{child} separated from {item}")


def get_inventory_names():
    game.inventory_names = []
    for item in game.inventory:
        game.inventory_names.append(item.name)
    return game.inventory_names


def print_inventory():

    inv_list = get_inventory_names()
    print(f"Inv list: {inv_list}")


    print_list = []
    for item in inv_list:
        spaced_item = f"    {assign_colour(item)}"
        if spaced_item in print_list:
            for i in range(len(print_list)):
                if print_list[i] == str(spaced_item):
                    print_list[i] = str(spaced_item + " (x2)") ## only allows for a single duplicate but will do for the moment
                    #dupe_list = registry.get_duplicate_details(item) ## not using this yet but want to remember it exists.
        else:
            print_list.append(spaced_item)

    do_print(print_list)

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
        do_print("To examine an item more closely, type it here, otherwise hit 'enter' to continue.")
        test=user_input()
        if not test or test=="" or test==None:
            done=True
            return test
        while True:
            if test and test in game.inventory_names:
                test=from_inventory_name(test)
                desc = registry.describe(test, caps=True)
                if desc and desc != "" and desc != f"[DESCRIBE] No such item: {test}":
                    slowWriting((f"Description: {assign_colour(desc, "description")}"))
                else:
                    do_print(f"Failed to describe from registry. Investigate. Data: {test}")
                    exit()
                    desc = loc_loot.describe(test, caps=True)
                    if desc and desc != "":
                        if test.colour != None:
                            colour = test.colour
                        else:
                            colour = "description"
                        slowWriting((f"Description: {assign_colour(desc, colour)}"))
                    else:
                        slowWriting(f"Not much to say about the {test}.")

                update_text_box(to_print="  ")

            else:
                break

def god_mode():

    attr_dict={
        "time":choices.time_of_day,
        "weather":list(env_data.weatherdict.keys())
    }
    update_text_box(to_print="God mode: set game.[] parameters during a playthrough. For a print of all game.[] parameters, type 'game_all. Otherwise, just type the change you wish to make.")

    while True:
        text=do_input()
        if "game_all" in text:
            do_print("Trying to print all attr of 'game' class: ")
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
            do_print("Returning to game with changes made.")
            break

def user_input():
    text = do_input()
    if text.lower() == "godmode":
        do_print("Allowing input to set parameters. Please type 'done' or hit enter on a blank line when you're finished.")
        god_mode()
        do_print()
        return "done"
    if text.lower() == "help":
        do_print()
        slowWriting(f"  Type the (highlighted) words to progress, 'i' for 'inventory', 'd' to describe the environment, 'settings' to set some settings - that's about it.")
        do_print()
        return "done"
    if text.lower()== "settings":
        do_print()
        do_print("Settings:")
        init_settings(manual=True)
        do_print()
        return "done"
    if text.lower() == "stats":
        do_print()
        do_print(f"    weird: {game.weirdness}. location: {assign_colour(game.place, 'loc')}. time: {game.time}. weather: {game.weather}. checks: {game.checks}")
        get_inventory_names()
        do_print(f"    inventory: {game.inventory_names}, carryweight: {game.carryweight}")
        pprint(f"    {game.player}")
        do_print()
        return "done"
    if text.lower() == "i":
        do_print()
        do_inventory()
        do_print()
        return "inventory_done"
    if text.lower() == "d":
        loc_data = p_data[game.place]
        do_print(f"{text}: Describe location.")
        slowWriting(f"[{smart_capitalise(game.place)}]  {loc_data.overview}")
        obj = getattr(p_data[game.place], game.facing_direction)
        slowWriting(f"  You're facing {game.facing_direction}. {obj}\n")
        do_print()
        do_print(f"{[game.place]}:{places[game.place].description}")#{descriptions[game.place].get('description')}")
        do_print()
        text=None # clear text to stop it picking 'dried flowers' after `describe location` runs.
        return "done"
    if text.lower().startswith("drop "):
        do_print(f"Text starts with drop: {text}")
        textparts=text.split()[1:]
        do_print(f"textparts: {textparts}, len: {len(textparts)}")
        if len(textparts) > 1:
            textparts = " ".join(textparts[0:])
        else:
            textparts = textparts[0]
        item = registry.instances_by_name(textparts)
        if item:
            item=item[0]
            do_print(f"Sending item to drop: {item}")
            drop_loot(item)
        return "drop_done"
    if text and text.lower() in ("exit", "quit", "stop", "q"):
        # Should add the option of saving and returning later.
        do_print("Okay, bye now!")
        exit()
    else:
        return text

def option(*values, no_lookup=None, print_all=False, none_possible=True, preamble=None, inventory=False):

    values = [v for v in values if v is not None]
    option_chosen = False

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
                    formatted.append(f"{assign_colour(v[0])}")
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
            slowWriting(f"    {', '.join(formatted[:-1])} or {formatted[-1]}")
        elif len(formatted) > 1 and inventory:
            slowWriting(f"    {', '.join(formatted)}")
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
                            clean_values.append(value_deeper)

        test=user_input()
        if test in ("inventory_done", "description_done", "drop_done"):
            if test == "drop_done":
                get_inventory_names()
                values=game.inventory
            continue
        if none_possible and test=="":
            return None
        #print(f"Test: {test}")
        if not test or test == "":
            if test is None:
                return None

        if test.isdigit():
            while test.isdigit():
                index = int(test)
                if 1 <= index <= len(clean_values):
                    test = clean_values[index - 1]
                    return test
                do_print(f"{test} is not a valid option, please try again.")
                test=user_input()

        for v in clean_values:
            returning=None
            if len(test) == 1 and test.lower() == v[0].strip().lower():
                returning = v
            elif v.lower() == test.lower():
                returning = v
            elif v.lower().startswith("a ") or v.startswith("a "):
                if v.lower().startswith("a "):
                    new_v = v[2:]
                elif v.lower().startswith("an "):
                    new_v = v[3:]
                if test.lower() == v.strip().lower() or test.lower() == new_v.strip().lower():
                    returning = v
            else:
                if len(test) > 2 and test.lower() == choose.get(v.lower()):
                    returning = v

            if returning:
                return returning

        if test in no:
            return no
        if test in yes:
            return yes

def roll_risk(rangemin=None, rangemax=None):


    min = 1
    max = 20
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
        if r[0] <= roll <= r[1] or roll in r:
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
    if "is missing. Did" in outcome:
        if not game.inventory:
            dropped = "everything"
        else:
            dropped = random.choice((game.inventory))
            places[game.place].items.append(dropped)
        item = dropped

    return outcome

def drop_loot(named=None, forced_drop=False):
    get_inventory_names()
    if forced_drop:
        test = random.choice((game.inventory))
        newlist = [x for x in game.inventory if x is not test]
        game.inventory = newlist
        return
    if named:
        test=named
    else:
        if len(game.inventory) < 1:
            slowWriting("You don't have anything to drop!")
        test = option(game.inventory_names, print_all=True, preamble="[Type the name of the object you want to leave behind]", inventory=True)

    if test in game.inventory_names or isinstance(test, ItemInstance):
        if isinstance(test, ItemInstance):
            item_test=test

        else:
            do_print(f"Test in inventory names: {test}")
            item_test=from_inventory_name(test)

        game.inventory.remove(item_test)
        game.inventory_names.remove(item_test.name)
        do_print(f"test from inventory name: {test}")
        slowWriting(f"Dropped {assign_colour(test)}.")

    slowWriting("Load lightened, you decide to carry on.")
    if game.checks["inventory_asked"] == False:
        slowWriting("[[ Psst. Hey. Type 'secret' for a secret hidden option, otherwise type literally anything else. ]]")
        game.player["inventory_asked"] = True
        test = user_input()
        if test == "secret":
            test=option("yes", "no", preamble="Hey so... not everyone loves inventory management. So I'll give you the option now - do you want to turn it off and carry without limitation?")
            if test in yes:
                game.player["inventory_management"] = False
                update_settings_json=option("yes", "no", preamble="Do you want to update this for future runs too?")
                if update_settings_json in yes:
                    import json
                    with open("settings.json") as f:
                        data = json.load(f)
                        inventory_state=data["no_inv"]
                        if inventory_state == False and 'yes' in test:
                            data["no_inv"] = True
                        elif inventory_state != False and not 'yes' in test:
                            data["no_inv"] = False

                    with open("settings.json", "w+") as f:
                        json.dump(data, f)
                do_print("Settings updated. Returning.")

    get_inventory_names()
    do_print()

def switch_the(text, replace_with=""): # remember: if specifying the replace_with string, it must end with a space. Might just add that here actually...
    if isinstance(text, list):
        if len(text) == 1:
            text=text[0]
            text=text.name
        else:
            do_print("Trying to `switch_the`, but text is a list with more than one item.")
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
        #do_print(f"Named in get_loot, about to go to pick_up_test: `{named}`, type: {type(named)}")
        if isinstance(named, str):
            item = registry.instances_by_name(named)
            if isinstance(item, list) and len(item) == 1:
                item=item[0]
        elif isinstance(named, ItemInstance):
            item = named
        #do_print(f"item: {item}, type: {type(item)}")

        #pickup_test=loc_loot.pick_up_test(named) #should I test for get_item first? Probably no point. No.
        #if pickup_test == "No such item.":
        #    do_print("Not a location object.")
        #elif pickup_test == "Can pick up":
        #    #print("Can be picked up. Will let it continue, obj should get picked up.")
        #    item=named
        #elif pickup_test == "Cannot pick up": # is a positive failure - it was found, so is a loc item.
        #    do_print("Cannot be picked up. Print a message about how it can't be picked up. Maybe one per item for variation.")
        #    return None
        if not item:
            do_print(f"Failed to check pickupability. Count not get item instance. named: {named}.")

        #if not item:
        #    test_item = loot.get_item(named)
        #    if test_item:
        #        do_print("Item found in regular loot tables. Continuing.")
        #        item=test_item
        #if loc_loot.pick_up_test(named): # should this be negative or positive? More things to look at but not pick up, or the inverse?
        #    item = named

    elif random:
        #print(f"value: {value}")
        item = registry.random_from(value)
        #do_print(f"Item: {item}, type: {type(item)}")
    else:
        do_print("Not random and no name given. This shouldn't happen, but defaulting to random.")
        do_print(f"value: {value}")
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
        _, game.inventory = registry.pick_up(item, game.inventory, game.place, game.facing_direction) ##
        slowWriting(f"{assign_colour(item)} added to inventory.")
        add_infobox_data(print_data=True, inventory=game.inventory) ### Not sure exactly why but: TODO:: This print didn't add a new one, instead overwriting the previously added item.
    #move_item_any(item)

### drop random item if inventory full // not sure if I hate this. ###
    if len(game.inventory) > carryweight:
        do_print()
        #switched = switch_the(item, 'the ')
        test = option(f"drop", "ignore", preamble=f"It looks like you're already carrying too much. If you want to pick up {assign_colour(item, None, nicename=registry.nicename(item), switch=True)}, you might need to drop something - or you can try to carry it all.")
        if test in ("ignore", "i"):
            slowWriting("Well alright. You're the one in charge...")

            if game.player["encumbered"]: # 50/50 chance to drop something if already encumbered and choose to ignore
                outcome = roll_risk()
                if outcome in (1, 2):
                    #print(f"Forced to drop something.") #TODO: remove this later.
                    drop_loot(forced_drop=True) # force drop something.
                    add_infobox_data(print_data=True, inventory=game.inventory) ## TODO: Need to clear this first, otherwise it overwrites in an awful way. Also set a limiter on how many lines it can write on, even if the inventory is more than that.
                    do_print("You feel a little lighter all of a sudden...") ## does not add the item to the location yet. Have to do that.
            if len(game.inventory) > game.carryweight:
                game.player["encumbered"] = True
            else:
                game.player["encumbered"] = False

        else:
            slowWriting("You decide to look in your inventory and figure out what you don't need.")
            drop_loot()
    do_print()
    return item

def have_a_rest():
    slowWriting("You decide to take it easy for a while.")
    # can do things like read a book, check phone if you have them, daydream (roll for it), etc.
    do_print()
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
        do_print(f"You decided to stay at {assign_colour(switch_the(game.place, 'the'), 'loc')} a while longer.")
    else:
        slowWriting(f"You make your way to {assign_colour(game.place, 'loc')}. It's {game.time}, the weather is {game.weather}, and you're feeling {game.emotional_summary}.")
        if places[game.place].visited:
            slowWriting(f"You've been here before... It was {places[game.place].first_weather} the first time you came.")
            if places[game.place].first_weather == game.weather:
                do_print(places[game.place].same_weather)
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
    do_print()
    slowWriting("Finally asleep, you dream deeply.")
    slowWriting("  ...")
    do_print()
    slowWriting("    ...")
    do_print()
    slowWriting("       ...")
    do_print()
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
        do_print(f"\n  You're facing {assign_colour(game.facing_direction)}. {obj}\n") # description
        if obj == None or obj == "None":
            do_print("This description hasn't been written yet... It should have some ")
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
                        do_print(f"{registry.describe(item_entry, caps=True)}")
                        #print("What do you want to do? [Investigate] item, [take] item, [leave] it alone.") # Do I want to list the options like this, or just try to make a megalist of what options may be chosen and work from that?
                        decision=option("investigate", "take", "leave", preamble=f"What do you want to do with {assign_colour(text, switch=True)} - investigate it, take it, or leave it alone?")
                        #print(f"text after decision: {text}")
                        #decision=user_input()
                        if decision.lower()=="investigate":
                            do_print("Nothing here yet.")
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
                            #    do_print("[Find the loot taking function that already exists, make sure the item is removed from the list here.]") # does the current loot table allow for 'already picked up'? I don't think it does. Need to do that.
                        elif decision.lower()=="leave":
                            do_print(f"You decide to leave the {assign_colour(text)} where you found it.")

                    else:
                        do_print(f"No entry in loc_loot for {item_entry}")
                else:
                    do_print(f"Could not find what you're looking for. The options: {potential}")

        slowWriting("Unfortunately I haven't written anything here yet. Maybe just... go somewhere else?")
        slowWriting(f"Keeping in mind that it's {time} and {weather}, where do you want to go?")
        relocate()

    if status == "exhausted" and time not in night:
        slowWriting("Stumbling, you're going to hurt yourself even if it's nice and bright. Haven't written it yet though.")
        look_dark()

## ==== Actual start here ===

    inside = getattr(p_data[game.place], "inside")
    if inside:
        add_text="outside"
    else:
        add_text=""
    slowWriting(f"With the weather {add_text}{game.weather}, you decide to look around the {game.facing_direction} of {assign_colour(switch_the(game.place, 'the '), 'loc')}.")
    if time in night:
        slowWriting(f"It's {game.time}, so it's {random.choice(choices.emphasis["low"])} dark.")
        look_dark()
    else:
        if places[game.place].sub_places:
            for sub_place in places[game.place].sub_places:
                do_print(f"[[[[  sub_place: {sub_place}  ]]]]")
        else:
            look_light("skip_intro")

def new_day():

    if game.loop==False:
        decision = option("yes", "no", preamble="Keep looping?")
        if decision in no:
            slowWriting("Hope you had fun? Not sure really what this is, but thank you.")
            exit()

    game.checks["play_again"]
    game.time = random.choice(["pre-dawn", "early morning", "mid-morning"])
    inner_loop()

def describe_loc():

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
    do_print()
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
    do_print("\n")
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
    do_print("\n")
    do_print("To play: ")
    do_print("Type the words in parentheses, or select by number")
    do_print("    eg: for [[  (stay) or (go))  ]], '1' would choose 'stay'.")

def run():

    do_print("\n \n")
    global game
    run_loc()
    placedata_init()
    rigged=True
    if rigged:
        playernm = "Testbot"
    else:
        intro()
        do_print()
        slowWriting("What's your name?")
        playernm = do_input()
    game = set_up(weirdness=True, bad_language=True, player_name=playernm)
    col_list(game.inventory)

    do_print()
    slowWriting("[[ Type 'help' for controls and options. ]]")
    do_print()
    inner_loop()

#run() # uncomment me to actually play again.


import os
def test():

    os.system("cls")
    global game
    game = set_up(weirdness=True, bad_language=True, player_name="A")

    player_name = run_tui_intro()

    if player_name:
        game.playername = player_name

    world = (game.place, game.weather, game.time, game.day_number)
    player = (game.player, game.carryweight, game.playername)
    add_infobox_data(print_data = True, backgrounds = False, inventory=None, playerdata=player, worldstate=world)
    print_commands(backgrounds=False)
    update_infobox(hp_value=game.player["hp"], name=game.playername, carryweight_value=game.carryweight, location=game.place, weather=game.weather, time_of_day=game.time, day=game.day_number)
    add_infobox_data(print_data = True, inventory=game.inventory)

    col_list(game.inventory)
    slowWriting("[[ Type 'help' for controls and options. ]]")
    do_print()
    inner_loop()


    loc_data = p_data[game.place]

    choose_direction:str = ""
    for item in game.cardinals:
        choose_direction += (assign_colour(item) + " ")
    choose_direction+=assign_colour("go")


os.system("cls")
time.sleep(1)
test()

