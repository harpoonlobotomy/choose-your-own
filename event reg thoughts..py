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
