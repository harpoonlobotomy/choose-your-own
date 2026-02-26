# choices - static lists/dicts etc used as reference.

import random

letters_used = ["y", "n", "s", "l", "e" "g"] # should just check 'is the input 1 letter long and that one letter is the first of one of the options

choose = {
    "yes": ["y", "yes"],
    "no": ["n", "no", "nope"],
    "stay": ["s", "stay", "look around"],
    "go": ["g", "go", "elsewhere", "leave", "go elsewhere"] ## added 'leave', remove if it causes issues.
    }

emphasis={"low": ["rather", "a bit", "somewhat", "quite"],
          "high": ["very", "uncharacteristically", "really quite", "extremely"]}

looking_intro=["You take a moment to take in your surroundings.", ""] ## why the hell is this a list? I guess I was intending to have a few variations.

carrier_options = {
    "large": [{"backpack": 10}],
    "medium": [{"cargo pants": 8}, {"satchel": 8}],
    "small": [{"pockets": 6}]
    }

items_template = {
    "category": {"item": {"name": "", "description": ""}}
    }

currency = random.choice(("dollar", "pound", "yen"))

paintings = ["a ship in rough seas", "a small farmstead", "a businessman, sitting in an office in front of a large window", "a dog, running in a field of flowers"]

time_of_day = ["pre-dawn", "early morning", "mid-morning", "late morning", "midday", "early afternoon", "late afternoon", "evening", "late evening", "late night", "midnight", "2am"]

night = ["midnight", "late evening", "late night", "2am"]

## How to best align 'night' to 'time of day'.
#   options:
    #   dict: {pre-dawn: {"night"=False}}
    #   two lists as I have it now, works but means if you edit the t_o_d you have to edit the night entry too.

emotion_table = {
    #"blind": {"weight": 1}, # -1/0 = can see, +1 = blind ## only add later for a reason, don't start with this by default ever
    "tiredness": {"weight": 1}, # -1 = well rested, +1 = tired
    "hunger": {"weight": 1}, # -1 = full, +1 = hungry
    "sadness": {"weight": 1}, # -1 = happy, +1 = sad
    "overwhelmed": {"weight": 1}, # -1/0 = fine, +1 = overwhelmed
    "encumbered": {"weight": 0} # -1/0 = fine, +1 = encumbered
}

trip_over={"any": ["some poorly lit hazard", "your own feet"],
           "outside": ["a small pile of debris"],
           "inside": ["a small pile of clothes"]}


#def get_hazard():
#    logging_fn()
#    inside = getattr(loc.current, "inside")
#    if inside:
#        options = trip_over["any"] + trip_over["inside"]
#    else:
#        options = trip_over["any"] + trip_over["outside"]
#    hazard = random.choice(options)
#    return hazard


def set_choices():

    carrier_size = random.choice((list(carrier_options.keys())))
    carrier_dict = random.choice((carrier_options[carrier_size]))
    for k, v in carrier_dict.items():
        carrier, carryweight = k, v
    return carrier, carryweight

carrier, carryweight = set_choices()

