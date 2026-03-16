conversation_notes.md

# Notes for how conversation works, things to remember, etc.

can_speak item_type traits: `[NPC defs stored in NPC_defs.json.]`
    'can_speak': True == true by default, false if temporarily mute etc. Possible a conversation can be started if item_type can_speak but can_speak == False.
    'speaks_common': True if false, must give alternate language in language_spoken.
    "language_spoken": [] = list of languages spoken, defaults to contain "common"
    "knows_about": [] = list of topics the NPC has knowledge about.
    "speech_traits": [] = alterations to speech for this NPC eg 'ellipses' (ends each sentence with "...", no_pronouns, etc.)

conversations.py:
Stores conversation data to be used by NPCs.

 "church_history": {"relevant_items": [], "conversation": {"0": {"has_requirements": False, "keywords": [], "speech": ""}, parts_said: []}},

Not sure how much I want this to branch. 'church_history' is a topic, and I like the idea of the conversation being somewhat linear. Can either be produced linearly, or can just be used to reference which parts have been said already and which haven't.
Maybe some NPCs give speeches and wait for you to prompt.

Added 'keywords' to each conversation part, so for situations where speech needs to be prompted, it can identify them quickly. So mentioning 'x' to the NPC will trigger a relevant response. Keywords is optional because I could just check the response strings, but this way the word doesn't have to be in the response itself. Having the triggers separate makes it more flexible I think. Also, 'relevant_items' can be keywords, so having the item in your possession will trigger/enable that speech part.
Oh, some speech lines should require certain things. Hm. Adding 'has_requirements' to conversation parts, so say the second thing NPC1 says only gets said if you meet that requirement. That should work.

'parts_said' will be used to store the index of parts of speech once they've been said. Doesn't mean they can't be repeated, though possibly I could add 'only once' if needed, but means I can have intro speeches that only run once.

Oh, "parts_said" needs to be stored in the NPC, not the conversation. Hm or maybe both, so we have a way of tracking what the player has been told? Not sure.

Need an NPC class to store those things.

Working on the class now.

Have made
 "has_requirements": {"item": "paperclip"},
into a dict, so I can specify type. If not an item, perhaps certain conversations have to happen at night, at certain locations, etc.

parts_said is working, and the basic conversation loop is alright. So far all it can do at most is recognise keywords that can lead to either a conversation topic (given in a list at present) or keywords that will access specific lines of dialogue, and potentially start events related to them.

Some parts of conversation require a trigger to be present to play that line (eg holding a particular item).

Things I need to add:
Specific things you can ask all NPCs, eg ask about items or places, things like that. currently it only works if they have a keyworded response.

Also, I need a way to prioritise triggered conversation elements. Currently they're ordered, but I need to be able to say 'if a person is carrying a trigger item, start the conversation with that'. Though maybe I just do that using the speech line idx tbh. Will make it a pain down the line though if I realise I want to add a new trigger item line and have to relabel every speech line thereafter. Yeah I need a fix for that. Okay.

I need to figure out how to have proper conversation chains. So the npc can ask a question and have the player answer without having to make events for each element.


dammit.
