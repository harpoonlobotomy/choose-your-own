## item_definitions, chopped up from the loot tables in choices.py

import random

currency = random.choice(("dollar", "pound", "yen"))

colour_list = ["blue", "red", "green"] ## testing this for different coloured rocks. It'll be ignored in the description though, they're still treated as identical. But this at least has the start of some minor variatin, even if it's not used yet.

texture_list = ["smooth", "bumpy", "cracked", "slightly rough"]

def get_random_col(): ## doesn't work. It is set at runtime and always returns the same. Same as 'texture list''s method.
    #It's fine, it wasn't implemented meaningfully anyway, but fix it later.
    return random.choice(colour_list)


#flags=["can_open", "locked", "flammable", "can_pick_up", "container", "dirty", "fragile", "can_open", "can_read"] # why do I need this list here? Really should just make a dict...

######  FLAGS ########
CAN_PICKUP = "can_pick_up"
CONTAINER = "container"
FLAMMABLE = "flammable"
DIRTY = "dirty"
LOCKED = "locked"
CAN_LOCK = "can_lock"
FRAGILE = "fragile"
CAN_OPEN = "can_open"
CAN_READ = "can_read"
CAN_COMBINE = "can_combine"
WEIRD = "weird"
DUPE = "dupe" ## can be a duplicate, found multiple times. Do not remove from loot pool after selection.
IS_CHILD = "is_child"
COMBINE_WITH = "combine_with"
CAN_REMOVE_FROM = "can_remove_from" ## not sure about this. Serves the same purpose as 'is_child' etc but might be a more directly accessible route to the same data. Can use it as a direct route to parenting. Separate this child? Instead of checking parent containers etc, just 'can remove from x'. idk. Maybe.

# 'fragile' just means it can be broken. Context's required for breaking are not yet defined.
## if 'loot_type', is a random draw. else is from a location.

## DOING STUFF WITH INVENTORY. This section is just thinking aloud. Not implemented at all.

item_actions = [  ## NOTE: I think this is only used for get_actions_for_item, which won't be needed in the new setup. Need to check into it.
    CAN_PICKUP,
    CONTAINER,
    FLAMMABLE,
    DIRTY,
    LOCKED,
    CAN_LOCK,
    FRAGILE,
    CAN_OPEN,
    CAN_READ,
    CAN_COMBINE,
    WEIRD,
    DUPE,
    IS_CHILD,
    COMBINE_WITH,
    CAN_REMOVE_FROM
    ]


#item_actions = {"from_flags": [CAN_READ], "contextual_actions": [{CAN_PICKUP: "not_in_inventory"}, {CAN_OPEN: "is_not_open"}, {CAN_COMBINE: "requires_item"}, {FLAMMABLE: "has_fire"}, {LOCKED:"needs_key"}]} ## 'has_fire' = player state, whether matches or it as a location with viable fire source.

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
KEY="key"
PANACEA = "panacea" # magical item that does exactly what is needed in the given context, then expires.

TAKES_BATTERIES = "takes_batteries"
IS_CHARGED = "is_charged"
CAN_BE_CHARGED = "is_charged"

container_limit_sizes = {
    SMALL_FLAT_THINGS: 1,
    A_FEW_MARBLES: 2,
    SMALLER_THAN_APPLE: 3,
    PALM_SIZED: 4,
    SMALLER_THAN_BASKETBALL: 5,
    BIGGER_THAN_BASKETBALL: 6
}

## INVESTIGATE ITEM:
## if CAN_READ: [ "print_on_investigate": paper_scrap_details, ]
# ' is_tested' - varying data based on roll. Else, straight print without checking for roll state.

detail_data = { # should tie this into the class directly. Will leave it here for now, flagging hard.

# failure = <10, success = 10-19, crit = 20.
"paper_scrap_details": {"is_tested": True, "failure": "The last three digits are 487, but the rest are illegible.", "success": "It takes you a moment, but the number on the paper is `07148 718 487'. No name, though.", "crit": "The number is `07148 718 487. Looking closely, you can see a watermark on the paper, barely visible - `Vista Continental West`. Do you know that name?"},

"puzzle_mag_details": {"is_tested":False, "print_str": "A puzzle magazine. Looks like someone had a bit of a go at one of the Sudoku pages but gave up. Could be a nice way to wait out a couple of hours if you ever wanted to."},

"fashion_mag_details": {"is_tested":False, "print_str": "A glamourous fashion magazine, looks like it's a couple of years old. Not much immediate value to it, but if you wanted to kill some time it'd probably be servicable enough."},

"gardening_mag_details": {"is_tested":False, "print_str": "A gardening magazine, featuring the latest popular varieties and a think-piece on the Organic vs Not debate. Could be a decent way to wait out a couple of hours if you ever wanted to."},

"mail_order_catalogue_details": {"is_tested":False, "print_str": "A mail order catalogue, with the reciever's address sticker ripped off. Clothes, homegoods, toys, gadgets - could be a nice way to wait out a couple of hours if you ever wanted to."},

"regional_map_details": {"is_tested":True, 1: "Despite always knowing which way is north, this map is utterly confounding to you.", 3: "A pretty detailed map of the local area. Could be good for finding new places to go should you have a destination in mind."},

"damp_newspaper": {"is_tested":True, 1: "Despite your best efforts, the newspaper is practically disintegrating in your hands. You make out something about an event in ballroom, but nothing beyond that..", 3: "After carefully dabbing off as much of the mucky water and debris as you can, you find the front page is a story about the swearing in of a new regional governor, apparenly fraught with controversy.", 4: "Something about a named official and a contraversy from years ago where a young man went missing in suspicious circumstances."} ## no idea where this would go, but I need some placeholder text so here it is.
}
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
if CAN_COMBINE:
    must have something to combine with. (Note: At present, those things don't exist yet, all just placeholders.)

SECONDARY RULES:

    if "CAN_BE_CHARGED": must be able to find a charger. Can be combined with charger.
    if "CAN_LOCK": must have a key

"""

graveyard = "graveyard"
city = "city hotel room" ## better way of doing it, in case I want to change the names of locations later. Ideally, have this centralised somewhere accessible.

item_defs_dict = {
    "watch": {"name": "a gold watch", "description": f"A scratched gold watch.", "flags": [CAN_PICKUP], "item_size": SMALLER_THAN_APPLE},
    "glass jar": {"name": "a glass jar with flowers", "description": f"a glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers.",
                    "description_no_children": "a glass jar, now empty aside from some bits of debris.", "starting_children": ["dried flowers"], "name_children_removed":"a glass jar", "flags":[CAN_PICKUP, CONTAINER, DIRTY], "container_limits": SMALLER_THAN_APPLE, "item_size": SMALLER_THAN_BASKETBALL, "starting_location": {graveyard: "east"}},
    "dried flowers": {"name": "some dried flowers", "description": "a bunch of old flowers, brittle and pale; certainly not as vibrant as you imagine they once were.", "started_contained_in": "glass jar",
                    "flags":[CAN_PICKUP, FLAMMABLE], CAN_REMOVE_FROM:"glass jar", "item_size": SMALLER_THAN_APPLE, "starting_location": {graveyard: "east"}},
    "moss": {"name": "a few moss clumps", "description": "a few clumps of mostly green moss.", "flags":[CAN_PICKUP], "special_traits": MOSS_TRAIT, "item_size": A_FEW_MARBLES, "starting_location": {graveyard: "east"}}, # moss trait: will dry up after a few days
    "headstone": {"name":"a carved headstone", "description": "a simple stone headstone, engraved with the name `J.W. Harstott`.", "flags":[DIRTY], "starting_location": {graveyard: "east"}},
    "TV set": {"name": "a television set", "description": "A decent looking TV set, probably a few years old but appears to be well kept. Currently turned off. This model has a built-in DVD player.",
                    "flags":[CAN_COMBINE], COMBINE_WITH: "DVD", "starting_location": {city: "east"}}, # need to be able to add a DVD to this maybe.
    "window": {"name":"a window", "description":"a window, facing out of the hotel room and down over the street below. Currently closed.", "flags":[CAN_OPEN, FRAGILE],
                    "starting_location": {city:"east"}},
    "carved stick": {"name": "a spiral-carved stick", "description": "a stick, around 3 feet long, with tight spirals carved around the length except for a 'handle' at the thicker end.",
                    "flags":[CAN_PICKUP], "item_size": BIGGER_THAN_BASKETBALL,  "starting_location": {"forked tree branch": "east"}},

    "paperclip": {"name": "a paperclip", "description": "a humble paperclip.", "flags":[DUPE], "item_size": SMALL_FLAT_THINGS, "loot_type": "starting"},
    "puzzle mag": {"name": "a puzzle magazine", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "magazine"}, ## could I actually do a sudoku in this?
    "fashion mag": {"name": "a fashion magazine", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "magazine"}, # maybe a teen girl quiz
    "gardening mag": {"name": "a gardening magazine", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "magazine"},
    "mail order catalogue": {"name": "a mail order catalogue", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "magazine"},
    "car keys": {"name": "a set of car keys", "description": "none yet","flags":[CAN_COMBINE, TAKES_BATTERIES], COMBINE_WITH: ["blue_car", "batteries"],  "item_size": A_FEW_MARBLES, "loot_type": "starting"},
    "fish food": {"name": "a jar of fish food", "description": "none yet", "flags":[CAN_COMBINE], COMBINE_WITH: ["fish_tank, river"], "item_size": A_FEW_MARBLES, "loot_type": "starting"},
    "anxiety meds": {"name": "a bottle of anxiety meds", "description": "none yet", "flags":list(), "item_size": A_FEW_MARBLES, "loot_type": "starting"},
    "regional map": {"name": "a regional map", "description": "none yet", "flags":[CAN_READ, ""], "item_size": SMALLER_THAN_APPLE, "loot_type": "starting"},
    "unlabelled cream": {"name": "an unlabelled cream", "description": "none yet", "flags":list(), "item_size": SMALLER_THAN_APPLE, "loot_type": "starting"}, ## any item not used during starting should be put onto a value list so it can be found later.
    "batteries": {"name": "a set of batteries", "description": "none yet", "flags":list(DUPE), "item_size": A_FEW_MARBLES, "loot_type": ["starting", "medium_loot"]}, ## need to allow for lists
    "costume jewellery": {"name": "a bit of costume jewellery", "description": "Pretty but probably not too expensive. Gold metal with dark red gems.", "flags":[FRAGILE], "item_size": A_FEW_MARBLES, "loot_type": "minor_loot"},
    "plastic bag": {"name": "a sturdy plastic bag", "description": "a used plastic bag from a grocery store. No holes, at least.", "flags":[CONTAINER, FLAMMABLE, DUPE], "container_limits": BIGGER_THAN_BASKETBALL, "item_size": SMALLER_THAN_APPLE, "loot_type": "minor_loot"},
    "pretty rock": {"name": "a pretty rock", "description": f"A particularly pretty rock. A nice {get_random_col()} colour and {random.choice(texture_list)} texture, pleasant to hold.", "flags":[DUPE], "item_size": A_FEW_MARBLES, "loot_type": "minor_loot"},
    "damp newspaper": {"name": "a damp newspaper", "description": "A damp newspaper from about a week ago.", "flags":[CAN_READ, FLAMMABLE], "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "minor_loot"}, # maybe not flammable - it'll take a while
    f"5 {currency} note": {"name": f"a 5 {currency} note", "description": "A small amount of legal tender. Could be useful if you find a shop.", "flags":[FLAMMABLE, DUPE], "item_size": SMALL_FLAT_THINGS, "loot_type": "medium_loot"},
    "paper scrap with number": {"name": "a scrap of paper with a number written on it", "description": "A small scrap of torn, off-white paper with a hand-scrawled phone number written on it.",
                    "flags":[CAN_READ, FLAMMABLE], "item_size": SMALL_FLAT_THINGS, "print_on_investigate": True, "loot_type": "medium_loot"},
    "mobile phone": {"name": "a mobile phone", "description": "A mobile phone. You don't think it's yours. Doesn't seem to have a charge.", "flags":[FRAGILE, LOCKED, CAN_LOCK, CAN_BE_CHARGED], KEY:"mobile_passcode", "item_size": PALM_SIZED, "loot_type": "great_loot"},
    "wallet": {"name": "a wallet, with cash", "description": f"A worn leather wallet with around 30 {currency} inside. No identification or cards.", "flags":[CAN_OPEN, CONTAINER], "container_limits": SMALL_FLAT_THINGS, "item_size": PALM_SIZED, "loot_type": "great_loot"},
    "the exact thing": {"name": "the exact thing you've been needing", "description": "It's the exact thing you need for the thing you need it for. But only once.", "flags":list(PANACEA), "item_size": SMALL_FLAT_THINGS, "loot_type": "special_loot"},
    "severed tentacle": {"name": "a severed tentacle", "description":"none yet", "flags":[WEIRD], "item_size": SMALLER_THAN_BASKETBALL, "loot_type": "weird"}
    }


def get_item_defs(item_name=None):
    #print("\n" * 10)
    if item_name:
        attr=item_defs_dict.get(item_name)
        return attr
    else:
        for item, attr in item_defs_dict.items():
            #print(f"Item: {item}, attr: {attr}")
            if "loot_type" in list(attr):
                item_data = item_defs_dict[item]
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
                    item_data["flags"].append(IS_CHILD)
                    ## this flag is flexibile. Maybe shouldn't be added here. Maybe should be added at the instance generation instead, so 'IS_CHILD' can be removed when the item is separated from Parent.
                if not item_data.get("current_location"):
                    if item_data.get("starting_location"):
                        item_data["current_location"]=item_data["starting_location"]
                    else:
                        item_data["current_location"] = None
            description = attr["description"]
            if description == "none yet":
                attr["description"] = f"It's {item_data["name"]}"

    return item_defs_dict

