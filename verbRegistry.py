## Going to rename this one to make it 'string_parser' or similar. The verbs don't live here, the string is just tokenised and formalised using the wordlists.

#Note for future me: 'meta_commands' is where all meta actions are directed to. 'meta' + <noun/loc/card>' or just <meta> will trigger meta_commands.

import uuid

from dataclasses import dataclass
from typing import Optional

#import generate_locations
from printing import print_green, print_red
from verb_actions import get_current_loc

print("Verb registry is being run right now.")

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

    def __repr__(self):
        return f"<verbInstance {self.name} ({self.id})>"

class VerbRegistry:
    """
    Central manager for all verb instances.
    Also keeps a lookups for all-verbs, standardised text-parts, formats.
    """

    def __init__(self):

        self.verbs = {}      # id -> VerbInstance
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

    def check_compound_words(parts_dict, word, parts, idx, kinds, word_type, omit_next):

        canonical = potential_match = None
        compound_match = 0
        compound_matches = {}
        #if not word.startswith("a "):
            #word = "a " + word
        #print(f"parts dict:: type: {type(parts_dict)}")
        for compound_word, word_parts in parts_dict.items():
            if word == "tv":
                word = "TV"
            #print(f"Word: {word} // word parts: {word_parts}")
            if word in word_parts:
                #test_print(f"MATCH IN PLURAL WORDS: `{word}` FOR COMPOUND WORD: {compound_word}", print_true=True)
                matches_count = 1
                for _ in word_parts:
                    try:
                        if parts[idx+matches_count] and parts[idx+matches_count].lower() in word_parts:
                            #test_print(f"parts[{idx}+{matches_count}]: {parts[idx+matches_count]}", print_true=True)
                            matches_count += 1
                        elif parts[idx+matches_count].lower() == "magazine" and "mag" in word_parts: # hardcoded for magazines, they're an odd one.
                            #TODO: later, put something like this in for general shorthand.
                            #test_print(f"parts[{idx}+{matches_count}]: {parts[idx+matches_count]}")#, print_true=True)
                            matches_count += 1

                        #else:
                            #print(f"parts[idx+matches_count]: {parts[idx+matches_count].lower()}")
                            #print(f"Part {matches_count+1} `{parts[idx+matches_count+1]}` does not match expected second word {word_parts[matches_count+1]}")
                    except:
                        test_print(f"No matched word-parts after parts[{idx}+{matches_count}].", print_true=False)
                        break
                compound_match += 1
                compound_matches[compound_word]=tuple(((compound_match, len(word_parts)))) ## if input == 'paper scrap': "paper scrap with paper":(2,4)

        if compound_match == 1:
            #print(f"list compound_matches: {list(compound_matches)}")
            canonical = list(compound_matches)[0] ## just add it if it's the only possible match, for now. Make it more rigorous later, but this'll catch most cases.
            kinds.add(word_type)
            potential_match=True
            omit_next = matches_count ## Skip however many successful matches there were, so we don't re-test words confirmed to be part of a compound word.
            #print("omit_next: ", omit_next)

        elif compound_match > 1: ## TODO make this better.
            from itemRegistry import registry
            from env_data import locRegistry
            from set_up_game import game
            inventory = game.inventory
            current_loc = locRegistry.current
            current_loc_items = registry.get_item_by_location(current_loc)
            local_named = set()
            matches = set()
            match = None
            if inventory:
                for item in inventory:
                    local_named.add(item.name)
            if current_loc_items:
                for item in current_loc_items:
                    local_named.add(item.name)

            for item_name in compound_matches: # this just takes the first match, so if 'gold key' and 'iron key' are both there, it will take gold key regardless.
                #print(f"item name in compound matches: {item_name}")
                #print(f"local named (all): {local_named}")
                if item_name in local_named:
                    #print(f"Item name in local_named: {item_name}")
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
                    if item in local_named:
                        match = item
                        break

            if match:
                canonical = match
                kinds.add(word_type)
                potential_match=True
                omit_next = matches_count

            else:
                print(f"Compound matches: {compound_match}")
                print(f"Content: {compound_matches}")
                print_red("More than one potential compound match, the system can't cope with that yet.")

        return idx, word, kinds, canonical, potential_match, omit_next

    def tokenise(input_str, nouns_list, locations, directions, cardinals, membrane):

        current_location = get_current_loc()
        word_phrases = membrane.combined_wordphrases
        #print(f"Word phrases: {word_phrases}")
        parts = input_str.split()
        loc_options = locations
        compound_locs = membrane.compound_locations
        #print(f"compound_locs: {compound_locs}")
        compound_nouns = membrane.plural_words_dict
        #print("compound nouns:")
        #print(compound_nouns)
        #exit()

        #for word in locations:
        #    compound_locs[word] = tuple(word.split())
        items = nouns_list
        #print(f"nouns list: {items}")
        tokens = []
        omit_next = 0

        #print("verbs.semantics: ", verbs.semantics)
        initial = verbs.list_null_words | set(directions) | set(loc_options) | verbs.semantics | cardinals

        #print(f"verbs.null words: {verbs.list_null_words}")

        for idx, word in enumerate(parts):
            word = word.lower()
            kinds = set()
            potential_match=False

            #test_print(f"idx {idx}, word: {word}", print_true=True)
            if omit_next > 1:
                #print(f"Skipping word part {idx} because it is a part match for {canonical}")
                #print(f"Omit next: {omit_next}")
                omit_next -= 1
                continue

            else:
                canonical = None # reset to None here just so I can test_print the prior 'canonical' for word parts.
                #print(f"idx {idx}, word: {word}")

                if word in verbs.all_meta_verbs:
                    if word not in verbs.meta_verbs:
                        for key_word in verbs.meta_verbs:
                            #print(f"key_word: {key_word}, type: {type(key_word)}")
                            if word in verbs.meta_verbs[key_word].get("alt_words"):
                                word = key_word
                                kinds.add("meta")
                                canonical = word
                    else:
                        kinds.add("meta")
                        canonical = word

                elif word in initial or f"a {word}" in initial:
                    #print(f"Word in initial: {word}")
                    if word in word_phrases and (word_phrases.get(word) and parts[0] in word_phrases.get(word)):
                        #print(f"canonical in word phrases: {canonical}")
                        #print(f"Parts: {parts}")
                        #print(word_phrases.get(word))
                        kinds.add("null")
                        canonical = word
                        #print(f"canonical: {canonical}")
                        #exit()
                    #print(f"Word after word phrases: {canonical}")
                    if word in verbs.semantics:
                        #print(f"canonical in semantics: {canonical}")
                        kinds.add("sem")
                        canonical = word
                    elif word in verbs.list_null_words:
                        #print(f"null word: {word}")
                        kinds.add("null")
                        canonical = word

                    else:
                        if word in cardinals:
                            kinds.add("cardinal")
                            canonical = word

                        if word in directions:
                            kinds.add("direction")
                            canonical = word

                        if word in loc_options or f"a {word}" in loc_options:
                            if word in current_location or f"a {word}" in current_location:
                                canonical = current_location[0]
                                #print("Location is current_location")
                            else:
                                canonical = word
                            kinds.add("location")

                else:
                    if word in verbs.all_verbs:
                        #print(f"word in verb.all_verbs: {verbs}")
                        if word in word_phrases and word_phrases.get(word) and parts[0] in word_phrases.get(word):
                            kinds.add("null")
                            canonical = word
                            #print(f"canonical: {canonical}")
                            continue
                        #if word == "open" and idx > 0 and parts[idx-1] == "pry":
                        #    kinds.add("null")
                        #    canonical = word
                        #    continue
                        #print(f"Word in all_verbs: {word}")
                        kinds.add("verb")
                        canonical = word
                        #print(f"canonical for verb: {canonical}")

                    if word in verbs.adjectives:
                        if null_adjectives: ## exclude adjectives here. For now, adjectives are not actively implemented, just excluded in a specific way. Will amend this later.
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
                    tokens.append(Token(idx, word, kinds, canonical))
                    potential_match = True
                else:
                    #print(f"Word going to check compound words: {word}")
                    #new_idx, word, kinds, canonical, potential_match, omit_next = Parser.check_compound_words(parts_dict = verbs.compound_words.items(), word=word, parts=parts, idx=idx, kinds=kinds, word_type = "noun", omit_next=omit_next)
                    #maybe new_idx is bad. Now with 'tv set', it correctly finds 'tv set', but then also finds 'set' as a verb when it should have been omitted.
                    idx, word, kinds, canonical, potential_match, omit_next = Parser.check_compound_words(parts_dict = compound_nouns, word=word, parts=parts, idx=idx, kinds=kinds, word_type = "noun", omit_next=omit_next)

                    if canonical:
                        #print(f"CANONICAL: {canonical, idx}")
                        tokens.append(Token(idx, word, kinds, canonical))

                    else:
                        #print(f"Word going to compound loc: ({word})")
                        idx, word, kinds, canonical, potential_match, omit_next = Parser.check_compound_words(parts_dict = compound_locs, word=word, parts=parts, idx=idx, kinds=kinds, word_type = "location", omit_next=omit_next)
                        if canonical:
                            #print(f"canonical loc: {canonical}")
                            tokens.append(Token(idx, word, kinds, canonical))
                    if not canonical:
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

                    #print(f"verbs.compound_words: {verbs.compound_words}")

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

    def get_viable_verb(token, force_location=False):
        word = token.text
        if force_location:
            word="go"
        if word == "edit":
            word = "meta" # a nasty little shortcut here. Not ideal but it'll work for the moment.
        viable_instance = None
        #print(f"Word: {word}")
        if verbs.verbs.get(word):
            viable_instance = verbs.verbs.get(word)
        else:
            #print(f"verbs.by_alt_words: ")
            #print(verbs.by_alt_words)
            if verbs.by_alt_words.get(word):
                viable_instance = (verbs.by_alt_words[word][0])

        #print(f"Viable instance: {viable_instance}")
        #print(f"Viable instance name: {viable_instance.name}")
        if not viable_instance:
            print(f"Could not find viable instance for verb `{word}`. \nExiting immediately.")
            exit()
        return viable_instance

    def generate_initial_dict(tokens, sequences) -> tuple[dict, int]:
        reformed_dict = {}

        if len(sequences) > 1:
            print("More than one viable sequence. Help?")
            print(sequences)
            print("[This should be where it's culled down, right? Idk. Or maybe we just go with the first here and refine it later if it breaks. Idk yet. For now, just quit. Shouldn't be more than one I think.]")
            exit()

        sequence = sequences[0]
        matched = 0
        for token in tokens:
            if matched == len(sequence):
                break
            if token.kind != {"null"} and token.kind != set():
                if sequence[matched] in token.kind:
                    #print(f"This is {token.kind}")
                    #print(f"Token: {token}")

                    reformed_dict[matched] = {sequence[matched]: token.canonical}
                    matched += 1

        return reformed_dict, sequence

    def get_sequences_from_tokens(tokens) -> list:

        sequences = [[]]
        verb_instances = []
        meta_instances = []
        verb_entry = None

        for i, token in enumerate(tokens):
            options = Parser.token_role_options(token)
            #print(f"Options: {options}")
            if len(tokens) in (1, 2):
                #print(f"Token.kind: {token.kind}, type: {type(token.kind)}")
                if list(token.kind)[0] in ("location", "direction"):
                    #print(f"Token kind: {token.kind}")
                    instance = Parser.get_viable_verb(token, force_location=True)
                    verb_instances.append({i:instance})
                if list(token.kind)[0] == "cardinal":
                    #print(f"Token: {token}")
                    instance = Parser.get_viable_verb(token, force_location=True)
                    verb_instances.append({i:instance})
            #print(f"Options: {options}")
            if "verb" in options:
                instance = Parser.get_viable_verb(token)
                verb_instances.append({i:instance})
                #print(f"verb instance: {instance}")
                #print(f"Name: {instance.name}")
            if "meta" in options:
                #print(i, token)
                meta_instances.append({i:token})

            new_sequences = []

            for seq in sequences:
                #print(f"seq: {seq}")
                for opt in options:
                    if opt is None:
                        new_sequences.append(seq)
                    else:
                        new_sequences.append(seq + [opt])

            sequences = new_sequences
        #test_print(f"Sequences: {sequences}", print_true=True)

        if not verb_instances:
            if not meta_instances:
                print("No verb_instance or meta_instance found in get_sequences_from_tokens. Returning None.")
                print(f"TOKENS: {tokens}")
                return None, None

        #print(f"verb instances: {verb_instances}")
        #print(f"meta instances: {meta_instances}")
        if len(verb_instances) == 1:
            verb_entry = verb_instances

        #print(f"Verb instances: {verb_instance}")
        viable_sequences = []

        for seq in sequences:
            if seq:
                #print(f"SEQ: {seq}")
                if verb_instances: ## wtf, 'verb_entry' doesn't exist at this point...
                    for verb_entry in verb_instances:
                        #print(f"for verb entry {verb_entry} in verb instances:")
                        for verb in verb_entry.values():
                            #print(f"VERB: {verb}")
                            #print(f"seq: {seq}, type: {type(seq)}, verb.formats: {verb.formats}, viable_sequences: {viable_sequences}")
                            if tuple(seq) in verb.formats and seq not in viable_sequences:
                                #print(f"This tuple sequence is compatible with verb_instance {verb.name}: {seq}")
                                viable_sequences.append(seq)
                            elif seq in viable_sequences and seq not in viable_sequences: # needed because I think single-entry tuples don't count in the above?
                                #print(f"This non-tuple sequence is compatible with verb_instance {verb.name}: {seq}")
                                viable_sequences.append(seq)

                if meta_instances:
                    for entry in meta_instances:
                        #print(f"ENTRY: {entry}")
                        for verb in entry.values():
                            #print(f"META: {verb}")
                            #print(f"seq: {seq}, type: {type(seq)}, verb.kind: {verb.kind}, viable_sequences: {viable_sequences}")
                            #print(f"Verb.formats: {verb.kind}")
                            if tuple(seq) in verb.kind and seq not in viable_sequences:
                                #print(f"This sequence is compatible with verb_instance {verb.name}: {seq}")
                                viable_sequences.append(seq)
                            #else:
                            #    print(f"SEQ: {seq}, type: {type(seq)}")
                            #    print(f"verb.kind: {verb.kind}, type: {type(verb.kind)}")
                            elif set(seq) == verb.kind and seq not in viable_sequences:
                                #print(f"SEQ: {seq}, type: {type(seq)}")
                                #print(f"verb.kind: {verb.kind}, type: {type(verb.kind)}") ## so metas options come out as sets, not tuples. Need to look into why. Certainly something I did. #TODO
                                #print(f"This sequence is compatible with verb_instance {verb.name}: {seq}")
                                viable_sequences.append(seq)
                    if not viable_sequences:
                        meta = meta_instances[0]
                        #print(f"META: {meta}")
                        token = meta[0]
                        #print(f"TOKEN: {token}")
                        instance = Parser.get_viable_verb(token)
                        #print(f"INSTANCE: {instance}")
                        #print(f"instance vars: {vars(instance)}")
                        if hasattr(instance, "formats"):
                            #print(f"SEQ: {seq}")
                            #print(f"INSTANCE FORMATS: {instance.formats}")
                            if tuple(seq) in instance.formats:
                                viable_sequences.append(seq)



        #if not viable_sequences:
        """
            ### Want to add something here to check if the input is just 'put thing down' + location, where location would not change anything. To avoid having to add it to each option. Sometimes it's necessary, but some verbs can ignore it as long as it matches current_loc.
            Not sure how to do it yet.

            I did try just below but it didn't work, can't remember why. Need to keep better notes.
        """
        #    for seq in sequences:
        #        #print("[-1:] :", seq[-1:]) ## first bit
        #        #print("[-1] : ", seq[-1]) ## first bit
        #        #if seq[-1] == "location" and seq[-2] == "direction":
        #        #    for token in tokens:
        #        #        print(f"token: {token}")
        #        #        print(f"kind: {token.kind}")
        #        #        if "location" in token.kind:
        #        #            print(f"Token kind is location. Canonical: {token.canonical}")
        #        #            if token.canonical in get_current_loc():
        #        #                print(f"Value in current loc: {print}")
        #        #            else:
        #        #                print(f"{token.canonical} location not in current location.")
        #        #print(f"SEQ::: {seq}")
        #        if tuple(seq) in verb_instance.formats:
        #            #print(f"This sequence is compatible with verb_instance {verb_instance.name}: {seq}")
        #            viable_sequences.append(seq)

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
            item_name = initial_dict[i][item]
            #print(f"item_name: {item_name}")
            if item == "verb":
                verb, _ = Parser.resolve_verb(tokens, item_name, format_key)
                #resolve_verb(tokens, verb_name, format_key)
                if verb:
                    #print(f"Verb::: {verb}, verb_name: {verb.name}")
                    #dict_for_output[i]={item: verb}
                    dict_for_output[i]={item: {"instance":verb, "str_name":item_name}}
                    ## changed t oadd instance and item_name
                #for verb_dicts in confirmed_verb:
                #    for entry in verb_dicts.values():
                #        print(f"Entry: {entry}")
                #        print(f"Entry: {entry.name}")
                #        Parser.resolve_verb(tokens, entry.name, format_key)
                #        print(f"item_name: {item_name}")
                #        if entry.name == item_name:
                #            print("entry name is item name.")
                #            dict_for_output[i]={item: entry}
            else:
                dict_for_output[i]={item:{"instance":None, "str_name":item_name}}

        return dict_for_output, tokens # including tokens for any minor input detail that might matter later.


    def input_parser(self, input_str): # temporarily adding 'items' just so I can test with any item from the item dict without having to add to inventory/location first. Purely for testing convenience.

        from verb_membrane import membrane

        nouns_list = membrane.nouns_list
        locations = membrane.locations
        directions = membrane.directions
        cardinals = membrane.cardinals

        tokens = self.tokenise(input_str, nouns_list, locations, directions, cardinals, membrane)

        #print(f"Tokens: {tokens}")

        sequences, verb_instances = self.get_sequences_from_tokens(tokens)

        if not sequences:
            print(f"No viable sequences found for {input_str}.")
            clean_parts = []
            token_parts = [i.kind for i in tokens if i.kind != "null"]
            for parts in token_parts:
                for part in parts:
                    if part != "null":
                        clean_parts.append(part)
                        break

            print(" ".join(clean_parts))
            return clean_parts, None

            #TODO:  If no functional sequences, need to pick out parts that might be applicable to make reasonable guesses. Like if we have 'go'  and 'location', 'did you mean 'go to location', etc. Need a way to pause mid-parse, get confirmation then come back and run the sequencer again. Not today, but soon.

        token_count = len([i for i in tokens if i.kind != {"null"} and i.kind != set()])

        length_checked_sequences = []
        for sequence in sequences:
            if len(sequence) == token_count:
                length_checked_sequences.append(sequence)
        #print(f"Length_checked_sequences: {length_checked_sequences}, len: {len(length_checked_sequences)}")
        initial_dict, sequence = Parser.generate_initial_dict(tokens, length_checked_sequences) # culls to just the first sequence. Doesn't deal with 'picking the best version' if there's more than one yet. Needs to in the future.

        #print(f"length checked sequences: {length_checked_sequences}")
        #print("initial_dict", initial_dict)
        dict_for_output, tokens = self.build_dict(verb_instances, tokens, initial_dict, sequence)
        #print(f"dict for output; {dict_for_output}")
        return sequence, dict_for_output

    # -------------


verbs = VerbRegistry()

colours = ["BLACK","RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]
sizes = ["big", "small", "tiny", "enormous", "massive", "little"]

def initialise_verbRegistry():

    from verb_definitions import get_verb_defs, allowed_null, semantics, formats, meta_verbs

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

    from itemRegistry import registry

    verbs.compound_words = registry.plural_words

    for item_name, attr in verb_defs_dict.items():
        verbs.create_verb_instance(item_name, attr)

        if attr.get("null_words"):
            for word in attr.get("null_words"):
                if word.lower() != None:
                    verbs.list_null_words.add(word)
