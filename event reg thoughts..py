import verb_actions


#      Path for events added by noun_inst:

"""
is_event_trigger(self, noun_inst, noun_loc) called by verb_actions



if noun_inst.name in events.no_item_restriction[event_name]
    [ dict of event_name: set of item names]

    Check for event at events.get_item_triggers.
    >>>
        uses self.get_event_by_noun(event_name, noun_inst = trigger_check)
    to check if an event by that name is using that noun instance.
        if so, it returns the event, else returns None.
        if it finds an event, it
         >> leaves get_event_triggers and returns to is_event_trigger.
"""


"""

# Removing
        if not event and trigger_check: # if there's a noun provided
            event = events.add_event(event_name, event_entry)
            event.state = 1 # if event was added due to a trigger, start it immediately.

from get_trigger_events, it makes it too hard.

Currently, it doesn't use item_data at all. It really needs to. The event data for 'moss' is really minimal, so it needs to plan to draw item_def data.


okay events.items_to_events[event_item] = event should add every item instance to the dict with its relevant event at initialisation.
Currently I think it's adding it twice, once in trigger initialisation and once in event initialisation, but I want to run a test through and check that /all/ of them hit twice before I remove one.

 events.no_item_restriction[self.item_inst.name].add(event) already keeps a dict very much like this, but that's for only no_item_restricted items. Guess I could keep that to event>item and remove the

 event.no_item_restriction[self.item_inst.name].add(self.item_inst) ?


 if events.no_item_restriction.get(self.item_inst.name):
    <no, I still need a middle step here to get the event instances. Will keep the extra dict for now, remove it later. I need the events level one to be by name so I can check quickly if 'moss' exists.
    events.items_to_events[event_item] = event

Oh jeez, item_data-created events don't even get access to triggers. yeah that's a wreck.

Well actually, is there any data to be had from item_defs that /isn't/ in loc_data or event_data? Shouldn't be, right? Event data is 'item concepts', and a whole concept isn't likely to be part of an event. Or I guess, moss disproves that, every default moss is part of an event. But, the moss-relevant data for the eventReg is in event_defs. It doesn't need descriptions etc.

... We already bring registry into get_event_triggers. This shouldn't even be a consideration.
"""

"""
first run after today's edits:

event name: <eventInstance mermaid_grotto_appears (48f9e55b-8753-4a14-a680-20de3bfa1d4d, event state: 2>, event: None, trigger_check: None
TRIGGER DICT: {'event': <eventInstance mermaid_grotto_appears (48f9e55b-8753-4a14-a680-20de3bfa1d4d, event state: 2>, 'trigger_model': 'item_trigger', 'trigger_type': 'start_trigger', 'trigger_item': 'ocean crown', 'trigger_item_loc': None, 'trigger_actions': ['item_in_inv'], 'item_flags_on_start': None, 'item_flags_on_end': None}
event name: <eventInstance reveal_iron_key (2f6a6af0-a493-4e5a-9f4d-3386a2273634, event state: 1>, event: None, trigger_check: None
TRIGGER DICT: {'event': <eventInstance reveal_iron_key (2f6a6af0-a493-4e5a-9f4d-3386a2273634, event state: 1>, 'trigger_model': 'item_trigger', 'trigger_type': 'end_trigger', 'trigger_item': <ItemInstance local map (32433b65-d183-4068-9822-222de6305711)>, 'trigger_item_loc': <cardinalInstance north work shed (506092bf-53d9-4313-9dbc-47b3544d4399)>, 'trigger_actions': ['item_in_inv'], 'item_flags_on_start': {}, 'item_flags_on_end': None}
event name: <eventInstance moss_dries (d281bc94-7e3d-4087-a36a-f6c8d863adc4, event state: 2>, event: None, trigger_check: None
TRIGGER DICT: {'event': <eventInstance moss_dries (d281bc94-7e3d-4087-a36a-f6c8d863adc4, event state: 2>, 'trigger_model': 'item_trigger', 'trigger_type': 'start_trigger', 'trigger_item': <ItemInstance moss (b77efc2b-5cb5-4844-83cc-4943ebf131c2)>, 'trigger_item_loc': <cardinalInstance east graveyard (971bb270-668b-41f0-8e9d-ac8a9bdb582b)>, 'trigger_actions': ['item_in_inv'], 'item_flags_on_start': None, 'item_flags_on_end': None}
TRIGGER DICT: {'event': <eventInstance moss_dries (d281bc94-7e3d-4087-a36a-f6c8d863adc4, event state: 2>, 'trigger_model': 'item_trigger', 'trigger_type': 'end_trigger', 'trigger_item': 'moss', 'trigger_item_loc': None, 'trigger_actions': ['item_in_inv_continued'], 'item_flags_on_start': None, 'item_flags_on_end': None, 'trigger_constraint': {'time_constraint': {'days': 3}, 'constraint_tracking': {'days': 0}}, 'item_model': 'failure_trigger', 'failure_trigger': {'no_item_restriction': True, 'trigger_item': 'moss', 'trigger': ['item_removed_from_inv']}}
event name: <eventInstance graveyard_gate_opens (ba8608bb-2e81-4373-843e-61849b09fb45, event state: 1>, event: None, trigger_check: None
TRIGGER DICT: {'event': <eventInstance graveyard_gate_opens (ba8608bb-2e81-4373-843e-61849b09fb45, event state: 1>, 'trigger_model': 'item_trigger', 'trigger_type': 'end_trigger', 'trigger_item': <ItemInstance padlock (881642b7-ae08-4928-9385-88d2de81dba4)>, 'trigger_item_loc': <cardinalInstance north graveyard (53352177-9121-4125-9f9c-022853d4effc)>, 'trigger_actions': ['item_broken', 'item_unlocked'], 'item_flags_on_start': {'can_pick_up': False, 'requires_key': 'iron key', 'key_is_placed_elsewhere': {'item_in_event': 'reveal_iron_key'}}, 'item_flags_on_end': {'can_pick_up': True}}
Get event item names: EVENT:: <eventInstance mermaid_grotto_appears (48f9e55b-8753-4a14-a680-20de3bfa1d4d, event state: 2>, type: <class 'eventRegistry.eventInstance'>
This item does not have an instance: ocean crown (in event mermaid_grotto_appears)
Get event item names: EVENT:: <eventInstance reveal_iron_key (2f6a6af0-a493-4e5a-9f4d-3386a2273634, event state: 1>, type: <class 'eventRegistry.eventInstance'>
Get event item names: EVENT:: <eventInstance moss_dries (d281bc94-7e3d-4087-a36a-f6c8d863adc4, event state: 2>, type: <class 'eventRegistry.eventInstance'>
This item does not have an instance: moss (in event moss_dries)
Get event item names: EVENT:: <eventInstance graveyard_gate_opens (ba8608bb-2e81-4373-843e-61849b09fb45, event state: 1>, type: <class 'eventRegistry.eventInstance'>

"""
