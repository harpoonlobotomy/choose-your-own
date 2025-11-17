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
    "category": {"item": {"name": "name to use in inventory", "description": "the description to use in inventory 'details'."},
                 "next_item": {}}
    }

currency = random.choice(("dollar", "pound", "yen")) # build it here instead

standard_loot = {
    "guaranteed": {"paperclip": {"name": "a paperclip", "description": "a humble paperclip."}},
    "mags": {"puzzle mag": {"name": "a puzzle magazine", "description": ""},
            "fashion mag": {"name": "a fashion magazine", "description": ""},
            "gardening mag": {"name": "a gardening magazine", "description": ""},
            "mail order catalogue": {"name": "a mail order catalogue", "description": ""}
            },
    "starting": {"car keys": {"name": "a set of car keys", "description": ""},
                 "fish food": {"name": "a jar of fish food", "description": ""},
                 "anxiety meds": {"name": "a bottle of anxiety meds", "description": ""},
                 "regional map": {"name": "a regional map", "description": ""},
                 "unlabelled cream": {"name": "an unlabelled cream", "description": ""},
                 "batteries": {"name": "a set of batteries", "description": ""}
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
    "special_loot": {"the exact thing": {"name": "the exact thing you've been needing", "description": "It's the exact thing you need for the thing you need it for. But only once."}}
    }

time_of_day = ("early morning", "morning", "midday", "evening", "middle of the night")

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

    def get_full_category(self, selection):
        category = selection
        items = list(self.by_category.get(category, {}).keys())
        return items

    def get_item(self, name: str):
        """Retrieve an item by name, or None if not found."""
        return self.by_name.get(name)

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
        if not item:
            return f"No such item: {name}"
        if caps:
            cap_desc = smart_capitalise(item['description'])
        else:
            cap_desc = item['description']
        return f"{cap_desc}"#{name} ({item['category']}): {item['description']}"

    def nicename(self, name: str):
        item = self.get_item(name)
        if not item:
            print("No such item.")
            return None
        return item['name']
    ## carrier ##
    #carrier_options = {
    #    "large": [{"backpack": 10}],
    #    "medium": [{"cargo pants": 8}, {"satchel": 8}],
    #    "small": [{"pockets": 6}]
    #    }


def set_choices():
    loot = LootTable(standard_loot, name="Standard")
    carrier_size = random.choice((list(carrier_options.keys())))
    carrier_dict = random.choice((carrier_options[carrier_size]))
    for k, v in carrier_dict.items():
        carrier, volume = k, v
    return loot, carrier, volume

loot, carrier, volume = set_choices()





#print(loot.describe("plastic bag", caps=True))
# → A used plastic bag from a grocery store. no holes, at least.

#print(loot.random_from("minor_loot"))
# → Randomly picks one of the minor_loot items
#randomloot = loot.random_from("minor_loot")
#print((loot.describe(randomloot)))
