#verb_definitions.py


from item_management_2 import ItemInstance
#from verbRegistry import VerbInstance

#null = "[null]"
#verb = "[verb]"
#location = "[location]"
#noun = "[noun]"

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
directions = ["down", "up", "left", "right", "away", "toward", "towards", "closer", "further", "to", "against", "across", "at", "in"]

semantics = ["with"]
directions = directions + cardinals


formats = {
    "verb_only": (verb),
    "verb_noun": (verb, noun),
    "verb_loc": (verb, location),
    "verb_dir_loc": (verb, direction, location), # go to graveyard
    "verb_sem_loc": (verb, sem, location), # throw ball up
    "verb_noun_noun": (verb, noun, noun), # can't think of any examples.
    "verb_dir_noun": (verb, direction, noun), # 'look at watch'
    "verb_noun_dir": (verb, noun, direction), # throw ball up
    "verb_noun_dir_noun": (verb, noun, direction, noun), # push chest towards door
    "verb_noun_sem_noun": (verb, noun, sem, noun),
    "verb_dir_noun_sem_noun": (verb, direction, noun, sem, noun)
}

### 'sem' == semantic operators, eg 'with' in 'combine x with y'.
verb_only = formats["verb_only"]
verb_noun = formats["verb_noun"]
verb_loc = formats["verb_loc"]
verb_noun_noun = formats["verb_noun_noun"]
verb_dir_loc = formats["verb_dir_loc"]
verb_sem_loc = formats["verb_sem_loc"]
verb_dir_noun = formats["verb_dir_noun"]
verb_noun_dir = formats["verb_noun_dir"]
verb_noun_dir_noun = formats["verb_noun_dir_noun"]
verb_noun_sem_noun = formats["verb_noun_sem_noun"]
verb_dir_noun_sem_noun = formats["verb_dir_noun_sem_noun"]

## Note: Need to figure out how I'm getting noun-objects in here. Like, 'magnifying glass' is 1 noun, but two words. Need to figure that out.

allowed_null = set(('and', 'with', 'to', 'the', 'at', 'plus', 'a', 'an', 'from', 'out', 'of', 'on', 'against')) ### Note: There may be more than one viable semantic when only one is required. That's fine.
# So if it expects 'verb noun sem noun'
# and the input is
# take flowers from in the vase
# while technically that's three viable semantics (and two that would be viable for 'vase'),
# it meets the requirement of 'one' - exceeding is not exclusion for semantics.


# "from" (eg 'remove flowers from the vase')
# "inside" eg ("look inside the book" == "look at book")
# if no 'allowed_null', all null = allowed.

verb_defs_dict = {
    "go": {"alt_words":["go to", "approach"], "allowed_null": None, "formats": [verb_loc, verb_dir_loc]},
    "leave": {"alt_words": ["depart", ""], "allowed_null": None, "formats": [verb_only, verb_loc]},
    "combine": {"alt_words": ["mix", "add"], "allowed_null": None, "formats": [verb_noun_sem_noun]},
    "separate": {"alt_words": ["remove", "get"], "allowed_null": None, "formats": [verb_noun_sem_noun]},
    "throw": {"alt_words": ["chuck", "lob"], "allowed_null": None, "formats": [verb_noun, verb_noun_dir, verb_noun_sem_noun]}, # throw ball down, throw ball at tree
    "push": {"alt_words": ["shove", "move", "pull"], "allowed_null": None, "formats": [verb_noun, verb_noun_dir, verb_noun_dir_noun]},
    "drop": {"alt_words": ["discard", ""], "allowed_null": None, "formats": [verb_noun]},
    "open": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun]},
    "read": {"alt_words": ["examine", ""], "allowed_null": None, "formats": [verb_noun]}, ## Two nouns have 'examine'. Maybe make 'read' its own specific thing instead of referring 'examine' here. idk.
    "burn": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun], "inventory_check": "fire_source"},
    "lock": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun], "inventory_check": "key"},
    "unlock": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun_sem_noun], "inventory_check": "key"},
    "open": {"alt_words": ["pry", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun]},
    "break": {"alt_words": ["smash", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun]},
    "take": {"alt_words": ["pick up", "get", "pick"], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun]}, # take ball, take ball from bag
    "put": {"alt_words": ["place", "leave"], "allowed_null": ["on", "in", "inside"], "formats": [verb_noun_dir, verb_noun_sem_noun, verb_noun_dir_noun]}, # put paper down, put paper on table ## using 'leave' here might be tricky. But I want to allow for 'leave church' and 'leave pamphlet on table' both.
    "eat": {"alt_words": ["consume", "drink"], "allowed_null": None, "formats": [verb_noun]},
    "look": {"alt_words": ["watch", "observe", "investigate", "examine"], "allowed_null": ["at", "to", "with"],  "formats": [verb_only, verb_noun, verb_noun_sem_noun, verb_noun_dir_noun, verb_dir_noun, verb_dir_noun_sem_noun]}, # look, look at book, look at book with magnifying glass
    "set": {"alt_words": [""], "allowed_null": None, "formats": [verb_noun_dir, verb_noun_sem_noun], "distinction": {"second_noun":"fire", "new_verb":"burn", "else_verb":"put"}} ## not implemented, just an idea. 'if fire is the second noun, the correct verb to use is 'burn', else the verb is 'put'. So 'set' is not its own thing, just a membrane/signpost.
    }

### how to deal with two-part 'word phrases' (eg 'pick up')? Initial thought, just use the first word and check the second (so 'pick up the book', 'pick' is the verb, and we check it's 'pick up' once 'pick' is identified to make sure it's right. Though that might not even be necessary, 'pick' isn't exactly its own separate verb)
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
        return attr
    else:
        for verb, attr in verb_defs_dict.items():
            verb_set.add(verb)
            for alt_name in attr["alt_words"]:
                if alt_name:
                    verb_set.add(alt_name)
        #    #print(f"verb: {verb}, attr: {attr}")
        #    verb_data = verb_defs_dict[verb]

        return verb_defs_dict, verb_set ## Just a strait up set of all the verbs, nothing else.
