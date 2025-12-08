## item_definitions, chopped up from the loot tables in choices.py

import random
currency = random.choice(("dollar", "pound", "yen"))

flags=["can_open", "locked", "flammable", "can_pick_up", "container", "dirty", "fragile", "can_open", "can_read"]

######  FLAGS ########
CAN_PICKUP = "can_pick_up"
CONTAINER = "container"
FLAMMABLE = "flammable"
DIRTY = "dirty"
LOCKED = "locked"
FRAGILE = "fragile"
CAN_OPEN = "can_open"
CAN_READ = "can_read"
WEIRD = "weird"
DUPE = "dupe" ## can be a duplicate, found multiple times. Do not remove from loot pool after selection.
IS_CHILD = "is_child"

# 'fragile' just means it can be broken. Contexts required for breaking are not yet defined.
## if 'loot_type', is a random draw. else is from a location.

"""
Need to figure out how to define 'container limits' ' possible values.
eg.
"container_limits" = 'small_flat_things', 'a few marbles', 'smaller_than_apple', 'smaller_than_basketball', etc

And then all items that can be picked up need one of these flags, I guess. Unless they're too big to put in any container (inc plastic bag).

So if container lists 'smaller_than_apple', anything in that category or below is allowed in that container. Doesn't factor for multiple things yet.
"""
####### CONTAINER LIMIT CATEGORIES ############

SMALL_FLAT_THINGS = "small_flat_things"
A_FEW_MARBLES = 'a_few_marbles'
SMALLER_THAN_APPLE = 'smaller_than_apple'
PALM_SIZED = 'palm_sized'
SMALLER_THAN_BASKETBALL = 'smaller_than_basketball'
BIGGER_THAN_BASKETBALL = 'bigger_than_basketball'

MOSS_TRAIT = "After 3 ingame days, after being picked up and kept in inventory, will dry. If dry, no longer suitable for commerce with bridge goblin."


## Need to track no of days/nights. Should already be doing this.

##  "starting_children": ["dried flowers"] -- changed to 'starting_children', so it's used in init but not picked up by default children checks. May not be necessary.
# item_size == the size the thing is

group_flags = {"magazine": (FLAMMABLE, CAN_READ)}

###

"""
        RULES:
If 'CAN_PICKUP':
    must have item_size.
If flags(CONTAINER):
    must have container_limits



"""


item_definitions = {
    "glass jar": {"name": "a glass jar with flowers", "description": f"a glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers.",
                    "description_no_children": "a glass jar, now empty aside from some bits of debris.", "starting_children": ["dried flowers"], "name_children_removed":"a glass jar", "flags":[CAN_PICKUP, CONTAINER, DIRTY], "container_limits": SMALLER_THAN_APPLE, "item_size": SMALLER_THAN_BASKETBALL, "starting_location": ("graveyard", "east")},
    "dried flowers": {"name": "some dried flowers", "description": "a bunch of old flowers, brittle and pale; certainly not as vibrant as you imagine they once were.", "started_contained_in": "glass jar",
                    "flags":[CAN_PICKUP, FLAMMABLE], "item_size": SMALLER_THAN_APPLE, "starting_location": ("graveyard", "east")},
    "moss": {"name": "a few moss clumps", "description": "a few clumps of mostly green moss.", "flags":[CAN_PICKUP], "special_traits": MOSS_TRAIT, "item_size": A_FEW_MARBLES, "starting_location": ("graveyard", "east")}, # will dry up after a few days
    "headstone": {"name":"a carved headstone", "description": "a simple stone headstone, engraved with the name `J.W. Harstott`.", "flags":[DIRTY], "starting_location": ("graveyard", "east")},
    "TV set": {"name": "a television set", "description": "A decent looking TV set, probably a few years old but appears to be well kept. Currently turned off. This model has a built-in DVD.",
                    "flags":list(), "starting_location": ("city hotel room", "east")}, # need to be able to add a DVD to this maybe.
    "window": {"name":"a window", "description":"a window, facing out of the hotel room and down over the street below. Currently closed.", "flags":[CAN_OPEN, FRAGILE],
                    "starting_location": ("city hotel room", "east")},
    "carved stick": {"name": "a spiral-carved stick", "description": "a stick, around 3 feet long, with tight spirals carved around the length except for a 'handle' at the thicker end.",
                    "flags":[CAN_PICKUP], "item_size": BIGGER_THAN_BASKETBALL,  "starting_location": ("forked tree branch", "east")},
    "paperclip": {"name": "a paperclip", "description": "a humble paperclip.", "flags":[DUPE], "item_size": SMALL_FLAT_THINGS, "loot_type": "magazine"},
    "puzzle mag": {"name": "a puzzle magazine", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "magazine"},
    "fashion mag": {"name": "a fashion magazine", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "magazine"},
    "gardening mag": {"name": "a gardening magazine", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "magazine"},
    "mail order catalogue": {"name": "a mail order catalogue", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "magazine"},
    "car keys": {"name": "a set of car keys", "description": "none yet","flags":list(),  "item_size": A_FEW_MARBLES, "loot_type": "starting"},
    "fish food": {"name": "a jar of fish food", "description": "none yet", "flags":list(), "item_size": A_FEW_MARBLES, "loot_type": "starting"},
    "anxiety meds": {"name": "a bottle of anxiety meds", "description": "none yet", "flags":list(), "item_size": A_FEW_MARBLES, "loot_type": "starting"},
    "regional map": {"name": "a regional map", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_APPLE, "loot_type": "starting"},
    "unlabelled cream": {"name": "an unlabelled cream", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_APPLE, "loot_type": "starting"},
    "batteries": {"name": "a set of batteries", "description": "none yet", "flags":list(), "item_size": A_FEW_MARBLES, "loot_type": "starting"},
    "costume jewellery": {"name": "a bit of costume jewellery", "description": "Pretty but probably not too expensive. Gold metal with dark red gems.", "flags":[FRAGILE], "item_size": A_FEW_MARBLES, "loot_type": "minor_loot"},
    "plastic bag": {"name": "a sturdy plastic bag", "description": "a used plastic bag from a grocery store. No holes, at least.", "flags":[CONTAINER, FLAMMABLE, DUPE], "container_limits": BIGGER_THAN_BASKETBALL, "item_size": SMALLER_THAN_APPLE, "loot_type": "minor_loot"},
    "pretty rock": {"name": "a pretty rock", "description": "A particularly pretty rock. A nice colour and texture, pleasant to hold.", "flags":[DUPE], "item_size": A_FEW_MARBLES, "loot_type": "minor_loot"},
    "damp newspaper": {"name": "a damp newspaper", "description": "A damp newspaper from about a week ago.", "flags":[CAN_READ, FLAMMABLE], "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "minor_loot"}, # maybe not flammable - it'll take a while
    f"5 {currency} note": {"name": f"a 5 {currency} note", "description": "A small amount of legal tender. Could be useful if you find a shop.", "flags":[FLAMMABLE, DUPE], "item_size": SMALL_FLAT_THINGS, "loot_type": "medium_loot"},
    "paper scrap with number": {"name": "a scrap of paper with a number written on it", "description": "A small scrap of torn, off-white paper with a hand-scrawled phone number written on it.",
                    "flags":[CAN_READ, FLAMMABLE], "item_size": SMALL_FLAT_THINGS, "loot_type": "medium_loot"},
    "mobile phone": {"name": "a mobile phone", "description": "A mobile phone. You don't think it's yours. Doesn't seem to have a charge.", "flags":[FRAGILE, LOCKED], "item_size": PALM_SIZED, "loot_type": "great_loot"},
    "wallet": {"name": "a wallet, with cash", "description": f"A worn leather wallet with around 30 {currency} inside. No identification or cards.", "flags":[CAN_OPEN, CONTAINER], "container_limits": SMALL_FLAT_THINGS, "item_size": PALM_SIZED, "loot_type": "great_loot"},
    "the exact thing": {"name": "the exact thing you've been needing", "description": "It's the exact thing you need for the thing you need it for. But only once.", "flags":list(), "item_size": SMALL_FLAT_THINGS, "loot_type": "special_loot"},
    "severed tentacle": {"name": "a severed tentacle", "description":"none yet", "flags":[WEIRD], "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "weird"}
    }



def update_flags():
    #print("\n" * 10)
    for item, attr in item_definitions.items():
        #print(f"Item: {item}, attr: {attr}")
        if "loot_type" in list(attr):
            item_data = item_definitions[item]
            if not CAN_PICKUP in item_data["flags"]:
                #print(f"Can Pickup not listed in `{item}`. Adding now.")
                item_data["flags"].append(CAN_PICKUP)

            if not item_data.get("item_size"):
                print(f"Item `{item}` does not have item size but can be picked up. Please add an item size to {item}'s entry in item_definitions")
            if item_data.get("loot_type") == "magazine":
                for flag in group_flags["magazine"]:
                    if flag not in item_data["flags"]:
                        item_data["flags"].append(flag)
            if item_data.get("started_contained_in"):
                item_data["flags"].append(IS_CHILD) ## this flag is flexibile. Maybe shouldn't be added here. Maybe should be added at the instance generation instead, so 'IS_CHILD' can be removed when the item is separated from Parent.
            #print(f"Amended: {item_data["flags"]}")

    #from pprint import pprint
    #pprint(item_definitions)

    return item_definitions
