import uuid

from dataclasses import dataclass
from typing import Optional

@dataclass
class Token:
    idx: int
    text: str
    kind: str              # 'verb', 'noun', 'semantic', 'null'
    canonical: Optional[str] = None  # normalized form for verbs/semantics
# turning off canonical for the moment.


class VerbInstance:
    """
    Represents a single item in the game world or player inventory.
    """

    # "go to": {"alt_words":["go", "approach"], "null_words": None, "expected_parts":1, "format": f"[verb] [location]"}

    def __init__(self, verb_key:str, attr:dict):
        #print(f"Init in item instance is running now. {definition_key}")
        self.id = str(uuid.uuid4())  # unique per instance
        self.name = verb_key
        self.kind = None
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
        self.adjectives = set()
        self.semantics = set()

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
            print(f"Item: {item}")
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


class Parser:

    def tokenise(input_str, location = None,  inventory = None, items = None):

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
            #print(f"inventory: {inventory}")

        tokens = []
        for idx, word in enumerate(parts):
            kinds = set()
            canonical = None
            potential_match=False

            initial = verbs.list_null_words | set(directions) | set(loc_options)

            if word.lower() in initial or f"a {word}" in initial:
                if word.lower() in verbs.list_null_words:
                    kinds.add("null")
                    canonical = word

                if word.lower() in verbs.semantics:
                    kinds.add("sem")
                    canonical = word
                if word.lower() == "up" and idx == 1: ## temporarily doing this for 'pick up x'
                    if parts[0] == "pick":
                        #print("pick up")
                        kinds.add("null")
                        canonical = word
                else:
                    if word.lower() in directions:
                        kinds.add("direction")
                        canonical = word

                    if word.lower() in loc_options or f"a {word}" in loc_options:
                        kinds.add("location")
                        canonical = word

            else:
                if word.lower() in verbs.all_verbs:
                    kinds.add("verb")
                    canonical = word

                if word.lower() in verbs.adjectives:
                    kinds.add("adjective")
                    canonical = word

                if inventory and word in inventory:
                    kinds.add("noun")
                    canonical = word

                if location and word in item_names:
                    kinds.add("noun")
                    canonical = word

                if items:
                    if word.lower() in items:
                        kinds.add("noun")
                        canonical = word

            if canonical != None:
                potential_match = True
            tokens.append(Token(idx, word, kinds, canonical))

        if not potential_match:
            print(f"No verb found in {input_str}.")
        return tokens

    def token_role_options(token) -> list:

            kinds = set(token.kind)

            # pure optional null
            if kinds == {"null"}:
                return [None]

            # null + other roles → optional
            if "null" in kinds:
                return [k for k in kinds if k != "null"] + [None]

            # normal token
            return list(kinds)

    def get_viable_verbs(token):
        word = token.text
        viable_verbs = set()
        #print(f"Word: {word}")
        if verbs.by_name.get(word):
            viable_verbs.add(word)
        else:
            if verbs.by_alt_words.get(word): ## only allows for one alt_word to be true. Which is fine for now, I just need to make sure the wording is consistent.
                # Really though it needs to change, to allow for verbs that could have multiple meanings to be discerned.
                word_name = verbs.by_alt_words[word]
                word_name = word_name.name
                #print(f"word_name: {word_name}")
                viable_verbs.add(word_name)
        return viable_verbs

    def get_non_null_tokens(tokens) -> tuple[dict, int]:
        reformed_dict = {}
        token_count = 0
        for token in tokens:
            if token.kind == {"null"}:
                continue
            #print(token.text)
            reformed_dict[token_count] = token.text
            token_count += 1
        return reformed_dict, token_count

    def get_sequences_from_tokens(tokens) -> list:
        sequences = [[]]
        verb_options = set()

        for token in tokens:
            #print(f"Token: {token}")
            options = Parser.token_role_options(token)
            #print(f"Options: {options}")
            if "verb" in options:
                verb_options = Parser.get_viable_verbs(token)
            new_sequences = []

            for seq in sequences:
                #print(f"seq: {seq}")
                for opt in options:
                    if opt is None:
                        new_sequences.append(seq)
                    else:
                        new_sequences.append(seq + [opt])

            sequences = new_sequences

        return [tuple(seq) for seq in sequences if seq], verb_options

    def resolve_verb(tokens, verb_name, format_key) -> VerbInstance:

        #print(f"Format key: {format_key}")
        items = verbs.by_format.get(format_key) # gets verb names that match the format key
        #print(f"Items: {items}")
        #print(f"verb: {verb}")
        #print("by alt words: ", self.by_alt_words.get(verb.text))
        if items and verb_name in items:
            #print(f"Verb in items: {verb}")
            verb_obj = verbs.by_name.get(verb_name)[0]
            if not verb_obj:
                verb_obj = verbs.by_alt_words.get(verb_name)[0]
            #print(f"verb_obj: {verb_obj}")
            #print("verb_obj.name: ", verb_obj.name)
            if verb_obj:
                #verb_token = [i for i in tokens if i.text == verb_name]
                #print(f"Verb token: {verb_token}")
                print(f"Winning format: {format_key}")
                return verb_obj, format_key ## currently returns once it has a single success. Again, works as long as there's only one verb. For now, is fine.

        return None, format_key
    def reform_str(confirmed_verb, tokens, format_key):

        reformed_list = []

        ## 'if only one verb in format_key' <- should implement.
        reformed_dict, token_count = Parser.get_non_null_tokens(tokens)

        #print(f"Token count: {token_count}")

        for i, part in enumerate(format_key):
            if part == "verb":
                reformed_list.append(confirmed_verb.name)
            else:
                reformed_list.append(reformed_dict[i])

        return reformed_list



    def input_parser(self, input_str, location=None, inventory=None, items=None): # temporarily adding 'items' just so I can test with any item from the item dict without having to add to inventory/location first. Purely for testing convenience.
        confirmed_verb=None
        reformed_list = None
        tokens = self.tokenise(input_str, location, inventory, items)
        #print(f"Tokens at start: {tokens}") # here because determine_format previously altered the tokens themselves, that is fixed now but keeping in case.
   #     verb, format_keys = self.determine_format(tokens)
   #     confirmed_verb = self.find_by_format(verb, format_keys)

        sequences, verb_options = self.get_sequences_from_tokens(tokens)
        #print(f"Len sequences: {len(sequences)}")
        #print(f"Sequences: {sequences}")
        #print(f"Verb options: {verb_options}")
        _, token_count = Parser.get_non_null_tokens(tokens)
        #sequence_of_length = 0
        #confirmed_verb_numbers = 0
        for sequence in sequences:
            if not reformed_list:
                #print(f"Len sequence: {len(sequence)}, token count: {token_count}")
                if len(sequence) == token_count:
                    #sequence_of_length += 1
                    for verb_name in verb_options: ## Will generally only ever be one. But this will at least give the suggestion of dealing with multiple verbs. I guess this is good for the 'watch the watch' type thing.
                        confirmed_verb, format_key = self.resolve_verb(tokens, verb_name, sequence)
                        if confirmed_verb:
                            #confirmed_verb_numbers += 1
                            #print(f"confirmed verb: {confirmed_verb}")
                            #print(f"confirmed verb name: {confirmed_verb.name}")
                            reformed_list = self.reform_str(confirmed_verb, tokens, format_key)
                            print(f"Reformed list: {reformed_list}")
                            #break # stop once verb is found

        #print(f"correct length sequences: {sequence_of_length}")
        #print(f"confirmed_verb_numbers found: {confirmed_verb_numbers}")
        if not confirmed_verb and not reformed_list:
            print(f"NO CONFIRMED VERB FOUND FOR {input_str}")
        #print("At end: ")
        #print(f"TOKENS: {tokens}")
        #print(f"verb: {verb}")
        #print(f"format keys: {format_keys}")

    # -------------


verbs = VerbRegistry()

colours = ["BLACK","RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]

def initialise_registry():
    from verb_definitions import get_verb_defs, allowed_null, semantics
    verb_defs_dict, verb_set = get_verb_defs()
    verbs.all_verbs = verb_set
    verbs.adjectives = set(i.lower() for i in colours)
    verbs.semantics = set(i for i in semantics)
    verbs.list_null_words = allowed_null
    for item_name, attr in verb_defs_dict.items():
        verbs.create_verb_instance(item_name, attr)
        if attr.get("null_words"):
            for word in attr.get("null_words"):
                if word.lower() != None:
                    #print(f"Word in null words: {word}")
                    verbs.list_null_words.add(word)


if __name__ == "__main__":
    initialise_registry()
    #print("verbs: ")
    #print(verbs.by_name)
    #print("verbs by alt_words:")
    #print(verbs.by_alt_words)
    #print("go to the museum")
    #verbs.match_format("go to the museum")

    test=True
    if test:
        test_str = "go to the graveyard"
        print(f"\nTEST STRING: `{test_str}`")
        Parser.input_parser(Parser, test_str)
        from set_up_game import game, set_up ## might break
        set_up(weirdness=True, bad_language=True, player_name="Testing")
        test_str = "pick up the paperclip"
        print(f"\nTEST STRING: `{test_str}`")
        Parser.input_parser(Parser, test_str, inventory=game.inventory)
        test_str = "watch the watch"
        print(f"\nTEST STRING: `{test_str}`")
        Parser.input_parser(Parser, test_str, inventory=game.inventory)
        test_str = "look at watch"
        print(f"\nTEST STRING: `{test_str}`")
        Parser.input_parser(Parser, test_str, inventory=game.inventory)
        test_str = "put batteries in wallet"
        from item_definitions import item_defs_dict
        print(f"\nTEST STRING: `{test_str}`")
        Parser.input_parser(Parser, test_str, inventory=game.inventory, items=list(item_defs_dict.keys()))
        test_str = "look at batteries with wallet"
        print(f"\nTEST STRING: `{test_str}`")
        Parser.input_parser(Parser, test_str, inventory=game.inventory, items=list(item_defs_dict.keys()))
        test_str = "watch watch with watch"
        print(f"\nTEST STRING: `{test_str}`")
        Parser.input_parser(Parser, test_str, inventory=game.inventory, items=list(item_defs_dict.keys()))
