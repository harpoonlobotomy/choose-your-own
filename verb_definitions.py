

#null = "[null]"
#verb = "[verb]"
#location = "[location]"
#noun = "[noun]"


meta_verbs = { ## Added to work with specific user inputs. Not sure how to implement it yet, but will figure it out. Just a placeholder for now.
    "inventory": {"alt_words": ""},
    "help": {"alt_words": ""},
    "settings": {"alt_words": ""},
    "stats": {"alt_words": ""},
    "godmode": {"alt_words": ""},
    "quit": {"alt_words": ""}
}


null = "null"
verb = "verb"
location = "location"
noun = "noun"
sem = "sem" # semantic operator (with, to, from etc)
direction = "direction"

# o[type] == 'optional {type}'

#formats = {
#    "verb_only": f"{verb}",
#    "verb_noun": f"{verb} o{null} {noun}",
#    "verb_loc": f"{verb} o{null} {location}",
#    "verb_noun_noun": f"{verb} o{null} {noun} {null} o{null} {noun}"
#}
cardinals = ["north", "east", "south", "west"]
directions = ["down", "up", "left", "right", "away", "toward", "towards", "closer", "further", "to", "against", "across", "at", "in", "on", "from", "inside", "away", "into"]
## "in front of"?? Need to be able to cope with that.

nulls = ["the", "a", "an"]
semantics = ["with", "and"]
directions = directions + cardinals

positional_dict = {
    "in": {"alts": ["inside", "within"]},
    "on": {"alts": ["atop", "onto"]},
    "against": {"alts": ["leant", "leaning on"]}
    }


formats = {
    "verb_only": (verb,), #'leave'
    "verb_noun": (verb, noun), # drop paperclip
    "verb_loc": (verb, location), # go graveyard
    "verb_dir": (verb, direction), # go graveyard
    "verb_dir_loc": (verb, direction, location), # go to graveyard
    "verb_noun_noun": (verb, noun, noun), # can't think of any examples.
    "verb_dir_noun": (verb, direction, noun), # 'look at watch'
    "verb_noun_dir": (verb, noun, direction), # throw ball up
    "verb_noun_dir_noun": (verb, noun, direction, noun), # push chest towards door, put paperclip in jar
    "verb_noun_dir_dir_noun": (verb, noun, direction, direction, noun), # put paperclip down on table
    "verb_noun_dir_noun_dir_loc": (verb, noun, direction, noun, direction, location), # put paperclip in glass jar in graveyard # pointless, but included just in case.
    "verb_noun_dir_loc": (verb, noun, direction, location), # drop paperclip at graveyard #only works if you're in the graveyard, identical in function to 'drop paperclip' while at graveyard.
    "verb_noun_sem_noun": (verb, noun, sem, noun),
    "verb_dir_noun_sem_noun": (verb, direction, noun, sem, noun)
}

### 'sem' == semantic operators, eg 'with' in 'combine x with y'.
verb_only = formats["verb_only"]
verb_noun = formats["verb_noun"]
verb_loc = formats["verb_loc"]
verb_dir = formats["verb_dir"]
verb_noun_noun = formats["verb_noun_noun"]
verb_dir_loc = formats["verb_dir_loc"]
verb_dir_noun = formats["verb_dir_noun"]
verb_noun_dir = formats["verb_noun_dir"]
verb_noun_dir_noun = formats["verb_noun_dir_noun"]
verb_noun_dir_dir_noun = formats["verb_noun_dir_dir_noun"]
verb_noun_dir_noun_dir_loc = formats["verb_noun_dir_noun_dir_loc"]
verb_noun_dir_loc = formats["verb_noun_dir_loc"]
verb_noun_sem_noun = formats["verb_noun_sem_noun"]
verb_dir_noun_sem_noun = formats["verb_dir_noun_sem_noun"]

## Note: Need to figure out how I'm getting noun-objects in here. Like, 'magnifying glass' is 1 noun, but two words. Need to figure that out.

allowed_null = set(('the', 'a', 'an', 'out', 'of')) ## removed strictly directional words from null, as null is used differently now.
#allowed_null = set(('and', 'with', 'to', 'the', 'at', 'plus', 'a', 'an', 'from', 'out', 'of', 'on')) ### Note: There may be more than one viable semantic when only one is required. That's fine.

combined_wordphrases = { # maybe something like this, instead of the hardcoded exceptions.
    "up" : ["pick"], # reversed the directions
    "open" : ["pry", "break"], ## a way to apply the key verb-name then check against that instead? Instead of listing all variations of a key phrase here.
    "from" : ["away"],
    "on": ["down"]
}
#What about something like 'away from', eg 'move papers away from fire'. Need a mechanism to check #if 'away', is next part 'fire', and treat 'away from' as its own direction.
# I know it's sprawling but it'll keep things viable without having to add a hundred options for each /noun/ if they're added at the verb le

# So if it expects 'verb noun sem noun'
# and the input is
# take flowers from in the vase
# while technically that's three viable semantics (and two that would be viable for 'vase'),
# it meets the requirement of 'one' - exceeding is not exclusion for semantics.

# "from" (eg 'remove flowers from the vase')
# "inside" eg ("look inside the book" == "look at book")
# if no 'allowed_null', all null = allowed.

verb_defs_dict = {
    ## NOTE: Allowed_null is not used at present. All nulls are treated as equal, and all sem/loc/dirs are treated as viable in all cases. Will need to change this later but for now it works alright.
    "go": {"alt_words":["go to", "approach"], "allowed_null": None, "formats": [verb_only, verb_loc, verb_dir, verb_dir_loc]},
    "leave": {"alt_words": ["depart", ""], "allowed_null": None, "formats": [verb_only, verb_loc, verb_noun_dir_noun]},
    "combine": {"alt_words": ["mix", "add"], "allowed_null": ["with", "and"], "formats": [verb_noun_sem_noun, verb_noun_dir_noun, verb_noun]},
    "separate": {"alt_words": ["remove", ""], "allowed_null": ["from", "and"], "formats": [verb_noun_sem_noun, verb_noun_dir_noun, verb_noun]},
    "throw": {"alt_words": ["chuck", "lob"], "allowed_null": ["at"], "formats": [verb_noun, verb_noun_dir, verb_noun_sem_noun, verb_noun_dir_noun, verb_noun_dir_loc]}, # throw ball down, throw ball at tree
    "push": {"alt_words": ["shove", "move", "pull"], "allowed_null": None, "formats": [verb_noun, verb_noun_dir, verb_noun_dir_noun]},
    "drop": {"alt_words": ["discard", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_dir_noun, verb_noun_dir_loc, verb_noun_dir_noun_dir_loc]},
    "read": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_dir_loc]}, ## Two nouns have 'examine'. Maybe make 'read' its own specific thing instead of referring 'examine' here. idk.
    "burn": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun, verb_noun_dir_loc], "inventory_check": "fire_source"},
    "lock": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun], "inventory_check": "key"},
    "unlock": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun_sem_noun, verb_noun], "inventory_check": "key"},
    "open": {"alt_words": ["pry", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun]},
    "close": {"alt_words": ["barricade", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun]},
    "break": {"alt_words": ["smash", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun]},
    "take": {"alt_words": ["pick up", "get", "pick"], "allowed_null": None, "formats": [verb_noun, verb_dir_noun, verb_noun_sem_noun, verb_noun_dir_noun, verb_noun_dir_noun_dir_loc]}, # take ball, take ball from bag
    "put": {"alt_words": ["place", "leave"], "allowed_null": ["in", "inside"], "formats": [verb_noun_dir, verb_noun_sem_noun, verb_noun_dir_noun, verb_noun_dir_noun_dir_loc]}, # put paper down, put paper on table ## using 'leave' here might be tricky. But I want to allow for 'leave church' and 'leave pamphlet on table' both.
    "eat": {"alt_words": ["consume", "drink"], "allowed_null": None, "formats": [verb_noun]},
    "look": {"alt_words": ["watch", "observe", "investigate", "examine"], "allowed_null": ["at", "to"],  "formats": [verb_only, verb_noun, verb_dir, verb_loc, verb_noun_sem_noun, verb_noun_dir_noun, verb_dir_noun, verb_dir_noun_sem_noun]}, # look, look at book, look at book with magnifying glass
    "set": {"alt_words": [""], "allowed_null": None, "formats": [verb_noun_dir, verb_noun_sem_noun, verb_noun], "distinction": {"second_noun":"fire", "new_verb":"burn", "else_verb":"put"}}, ## not implemented, just an idea. 'if fire is the second noun, the correct verb to use is 'burn', else the verb is 'put'. So 'set' is not its own thing, just a membrane/signpost.
    "move": {"alt_words": ["shift"], "allowed_null": None, "formats": [verb_noun, verb_noun_dir, verb_noun_dir_noun]},
    "clean": {"alt_words": ["wipe"], "allowed_null": None, "formats": [verb_noun, verb_loc, verb_noun_sem_noun]}
    }

## also, how to deal with something like 'set paper on fire'
# Need a clean way to deal with multi-component things like this. Say, 'set', could be 'set paper on table', or 'set paper on fire'. So maybe
# 'if set, if input[noun2] == "fire", verb = burn. else, verb = place

#verb_defs_dict = {
#    "go to": {"alt_words":["go", "approach"], "null_words": ["to"], "formats": [verb_only, verb_noun]},
#    "leave": {"alt_words": ["depart", ""], "null_words": ["the"], "formats": [verb_noun]},
#    "combine": {"alt_words": ["mix", "add"], "null_words": ["and", "with", "plus", "the", "a"], "expected_parts": 2, "formats": f"[verb] [null] {type#(ItemInstance)} [null] {type(ItemInstance)}", "requires_noun": True},
#    "drop": {"alt_words": ["", ""], "null_words": ["the", "a"], "expected_parts": 1, "formats": f"[verb] {type(ItemInstance)}", "requires_noun": True},
#    "eat": {"alt_words": ["consume", ""], "null_words": ["the", "a"], "expected_parts": 1, "formats": f"[verb] {type(ItemInstance)}", "requires_noun": True},
#    "look": {"alt_words": ["watch", "observe"], "null_words": ["at"], "expected_parts": 1, "formats": f"[verb] {type(ItemInstance)}", "requires_noun": False}
#    }


def get_verb_defs(verb_name=None):
    #print("\n" * 10)
    verb_set=set()
    if verb_name:
        attr=verb_defs_dict.get(verb_name)
        return attr, None
    else:
        for verb, attr in verb_defs_dict.items():
            verb_set.add(verb)
            for alt_name in attr["alt_words"]:
                if alt_name:
                    verb_set.add(alt_name)

        return verb_defs_dict, verb_set ## Just a strait up set of all the verbs, nothing else.
