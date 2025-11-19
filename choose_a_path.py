import choices
import env_data
from set_up_game import load_world, set_up
from choices import choose, loot
import random
from locations import run_loc, places, descriptions
from env_data import placedata_init, p_data
from pprint import pprint
# https://projects.blender.org/blender/blender/pulls/149089

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


def do_inventory():
    done=False
    slowWriting("INVENTORY: ")
    while done == False:
        slowWriting("To examine an item more closely, type it here, otherwise hit 'enter' to continue.")
        slowWriting(f"    {game.inventory}")
        test = user_input()
        if test=="" or test==None:
            done=True
            break
        while True:
            if test in game.inventory:
                    #places[game.place].first_weather = game.weather
                # needs to be looking in [name].values().get("inv_name")
                desc = loot.describe(test, caps=True)
                if desc and desc != "" and desc != f"No such item: {test}":
                    slowWriting((f"Description: {desc}"))
                    break
                else:
                    desc = choices.loc_loot.describe(test, caps=True)
                    if desc and desc != "":
                        slowWriting((f"Description: {desc}"))
                        break
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
            if type(obj) == str: # returned a single attr, not a list of attrs (which will be the majority of the time)
                obj = attr_dict.get(obj)
            print(obj)

            #print(f"Trying to print all attr of 'game.{text}': ")
            ##text=eval(text)
            #attributes = [attr for attr in dir(game.text)
            #  if not attr.startswith('__')]
            #print(f"attributes: {attributes}")
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
                        print(f"{textstart} has been set: game.place: {game.place}")
                except Exception as e:
                    print(f"Cannot set {text}: {e}.")
        if "done" in text or text == "":
            print("Returning to game with changes made.")
            break

def user_input():
    text = input()
    if text.lower() == "godmode":
        print("Allowing input to set parameters. Please type 'done' or hit enter on a blank line when you're finished.") #this is just so I can test specific locations without having to amend the scripts manually tbh.
        god_mode()
        print()
    elif text.lower() == "help":
        print()
        slowWriting(f"  Type the (highlighted) words to progress, 'i' for 'inventory', 'd' to describe the environment, 'settings' to set some settings - that's about it.")
        print()
    elif text.lower()== "settings":
        print()
        print("Settings:")
        print("  Not currently functioning, but options should include text speed and a luck modifier (ie chance to succeed at rolls)")
        print()
    elif text.lower() == "stats":
        print()
        print(f"    weird: {game.weirdness}. location: {game.place}. time: {game.time}. weather: {game.weather}. checks: {game.checks}")
        print(f"    inventory: {game.inventory}, carryweight: {game.volume}")
        pprint(f"    {game.player}")
        print()
    elif text.lower() == "i":
        print()
        do_inventory()
        print()
    elif text.lower() == "d":
        loc_data = p_data[game.place]
        print(f"{text}: Describe location.")
        slowWriting(f"[{smart_capitalise(game.place)}]  {loc_data.overview}")
        print()
#        print(f"{[game.place]}:{places[game.place].description}")#{descriptions[game.place].get('description')}")
        print()
    elif text.lower() in ("exit", "quit", "stop"):
        # Should add the option of saving and returning later.
        print("Okay, bye now!")
        exit()
    else:
        return text
    return None

def option(*values, no_lookup=None, print_all=False, preamble=None):

## I need to pre-clean `values` here to make it easier later.
# non-exclusive sample of values inputs:
#       Values: (['north', 'south', 'east', 'west'], 'go'), type: <class 'tuple'>
#       Values: (['south', 'east', 'west'], 'leave', ['glass jar', 'dried flowers', 'moss', 'headstone']), type: <class 'tuple'>
#       Values: ('investigate', 'take', 'leave'), type: <class 'tuple'>
#       Values: (['a graveyard', 'a forked tree branch', 'a city hotel room'],), type: <class 'tuple'>
# or if 'options' is a set instead of a list:
#       Values: [{'a city hotel room', 'a forked tree branch', 'a graveyard'}], type: <class 'list'>

    option_chosen = False
    values = [v for v in values if v is not None]
    #print(f"Values: {values}m len(values): {len(values)}")
    formatted = []
    for v in values:
        if isinstance(v, (list, tuple)):
            if print_all:
                formatted.append(f"({', '.join(v)})")
            else:
                formatted.append(f"({v[0]})") # add the first one as the 'label', use the rest as list later.
        else:
            formatted.append(f"({v})")
    #print(f"--" * 10, f"\nformatted: {formatted}, formatted_type: {type(formatted)}\n")
    while option_chosen != True:
        if preamble:
            slowWriting(preamble)
        if len(formatted) > 1:
            slowWriting(f"    {', '.join(formatted[:-1])} or {formatted[-1]}") # this formatting is good visually, so don't change it before  this. The delineation here is preferable.
        else:
            slowWriting(f"    {formatted[0]}")

### So fix the tuple/list/etc shit here.
# get rid of all nesting, just have one list of strings, all inclusively.

        print("--" * 10, f"\nValues: {values}, type: {type(values)}")
        if no_lookup:
            return
        test=user_input()
        #print(f"Test: {test}")
        while not test:
            test=user_input()

        if test.isdigit(): # if you type 1, it returns the first option, etc
            while test.isdigit():
                index = int(test)
                #print(f"Values: {values}. type: {type(values)}")
                if isinstance(values[0], (list, tuple)):
                    if 1 <= index <= len(values[0]):
                    #print(f"Values [0]: {values[0]}")
                        test=(values[0])[index - 1]
                        print(f"Chosen: ({test})")
                        return test
                if 1 <= index <= len(values):
                    test = values[index - 1]
                    print(f"Chosen: ({test})")
                    return test
                print(f"{test} is not a valid option, please try again.")
                test=user_input()

        for v in values:
            if len(test) == 1:
                if test == v[0].strip():
                    print(f"Chosen: ({v})")
                    return v
            if v == test:
                print(f"Chosen: ({v})")
                return test

        for an_option in values: # neaten all of this. This whole func really.
            if test == an_option:
                return an_option
            if isinstance(an_option, (list, tuple)): # manually listed in the call signature
                for sub in an_option:
                    #print(f"Sub: {sub} in an_option: {an_option}")
                    if len(test) == 1:
                        if test == sub[0].strip():
                            return sub
                    if print_all:
                        if test.lower() == sub.lower():
                            return sub
                    elif test.lower() == sub.lower():
                        return sub
                    elif test in choose.get(sub):
                        return sub
            else:
                if len(test) > 2 and test == choose.get(an_option):
                    return an_option
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
    very_negative = ["It hurts suddenly. This isn't good...", f"You suddenly realise, your {item} is missing. Did you leave it somewhere?"]
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

def drop_loot(forced_drop=False):

    if forced_drop:
        test = random.choice((game.inventory))
        newlist = [x for x in game.inventory if x is not test]
        game.inventory = newlist
        return

    if len(game.inventory) < 1:
        slowWriting("You don't have anything to drop!")
    slowWriting("[[ Type the name of the object you want to leave behind ]]")
    print(game.inventory)
    test = user_input()
    while test not in game.inventory and test not in ("done", "exit", "quit"):
        slowWriting("Type the name of the object you want to leave behind.")
        test = user_input()
    if test in game.inventory:
        newlist = [x for x in game.inventory if x is not test]
        slowWriting(f"Dropped {test}. If you want to drop anything else, type 'drop', otherwise we'll carry on.")
        test = user_input()
        if test == "drop" and len(game.inventory) >= 1:
            game.inventory = newlist
            drop_loot()

    slowWriting("Load lightened, you decide to carry on.")
    if game.checks["inventory_on"] == False:
        slowWriting("[[ Psst. Hey. Type 'secret' for a secret hidden option, otherwise type literally anything else. ]]")
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
                    print("update the settings json here. Not implemented yet.")

            if test in no:
                game.player["inventory_management"] = True
            # if no proper answer, it stays as it already was.

    game.inventory = newlist
    print()

def switch_the(text, replace_with=""): # remember: if specifying the replace_with string, it must end with a space. Might just add that here actually...
    for article in ("a ", "an "):
        if article in text:
            if replace_with != "":
                #print(f"replace with isn't blank: `{replace_with}`")
                if replace_with[-1] != " ":
                    #print(f"replace with doesn't end with a space: `{replace_with}`")
                    replace_with = replace_with + " "
                    #print(f"replace with should now have a space: `{replace_with}`")
            text = text.replace(article, replace_with) # added 'replace with' so I can specify 'the' if needed. Testing.
    return text

def get_loot(value=None, random=True, named="", message=None):

    carryweight = game.volume
    if named != "":
        if choices.loc_loot.pick_up_test(named): # should this be negative or positive? More things to look at but not pick up, or the inverse?
            item = named
    elif random:
        #print(f"value: {value}")
        item = loot.random_from(value)
    else:
        print("Not random and no name given. This shouldn't happen, but defaulting to random.")
        print(f"value: {value}")
        item = loot.random_from(value)
    #print(f"Item: {item}")
    if message:
        message = message.replace("[item]", loot.nicename(item))
        message = message.replace("[place]", game.place)
        slowWriting(message)
    #item = loot.get_item(item)
    slowWriting(f"[[ `{item}` added to inventory. ]]")
    game.inventory.append(item)
    if len(game.inventory) > carryweight:
        print()
        test = option(f"drop", "ignore", preamble=f"It looks like you're already carrying too much. If you want to pick up {switch_the(item, 'the ')}, you might need to drop something - or you can try to carry it all.")
        if test in ("ignore", "i"):
            if game.player["encumbered"]: # 50/50 chance to drop something if already encumbered and choose to ignore
                outcome = roll_risk()
                if outcome in (1, 2):
                    #print(f"Forced to drop something.") #TODO: remove this later.
                    drop_loot(forced_drop=True) # force drop something

            slowWriting("Well alright. You're the one in charge...")
            game.player["encumbered"] = True
        else:
            slowWriting("You decide to look in your inventory and figure out what you don't need.")
            drop_loot()
    print()
    #slowWriting(f"Inventory items: {len(game.inventory)}") # prints after the forced drop, so it's not really that secret.
    print()
    return item

#def loot(value):
#
#    table = {
#        1: "minor_loot",
#        2: "medium_loot",
#        3: "great_loot",
#        4: "special_loot"
#    }##

#    loot_val = table[value]
#    if game.w_value:
#        #print((choices.loot_groups[loot_val]))
#        return random.choice((choices.loot_groups[loot_val]))
#        #return random.choice((choices.weird_loot_table[value]))
#    return random.choice((choices.loot_groups[loot_val]))

def have_a_rest():
    slowWriting("You decide to take it easy for a while.")
    # can do things like read a book, check phone if you have them, daydream (roll for it), etc.
    print()
    slowWriting("But after a while, you decide to get up anyway.")
    look_around()

def get_hazard():
    inside = getattr(p_data[game.place], "inside")
    if inside:
        #pick an option from 'any' and 'inside'
        options = choices.trip_over["any"] + choices.trip_over["inside"]
    else:
        options = choices.trip_over["any"] + choices.trip_over["outside"]

    hazard = random.choice(options)
    #print(f"hazard randomly chosen: `{hazard}`")
    return hazard

def relocate(need_sleep=None):
    options = set()
    current_loc = game.place
    current_weather = game.weather
    #load_world() # this is silly. Rebuilding the full world load just for this? No. Changing this.
    #print(f"Old time: {game.time}")
    times_of_day = choices.time_of_day
    time_index=times_of_day.index(game.time)
    #print(f"time index: {time_index}")
    new_time_index=time_index + 1 # works
    #print(f"new_time_index: {new_time_index}, len(times_of_day): {len(times_of_day)}")
    if new_time_index == len(times_of_day):
        new_time_index=0
    game.time=times_of_day[new_time_index] ### WOP TODO FINISH THIS BIT
    #print(f"new time: {game.time}")
    weather_options = list(env_data.weatherdict)
    weather_index=weather_options.index(game.weather)
    #print(f"Old weather: {game.weather}")
    #print(f"weather_index: {weather_index}")
    weather_variance=random.choice([int(-1), int(1)])
    new_weather_index=weather_index + int(weather_variance)
    #print(f"new_weather_index: {new_weather_index}, len(weather_options: {len(weather_options)})")
    if new_weather_index == len(weather_options):
        new_weather_index=0
    game.weather=weather_options[new_weather_index]
    #print(f"New weather: {game.weather}")

    """
    What needs to change?

        We choose the new place from the options. Should just get the list separate from load_world entirely.

        Options should not include current location (so have to remove the min of 3 options, as there are only 3 locations in operation presently.) (Will not implement this yet, as just sticking to the one location is handy for now.)

        Time of day advances by 1 for each relocation.
        need_sleep = true if overnight happens (ie if current == midnight.)


        * Need to add something to 'stress' based on discoveries/travel/etc. If you travel a bunch but don't find/accomplish anything, stress point. Something like that. Later.

    """

    while len(options) < 3:
        new_place = random.choice((game.loc_list))
        if new_place not in options: # and new_place != current_loc <- turn on when I don't want current loc as an option anymore.
            options.add(new_place)

    slowWriting("Please pick your destination:")
    game.place = option(options, print_all=True)
    load_world(relocate=True)
    if game.place==current_loc:
        print(f"You decided to stay at {switch_the(game.place, 'the')} a while longer.")
    else:
        slowWriting(f"You make your way to {game.place}. It's {game.time}, the weather is {game.weather}, and you're feeling {game.emotional_summary}.")
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
#    else:
#        decision = option("look around", "sit", preamble=f"Do you want to look around {switch_the(f'the {game.place}')}, or sit for a while?")
#        if decision == "look around":
#            look_around()
#        else:
#            have_a_rest()
#    #print(f"New place: {game.place}, new weather: {game.weather}")

def sleep_outside():
    if getattr(p_data[game.place], "nature"):
    #if p_data[game.place]."nature": # changed from 'description' in locations.py
        slowWriting("You decide to spend a night outside in nature.")
    else:
        slowWriting(f"You decide to spend a night outside in {switch_the({game.place}, "the ")}.")
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
            slowWriting("Something else happens here. Who knows what.")
            the_nighttime()
        else:
            relocate(need_sleep=True)

def sleep_inside():
    slowWriting(f"Deciding to hunker down in {game.place} for the night, you find the comfiest spot you can and try to rest.")
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

            test=option("yes", "no", preamble=f"It's too dark to see much of anything in {switch_the(place, 'the ')}, and without a torch or some other light source, you might trip over something. Do you want to keep looking?")
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
            test = option("stay", "go", preamble=f"You could stay and sleep in {switch_the(place, "the ")} until morning, or go somewhere else to spend the wee hours. What do you do?")
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
            slowWriting(f"Using the power of {reason}, you're able to look around {switch_the(game.place, 'the ')} without too much fear of a tragic demise.")
        obj = getattr(p_data[game.place], game.facing_direction)
        #print(f"\n{obj}\n")
        print(f"\n{obj}\n") # description
        if obj == None or obj == "None":
            print("This description hasn't been written yet... It should have some ")
        remainders = list(x for x in game.cardinals if x is not game.facing_direction)
        print(f"Directions to look: {remainders}")
        options = choices.location_loot.get(game.place)
        print(f"Interactable items: {list(options.keys())}") # this is not defined per facing_direction. Needs to be.
        #slowWriting(f"You can look around more, or try to interact with the environment:")

        text=option(remainders, "leave", list(options.keys()), no_lookup=None, print_all=True, preamble="You can look around more, leave, or try to interact with the environment:")
        #text=user_input()
        #print(f"Text from options: {text}")
        if text in remainders:
            game.facing_direction=text
            look_light("turning") # run it again, just printing the description of where you turned to.
        if (text in obj or text in options) and text != "":
            #print(f"Text: {text}, obj: {obj}")
            if text in list(options):
            #for option_entry in options: ## 'if text in options', surely?
            #    if text in option_entry: # this gets 'television' if I type 'e'. Not working...
                loc_loot = choices.initialise_location_loot() # we don't do this every time. This is jsut for testing.
                item_entry = loc_loot.get_item(text)
                if item_entry:
                    print(f"{loc_loot.describe(text, caps=True)}")
                    #print("What do you want to do? [Investigate] item, [take] item, [leave] it alone.") # Do I want to list the options like this, or just try to make a megalist of what options may be chosen and work from that?
                    decision=option("investigate", "take", "leave", preamble="What do you want to do - investigate it, take it, or leave it alone?")
                    #decision=user_input()
                    if decision.lower()=="investigate":
                        print("Nothing here yet.")
                    elif decision.lower()=="take":
                        get_loot(value=None, random=True, named=text, message=None)
                        print("[Find the loot taking function that already exists, make sure the item is removed from the list here.]") # does the current loot table allow for 'already picked up'? I don't think it does. Need to do that.
                    elif decision.lower()=="leave":
                        print(f"You decide to leave the {text} where you found it.")
                    # this should loop, not just kick you out and relocate you immediately.
                else:
                    print(f"No entry in loc_loot for {item}: {list(loc_loot)}")
            else:
                print(f"Could not find what you're looking for. The options: {options}")
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
    slowWriting(f"With the weather {add_text}{game.weather}, you decide to look around the {game.facing_direction} of {switch_the(game.place, 'the ')}.")
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
    decision = option("yes", "no", preamble="Keep looping?")
    if decision in yes:
        game.checks["play_again"]
        game.time = "morning"
        inner_loop()
    else:
        slowWriting("Hope you had fun? Not sure really what this is, but thank you.")
        exit()

def describe_loc():
    #loc = game.place
    ## Needs to also describe weather here.
    loc_data = p_data[game.place]
    slowWriting(f"You take a moment to take in your surroundings. {loc_data.overview}")
    test=option(game.cardinals, "go", print_all=True, preamble="Pick a direction to investigate, or go elsewhere?")
    if test in game.cardinals:
        game.facing_direction = test
        look_around()
    else:
        slowWriting(f"You decide to leave {switch_the(game.place, 'the ')}")
        relocate()

def inner_loop():

    slowWriting(f"You wake up in {game.place}, right around {game.time}. You find have a bizarrely good sense of cardinal directions; how odd.")
    places[game.place].visited = True
    places[game.place].first_weather = game.weather

    slowWriting(f"`{game.playername}`, you think to yourself, `is it weird to be in {game.place} at {game.time}, while it's {game.weather}?`")# And with so {game.pops} people around?`")
    print()
    describe_loc()

    test=option("stay", "go", preamble="What do you want to do? (Stay) here and look around, or (Go) elsewhere?")
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
    print()
    slowWriting("[[ Type 'help' for controls and options. ]]")
    print()
    inner_loop()

run() # uncomment me to actually play again.

def test():
    #from set_up_game import calc_emotions#loadout, set_up
    #calc_emotions()#
    global game
    game = set_up(weirdness=True, bad_language=True, player_name="A")
    get_hazard()

#test()

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
