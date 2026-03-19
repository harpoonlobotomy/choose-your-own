"""Class(es) for NPC data. Holds interaction data, conversation history, etc. Also holds speech trait string modifications."""

from env_data import cardinalInstance

filler_words = ["well", "umm", "ah", "well, uh", "I guess", "I think"]
sample_convo_parts = {"start": "Hello.", "end": "Goodbye."}
sample_responses = {"acceptance": "Alright", "approval": "Indeed", "disapproval": "I doubt that.", "unsure": "What?"}

class conversationInstance:

    def __init__(self, topic:str, data:dict):
        self.topic = topic
        self.topic_label:str = data["topic_label"]
        self.relevant_items:list = data.get("relevant_items")
        self.parts_said = []
        self.by_part:dict[str, dict] = {}
        self.keywords: dict[str, str] = {} # keyword: part_idx
        self.autoplay_parts:set[str] = set()
        for idx in data["conversation"]:
            if data["conversation"][idx].get("keywords"):
                for keyword in data["conversation"][idx]["keywords"]:
                    self.keywords[keyword] = idx
            self.by_part.setdefault(idx, data["conversation"][idx])
            if data["conversation"][idx].get("autoplay"):
                self.autoplay_parts.add(idx)
        self.language:str = data.get("language")

    def __repr__(self):
        return f"<conversationInstance `{self.topic}`>"


class conversationsRegistry:

    def __init__(self):

        self.conversations:set[conversationInstance] = set()
        self.by_topic:dict[str, conversationInstance] = {} # effectively 'by_name', eg "church_history" > church history instance
        self.by_item:dict[str, set] = {} # for finding topics related to items
        self.by_character:dict[npcInstance, set[conversationInstance]] = {} # for storing which character has spoken about what
        self.by_language:dict[str, set[conversationInstance]] = {}

    def init_conversations(self, convo_defs:dict):
        """Init all NPCs from NPC_defs and add to npcRegistry"""

        for name, data in convo_defs.items():
            conversation = conversationInstance(name, data)

            self.conversations.add(conversation)
            self.by_topic[name] = conversation
            if conversation.relevant_items:
                for item in conversation.relevant_items:
                    self.by_item.setdefault(item, set()).add(conversation)

            if not conversation.language:
                conversation.language = "common"
            self.by_language.setdefault(conversation.language, set()).add(conversation)


class npcInstance:

    def __init__(self, name:str, data:dict):

        self.name = name
        self.print_name = data.get("print_name") if data.get("print_name") else name
        self.text_styling = data.get("text_styling")
        self.colour:str = None
        self.colourcode_start:str = None
        self.colourcode_end:str = None
        self.age:str = data.get("age")
        if not self.age:
            self.age:str = "average"
        self.can_die:bool = data.get("can_die")
        self.is_dead:bool = False
        self.alt_names:list[str] = data["alt_names"]
        self.can_speak:bool = data.get("can_speak")

        self.speaks_common:bool = data.get("speaks_common")
        self.languages_spoken:list[str] = data.get("languages_spoken")
        self.speech_traits:list[str] = data.get("speech_traits")

        self.item_type:list[str] = data.get("item_type")
        self.knows_about:list[str] = data.get("knows_about")
        self.conversations:dict[conversationInstance, str] = {}

        self.location = data.get("location")
        from env_data import locRegistry, cardinalInstance

        if not self.location:
            self.location = locRegistry.no_place
        elif isinstance(self.location, str):
            loc = locRegistry.by_cardinal_str(self.location)
            if loc and isinstance(loc, cardinalInstance):
                self.location = loc

        self.nicenames:dict = data.get("nicenames")
        if (self.nicenames and self.nicenames.get("generic") and self.nicenames["generic"] == "") or not self.nicenames or not self.nicenames.get("generic"):
            self.nicenames["generic"] = self.name
        self.nicename = self.nicenames["generic"]

        self.descriptions = data.get("descriptions") if data.get("descriptions") and data["descriptions"]["generic"] != "" else {"generic": f"It's a {self.name}", "npc_introduction": f"Before you, you see {(self.name)}"}
        self.description = self.descriptions["generic"]
        self.introduction = self.descriptions.get("npc_introduction")
        self.conversation_parts:dict[str, str] = data.get("conversation_parts")
        if not self.conversation_parts:
            self.conversation_parts = sample_convo_parts

        self.convo_start = self.conversation_parts["start"]
        if "[[playername]]" in self.convo_start:
            from set_up_game import game
            self.convo_start = self.convo_start.replace("[[playername]]", game.playername)
        self.convo_end = self.conversation_parts["end"]
        if "[[playername]]" in self.convo_end:
            from set_up_game import game
            self.convo_end = self.convo_end.replace("[[playername]]", game.playername)

        self.keywords: dict[str, dict[conversationInstance, str]] = {} # npc.keywords[kw] = {convo:convo.keywords[kw]} <- saving convo:idx on npcs, so I can check directly during conversations across all possible conversations for keywords.

        self.slice_attack = data.get("slice_attack")
        self.slice_defence = data.get("slice_defence")
        self.smash_attack = data.get("smash_attack")
        self.smash_defence = data.get("smash_defence")

        self.encountered = False

        if not data.get("responses"):
            responses = sample_responses
        else:
            responses = data["responses"]
        self.acceptance = responses.get("acceptance")
        self.approval = responses.get("approval")
        self.disapproval = responses.get("disapproval")
        self.unsure = responses.get("unsure")

        for item in data:
            if not hasattr(self, item) and item != "responses":
                print(f"Item `{item}` in NPC_defs but not in npcInstance")

    def __repr__(self):
        return(f"<npcInstance `{self.name}`, {(f'at {self.location}') if hasattr(self, "location") else ''}")


class npcRegistry:

    def __init__(self):
        self.npcs:set[npcInstance] = set() # all instances
        self.by_name:dict[str, npcInstance] = {} # name: instance # one per name, for now. can change it later if I need to.
        self.by_altname:dict[str, npcInstance] = {} # altname: instance
        self.by_location:dict[cardinalInstance, set[npcInstance]] = {}
        self.by_language_spoken:dict[str, set[npcInstance]] = {}
        self.by_conversation_topic:dict[str, set[npcInstance]] = {} # topic: set of npcInstances with that topic


    def init_npcs(self, npc_defs:dict):
        """Init all NPCs from NPC_defs and add to npcRegistry"""

        for name, data in npc_defs.items():
            npc = npcInstance(name, data)

            self.npcs.add(npc)
            self.by_name[name] = npc
            if hasattr(npc, "alt_names") and npc.alt_names:
                for alt in npc.alt_names:
                    from itemRegistry import registry
                    registry.by_alt_names[alt] = npc # adding to itemReg so I can still use the parser.
                    self.by_altname[alt] = npc # might not need this one.

            self.by_location.setdefault(npc.location, set()).add(npc)

            if npc.languages_spoken:
                for language in npc.languages_spoken:
                    self.by_language_spoken.setdefault(language, set()).add(npc)

            if npc.text_styling:
                ita = bld = und = bg = colour = False
                from tui.colours import Colours
                for item in npc.text_styling:
                    if item == "italics":
                        ita = True
                    elif item == "bold":
                        bld = True
                    elif item == "underline":
                        und = True
                    else:
                        colour = item
                if colour:
                    npc.colour = colour
                code = Colours.c("split", fg=colour, bg=bg, bold=bld, italics=ita, underline=und, invert=False, no_reset=False)
                code_parts = code.split("split")
                npc.colourcode_start = code_parts[0]
                npc.colourcode_end = code_parts[1]
                #print(f"npc.colourcode: {npc.colourcode_start} This is this NPC's text formatting. {npc.colourcode_end}")

    def alter_speech(self, npc:npcInstance, speech_str:str, styling=True):
        """Here we edit the speech str in accordance with npc.speech_traits"""
# "ellipses": Replaces all full-stops at end of sentences with "...". Possibly commas too, need to test.
# "commalipses": Replaces all commas with "...".
# "run_ons": replaces mid-speech full stops with commas.
# "no_pronouns": not techinically accurate, still allows 'you', but does not refer to self directly.
# "it_not_i": replaces 'I' with 'it'.
# "well_umm": Adds filler words, drawn at random from a list.
        if not npc.speech_traits:
            if styling and npc.text_styling:
                speech_str = npc.colourcode_start + speech_str + npc.colourcode_end
            return speech_str
        else:
            if "..." in speech_str:
                speech_str = speech_str.replace("...", "**") # replace w double asterisks so it's unaffected by speech traits, and put it back later.
            string_parts = speech_str.split(". ")
            reformed = ""
            prev_filler = None

            for i, speech in enumerate(string_parts):
                #print(f"speech; {speech}")
                if speech == None:
                    continue
                if "no_pronouns" in npc.speech_traits:
                    speech = speech.replace(" I.", ".")
                    speech = speech.replace(" I ", " ")
                    if speech.startswith("I "):
                        speech = speech.replace("I ", "", 1)
                        speech = speech.capitalize()

                elif "it_not_i" in npc.speech_traits:
                    speech = speech.replace(" I.", " it.")
                    speech = speech.replace(" I ,", " it ")
                    if speech.startswith("I "):
                        speech = speech.replace("I ", "It ", 1)
                        speech = speech.replace("It think ", "It thinks ", 1)

                if "well_umm" in npc.speech_traits:
                    import random
                    if i == 0 or random.choice((True, False)) == True:
                        #if speech[0].isupper() and not speech.startswith("I "):
                        #    speech = speech[0].lower() + speech[1:]
                        if prev_filler:
                            choose_from = list(i for i in filler_words if i != prev_filler)
                        else:
                            choose_from = filler_words
                        filler = random.choice(choose_from).capitalize()
                        prev_filler = filler.lower()
                        if "run_ons" in npc.speech_traits:
                            if i != 0:
                                filler = filler.lower()
                            speech = speech[0].lower() + speech[1:]
                        if "commalipses" in npc.speech_traits:
                            if not speech.startswith("I "):
                                speech = speech[0].lower() + speech[1:]
                            speech = filler + ". " + speech
                        else:
                            if not speech.startswith("I "):
                                speech = speech[0].lower() + speech[1:]
                            speech = filler + ", " + speech

                if "run_ons"  in npc.speech_traits:
                    if speech[0].isupper() and not speech.startswith("I "):
                        speech = speech[0].lower() + speech[1:]
                    dot = ","
                else:
                    dot = "."
                if speech[-1] == ".":
                    reformed = reformed + speech
                else:
                    reformed = reformed + speech + f"{dot} "

                if reformed[-3:] == f".{dot} " and not reformed[-4:] == f".{dot}. ":
                    reformed = reformed[:-3] + ". "

            reformed = reformed.replace(" i ", " I ")

            if "ellipses" in npc.speech_traits:
                reformed = reformed.replace(". ", "... ")
            if "commalipses" in npc.speech_traits:
                reformed = reformed.replace(", ", "... ")

            if reformed[-1] == " ":
                reformed = reformed[:-1]

            if "run_ons" in npc.speech_traits:
                reformed = reformed[:-1] + reformed[-1].replace(",", ".")

            reformed = reformed.replace("**", "...")
            reformed = reformed[0].upper() + reformed[1:]

            if styling and npc.text_styling:
                reformed = npc.colourcode_start + reformed + npc.colourcode_end

            return reformed

    def add_conversation_to_npc(self, npc:npcInstance, topic:str):
        self.by_conversation_topic.setdefault(topic, set()).add(npc)
        convo = conversing.by_topic.get(topic)
        if not convo:
            print(f"No convo found for `{topic}`.")
            return
        npc.conversations[convo] = {"parts_said": set()}
        if convo.keywords:
            for kw in convo.keywords:
                npc.keywords[kw] = {convo:convo.keywords[kw]}

    def __repr__(self):
        print(f"<npcRegistry>")


conversing = conversationsRegistry()
npc_Registry = npcRegistry()

def initialise_conversations():
    from config import conversation_data
    import json
    with open(conversation_data, "r") as f:
        convo_defs = json.load(f)
    conversing.init_conversations(convo_defs)


def initialise_npcs():
    from config import npc_data
    import json
    with open(npc_data, "r") as f:
        npc_defs = json.load(f)
    npc_Registry.init_npcs(npc_defs)

    for npc in npc_Registry.npcs:
        #print(f"introduction: {npc.introduction},  npc.languages: {npc.languages_spoken}")
        if npc.knows_about:
            for topic in npc.knows_about:
                npc_Registry.add_conversation_to_npc(npc, topic)

        if npc.location and isinstance(npc.location, cardinalInstance):# and npc.location.description:
            npc.location.NPCs.add(npc)
            from itemRegistry import registry
            registry.by_location[npc.location].add(npc)


def test_npc():
    for npc in npc_Registry.npcs:
        convo = list((i for i in npc.conversations if i.topic == "church_history") if npc.conversations else None)[0]
        convo:conversationInstance
        print(f"npc loc: {npc.location}")
        print(convo.by_part)
        for part in convo.by_part:
            speech = npc_Registry.alter_speech(npc, convo.by_part[part]["speech"])
            if speech:
                print(f"\n`{speech}`\n")

        print(f"\ntalk to Father ((regular text))\n\n{npc.convo_start}\n")
        print(f"\ntalk to Father ((with alter_speech))\n\n{npc_Registry.alter_speech(npc, npc.convo_start, styling=False)}\n")
        print(f"\ntalk to Father ((with alter_speech and styling))\n\n{npc_Registry.alter_speech(npc, npc.convo_start, styling=True)}\n\n")


if __name__ == "__main__":
    initialise_conversations()
    initialise_npcs()
    test_npc()
