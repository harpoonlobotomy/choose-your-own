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

    def check_compound_words(parts_dict, word, parts, idx, kinds, word_type, omit_next, local_named):
        logging_fn()

        #print(f"\nCHECK COMPOUND WORDS: {word_type}\n")
        #print(f"omit_next at top of compound_words: {omit_next}")
        canonical = potential_match = perfect_match = None
        compound_match = 0
        compound_matches = {}
        #if not word.startswith("a "):
            #word = "a " + word
        #print(f"WORD: {word}, PARTS: {parts}")
        #print(f"parts dict:: type: {type(parts_dict)}")
        for compound_word, word_parts in parts_dict.items():
            if perfect_match:
                break
            #print(f"Word: {word} // word parts: {word_parts}")
            if word in word_parts:
                #print(f"word {word} in word parts: {word_parts}")
                #test_print(f"MATCH IN PLURAL WORDS: `{word}` FOR COMPOUND WORD: {compound_word}", print_true=True)
                matches_count = 0
                for i, bit in enumerate(word_parts):
                    try:
                        #print(f"bit: {bit}, i+matches_count: {i+matches_count}, parts[idx + matches_count]: {parts[idx + matches_count]})")
                        #if len(parts) <= idx + matches_count and bit == parts[idx+matches_count]:
                        if len(parts) > idx + matches_count and bit == parts[idx+matches_count]:
                            matches_count += 1
                            #print(f"Matches_count: {matches_count}")
                            if matches_count == len(word_parts):
                                perfect_match = compound_word
                                break

                    except Exception as e:
                        print(f"Failed: {e}")
                        print(f"No matched word-parts after parts[{idx}+{matches_count}].")
                        break
                compound_match += 1
                compound_matches[compound_word]=tuple(((compound_match, len(word_parts)))) ## if input == 'paper scrap': "paper scrap with paper":(2,4)

        if len(compound_matches) == 1 or perfect_match:
            #print(f"list compound_matches: {list(compound_matches)}")
            if perfect_match:
                canonical = perfect_match
            else:
                canonical = list(compound_matches)[0] ## just add it if it's the only possible match, for now. Make it more rigorous later, but this'll catch most cases.
            if isinstance(kinds, str):
                if kinds == "No match":
                    kinds = set()
            kinds.add(word_type)
            potential_match=True
            omit_next += matches_count-1 ## Skip however many successful matches there were, so we don't re-test words confirmed to be part of the compound word.
            return idx, word, kinds, canonical, potential_match, omit_next, perfect_match


        elif compound_match > 1: ## TODO make this better.
            if perfect_match:
                #print(f"PERFECT MATCH: {perfect_match}")
                canonical = perfect_match
                if isinstance(kinds, str):
                    kinds = set()
                kinds.add(word_type)
                potential_match=True
                omit_next += matches_count
                return idx, word, kinds, canonical, potential_match, omit_next, perfect_match

            #print("More than one compound match")
            matches = set()
            match = None
            #print(f"Compound matches: {compound_matches}")

            for item_name in compound_matches: # this just takes the first match, so if 'gold key' and 'iron key' are both there, it will take gold key regardless.
                #print(f"item name in compound matches: {item_name}")
                matches.add(item_name)
                match = item_name

            if not match and len(matches) > 1:
                print("There are multiple items here you could be talking about. Please enter which one you mean:")
                items = ', '.join(matches)
                print_green(items)
                test = input()
                if test in matches:
                    match = test
            else:
                 for item in compound_matches: # this just takes the first match, so if 'gold key' and 'iron key' are both there, it will take gold key regardless.
                    #print(f"item in compound matches: {item}")
                    if local_named and item in local_named:
                        #print(f"item in local_named: {item}")
                        if item in parts_dict:
                            #print(f"item in parts_dict: {item}")
                            compound_word, word_parts in parts_dict.get(item) # what is this even here for. Honestly. It does nothing.
                        match = item
                        break

            if match:
                canonical = match
                kinds.add(word_type)
                potential_match=True
                omit_next += matches_count -1

            else:
                if not matches:
                    print(f"Nothing found here by the name \033[1;33m`{word}`\033[0m.")
                    return idx, word, "No match", canonical, potential_match, omit_next, perfect_match
                print(f"Compound matches: {compound_match}")
                print(f"Content: {compound_matches}")
                print_red("More than one potential compound match, the system can't cope with that yet.")
        "idx, word, kinds, canonical, potential_match, omit_next, perfect_match: {idx, word, kinds, canonical, potential_match, omit_next, perfect_match}"
        return idx, word, kinds, canonical, potential_match, omit_next, perfect_match

    def tokenise(input_str, nouns_list, locations, directions, cardinals, membrane):

        current_location = get_current_loc()
        word_phrases = membrane.combined_wordphrases
        parts = input_str.split()
        loc_options = locations
        compound_locs = membrane.compound_locations
        compound_nouns = membrane.plural_words_dict
        items = nouns_list
        local_items = membrane.local_nouns
        tokens = []
        omit_next = 0

        initial = verbs.list_null_words | set(directions) | set(loc_options) | verbs.semantics | cardinals

        #print(f"initial: {initial}")

        for idx, word in enumerate(parts):
            word = word.lower()
            kinds = set()
            potential_match=False
            verbReg_Reciever(f"Tokenise: idx: {idx}, word: {word}, omit_next: {omit_next}")
            if omit_next >= 1: # shouldn't this be >=, not ==? Surely if omit_next == 1, we need to omit once...
                omit_next -= 1
                continue

            else:
                canonical = None

                if word in verbs.all_meta_verbs:
                    #print(f"word in verbs.all_meta_verbs: {word}")
                    if word not in verbs.meta_verbs:
                        #print("word not in meta_verbs")
                        for key_word in verbs.meta_verbs:
                            if verbs.meta_verbs[key_word].get("alt_words"):
                                for alt_word in verbs.meta_verbs[key_word]["alt_words"]:
                                    if word == alt_word:
                                        #print(f"word in verbs.meta_verbs[key_word]: {word}, key word: {key_word}")
                                        word = key_word
                                        kinds.add("meta")
                                        canonical = word
                    else:
                        #print(f"word in meta_verbs: {word}")
                        kinds.add("meta")
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
                    idx, word, kinds, canonical, potential_match, omit_next, perfect = Parser.check_compound_words(parts_dict = compound_nouns, word=word, parts=parts, idx=idx, kinds=kinds, word_type = "noun", omit_next=omit_next, local_named=local_items)
                    second_perfect = None
                    #print(f"omit_next after first check compound words: {omit_next}")
                    try:
                        second_idx, second_word, second_kinds, second_canonical, second_potential_match, second_omit_next, second_perfect = Parser.check_compound_words(parts_dict = compound_locs, word=word, parts=parts, idx=idx, kinds=kinds, word_type = "location", omit_next=omit_next, local_named=local_items)
                    except Exception as e:
                        print(f"Could not get location: {e}")

                    #print(f"omit_next after second check compound words: {omit_next}")

                    if perfect and not second_perfect:
                        kinds = (("noun",))
                        tokens.append(Token(idx, word, kinds, canonical))
                        continue
                    #    tokens.append(Token(idx, word, kinds, canonical))
                    #    continue

                    elif second_perfect and not perfect:
                        kinds = (("location",)) # made this but was still adding second_kinds. bleh.
                        tokens.append(Token(second_idx, second_word, kinds, second_canonical))
                        omit_next = second_omit_next
                        continue
                    #    tokens.append(Token(second_idx, second_word, second_kinds, second_canonical))
                    #
#
                    #elif perfect and second_perfect:
                    #    #print(f"Perfect for both noun and location: help? {idx}, {word} // {kinds}/{second_kinds} // {perfect} / {second_perfect} // {canonical} / {second_canonical}")
                    #    #exit() # arbitrarily setting this to location.
                    #    kinds = (("location",))
                    #    tokens.append(Token(second_idx, second_word, second_kinds, second_canonical))
                    #if perfect:
                        #print(f"Perfect: idx: {idx}, word: {word}, canonical: {canonical}")
                        #tokens.append(Token(idx, word, kinds, canonical))
                        #continue

                    if canonical:
                        #print(f"CANONICAL AFTER PERFECT CHECKS: {canonical}")
                        tokens.append(Token(idx, word, kinds, canonical))
                        continue

                    if (not canonical and second_canonical) or (perfect and second_perfect):
                        idx = second_idx
                        word = second_word
                        kinds = second_kinds
                        canonical = second_canonical
                        potential_match = second_potential_match
                        omit_next = second_omit_next
                        tokens.append(Token(idx, word, kinds, canonical))
                        continue

                    #if canonical and not second_perfect:

                    if not canonical:
                        verbReg_Reciever(f"Tokenise: idx: {idx}, word: {word}, not canonical")
                        if kinds == "No match":
                            return word, kinds

                        from config import add_new_words_if_missing
                        if not add_new_words_if_missing:
                            #MOVE_UP = "\033[A"
                            #print(f"{MOVE_UP}\033[1;31m[ Couldn't find anything to do with the input `{input_str}`, sorry. ]\033[0m")
                            continue
                        print(f"No canonical for idx `{idx}`, word `{word}`")
                        print("Please enter a word type if you would like to add a new noun/verb/location")
                        test = input()
                        if test in ("noun", "verb", "location", "loc"):
                            if test == "location" or test == "loc":
                                from generate_locations import generate_new_location
                                generate_new_location(word)
                                #import json
                                #temp_defs = "dynamic_data/temp_defs.json"
                                #with open(temp_defs, 'r') as file:
                                #    temp_def_dict = json.load(file)
                                #    temp_def_dict[word] = new_dict#({"kinds":["location"], "canonical": word})
                                #with open(temp_defs, 'w') as file:
                                #    json.dump(temp_def_dict, file, indent=2)

                            tokens.append(Token(idx, word, [test], word))
                            continue

                    #print(f"verbs.compound_words: {verbs.compound_words}")

                        ## Set up a fn where it tests the results tuple of compound_word, whichever compound_word in compound_matches has the best ration of (matches, total_parts) wins.)
                        ## If multiple options and all have same ratio, then we take the longest. So, 'blue glass jar, glass jar and jar' might all successfully match for separate jar-type items. But even if 'glass jar', 'blue glass jar' and 'jar' are legit entities, 'blue glass jar' wins if all three are matched. So first get match-ratio, then if no winner, get matched-length. There'll most likely only be one potential winner but good to have the system in place.

            if not potential_match:
                test_print(f"No full match found for parts in `{input_str}`.")

        return tokens


    def token_role_options(token) -> list:

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
                if matched == len(sequence):
                    full_matches = reformed_dict
                    break
                if token.kind != {"null"} and token.kind != set():
                    if sequence[matched] in token.kind:
                        #print(f"sequence[matched]: {sequence[matched]}, token.kind: {token.kind}")
                        #print(f"This is {token.kind}")
                        #print(f"Token: {token}")

                        reformed_dict[matched] = {sequence[matched]: {"canonical": token.canonical, "text": token.text}}
                        #print(reformed_dict[matched])

                        matched += 1
                    #else:
                        #print(f"NO MATCH: sequence[matched]: {sequence[matched]}, token.kind: {token.kind}")

        if len(full_matches) > 1:
            print(f"More than one fully viable sequence:\n{full_matches}")
        elif len(full_matches) == 1:
            reformed_dict = full_matches
        #print(f"reformed_dict {reformed_dict}, sequence {sequence}")
        return reformed_dict, sequence

    def get_sequences_from_tokens(tokens) -> list:
        sequences = [[]]
        verb_instances = []
        meta_instances = []
        verb_entry = None
        strings = []
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
                return None, None

        #print(f"verb instances: {verb_instances}")
        #print(f"meta instances: {meta_instances}")
        if len(verb_instances) == 1:
            verb_entry = verb_instances


        def run_sequences(sequences, verb_instances):
            viable_sequences = []
            #for verb_entry in verb_instances:
                #for verb in verb_entry.values():
                    #if hasattr(verb, "formats"):
                        #print(f"VERB FORMATS: {verb.formats}")

            for seq in sequences:
                if seq:
                    #print(f"SEQ: {seq}")
                    if verb_instances:
                        for verb_entry in verb_instances:
                            for verb in verb_entry.values():
                                if tuple(seq) in verb.formats and seq not in viable_sequences:
                                    viable_sequences.append(seq)
                                elif seq in viable_sequences and seq not in viable_sequences:
                                    viable_sequences.append(seq)
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

            return viable_sequences
        #if not viable_sequences:
        #    for seq in sequences:
        #        seq = str(seq)
        #        print(f"seq: {seq}")
        #        if "'direction', 'sem'" in seq:
        #            dir_text = sem_text = None
        #            for token in tokens:
        #                if "direction" in token.kind:
        #                    dir_text = token.text
        #                if "sem" in token.kind:
        #                    sem_text = token.text
#
        #            if dir_text and sem_text:
        #                print(f"dir_text: {dir_text}, sem_text: {sem_text}")
        #            print("Direction, sem in seq")

        viable_sequences = run_sequences(sequences, verb_instances)
        if not viable_sequences:
            #print(f"SEQUENCES: {sequences}")
            if "inventory" in strings and ("in" in strings or "at" in strings):
                new_seq = list(sequences[0])
                new_seq.remove("meta")
                new_seq.append('location')
                #print(f"NEW SEQ: {new_seq}")
                #exit()
                sequences.append(new_seq)

        viable_sequences = run_sequences(sequences, verb_instances)
        verbReg_Reciever(f"return for sequences: viable sequences: {viable_sequences}, verb_instances: {verb_instances}, sequences: {sequences}")
        return [tuple(seq) for seq in viable_sequences if seq], verb_instances

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

    def input_parser(self, input_str):
        logging_fn()
        from verb_membrane import membrane

        all_nouns_list = membrane.nouns_list # swapping these out so it only considers local nouns. Keeping the orignal here as all_ in case it breaks things.
        nouns_list = membrane.nouns_list
        locations = membrane.locations
        directions = membrane.directions
        cardinals = membrane.cardinals

        membrane.get_local_nouns()

        tokens = self.tokenise(input_str, nouns_list, locations, directions, cardinals, membrane)
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
        sequences, verb_instances = self.get_sequences_from_tokens(tokens)
        verbReg_Reciever(f"sequences after sequencer: {sequences}")

        if not sequences:
            MOVE_UP = "\033[A"
            print(f"{MOVE_UP}\033[1;31m[ Couldn't find anything to do with the input `{input_str}`, sorry. <after get_sequences_from_tokens>]\033[0m")
            clean_parts = []
            token_parts = [i.kind for i in tokens if i.kind != "null"]
            for parts in token_parts:
                if isinstance(parts, str):
                    clean_parts.append(parts)
                else:
                    for part in parts:
                        if part != "null":
                            clean_parts.append(part)
                            break

            #print(" ".join(clean_parts))
            #print(f"Raw tokens: {tokens}")
            return clean_parts, None

            #TODO:  If no functional sequences, need to pick out parts that might be applicable to make reasonable guesses. Like if we have 'go'  and 'location', 'did you mean 'go to location', etc. Need a way to pause mid-parse, get confirmation then come back and run the sequencer again. Not today, but soon.

        token_count = len([i for i in tokens if i.kind != {"null"} and i.kind != set()])

        length_checked_sequences = []
        for sequence in sequences:
            if len(sequence) == token_count:
                length_checked_sequences.append(sequence)

        initial_dict, sequence = Parser.generate_initial_dict(tokens, length_checked_sequences) # culls to just the first sequence. Doesn't deal with 'picking the best version' if there's more than one yet. Needs to in the future.

        dict_for_output, tokens = self.build_dict(verb_instances, tokens, initial_dict, sequence)
        #print(f"dict for output; {dict_for_output}")
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
    verbs.null_sem_combinations

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


