"""Class(es) for NPC data. Holds interaction data, conversation history, etc. Also holds speech trait string modifications."""

class conversationInstance:

    def __init__(self, topic, data):
        self.topic = topic
        self.relevant_items = data["relevant_items"]
        #self.conversation_data =  # "0": has_requirements, keywords, speech
        self.parts_said = data["parts_said"] # list of str digits identifying which parts of the conversation have been said globally. Does not track per character. Should probably get these from npcInstances, actually, instead of storing it twice.
        self.by_part = {}
        self.keywords = {} # keyword: part_idx
        for idx in data["conversation"]:
            if data["conversation"][idx].get("keywords"):
                for keyword in data["conversation"][idx]["keywords"]:
                    self.keywords[keyword] = idx
            self.by_part.setdefault(idx, data["conversation"][idx])


class conversationsRegistry:

    def __init__(self):

        self.conversations = set()
        self.by_topic = {} # effectively 'by_name', eg "church_history". dict of dicts
        self.by_item = {} # for finding topics related to items
        self.by_character = {} # for storing which character has spoken about what


class npcInstance:

    def __init__(self, name, data):

        self.name = name
        self.age = data.get("age")
        if not self.age:
            self.age = "average"
        self.can_die = data.get("can_die")
        self.is_dead = False
        self.alt_names = data["alt_names"]
        self.can_speak = data.get("can_speak")

        self.speaks_common = data.get("speaks_common")
        self.languages_spoken = data.get("languages_spoken")
        self.speech_traits = data.get("speech_traits")

        self.item_type = data.get("item_type")
        self.knows_about = data.get("knows_about")

        self.location = data.get("location")

        self.nicenames = data.get("nicenames")
        if (self.nicenames and self.nicenames.get("generic") and self.nicenames["generic"] == "") or not self.nicenames or not self.nicenames.get("generic"):
            self.nicenames["generic"] = self.name
        self.nicename = self.nicenames["generic"]

        self.descriptions = data.get("descriptions") if data.get("descriptions") and data["descriptions"]["generic"] != "" else {"generic": f"It's a {self.name}", "npc_introduction": f"Before you, you see {(self.name)}"}
        self.description = self.descriptions["generic"]
        self.introduction = self.descriptions.get("npc_introduction")

        self.slice_attack = data.get("slice_attack")
        self.slice_defence = data.get("slice_defence")
        self.smash_attack = data.get("smash_attack")
        self.smash_defence = data.get("smash_defence")

        self.encountered = False

        for item in data:
            if not hasattr(self, item):
                print(f"Item `{item}` in NPC_defs but not in npcInstance")

    def __repr__(self):
        return(f"<npcInstance `{self.name}`, {(f'at {self.location}') if self.location else ''}")


class npcRegistry:

    def __init__(self):
        self.npcs = set() # all instances
        self.by_name = {} # name: instance # one per name, for now. can change it later if I need to.
        self.by_altname = {} # altname: instance
        self.by_location = {} # cardinalInstance: set of npcInstances
        self.by_language_spoken = {} # language str: set of npcInstances


    def init_npcs(self, npc_defs):
        """Init all NPCs from NPC_defs and add to npcRegistry"""
        from env_data import locRegistry, cardinalInstance

        for name, data in npc_defs.items():
            npc = npcInstance(name, data)

            self.npcs.add(npc)
            self.by_name[name] = npc
            if hasattr(npc, "alt_names") and npc.alt_names:
                for alt in npc.alt_names:
                    self.by_altname[alt] = npc
            if not hasattr(npc, "location") or not npc.location:
                npc.location = locRegistry.no_place
            elif isinstance(npc.location, str):
                    loc = locRegistry.by_cardinal_str(npc.location)
                    if loc and isinstance(loc, cardinalInstance):
                        npc.location = loc
            self.by_location.setdefault(npc.location, set()).add(npc)

            if npc.languages_spoken:
                for language in npc.languages_spoken:
                    self.by_language_spoken.setdefault(language, set()).add(npc)

            #print(f"SELF BY LOCATION: {self.by_location}")
    def alter_speech(self, npc:npcInstance, speech):
        """Here we edit the speech str in accordance with npc.speech_traits"""
# "ellipses": Replaces all full-stops at end of sentences with "...". Possibly commas too, need to test.
# "no_pronouns": not techinically accurate, still allows 'you', but does not refer to self directly.
# "it_not_i": replaces 'I' with 'it'.
# "run_ons": replaces mid-speech full stops with commas.
# "well_umm": Adds filler words, drawn at random from a list.
        if not npc.speech_traits:
            return
        else:
#            for trait in npc.speech_traits:
#                if trait != "ellipses":

            print("They probably need to be ordered. Ellipses last.")

    def __repr__(self):
        print(f"<npcRegistry>")


npc_Registry = npcRegistry()

def initialise_npcs():
    from config import npc_data
    import json
    with open(npc_data, "r") as f:
        npc_defs = json.load(f)
    npc_Registry.init_npcs(npc_defs)


initialise_npcs()


for npc in npc_Registry.npcs:
    print(f"introduction: {npc.introduction},  npc.languages: {npc.languages_spoken}")
