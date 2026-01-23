# event registry, to manage events. Obviously.

"""
Only event so far: The one I'm writing right now.
Cannot travel outside the graveyard until the gate in graveyard north is unlocked.
So the event 'ends' when the gate is unlocked; the event starts on runstart.
if the padlock is unlocked or broken, it falls to the ground and the gate creaks open slightly. At this point, event ends, and travel to other locations is accessible.
"""

import uuid

event_states = {
    "past": 0,
    "current": 1,
    "future": 2
}


class eventInstance:

    def __init__(self, name, attr):
        self.name = name
        self.id = str(uuid.uuid4())
        self.event_state:int
        self.start_trigger = None # just to make sure these are here so other things can be more solid.
        self.end_trigger = None

        for item in attr:
            setattr(self, item, attr[item])

        self.attr = attr
        """
        self.event_items
        self.event_triggers
        """
    def __repr__(self):
        return f"<cardinalInstance {self.name} ({self.id}, state: {self.event_state}, all attributes: {self.attr})>"

class eventRegistry:

    def __init__(self):

        self.events = set()
        self.by_id = {}
        self.by_name = {}
        self.current_events = set()
        self.past_events = set()
        self.future_events = set()
        self.by_state = {}

        for state in event_states.values():
            self.by_state[state] = set() ## really don't need these and the current/past/future. Will probably use this alone instead, it'll be easier to set up the direction.
        print(f"Self by event state: {self.by_state}")
        """
        future events =
        0 = current
        1 = future
        2 = past

        or

        past
        current
        future

        or

        future
        current
        past

        I actually think
        0 = past
        1 = current
        2 = future
        because then if not-null it at least has a shot at being relevant, right? Either 1 or 2 /might/ be triggered, but 0 def won't.
        """

    def add_event(self, event_name, event_attr):
        event = eventInstance(event_name, event_attr)
        self.events.add(event)
        self.by_id[event.id] = event
        self.by_name[event.name] = event

#'## Remove this bit with current_, future_, just use the dict.
        if hasattr(event, "starts_current"):
            self.current_events.add(event)
            event.event_state = 1 # (current event)
        else:
            self.future_events.add(event)
            event.event_state = 2 # (future event)

        self.by_state[event.event_state].add(event)

    def event_by_state(self, state)-> set:
        if isinstance(state, int) or (isinstance(state, str) and len(state)==1):
            if str(state) == "1":
                return self.current_events
            elif str(state) == "2":
                return self.future_events
            else:
                return self.past_events
        elif state in event_states:
            state_int = event_states[state]



    def event_by_id(self, event_id)-> eventInstance:

        if not isinstance(event_id, str):
            event_id = str(event_id)

        instance = self.by_id(event_id)
        if instance:
            return instance

    def event_by_name(self, event_name:str)-> eventInstance:

        if isinstance(event_name, str):
            instance = self.by_name(event_name)
            if instance:
                return instance

    def start_event(self, event_name:str):

        # Note that events can be concurrent, so setting a current event does not necessarily remove an existing event.
        to_be_current = self.event_by_name(event_name)
        if to_be_current in self.future_events:
            self.future_events.remove(to_be_current)
            self.current_events.add(to_be_current)
            if to_be_current in self.current_events: # redundant but just in case anything went super wrong:
                to_be_current.event_state = 1

        else:
            print(f"Cannot set event {event_name} as current event, because it is not present in future_events: {self.future_events}")
            exit()

    def end_event(self, event_name):

        to_end_current = self.event_by_name(event_name)
        if to_end_current in self.current_events:
            self.current_events.remove(to_end_current)
            self.past_events.add(to_end_current)
            if to_end_current in self.past_events: # redundant but just in case anything went super wrong:
                to_end_current.event_state = 2
        else:
            print(f"Cannot set event {event_name} as ended event, because it is not present in current_events: {self.current_events}")
            exit()
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

def initialise_eventRegistry():

    import json
    event_data = "event_defs.json"
    with open(event_data, 'r') as loc_data_file:
        event_dict = json.load(loc_data_file)
    for event_name in event_dict:
        events.add_event(event_name, event_dict[event_name])

if __name__ == "__main__":

    initialise_eventRegistry()

    print("For event in events: vars.")
    for event in events.by_name:
        print(event)

    print(events.by_name)
#    graveyard_gate_open
#    {'graveyard_gate_open': <cardinalInstance graveyard_gate_open (1835367c-bbc8-4558-b463-fa40464f6f0f, state: 1, all attributes: {'starts_current': True, 'end_trigger': {'item_trigger': {'trigger_name': 'padlock', 'trigger_location': 'graveyard east', 'trigger': 'child_removed'}}})>}
