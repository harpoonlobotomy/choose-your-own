So. I need to do the save system for this game before I can move onto the player stats.

Current plan:
    * Save the ID and non-default vars for all items and NPCs.
    * Save all events.
     - Also: update events to delete item associations etc unless the event strictly requires the item/details be remembered. Useful to be able to store, but not necessary. I don't need to know which event dried this bit of moss once it's dry and that event is over. With that done, only current and/or memorable events will have their data saved. Any non-recurring event (or maybe any event) that is completed will just have  the event name + 'past' state saved.
        -- so: for all events (or all non-recurring, not sure, going with 'all' for now) have id, name, state saved.
        - future + current events and past events that might matter have all non-default vars saved. So if they have an item associated or something, that item ID is saved. If an attr is default or is generated during run (and has not been generated during this run yet), do not save. So only the new bits, but every active instance named. So it pulls event deffs, but only for the named events, so we don't init all then just try to transfer. Same theory as the items/npcs.
    * save datapoints from set_up_game, for npc conversations etc to persist across loads.

NPC dict (to figure out what elements to save to file):
name, id,
    NPC dict: {'name': 'Bridge Troll', 'id': '25153cd4-a40c-41f4-80af-e83ef1778cbd', 'is_hidden': False, 'print_name': 'Bridge Troll', 'text_styling': ['green'], 'colour': 'green', 'colourcode_start': '\x1b[32m', 'colourcode_end': '\x1b[0m', 'age': 'average', 'can_die': 'True', 'is_dead': False, 'alt_names': [], 'can_speak': 'True', 'speaks_common': 'True', 'languages_spoken': ['common', 'Trollish'], 'speech_traits': ['no_pronouns', 'hic'], 'item_type': ['can_speak', 'living', 'standard', 'can_trade'], 'knows_about': ['moss', 'dried moss'], 'conversations': {<conversationInstance `moss`>: {'autoplay_failed': set()}, <conversationInstance `dried moss`>:
    {'autoplay_failed': set()}}, 'gold': 5, 'inventory': {<ItemInst [mummified mouse ID:d419db08f1d5] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [goat excrement ID:c4bcc30e369d] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [scroll ID:cf140555a70f] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [car keys ID:286f12167619] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [fish food jar ID:ec5f3fc3215f] [loc: north npc_inventory_place] [event:event str: None] >}, 'special_responses': {'dried moss': ['Eh yes! good soft, good...', "Mm, 's good squishy. Good trade."]}, 'trade_items': {<ItemInst [mummified mouse ID:d419db08f1d5] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [goat excrement ID:c4bcc30e369d] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [scroll ID:cf140555a70f] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [car keys ID:286f12167619] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [fish food jar ID:ec5f3fc3215f] [loc: north npc_inventory_place] [event:event str: None] >}, 'will_not_sell': ['dried moss'], 'trade_start': 'You got nice-soft moss, mm? *hic*', 'trade_end': 'Bah, no more soft-moss? Beh-crz ih.', 'trade_intake': {'named_only': ['dried moss']}, 'thief_awareness': 5, 'location': <cardinalInstance north bridge (60df641d-b009-4363-b275-0942d4e93242)>, 'nicenames': {'generic': 'Bridge Troll'}, 'nicename': 'Bridge Troll', 'descriptions': {'generic': 'a bridge troll, green of skin and weathered, wearing a satchel over its shoulder and a loincloth protecting its dignity', 'npc_introduction': 'Stooped over and seemingly staring at a
    dandelion growing from the ground, you see a bridge troll. A patched leather satchel hangs loose over one shoulder, its weathered bare skin showing everywhere except for where it was covered by a thin, worn loincloth.'}, 'description': 'a bridge troll, green of skin and weathered, wearing a satchel over its shoulder and a loincloth protecting its dignity', 'introduction': 'Stooped over and seemingly staring at a dandelion growing from the ground, you see a bridge troll. A patched leather satchel hangs loose over one shoulder, its weathered bare skin showing everywhere except for where it was covered by a thin, worn loincloth.', 'conversation_parts': {'start': '*sniff* Eh, what you want?', 'end': 'Get away then.', 'trade_start': 'You got nice-soft moss, mm? *hic*', 'trade_end': 'Bah, no more soft-moss? Beh-crz ih.'}, 'convo_start': '*sniff* Eh, what you want?', 'convo_end': 'Get away then.', 'keywords': {'dried moss': {<conversationInstance `dried moss`>: '1'}}, 'slice_attack': '5', 'slice_defence': '5', 'smash_attack': '5', 'smash_defence': '5', 'encountered': True, 'acceptance'Exiting now.', "M'kay."], 'approval': ['Eh, guess so.'], 'disapproval': ["Hah, jokin'.", 'Nope.'], 'unsure': ['What?'], 'nothing_else': ["'s all there is.", "'s all to say."]}


    NPC dict: {'name': 'Bridge Troll', 'id': '25153cd4-a40c-41f4-80af-e83ef1778cbd', 'is_hidden': False, 'print_name': 'Bridge Troll', 'text_styling': ['green'], 'colour': 'green', 'colourcode_start': '\x1b[32m', 'colourcode_end': '\x1b[0m', 'age': 'average', 'can_die': 'True', 'is_dead': False, 'alt_names': [], 'can_speak': 'True', 'speaks_common': 'True', 'languages_spoken': ['common', 'Trollish'], 'speech_traits': ['no_pronouns', 'hic'], 'item_type': ['can_speak', 'living', 'standard', 'can_trade'], 'knows_about': ['moss', 'dried moss'], 'conversations': {<conversationInstance `moss`>: {'autoplay_failed': set()}, <conversationInstance `dried moss`>:
    {'autoplay_failed': set()}}, 'gold': 5, 'inventory': {<ItemInst [mummified mouse ID:d419db08f1d5] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [goat excrement ID:c4bcc30e369d] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [scroll ID:cf140555a70f] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [car keys ID:286f12167619] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [fish food jar ID:ec5f3fc3215f] [loc: north npc_inventory_place] [event:event str: None] >}, 'special_responses': {'dried moss': ['Eh yes! good soft, good...', "Mm, 's good squishy. Good trade."]}, 'trade_items': {<ItemInst [mummified mouse ID:d419db08f1d5] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [goat excrement ID:c4bcc30e369d] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [scroll ID:cf140555a70f] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [car keys ID:286f12167619] [loc: north npc_inventory_place] [event:event str: None] >, <ItemInst [fish food jar ID:ec5f3fc3215f] [loc: north npc_inventory_place] [event:event str: None] >}, 'will_not_sell': ['dried moss'], 'trade_start': 'You got nice-soft moss, mm? *hic*', 'trade_end': 'Bah, no more soft-moss? Beh-crz ih.', 'trade_intake': {'named_only': ['dried moss']}, 'thief_awareness': 5, 'location': <cardinalInstance north bridge (60df641d-b009-4363-b275-0942d4e93242)>, 'nicenames': {'generic': 'Bridge Troll'}, 'nicename': 'Bridge Troll', 'descriptions': {'generic': 'a bridge troll, green of skin and weathered, wearing a satchel over its shoulder and a loincloth protecting its dignity', 'npc_introduction': 'Stooped over and seemingly staring at a
    dandelion growing from the ground, you see a bridge troll. A patched leather satchel hangs loose over one shoulder, its weathered bare skin showing everywhere except for where it was covered by a thin, worn loincloth.'}, 'description': 'a bridge troll, green of skin and weathered, wearing a satchel over its shoulder and a loincloth protecting its dignity', 'introduction': 'Stooped over and seemingly staring at a dandelion growing from the ground, you see a bridge troll. A patched leather satchel hangs loose over one shoulder, its weathered bare skin showing everywhere except for where it was covered by a thin, worn loincloth.', 'conversation_parts': {'start': '*sniff* Eh, what you want?', 'end': 'Get away then.', 'trade_start': 'You got nice-soft moss, mm? *hic*', 'trade_end': 'Bah, no more soft-moss? Beh-crz ih.'}, 'convo_start': '*sniff* Eh, what you want?', 'convo_end': 'Get away then.', 'keywords': {'dried moss': {<conversationInstance `dried moss`>: '1'}}, 'slice_attack': '5', 'slice_defence': '5', 'smash_attack': '5', 'smash_defence': '5', 'encountered': True, 'acceptance'Exiting now.', "M'kay."], 'approval': ['Eh, guess so.'], 'disapproval': ["Hah, jokin'.", 'Nope.'], 'unsure': ['What?'], 'nothing_else': ["'s all there is.", "'s all to say."]}

NPC elements that can change: (description etc should always be generated at run, not saved. And speech etc don't change across runs.)
    - id
    - is_hidden
    - can_die
    - is_dead
    - conversations - do not save IDs, but conversation name if identifiable.(if not think of something else. Or maybe give conversations a specific code to refer to if naming them is silly. Might be better?)
    - gold
    - inventory
    - trade_items
    - thief_awareness
    - location
    - keywords

Re 'conversations' note above:
    currently conversation elements are given by the conversation topic, then just an int. For now just save the conversation topic. Or maybe they should be autogenerated, actually. If we save the relevant metadata, then the conversations should regen from the npc as required.

I kind of want to set up a smaller, simpler game with very few objects and events for testing this. The scale just makes it annoying. Useful for later testing, but for right now I might make a little play version.

Have found the old test_locs and test_events files, so am using those.


Still this happening:
[<  unlock gate with key  >]
 '-                      -'
Failed to find the correct function to use for <verbInstance unlock (26c132d3-2ad8-478e-abb0-7826254fc6c2)>: argument of type 'NoneType' is not a container or iterable

/why/. What did I change now?
Oh, actually, that was a good one to find. Technically the key doesn't open the gate, it opens the padlock. Fixed it now so it just says 'you can't' instead of erroring. May add an indicator of 'did you mean 'unlock padlock w key' for things that have attached lock-items etc later. #TODO.

So. With the standard priest NPC in the standard game, if you say 'cult', he runs the convo about the cult and mentions mother, then you can ask about mother. But for some reason, on the test version, that 'cult' convo doesn't work.

Huh. Why, when I cut a bunch of items/locations and move the priest to the graveyard, does the 'cult' keyword no longer start the.... Oh, the mother event. Right. Okay. will fix.

Okay, have that fixed. In my minimal events test file I hadn't included the event that triggers the mother questline.
Though that event is still marked as current. Hm. Surely should end immediately. Or I should not use an event at all there and just use the datapoints. That's far better, right? An event just to say 'you learned this' feels a bit much.

So the setup is:
            "3": {
                "has_requirements": false,
                "autoplay": false,
                "keywords": ["cult"],
                "speech": "Oh, you're starting to remember. Good. Though I do so hate that word. Your mother's around town somewhere, though whether she will talk to you after all this is questionable.\n      The rest of the congregation have... left.",
                "event": {"starts_event": "learn_about_cult"} # <- once you've asked about this, it starts this event.
                },
            "4": {
                "has_requirements": {"event": "learn_about_cult", "keyword": "mother"}, # <- and this one checks to see if that event is running. It should check for datapoints instead.
                "autoplay": false,
                "keywords": ["mother"]...}

Okay, fixed that I think. It's still events for now, will change it later. Trying not to get distracted.

But, why is
"can_die": "str_True",
 can_die a string? the "str_" part is part of the serialisation to send to savefile, but why is that not a bool the entire time?

okay, fixed. It was a string in the npc ref file for some reason. must've been tired.

Why are all the attack/defense numbers strings too? Will look into it later #TODO

12.39pm
Now up to getting events initialised. The items seem pretty good from what I can tell. Now just need to do a similar thing for reloading events.

Oh you know what? I'm going to add the type prefix to the IDs themselves. So I don't need to add it when saving, it'lls just self-report. That's far better.


hm.

key in existing keys: <ItemInst [iron key ID:6d7f8f6dd50d] [loc: north work shed] [event:'moss_dries' ID:b619a state: 2] > // val: {'iron key': {'key_is_placed_elsewhere': {'item_in_event': 'reveal_iron_key'}}}
item not in event: `reveal_iron_key` / key.event: <eventInst [moss_dries] [ID:b619a] [state: 2]>

items being assigned to the wrong event. Bet I have a variable name wrong somewhere.


Re: identifying by id:  the iron key is identified by both it's name and the event it's part of. If an event uses a specific item, it'll give a number, so the name part should only be used in cases where any item works. This is assumed to be true.
