#verb_definitions.py


from item_management_2 import ItemInstance
#from verbRegistry import VerbInstance

verb_defs_dict = {
    "go to": {"alt_words":["go", "approach"], "null_words": ["to"], "expected_parts":1, "format": f"[verb] [location]", "requires_noun": True},
    "leave": {"alt_words": ["depart", ""], "null_words": ["the"], "expected_parts":1, "format": f"[verb] [location]", "requires_noun": False},
    "combine": {"alt_words": ["mix", "add"], "null_words": ["and", "with", "plus", "the", "a"], "expected_parts": 2, "format": f"[verb] [null] {type(ItemInstance)} [null] {type(ItemInstance)}", "requires_noun": True},
    "drop": {"alt_words": ["", ""], "null_words": ["the", "a"], "expected_parts": 1, "format": f"[verb] {type(ItemInstance)}", "requires_noun": True},
    "eat": {"alt_words": ["consume", ""], "null_words": ["the", "a"], "expected_parts": 1, "format": f"[verb] {type(ItemInstance)}", "requires_noun": True},
    "look": {"alt_words": ["watch", "observe"], "null_words": ["at"], "expected_parts": 1, "format": f"[verb] {type(ItemInstance)}", "requires_noun": False}
    }


def get_verb_defs(verb_name=None):
    #print("\n" * 10)
    if verb_name:
        attr=verb_defs_dict.get(verb_name)
        return attr
    else:
        #for verb, attr in verb_defs_dict.items():
        #    #print(f"verb: {verb}, attr: {attr}")
        #    verb_data = verb_defs_dict[verb]
        return verb_defs_dict
