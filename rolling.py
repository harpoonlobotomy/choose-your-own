#rolling.py
from set_up_game import game
from logger import logging_fn
import random

def roll_risk(rangemin=None, rangemax=None):
    logging_fn()

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
                print(f"Roll: {roll}\n{msg}")
            return val


def outcomes(state, activity):
    from misc_utilities import assign_colour
    logging_fn()

    item = None
    ## item needs to be a random item from inventory, droppable. (TODO: Add droppable (or, 'undroppable', probably better) to relevant items so you can't drop anything too important.)
    # Also it needs to be dropped at the location you're currently at.
    very_negative = ["It hurts suddenly. This isn't good...", f"You suddenly realise, your {assign_colour(item)} is missing. Did you leave it somewhere?"]
    negative = [f"Uncomfortable, but broadly okay. Not the worst {activity} ever.", f"Entirely survivable, but not much else to say about this {activity}.", f"You did a {activity}. Not much else to say about it really."]
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
            from env_data import locRegistry as loc
            loc.current.items.append(dropped)
        item = dropped
    return outcome
