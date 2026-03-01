## Going to rename this one to make it 'string_parser' or similar. The verbs don't live here, the string is just tokenised and formalised using the wordlists.

#Note for future me: 'meta_commands' is where all meta actions are directed to. 'meta' + <noun/loc/card>' or just <meta> will trigger meta_commands.

import uuid

from dataclasses import dataclass
from typing import Optional

#import generate_locations
from logger import logging_fn
from printing import print_green, print_red
from verb_actions import get_current_loc

from config import show_reciever
print("Verb registry is being run right now.")

null_adjectives = True

def verbReg_Reciever(*values):
    if show_reciever:
        logging_fn()
        return values

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
    Represents a single verb to be used by the parser.
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

    def __repr__(self):
        return f"<verbInstance {self.name} ({self.id})>"

class VerbRegistry:
    """
    Central manager for all verb instances.
    Also keeps a lookups for all-verbs, standardised text-parts, formats.
    """

    def __init__(self):

        self.verbs = {}      # name -> VerbInstance
        self.meta_verbs = {}
        self.all_meta_verbs = {}
        self.by_format = {}        # format -> set of verbs
        self.by_alt_words = {}
        self.list_null_words = set()
        self.all_verbs = set() ## just a list of all verbs inc alt names
        self.adjectives = set()
        self.semantics = set()
        self.formats = set()
        self.cardinals = set()
        self.compound_words = {}
        self.null_sem_combinations = list()

    def create_verb_instance(self, verb_key:str, attr:dict)->VerbInstance:

        inst = VerbInstance(verb_key, attr)
        self.verbs[verb_key]=inst
        self.name = verb_key
        for alt_word in attr["alt_words"]:
            if alt_word == "":
                continue
            if alt_word and self.by_alt_words.get(alt_word):
                test_print(f"Alt words {alt_word} already exists.", print_true=True)
            else:
                self.by_alt_words.setdefault(alt_word, list()).append(inst)

        for item in attr["formats"]:
            self.by_format.setdefault(item, list()).append(inst.name)

        return inst

@dataclass
class Parser:

    def check_compound_words(parts_dict, word, parts, idx, kinds, word_type, omit_next, local_nouns = None):
        logging_fn()

        #print(f"\nCHECK COMPOUND WORDS: {word_type}\n")
        #print(f"omit_next at top of compound_words: {omit_next}")
        canonical = potential_match = perfect_match = None
        compound_match = 0
        compound_matches = {}

        for compound_word, word_parts in parts_dict.items():
            if perfect_match:
                #print(f"PERFECT MATCH: {perfect_match}")
                break
            #print(f"Word: {word} // word parts: {word_parts}")
            if word in word_parts:
                matches_count = 0
                for bit in word_parts:
                    try:
                        if len(parts) > idx + matches_count and bit == parts[idx+matches_count]:
                            matches_count += 1
                            #print(f"Matches_count: {matches_count} / bit: {bit}")
                            if matches_count == len(word_parts):
                                perfect_match = compound_word
                                break

                    except Exception as e:
                        print(f"Failed in check_compound_words: {e}")
                        print(f"No matched word-parts after parts[{idx}+{matches_count}].")
                        break
                compound_match += 1

                compound_matches[compound_word]=tuple(((matches_count, len(word_parts)))) ## if input == 'paper scrap': "paper scrap with paper":(2,4)

        if perfect_match:
            #print(f"PERFECT MATCH: {perfect_match}, matches_count: {matches_count}")
            canonical = perfect_match
            if isinstance(kinds, str):
                if kinds == "No match" or kinds == "":
                    kinds = set()
                else:
                    temp = kinds
                    kinds = set()
                    kinds.add(temp)
            kinds.add(word_type)
            potential_match=True
            omit_next += matches_count-1
            return idx, word, kinds, canonical, potential_match, omit_next, perfect_match

        elif compound_match:
            matches = set()
            match = None
            #print(f"Compound matches: {compound_matches}")
            least_missing = 10
            winner = None
            locals = list()
            if word_type == "noun":
                for item in local_nouns:
                    if item in compound_matches:
                        locals.append(item)

                if locals and len(locals) == 1:
                    matches_count, _ = compound_matches[locals[0]]
                    canonical = locals[0]
                    omit_next += matches_count -1
                    kinds.add(word_type)
                    #perfect_match = canonical
                    return idx, word, kinds, canonical, potential_match, omit_next, perfect_match


            for item in compound_matches:
                by_alt_words = verbs.by_alt_words.get(item)
                if by_alt_words:
                    print(f"ITEM in compound_matches: {item}")
                    print(f"By alt words: {by_alt_words}")

                matched, total_parts = compound_matches[item]
                if matched == 0:
                    matched = 1 # eg 'mag' is 'fashion magazine', but the index is wrong so it marks nothing and breaks later. At least one match happened or it wouldn't be in compound_matches.
                missing = total_parts - matched
                ratio = missing/total_parts
                #print(f"Missing: {missing} / ratio total/missing: {ratio} (total_parts: {total_parts})")
                if missing < least_missing:
                    least_missing = missing
                    winner = item

            match = winner
            if match:
                matches_count, _ = compound_matches[match]
            else:
                matches_count = 0
            if match:
                canonical = match
                omit_next += matches_count -1
                kinds.add(word_type)
                #print(f"Canonical: {canonical}. omit_next: {omit_next}, word type: {word_type}")
            else:
                if not matches:
                    if word_type == "noun":
                        kinds.add("noun")
                    canonical = "assumed_noun"
                    return idx, word, kinds, canonical, potential_match, omit_next, perfect_match

        else:
            kinds.add("noun")
            canonical = "assumed_noun"

        return idx, word, kinds, canonical, potential_match, omit_next, perfect_match

    def tokenise(input_str, membrane):

        current_location = get_current_loc()

        locations = membrane.locations
        directions = membrane.directions
        cardinals = membrane.cardinals

        word_phrases = membrane.combined_wordphrases
        parts = input_str.split()
        loc_options = locations
        compound_locs = membrane.compound_locations
        compound_nouns = membrane.plural_words_dict
        numbers = membrane.numbers

        items = membrane.local_nouns

        tokens = []
        omit_next = 0

        initial = verbs.list_null_words | set(directions) | set(loc_options) | verbs.semantics | cardinals

        for idx, word in enumerate(parts):
            word = word.lower()
            kinds = set()
            potential_match=False
            verbReg_Reciever(f"Tokenise: idx: {idx}, word: {word}, omit_next: {omit_next}")
            if omit_next >= 1:
                omit_next -= 1
                continue

            else:
                canonical = None
                if word in verbs.all_meta_verbs:
                    if word not in verbs.meta_verbs:
                        for key_word in verbs.meta_verbs:
                            if verbs.meta_verbs[key_word].get("alt_words"):
                                for alt_word in verbs.meta_verbs[key_word]["alt_words"]:
                                    if word == alt_word:
                                        word = key_word
                                        kinds.add("meta")
                                        canonical = word
                    else:
                        #print(f"word in meta_verbs: {word}")
                        kinds.add("meta")
                        canonical = word
                if word in numbers:
                        #print(f"word in verbs.semantics: {word}")
                        kinds.add("number")
                        canonical = word
                if word in initial or f"a {word}" in initial:
                    #print(f"Word in initial: {word}")
                    if word in word_phrases and (word_phrases.get(word) and parts[0] in word_phrases.get(word)):
                        #print(f"word in verbs.null_words: {word}")
                        kinds.add("null")
                        canonical = word
                    if word in verbs.semantics:
                        #print(f"word in verbs.semantics: {word}")
                        kinds.add("sem")
                        canonical = word
                    elif word in verbs.list_null_words:
                        #print(f"word in verbs.null_words: {word}")
                        kinds.add("null")
                        canonical = word

                    else:
                        #print(f"word in else initial: {word}")
                        if word in cardinals:
                            kinds.add("cardinal")
                            canonical = word

                        if word in directions:
                            kinds.add("direction")
                            canonical = word

                        if word in loc_options or f"a {word}" in loc_options:
                            if word in current_location or f"a {word}" in current_location:
                                canonical = current_location[0]
                            else:
                                canonical = word
                            kinds.add("location")

                if word in verbs.all_verbs:
                    if word in word_phrases and word_phrases.get(word) and parts[0] in word_phrases.get(word):
                        kinds.add("null")
                        canonical = word
                        continue

                    if word in verbs.split_verbs and verbs.split_verbs.get(word) and parts[1] in verbs.split_verbs[word]:
                        canonical = verbs.split_verbs[word]
                        kinds.add("verb")
                        omit_next += 1

                    else:
                        kinds.add("verb")
                        canonical = word

                if word in verbs.adjectives:
                    if null_adjectives:
                        kinds.add("null")
                    else:
                        kinds.add("adjective")
                    canonical = word

                if word in items:
                    kinds.add("noun")
                    canonical = word

                if word in verbs.meta_verbs:
                    kinds.add("meta")
                    canonical = word
                else:
                    for verb in verbs.meta_verbs:
                        if verbs.meta_verbs[verb].get("alt_words"):
                            if word == verbs.meta_verbs[verb]["alt_words"]:
                                kinds.add("meta")
                                canonical = word

                if canonical != None:
                    if "meta" in kinds and "verb" in kinds and len(kinds) == 2:
                        kinds = (("meta",))
                    tokens.append(Token(idx, word, kinds, canonical))
                    potential_match = True
                else:
                    second_perfect = None
                    idx, word, kinds, canonical, potential_match, omit_next, perfect = Parser.check_compound_words(parts_dict = compound_nouns, word=word, parts=parts, idx=idx, kinds=kinds, word_type = "noun", omit_next=omit_next, local_nouns = items)
                    second_perfect = None

                    try:
                        second_idx, second_word, second_kinds, second_canonical, second_potential_match, second_omit_next, second_perfect = Parser.check_compound_words(parts_dict = compound_locs, word=word, parts=parts, idx=idx, kinds=kinds, word_type = "location", omit_next=omit_next)
                    except Exception as e:
                        print(f"Could not get location: {e}")

                    if perfect and not second_perfect:
                        omit_next = len(perfect.split(" "))
                        kinds = (("noun",))
                        word = perfect
                        tokens.append(Token(idx, word, kinds, canonical))
                        continue

                    elif second_perfect:
                        omit_next = len(second_perfect.split(" "))
                        kinds = (("location",))
                        second_word = second_canonical
                        tokens.append(Token(second_idx, second_word, kinds, second_canonical))
                        continue

                    if canonical and canonical != "assumed_noun":
                        tokens.append(Token(idx, word, kinds, canonical))
                        continue

                    if ((not canonical or canonical == "assumed_noun") and (second_canonical and not second_canonical == "assumed_noun")) or (perfect and second_perfect):
                        idx = second_idx
                        word = second_word
                        kinds = (("location",))
                        #kinds = second_kinds
                        canonical = second_canonical
                        potential_match = second_potential_match
                        omit_next = second_omit_next
                        tokens.append(Token(idx, word, kinds, canonical))
                        continue

                    if not canonical or second_canonical:
                        verbReg_Reciever(f"Tokenise: idx: {idx}, word: {word}, not canonical")
                        kinds = set()
                        kinds.add("noun")
                        canonical = "assumed_noun"
                        tokens.append(Token(idx, word, kinds, canonical))
                        continue

            if not potential_match:
                test_print(f"No full match found for parts in `{input_str}`.")

        return tokens


    def token_role_options(token:Token) -> list:

            verbReg_Reciever(f"top of token_role_options: {token}")
            kinds = set(token.kind)
            if not kinds:
                return [None]
            # pure optional null
            if kinds == {"null"}:
                verbReg_Reciever(f"token_role_options: {token} // kinds: {kinds}")
                return [None]

            # null + other roles → optional
            if "null" in kinds:
                verbReg_Reciever(f"token_role_options: {token} // kinds: {kinds}")
                return [k for k in kinds if k != "null"] + [None]

            # normal token
            verbReg_Reciever(f"token_role_options: {token} // kinds: {kinds}")
            return list(kinds)

    def get_viable_verb(token, force_location=False):
        #print(f"GET VIABLE VERB: {token}")
        word = token.text
        if force_location:
            word="go"
        if word == "edit":
            word = "meta" # a nasty little shortcut here. Not ideal but it'll work for the moment.
        viable_instance = None
        if verbs.verbs.get(word):
            viable_instance = verbs.verbs[word]
        else:
            if verbs.by_alt_words.get(word):
                viable_instance = (verbs.by_alt_words[word][0])

        if not viable_instance:
            if "meta" in token.kind:
                print(f"VERBs.VERBS: {verbs.verbs}")
                viable_instance = verbs.verbs.get(word)
                return viable_instance
            print(f"Could not find viable instance for verb `{word}`. \nExiting immediately.")
            exit()
        return viable_instance

    def generate_initial_dict(tokens, sequences) -> tuple[dict, int]:
        reformed_dict = {}

        #if len(sequences) > 1:
            #print("More than one viable sequence. Help?")
            #print(sequences)
            #print("[This should be where it's culled down, right? Idk. Or maybe we just go with the first here and refine it later if it breaks. Idk yet. For now, just quit. Shouldn't be more than one I think.]")
            #exit()

        #sequence = sequences[0]
        full_matches = {}
        for i, sequence in enumerate(sequences):
            #print(f"Sequence: {sequence}")
            matched = 0
            for token in tokens:
                #print(f"TOKEN.KIND + TYPE: {token.kind}, {type(token.kind)}")
                if matched == len(sequence):
                    full_matches = reformed_dict
                    break
                if token.kind != {"null"} and token.kind != set():
                    if token.kind == {'adjective'} and token.idx >= 10:
                        reformed_dict[matched*10] = {"adjective": {"canonical": token.canonical, "text": token.text, "str_name": token.text}}
                    if sequence[matched] in token.kind:
                        #print(f"sequence[matched]: {sequence[matched]}, token.kind: {token.kind}")
                        #print(f"This is {token.kind}")
                        #print(Returning viable_sequencef"Token: {token}")

                        reformed_dict[matched] = {sequence[matched]: {"canonical": token.canonical, "text": token.text}}
                        #print(reformed_dict[matched])

                        matched += 1
                    else:
                        print(f"NO MATCH: sequence[matched]: {sequence[matched]}, token.kind: {token.kind}")
        #print(f"full matches: {full_matches}")
        if len(full_matches) > 1:
            print(f"More than one fully viable sequence:\n{full_matches}")
        elif len(full_matches) == 1:
            reformed_dict = full_matches
        #print(f"reformed_dict {reformed_dict}, sequence {sequence}")
        return reformed_dict, sequence

    def get_sequences_from_tokens(self, tokens) -> list:
        sequences = [[]]
        verb_instances = []
        meta_instances = []
        verb_entry = None
        strings = []
        canonical_nouns = dict()
        for i, token in enumerate(tokens):
            options = Parser.token_role_options(token)
            strings.append(token.canonical)
            if len(tokens) == 1 and not token.kind:
                return None, None
            #if not options:
            if not token.kind: # for things like 'waste time', which just don't give a kind to 'waste'.
                continue

            if len(tokens) in (1, 2):
                if list(token.kind)[0] in ("location", "direction"):
                    instance = Parser.get_viable_verb(token, force_location=True)
                    verb_instances.append({i:instance})
                if list(token.kind)[0] == "cardinal":
                    instance = Parser.get_viable_verb(token, force_location=True)
                    verb_instances.append({i:instance})

            if "verb" in options:
                instance = Parser.get_viable_verb(token)
                verb_instances.append({i:instance})
            if "meta" in options:
                meta_instances.append({i:token})
                if token.text == "inventory":
                    token.kind.add("location")

            if "noun" in options:
                canonical_nouns[token.canonical] = i


            new_sequences = []

            for seq in sequences:
                #print(f"seq: {seq} // sequences: {sequences}")
                for opt in options:
                    if opt is None:
                        new_sequences.append(seq)
                    else:
                        new_sequences.append(seq + [opt])
                    #print(f"after opt({opt}): {new_sequences}")

            sequences = new_sequences
        #test_print(f"Sequences: {sequences}", print_true=True)

        if not verb_instances:
            if not meta_instances:
                #print("No verb_instance or meta_instance found in get_sequences_from_tokens. Returning None.")
                #print(f"TOKENS: {tokens}")
                return None, None, tokens

        if verb_instances and len(verb_instances) > 1:
            #print(f"VERB INSTANCES[0]: {verb_instances[0]} \nSequences: {sequences}\n") # have to add newlines so it doesn't get overlapped by the input text.
            if list(('verb', 'noun', 'direction', 'verb', 'noun')) in sequences:
                #print("       That pattern exists.\n")
                new_seq = ["verb", "noun", "sem", "noun"] # new_verb, noun with noun2 == use noun2 to verb noun
                sequences.append(new_seq)
                ## So I need to fix the instances before it goes forward, because it needs to output a sequence viable with unlock, not use.
        #print(f"verb instances: {verb_instances}")
        #print(f"meta instances: {meta_instances}")
        def run_sequences(sequences, verb_instances):
            viable_sequences = []
            #for verb_entry in verb_instances:
                #for verb in verb_entry.values():
                    #if hasattr(verb, "formats"):
                        #print(f"\nVERB FORMATS: {verb.formats}\n")

            for seq in sequences:
                if seq:
                    #print(f"SEQ: {seq}, type: {type(seq)}")
                    if verb_instances:
                        for verb_entry in verb_instances:
                            for verb in verb_entry.values():
                                if tuple(seq) in verb.formats and seq not in viable_sequences:
                                    viable_sequences.append(seq)
                                elif seq in viable_sequences and seq not in viable_sequences:
                                    viable_sequences.append(seq)
                                #else:
                                    #print(f"SEQ is not in verb.formats: {tuple(seq)} // verb formats: {verb.formats}")
                    #print("before meta_instances")
                    elif meta_instances:
                        for entry in meta_instances:
                            for verb in entry.values():
                                if tuple(seq) in verb.kind and seq not in viable_sequences:
                                    viable_sequences.append(seq)
                                elif set(seq) == verb.kind and seq not in viable_sequences:
                                    viable_sequences.append(seq)
                                elif isinstance(seq, list) and len(seq) == 1: ## Added to allow 'meta' to work. Not sure why it was needed, though.
                                    #print("is seq list and len == 1")
                                    if seq[0] in verb.kind:
                                        viable_sequences.append(seq)

                        if not viable_sequences:
                            meta = meta_instances[0]
                            #print(f"META: {meta}")
                            token = meta[list(meta)[0]] # only works if the meta is the first entry.
                            instance = Parser.get_viable_verb(token)
                            if hasattr(instance, "formats"):
                                if tuple(seq) in instance.formats:
                                    viable_sequences.append(seq)
            #print(f"Returning viable_sequences: {viable_sequences}\n")
            return viable_sequences

        for seq in sequences:
            if "noun, noun" in str(seq) or "'noun', 'noun'" in str(seq):
                #print(f"'noun', 'noun' in seq: {seq}")
                if canonical_nouns:
                    #print(f"Canonical_nouns: {canonical_nouns}")
                    if len(canonical_nouns) == 2:
                        bad_noun = good_noun = None
                        for word in canonical_nouns:
                            #print(f"val: {canonical_nouns[word]}, type: {type(canonical_nouns[word])}")
                            if word == "assumed_noun":
                                bad_noun = word
                            else:
                                good_noun = word
                        if bad_noun and good_noun and bad_noun == "assumed_noun" and good_noun != "assumed_noun":
                            #print(f"good noun: {good_noun}. bad noun: {bad_noun}")
                            for token in tokens:
                                if token.idx == canonical_nouns[bad_noun]:
                                    bad_token = token
                                    bad_text = token.text
                                if token.idx == canonical_nouns[good_noun]:
                                    good_token = token
                                    good_text = token.text

                            token = bad_token
                            if token:
                                idx = token.idx
                                if good_token:
                                    bad_token.idx = idx * 10
                                    bad_token.kind = set(("adjective",))
                                    #tokens.remove(token) # want to avoid this. Doing the idx*10 + kind == adjective to avoid. Not perfect though.
                                    if good_token.idx > idx:
                                        good_token.text = bad_text + " " + good_text
                                    else:
                                        good_token.text = good_text + " " + bad_text

                                    good_token.idx = idx
                                    #print(f"TOKENS AFTER: {tokens}")
                                    sequence = []
                                    for token in tokens: ## NOTE: This may have terrifying unintented outcomes. Replace it with something better and less descructive, and hopefully earlier in the process. Maybe we just add a list of adjectives that are optional if not present (burned, broken, etc, that are treated like null if not found.)
                                        #print(f"token.kind type: {type(token.kind)}")
                                        if token.idx != (idx * 10):
                                            sequence.append(list(token.kind)[0])
                                    sequences = list()
                                    sequences.append(sequence)
        #print(f"SEQUENCES before run_sequences: {sequences}")
        viable_sequences = run_sequences(sequences, verb_instances)
        if not viable_sequences:
            #print(f"not viable sequences: SEQUENCES: {sequences}")
            if "inventory" in strings and ("in" in strings or "at" in strings):
                new_seq = list(sequences[0])
                new_seq.remove("meta")
                new_seq.append('location')
                #print(f"NEW SEQ: {new_seq}")
                #exit()
                sequences.append(new_seq)

                viable_sequences = run_sequences(sequences, verb_instances) # why did I run this twice on the mainline?
        verbReg_Reciever(f"return for sequences: viable sequences: {viable_sequences}, verb_instances: {verb_instances}, sequences: {sequences}")
        return [tuple(seq) for seq in viable_sequences if seq], verb_instances, tokens

    def resolve_verb(tokens, verb_name, format_key) -> tuple[VerbInstance|str]:

        #print(f"Format key: {format_key}")
        items = verbs.by_format.get(format_key) # gets verb names that match the format key

        #print(f"Items: {items}")
        #print("by alt words: ", verbs.by_alt_words.get(verb_name))
        if items and verb_name in items:
            verb_obj = verbs.verbs.get(verb_name)
            if not verb_obj:
                verb_obj = verbs.by_alt_words.get(verb_name)[0] ## Currently just takes the first. I think this is fine for now, later would like to set some minor refinement rules (such as the 'if 'fire' in noun token, then 'burn' instead of 'place' if 'burn' in by_alt_words options. But for now this is fine.)
            #print(f"verb_obj: {verb_obj}")
            #print("verb_obj.name: ", verb_obj.name)
            if verb_obj:
                #print(f"verb obj name: {verb_obj.name}")
                #verb_token = [i for i in tokens if i.text == verb_name]
                #print(f"Verb token: {verb_token}")
                #test_print(f"Winning format: {format_key}", print_true=True)
                return verb_obj, format_key ## currently returns once it has a single success. Again, works as long as there's only one verb. For now, is fine.

            else:
                print(f"Could not find verb obj for {verb_name}")

        else:
            verb_obj = verbs.by_alt_words.get(verb_name)[0]
            #print(f"verb_obj: {verb_obj}")
            if verb_obj and verb_obj.name in items:
                #print("verb obj and verb_obj.name in items == true")
                return verb_obj, format_key
            else:
                print(f"verb obj is {verb_obj} with name `{verb_obj.name}` but not in items: {items}")
        return None, format_key

    def build_dict(confirmed_verb, tokens, initial_dict, format_key):

        """
        Need to change this a bit -- I need to ensure the original typed name is kept, currently it's wiped and I'm relying on the verb_instance name only, which won't work if they type a variation that has connotations. I need to be able to branch out from the primary function into more detailed actions (or just response strings).
        """

        dict_for_output = initial_dict
        #print(f"Format key: {format_key}")
        for i, item in enumerate(format_key):
            #print(f"Word type: {item}, type: {type(item)}")
            #print(f"Initial dict[i]: {initial_dict[i]}")
            item_name = initial_dict[i][item].get("canonical")
            if item == "verb":
                verb, _ = Parser.resolve_verb(tokens, item_name, format_key)
                #resolve_verb(tokens, verb_name, format_key)
                if verb:
                    #print(f"Verb::: {verb}, verb_name: {verb.name}")
                    #dict_for_output[i]={item: verb}
                    dict_for_output[i]={item: {"instance":verb, "str_name":item_name, "text": initial_dict[i][item].get("text")}}

            else:
                #print(f"{initial_dict[i]}")
                dict_for_output[i]={item:{"instance":None, "str_name":item_name, "text": initial_dict[i][item].get("text")}}

        return dict_for_output, tokens # including tokens for any minor input detail that might matter later.

    def reorder_tokens_to_sequence(tokens, sequence):
        logging_fn()
        sequences = list(())
        no_verb = no_noun = True
        verb1 = verb2 = noun1 = noun2 = direction = None
        for token in tokens:
            #print(f"TOKEN: {token}, vars: {vars(token)}")
            if "verb" in token.kind:
                if no_verb:
                    if token.text != "use":
                        print("This should only be used for `use` x to verb y. It probably won't work with anything else.")
                    verb1 = token
                    no_verb = False
                else:
                    verb2 = token
            if "direction" in token.kind:
                direction = token

            if "noun" in token.kind:
                if no_noun:
                    noun1 = token
                    no_noun = False
                else:
                    noun2 = token

        if direction.text == "to" and verb1.text == "use":
            #print("use + to  confirmed")
            if noun1 and noun2:
                #print("Two nouns confirmed.")
                sequences.append(sequence)

        if not (direction.text == "to" and verb1.text == "use" and noun1 and noun2):
            return None, None, False # Return if it doesn't meet the minimums.

        verb1_idx = verb1.idx
        #print(f"TOKENS type: {type(tokens)}")
        verb2.idx = verb1_idx
        noun2.idx = noun2.idx - 1


        def sort_tokens(counter, token, verb1):
            #print(f"sort_tokens({counter}, {token})")
            if token != verb1 and token.idx == counter:
                if "direction" in token.kind:
                    #print("direction in token kind")
                    token.text = "with"
                    token.str_name = "with"
                    token.canonical = "with"
                    token.kind.remove("direction")
                    token.kind.add("sem")
                #print(f"Token is not verb1 and counter == counter: {token} // counter == {counter} ")
                counter += 1
                #print(f"token in tokens at end: {token}")
                return token, counter
            else:
                #print(f"token == verb or token idx != counter: {token}, counter: {counter}")
                return None, counter

        counter = 0
        new_tokens = list()
        recursion_counter = 0
        while len(new_tokens) < len(sequence):
            if recursion_counter > len(tokens):
                #print("Ending due to recursion limiter.")
                break
            for token in tokens:
                test, counter = sort_tokens(counter, token, verb1)
                #print(f"After sort_tokens: {test} // {counter}")
                if test:
                    new_tokens.append(test)
            recursion_counter += 1
            #print(f"Length of new_tokens: {len(new_tokens)}, new_tokens: {new_tokens}")
        #print(f"If new tokens: {new_tokens}")
        if len(new_tokens) == len(sequence):
            tokens = new_tokens

        #print(f"sequence: {sequence}, type: {type(sequence)}. Print sequences: {sequences}/ tokens on leaving reorder: {tokens}")
        return tokens, sequences, True if sequences else False

        ## must make sequence a list inside a list before returning


    def input_parser(self, input_str):
        logging_fn()
        from verb_membrane import membrane

        from interactions.item_interactions import find_local_item_by_name
        local_nouns = find_local_item_by_name()
        clean_nouns  = {}
        if not local_nouns:
            clean_nouns = dict()
        else:
            for item in local_nouns: # make this a fn to reuse for all plural gets.
                clean_nouns[item.name] = item
                if " " in item.name:
                    if not membrane.plural_words_dict.get(item.name):
                        parts = item.name.split(" ")
                        membrane.plural_words_dict[item.name] = tuple(parts)

        membrane.local_nouns = clean_nouns

        tokens = self.tokenise(input_str, membrane)

        if not tokens:
            return None, None
        verbReg_Reciever(f"Tokens after tokenise: {tokens}")
        #print(f"Tokens: {tokens}")
        if isinstance(tokens, tuple):
            word_str, part2 = tokens
            #print(f"part 1: {word_str}, part2: {part2}")
            if part2 == "No match":
                return word_str, None

        verbReg_Reciever(f"tokens before sequencer: {tokens}")
        sequences, verb_instances, tokens = self.get_sequences_from_tokens(self, tokens)
        verbReg_Reciever(f"sequences after sequencer: {sequences}")
        #print(f"SEQUENCES: {sequences}/tokens: {tokens}")
        if not sequences:
            #print(f"FAILURE IN SEQUENCES: {tokens}")
            from misc_utilities import print_failure_message
            print_failure_message(input_str=input_str)
            return None, None

            #TODO:  If no functional sequences, need to pick out parts that might be applicable to make reasonable guesses. Like if we have 'go'  and 'location', 'did you mean 'go to location', etc. Need a way to pause mid-parse, get confirmation then come back and run the sequencer again. Not today, but soon.

        token_count = len([i for i in tokens if i.kind != {"null"} and i.kind != set()])

        length_checked_sequences = []
        for sequence in sequences:
            if len(sequence) == token_count:
                length_checked_sequences.append(sequence)
        if not length_checked_sequences and len(sequences) == 1:
            length_checked_sequences = sequences # may make things fail unexpectedly, but allows for 'failed' words to be attributed as nouns if the sequence would be correct without them (eg 'burned book' if there's a book but not a burned one. Not sure if I want this or not but that's what it is for now.)

        for seq in length_checked_sequences:
            if seq == tuple(('verb', 'noun', 'sem', 'noun')) and len(tokens) == 5 and len(verb_instances) == 2:
                # use x to verb y switcharoo time.
                #print("Going to reorder_tokens_to_sequence")
                test_tokens, test_length_checked_sequences, success = self.reorder_tokens_to_sequence(tokens, seq)
                if success:
                    tokens = test_tokens
                    length_checked_sequences = test_length_checked_sequences
                    break

        initial_dict, sequence = Parser.generate_initial_dict(tokens, length_checked_sequences) # culls to just the first sequence. Doesn't deal with 'picking the best version' if there's more than one yet. Needs to in the future.
        #print(f"About to go to build_dict: {initial_dict}\n")
        dict_for_output, tokens = self.build_dict(verb_instances, tokens, initial_dict, sequence)
        #print(f"dict for output; {dict_for_output}\n")
        return sequence, dict_for_output

    # -------------


verbs = VerbRegistry()

colours = ["BLACK","RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]
sizes = ["big", "small", "tiny", "enormous", "massive", "little"]

def initialise_verbRegistry():

    from verb_definitions import get_verb_defs, allowed_null, semantics, formats, meta_verbs, null_sem_combinations

    verb_defs_dict, verb_set = get_verb_defs()
    verbs.all_verbs = verb_set
    verbs.meta_verbs = meta_verbs
    verbs.all_meta_verbs = set(meta_verbs)
    for meta in meta_verbs:
        if "alt_words" in meta_verbs[meta]:
            for alt_word in meta_verbs[meta]["alt_words"]:
                verbs.all_meta_verbs.add(alt_word)
    verbs.formats = set(formats.values())
    verbs.adjectives = set(i.lower() for i in colours) | set(i.lower() for i in sizes)

    verbs.semantics = set(i for i in semantics)
    verbs.list_null_words = allowed_null
    verbs.cardinals = set(("north", "south", "east", "west"))
    verbs.null_sem_combinations = null_sem_combinations

    from itemRegistry import registry

    verbs.compound_words = registry.plural_words

    for item_name, attr in verb_defs_dict.items():
        verbs.create_verb_instance(item_name, attr)

        if attr.get("null_words"):
            for word in attr.get("null_words"):
                if word.lower() != None:
                    verbs.list_null_words.add(word)

    split_dict = {}
    for word in verbs.all_verbs:
        if " " in word:
            parts = word.split(" ")
            split_dict[parts[0]] = {verbs.verbs.get(word)}

    if split_dict:
        verbs.split_verbs = split_dict


