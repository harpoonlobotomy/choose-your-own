

#null = "[null]"
#verb = "[verb]"
#location = "[location]"
#noun = "[noun]"


meta_verbs = {
    "inventory": {"alt_words": ["i"]},
    "help": {"alt_words": ""},
    "settings": {"alt_words": ""},
    "stats": {"alt_words": ""},
    "describe": {"alt_words": ["d"]},
    "godmode": {"alt_words": ["god"]}, # remove this if there's ever a god...?
    "quit": {"alt_words": ["q"]},
    "show visted": {"alt_words": ""},
    "update_json": {"alt_words": ["update"]},
    "meta": {"alt_words": ["edit"]}
}


null = "null"
verb = "verb"
location = "location"
noun = "noun"
sem = "sem" # semantic operator (with, to, from etc)
direction = "direction"
car = "cardinal"
meta = "meta"

# o[type] == 'optional {type}'

#formats = {
#    "verb_only": f"{verb}",
#    "verb_noun": f"{verb} o{null} {noun}",
#    "verb_loc": f"{verb} o{null} {location}",
#    "verb_noun_noun": f"{verb} o{null} {noun} {null} o{null} {noun}"
#}
cardinals = ["north", "east", "south", "west"]
directions = ["down", "up", "left", "right", "away", "toward", "towards", "closer", "further", "to", "into", "against", "across", "at", "in", "on", "from", "inside", "outside", "away", "into", "elsewhere", "here", "through"]
## "in front of"?? Need to be able to cope with that.

nulls = ["the", "a", "an"]
semantics = ["with", "and", "around", "for", "while", "set", "on"]

null_sem_combinations = ["a while"]

positional_dict = {
    "in": {"alts": ["inside", "within"]},
    "on": {"alts": ["atop", "onto"]},
    "against": {"alts": ["leant", "lean"]}
    }

formats = {
    ### META ###
    "meta": (meta), #inventory
    "verb_meta": (verb, meta), #open inventory
    "meta_noun": (meta, noun), #for literally like 'meta key', which I can then use to edit key entry etc. Just a signpost
    "meta_loc": (meta, location),
    "meta_car": (meta, car),
    "verb_dir_meta": (verb, direction, meta), #open up inventory
    "verb_noun_dir_meta": (verb, noun, direction, meta), # remove item from inventory == drop item

    ### CARDINAL ###
    "car": (car,), # (go) west, assume verb 'go'
    "verb_car": (verb, car), # go west
    "verb_dir_car": (verb, direction, car), # go to the west
    "verb_dir_car_loc": (verb, direction, car, location), # go to east graveyard
    "verb_dir_loc_car": (verb, direction, location, car), # go to graveyard east

    ### LOCATION ONLY ###
    "verb_only": (verb,), #'leave'
    "loc": (location,), #location only, assume verb 'go'.
    "loc_car": (location, car), # # 'graveyard east'
    "car_loc": (car, location), # # 'east graveyard'
    "verb_car_loc": (verb, car, location),
    "verb_loc_car": (verb, location, car),
    "dir": (direction,), #direction only, assume verb 'go'.
    "verb_sem": (verb, sem),
    "verb_dir": (verb, direction), #go up, go outside
    "verb_sem": (verb, sem), # 'look around'
    "verb_loc": (verb, location), # go graveyard
    "verb_dir_loc": (verb, direction, location), # go to graveyard

    ### SINGLE NOUNS ###
    "verb_noun": (verb, noun), # drop paperclip
    "verb_sem_noun": (verb, sem, noun), # 'look at watch'
    "verb_dir_noun": (verb, direction, noun), # 'look at watch'
    "verb_noun_sem": (verb, noun, sem), # 'read book a while
    "verb_noun_dir": (verb, noun, direction), # throw ball up
    "verb_noun_dir_loc": (verb, noun, direction, location), # drop paperclip at graveyard

    ### TWO NOUNS ###
    "verb_noun_noun": (verb, noun, noun), # can't think of any examples.
    "verb_noun_dir_noun": (verb, noun, direction, noun), # push chest towards door, put paperclip in jar
    "verb_noun_sem_sem": (verb, noun, sem, sem), # "read mag for a while" (Don't know why 'for' is directional, surely it should be semantic.)
    #"verb_noun_dir_sem": (verb, noun, direction, sem), # have changed 'for' to be semantic instead of directional, for now. Will see how much it breaks things.
    "verb_noun_dir_dir_noun": (verb, noun, direction, direction, noun), # put paperclip down on table
    "verb_noun_dir_noun_dir_loc": (verb, noun, direction, noun, direction, location), # put paperclip in glass jar in graveyard # pointless, but included just in case.
    "verb_noun_sem_noun": (verb, noun, sem, noun), # mix water with potion
    "verb_dir_noun_sem_noun": (verb, direction, noun, sem, noun), #go to table with box

    "sem_noun_verb": (sem, noun, verb), # 'set magazine alight
    "sem_noun_dir_verb": (sem, noun, direction, verb) # set magazine on fire
    ## NOTE: Will likely break at several points in the parser, as they expect 'verb' to always be first. Also may break because 'set' is a verb, too.

}
"""
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
"""

loc_only = formats["loc"]
loc_car = formats["loc_car"] # graveyard east
car_loc = formats["car_loc"] # east graveyard
dir_only = formats["dir"]
car_only = formats["car"]
### 'sem' == semantic operators, eg 'with' in 'combine x with y'.
meta = formats["meta"]
meta_noun = formats["meta_noun"]
meta_loc = formats["meta_loc"]
meta_car = formats["meta_car"]
verb_meta = formats["verb_meta"]
verb_dir_meta = formats["verb_dir_meta"]
verb_noun_dir_meta = formats["verb_noun_dir_meta"]

verb_only = formats["verb_only"]
verb_noun = formats["verb_noun"]
verb_loc = formats["verb_loc"]
verb_dir = formats["verb_dir"]
verb_car = formats["verb_car"]
verb_sem = formats["verb_sem"] # 'turn around'

verb_car_loc = formats["verb_car_loc"]
verb_loc_car = formats["verb_loc_car"]
verb_dir_car = formats["verb_dir_car"]
verb_dir_car_loc = formats["verb_dir_car_loc"]
verb_dir_loc_car = formats["verb_dir_loc_car"]
verb_dir_loc = formats["verb_dir_loc"]
verb_dir_noun = formats["verb_dir_noun"]
verb_sem_noun = formats["verb_sem_noun"] # wait with book
verb_noun_sem = formats["verb_noun_sem"] # read book a while
verb_noun_dir = formats["verb_noun_dir"] # [enter] [work shed] [door]

verb_noun_noun = formats["verb_noun_noun"]
verb_noun_dir_noun = formats["verb_noun_dir_noun"]
verb_noun_dir_dir_noun = formats["verb_noun_dir_dir_noun"]
verb_noun_dir_noun_dir_loc = formats["verb_noun_dir_noun_dir_loc"]
verb_noun_dir_loc = formats["verb_noun_dir_loc"]
#verb_noun_dir_sem = formats["verb_noun_dir_sem"]
verb_noun_sem_sem = formats["verb_noun_sem_sem"]
verb_noun_sem_noun = formats["verb_noun_sem_noun"]
verb_dir_noun_sem_noun = formats["verb_dir_noun_sem_noun"]

sem_noun_verb = formats["sem_noun_verb"]
sem_noun_dir_verb = formats["sem_noun_dir_verb"]

## Note: Need to figure out how I'm getting noun-objects in here. Like, 'magnifying glass' is 1 noun, but two words. Need to figure that out.

allowed_null = set(('the', 'a', 'an', 'out', 'of')) ## removed strictly directional words from null, as null is used differently now.
#allowed_null = set(('and', 'with', 'to', 'the', 'at', 'plus', 'a', 'an', 'from', 'out', 'of', 'on')) ### Note: There may be more than one viable semantic when only one is required. That's fine.

combined_wordphrases = { # maybe something like this, instead of the hardcoded exceptions.
    "up" : ["pick"], # reversed the directions
    "open" : ["pry", "break"], ## a way to apply the key verb-name then check against that instead? Instead of listing all variations of a key phrase here.
    "from" : ["away"],
    "on": ["down"],
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
    f"attributes": {"alt_words": ["att"], "allowed_null": None, "formats": [verb_noun]},
    ## NOTE: Allowed_null is not used at present. All nulls are treated as equal, and all sem/loc/dirs are treated as viable in all cases. Will need to change this later but for now it works alright.
    "meta": {"alt_words": [], "allowed_null": None, "formats": [meta, meta_noun, meta_loc, meta_car]},
    "go": {"alt_words":["go to", "approach", "head", "travel"], "allowed_null": None, "formats": [loc_only, loc_car, car_loc, verb_car_loc, verb_loc_car, dir_only, car_only, verb_only, verb_loc, verb_dir, verb_dir_loc, verb_dir_noun, verb_car, verb_dir_car, verb_dir_car_loc, verb_dir_loc_car, verb_noun_noun]},
#   ,making 'move' its own verb because it needs to route to both 'push' and 'go'. # Turns out I already had one but used it terribly and still had alt_words directing actions away. So now it's here.
    "move": {"alt_words": ["shift"], "allowed_null": None, "formats": [verb_noun, verb_noun_dir, verb_noun_dir_noun, loc_only, loc_car, car_loc, verb_car_loc, verb_loc_car, dir_only, car_only, verb_only, verb_loc, verb_dir, verb_dir_loc, verb_car, verb_dir_car, verb_dir_car_loc, verb_dir_loc_car]},
    "turn": {"alt_words": [""], "allowed_null": None, "formats": [verb_car, verb_sem, verb_dir, verb_dir_car, verb_dir_car_loc]},
    "leave": {"alt_words": ["depart", ""], "allowed_null": None, "formats": [verb_only, verb_loc, verb_noun, verb_dir_loc, verb_noun_dir, verb_noun_dir_noun, verb_dir_noun, verb_noun_noun]},
    "combine": {"alt_words": ["mix", "add"], "allowed_null": ["with", "and"], "formats": [verb_noun_sem_noun, verb_noun_dir_noun, verb_noun]},
    "separate": {"alt_words": ["remove", ""], "allowed_null": ["from", "and"], "formats": [verb_noun_sem_noun, verb_noun_dir_noun, verb_noun]},
    "throw": {"alt_words": ["chuck", "lob"], "allowed_null": ["at"], "formats": [verb_noun, verb_noun_dir, verb_noun_sem_noun, verb_noun_dir_noun, verb_noun_dir_loc]}, # throw ball down, throw ball at tree
    "push": {"alt_words": ["shove", "pull"], "allowed_null": None, "formats": [verb_noun, verb_noun_dir, verb_noun_dir_noun, verb_noun_noun]},
    "drop": {"alt_words": ["discard", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_dir, verb_noun_dir_noun, verb_noun_dir_loc, verb_noun_dir_noun_dir_loc, verb_noun_dir_meta]},
    "read": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_dir_loc, verb_noun_sem_sem, verb_noun_sem]},
    "use": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun, verb_noun_dir_loc, verb_noun_dir_noun, verb_noun_noun]},
    "burn": {"alt_words": ["fire", "alight", "light"], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun, verb_noun_dir_loc, sem_noun_dir_verb, sem_noun_verb], "inventory_check": "fire_source"},
    "lock": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun, verb_noun_noun], "inventory_check": "key"},
    "unlock": {"alt_words": ["", ""], "allowed_null": None, "formats": [verb_noun_sem_noun, verb_noun, verb_noun_noun], "inventory_check": "key"},
    "open": {"alt_words": ["pry", ""], "allowed_null": None, "formats": [verb_noun, verb_meta, verb_dir_meta, verb_noun_sem_noun, verb_dir_meta, verb_noun_noun, verb_noun_dir_loc]},
    "barricade": {"alt_words": [""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun, verb_noun_noun, verb_noun_dir_loc]},
    "close": {"alt_words": [""], "allowed_null": None, "formats": [verb_noun, verb_meta, verb_dir_meta, verb_noun_sem_noun, verb_noun_noun, verb_noun_dir_loc]},
    "break": {"alt_words": ["smash", ""], "allowed_null": None, "formats": [verb_noun, verb_noun_sem_noun]},
    "take": {"alt_words": ["pick up", "get", "pick"], "allowed_null": None, "formats": [verb_noun, verb_dir_noun, verb_noun_sem_noun, verb_noun_dir_noun, verb_noun_dir_noun_dir_loc, verb_noun_dir_loc]}, # take ball, take ball from bag
    "put": {"alt_words": ["place"], "allowed_null": ["in", "inside"], "formats": [verb_noun_dir, verb_noun_dir_meta, verb_noun_sem_noun, verb_noun_dir_noun, verb_noun_dir_noun_dir_loc, verb_noun_dir_loc]}, # put paper down, put paper on table ## using 'leave' here might be tricky. But I want to allow for 'leave church' and 'leave pamphlet on table' both.
    "eat": {"alt_words": ["consume", "drink"], "allowed_null": None, "formats": [verb_noun]},
    "look": {"alt_words": ["watch", "observe", "investigate", "examine"], "allowed_null": ["at", "to"],  "formats": [verb_only, verb_noun, verb_dir, verb_sem, verb_loc, verb_dir_meta, verb_noun_sem_noun, verb_noun_dir_noun, verb_dir_noun, verb_dir_noun_sem_noun, verb_car, verb_dir_car, verb_dir_car_loc, verb_dir_loc_car, verb_dir_loc, verb_sem_noun]}, # look, look at book, look at book with magnifying glass
    "set": {"alt_words": [""], "allowed_null": None, "formats": [verb_noun_dir, verb_noun_sem_noun, verb_noun], "distinction": {"second_noun":"fire", "new_verb":"burn", "else_verb":"put"}}, ## not implemented, just an idea. 'if fire is the second noun, the correct verb to use is 'burn', else the verb is 'put'. So 'set' is not its own thing, just a membrane/signpost.
    "clean": {"alt_words": ["wipe"], "allowed_null": None, "formats": [verb_noun, verb_loc, verb_noun_sem_noun]},
    "enter": {"alt_words": [], "allowed_null": None, "formats": [verb_loc, verb_dir_loc, verb_noun, verb_dir_noun, verb_noun_noun]},
    "time": {"alt_words": ["wait", "waste time", "spend time"], "allowed_null": None, "formats": [verb_only, verb_dir, verb_sem_noun, verb_noun_sem_sem]},
    "find": {"alt_words": ["search"], "allowed_null": None, "formats": [verb_noun, verb_noun_dir_loc, verb_loc, verb_sem_noun]}
    }


## also, how to deal with something like 'set paper on fire'
# Need a clean way to deal with multi-component things like this. Say, 'set', could be 'set paper on table', or 'set paper on fire'. So maybe
# 'if set, if input[noun2] == "fire", verb = burn. else, verb = place

def get_verb_defs(verb_name=None):

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

        return verb_defs_dict, verb_set
