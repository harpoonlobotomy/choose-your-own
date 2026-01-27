# event registry, to manage events. Obviously.

"""
Only event so far: The one I'm writing right now.
Cannot travel outside the graveyard until the gate in graveyard north is unlocked.
So the event 'ends' when the gate is unlocked; the event starts on runstart.
if the padlock is unlocked or broken, it falls to the ground and the gate creaks open slightly. At this point, event ends, and travel to other locations is accessible.
"""

import uuid

from misc_utilities import assign_colour

event_states = {
    "past": 0,
    "current": 1,
    "future": 2
}

def load_json():
    import json
    event_data = "event_defs.json"
    with open(event_data, 'r') as loc_data_file:
        event_dict = json.load(loc_data_file)
    return event_dict


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
        self.event_state:int
        self.start_trigger = None # just to make sure these are here so other things can be more solid.
        self.end_trigger = None
        self.items = set() ## items affected by the event
        self.keys = set() ## items that effect the event
        self.msgs = attr.get("messages") # what prints when the event starts/ends/on certain cues
        self.limits_travel = False
        self.held_items = {}
        self.hidden_items = set()
        self.start_trigger_location = None
        self.end_trigger_location = None

        for item in attr:
            setattr(self, item, attr[item])

        #self.effects = {attr["effects"].get("limit_travel")}
        if attr.get("effects"):
            if attr["effects"].get("limit_travel"):
                self.limits_travel = True
                self.travel_limited_to = set()
                #events.travel_is_limited = attr["effects"]["limit_travel"] # OH this is broken. Can't overwrite it like this, otherwise adding a new event will just clear this.
                if attr["effects"]["limit_travel"].get("cannot_leave"):
                    for location in attr["effects"]["limit_travel"].get("cannot_leave"):
                        self.travel_limited_to.add(location)
                        #events.held_at = dict({"held_at_loc": location, "held_by": self}) ## only records 'held_at_loc' as the last one, so graveyard_gate event records 'graveyard' but not 'work shed' even though both are valid. Works okay with travel_limited_to though, so the potential locations are correct.
                    #events.held_at_loc = attr["effects"]["limit_travel"]["cannot_leave"]

                #print(f"Initiated event limits travel: {attr["effects"].get("limit_travel")}")

            if attr["effects"].get("hide_item"):
                self.hidden_items.add(attr["effects"]["hide_item"]["item_name"])
                self.items.add(attr["effects"]["hide_item"]["item_name"])

            if attr["effects"].get("hold_item"):
                print(f"Event holds an item: {attr["effects"]["hold_item"]["item_name"]}")
                self.held_items[(attr["effects"]["hold_item"]["item_name"])] = attr["effects"]["hold_item"]["item_loc"] # only allows for one item to be held. Fine for now but will need changing.
                self.items.add(attr["effects"]["hold_item"]["item_name"])

        if attr.get("end_trigger"):
            if attr.get("end_trigger"):
                if attr["end_trigger"].get("item_trigger"):
                    self.keys.add(attr["end_trigger"]["item_trigger"]["trigger_name"])
                    self.end_trigger_location = attr["end_trigger"]["item_trigger"]["trigger_location"]

        """
        self.event_items
        self.event_triggers
        """
    def __repr__(self):
        return f"<eventInstance {self.name} ({self.id}, event state: {self.event_state}>"#, all attributes: {self.attr})>"

class eventRegistry:

    def __init__(self):

        self.events = set()
        self.by_id = {}
        self.by_name = {}
        self.by_state = {}
        self.trigger_items = {}
        self.travel_is_limited = False

        for state in event_states.values():
            self.by_state[state] = set() ## really don't need these and the current/past/future. Will probably use this alone instead, it'll be easier to set up the direction.



                    #if event_dict[event][trigger]["item_trigger"].get("trigger_location"):
                        #event event_dict[event][trigger]["item_trigger"]["trigger_location"]:
        # so braindead right now. Maybe I just ignore the whole trigger_location thing in this case because you can only pick up an item from its start location.




    def add_event(self, event_name, event_attr):
        event = eventInstance(event_name, event_attr)
        self.events.add(event)
        self.by_id[event.id] = event
        self.by_name[event.name] = event


        if hasattr(event, "starts_current"):
            self.by_state[1].add(event)
            event.event_state = 1 # (current event)
            if event.limits_travel:
                self.travel_is_limited = True # mark as true if event starts at runtime.
            if event.held_items:
                from interactions.item_interactions import set_attr_by_loc
                for item in event.held_items:
                    location = event.held_items[item]
                    set_attr_by_loc(attr = "can_pick_up", val = "False", location = location, items = item)

                print(f"Attribute set: can_pick_up")
        else:
            self.by_state[2].add(event)
            event.event_state = 2 # (future event)

        return event

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

    def event_by_name(self, event_name:str)-> eventInstance:

        if isinstance(event_name, str):
            instance = self.by_name.get(event_name)
            if instance:
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

        def print_current(event, state_type="held", print_text=False):

            if event.msgs.get(f"{state_type}_msg"):
                msg = event.msgs[f"{state_type}_msg"]
                if print_text:
                    print(assign_colour(msg, colour="event_msg"))
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


    def start_event(self, event_name:str):

        # Note that events can be concurrent, so setting a current event does not necessarily remove an existing event.
        to_be_current = self.event_by_name(event_name)

        event_state = to_be_current.event_state

        if event_state == 0:
            print(f"Event {event_name} is already over.")
            return
        if event_state == 1:
            print(f"Event {event_name} is already happening.")
            return

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


    def end_event(self, event_name):

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
                    if event != event_to_end and hasattr(event, "limits_travel"):
                        no_limits = False

                if no_limits:
                    self.travel_is_limited = False # untested

            if event_to_end.hidden_items:
                #print(f"event_to_end.hidden_items: {event_to_end.hidden_items}")
                #print("Here we need to unhide any hidden items.")
                event_to_end.end_trigger_location
                from interactions.item_interactions import set_attr_by_loc
                set_attr_by_loc(attr = "is_hidden", val = "False", location = event_to_end.end_trigger_location, items = event_to_end.hidden_items)

            if event_to_end.held_items:
                from interactions.item_interactions import set_attr_by_loc
                set_attr_by_loc(attr = "is_pick_up", val = "True", location = event_to_end.end_trigger_location, items = event_to_end.hidden_items)
                print(f"event_to_end.held_items: {event_to_end.held_items}")
                print("Here we need to release any held items (eg what the padlock should be but currently isn't).")

            self.play_event_msg(msg_type="end", event=event_to_end)

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

    def is_event_trigger(self, noun_inst, noun_loc):

        for event in self.events:
            if event.event_state != 1:
                continue
            for item in event.keys:
                if item == noun_inst.name:
                    if event.end_trigger_location == noun_loc.place_name:
                        self.end_event(event)
                        break

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



def add_items_to_events(item_data):
    event_dict = load_json()
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
    for item in item_data:
        event_name = item_data[item].get("event_name")
        if events.event_by_name(event_name):
            event = events.event_by_name(event_name)
            event.items.add(item_data[item].get("item")) ## by using the instance here (""item""") instead of the name, it means that only this specific instance is the trigger, not any random one. Should be a benefit, but need to keep in mind that if a thing has many possible triggers, all need the flags. Should be okay though, just be mindful.
            if item_data[item].get("event_key"):
               event.keys.add(item_data[item].get("item")) ## add by name or by id... or maybe just send the damn instance over. Only reason to send an ID is to make savestates easier, but I can get grab the ID when needed if that's the case...
            if event_dict[event_name].get("end_trigger"):
                if event_dict[event_name]["end_trigger"].get("item_trigger"):
                    if event_dict[event_name]["end_trigger"]["item_trigger"].get("item_flags"):
                        for flag in event_dict[event_name]["end_trigger"]["item_trigger"]["item_flags"]:
                            item_data[item].get("item").flag = event_dict[event_name]["end_trigger"]["item_trigger"]["item_flags"].get(flag)

                    if event_dict[event_name]["end_trigger"]["item_trigger"].get("flags_on_event_end"):
                        if not hasattr(event, "flags_to_restore"):
                            event.flags_to_restore = {}
                        event.flags_to_restore[item] = event_dict[event_name]["end_trigger"]["item_trigger"]["flags_on_event_end"]


               #events.trigger_items[item_data[item].get("item")] = {event} # for ready access for the main script to check against. But might remove this. Functionally, I just need a quick way for 'this item says its an event trigger, do I need to do anything rn?' to check things. But again, if it's an item trigger, the item itself should be managing its trigger, no? Just sending word to the event if trigger happens. events isn't checking each item for trigger-ness.


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

            #print(f"event: {event_name}, event.items: {event.items}")
#       'padlock': {'event_name': 'graveyard_gate_opens', 'event_key': True, 'event_item': None, "item_id": 'id number here'}}

def initialise_eventRegistry():
    event_dict = load_json()

    for event_name in event_dict:
        event = events.add_event(event_name, event_dict[event_name])



if __name__ == "__main__":

    initialise_eventRegistry()
    if events.travel_is_limited:
        print(f"Travel is limited: {(events.travel_is_limited)}")
        print(f"{events.held_at}")

    #print("For event in events: vars.")
    #for event in events.by_name:
    #    print(event)
#
    #print(events.by_name)

    #events.start_event("mermaid_grotto_appears")


#    graveyard_gate_open
#    {'graveyard_gate_open': <cardinalInstance graveyard_gate_open (1835367c-bbc8-4558-b463-fa40464f6f0f, state: 1, all attributes: {'starts_current': True, 'end_trigger': {'item_trigger': {'trigger_name': 'padlock', 'trigger_location': 'graveyard east', 'trigger': 'child_removed'}}})>}
