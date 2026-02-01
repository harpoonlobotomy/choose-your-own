# event registry, to manage events. Obviously.

"""
Only event so far: The one I'm writing right now.
Cannot travel outside the graveyard until the gate in graveyard north is unlocked.
So the event 'ends' when the gate is unlocked; the event starts on runstart.
if the padlock is unlocked or broken, it falls to the ground and the gate creaks open slightly. At this point, event ends, and travel to other locations is accessible.
"""

import pprint
import uuid

from itemRegistry import ItemInstance, get_loc_items
from logger import logging_fn
from misc_utilities import assign_colour

event_states = {
    "past": 0,
    "current": 1,
    "future": 2
}

event_state_by_int = {
    0: "past/completed",
    1: "current/ongoing",
    2: "future/not started"
}

def load_json():
    import json
    event_data = "event_defs.json"
    with open(event_data, 'r') as loc_data_file:
        event_dict = json.load(loc_data_file)
    return event_dict

event_dict = load_json()

event_effects = ["hold_item", "lock_item", "hide_item", "limit_travel"]



class eventInstance:
    """
    {
    "graveyard_gate_opens": {
        "starts_current":true,
        "end_trigger":
        {"item_trigger": {
            "trigger_name": "padlock", "trigger_location": "graveyard east", "trigger": ["item_broken", "item_unlocked"], "item_flags": {"can_pick_up": false, "requires_key": "iron_key", "flags_on_event_end": {"can_pick_up": true}}
        }
        },
        "effects": {"limit_travel": {"cannot_leave": "graveyard"}},
        "messages": {"start_msg": "", "end_msg": "", "held_msg": "Until the gate's unlocked, you don't see a way out of here."}
    },
    """

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
        self.items = set() ## items affected by the event
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

        if attr.get("effects"):
            if attr["effects"].get("limit_travel"):
                self.limits_travel = True

                if attr["effects"]["limit_travel"].get("cannot_leave"):
                    if not hasattr(self, "travel_limited_to"):
                        self.travel_limited_to = set()
                    for location in attr["effects"]["limit_travel"].get("cannot_leave"):
                        self.travel_limited_to.add(location)

        """
        self.event_items
        self.event_triggers
        """
    def __repr__(self):
        return f"<eventInstance {self.name} ({self.id}, event state: {self.state}>"#, all attributes: {self.attr})>"

trigger_actions = ["item_in_inv", "item_broken", "item_unlocked"]

class Trigger:

    def __init__(self, trigger_dict, event:eventInstance):

        print(f"TRIGGER DICT: {trigger_dict}")
        """
TRIGGER DICT: {'event': <eventInstance graveyard_gate_opens (27df1d29-6d80-4329-b955-77f39de45be5, event state: 1>,
'trigger_model': 'item_trigger',
'trigger_type': 'end_trigger',
'trigger_item': <ItemInstance padlock (f5f172e4-aa83-4a42-853b-cc3545e3d0d3)>,
'trigger_item_loc': <cardinalInstance north graveyard (ffd69823-dfe7-4893-a94c-9470fb7742e4)>,
'trigger_actions': ['item_broken', 'item_unlocked'],
'item_flags_on_start': {'can_pick_up': False, 'requires_key': 'iron key',
    'key_is_placed_elsewhere': {'item_in_event': 'reveal_iron_key'}},
'item_flags_on_end': {'can_pick_up': True}}

        """
        self.id = str(uuid.uuid4())
        self.event = event#trigger_dict["event"]
        self.state = event.state

        self.triggers = set() #item_broken, 'item_in_inv', etc.
        """
        trigger_dict = {
            "event": event,
            "trigger_model": "item_trigger",
            "trigger_type": trigger,
            "trigger_item": trigger_item,
            "trigger_item_loc": trigger_loc,
            "trigger_actions": trigger_actions,
            "item_flags_on_start": item_flags_on_start,
            "item_flags_on_end": item_flags_on_end
            }
            """
        if trigger_dict["trigger_type"] == "end_trigger":
            self.start_trigger = False
            self.end_trigger = True
            event.end_triggers.add(self)
        else:
            self.start_trigger = False
            self.end_trigger = True
            event.start_triggers.add(self)

        if trigger_dict["trigger_model"] == "item_trigger":
            self.is_item_trigger = True
            if self.is_item_trigger:
                if not trigger_dict.get("no_item_restriction") or isinstance(trigger_dict["trigger_item"], ItemInstance):
                    self.item_inst = trigger_dict["trigger_item"]
                else:
                    if (isinstance(trigger_dict["trigger_item"], list|set|tuple) and len(len(trigger_dict["trigger_item"]) == 1)):
                        self.item_inst = trigger_dict["trigger_item"][0]

                event.items.add(self.item_inst)
                events.items_to_events[self.item_inst] = event
                self.item_inst_loc = trigger_dict["trigger_item_loc"]
                if self.end_trigger:
                    event.end_trigger_location = self.item_inst_loc
                self.item_flags_on_start = trigger_dict["item_flags_on_start"]
                self.item_flags_on_end = trigger_dict["item_flags_on_end"]

                if isinstance(self.item_inst, ItemInstance):
                    setattr(self.item_inst, "event", event)
                    if self.state == 1:
                        if self.item_flags_on_start:
                            for flag in self.item_flags_on_start:
                                setattr(self.item_inst, flag, self.item_flags_on_start[flag])
    ## NOTE: Only applies to events that had item instances at init, so the default event for moss drying does not yet have instances. Not sure what to do about that yet.

                    #if self.item_flags_on_end:
                    #    for flag in self.item_flags_on_end:
                    #        setattr(self.item_inst, flag, self.item_flags_on_end[flag]) # duh, don't set these flags at the start, they're for the /end/.

                if trigger_dict.get("trigger_constraint"):
                    self.time_constraint = trigger_dict["trigger_constraint"].get("time_constraint")
                    event.timed_triggers.add(self)
                    #   how long the event needs to run in order to succeed (days/less time (time blocks are roughly 2 hrs))
                    self.constraint_tracking:dict = trigger_dict["trigger_constraint"].get("constraint_tracking")
                    #event.constraint_tracking = {trigger_dict["item_trigger"]["trigger_constraint"].get("constraint_tracking")} # turning this one off, will use event.timed_triggers to get trig.constraint_tracking.

                    # if constraint_tracking:
                    #   when day advances, add 1 to any constraint_tracking value (constraint_tracking == int.)
                    ## TODO: set up constraint checking for timed events.

                    if isinstance(self.item_inst, ItemInstance):
                        item_name = self.item_inst.name
                    else:
                        item_name = self.item_inst
                    if not events.no_item_restriction.get(item_name):
                        events.no_item_restriction[item_name] = set()
                    events.no_item_restriction[item_name].add(event)

                    if not event.no_item_restriction.get(item_name):
                        event.no_item_restriction[item_name] = set()
                    event.no_item_restriction[item_name].add(self.item_inst) # Keeping this on the event. [Item_name] = [instance]
            # TODO: only works if items are instances already. Might need to keep a dict of things that don't have instances? Or just account for it later, this should only occur in the generating events so maybe I can just make it part of the intended process.

        if trigger_dict["trigger_model"] == "failure_trigger":
            self.item_inst = trigger_dict["trigger_item"]
            event.items.add(self.item_inst) # ,aybe don't need this one.
            events.items_to_events[self.item_inst] = event

        if isinstance(trigger_dict["trigger_actions"], str):
            self.triggers.add(trigger_dict["trigger_actions"])
        else:
            for action in trigger_dict["trigger_actions"]:
                self.triggers.add(action)


    def __repr__(self):
        return f"<triggerInstance {self.id} for event {self.event.name}, event state: {event_state_by_int[self.state]}, {((f'Trigger item: {self.item_inst.name}' if isinstance(self.item_inst, ItemInstance) else f'Trigger item: {self.item_inst}') if self.is_item_trigger else None)}>"



class eventRegistry:

    def __init__(self):

        self.events = set()
        self.by_id = {}
        self.by_name = {}
        self.by_state = {}
        self.trigger_items = {}
        self.travel_is_limited = False
        self.triggers = set()
        self.item_names = dict()
        self.items_to_events = dict() # just every item attached to an event, for now. Won't keep this but it'll be convenient for testing the general shape of things.
        self.no_item_restriction = {} # no I was right the first time. noun_name: event_name. Then check if noun in events by that name. Makes way more sense. Don't check all events then all items, check if the item is viable before events are even considered.

        # Actual way of doing it: event_name:item_name # event NAME, so it can start a new event when the item is encountered.
        # dict: item_name: event (assuming item_trigger) May only allow one event per item, though could make it a set. Though actually it's already checking all events when items are encountered, so really should just do it in that same pass. Okay.#
        self.timed_triggers = set()

        for state in event_states.values():
            self.by_state[state] = set() ## really don't need these and the current/past/future. Will probably use this alone instead, it'll be easier to set up the direction.



                    #if event_dict[event][trigger]["item_trigger"].get("trigger_location"):
                        #event event_dict[event][trigger]["item_trigger"]["trigger_location"]:
        # so braindead right now. Maybe I just ignore the whole trigger_location thing in this case because you can only pick up an item from its start location.

    def add_event(self, event_name, event_attr=None):

        if not event_attr:
            event_attr = event_dict.get(event_name)
        event = eventInstance(event_name, event_attr)
        self.events.add(event)
        self.by_id[event.id] = event
        if not self.by_name.get(event.name):
            self.by_name[event.name] = set()
        self.by_name[event.name].add(event)

        if hasattr(event, "starts_current"):
            self.by_state[1].add(event)
            event.event_state = 1 # (current event)
            if event.limits_travel:
                self.travel_is_limited = True

        else:
            self.by_state[2].add(event)
            event.event_state = 2 # (future event)

        if self.timed_triggers:
            events.timed_events.add(self)

        return event, event_attr

    def get_event_by_noun(self, event_name, noun_inst):

        if event_name:
            event = self.event_by_name(event_name)
            #for event in self.event_by_name(event_name):
            if noun_inst in event.items:
                noun_inst.event = event
                return event

        return


    def manage_constraint_tracking(event):
        """
        Call this from the day/time management (set_up_game, probably) to check if any time-based events have completed.
        """
        if event.timed_triggers:
            for trigger in event.timed_triggers:
               constraint_current = trigger.constraint_tracking
               event_constraint = trigger.time_constraint
               for constraint_option in ("days", "timeblocks"):
                   if event_constraint.get(constraint_option):
                       if constraint_current[constraint_option] == event_constraint[constraint_option]:
                           print("Event completed, let something happen here.")
                           print("Then once it happens, run end_event.")
                           return True

        return False

    def get_event_triggers(self, event_name = None, event = None, trigger_check = None):

        #event_dict = load_json()

        from env_data import locRegistry as loc
        from itemRegistry import registry

        print(f"event name: {event_name}, event: {event}, trigger_check: {trigger_check}")
        if event and not event_name:
            event_name = event.name

        if isinstance(event_name, eventInstance):
            event = event_name
            event_name = event.name

        event_entry = event_dict.get(event_name)

        for trigger in ("start_trigger", "end_trigger"):
            trigger_dict = {}
            if event_entry.get(trigger):
                if event_entry[trigger].get("item_trigger"):
                    trigger_item = event_entry[trigger]["item_trigger"]["trigger_item"]
                    trigger_loc = event_entry[trigger]["item_trigger"].get("trigger_location")
                    trigger_actions = event_entry[trigger]["item_trigger"]["trigger"]
                    item_flags_on_start = event_entry[trigger]["item_trigger"].get("flags_on_event_start")
                    item_flags_on_end = event_entry[trigger]["item_trigger"].get("flags_on_event_end")
                    if trigger_loc:
                        trigger_loc = loc.by_cardinal_str(trigger_loc)
                        loc_items = registry.get_item_by_location(trigger_loc)
                        for item in loc_items:
                            if item.name == trigger_item:
                                trigger_item = item
                                break

                    elif event_entry[trigger]["item_trigger"].get("no_item_restriction"):
                        if trigger_check:
                            trigger_item = trigger_check
                        else:
                            trigger_items = registry.instances_by_name(trigger_item)
                            for item in trigger_items:
                                if not hasattr(item, "event"):
                                    trigger_item = item
                                    break
                            # Assumes that an item of that name will be correct by default. Not ideal. Should probably check it has the event tag, but here we're ruling those /out/ instead of prioritising them. TODO: Will work on this later.

                    trigger_dict = {
                        "event": event,
                        "trigger_model": "item_trigger",
                        "trigger_type": trigger,
                        "trigger_item": trigger_item,
                        "trigger_item_loc": trigger_loc,
                        "trigger_actions": trigger_actions,
                        "item_flags_on_start": item_flags_on_start,
                        "item_flags_on_end": item_flags_on_end
                        }
                    if event_entry[trigger]["item_trigger"].get("trigger_constraint"):
                        trigger_dict["trigger_constraint"] = event_entry[trigger]["item_trigger"]["trigger_constraint"]

                if event_entry[trigger].get("failure_trigger"):
                    trigger_dict["item_model"] = "failure_trigger"
                    trigger_dict["failure_trigger"] = event_entry[trigger]["failure_trigger"]

                event.triggers.add(Trigger(trigger_dict, event))
                events.items_to_events[trigger_item] = event

        if event_entry.get("effects"):
            for effect in event_entry["effects"]:
                event_item = None
                if effect in event_effects:
                    if "item_loc" in event_entry["effects"][effect]:
                        event_loc = loc.by_cardinal_str(event_entry["effects"][effect]["item_loc"])
                        loc_items = registry.get_item_by_location(event_loc)
                        for item in loc_items:
                            if item.name == event_entry["effects"][effect]["item_name"]:
                                event_item = item
                                break

                        if effect == "hide_item":
                            event.hidden_items[event_item] = event_loc
                            setattr(event_item, "is_hidden", True)
                            setattr(event_item, "can_pick_up", False)
                            event.items.add(event_item)
                            events.items_to_events[event_item] = event
                            setattr(event_item, "event", event)

                        elif effect == "hold_item":
                            event.held_items[event_item] = event_loc
                            setattr(event_item, "can_pick_up", False)
                            event.items.add(event_item)
                            events.items_to_events[event_item] = event
                            setattr(event_item, "event", event)

                        elif effect == "lock_item":
                            event.locked_items[event_item] = event_loc
                            setattr(event_item, "is_locked", True)
                            setattr(event_item, "can_pick_up", False)

                            event.items.add(event_item)
                            events.items_to_events[event_item] = event
                            setattr(event_item, "event", event)

                else:
                    print(f"Effect not in event_effects: {event_entry["effects"][effect]}")
                    exit()
        return event

    def get_event_item_names(self, event):

        print(f"Get event item names: EVENT:: {event}, type: {type(event)}")

        def get_items_inner(event):
            for item in event.items:
                #print(f"ITEM IN EVENT ITEMS: {item}")
                if isinstance(item, ItemInstance):
                    events.item_names[item.name] = item
                    setattr(item, "event", event) # TODO: Doing this way too often, need to find the single choke point they all pass through no matter where they're added from.
                else:
                    print(f"This item does not have an instance: {item} (in event {event.name})")

        if isinstance(event, str):
            event_options = self.event_by_name(event)
            for event in event_options:
                get_items_inner(event)
                return

        get_items_inner(event)

    def event_by_state(self, state)-> set:
        if not isinstance(state, int):
            if (isinstance(state, str) and len(state)==1):
                state = int(state)
            elif state in event_states:
                state = event_states[state]

        return self.by_state.get(state)


    def event_by_id(self, event_id)-> eventInstance:

        if not isinstance(event_id, str):
            event_id = str(event_id)

        instance = self.by_id(event_id)
        if instance:
            return instance

    def event_by_name(self, event_name:str)-> eventInstance: # actually |list but the typehints of it thinking it starts as eventInstance is more useful.

        if isinstance(event_name, str):
            instance = self.by_name.get(event_name)

            if instance:
                if isinstance(instance, eventInstance):
                    return instance
                if isinstance(instance, set|list|tuple):
                    if len(instance) == 1:
                        if isinstance(instance, set|tuple):
                            return list(instance)[0]
                        return instance[0]
                    else:
                        print(f"Multiple instances in {instance} for name {event_name}. Haven't dealt with this yet.")
                        return instance

    def play_held_msg(self, event=None, print_txt=False):

        if self.travel_is_limited:
            if event == None:
                holder = self.held_at.get("held_by") # currently only works if you can only be restricted by one event, will have to change this later.
                if holder.msgs.get("held_msg"):
                    if print_txt:
                        print(holder.msgs["held_msg"])
                    return holder.msgs["held_msg"]

            else:
                if event.event_state == 1:
                    if event.msgs.get("held_msg"):
                        if print_txt:
                            print(event.msgs["held_msg"])
                        return event.msgs["held_msg"]

    def play_event_msg(self, msg_type="held", event=None, print_txt=True):
        logging_fn()

        def print_current(event, state_type="held", print_text=False):

            if event.msgs.get(f"{state_type}_msg"):
                msg = event.msgs[f"{state_type}_msg"]
                if print_text:
                    print("\n", assign_colour(msg, colour="event_msg"))
                return msg


            return f"Nothing to print print for event `{event}`, msg_type `{msg_type}`." # remove this later and replace with a type-defined default.

        if "_msg" in msg_type:
            msg_type = msg_type.replace("_msg", "")

        if msg_type == "held":

            if self.travel_is_limited:
                if event == None:
                    event = self.held_at.get("held_by")

                return print_current(event, state_type="held", print_text=print_txt)

        if not event:
            print("Need to define event for start/end messages.")
            return ""

        if msg_type == "start":
            return print_current(event, state_type="start", print_text=print_txt)

        if msg_type == "end":
            if not event:
                print("Need to define event for start/end messages.")
                return ""

            return print_current(event, state_type="end", print_text=print_txt)


    def start_event(self, event_name:str, event:eventInstance=None):
        logging_fn()

        # Note that events can be concurrent, so setting a current event does not necessarily remove an existing event.
        if not event:
            to_be_current = self.event_by_name(event_name) # assumes all events already init, does not support dynamic event generation.
            #TODO: change event_by_name only supporting one instance per name.
        else:
            to_be_current = event

        event_state = to_be_current.event_state

        if event_state == 0:
            print(f"Event {event_name} is already over.")
            return
        if event_state == 1:
            print(f"Event {event_name} is already happening.")
            return

        for trigger in to_be_current.triggers:
            trigger.state == 1

        self.by_state.get(2).remove(to_be_current)
        self.by_state.get(1).add(to_be_current)
        to_be_current.event_state = 1

        if to_be_current in self.by_state.get(1): # redundant but just in case anything went super wrong:
            to_be_current.event_state = 1
            self.play_event_msg("start_msg", to_be_current)
            #if hasattr(to_be_current, "start_msg") and getattr(to_be_current, "start_msg"): ## 'get' here excludes if null, which in this case is what I want.
            #    print(to_be_current.start_msg)
            #else:

        else:
            print(f"Cannot set event {event_name} as current event, because it is not present in future_events: {self.future_events}")
            exit()

        if hasattr(to_be_current, "effects"):
            if to_be_current.effects.get("limit_travel"):
                print(f"Started event limits travel: {to_be_current.effects["limit_travel"]}")# {"cannot_leave": "graveyard"}}
                if getattr(to_be_current, "msgs"):
                    self.play_event_msg("start_msg", to_be_current)
                    #if to_be_current.msgs.get("start_msg"):


    def end_event(self, event_name, trigger:Trigger=None, noun_loc=None):

        print_desc_again = False # Use to reprint the local description if items have become unhidden. Do it in a better way later, for now this will do.
        logging_fn()
        if isinstance(event_name, str):
            event_to_end = self.event_by_name(event_name)
        else:
            event_to_end = event_name

        if event_to_end in self.event_by_state(1):
            self.by_state[1].remove(event_to_end)
            self.by_state[2].add(event_to_end)
            if event_to_end in self.by_state[2]: # redundant but just in case anything went super wrong:
                event_to_end.event_state = 2

            if event_to_end.limits_travel:
                no_limits = True
                for event in self.by_state:
                    still_limited_to = set()
                    if event != event_to_end and hasattr(event, "limits_travel"):
                        for loc in event.travel_limited_to:
                            still_limited_to.add(loc)
                        no_limits = False


                if no_limits:
                    self.travel_is_limited = False
                    self.travel_limited_to = set()
                else:
                    self.travel_limited_to = still_limited_to #reinstate the limits imposed by any other events but remove your own.

# The following all assume that all events only act on unique items (eg an item won't be hidden by multiple events (or if they are, cannot be revealed by any old one of them. Going with it to keep it simple for now.))
            if event_to_end.hidden_items:
                pop_me = set()
                for item in event_to_end.hidden_items:
                    setattr(item, "is_hidden", False)
                    setattr(item, "can_pick_up", True)
                    pop_me.add(item)
                    print_desc_again = True

                if pop_me:
                    for item in pop_me:
                        event_to_end.hidden_items.pop(item)

            if event_to_end.held_items:
                pop_me = set()
                for item in event_to_end.held_items:
                    setattr(item, "can_pick_up", True)
                    pop_me.add(item)

                if pop_me:
                    for item in pop_me:
                        event_to_end.held_items.pop(item)


            if event_to_end.locked_items:
                pop_me = set()
                for item in event_to_end.locked_items:
                    setattr(item, "is_locked", False)
                    pop_me.add(item)

                if pop_me:
                    for item in pop_me:
                        event_to_end.locked_items.pop(item)

            print("Need a section here that removes itemInstances from events.items. Or maybe not, if one day it'd be useful to know that this is the coin you gave to the witch in exchange for your left eye or smth")

            self.play_event_msg(msg_type="end", event=event_to_end)

            if trigger:
                trigger.state = 0
            if print_desc_again:
                from env_data import get_loc_descriptions
                get_loc_descriptions(event_to_end.end_trigger_location)
                print(f"\nYou're facing {assign_colour(event_to_end.end_trigger_location.name)}. {event_to_end.end_trigger_location.description}")
        else:
            print(f"Cannot set event {event_name} as ended event, because it is not present in current_events: {self.event_by_state(1)} (type: { type(self.event_by_state(1))})")
            exit()

    def check_movement_limits(self)-> dict:

        allowed_locations = {}
        allowed_locations_by_loc = {}
        for event in self.by_state[1]:
            if hasattr(event, "travel_limited_to"):
                allowed_locations[event] = set()
                for loc in event.travel_limited_to:
                    allowed_locations[event].add(loc)
                    allowed_locations_by_loc.setdefault(loc, set()).add(event)

        #return allowed_locations
        return allowed_locations_by_loc

    def is_event_trigger(self, noun_inst, noun_loc, reason = None):
        logging_fn()

        print(f"start of event_trigger:\nnoun inst: {noun_inst}, noun_loc: {noun_loc}, reason: {reason}.")
        def check_triggers(event, noun, reason):
            print(f"start of check_triggers: event: {event}, noun: {noun}, reason: {reason}")
    # Reason == str containing the key phrase of the trig.trigger. eg 'added_to_inv'
            if event.end_triggers:
                print(f"event.end_triggers: {event.end_triggers}")
                for trig in event.end_triggers:
                    print(f"For trig in event.end_triggers: {trig}")
                    print(f"VARS: {vars(trig)}")
                    if hasattr(trig, "constraint_tracking"):
                        print("Whether the event ends or not depends on this constraint. Maybe it should be checked earlier, I feel like I do this check in item_interactions. Needs to be one or the other.")
                        exit()
                    #print(f"TRIG: {trig}, vars: {vars(trig)}")
                    if trig.is_item_trigger:
                        print("trig is item trigger")
                        if trig.item_inst == noun:
                            print("item inst == noun")
                            if reason in trig.triggers:
                                if trig.item_inst_loc and trig.item_inst_loc != noun_loc:
                                    continue # fail if the fail should have a location but doesn't. Doesn't apply to any current ones, but if you have to read a book under a specific tree, this would apply.

                                self.end_event(event, trig, noun_loc)
                                break
                        else:
                            print(f"item inst {trig.item_inst} =! noun {noun}")
#events.no_item_restriction[self.item_inst.name].add(event) # eventsRegistry holds instance name to event (this instance name gets managed by this event)
#event.no_item_restriction[self.item_inst.name].add(self.item_inst) #the eventInstance holds (this item name goes to these itemInstances)
        print(f"Events.no_item_restriction: {events.no_item_restriction}")
        if events.no_item_restriction.get(noun_inst.name):
            print(f"events.no_item_restriction gets noun_inst.name: {noun_inst.name}")
            existing_event = False
            event_name = None
            for event in events.no_item_restriction[noun_inst.name]:
                print(f"event in no_item_rest: {event}")
                event_name = event.name # assume only one event per name, will work for now.
                if event.no_item_restriction[noun_inst.name] == noun_inst:
                    existing_event = True
                    print(f"Item is part of an existing event: {event}")
                    print("Do anything involving item triggers here (eg if dropping it fails the event, that will happen here.)")
                    check_triggers(event, noun=noun_inst, reason=reason)
                    return

            if not existing_event:
                print("an unrestricted noun needs an event made.")
                event, event_entry = self.add_event(event_name)
                add_items_to_events(event=event, noun_inst=noun_inst)
                self.start_event(event_name = event.name, event = event)
                print(f"Event has now been created [{event}]. No need to check for triggers as no event will have an event start and finish in the same item interaction. I assume.")
                return

        print(f"events.items_to_events: {events.items_to_events}")
        if events.items_to_events.get(noun_inst):
            print(f"noun inst is in items_to_events: {events.items_to_events.get(noun_inst)}")
            event = events.items_to_events[noun_inst]
            print(f"Event: {event}")
            if event.state == 1:
                check_triggers(event, noun_inst, reason)

            #pausing that for now, it seems far too messy.

            # Really need to test how this part works, I'm not sure if it will at all. But it's nearly 4am so I should sleep.
            #if events.no_item_restriction.get(event.name) and events.no_item_restriction[event.name].get(noun_inst.name):
            #    event = events.get_event_triggers(event_dict, event.name, trigger_check=noun_inst) # will create new event if there is none
            #    if event.state == 1: # means the event already started before the prev line, so is not new/does not need items added.
            #        continue
            #    add_items_to_events(event = event, noun_inst=noun_inst)

            #assert isinstance(event, eventInstance), "printing if this is not an instance"

            #if event.event_state != 1:
            #    ## Events that are started (ie those by triggers in no_item_restriction) should be dealt with above.
            #    continue
            #for item in event.keys:



    """
    What else do I need here.
    Check for starting triggers: check events in future_events, what their trigger types are.
    Maybe if a trigger can only be changed in a particular area, check that first?
    Well I don't need a global trigger check, because the trigger itself should trigger it.
    Maybe though, have an ongoing 'upcoming triggers' dict, of just potential event triggers exclusively. So nothing from past events, no later-stage triggers, etc, just the start-trigger for any future events that don't have other prerequisites and the current-stage trigger for any current triggers. Then if an item/scene trigger happens, we check against this dict, not against all triggers in the trigger defs. Yeah I like that I think.
    """

    #def set_potential_triggers(self):
    #    for event in events.by_name:


events = eventRegistry()


def add_items_to_events(event = None, noun_inst = None):

    def assign_event_keys(event):

        for item in event.items:
            if hasattr(item, "requires_key"):
                required_key = item.requires_key
                if hasattr(item, "key_is_placed_elsewhere"):
                    if isinstance(item.key_is_placed_elsewhere, dict):
                        if item.key_is_placed_elsewhere.get("item_in_event"):
                            event_with_key = item.key_is_placed_elsewhere["item_in_event"]
                            key_event = events.event_by_name(event_with_key)

                            key_item_names = {}

                            for potential_key in key_event.items:
                                if isinstance(potential_key, ItemInstance):
                                    key_item_names[potential_key.name] = potential_key

                            if key_item_names.get(required_key):
                                item.requires_key = key_item_names[required_key]
                        else:
                            print("Later, can add item locations to the event dict and find them through this. For now it only does event-held keys though.")
                else:
                    if events.item_names.get(required_key):
                        item.requires_key = events.item_names[events.item_names[required_key]]

    if noun_inst:
        noun = noun_inst
    else:
        noun = None

    if event:
        events.get_event_triggers(event, trigger_check = noun)
        events.get_event_item_names(event)
        assign_event_keys(event)

    else:
        for event in events.events:
            events.get_event_triggers(event) # each loop done separately so event_item_names gets the complete dataset from the previous.

        for event in events.events:
            events.get_event_item_names(event)

        for event in events.events:
            assign_event_keys(event)

"""
blocking this out for now so I can do everything in the above, this part will just fail now because it doesn't use triggers at all. It does give us the instances directly, which is very nice, but I think this is likely better. Can always just send all event-marked items over and incorporate that into the above; if it needs an instnace named x at loc y, we can give it a set of instances to pick from as a priority before looking through locations etc. But the trigger application etc, should all be done above for all sources.
if item_data:
    for item in item_data:
        event_name = item_data[item].get("event_name")
        if events.event_by_name(event_name):
            event = events.event_by_name(event_name)
            event.items.add(item_data[item].get("item"))
            if item_data[item].get("event_key"):
                event.keys.add(item_data[item].get("item"))
                if event_dict[event_name].get("end_trigger"):
                    if event_dict[event_name]["end_trigger"].get("item_trigger"):
                        if event_dict[event_name]["end_trigger"]["item_trigger"].get("item_flags"):
                            for flag in event_dict[event_name]["end_trigger"]["item_trigger"]["item_flags"]:
                                item_data[item].get("item").flag = event_dict[event_name]["end_trigger"]["item_trigger"]["item_flags"].get(flag)

                        if event_dict[event_name]["end_trigger"]["item_trigger"].get("flags_on_event_end"):
                            if not hasattr(event, "flags_to_restore"):
                                event.flags_to_restore = {}
                            event.flags_to_restore[item] = event_dict[event_name]["end_trigger"]["item_trigger"]["flags_on_event_end"]
"""

"""
So to conceptuialise a bit:
padlock is a key item.
When it is unlocked, event ends.
so itemreg needs to be aware of the trigger.
**  Wherever the item goes from item.is_locked to item.is_unlocked needs to identify events.  **
Then events checks the event is still current and that that's the correct item for this event. Then the event action/s happen.

So the keeping of event items/keys here is for crosschecking, and so events knows which items to act on (instead of just sending "gate" and making itemreg figure out which gate it is.)

okay, I like that.
"""

def initialise_eventRegistry():

    for event_name in event_dict:
        events.add_event(event_name, event_dict[event_name])


if __name__ == "__main__":

    from env_data import initialise_placeRegistry
    initialise_placeRegistry()
    from itemRegistry import initialise_itemRegistry
    initialise_itemRegistry()
    initialise_eventRegistry()
    if events.travel_is_limited:
        #print(f"Travel is limited: {(events.travel_is_limited)}")
        print(events.check_movement_limits())

    add_items_to_events(None) # not in initialise_evReg because it gets called by initialise_all with data from item_def. Need to look into that though because I might need it later. Should really just do it all directly here, or it not need to reevaluate what data itemReg is sending because it's likely out of date now. Either way though, two entirely different paths whether item_data or not is silly. And currently generated events (eg moss_drying) don't get access to item_data at all.

    #for event in events.events:
        #print(f"Event triggers: {event.triggers}")
        #for trigger in event.triggers:
            #print(f"Event trigger vars: {vars(trigger)}")
    #print("For event in events: vars.")
    #for event in events.by_name:
    #    print(event)
#
    #print(events.by_name)

    #events.start_event("mermaid_grotto_appears")


#    graveyard_gate_open
#    {'graveyard_gate_open': <cardinalInstance graveyard_gate_open (1835367c-bbc8-4558-b463-fa40464f6f0f, state: 1, all attributes: {'starts_current': True, 'end_trigger': {'item_trigger': {'trigger_name': 'padlock', 'trigger_location': 'graveyard east', 'trigger': 'child_removed'}}})>}
