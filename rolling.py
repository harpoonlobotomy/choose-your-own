#rolling.py
from set_up_game import game
from logger import logging_fn
import random
from misc_utilities import do_print

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
                do_print(f"Roll: {roll}\n{msg}")
            return val
