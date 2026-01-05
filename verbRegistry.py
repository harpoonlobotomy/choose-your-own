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
        self.formats = attr.get("formats")
        self.format_parts = {}
        for i, format_set in enumerate(self.formats):
            f_parts_dict = self.format_parts.setdefault(i, {})
            for idx, format_element in enumerate(format_set):
                f_parts_dict[idx]=format_element
        #self.format_parts = f_parts_dict
        #print(f"Format parts (list): {self.format_parts}")
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
        self.compound_words = {}

    def create_verb_instance(self, verb_key:str, attr:dict)->VerbInstance:

        inst = VerbInstance(verb_key, attr)
        self.name = verb_key
        self.by_name.setdefault(verb_key, list()).append(inst)
        for alt_word in attr["alt_words"]:
            if alt_word and self.by_alt_words.get(alt_word):
                test_print(f"Alt words {alt_word} already exists.", print_true=True)
                self.by_alt_words.setdefault(alt_word, list()).append(inst)

        for item in attr["formats"]:
            self.by_format.setdefault(item, list()).append(inst.name)

        return inst

@dataclass
class Parser:

    def tokenise(input_str, nouns_list, locations, directions):

        parts = input_str.split()
        loc_options = locations

        items = nouns_list

        tokens = []
        omit_next = 0

        initial = verbs.list_null_words | set(directions) | set(loc_options)

        #print(f"verbs.null words: {verbs.list_null_words}")

        for idx, word in enumerate(parts):
            word = word.lower()
            kinds = set()
            potential_match=False

            #test_print(f"idx {idx}, word: {word}")#, print_true=True)
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

                    if word in items:
                        kinds.add("noun")
                        canonical = word


                if canonical != None:
                    potential_match = True
                else:
                    compound_match = 0
                    compound_matches = {}
                    #print(f"No canonical for idx `{idx}`, word `{word}`")
                    #print(f"verbs.compound_words: {verbs.compound_words}")
                    for compound_word, word_parts in verbs.compound_words.items():
                        #print(f"Word: {word} // word parts: {word_parts}")
                        if word in word_parts:
                            test_print(f"MATCH IN PLURAL WORDS: `{word}` FOR COMPOUND WORD: {compound_word}", print_true=True)
                            matches_count = 0
                            for _ in word_parts:
                                try:
                                    if parts[idx+matches_count] and parts[idx+matches_count].lower() in word_parts:
                                        test_print(f"parts[{idx}+{matches_count}]: {parts[idx+matches_count]}")#, print_true=True)
                                        matches_count += 1
                                    elif parts[idx+matches_count].lower() == "magazine" and "mag" in word_parts: # hardcoded for magazines, they're an odd one.
                                        #TODO: later, put something like this in for general shorthand.
                                        test_print(f"parts[{idx}+{matches_count}]: {parts[idx+matches_count]}")#, print_true=True)
                                        matches_count += 1

                                    else:
                                        print(f"parts[idx+matches_count]: {parts[idx+matches_count].lower()}")
                                        print(f"Part {matches_count+1} `{parts[idx+matches_count]}` does not match expected second word {word_parts[matches_count]}")
                                except:
                                    test_print(f"No matched word-parts after parts[{idx}+{matches_count}].", print_true=True)
                                    break
                            compound_match += 1
                            compound_matches[compound_word]=tuple(((compound_match, len(word_parts)))) ## if input == 'paper scrap': "paper scrap with paper":(2,4)

                    if compound_match == 1:
                        canonical = list(compound_matches.keys())[0] ## just add it if it's the only possible match, for now. Make it more rigorous later, but this'll catch most cases.
                        kinds.add("noun")
                        potential_match=True
                        omit_next = matches_count ## Skip however many successful matches there were, so we don't re-test words confirmed to be part of a compound word.

                    else:
                        print(f"Compound matches: {compound_match}")
                        print(f"Content: {compound_matches}")
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

    def get_viable_verb(token):
        word = token.text
        viable_instance = None
        #print(f"Word: {word}")
        if verbs.by_name.get(word):
            viable_instance = (verbs.by_name.get(word)[0])
        else:
            if verbs.by_alt_words.get(word):
                viable_instance = (verbs.by_alt_words[word][0]) ## the advantage of this is that if we have a verb with two very different interpretations (eg 'set on fire' and 'set down', we can differentiate later. But it's very very messy. That should be done inside 'set' if needed.)

        if not viable_instance:
            print(f"Could not find viable instance for verb `{word}`. \nExiting immediately.")
            exit()
        return viable_instance

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
            #print(f"Token dir: {dir(token)}")
            #rint(f"Token text: {token.canonical}")
            token_count += 1

        return reformed_dict, token_count

    def get_sequences_from_tokens(tokens) -> list:
        sequences = [[]]
        verb_instance = None

        for token in tokens:
            #print(f"Token: {token}")
            options = Parser.token_role_options(token)
            #print(f"Options: {options}")
            if "verb" in options:
                verb_instance = Parser.get_viable_verb(token)

            new_sequences = []

            for seq in sequences:

                for opt in options:
                    if opt is None:
                        new_sequences.append(seq)
                    else:
                        new_sequences.append(seq + [opt])

            sequences = new_sequences
        #test_print(f"Sequences: {sequences}", print_true=True)

        if not verb_instance:
            print("No verb_instance found in get_sequences_from_tokens. Exiting immediately.")
            print(f"TOKENS: {tokens}")
            exit()

        #print(f"Verb instances: {verb_instance}")
        viable_sequences = []
        for seq in sequences:
            if seq:
                #if tuple(seq) in verbs.formats:
                if tuple(seq) in verb_instance.formats:
                    #print(f"This sequence is compatible with verb_instance {verb_instance.name}: {seq}")
                    viable_sequences.append(seq)

        return [tuple(seq) for seq in viable_sequences if seq], verb_instance

    def resolve_verb(tokens, verb_name, format_key) -> tuple[VerbInstance|str]:

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

    def build_dict(confirmed_verb, tokens, initial_dict, format_key):

        dict_for_output = initial_dict
        print_refined = []
        for token_index, data in initial_dict.items():
            #   idx: `0`, kind: `{'verb': 'drop'}`
            for kind, entry in data.items():
                #   k: `verb`, v: `drop`
                if kind == "verb":
                    dict_for_output[token_index][kind]=confirmed_verb
                print_refined.append(entry)

        print(f"RESULT: [[ '{"' '".join(print_refined)}' ]]")
        return format_key, dict_for_output, tokens # including tokens for any minor input detail that might matter later.


    def input_parser(self, input_str, membrane_data): # temporarily adding 'items' just so I can test with any item from the item dict without having to add to inventory/location first. Purely for testing convenience.

        nouns_list, locations, directions = membrane_data
        tokens = self.tokenise(input_str, nouns_list, locations, directions)
        #print("done with tokenise")
        #print(f"Tokens: {tokens}")
        sequences, verb_instance = self.get_sequences_from_tokens(tokens)

        if not sequences:
            print(f"No viable sequences found for {input_str}. Exiting immediately.")
            exit()
        initial_dict, token_count = Parser.get_non_null_tokens(tokens)

        length_checked_sequences = []
        for sequence in sequences:
            if len(sequence) == token_count:
                length_checked_sequences.append(sequence)

        viable_formats, dict_for_output, tokens = self.build_dict(verb_instance, tokens, initial_dict, length_checked_sequences)

        return viable_formats, dict_for_output

    # -------------


verbs = VerbRegistry()

colours = ["BLACK","RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]
sizes = ["big", "small", "tiny", "enormous", "massive", "little"]

def initialise_verbRegistry():
    from verb_definitions import get_verb_defs, allowed_null, semantics, formats, nulls

    verb_defs_dict, verb_set = get_verb_defs()
    verbs.all_verbs = verb_set
    verbs.formats = set(formats.values())
    verbs.adjectives = set(i.lower() for i in colours) | set(i.lower() for i in sizes)
    verbs.semantics = set(i for i in semantics)
    verbs.list_null_words = allowed_null

    from item_definitions import item_defs_dict
    plural_word_names = [i for i in list(item_defs_dict.keys()) if len(i.split()) > 1]
    verbs.compound_words = {}
    for word in plural_word_names:
        verbs.compound_words[word] = tuple(word.split())

    for item_name, attr in verb_defs_dict.items():
        verbs.create_verb_instance(item_name, attr)
        #verb_inst = verbs.by_name.get(item_name)[0]
        #print(f"Verb inst: {verb_inst}")
        #print("formats: ")
        #print(verb_inst.formats) # list of sets
        #exit()

        if attr.get("null_words"):
            for word in attr.get("null_words"):
                if word.lower() != None:
                    #print(f"Word in null words: {word}")
                    verbs.list_null_words.add(word)


if __name__ == "__main__":
    initialise_verbRegistry()


    test=True
    action_test=True
    if test:

        from set_up_game import game, set_up ## might break
        set_up(weirdness=True, bad_language=True, player_name="Testing")


        if action_test:
            test_str_list = ["drop the paperclip"]
            #test_str_list = ["go to the graveyard", "pick up the paperclip", "put batteries in wallet", "GET PAPER SCRAP FROM JAR", "place the batteries on the jar"]
        else:
            test_str_list = []#"go to the graveyard", "pick up the paperclip", "watch the watch", "look at watch", "put batteries in wallet", "look at batteries with wallet", "watch watch with watch", "pick up red wallet", "drop batteries in jar", "take paper scrap", "get paper scrap with number from jar", "get paper scrap from jar", "GET PAPER SCRAP FROM JAR", "place the batteries on the jar"]
        #test_str_list = ["verb noun dir noun"]

        for item in test_str_list:
            test_str = item
            test_print(f"\nTEST STRING: `{test_str}`", print_true=True)
            from item_definitions import item_defs_dict
            items = list(item_defs_dict.keys())
            viable_formats, dict_for_output = Parser.input_parser(Parser, test_str, items)

            if action_test:
                print("Initialising verb membrane: ")
                #result_dict:


##  >   router(noun_inst, verb_inst, reformed_dict)
                #verb_name, reformed_dict, format, tokens = parser_output
                print(f"Reformed dict before route_verbs: {dict_for_output}")
                #v_actions.route_verbs(dict_for_output)
            #'winning format: ('verb', 'noun', 'direction', 'noun')
            #Reformed list: ('put', ('verb', 'noun', 'direction', 'noun'), {0: 'place', 1: 'batteries', 2: 'on', 3: 'glass jar'}, [Token(idx=0, text='place', kind={'verb'}, canonical='place'), Token(idx=1, text='the', kind={'null'}, canonical='the'), Token(idx=2, text='batteries', kind={'noun'}, canonical='batteries'), Token(idx=3, text='on', kind={'null', 'direction'}, canonical='on'), Token(idx=4, text='the', kind={'null'}, canonical='the'), Token(idx=5, text='jar', kind={'noun'}, canonical='glass jar')])'
