Okay. New scratch pad, because initing the events is hurting my head. No sleep, again, which doesn't help, but it shouldn't be quite this bad.

So:

For the initial init:

#    for event_name in event_dict:
#        events.add_event(event_name, event_dict[event_name])

Adds the base events for all events in the event_dict.
Does not add triggers or really much event data at all, but does add all attr by default and adds the limits_travel section to the event.

After that it runs

#   events.add_items_to_events(event_data)

which runs

        events.get_event_triggers(event, trigger_check = noun)
        events.get_event_item_names(event)
        assign_event_keys(event)

for each event. (If doing the initial init, it runs three full loops, one for each pass so they all have full datasets to work from, if doing a single event pass, just runs each once with the named event.)

#    events.get_event_triggers
gets all trigger data from event_data, builds a dict, and creates a trigger instance for each event, adding it to event.triggers, as well as handling the 'effects' section and applying starting attr to effected items for each started event.
(This should probably be separated out.)

"""
Notes:
    I need a way to hold all named items for an event during this process. If I use 'iron key' as a start trigger and 'iron key' is named again later, it should know to use the same one. I'll add a specifier in the dict (currently event defs is quite minimal).
    Also, maybe we get all the names first, and then apply all the items /after, and then generate the triggers. Instead of 'get some, make triggers, do effects by getting items by location /again/. Currently it's working fine, technically, but it's a brittle system and currently it's barely used. It'll fall apart later, the way it is now.
"""

After the triggers/effects, it runs

events.get_event_item_names(event)

where it takes the item instances (assuming they're instances) and applies them to
#   events.item_names[item.name] = item

Which I realise would be more useful if it separated by event, actually. That version was basically a quick lookup to see if any encountered noun_name even had a chance at being a trigger, for quick exclusion of most nouns. Might be worth keeping for that I guess, but given only one item instance can be attached per item.name, it's not very workable long-term. (Take drying_moss - the point is you can grab a few of them and they'll try at different times depending on when you grabbed them.)
So maybe it should be
#   events.item_names[item.name] = event
assuming that each item name is only in one event? But again, why assume that.
I want a way to quickly say 'an item of this name is involved in this event'.
So I guess
#   events.item_names[item.name].add(event)
would cover that; add as many eventInstances as have an item of that name, can allow for overlap etc.

"""
Note:
I need to specify all tags to be applied, and do them all at once. Currently they're being applied whenever, and redundantly often just to make sure it gets 'caught' somewhere. Bad, bad plan.
"""

#   assign_event_keys()
is basically fine, I think. Messy and looks bad, but I think it's basically fine.

#####

For single, added events:
They are discovered by

#   is_event_trigger(self, noun_inst, noun_loc, reason = None)
(currently only covering item_triggers, which I should amend, and it's messy af.)
First it checks to see if the noun_inst is known in the events.no_item_restriction. if found there, it carries on.
Theoretically it should start a new event if no match is found, but that's /inside of
if events.no_item_restriction.get(noun_inst.name):
 but after a for loop, so it'll never fail because... if it's in events.no_item_restriction, then surely it's in an event. Otherwise it'll never fail.

I need a new way of doing that. For the repeated events, specifically.
Honestly I should only initialise the events that start on runtime, and initialise the others when they're encountered.

Maybe a... pre-event-check. Could be a lil class. It stores the start trigger data (by name/location/whatever is given), and if a new, non-event-bearing item is encountered with that name, then it checks 'are you suitable to start this event'. Leave most of the checks in is_event_trigger to actually check for existing events, and leave the 'start events' separate. Hm.


Okay. So. Basic structure is... okay.

We go through event_dict. For all events with "starts_current":true, we init on event registry init.
For anything else, we make the dict, but store it for later.
Or does that make it harder. Shit. I mean if an item is required for a quest and it moves before the quest is triggered, it's going to fuck things up.
Okay, no - Two main quest types. 'standard' and 'generated' (need new names). Standard quests run once, with predetermined items (mostly). All required data to ascertain item identity etc is in the file. Initialise them all as I'm doing already, let there be future events, with fully tracked items /from init/. So if that random item moves before the quest is triggered, we still know that's the event item.
Generated-type, we make the dict, but don't start any event yet. We don't know what item instance will be used, and we don't want random str entries in item_instance expecting places.
We add item_name:event_name to a special dict for these (which I kind of do already but it tries to use instances, which breaks things immediately without a heap of exclusions). We do a check for encountered nouns, if they are named, then we check to see if they meet the criteria for that trigger item. If so, we init a new event with that noun as the relevant trigger item.

Okay. That works better.
And I need to break up the parts a bit. We should make the trigger dict in one stage, get it all neat and portable, then a) use it immediately thereafter for the standard events and b) store it to the event_intake class if it's a generated event.


Right now, these are all the things held for the event instances:

def __init__(self, name, attr):
        self.name = name
        self.id = str(uuid.uuid4())
        if attr.get("starts_current"):
            self.state:int = 1
        else:
            self.state:int = 2
        self.triggers = set() #all triggers, delineate start/end after this point.
        self.start_triggers = set() # just to make sure these are here so other things can be more solid.
        self.end_triggers = set()
        self.item_instances = set() #items affected by the event
        self.items = set() ## ## Explicitly (for the moment), item /names/, not instances.
        self.keys = set() ## items that effect the event
        self.msgs = attr.get("messages") # what prints when the event starts/ends/on certain cues
        self.limits_travel = False
        self.held_items = {}
        self.hidden_items = {}
        self.locked_items = {}
        self.start_trigger_location = None
        self.end_trigger_location = None
        self.no_item_restriction = {} # Keeping this on the event. [Item_name] = [instance]
        self.constraint_tracking = {} # [constraint_type (eg 'days')] = int(starts at 0)} #each instance triggers its own event, so one instance per event. At least for now, so I can track failures/successes by event state, instead of managing sub-event failures/successes. # might get rid of this and just use timed_triggers below instead.
        self.timed_triggers = set()

        for item in attr:
            setattr(self, item, attr[item])

        if attr.get("effects") and attr["effects"].get("limit_travel"):
                self.limits_travel = True
                if attr["effects"]["limit_travel"].get("cannot_leave"):
                    if not hasattr(self, "travel_limited_to"):
                        self.travel_limited_to = set()
                    for location in attr["effects"]["limit_travel"].get("cannot_leave"):
                        self.travel_limited_to.add(location)

Now that's fking ridiculous, right?

I don't need 'keys', because I'm explicitly holding end_triggers and start_triggers.

Actually maybe I just use an entirely separate class for generated events... But they'd still have to share format for Events to recognise/work with them. So maybe not.

Maybe an additional external thing? It's the tracking I'm thinking of. Most of the events aren't modified at all once they've started; they start, and when a trigger is hit, they end. During the middle they don't do anything, they just wait for triggers.

Maybe, for like the drying moss (don't know why that was my go-to time-based event but hey ho), it has sub events? so, the moss changes sightly on each day, instead of 'boom dry now' at day3. 
