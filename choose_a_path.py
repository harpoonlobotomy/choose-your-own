import choices
import env_data
from set_up_game import load_world, set_up, init_settings
from choices import choose, loot
import random
from locations import run_loc, places, descriptions
from env_data import placedata_init, p_data
from pprint import pprint

# https://projects.blender.org/blender/blender/pulls/149089

user_prefs = "path_userprefs.json"
run_again = False

yes = ["y", "yes"]
no = ["n", "no", "nope"]
night = ["midnight", "late evening", "night", "pre-dawn"]

import time


def slow_lines(txt, speed=0.1):
    print(txt)
    time.sleep(speed)


def slow_writing(txt: str, speed=0.001):  # remove a zero to set it to regular speed again.
    for c in str(txt):
        print(c, end='', flush=True)
        time.sleep(speed * random.uniform(0.2, 2))
    print()


def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def do_inventory():
    done = False
    slow_writing("INVENTORY: ")
    while not done:
        # slowWriting("To examine an item more closely, type it here, otherwise hit 'enter' to continue.")
        # slowWriting(f"    {game.inventory}")
        inv_test = option(game.inventory, print_all=True, none_possible=True,
                          preamble="To examine an item more closely, type it here, otherwise hit 'enter' to continue.")
        # test = user_input()
        # print(f"Test: {test}")
        if not inv_test or inv_test == "" or inv_test is None:
            return inv_test
        while True:
            if inv_test and inv_test in game.inventory:
                # places[game.place].first_weather = game.weather
                # needs to be looking in [name].values().get("inv_name")
                desc = loot.describe(inv_test, caps=True)
                if desc and desc != "" and desc != f"No such item: {inv_test}":
                    # slow_writing((f"Description: {desc}")) ## redundant parenthesis, potentially. Need to test once it's working again.
                    slow_writing(
                        f"Description: {desc}")  ## redundant parenthesis, potentially. Need to test once it's working again.
                else:
                    desc = choices.loc_loot.describe(inv_test, caps=True)
                    if desc and desc != "":
                        slow_writing(f"Description: {desc}")
                    else:
                        slow_writing(f"Not much to say about the {inv_test}.")

                print()
                decision = option("drop", "separate", none_possible=True,
                                  preamble=f"You can drop the {inv_test} or try to separate it into parts, or hit enter to continue.")
                # text=user_input()
                if decision == "" or decision is None:
                    print("Continuing.")
                    break
                if decision in ("drop", "separate"):
                    print("For now it drops it either way. Will change this later.")
                    drop_loot(inv_test)
                    break
                print()
            else:
                break


def god_mode():
    attr_dict = {
        "time": choices.time_of_day,
        "weather": list(env_data.weatherdict.keys())
    }
    print(
        "God mode: set game.[] parameters during a playthrough. For a print of all game.[] parameters, type 'game_all. Otherwise, just type the change you wish to make.")
    while True:
        text = input()
        if "game_all" in text:
            print("Trying to print all attr of 'game' class: ")
            attributes = [attr for attr in dir(game)
                          if not attr.startswith('__')]
            print(f"attributes: {attributes}")
        if "print" in text:
            text = text.replace("print ", "")
            obj = getattr(game, text)
            if isinstance(obj, str):
                # if type(obj) == str:
                obj = attr_dict.get(obj)
            print(obj)
        if "game." in text:
            textstart, value = text.split("=")
            print(f"Text: {text}, textstart: {textstart}, value: {value}")
            if textstart in ("game.time", "game.weather", "game.place"):
                try:
                    if "time" in textstart:
                        game.time = value
                        print(f"{textstart} has been set: game.time: {game.time}")
                    if "weather" in textstart:
                        game.weather = value
                        print(f"{textstart} has been set: game.weather: {game.weather}")
                    if "place" in textstart:
                        game.place = value
                        print(f"{textstart} has been set: game.place: {game.place}")
                except Exception as e:
                    print(f"Cannot set {text}: {e}.")
        if "done" in text or text == "":
            print("Returning to game with changes made.")
            break


def user_input():
    text: str = input()
    if text.lower() == "godmode":
        print("Allowing input to set parameters. Please type 'done' or hit enter on a blank line when you're finished.")
        god_mode()
        print()
        return None
    if text.lower() == "help":
        print()
        slow_writing(
            f"  Type the (highlighted) words to progress, 'i' for 'inventory', 'd' to describe the environment, 'settings' to set some settings - that's about it.")
        print()
        return None
    if text.lower() == "settings":
        print()
        print("Settings:")
        init_settings(manual=True)
        print()
        return None
    if text.lower() == "stats":
        print()
        print(f"    location: {game.place}. time: {game.time}. weather: {game.weather}. checks: {game.checks}")
        print(f"    inventory: {game.inventory}. carryweight: {game.volume}. weird: {game.weirdness}. ")
        pprint(f"    {game.player}")
        print()
        return None
    if text.lower() == "i":
        print()
        do_inventory()
        print()
        return None
    if text.lower() == "d":
        loc_data = p_data[game.place]
        print(f"{text}: Describe location.")
        slow_writing(f"[{smart_capitalise(game.place)}]  {loc_data.overview}")
        print()
        # print(f"{[game.place]}:{places[game.place].description}")#{descriptions[game.place].get('description')}")
        # text=None # clear text to stop it picking 'dried flowers' after ;describe location' runs.
        # I think the above line was for when they didn't all return immediately?
        return None
    if text and text.lower() in ("exit", "quit", "stop"):
        # Should add the option of saving and returning later.
        print("Okay, bye now!")
        exit()
    else:
        return text


def option(*values, no_lookup=None, print_all: bool = False, none_possible: bool = True, preamble: str = None):
    # none_possible=True == "if blank input, consider it a viable return". I didn't need this before but I'm going to see if it fixes it.
    option_chosen = False
    values = [v for v in values if v is not None]
    # print(f"Values: {values}m len(values): {len(values)}")
    formatted = []
    for v in values:
        if isinstance(v, (list, tuple)):
            if print_all:
                formatted.append(f"({', '.join(v)})")
            else:
                formatted.append(f"({v[0]})")  # add the first one as the 'label', use the rest as list later.
        else:
            formatted.append(f"({v})")
    # print(f"--" * 10, f"\nformatted: {formatted}, formatted_type: {type(formatted)}\n")
    while not option_chosen:
        if preamble:
            slow_writing(preamble)
        if len(formatted) > 1:
            slow_writing(
                f"    {', '.join(formatted[:-1])} or {formatted[-1]}")  # this formatting is good visually, so don't change it before  this. The delineation here is preferable.
        else:
            slow_writing(f"    {formatted[0]}")

        if no_lookup:
            return None

        clean_values = []
        if isinstance(values, (list, tuple, set)):
            # if type(values) in (list, tuple, set):
            for value in values:
                if isinstance(value, str):
                    # if type(value) == str:
                    clean_values.append(value)
                else:
                    for value_deeper in value:
                        if isinstance(value_deeper, str):
                            # if type(value_deeper) == str:
                            clean_values.append(value_deeper)  # I cannot imagine another layer of nesting here.

        test_input: str = user_input()
        if none_possible and test_input == "":
            return None
        # print(f"Test: {test}")
        if not test_input or test_input == "":
            if test_input is None:  # This is really silly..... Why on earth is this like this?
                return None

        if test_input.isdigit():  # if you type 1, it returns the first option, etc
            while test_input.isdigit():
                index = int(test_input)
                if 1 <= index <= len(clean_values):
                    test_input = clean_values[index - 1]
                    print(f"Chosen: ({test_input})")
                    return test_input
                print(f"{test_input} is not a valid option, please try again.")
                test_input = user_input()

        for v in clean_values:
            if len(test_input) == 1:
                if test_input.lower() == v[0].strip().lower():
                    print(f"Chosen: ({v})")
                    return v
            if v.lower() == test_input.lower():
                print(f"Chosen: ({v})")
                return v
            else:
                if len(test_input) > 2 and test_input == choose.get(v):
                    print(f"Chosen: ({v})")
                    return v

        if test_input in no:
            return no
        if test_input in yes:
            return yes


def roll_risk(rangemin=None, rangemax=None):
    # I want to make this variable. So I can weight it.
    min_val = 1
    max_val = 20  # this will do but isn't what I really want.
    if rangemin:
        min_val = rangemin
    if rangemax:
        max_val = rangemax

    results = [
        ((1, 4), "INJURY", 1),
        ((5, 11), "MINOR SUCCESS", 2),
        ((12, 18), "GREATER SUCCESS", 3),
        ((19, 20), "GREATEST SUCCESS!", 4)
    ]

    roll = random.randint(min_val, max_val)
    for r, msg, val in results:
        if r[0] <= roll <= r[
            1] or roll in r:  # ("if roll is between first and second part of the tuple, or is in the tuple itself", y?)  # supports both singletons and ranges
            if game.show_rolls:
                slow_writing(f"Roll: {roll}\n{msg}")
            return val


def outcomes(state, activity):
    item = None
    very_negative = ["It hurts suddenly. This isn't good...",
                     f"You suddenly realise, your {item} is missing. Did you leave it somewhere?"]
    negative = [f"Uncomfortable, but broadly okay. Not the worst {activity} ever",
                f"Entirely survivable, but not much else to say about this {activity}.",
                f"You did a {activity}. Not much else to say about it really."]
    positive = [f"Honestly, quite a good {activity}", f"One of the better {activity}-based events, it turns out."]
    very_positive = [f"Your best {activity} in a long, long time."]

    outcome_table = {
        1: very_negative,
        2: negative,
        3: positive,
        4: very_positive
    }

    outcome = random.choice((outcome_table[state]))
    if "is missing. Did" in outcome:  # should only run when dropping actually happens.
        if not game.inventory:
            dropped = "everything"  # in case everything's already gone?
        else:
            dropped = random.choice(game.inventory)
            places[game.place].items.append(dropped)  # stored in this location, can find it again later.
        item = dropped
        # placeholder

    return outcome  ## better? Not sure.


def drop_loot(named=None, forced_drop=False):
    newlist = None
    if forced_drop:
        loot_test = random.choice(game.inventory)
        newlist = [x for x in game.inventory if x is not loot_test]
        game.inventory = newlist
        return
    if named:
        loot_test = named
    else:
        if len(game.inventory) < 1:
            slow_writing("You don't have anything to drop!")
        # slowWriting("[[ Type the name of the object you want to leave behind ]]")
        # print(game.inventory)
        loot_test = option(game.inventory, print_all=True,
                           preamble="[Type the name of the object you want to leave behind]")
        # while test not in game.inventory and test not in ("done", "exit", "quit"):
        #    slowWriting("Type the name of the object you want to leave behind.")
        #    test = user_input()
    if loot_test in game.inventory:
        # print(f"test: {test}")
        newlist = [x for x in game.inventory if x is not loot_test]
        # TODO: update location for test

        # print(f"newlist: {newlist}")
        slow_writing(f"Dropped {loot_test}. If you want to drop anything else, type 'drop', otherwise we'll carry on.")
        game.inventory = newlist
        loot_test = user_input()
        if loot_test == "drop" and len(game.inventory) >= 1:
            drop_loot()

    # print(f"game.inventory: {game.inventory}, named: {named}")
    slow_writing("Load lightened, you decide to carry on.")
    if not game.checks["inventory_on"]:
        slow_writing(
            "[[ Psst. Hey. Type 'secret' for a secret hidden option, otherwise type literally anything else. ]]")
        loot_test = user_input()
        if loot_test == "secret":
            # slowWriting("Hey so... not everyone loves inventory management. So I'll give you the option now - do you want to turn it off and carry without limitation?")
            # slowWriting("         (yes) or (no)")
            # test = user_input()
            loot_test = option("yes", "no",
                               preamble="Hey so... not everyone loves inventory management. So I'll give you the option now - do you want to turn it off and carry without limitation?")
            if loot_test in yes:
                game.player["inventory_management"] = False
                # slowWriting("Do you want to update this for future runs too?")
                update_settings_json = option("yes", "no", preamble="Do you want to update this for future runs too?")
                if update_settings_json in yes:
                    print("update the settings json here. Not implemented yet.")

            if loot_test in no:
                game.player["inventory_management"] = True
            # if no proper answer, it stays as it already was.

    game.inventory = newlist
    print()


def switch_the(text,
               replace_with=""):  # remember: if specifying the replace_with string, it must end with a space. Might just add that here actually...
    for article in ("a ", "an "):
        if article in text:
            if replace_with != "":
                # print(f"replace with isn't blank: `{replace_with}`")
                if replace_with[-1] != " ":
                    # print(f"replace with doesn't end with a space: `{replace_with}`")
                    replace_with = replace_with + " "
                    # print(f"replace with should now have a space: `{replace_with}`")
            text = text.replace(article,
                                replace_with)  # added 'replace with' so I can specify 'the' if needed. Testing.
    return text


def get_loot(value=None, random_bool=True, named="", message: str = None):
    item = None
    carryweight = game.volume
    # print(f"in get_loot: value: {value}, random: {random}, named: {named}, message: {message}")
    if named != "" and value is None:  # don't add value for location items.
        pickup_test = choices.loc_loot.pick_up_test(named)  # should I test for get_item first? Probably no point. No.
        if pickup_test == "No such item.":
            print("Not a location object.")
        elif pickup_test == "Can pick up":
            # print("Can be picked up. Will let it continue, obj should get picked up.")
            item = named
        elif pickup_test == "Cannot pick up":  # is a positive failure - it was found, so is a loc item.
            print(
                "Cannot be picked up. Print a message about how it can't be picked up. Maybe one per item for variation.")
            return None
        else:
            print("Failed to check pickupability. Letting it run to see what happens.")
        if not item:
            test_item = loot.get_item(named)
            if test_item:
                print("Item found in regular loot tables. Continuing.")
                item = test_item
        # if choices.loc_loot.pick_up_test(named): # should this be negative or positive? More things to look at but not pick up, or the inverse?
        #    item = named

    elif random_bool:
        # print(f"value: {value}")
        item = loot.random_from(value)
    else:
        print("Not random and no name given. This shouldn't happen, but defaulting to random.")
        print(f"value: {value}")
        item = loot.random_from(value)
    # print(f"Item: {item}")
    if message:
        message = message.replace("[item]", loot.nicename(item))
        message = message.replace("[place]", game.place)
        slow_writing(message)
    # item = loot.get_item(item)
    slow_writing(f"[[ `{item}` added to inventory. ]]")
    game.inventory.append(item)
    choices.loc_loot.set_location(item, game.place, game.facing_direction, picked_up=True)

    # TODO: Need to remove the item from the location. Currently it just 'duplicates' whatever is picked up because it's never removed from its origin.

    ### drop random item if inventory full // not sure if I hate this. ###
    if len(game.inventory) > carryweight:
        print()
        heavy_test = option(f"drop", "ignore",
                            preamble=f"It looks like you're already carrying too much. If you want to pick up {switch_the(item, 'the ')}, you might need to drop something - or you can try to carry it all.")
        if heavy_test in ("ignore", "i"):
            if game.player["encumbered"]:  # 50/50 chance to drop something if already encumbered and choose to ignore
                outcome = roll_risk()
                if outcome in (1, 2):
                    # print(f"Forced to drop something.") #TODO: remove this later.
                    drop_loot(forced_drop=True)  # force drop something

            slow_writing("Well alright. You're the one in charge...")
            game.player["encumbered"] = True
        else:
            slow_writing("You decide to look in your inventory and figure out what you don't need.")
            drop_loot()
    print()
    return item


def have_a_rest():
    slow_writing("You decide to take it easy for a while.")
    # can do things like read a book, check phone if you have them, daydream (roll for it), etc.
    print()
    slow_writing("But after a while, you decide to get up anyway.")
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
    time_index = times_of_day.index(game.time)
    new_time_index = time_index + 1  # works
    if new_time_index == len(times_of_day):
        new_time_index = 0
    game.time = times_of_day[new_time_index]

    weather_options = list(env_data.weatherdict)
    weather_index = weather_options.index(game.weather)
    weather_variance = random.choice([int(-1), int(1)])
    new_weather_index = weather_index + int(weather_variance)
    if new_weather_index == len(weather_options):
        new_weather_index = 0
    game.weather = weather_options[new_weather_index]

    while len(options) < 3:
        new_place = random.choice(game.loc_list)
        if new_place not in options:  # and new_place != current_loc <- turn on when I don't want current loc as an option anymore.
            options.append(new_place)

    game.place = option(options, print_all=True, preamble="Please pick your destination:")
    load_world(relocate=True)
    if game.place == current_loc:
        print(f"You decided to stay at {switch_the(game.place, 'the')} a while longer.")
    else:
        slow_writing(
            f"You make your way to {game.place}. It's {game.time}, the weather is {game.weather}, and you're feeling {game.emotional_summary}.")
        if places[game.place].visited:
            slow_writing(
                f"You've been here before... It was {places[game.place].first_weather} the first time you came.")
            if places[game.place].first_weather == game.weather:
                print(places[game.place].same_weather)
        else:
            places[
                game.place].visited = True  # maybe a counter instead of a bool. Maybe returning x times means something. No idea what. Probably not.
            places[game.place].first_weather = current_weather

    if need_sleep:
        decision = option("rest", "look",
                          preamble="You're getting exhausted. You can look around if you like but the sleep deprivation's getting to you.")
        if decision == "rest":
            if not places[game.place].inside:
                sleep_outside()
            else:
                sleep_inside()
        else:
            look_around(status="exhausted")
    else:
        look_around()


def sleep_outside():
    if getattr(p_data[game.place], "nature"):
        slow_writing("You decide to spend a night outside in nature.")
    else:
        slow_writing(f"You decide to spend a night outside in {switch_the({game.place}, 'the ')}.")
    if not game.bad_weather:
        slow_writing("Thankfully, the weather isn't terrible at least.")
        slow_writing("You sleep until morning.")
        the_nighttime()
    else:
        slow_writing(f"Unfortunately, it's {game.weather}")
        slow_writing("You can weather it out (no pun intended) or try a last minute relocation - what do you do?")
        decision = option("stay", "move")
        if decision == "stay":
            risk = roll_risk()
            outcome = outcomes(risk, "sleep")
            slow_writing(outcome)
            slow_writing("Something else happens here. Who knows what. Interactive dream scene.")
            the_nighttime()
        else:
            relocate(need_sleep=True)


def sleep_inside():
    slow_writing(
        f"Deciding to hunker down in {game.place} for the night, you find the comfiest spot you can and try to rest.")
    risk = roll_risk(10, 21)
    outcome = outcomes(risk, "sleep")
    slow_writing(outcome)
    the_nighttime()


def the_nighttime():
    print()
    slow_writing("Finally asleep, you dream deeply.")
    slow_writing("  ...")
    print()
    slow_writing("    ...")
    print()
    slow_writing("       ...")
    print()
    slow_writing("Imagine a dream here. Something meaningful...")
    slow_writing("And/or wild animals if sleeping outside, and/or people, and/or ghosts/monster vibes if weird.")
    new_day()


def look_around(status=None):
    place = game.place
    current_time = game.time
    weather = game.weather

    def look_dark():
        if ("torch" or "phone" or "matchstick") not in game.inventory:
            if descriptions[place].get("electricity"):
                look_test = option("yes", "no",
                                   preamble="It's dark, but you can try to find a light switch if you want.")
                if look_test in yes:
                    outcome = roll_risk()
                    if outcome in (1, 2):
                        slow_writing("Try as you might, you can't find a lightswitch...")
                    else:
                        slow_writing("The light flickers on - you can see.")
                        look_light(reason="electricity")

            look_test = option("yes", "no",
                               preamble=f"It's too dark to see much of anything in {switch_the(place, 'the ')}, and without a torch or some other light source, you might trip over something. Do you want to keep looking?")
            if look_test in yes:
                slow_writing("Determined, you peer through the darkness.")
                outcome = roll_risk()
                if outcome == 1:
                    slow_writing("OW! You roll your ankle pretty badly.")
                    if len(game.inventory) < 4:
                        get_loot(1, random_bool=True,
                                 message=f"It's only a minor injury, sure, but damn it stings. You did find [item] while facefirst in the middle of [place], though.")
                        # slowWriting(f"It's only a minor injury, sure, but damn it stings. You did find {item} while facefirst in the middle of {place}, though.") # don't need these two lines. Need to combine them into just the loot message..
                    if game.w_value:
                        print(
                            "You see something shimmer slightly off in a bush, but by the time you hobble over, whatever it was has vanished.")
                if outcome == 2:
                    hazard = get_hazard()
                    get_loot(1, random_bool=True,
                             message=f"Narrowly avoiding tripping over {hazard}, you find [item]. Better than nothing, but probably all you'll find until there's more light.")  # want options for the poorly lit hazard part.
                    # game.carrier_size compared to item.size? Can I be bothered?
                if outcome in (3, 4):
                    get_loot(2, random_bool=True,
                             message=f"Once your eyes adjust a bit, you manage to make out more shapes than you expected - you find [item].")
            if look_test in no:
                slow_writing(
                    "Thinking better of it, you decide to keep the advanced investigations until you have more light. What now, though?")
            look_test = option("stay", "go",
                               preamble=f"You could stay and sleep in {switch_the(place, 'the ')} until morning, or go somewhere else to spend the wee hours. What do you do?")
            if look_test in ("sleep", "stay"):
                if not places[game.place].inside:
                    sleep_outside()
                else:
                    sleep_inside()
            else:
                slow_writing(f"Keeping in mind that it's {current_time} and {weather}, where do you want to go?")
                relocate()

        else:
            slow_writing(
                "Using your torch, you see things. Probably. I haven't written this yet. How do you have a torch?!?")

    def look_light(reason=None):
        skip_intro = False
        if reason == "turning" or reason == "skip_intro":
            skip_intro = True
        elif reason is None:
            reason = "the sun"
        if not skip_intro:  # if there are no other reason to skip intro, can just combine the above into one 'if/else'.
            slow_writing(
                f"Using the power of {reason}, you're able to look around {switch_the(game.place, 'the ')} without too much fear of a tragic demise.")
        obj = getattr(p_data[game.place], game.facing_direction)
        # print(f"\n{obj}\n")
        print(f"\n{obj}\n")  # description
        if obj is None or obj == "None":
            print("This description hasn't been written yet... It should have some ")
        remainders = list(x for x in game.cardinals if x is not game.facing_direction)
        print(f"Directions to look: {remainders}")
        options = choices.location_loot[game.place].get(game.facing_direction)
        if options:
            options = list(x for x in options.keys() if x not in game.cardinals)
            print(
                f"Interactable items: {options}")  # Should stop it including the cardinals. Not sure why it was, but it was.
        # slowWriting(f"You can look around more, or try to interact with the environment:")
        else:
            options = None
        text = None
        while text not in (remainders, "leave"):
            text = None
            while not text:  # not sure if I need both of these. Will test it later.
                text = option(remainders, "leave", options, no_lookup=None, print_all=True,
                              preamble="You can look around more, leave, or try to interact with the environment:")
                ## "leave" here is confusing. If facing the exit wall, it means 'leave the area'. If looking at an item, it means 'leave it alone'.
            if text == "leave":
                slow_writing(f"You decide to move on from {switch_the(game.place, 'the')}")
                relocate()
            if text in remainders:
                game.facing_direction = text
                look_light("turning")  # run it again, just printing the description of where you turned to.
            if text != "" and text is not None:
                if text in obj or text in options:
                    # print(f"Text: {text}, obj: {obj}")
                    if text in list(options):
                        # for option_entry in options: ## 'if text in options', surely?
                        #    if text in option_entry: # this gets 'television' if I type 'e'. Not working...
                        # print(f"text just before get_item: {text}")
                        # print(f"loc loot: {choices.loc_loot}")
                        # print(f"text: {text}")
                        # item_entry = getattr(choices.loc_loot[game.place][game.facing_direction], text)
                        item_entry = choices.loc_loot.get_item(text)
                        # print(f"item entry: {item_entry}")
                        if item_entry:
                            print(f"{choices.loc_loot.describe(text, caps=True)}")
                            # print("What do you want to do? [Investigate] item, [take] item, [leave] it alone.") # Do I want to list the options like this, or just try to make a megalist of what options may be chosen and work from that?
                            decision = option("investigate", "take", "leave",
                                              preamble="What do you want to do - investigate it, take it, or leave it alone?")
                            # print(f"text after decision: {text}")
                            # decision=user_input()
                            if decision.lower() == "investigate":
                                print("Nothing here yet.")
                            elif decision.lower() == "take":
                                # print(f"text in decision lower == take: {text}")
                                picked_up = get_loot(value=None, random_bool=True, named=text, message=None)
                                if picked_up:
                                    # print(f"To set location: {picked_up}, {game.place}, {game.facing_direction}")
                                    set_items: list = choices.loc_loot.set_location(picked_up, game.place,
                                                                                    game.facing_direction,
                                                                                    picked_up=True)
                                    for item_name in set_items:
                                        if item_name not in game.inventory:
                                            game.inventory.append(item_name)
                                    print(
                                        "[Find the loot taking function that already exists, make sure the item is removed from the list here.]")  # does the current loot table allow for 'already picked up'? I don't think it does. Need to do that.
                            elif decision.lower() == "leave":
                                print(f"You decide to leave the {text} where you found it.")
                            # this should loop, not just kick you out and relocate you immediately.
                        else:
                            print(f"No entry in loc_loot for {item_entry}: {choices.loc_loot}")
                    else:
                        print(f"Could not find what you're looking for. The options: {options}")
                        # for item in options:
                        #    item_entry = loc_loot.get_item(item)
                        #    print(f"item_entry: {item_entry}")
                # print("You've typed something that's in the location description. Sadly I haven't written anything else yet...")
                # else:
            # slowWriting() # list of cardinals except the one you're looking in already.
            # print(f"txt is not in remainders or in options: {text}")
            # Not adding anything else here for "leave" because the default route currently is relocate anyway. If this changes:: Must have 'relocate' option for "leave" entry.
            print("This should give us the list of things to look at again.")
        slow_writing("Unfortunately I haven't written anything here yet. Maybe just... go somewhere else?")
        slow_writing(f"Keeping in mind that it's {current_time} and {weather}, where do you want to go?")
        relocate()

    if status == "exhausted" and current_time not in night:
        slow_writing(
            "Stumbling, you're going to hurt yourself even if it's nice and bright. Haven't written it yet though.")
        look_dark()  # new one for this with light variation. Maybe 'looking' should be a class... It's going to be a major part of it....

    ## ==== Actual start here ===

    inside = getattr(p_data[game.place], "inside")
    if inside:
        add_text = "outside "  # just so it says 'with the weather outside raining, instead of 'with the weather raining'. Either way it's a poorly constructed sentence though.
    else:
        add_text = ""
    slow_writing(
        f"With the weather {add_text}{game.weather}, you decide to look around the {game.facing_direction} of {switch_the(game.place, 'the ')}.")
    if current_time in night:
        slow_writing(
            f"It's {game.time}, so it's {random.choice(choices.emphasis['low'])} dark.")  # trying a bit more variation in the benign text.
        look_dark()
    else:
        if places[game.place].sub_places:
            for sub_place in places[game.place].sub_places:
                print(f"[[[[  sub_place: {sub_place}  ]]]]")  # this has never printed.
        else:
            look_light("skip_intro")


def new_day():
    # print("You wake up ")
    if not game.loop:
        decision = option("yes", "no", preamble="Keep looping?")
        if decision in no:
            slow_writing("Hope you had fun? Not sure really what this is, but thank you.")
            exit()

    # game.checks["play_again"]
    game.time = random.choice(["pre-dawn", "early morning", "mid-morning"])  # sometime in the morning, we awaken.
    inner_loop()


def describe_loc():
    ## Needs to also describe weather here.
    loc_data = p_data[game.place]
    slow_writing(f"You take a moment to take in your surroundings. {loc_data.overview}")
    while True:
        facing_direction = option(game.cardinals, "go", print_all=True,
                                  preamble="Pick a direction to investigate, or go elsewhere?")
        if facing_direction in game.cardinals:
            game.facing_direction = facing_direction
            look_around()
        elif facing_direction == "go":
            slow_writing(f"You decide to leave {switch_the(game.place, 'the ')}")
            relocate()


def inner_loop():
    slow_writing(
        f"You wake up in {game.place}, right around {game.time}. You find have a bizarrely good sense of cardinal directions; how odd.")
    places[game.place].visited = True
    places[game.place].first_weather = game.weather

    slow_writing(
        f"`{game.playername}`, you think to yourself, `is it weird to be in {game.place} at {game.time}, while it's {game.weather}?`")
    print()
    describe_loc()

    test_innerloop = option("stay", "go",
                            preamble="What do you want to do? (Stay) here and look around, or (Go) elsewhere?")
    if test_innerloop in "stay, look":
        slow_writing("You decide to look around a while.")
        look_around()
    else:
        relocate()


def intro():
    # First run setup
    # ascii from https://patorjk.com/software/taag/#p=display&f=Big+Money-ne&t=paths&x=none&v=4&h=4&w=80&we=false
    print("\n")
    slow_lines("                          /================================ #")
    slow_lines("                         /                                  #")
    slow_lines("   # ===================/     /$$     /$$                   #")
    slow_lines("   #                         | $$    | $$                   #")
    slow_lines("   #     /$$$$$$   /$$$$$$  /$$$$$$  | $$$$$$$   /$$$$$$$   #")
    slow_lines("   #    /$$__  $$ |____  $$|_  $$_/  | $$__  $$ /$$_____/   #")
    slow_lines(r"   #   | $$  \ $$  /$$$$$$$  | $$    | $$  \ $$|  $$$$$$    #")
    slow_lines(r"   #   | $$  | $$ /$$__  $$  | $$ /$$| $$  | $$ \____  $$   #")
    slow_lines("   #   | $$$$$$$/|  $$$$$$$  |  $$$$/| $$  | $$ /$$$$$$$/   #")
    slow_lines(r"   #   | $$____/  \_______/   \___/  |__/  |__/|_______/    #")
    slow_lines("   #   | $$                                                 #")
    slow_lines("   #   | $$       /======================================== #")
    slow_lines("   #   |__/      /")
    slow_lines("   #            /")
    slow_lines("   # ==========/")
    print("\n")
    print("To play: ")
    print("Type the words in parentheses, or select by number")
    print("    eg: for [[  (stay) or (go))  ]], '1' would choose 'stay'.")


def run():
    print("\n \n")
    global game
    run_loc()
    placedata_init()
    choices.initialise_location_loot()
    rigged = True  # this one's just for the name/intro skip, doesn't affect weather etc.
    if rigged:
        playernm = "Testbot"
    else:
        intro()
        print()
        slow_writing("What's your name?")
        playernm = input()  # is not 'user_input' because we don't want the inventory actions available until game is initialised.
    game = set_up(weirdness=True, bad_language=True, player_name=playernm)
    print()
    slow_writing("[[ Type 'help' for controls and options. ]]")
    print()
    inner_loop()


run()  # uncomment me to actually play again.


def test():
    # from set_up_game import calc_emotions#loadout, set_up
    # calc_emotions()#
    global game
    game = set_up(weirdness=True, bad_language=True, player_name="A")
    get_hazard()


# test()

"""You wake up in a hospital, right around midday.
`Alex`, you think to yourself, `is this a weird time to be in a hospital? And with so few people around?`
     What do you want to do? Stay here and (look) around, or go (elsewhere)?
i
INVENTORY:
    ['severed tentacle', 'mail order magazine', 'fish food', 'regional map']
(type stay, look, or go, elsewhere)
stay
You decide to look around some more anyway.
     Honestly it's too dark to see much of anything in the a hospital. You can just about avoid tripping over yourself, but it's hard to see much else. Do you want to keep trying?
y
Determined, you peer through the darkness.
Narrowly avoiding tripping over some poorly lit hazard, you find a {'damp newspaper'}. Better than nothing, but probably all you'll find until there's more light.
{'damp newspaper'} added to inventory.
You could (sleep) in a hospital until morning, or (choose) somewhere else to spend the wee hours. What do you do?
sleep
You decide to sleep right where you are. Nice and comfy.
Thankfully, the weather isn't terrible at least.
You sleep until morning."""
