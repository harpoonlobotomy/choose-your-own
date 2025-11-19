# choices - static dicts etc used as reference.

import random
#from set_up_game import game
# letters used: y, n, s, g


letters_used = ["y", "n", "s", "l", "e" "g"] # should just check 'is the input 1 letter long and that one letter is the first of one of the options

choose = {
    "yes": ["y", "yes"],
    "no": ["n", "no", "nope"],
    "stay": ["s", "l", "stay", "look", "look around"],
    "go": ["g", "e", "go", "elsewhere"]
    }

emphasis={"low": ["rather", "a bit", "somewhat", "quite"],
          "high": ["very", "uncharacteristically", "really quite", "extremely"]}

looking_intro=["You take a moment to take in your surroundings.", ""]

carrier_options = {
    "large": [{"backpack": 10}],
    "medium": [{"cargo pants": 8}, {"satchel": 8}],
    "small": [{"pockets": 6}]
    }

#volume = {
#    "large": 10,
#    "medium": 8,
#    "small": 6
#}

items_template = {
    "category": {"item": {"name": "", "description": ""}}
    }

currency = random.choice(("dollar", "pound", "yen")) # build it here instead
paintings = ["a ship in rough seas", "a small farmstead", "a businessman in front of a large window in an office", "a dog, running around in a field of flowers"]
##
"""
LOOT ATTRIBUTES:
May be getting out of hand. Might need to be dealt with better than this.
"name": "a glass jar",
"description": f"a glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers.",
"description_no_children": "a glass jar, now empty aside from some bits of debris.",
"children": "dried_flowers",
"can_pick_up": True},

In addition, added within the class:
"open" (if status is open or not, default=False)
#"in_start_location" (not sure about this one. Functions to define if it's been moved from where it started, but idk if that matters.)
# have changed the above to
current_location (far more useful - just tracks where the item is now, either 'inventory' or a location. Need to include the cardinal as well as the game.place.)
"start_location": start_loc

                    """

location_loot = {
    "a graveyard": {"glass jar": {"name": "a glass jar", "description": f"a glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers.",
                    "description_no_children": "a glass jar, now empty aside from some bits of debris.", "children": "dried_flowers", "can_pick_up": True},
                  "dried flowers": {"name": "some dried flowers", "description": "a bunch of old flowers, brittle and pale; certainly not as vibrant as you imagine they once were.", "contained_in": "glass jar", "can_pick_up": True},
                  "moss": {"name": "a few moss clumps", "description": "a few clumps of mostly green moss.", "can_pick_up": True},
                  "headstone": {"name":"a carved headstone", "description": "a simple stone headstone, engraved with the name `J.W. Harstott`.", "can_pick_up":False}}, # not separated by facing_direction. Should it be?
    "a city hotel room": {"TV set": {"name": "a television set", "description": "A decent looking TV set, probably a few years old but appears to be well kept. Currently turned off. This model has a built-in DVD.", "can_pick_up": False}, # need to be able to add a DVD to this maybe.
                          "window": {"name":"a window", "description":"a window, facing out of the hotel room and down over the street below. Currently closed.", "can_pick_up":False, "can_open":True}}, # need to add an open/closed attrib for this...
                          # do I want the curtains to be separate? We open the curtains, can look, and can open the window separately? Or maybe the window doesn't open, and we can only open the curtains. The latter I think.
    "a forked tree branch": {"carved stick": {"name": "a spiral-carved stick", "description": "a stick, around 3 feet long, with tight spirals carved around the length except for a 'handle' at the thicker end.", "can_pick_up": True}}
    }

standard_loot = {
    "guaranteed": {"paperclip": {"name": "a paperclip", "description": "a humble paperclip."}},
    "mags": {"puzzle mag": {"name": "a puzzle magazine", "description": "none yet"},
            "fashion mag": {"name": "a fashion magazine", "description": "none yet"},
            "gardening mag": {"name": "a gardening magazine", "description": "none yet"},
            "mail order catalogue": {"name": "a mail order catalogue", "description": "none yet"}
            },
    "starting": {"car keys": {"name": "a set of car keys", "description": "none yet"},
                 "fish food": {"name": "a jar of fish food", "description": "none yet"},
                 "anxiety meds": {"name": "a bottle of anxiety meds", "description": "none yet"},
                 "regional map": {"name": "a regional map", "description": "none yet"},
                 "unlabelled cream": {"name": "an unlabelled cream", "description": "none yet"},
                 "batteries": {"name": "a set of batteries", "description": "none yet"}
                 },
    "minor_loot": {"costume jewellery": {"name": "a bit of costume jewellery", "description": "Pretty but probably not too expensive. Gold metal with dark red gems."},
                   "plastic bag": {"name": "a sturdy plastic bag", "description": "a used plastic bag from a grocery store. No holes, at least."},
                   "pretty rock": {"name": "a pretty rock", "description": "A particularly pretty rock. A nice colour and texture, pleasant to hold."},
                   "damp newspaper": {"name": "a damp newspaper", "description": "A damp newspaper from about a week ago."},
                  },
    "medium_loot": {f"5 {currency} note": {"name": f"a 5 {currency} note", "description": "A small amount of legal tender. Could be useful if you find a shop."},
                 "paper scrap with number": {"name": "a scrap of paper with a phone-number written on it", "description": "A small scrap of torn, off-white paper with a hand-scrawled phone number written on it"}
                  },
    "great_loot": {"mobile phone": {"name": "a mobile phone", "description": "A mobile phone. You don't think it's yours. Doesn't seem to have a charge."},
                 "wallet": {"name": "a wallet, with cash", "description": f"A worn leather wallet with around 30 {currency} inside. No identification or cards."},
                  },
    "special_loot": {"the exact thing": {"name": "the exact thing you've been needing", "description": "It's the exact thing you need for the thing you need it for. But only once."}},
        "weird": {"severed tentacle": {"name": "a severed tentacle", "description":"none yet"}, "second thing": {"other": "next"}
              }
    }

time_of_day = ("pre-dawn", "early morning", "mid-morning", "late morning", "midday", "early afternoon", "late afternoon" "evening", "late evening", "middle of the night", "2am")

starting = ["car keys", "fish food", "anxiety meds", "regional map", "unlabelled cream", "batteries"]

mag = ("puzzle", "fashion", "gardening", "mail order")
minor_loot = ["a sturdy plastic bag", "a bit of costume jewellery", "a pretty rock", "a damp newspaper"]
medium_loot = [f"a 5 {currency} note", "a scrap of paper with a phone-number written on it"]
great_loot = ["a mobile phone", "a wallet, with cash"]
special_loot = ["the exact thing you've been needing"]


weird_minor_loot = ["a sturdy plastic bag", "a bit of costume jewellery", "a cracked carved gem", "a burned book"]
weird_medium_loot = [f"a unusual 5 {currency} note", "a broken metal mask"]
weird_great_loot = ["a scroll with illegible writing", "a bloodied wallet, with equally bloodied cash"]
weird_special_loot = ["the exact thing you've been needing"]

weird_loot_table = {
    1: weird_minor_loot,
    2: weird_medium_loot,
    3: weird_great_loot,
    4: weird_special_loot
}

emotion_table = {
    #"blind": {"weight": 1}, # -1/0 = can see, +1 = blind
    "tired": {"weight": 1}, # -1 = well rested, +1 = tired
    "hunger": {"weight": 1}, # -1 = full, +1 = hungry
    "sadness": {"weight": 1}, # -1 = happy, +1 = sad
    "overwhelmed": {"weight": 1}, # -1/0 = fine, +1 = overwhelmed
    "encumbered": {"weight": 1} # -1/0 = fine, +1 = encumbered
}

#git log
#git shortlog --author="Bastien Montagne" --pretty=format:'%ci | %H' --no-merges -e -n



loot_table = {
    1: "minor_loot",
    2: "medium_loot",
    3: "great_loot",
    4: "special_loot"
}

trip_over={"any": ["some poorly lit hazard", "your own feet"],
           "outside": ["a small pile of debris"],
           "inside": ["a small pile of clothes"]}


def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s

class LootTable:
    def __init__(self, loot_data: dict, name: str = "Unnamed Table"):
        self.name = name
        self.by_category = loot_data
        self.by_name = {}
        self._build_lookup()

    def _build_lookup(self):
        """Flatten the loot data for fast name lookups."""
        for category, items in self.by_category.items():
            for item_name, data in items.items():
                entry = dict(data)
                entry["category"] = category
                self.by_name[item_name] = entry
                self.by_name[item_name].update({"open":False}) # add this for everything, then update if needed.

                ## only for those in location table.
                    # actually no - should use it for documenting the location where random loot was found, too.
                if self.name == "location_loot":
                    start_loc = category
                else:
                    start_loc=None
                #print(f"add location parent as start_location: item_name: {item_name}, location: {start_loc}")
                # current_location:
                self.by_name[item_name].update({"current_location": {"location": "cardinal"}, "start_location": {start_loc: "cardinal"}}) # need to update cardinal, so we have 'found this jar in the east of the graveyard'. I like that better than just 'in the graveyard. May walk it back later.
                #Should add the ability to search a location for something (eg 'I dropped item at the graveyard, will spend time searching specifically. Also general 'looking for clues', related.)

    def get_full_category(self, selection):
        category = selection
        items = list(self.by_category.get(category, {}).keys())
        return items

    def get_item(self, name: str):
        """Retrieve an item by name, or None if not found."""
        return self.by_name.get(name)

    def open_item(self, name:str):
        item = self.get_item(name)
        is_open = item["open"]
        if is_open:
            return "already_open"
        elif item["can_open"]:
            return "can_be_opened"
        else:
            return "cannot_open"

    #def random_from(self, category: str):
    def random_from(self, selection):
        """Pick a random item name from a category (int or str)."""
        if isinstance(selection, int):
            category = loot_table[selection]
        else:
            category = selection
        items = list(self.by_category.get(category, {}).keys())
        return random.choice(items) if items else None

    def describe(self, name: str, caps=False):
        """Convenience method to return a formatted description."""
        item = self.get_item(name)
        if item:
            if caps:
                description = smart_capitalise(item['description'])
            else:
                description = item['description']
            return description#{name} ({item['category']}): {item['description']}"
        return f"No such item: {name}"

    def nicename(self, name: str):
        item = self.get_item(name)
        if not item:
            print("No such item.")
            return None
        return item['name']

    def remove_from_container(self, name:str):
        print("Doesn't do anything yet.")


        #get container item obj
        #mark as 'removed from container'
        # mark container as 'item removed'.
    ## carrier ##
    #carrier_options = {
    #    "large": [{"backpack": 10}],
    #    "medium": [{"cargo pants": 8}, {"satchel": 8}],
    #    "small": [{"pockets": 6}]
    #    }
    def pick_up_test(self, name:str):
        item = self.get_item(name) ## fails to find 'glass jar'
        try:
            if item["can_pick_up"]:
                return True
        except Exception as e:
            print(f"Exception in pick_up_test: {e}")
        return False


def set_choices():
    loot = LootTable(standard_loot, name="Standard")
    carrier_size = random.choice((list(carrier_options.keys())))
    carrier_dict = random.choice((carrier_options[carrier_size]))
    for k, v in carrier_dict.items():
        carrier, volume = k, v
    return loot, carrier, volume

loot, carrier, volume = set_choices()

def initialise_location_loot():
    loot=LootTable(location_loot, name="location_loot")
    return loot

loc_loot=initialise_location_loot()





#print(loot.describe("plastic bag", caps=True))
# → A used plastic bag from a grocery store. no holes, at least.

#print(loot.random_from("minor_loot"))
# → Randomly picks one of the minor_loot items
#randomloot = loot.random_from("minor_loot")
#print((loot.describe(randomloot)))
