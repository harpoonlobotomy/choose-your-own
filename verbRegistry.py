## Going to rename this one to make it 'string_parser' or similar. The verbs don't live here, the string is just tokenised and formalised using the wordlists.

import uuid

from dataclasses import dataclass
from typing import Optional

null_adjectives = True

def test_print(input, print_true=False):
    #print(f"Input {input}, print_true: {print_true}")
    if print_true:
        print(input)

@dataclass
class Token:
    idx: int
    text: str
    kind: str              # 'verb', 'noun', 'semantic', 'null', 'location', 'direction'
    canonical: Optional[str] = None  # normalized form for words with alt variants


class VerbInstance:
    """
    Represents a single item in the game world or player inventory.
    """

    def __init__(self, verb_key:str, attr:dict):
        self.id = str(uuid.uuid4())  # unique per instance
        self.name = verb_key
        self.kind = None
        self.alt_words=attr["alt_words"]
        self.null_words = attr["allowed_null"]
        self.format = attr.get("format")
        self.distinction = attr.get("distinction") if attr.get("distinction") else None
        self.colour = None


class VerbRegistry:
    """
    Central manager for all verb instances.
    Also keeps a lookups for all-verbs, standardised text-parts, formats.
    """

    def __init__(self):

        self.verbs = {}      # id -> VerbInstance
        self.by_name = {}        # verb_key -> verb
        self.by_format = {}        # format -> set of verbs
        self.by_alt_words = {}
        self.list_null_words = set()
        self.all_verbs = set() ## just a list of all verbs inc alt names
        self.adjectives = set()
        self.semantics = set()
        self.formats = set()

    def create_verb_instance(self, verb_key:str, attr:dict)->VerbInstance:

        inst = VerbInstance(verb_key, attr)
        self.name = verb_key
        self.by_name.setdefault(verb_key, list()).append(inst)
        for alt_word in attr["alt_words"]:
            if alt_word:
                if self.by_alt_words.get(alt_word): ## does not work if alt words aren't exclusive. I think I need to keep them exclusive and let the verbs internally switch function (so, allow 'set' to recieve formats for both 'set x on fire' and 'set x on table', and inside 'set' refer it to 'burn'. not ideal but the best I have for nw.)
                    test_print(f"Alt words {alt_word} already exists.", print_true=True)
                self.by_alt_words.setdefault(alt_word, set()).add(inst)

        for item in attr["formats"]:
            self.by_format.setdefault(item, list()).append(inst.name)

        return inst

class Parser:

    def tokenise(input_str, location = None,  inventory = None, items = None):

        parts = input_str.split()
        from env_data import dataset
        loc_options = list(dataset.keys())
        from verb_definitions import directions

        if location:
            place, facing = location
            from itemRegistry import registry
            item_instances = registry.instances_by_location(place, facing) #### Can get this from the game, or pull it from location instances directly like this. Ideally though I think there should be an inbetween layer that handles 'requests for location items' to deal with 'what the player knows', 'what the lighting is', etc. But for testing this is okay.
            from misc_utilities import get_inst_list_names
            item_names = get_inst_list_names(item_instances)

        if inventory:
            from misc_utilities import get_inst_list_names
            inventory = get_inst_list_names(inventory)

        tokens = []
        omit_next = 0

        initial = verbs.list_null_words | set(directions) | set(loc_options)

        for idx, word in enumerate(parts):
            word = word.lower()
            kinds = set()
            potential_match=False

            test_print(f"idx {idx}, word: {word}")#, print_true=True)
            if omit_next>1:
                test_print(f"Skipping word part {idx} because it is a part match for {canonical}")
                test_print(f"Omit next: {omit_next}")
                omit_next -= 1
                continue

            else:
                canonical = None # reset to None here just so I can test_print the prior 'canonical' for word parts.
                #print(f"idx {idx}, word: {word}")

                ### Special allowance: Stating the kind directly, for testing only. Remove before actual game because it'll break things.
                if word in ("verb", "noun", "location", "sem", "dir"):
                    kinds.add(word)
                    canonical=word
                    tokens.append(Token(idx, word, kinds, canonical))
                    continue


                if word in initial or f"a {word}" in initial:
                    if word in verbs.list_null_words:
                        kinds.add("null")
                        canonical = word

                    if word in verbs.semantics:
                        kinds.add("sem")
                        canonical = word
                    if word == "up" and idx == 1: ## temporarily doing this for 'pick up x'
                        if parts[0] == "pick":
                            #print("pick up")
                            kinds.add("null")
                            canonical = word
                    else:
                        if word in directions:
                            kinds.add("direction")
                            canonical = word

                        if word in loc_options or f"a {word}" in loc_options:
                            kinds.add("location")
                            canonical = word

                else:
                    if word in verbs.all_verbs:
                        #print(f"Word in all_verbs: {word}")
                        kinds.add("verb")
                        canonical = word
                        #print(f"canonical: {canonical}")
                    if word in verbs.adjectives:
                        if null_adjectives: ## exclude adjectives here. For now, adjectives are not actively implemented, just excluded in a specific way. Will amend this later.
                            kinds.add("null")
                        else:
                            kinds.add("adjective")
                        canonical = word

                    if inventory and word in inventory:
                        kinds.add("noun")
                        canonical = word

                    if location and word in item_names:
                        kinds.add("noun")
                        canonical = word

                    if items:
                        if word in items:
                            kinds.add("noun")
                            canonical = word


                if canonical != None:
                    potential_match = True
                else:
                    compound_match = 0
                    compound_matches = {}
                    for compound_word, word_parts in plural_word_dict.items():
                        if word in word_parts:
                            test_print(f"MATCH IN PLURAL WORDS: `{word}` FOR COMPOUND WORD: {compound_word}")#, print_true=True)
                            matches_count = 0
                            for _ in word_parts:
                                try:
                                    if parts[idx+matches_count] and parts[idx+matches_count].lower() in word_parts:
                                        test_print(f"parts[{idx}+{matches_count}]: {parts[idx+matches_count]}")#, print_true=True)
                                        matches_count += 1
                                    else:
                                        test_print(f"parts[idx+matches_count]: {parts[idx+matches_count].lower()}")
                                        test_print(f"Part {matches_count+1} `{parts[idx+matches_count]}` does not match expected second word {word_parts[matches_count]}")
                                except:
                                    test_print(f"No matched word-parts after parts[{idx}+{matches_count}].")#, print_true=True)
                                    break
                            compound_match += 1
                            compound_matches[compound_word]=tuple(((compound_match, len(word_parts)))) ## if input == 'paper scrap': "paper scrap with paper":(2,4)

                    if compound_match == 1:
                        canonical = list(compound_matches.keys())[0] ## just add it if it's the only possible match, for now. Make it more rigorous later, but this'll catch most cases.
                        kinds.add("noun")
                        potential_match=True
                        omit_next = matches_count ## Skip however many successful matches there were, so we don't re-test words confirmed to be part of a compound word.

                    else:
                        test_print("More than one potential compound match, the system can't cope with that yet.", print_true=True)
                        ## Set up a fn where it tests the results tuple of compound_word, whichever compound_word in compound_matches has the best ration of (matches, total_parts) wins.)
                        ## If multiple options and all have same ratio, then we take the longest. So, 'blue glass jar, glass jar and jar' might all successfully match for separate jar-type items. But even if 'glass jar', 'blue glass jar' and 'jar' are legit entities, 'blue glass jar' wins if all three are matched. So first get match-ratio, then if no winner, get matched-length. There'll most likely only be one potential winner but good to have the system in place.

                #else:
                ## Currently if it doesn't match any of the above, it fails entirely. idk if I want to run a quick 'did you mean (close suggestion)' here later or not.

                #    kinds.add("noun")
                #    canonical = word ## just say it's a noun if nothing else, should be marked differently but this'll do for now.
                    #   Means at least for the moment in testing I can do
                    #   Winning format: ('verb', 'noun', 'direction', 'noun')
                    #   Reformed list: ['drop', 'batteries', 'in', 'toilet']
                #    potential_match=True

                tokens.append(Token(idx, word, kinds, canonical))
            #print(f"canonical: {canonical}")
                #print(idx, word, kinds, canonical)
            if not potential_match:
                test_print(f"No full match found for parts in `{input_str}`.")

        return tokens


    def token_role_options(token) -> list:

            kinds = set(token.kind)
            if not kinds:
                return [None]
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
            if verbs.by_alt_words.get(word):
                word_names = verbs.by_alt_words[word]
                for word_name in word_names:
                    viable_verbs.add(word_name.name)
        return viable_verbs

    def get_non_null_tokens(tokens) -> tuple[dict, int]:
        reformed_dict = {}
        token_count = 0
        for token in tokens:
            #print(f"Token kind: {token.kind}")
            if token.kind == {"null"} or token.kind == set(): ## simplify this later.
                continue

            #print(f"Token.kind: {token.kind}")
            #print(f"Token.canonical: {token.canonical}")
            reformed_dict[token_count] = {list(token.kind)[0]: token.canonical}
            #print(f"Token text: {token.text}")
            #rint(f"Token text: {token.canonical}")
            token_count += 1
        return reformed_dict, token_count

    def get_sequences_from_tokens(tokens) -> list:
        sequences = [[]]
        verb_options = set()
        force_false_verb = False

        for token in tokens:
            #print(f"Token: {token}")
            options = Parser.token_role_options(token)
            #print(f"Options: {options}")
            if "verb" in options:
                if token.canonical == "verb":

                    verb_options.add("verb")
                    force_false_verb=True
                else:
                    verb_options = Parser.get_viable_verbs(token)

            ## If 'dir' in token, note. If next token is also dir, check if it's the first part of a two part (eg 'away from', 'up against', etc. If so, then treat it as only one dir, omit the second, and make sure the combined-dir is the token-text instead.)
            ## Actually could do this in the tokeniser stage, like I have with verbs. Mm. Really should, actually. Okay, marked as a TODO.

            new_sequences = []

            for seq in sequences:

                for opt in options:
                    if opt is None:
                        new_sequences.append(seq)
                    else:
                        new_sequences.append(seq + [opt])

            sequences = new_sequences
        test_print(f"Sequences: {sequences}")#, print_true=True)
        test_print(f"Verb options: {verb_options}")#, print_true=True)
        viable_sequences = []
        for seq in sequences:
            if seq:
                if force_false_verb:
                    viable_sequences.append(seq)

                if tuple(seq) in verbs.formats:
                    viable_sequences.append(seq)

        #print("total potential sequences: ", len(sequences))
        #print("viable sequences: ", len(viable_sequences))
        #print(f"verb_options: {verb_options}")
        return [tuple(seq) for seq in viable_sequences if seq], verb_options

    def resolve_verb(tokens, verb_name, format_key) -> VerbInstance:

        #print(f"Format key: {format_key}")
        items = verbs.by_format.get(format_key) # gets verb names that match the format key
        if items == None and verb_name == "verb":
            if verb_name == "verb":
                #print("Returning: verb_name, format_key, ", verb_name, format_key)
                return verb_name, format_key
        #print("by alt words: ", verbs.by_alt_words.get(verb_name))
        if items and verb_name in items:
            #print(f"Verb in items: {verb}")
            verb_obj = verbs.by_name.get(verb_name)[0]
            if not verb_obj:
                verb_obj = verbs.by_alt_words.get(verb_name)[0] ## Currently just takes the first. I think this is fine for now, later would like to set some minor refinement rules (such as the 'if 'fire' in noun token, then 'burn' instead of 'place' if 'burn' in by_alt_words options. But for now this is fine.)
            #print(f"verb_obj: {verb_obj}")
            #print("verb_obj.name: ", verb_obj.name)
            if verb_obj:
                #verb_token = [i for i in tokens if i.text == verb_name]
                #print(f"Verb token: {verb_token}")
                test_print(f"Winning format: {format_key}", print_true=True)
                return verb_obj, format_key ## currently returns once it has a single success. Again, works as long as there's only one verb. For now, is fine.

        return None, format_key

    def reform_str(confirmed_verb, tokens, format_key, return_all_parts=True):

        reformed_list = []

        ## 'if only one verb in format_key' <- should implement.
        reformed_dict, token_count = Parser.get_non_null_tokens(tokens)

        #print(f"Token count: {token_count}")

        for i, part in enumerate(format_key):
            if part == "verb" and not isinstance(confirmed_verb, str): ## TODO: Remove this later, this is just for format testing so I can type 'verb' instead of having to actually have real formats set up. No idea why though, guess I kinda just thought of it decided to put it in. No improvement over just using things that exist. Eh..
                reformed_list.append(confirmed_verb.name)
                confirmed_verb = confirmed_verb.name
            else:
                #print("confirmed_verb: ",confirmed_verb)
                reformed_list.append(reformed_dict[i])

        if return_all_parts:
            for idx, kind in reformed_dict.items():
                for k, v in kind.items():
                    if k == "verb":
                        reformed_dict[idx][k]=confirmed_verb

            #reformed_dict[]
            return format_key, reformed_dict
        return reformed_list



    def input_parser(self, input_str, location=None, inventory=None, items=None): # temporarily adding 'items' just so I can test with any item from the item dict without having to add to inventory/location first. Purely for testing convenience.
        confirmed_verb = None
        reformed_list = None
        tokens = self.tokenise(input_str, location, inventory, items)

        sequences, verb_options = self.get_sequences_from_tokens(tokens)
        #print(f"Len sequences: {len(sequences)}")
        #print(f"Sequences: {sequences}")
        #print(f"Verb options: {verb_options}")
        _, token_count = Parser.get_non_null_tokens(tokens)
        sequence_of_length = 0
        confirmed_verb_numbers = 0
        for sequence in sequences:
                #print(f"Sequence in sequences: {sequences}")
            #if not reformed_list:
                #print(f"Len sequence: {len(sequence)}, token count: {token_count}")
                if len(sequence) == token_count:
                    sequence_of_length += 1
                    for verb_name in verb_options: ## Will generally only ever be one. But this will at least give the suggestion of dealing with multiple verbs. I guess this is good for the 'watch the watch' type thing.
                        #if verb_name == "verb":
                        #print(f"Verb name: {verb_name}")
                        confirmed_verb, format_key = self.resolve_verb(tokens, verb_name, sequence)
                        #print(f"confirmed verb: {confirmed_verb}, format key: {format_key}")
                        if confirmed_verb:
                            confirmed_verb_numbers += 1
                            #print(f"confirmed verb: {confirmed_verb}")
                            #print(f"confirmed verb name: {confirmed_verb.name}")
                            reformed_list = self.reform_str(confirmed_verb, tokens, format_key, return_all_parts=True) # if return_all_parts, returns parts not string, for verb_membrane.
                            format_key, reformed_dict = reformed_list
                            test_print(f"Reformed list: {reformed_list}", print_true=True)
                            return reformed_dict#, format_key ## for now we stop if we find one.
                            #break # stop once verb is found

        #print(f"correct length sequences: {sequence_of_length}")
        #print(f"confirmed_verb_numbers found: {confirmed_verb_numbers}")
        if not confirmed_verb and not reformed_list:
            test_print(f"NO CONFIRMED VERB FOUND FOR {input_str}", print_true=True)
        #print("At end: ")
        #print(f"TOKENS: {tokens}")
        #print(f"verb: {verb}")
        #print(f"format keys: {format_keys}")

    # -------------


verbs = VerbRegistry()

colours = ["BLACK","RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]
sizes = ["big", "small", "tiny", "enormous", "massive", "little"]

def initialise_registry():
    from verb_definitions import get_verb_defs, allowed_null, semantics, formats
    verb_defs_dict, verb_set = get_verb_defs()
    verbs.all_verbs = verb_set
    verbs.formats = set(formats.values())
    #test_print(f"Verbs format: {verbs.formats}")
    verbs.adjectives = set(i.lower() for i in colours) | set(i.lower() for i in sizes)
   #print(f"ADJECTIVES: {verbs.adjectives}")
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


    test=True
    action_test=True
    if test:

        from set_up_game import game, set_up ## might break
        set_up(weirdness=True, bad_language=True, player_name="Testing")
        from item_definitions import item_defs_dict
        plural_word_names = [i for i in list(item_defs_dict.keys()) if len(i.split()) > 1]
        plural_word_dict = {}
        for word in plural_word_names:
            plural_word_dict[word] = tuple(word.split())

        if action_test:
            test_str_list = ["go to the graveyard", "pick up the paperclip", "put batteries in wallet", "GET PAPER SCRAP FROM JAR", "place the batteries on the jar"]
        else:
            test_str_list = ["go to the graveyard", "pick up the paperclip", "watch the watch", "look at watch", "put batteries in wallet", "look at batteries with wallet", "watch watch with watch", "pick up red wallet", "drop batteries in jar", "take paper scrap", "get paper scrap with number from jar", "get paper scrap from jar", "GET PAPER SCRAP FROM JAR", "place the batteries on the jar"]
        #test_str_list = ["verb noun dir noun"]

        for item in test_str_list:
            test_str = item
            test_print(f"\nTEST STRING: `{test_str}`", print_true=True)
            reformed_dict = Parser.input_parser(Parser, test_str, inventory=game.inventory, items=list(item_defs_dict.keys()))

            if action_test:

                #result_dict:



                from verb_membrane import initialise_registry, v_actions
                initialise_registry()

                #verb_name, reformed_dict, format, tokens = parser_output
                v_actions.route_verbs(reformed_dict)
            #'winning format: ('verb', 'noun', 'direction', 'noun')
            #Reformed list: ('put', ('verb', 'noun', 'direction', 'noun'), {0: 'place', 1: 'batteries', 2: 'on', 3: 'glass jar'}, [Token(idx=0, text='place', kind={'verb'}, canonical='place'), Token(idx=1, text='the', kind={'null'}, canonical='the'), Token(idx=2, text='batteries', kind={'noun'}, canonical='batteries'), Token(idx=3, text='on', kind={'null', 'direction'}, canonical='on'), Token(idx=4, text='the', kind={'null'}, canonical='the'), Token(idx=5, text='jar', kind={'noun'}, canonical='glass jar')])'
