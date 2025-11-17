import choices
from set_up_game import load_world, set_up
from choices import choose, loot
import random
from locations import run_loc, places, descriptions
from env_data import placedata_init, p_data
from pprint import pprint
# https://projects.blender.org/blender/blender/pulls/149089
rigged = True
rig_place = "a graveyard"
rig_weather = "raining"
rig_time = "late evening"


user_prefs = r"D:\Git_Repos\Choose_your_own\path_userprefs.json"
run_again = False

yes = ["y", "yes"]
no = ["n", "no", "nope"]
night = ["midnight", "late evening", "night", "pre-dawn"]

import time

def slowLines(txt, speed=0.1):
    print(txt)
    time.sleep(speed)

def slowWriting(txt, speed=0.01):
    for c in str(txt):
        print(c, end='', flush=True)
        time.sleep(speed * random.uniform(0.5, 2))
    print()

def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def do_inventory():

    slowWriting("INVENTORY: ")
    slowWriting(f"    {game.inventory}")
    while True:
        slowWriting("To examine an item more closely, type it here, else type anything else.")
        test = user_input()
        if test in game.inventory:
                #places[game.place].first_weather = game.weather
            # needs to be looking in [name].values().get("inv_name")
            desc = loot.describe(test, caps=True)
            if desc and desc != "":
                slowWriting((desc))
            else:
                slowWriting(f"Not much to say about the {test}.")
                print()
        else:
            break

def user_input():
    text = input()
    if text.lower() == "help":
        print()
        slowWriting(f"  Type the (highlighted) words to progress, 'i' for 'inventory', 'd' to describe the environment, 'settings' to set some settings - that's about it.")
        print()
    if text.lower() == "i":
        print()
        do_inventory()
        print()
    if text.lower() == "stats":
        print()
        print(f"    weird: {game.weirdness}. location: {game.place}. Checks: {game.checks}")
        print(f"    inventory: {game.inventory}")
        pprint(f"    {game.player}")
        print()
    if text.lower() == "d":
        loc_data = p_data[game.place]
        print(f"{text}: Describe location.")
        slowWriting(f"[{smart_capitalise(game.place)}]  {loc_data.overview}")
#        print(f"{[game.place]}:{places[game.place].description}")#{descriptions[game.place].get('description')}")
        print()
    if text.lower() in ("exit", "quit", "stop"):
        print("Okay, bye now!")
        exit()
    else:
        return text
    return None

def option(*values, no_lookup=None, print_all=False, preamble=None):

    option_chosen = False
    values = [v for v in values if v is not None]
    formatted = []
    for v in values:
        if isinstance(v, (list, tuple)):
            if print_all:
                formatted.append(f"({', '.join(v)})")
            else:
                formatted.append(f"({v[0]})") # add the first one as the 'label', use the rest as list later.
        else:
            formatted.append(f"({v})")

    while option_chosen != True:
        if preamble:
            slowWriting(preamble)
        if len(formatted) > 1:
            slowWriting(f"    {', '.join(formatted[:-1])} or {formatted[-1]}")
        else:
            slowWriting(f"    {formatted[0]}")

        if no_lookup:
            return
        test = user_input()
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
                return test

        for an_option in values:
            if test == an_option:
                return an_option
            if isinstance(an_option, (list, tuple)): # manually listed in the call signature
                for sub in an_option:
                    if len(test) == 1:
                        if test == sub[0].strip():
                            return sub
                    #print(f"Sub: {sub} in an_option: {an_option}")
                    if print_all:
                        if test == sub:
                            return sub
                    elif test == sub:
                        return sub
                    elif test in choose[sub]:
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
    negative = [f"Uncomfortable, but broadly okay. Not the worst {activity} ever", "Entirely survivable, even if not much else", f"You did a {activity}. Not much else to say about it really."]
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
            slowWriting("Hey so... not everyone loves inventory management. So I'll give you the option now - do you want to turn it off and carry without limitation?")
            slowWriting("         (yes) or (no)")
            test = user_input()
            if test in yes:
                game.player["inventory_management"] = False
            if test in no:
                game.player["inventory_management"] = True
            # if no proper answer, it stays as it already was.

    game.inventory = newlist
    print()

def switch_the(text):

    for article in ("a ", "an "):
        if article in text:
            text = text.replace(article, "")
    return text

def get_loot(value, message=None):

    carryweight = game.volume
    print(f"value: {value}")
    item = loot.random_from(value)
    print(f"Item: {item}")
    if message:
        message = message.replace("[item]", loot.nicename(item))
        slowWriting(message)
    #item = loot.get_item(item)
    print(f"after get_item: {item}")
    slowWriting(f"[[ `{item}` added to inventory. ]]")
    game.inventory.append(item)
    if len(game.inventory) > carryweight:
        print()
        test = option(f"drop", "ignore", preamble=f"It looks like you're already carrying too much. If you want to pick up {switch_the(f'the {item}')}, you might need to drop something - or you can try to carry it all.")
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

def stay_resting():
    slowWriting("You decide to take it easy for a while.")
    # can do things like read a book, check phone if you have them, daydream (roll for it), etc.
    print()
    slowWriting("But after a while, you decide to get up anyway.")
    look_around()

def relocate(need_sleep=None):
    options = []
    current = game.place
    load_world()
    while len(options) < 3:
        if game.place == current or game.place in options or len(options) < 3:
            new_place = load_world()
            if new_place in options:
                continue
            options.append(new_place) ## still getting duplicates

    slowWriting("Please pick your destination:")
    game.place = option(options, print_all=True)
    slowWriting(f"You make your way to {game.place}. The weather is {game.weather}, and you're feeling {game.emotional_summary}.")
    if places[game.place].visited:
        slowWriting(f"You've been here before... It was {places[game.place].first_weather} the first time you came.")
        if places[game.place].first_weather == game.weather:
            print("I wonder if it's the same rain...")
    else:
        places[game.place].visited = True
        places[game.place].first_weather = game.weather

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
        decision = option("look around", "sit", preamble=f"Do you want to look around {switch_the(f'the {game.place}')}, or sit for a while?")
        if decision == "look around":
            look_around()
        else:
            stay_resting()
    #print(f"New place: {game.place}, new weather: {game.weather}")

def sleep_outside():
    if descriptions[game.place].get("nature"):
        slowWriting("You decide to spend a night outside in nature.")
    else:
        slowWriting(f"You decide to spend a night outside in {game.place}.")
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
    new_day()

def look_around(status=None):
    item = None
    place = game.place
    time = game.time
    weather = game.weather
    weather = "stormy"
    time = "midnight"

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

            test=option("yes", "no", preamble=f"Honestly it's too dark to see much of anything in {switch_the(f'the {place}')}. You can just about avoid tripping over yourself, but it's hard to see much else. Do you want to keep trying?")
            if test in yes:
                slowWriting("Determined, you peer through the darkness.")
                outcome = roll_risk()
                if outcome == 1:
                    slowWriting("OW! You roll your ankle pretty badly.")
                    if len(game.inventory) < 4:
                        item = get_loot(1, message=f"Once your eyes adjust a bit, you manage to make out more shapes than you expected. You find [item].")
                        slowWriting(f"It's only a minor injury, sure, but damn it stings. You did find {item} while facefirst in the middle of {place}, though.")
                    if game.w_value:
                        ("You see something shimmer slightly off in a bush, but by the time you hobble over, whatever it was has vanished.")
                if outcome == 2:
                    item = get_loot(1, message=f"Narrowly avoiding tripping over some poorly lit hazard, you find [item]. Better than nothing, but probably all you'll find until there's more light.")
                    # game.carrier_size compared to item.size? Can I be bothered?
                if outcome in (3,4):
                    item = get_loot(2, message=f"Once your eyes adjust a bit, you manage to make out more shapes than you expected. You find [item]")
            if test in no:
                slowWriting("Thinking better of it, you decide to keep the advanced investigations until you have more light. What now, though?")
            test = option("stay", "go", preamble=f"You could stay and sleep in {place} until morning, or (go) somewhere else to spend the wee hours. What do you do?")
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
        if reason == None:
            reason = "the sun"
        slowWriting(f"Using the power provided by {reason}, you're able to look around {game.place} without too much fear of a tragic demise.")
        slowWriting("Unfortunately I haven't written anything here yet. Maybe just... go somewhere else?")
        slowWriting(f"Keeping in mind that it's {time} and {weather}, where do you want to go?")
        relocate()

    if status == "exhausted" and time not in night:
        slowWriting("Stumbling, you're going to hurt yourself even if it's nice and bright. Haven't written it yet though.")
        look_dark() # new one for this with light variation. Maybe 'looking' should be a class... It's going to be a major part of it....

## ==== Actual start here ===

    slowWriting(f"With the weather {game.weather}, you decide to look around the {game.facing_direction} of {switch_the(f'the {game.place}')}.")
    if time in night:
        slowWriting(f"It's {game.time}, so it's dark.")
        look_dark()
    else:
        if places[game.place].sub_places:
            for sub_place in places[game.place].sub_places:
                print(f"[[[[  sub_place: {sub_place}  ]]]]") # this has never printed.
        else:
            look_light()

def new_day():
    #print("You wake up ")
    decision = option("yes", "no", preamble="Keep looping?")
    if decision in yes:
        game.checks["play_again"] # does nothing for now but I want other exit points.
        game.time = "morning"
        inner_loop()
    else:
        slowWriting("Hope you had fun? Not sure really what this is, but thank you.")
        exit()

cardinals = ("north", "south", "east", "west")
def describe_loc():
    #loc = game.place
    loc_data = p_data[game.place]
    slowWriting(f"{loc_data.overview}")
    test=option(cardinals, "go", print_all=True, preamble="Pick a (direction) to investigate, or (Go) elsewhere?")
    if test in cardinals:
        game.facing_direction = test
        look_around()
    else:
        slowWriting(f"You decide to leave {switch_the(f'the {game.place}')}")
        relocate()

def inner_loop():

    if rigged:
        game.place = rig_place
        game.weather = rig_weather
        game.time = rig_time

    slowWriting(f"You wake up in {game.place}, right around {game.time}. You find have a bizarrely good sense of cardinal directions; how odd.")
    places[game.place].visited = True
    places[game.place].first_weather = game.weather

    slowWriting(f"`{game.playername}`, you think to yourself, `is it weird to be in {game.place} at {game.time}? And with so {game.pops} people around?`")
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

run() # TODO:: uncomment me to actually play again.

def test():
    from set_up_game import calc_emotions#loadout, set_up
    calc_emotions()
    #game = set_up(weirdness=True, bad_language=True, player_name="A")
    #loadout()

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
