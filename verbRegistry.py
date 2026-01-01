import uuid

from dataclasses import dataclass
from typing import Optional

@dataclass
class Token:
    text: str
    kind: str              # 'verb', 'noun', 'semantic', 'null'
    canonical: Optional[str] = None  # normalized form for verbs/semantics
# turning off canonical for the moment.

class Parser:
    def tokenize(self, text): ...
    def determine_format(self, tokens): ...
    def resolve_verb(self, tokens, format): ...


class VerbInstance:
    """
    Represents a single item in the game world or player inventory.
    """

    # "go to": {"alt_words":["go", "approach"], "null_words": None, "expected_parts":1, "format": f"[verb] [location]"}

    def __init__(self, verb_key:str, attr:dict):
        #print(f"Init in item instance is running now. {definition_key}")
        self.id = str(uuid.uuid4())  # unique per instance
        self.name = verb_key
        self.alt_words=attr["alt_words"]
        self.null_words = attr["allowed_null"]
        #self.expected_parts = attr.get("expected_parts")  # switching over to make this the 'discovered at' attr.
        self.format = attr.get("format")
        self.distinction = attr.get("distinction") if attr.get("distinction") else None
        self.colour = None

#"set": {"alt_words": [""], "allowed_null": None, "format": [verb_noun_dir, verb_noun_sem_noun], "distinction": {"second_noun":"fire", "new_verb":"burn", "else_verb":"put"}}

class VerbRegistry:
    """
    Central manager for all item instances.
    Also keeps a location-indexed lookup for fast "what's here?" queries.
    """

    def __init__(self):
        #print(f"Init in lootregistry is running now.") ## it only seems to be running once.
        #sleep(1)

        self.verbs = {}      # id -> VerbInstance
        self.by_name = {}        # verb_key -> verb
        self.by_format = {}        # format -> set of verbs
        self.by_alt_words = {}
        self.list_null_words = set()
        self.all_verbs = set() ## just a list of all verbs inc alt names

    def create_verb_instance(self, verb_key:str, attr:dict)->VerbInstance:
        #logging_fn()

        inst = VerbInstance(verb_key, attr)#nicename, primary_category, is_container, can_pick_up, description, location, contained_in, item_size, container_data)
        self.name = verb_key
        #print(f"attr: {attr}")
        self.by_name.setdefault(verb_key, list()).append(inst)
        for alt_words in attr["alt_words"]:
            if alt_words:
                if self.by_alt_words.get(alt_words): ## does not work if alt words aren't exclusive.
                    print(f"Alt words {alt_words} already exists.")
                self.by_alt_words[alt_words] = inst
        for item in attr["formats"]:
            self.by_format.setdefault(item, list()).append(inst.name)

        return inst
    """
    def get_key_parts(self, input_str, inventory = None):
        # eg "go to graveyard"
        # "[verb] [location]"
        # Possibly, moving into a more point-and-click direction, if you could click the verb and/or the obj, then it would be a list of parts pre-made, not a string that needed pulling apart. not doing that here now, but would be an interesting direction. Like the old monkey island style.

        cleaned_parts = {}
        parts = input_str.split()
        #print(f"Parts: {parts}")
        #print(f"self.null_words: {self.list_null_words}")
        for i, part in enumerate(parts):
            if part in self.list_null_words:
                #print(f"part `{part}` is in list_null_words")
                cleaned_parts[i] = {"null":part}
            elif self.by_name.get(part):
                cleaned_parts[i] = {"verb":self.by_name[part]}
            elif self.by_alt_words.get(part):
                cleaned_parts[i] = {"verb":self.by_alt_words[part]}
            else:
                from item_management_2 import registry
                noun_options = registry.instances_by_name(part)
                if noun_options:
                    if inventory:
                        if part in inventory:
                            cleaned_parts[i] = list([x for x in inventory if x == part])[0] # not sure if this is right.
                    if not cleaned_parts.get(i):
                    ## use location/inventory here later instead of defaulting to first option. (So the string-sender can say 'I'm at {place}', and we refine using that datapoint, as the items_at_here does for iteminstances.)
                        cleaned_parts[i] = {"noun": noun_options[0]}
                else:
                    from env_data import dataset
                    loc_options = list(dataset.keys())
                    if part in loc_options:
                        cleaned_parts[i] = {"place": part}
                    elif f"a {part}" in loc_options:
                        cleaned_parts[i] = {"place": part}

                if not cleaned_parts.get(i):
                    cleaned_parts[i] = {"noun": part}

        print(f"Cleaned parts: {cleaned_parts}")
    """
    def get_key_parts(self, input_str, location = None,  inventory = None):

        parts = input_str.split()
        from env_data import dataset
        loc_options = list(dataset.keys())
        from verb_definitions import directions

        if location:
            place, facing = location
            from item_management_2 import registry
            item_instances = registry.instances_by_location(place, facing)
            from misc_utilities import get_inst_list_names
            item_names = get_inst_list_names(item_instances)

        if inventory:
            from misc_utilities import get_inst_list_names
            inventory = get_inst_list_names(inventory)
            print(f"inventory: {inventory}")

        tokens = []
        for i, word in enumerate(parts):
            kinds = set()
            text = None
            potential_match=False

            initial = self.list_null_words | set(directions) | set(loc_options)

            if word in initial or f"a {word}" in initial:
                if word in self.list_null_words:
                    kinds.add("null")
                    text = word
                    potential_match=True

                if word == "up" and i == 1: ## temporarily doing this for 'pick up x'
                    if parts[0] == "pick":
                        print("pick up")
                        kinds.add("null")
                        text = word
                else:
                    if word in directions:
                        kinds.add("direction")
                        text = word
                        potential_match=True

                    if word in loc_options or f"a {word}" in loc_options:
                        kinds.add("location")
                        text = word
                        potential_match=True

            else:
                if word in self.all_verbs:
                    word_name=None
                    print(f"Word: {word}")
                    if not self.by_name.get(word):
                        if self.by_alt_words.get(word):
                            word_name = self.by_alt_words[word]
                            word_name = word_name.name
                    kinds.add("verb")
                    if word_name == None:
                        word_name = word
                    text = word_name
                    potential_match=True

                #if word in self.all_adjectives: ## Would be good to implement this at some point, but for now we'll call them all leftovers 'nouns'
                #    kinds.add("adjective")
                #    resolved["verb"] = resolve_adjective(word)

                if inventory and word in inventory:
                    kinds.add("noun")
                    text = word
                    potential_match=True

                if location and word in item_names: ## so nouns only come from inventory (if inventory provided) and/or locational objects (if location provided). So 'red car' will only count 'car' as a token and omit 'red'.
                    kinds.add("noun")
                    text = word

                #if not value.get("noun"):
                #    kinds.add("noun")
                #    value["noun"] = word
                ## Does not account for two word items. Needs to.

            tokens.append(Token(word, kinds, text))
        print(f"Tokens: {tokens}")
        return tokens

        if not potential_match:
            print(f"No verb found in {input_str}.")

    def match_format(self, input_str:str):

        if not isinstance(input_str, str):
            print(f"match_format requires a string input, not {type(input_str)}")

        parts = input_str.split()
        print(f"Parts: {parts}")
        options = self.requires_noun
        result_by_name = self.by_name.get(parts[0])
        if result_by_name in options and len(result_by_name) == 1:
            print(f"Valid verb found from {input_str}: {result_by_name}, is full command.")
        elif result_by_name:
            print(f"Verb found from {input_str}, but needs additional information.")
        elif self.by_alt_words.get(parts[0]):
            result_by_name = self.by_alt_words.get(parts[0])
            print(f"Verb found by alt_name from {input_str}: {result_by_name.name}")
        else:
            print(f"No valid verb found from {input_str}.")
            print(f"Result by name: {result_by_name}")

        #if len(parts) == 1:
#
        #if len(parts) == 2:
    def determine_format(self, tokens):

        format_parts = []
        for token in tokens:
            if "verb" in token.kind:
                #print(f"Token: {token}")
                if isinstance(token.canonical, VerbInstance):
                    verb = token.canonical
                else:
                    verb = token
            if 'null' in token.kind:
                if len(token.kind)>1:
                    primary_type = (token.kind - {'null'})
                    if primary_type:
                        format_parts.append(primary_type.pop())
            else:
                for kinds in token.kind:
                    format_parts.append(kinds)
                #if primary_type:
                #    format_parts.append(primary_type.pop())
                #format_parts.append(token.kind.pop())
        print(f"Format parts: {format_parts}")
        print(f"Verb: {verb}")
        from verb_definitions import formats

        potential_formats = set()
        for item in formats.values():
            if tuple(format_parts) == item:
                potential_formats.add(item)

        return verb, potential_formats

    def find_by_format(self, verb, format_keys):


        for format_key in format_keys:
            print(f"Format key: {format_key}, type: {type(format_key)}")
            print(f"self.by_format: {self.by_format}")

            items = self.by_format.get(format_key)
            print(f"Items: {items}")
            print(f"verb: {verb}")
            #print("by alt words: ", self.by_alt_words.get(verb.text))
            if items and verb.canonical in items:
                #print(f"Verb in items: {verb}")
                verb_obj = self.by_name.get(verb.canonical)[0]
                if not verb_obj:
                    verb_obj = self.by_alt_words.get(verb.canonical)[0]
                print(f"verb_obj: {verb_obj}")
                print("verb_obj.name: ", verb_obj.name)
                return verb_obj

    def input_str_parser(self, input_str, location=None, inventory=None):
        tokens = self.get_key_parts(input_str, location, inventory)
        print(f"Tokens: {tokens}")
        verb, format_keys = self.determine_format(tokens)
        print(f"Tokens: {tokens}")
        confirmed_verb = self.find_by_format(verb, format_keys)

        print("At end: ")
        print(f"TOKENS: {tokens}")
        print(f"verb: {verb}")
        print(f"format keys: {format_keys}")
        print(f"confirmed verb: {confirmed_verb}")
        print(f"confirmed verb name: {confirmed_verb.name}")
    # -------------

verbs = VerbRegistry()
inventory = []


def initialise_registry():
    from verb_definitions import get_verb_defs, allowed_null
    verb_defs_dict, verb_set = get_verb_defs()
    verbs.all_verbs = verb_set
    verbs.list_null_words = allowed_null
    for item_name, attr in verb_defs_dict.items():
        verbs.create_verb_instance(item_name, attr)
        if attr.get("null_words"):
            for word in attr.get("null_words"):
                if word != None:
                    #print(f"Word in null words: {word}")
                    verbs.list_null_words.add(word)

#            verbs.list_null_words.add(i for i in attr["null_words"])
    #repr(verbs)

initialise_registry()
#print("verbs: ")
#print(verbs.by_name)
#print("verbs by alt_words:")
#print(verbs.by_alt_words)

#print("go to the museum")

#verbs.match_format("go to the museum")

verbs.input_str_parser("go to the graveyard")
from set_up_game import game, set_up ## might break
set_up(weirdness=True, bad_language=True, player_name="Testing")
verbs.input_str_parser("pick up the paperclip", inventory=game.inventory)
