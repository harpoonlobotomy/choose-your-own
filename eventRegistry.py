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


trigger_acts = { # the k/v a verb action has to send in order to meet the trigger requirement.
    "item_broken": {"is_broken": True},
    "item_unlocked": {"is_locked": False}
}

event_effects = ["hold_item", "lock_item", "hide_item", "limit_travel"]
event_effects = ["held_items", "locked_items", "hidden_items", "limit_travel"]

effect_attrs = {
    "held_items": {
        "on_event_start": {"can_pick_up": False},
        "on_event_end": {"can_pick_up": True}},
    "locked_items": {
        "on_event_start": {"is_closed": True, "is_locked": True},
        "on_event_end": {"is_closed": False, "is_locked": False}},
    "hidden_items": {
        "on_event_start": {"is_hidden": True, "can_pick_up": False},
        "on_event_end": {"is_hidden": False, "can_pick_up": True}}
}
# removed categories again, can just use effect name now.

   # "limit_travel": {"on_event_start": {"travel_limited": True}, "on_event_end":{"travel_limited": False}}




class eventInstance:

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
        self.items = set()
        self.item_name_to_inst = {} # to track 'iron key' to instance, to make sure instances are tracked through events. Note: Only works as intended if only one instance per name. If an event has multiple instances of one itemname, will need an alt route.
        self.msgs = attr.get("messages") # what prints when the event starts/ends/on certain cues
        self.limits_travel = False
        print(f"\n{name} ATTR@ ::: {attr} \n\n")
        print(f"STATE: {self.state}")
        self.held_items = (attr.get("held_items") if attr.get("held_items") else set())
        self.hidden_items = (attr.get("hidden_items") if attr.get("hidden_items") else set()) # These were dicts with item: item_loc. I can't see where/why I'm using the location though, that should be done with in item inst identification. Changing (back?) to sets.
        self.locked_items = (attr.get("locked_items") if attr.get("locked_items") else set())
        print(f'attr.get("hidden_items"): {attr.get("hidden_items")}')
        print(f'self.hidden_items: {self.hidden_items}')
        self.start_trigger_location = None
        self.end_trigger_location = None

        self.condition_items = set() ## for keeping items that are part of timed triggers.

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

        print(f"End of init: {self.state}")

    def __repr__(self):
        return f"<eventInstance {self.name} ({self.id}, event state: {self.state}>"#, all attributes: {self.attr})>"

trigger_actions = ["item_in_inv", "item_broken", "item_unlocked", "item_not_in_inv"]



#not sure about this whole thing. Might make it worse, not better.
class timedTrigger:
    """
    Maybe  this should be a timedTrigger, instead of timedEvent. All we need is for the event to notify 'i have a timed trigger' and redirect. Better that than a whole separate event class, maybe. Not really sure, still too tired to think.

    """

    def __init__(self, trigger_dict, event:eventInstance):

        self.id = str(uuid.uuid4())
        self.event = event#trigger_dict["event"]
        self.state = event.state
        self.is_item_trigger = False
        self.item_inst = None
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

        #if trigger_dict["trigger_type"] == "end_trigger": # surely will always be end_trigger, no?
        # Saying now that timed triggers will always be end_triggers. Don't bother with the rest of it.
        self.start_trigger = False
        self.end_trigger = True
        event.end_triggers.add(self)
       # else:
       #     self.start_trigger = False
       #     self.end_trigger = True
       #     event.start_triggers.add(self)

       # Honestly maybe this shouldn't be a trigger at all, maybe it should just be part of the event itself....
       # Well no, I need an end trigger to stop the duration. That's

        timed_dict = trigger_dict["timed_trigger"]
        self.time_unit = timed_dict["time_unit"]  # "days",
        self.full_duration = timed_dict["full_duration"]  # 3,

        event.constraint_tracking[self.time_unit] = {"full_duration": self.full_duration, "current_duration": 0}

        self.persistent_condition = timed_dict["persistent_condition"]  # true,

        if self.persistent_condition:
            print(f"Event must have condition maintained until completion of {self.full_duration} {self.time_unit}s.")
            print("Add something to set_up_game to manage 'when day changes, add to duration'.")
            print("I feel like the duration should be tracked on the event, not the trigger, though.")

        self.required_condition = timed_dict["required_condition"]  # {"item_in_inv": "moss"},
        print(f"SELF REQUIRED CONDITION: {self.required_condition}")
        self.condition_item_is_start_trigger = timed_dict["condition_item_is_start_trigger"]  # true

        for condition, value in self.required_condition.items():
            print(f"condition: {condition}, value: {value}")
            self.triggers.add(condition)
            if condition not in trigger_actions:
                print(f"Required_condition not known: {condition} // [value ({value}])")
                continue

            if event.is_generated_event or not event.item_name_to_inst.get(value):
                if self.required_condition.get(condition):
                    print(f"self.required_condition[condition]: {self.required_condition[condition]}")
                    condition_item = self.required_condition[condition]
                    print(f"TRIGGER DICT: {trigger_dict}")
                    #print(f":::::::: {trigger_dict["trigger_item"]}")
                    if trigger_dict.get("trigger_item") and isinstance(trigger_dict["trigger_item"], ItemInstance):
                        print(f"TRIGGER ITEM: {trigger_dict["trigger_item"]}")
                        self.is_item_trigger = True
                        if trigger_dict["trigger_item"].name == self.required_condition[condition]:
                                print("The instance sent with the trigger data will be used.")
                                self.item_inst = trigger_dict["trigger_item"]
                        #if trig_data["trigger_item"].name == self.required_condition["item_in_inv"]:
                                setattr(self, self.required_condition[condition], trigger_dict["trigger_item"])
                                #self.required_condition["item_in_inv"] = trig_data["trigger_item"]

                        else:
                            print("Needs an instance here but apparently couldn't find one. This is real bad, something's wrong upstream.")
                            exit()
                    elif trigger_dict.get("timed_trigger"):
                        print(f"Trigger dict[timed_trigger]: {trigger_dict["timed_trigger"]}")
                        for entry, v in self.required_condition[condition].items():# == self.required_condition[condition]:
                            print(f"V: {v}")
                            if event.item_name_to_inst.get(v):
                                print("The instance of this name used with this event will be used.")
                                self.item_inst = v
                                setattr(self, self.required_condition[condition], v)
                        #if trig_data["trigger_item"].name == self.required_condition["item_in_inv"]:
                                #setattr(self, self.required_condition[condition], trig_data["trigger_item"])
                else:
                    print(f"No self.required_condition[condition]: {self.required_condition[condition]}")

            elif event.item_name_to_inst.get(value):

                print("THIS SHOUILD NOT BE HERE IF THE EVENT IS AUTOGENNED. Same for regular triggers.")
                self.item_inst = event.item_name_to_inst[value]
                self.required_condition[condition] = self.item_inst
                print(f"required condition[condition]: {self.required_condition[condition]}")

            event.condition_items.add(self.item_inst)

            event.constraint_tracking[self.time_unit].update({"required_condition": condition, "condition_item": self.item_inst})

            event.items.add(self.item_inst) # ,aybe don't need this one.
            events.items_to_events[self.item_inst] = event

            """
        So event.constraint_tracking should be:
            event.constraint_tracking: {
                "day: {
                    "full_duration": self.full_duration,
                    "current_duration": 0,
                    "condition": "item_in_inv",
                    "condition_item": <moss_instance>}
                }

            """


        """
        So, if the duration is completed, the event succeeds.
        If an end trigger is hit, it succeeds/fails depending on the state in the trigger (so possibly, an event might have an end trigger that makes it succeed early (you find a warm fire and put the moss near it, it dries in one day instead of 3, etc).).

        """

    def __repr__(self):
        return f"<timedTrigger {self.id} for event {self.event.name}, event state: {event_state_by_int[self.state]}, {(f'Trigger item: {self.item_inst}' if isinstance(self.item_inst, ItemInstance) else None)}>"


class Trigger:

    def __init__(self, trigger_dict, event:eventInstance):

        #print(f"TRIGGER DICT: {trigger_dict}")
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
                if isinstance(trigger_dict["trigger_item"], ItemInstance):
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

            # TODO: only works if items are instances already. Might need to keep a dict of things that don't have instances? Or just account for it later, this should only occur in the generating events so maybe I can just make it part of the intended process.
        else:
            self.is_item_trigger = False

        if isinstance(trigger_dict["trigger_actions"], str):
            self.triggers.add(trigger_dict["trigger_actions"])
        else:
            for action in trigger_dict["trigger_actions"]:
                self.triggers.add(action)
        event.triggers.add(self)


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

        self.start_triggers = dict() #self.start_trigger_is_item

        self.items_to_events = dict() # just every item attached to an event, for now. Won't keep this but it'll be convenient for testing the general shape of things.
        self.no_item_restriction = {} # no I was right the first time. noun_name: event_name. Then check if noun in events by that name. Makes way more sense. Don't check all events then all items, check if the item is viable before events are even considered.
        self.generate_events_from_itemname = {}
        # Actual way of doing it: event_name:item_name # event NAME, so it can start a new event when the item is encountered.
        # dict: item_name: event (assuming item_trigger) May only allow one event per item, though could make it a set. Though actually it's already checking all events when items are encountered, so really should just do it in that same pass. Okay.#
        self.timed_triggers = set()
        self.condition_items = set()

        for state in event_states.values():
            self.by_state[state] = set() ## really don't need these and the current/past/future. Will probably use this alone instead, it'll be easier to set up the direction.



                    #if event_dict[event][trigger]["item_trigger"].get("trigger_location"):
                        #event event_dict[event][trigger]["item_trigger"]["trigger_location"]:
        # so braindead right now. Maybe I just ignore the whole trigger_location thing in this case because you can only pick up an item from its start location.

    def add_event(self, event_name, event_attr):

        event = eventInstance(event_name, event_attr)
        self.events.add(event)
        self.by_id[event.id] = event
        if not self.by_name.get(event.name):
            self.by_name[event.name] = set()
        self.by_name[event.name].add(event)

        if hasattr(event, "starts_current") and getattr(event, "starts_current"):
            self.by_state[1].add(event)
            event.state = 1 # (current event)
            if event.limits_travel:
                self.travel_is_limited = True

        else:
            print(f"Event not starts_current: {event}")
            self.by_state[2].add(event)
            event.state = 2 # (future event)

        if self.timed_triggers:
            events.timed_events.add(self)

        return event, event_attr

    def get_all_item_instances(self, event:eventInstance, event_entry, noun=None):

        from itemRegistry import registry
        event.item_name_to_inst = {}

        if not hasattr(event, "item_name_to_loc"):
            print(f"No item_name_to_loc dict for {event}\n")

        # Need to add a thing here for generated events to apply the newly found noun inst to the event directly.

        if noun and noun.name not in event.item_names:
            event.item_names.add(noun.name)


        for item in event.item_names:
            if event.item_name_to_inst.get(item) and not noun:
                continue
            instance = None
            if not noun:
                if event.item_name_to_loc.get(item):
                    item_loc = event.item_name_to_loc[item]
                    loc_items = registry.get_item_by_location(item_loc)
                    for loc_item in loc_items:
                        if loc_item.name in event.item_names: # instead of just the given item, add any matches found at once.#== item:
                            #print(f"Found instance for {loc_item.name} in {item_loc}: {loc_item}")
                            instance = loc_item
                            event.item_name_to_inst[loc_item.name] = instance

            if noun:
                instance = noun
                event.item_name_to_inst[noun.name] = instance
                event.items.add(instance)


            if not instance:
                print(f"No instance found by location for {item}")

        """
        remove_dict = {}
        add_dict = {}
        for effect in ("hidden_items", "held_items", "locked_items"):
            for item in getattr(event, effect):
                if item_name_to_inst.get(item):
                    print(f"{effect} item: {item}")
                    remove_dict.setdefault(effect, set()).add(item)
                    add_dict.setdefault(effect, set()).add(item_name_to_inst.get(item))

            if remove_dict.get(effect):
                for item in remove_dict[effect]:
                    print(f"Current {effect}: {getattr(event, effect)}")
                    getattr(event, effect).add(item_name_to_inst.get(item))
                    getattr(event, effect).remove(item)
                print(f"Updated {effect}: {getattr(event, effect)}")
        """
        #for trigger in ("start_trigger")




        missing = list(i for i in event.item_names if i not in event.item_name_to_inst)
        if missing:
            print(f"Missing instances: [[{missing}]]")
        #exit()


        """
EVENT VARS: {'name': 'reveal_iron_key', 'id': '3f2fea7b-b681-49f1-ac1d-2068557dbfb7', 'state': 1, 'triggers': set(), 'start_triggers': set(), 'end_triggers': set(), 'items': set(), 'msgs': {'start_msg': None, 'end_msg': 'As you pick up the regional map, an iron key falls from the folded paper and lands on the desk with a heavy thwack.', 'held_msg': None}, 'limits_travel': False, 'held_items': set(), 'hidden_items': {'iron key'}, 'locked_items': set(), 'start_trigger_location': None, 'end_trigger_location': None, 'no_item_restriction': {}, 'constraint_tracking': {}, 'timed_triggers': set(), 'attr': {'starts_current': True, 'end_trigger': {'item_trigger': {'trigger_item': 'local map', 'trigger_location': 'north work shed', 'trigger': ['item_in_inv'], 'flags_on_event_start': {}}}, 'effects': {'hide_item': {'item_name': 'iron key', 'item_location': 'north work shed'}}, 'messages': {'start_msg': None, 'end_msg': 'As you pick up the regional map, an iron key falls from the folded paper and lands on the desk with a heavy thwack.', 'held_msg': None}}, 'start_trigger_is_item': False, 'end_trigger_is_item': True, 'item_names': {'local map', 'iron
key'}, 'is_generated_event': None, 'is_timed_event': None, 'starts_current': True, 'start_trigger': None, 'end_trigger': 'local map', 'effects': {'hide_item': {'item_name': 'iron key', 'item_location': 'north work shed'}}, 'messages': {'start_msg': None, 'end_msg': 'As you pick up the regional map, an iron key falls from the folded paper and lands on the desk with a heavy thwack.', 'held_msg': None}, 'event_state': 1}

        """

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

    def get_event_triggers(self, event, event_name = None, trigger_check = None):
        logging_fn()
        #event_dict = load_json()

        from env_data import locRegistry as loc
        from itemRegistry import registry

        print(f"event name: {event_name}, event: {event}, trigger_check: {trigger_check}")
        if event:
            if isinstance(event, eventInstance):
                if not event_name:
                    event_name = event.name
            elif isinstance(event, str):
                event_name = event
                event = events.event_by_name(str)
                if not event:
                    print(f"No event by the name {event_name}")
                    exit()
                if isinstance(event, list):
                    if len(event) > 1:
                        print(f"There is more than one event named {event_name}. Arbitrarily picking the first, but this may be wrong.")
                    event = event[0]

        if not event and event_name:
            if isinstance(event_name, eventInstance):
                event = event_name
                event_name = event.name

        #event_entry = event_dict.get(event_name)
        #print(f"EVENT ENTRY: {event_entry}")
        if event.is_generated_event:
            print(f"{event} is a generated event, no pre-defined instances here.")

        for trigger in ("start_trigger", "end_trigger"):
            trigger_dict = {}
            trig_data = {}
            if hasattr(event, trigger) and getattr(event, trigger):
                for entry in getattr(event, trigger):
                    trig_data[entry] = getattr(event, trigger)[entry]

            #if event_entry.get(trigger):
                if trig_data.get("item_trigger"):
                    trigger_item = trig_data["item_trigger"]["trigger_item"]
                    if event.is_generated_event:
                        if trigger_check:
                            trigger_item = trigger_check
                            event.items.add(trigger_item)
                            event.item_names.add(trigger_item.name)
                    else:
                        if event.item_name_to_inst.get(trigger_item):
                            trigger_item = event.item_name_to_inst[trigger_item]
                        else:
                            trigger_items = registry.instances_by_name(trigger_item)
                            for item in trigger_items:
                                if not hasattr(item, "event"):
                                    trigger_item = item
                                    break
                            # Assumes that an item of that name will be correct by default. Not ideal. Should probably check it has the event tag, but here we're ruling those /out/ instead of prioritising them. TODO: Will work on this later.

                    trigger_actions = trig_data["item_trigger"]["trigger"]


                    item_flags_on_start = trig_data["item_trigger"].get("on_event_start")
                    item_flags_on_end = trig_data["item_trigger"].get("on_event_end")

                    if trig_data["item_trigger"].get("trigger_constraint"):
                        trigger_dict["trigger_constraint"] = trig_data["item_trigger"]["trigger_constraint"]


                trigger_dict.update({
                    "event": event,
                    "trigger_model": "item_trigger",
                    "trigger_type": trigger,
                    "trigger_item": trigger_item,
                    "trigger_item_loc": (trigger_item.location if isinstance(trigger_item, ItemInstance) else None),
                    "trigger_actions": trigger_actions,
                    "item_flags_on_start": item_flags_on_start,
                    "item_flags_on_end": item_flags_on_end
                    })

                if trig_data.get("item_trigger"):
                    event.triggers.add(Trigger(trigger_dict, event))

                if trig_data.get("timed_trigger"):
                    print("trig data timed trigger")
                    if event.is_generated_event:
                        print("event is generated event")
                        if trigger_check:
                            print(f"is trigger check: {trigger_check}")
                            trigger_item = trigger_check
                            trigger_dict["trigger_item"] = trigger_item
                            print(f'trigger_dict["trigger_item"] : {trigger_dict["trigger_item"] }')
                        else:
                            print("no trigger check")
                    else:
                        print(f"event {event} is not is_generated_event")
                    print(f"Trig data timed trigger: {trig_data["timed_trigger"]}")
                    trigger_dict["trigger_model"] = "timed_trigger"
                    trigger_dict["timed_trigger"] = trig_data["timed_trigger"]
                    event.triggers.add(timedTrigger(trigger_dict, event))
                    print(f"EVENT TRIGGERS: {event.triggers}")

                events.items_to_events[trigger_item] = event

        effects_dict = {}
        for effect in event_effects:
            if hasattr(event, effect) and getattr(event, effect):
                if effect_attrs.get(effect):
                    effects_dict[effect] = {}

                    for item in getattr(event, effect):
                        if isinstance(item, ItemInstance):
                            event_item = item
                        else:
                            event_item = event.item_name_to_inst.get(item)
                        if not event_item:
                            print(f"No event item found for {event} with name {item}")
                            exit()

                        effects_dict[effect][item] = event_item

                        if effect_attrs[effect].get("on_event_start"):
                            #print(f"effect_attrs[effect]['on_event_start']: {effect_attrs[effect]['on_event_start']}")
                            for k, v in effect_attrs[effect]["on_event_start"].items():
                                setattr(event_item, k, v)

                        if not event_item in event.items:
                            event.items.add(event_item)

                        if not events.items_to_events.get(event_item):
                            events.items_to_events[event_item] = event

                        setattr(event_item, "event", event)

        if effects_dict:
            for effect in effects_dict:
                for item in effects_dict[effect]:
                    if isinstance(item, str):
                        #print(f"Before removing the str and adding the instance: \n{getattr(event, effect)}")
                        getattr(event, effect).remove(item)
                        getattr(event, effect).add(effects_dict[effect][item])
                        #print(f"Removed {item} from event.{effect}, added {effects_dict[effect][item]}:\n{getattr(event, effect)}")

        return event

    def get_event_item_names(self, event):
        logging_fn()

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
        logging_fn()

        if self.travel_is_limited:
            if event == None:
                holder = self.held_at.get("held_by") # currently only works if you can only be restricted by one event, will have to change this later.
                if holder.msgs.get("held_msg"):
                    if print_txt:
                        print(holder.msgs["held_msg"])
                    return holder.msgs["held_msg"]

            else:
                if event.state == 1:
                    if event.msgs.get("held_msg"):
                        if print_txt:
                            print(event.msgs["held_msg"])
                        return event.msgs["held_msg"]

    def play_event_msg(self, msg_type="held", event=None, print_txt=True):
        logging_fn()

        def print_current(event, state_type="held", print_text=False):

            if not event.msgs:
                return
            if event.msgs.get(f"{state_type}_msg"):
                msg = event.msgs[f"{state_type}_msg"]
                if print_text:
                    print("\n",assign_colour(msg, colour="event_msg"))
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

        event_state = to_be_current.state

        if event_state == 0:
            print(f"Event {event_name} is already over.")
            return

        if event_state == 1:
            print(f"Event {event_name} is already happening.")
            return

        for trigger in to_be_current.triggers:
            trigger.state = 1
            #print(f"Trigger: {trigger}, trig state: {trigger.state}")

        self.by_state.get(2).remove(to_be_current)
        self.by_state[1].add(to_be_current)

        to_be_current.state = 1

        if to_be_current in self.by_state.get(1): # redundant but just in case anything went super wrong:
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
        logging_fn()

        print_desc_again = False # Use to reprint the local description if items have become unhidden. Do it in a better way later, for now this will do.
        if isinstance(event_name, str):
            event_to_end = self.event_by_name(event_name)
        else:
            event_to_end = event_name

        if event_to_end in self.event_by_state(1):
            self.by_state[1].remove(event_to_end)
            self.by_state[2].add(event_to_end)
            if event_to_end in self.by_state[2]: # redundant but just in case anything went super wrong:
                event_to_end.state = 2

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
    ##NOTE: Absolutely this can be done using the new category entry in effect_attrs instead of going through it manually each time. Implement that.
            """
            if effect_attrs[effect].get("on_event_start"):
            #print(f"effect_attrs[effect]['on_event_start']: {effect_attrs[effect]['on_event_start']}")
            for k, v in effect_attrs[effect]["on_event_start"].items():
                setattr(event_item, k, v)
                """
            print(f"event to end: hidden items:: {event_to_end.hidden_items}")
            if event_to_end.hidden_items:
                pop_me = set()
                for item in event_to_end.hidden_items:
                    setattr(item, "is_hidden", False)
                    setattr(item, "can_pick_up", True)
                    pop_me.add(item)
                    print_desc_again = True

                if pop_me:
                    for item in pop_me:
                        if item not in event_to_end.hidden_items:
                            print(f"Cannot remove {item} from event_to_end.hidden_items as it's not there.")
                        else:
                            event_to_end.hidden_items.remove(item)

            print(f"event to end: held items:: {event_to_end.held_items}")
            if event_to_end.held_items:
                pop_me = set()
                for item in event_to_end.held_items:
                    setattr(item, "can_pick_up", True)
                    pop_me.add(item)

                if pop_me:
                    for item in pop_me:
                        if item not in event_to_end.held_items:
                            print(f"Cannot remove {item} from event_to_end.held_items as it's not there.")
                        else:
                            event_to_end.held_items.remove(item)

            print(f"event to end: locked items:: {event_to_end.locked_items}")
            if event_to_end.locked_items:
                pop_me = set()
                for item in event_to_end.locked_items:
                    setattr(item, "is_locked", False)
                    pop_me.add(item)

                if pop_me:
                    for item in pop_me:
                        if item not in event_to_end.locked_items:
                            print(f"Cannot remove {item} from event_to_end.locked_items as it's not there.")
                        else:
                            event_to_end.locked_items.remove(item)

            print("Need a section here that removes itemInstances from events.items. Or maybe not, if one day it'd be useful to know that this is the coin you gave to the witch in exchange for your left eye or smth")


            # Need to add the removal of .event from items, if relevant. Depends if an event can run again. Need to formalise that.
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

        #print(f"start of is_event_trigger:\nnoun inst: {noun_inst}, noun_loc: {noun_loc}, reason: {reason}.")
        def check_triggers(event, noun, reason):
            #print(f"start of check_triggers: event: {event}, noun: {noun}, reason: {reason}")
    # Reason == str containing the key phrase of the trig.trigger. eg 'added_to_inv'
            if event.end_triggers:
                print(f"event.end_triggers: {event.end_triggers}")
                for trig in event.end_triggers:
                    print(f"For trig in event.end_triggers: {trig}")
                    #print(f"VARS: {vars(trig)}")
                    if hasattr(trig, "constraint_tracking"):
                        print("Whether the event ends or not depends on this constraint. Maybe it should be checked earlier, I feel like I do this check in item_interactions. Needs to be one or the other.")
                        exit()
                    #print(f"TRIG: {trig}, vars: {vars(trig)}")
                    if trig.is_item_trigger and trig.item_inst == noun:
                        print("item inst == noun")
                        print(f"REASON: {reason}, type: {type(reason)}")
                        print(f"trigger acts: {trig.triggers}")
                        if isinstance(reason, str) and reason in trig.triggers:
                            if trig.item_inst_loc and trig.item_inst_loc != noun_loc:
                                continue # fail if the fail should have a location but doesn't. Doesn't apply to any current ones, but if you have to read a book under a specific tree, this would apply.
                            print("ENDING EVENT VIA IS_EVENT_TRIGGER")
                            self.end_event(event, trig, noun_loc)
                            return

                        elif isinstance(reason, tuple):
                            print(f"REASON TUPLE: {reason}, len: {len(reason)}") # will it always need to go to inner? Not sure.
                            for inner in reason:
                                k, v = inner
                                for condition in trig.triggers:
                                    if trigger_acts.get(condition) and trigger_acts[condition].get(k) == v:
                                        print(f"Condition [{k}: {v}] met for {noun_inst}. Will end event now.")
                                        self.end_event(event, trig, noun_loc)
                                        return
                        else:
                            print(f"Could not parse {reason}, type: {type(reason)}")
                    else:
                        if trig.is_item_trigger:
                            print(f"item inst {trig.item_inst} =! noun {noun}")
#events.no_item_restriction[self.item_inst.name].add(event) # eventsRegistry holds instance name to event (this instance name gets managed by this event)
#event.no_item_restriction[self.item_inst.name].add(self.item_inst) #the eventInstance holds (this item name goes to these itemInstances)
        if events.generate_events_from_itemname.get(noun_inst.name):
            if hasattr(noun_inst, "event") and getattr(noun_inst, "event"):
                print(f"This {noun_inst} already has an event tied to it: {noun_inst.event}")
                check_triggers(noun_inst.event, noun=noun_inst, reason=reason)
                return

            existing_event = False

            event_name = events.generate_events_from_itemname[noun_inst.name]

            intake_event = registrar.by_name.get(event_name)


            if intake_event and hasattr(intake_event, "start_trigger") and intake_event.start_trigger.get("item_trigger"):
                if intake_event.start_trigger["item_trigger"].get("match_item_by_name_only"):
                    #print(f"Reason item is in this check? {reason}")
                    if hasattr(intake_event, "required_condition"):
                        if isinstance(reason, str):
                            if reason in intake_event.required_condition:
                                #print("The reason is correct, the event should be started.")
                                event = register_generated_event(event_name, noun_inst)
                                self.start_event(event_name = event.name, event = event)
                                #print("Finished adding event")
                                return

            if event.no_item_restriction[noun_inst.name] == noun_inst:
                print(f"Item is part of an existing event: {event}")
                print("Do anything involving item triggers here (eg if dropping it fails the event, that will happen here.)")
                check_triggers(event, noun=noun_inst, reason=reason)
                return

        if events.items_to_events.get(noun_inst):
            print(f"noun inst is in items_to_events: {events.items_to_events.get(noun_inst)}")
            event = events.items_to_events[noun_inst]
            print(f"Event: {event}")
            if event.state == 1:
                check_triggers(event, noun_inst, reason)

    """
    What else do I need here.
    Check for starting triggers: check events in future_events, what their trigger types are.
    Maybe if a trigger can only be changed in a particular area, check that first?
    Well I don't need a global trigger check, because the trigger itself should trigger it.
    Maybe though, have an ongoing 'upcoming triggers' dict, of just potential event triggers exclusively. So nothing from past events, no later-stage triggers, etc, just the start-trigger for any future events that don't have other prerequisites and the current-stage trigger for any current triggers. Then if an item/scene trigger happens, we check against this dict, not against all triggers in the trigger defs. Yeah I like that I think.
    """

events = eventRegistry()

class eventIntake:

    def setup_timed_events(self, attr):
        logging_fn()
#'end_trigger': {'timed_trigger': {'time_unit': 'days', 'full_duration': 3, 'constraint_tracking': 0, 'trigger_item_is_start_trigger': True, 'trigger_outcome': 'success'}, 'item_trigger': {'trigger_item': 'moss', 'trigger': ['item_removed_from_inv'], 'trigger_outcome': 'failure'}}
        self.time_unit = attr["end_trigger"]["timed_trigger"]["time_unit"]
        self.full_duration = attr["end_trigger"]["timed_trigger"]["full_duration"]
        self.persistent_condition = attr["end_trigger"]["timed_trigger"]["persistent_condition"] # This is here so if it's just a thing that starts and continues on without interruption or reliance on something continuing, you can just omit that section.

        self.required_condition = attr["end_trigger"]["timed_trigger"]["required_condition"]
        self.condition_item_is_start_trigger = attr["end_trigger"]["timed_trigger"]["condition_item_is_start_trigger"]


    def __init__(self, event_name, attr):

        self.name = event_name
        #self.attr = attr
        self.start_trigger_is_item = False
        self.end_trigger_is_item = False
        self.item_names = set()
        self.item_name_to_loc = {}
        self.hidden_items = set()
        self.held_items = set()
        self.locked_items = set()

        self.is_generated_event = attr.get("is_generated_event")
        self.is_timed_event = attr.get("is_timed_event")

        self.starts_current = attr.get("starts_current")
        self.start_trigger = attr.get("start_trigger")
        if self.start_trigger:
            if attr["start_trigger"].get("item_trigger"):
                self.start_trigger_is_item = True
                #self.start_trigger = attr["start_trigger"]["item_trigger"].get("trigger_item")
                self.item_names.add(attr["start_trigger"]["item_trigger"].get("trigger_item"))
                if attr["start_trigger"]["item_trigger"].get("trigger_location"):
                    self.item_name_to_loc[attr["start_trigger"]["item_trigger"]["trigger_item"]] = attr["start_trigger"]["item_trigger"]["trigger_location"]

        self.end_trigger = attr.get("end_trigger")
        if self.end_trigger:
            if attr["end_trigger"].get("item_trigger"):
                self.end_trigger_is_item = True
                #self.end_trigger = attr["end_trigger"]["item_trigger"].get("trigger_item")
                # turning the above off, because if I don't have that data here, I have to get it from the event_dict again, which is silly.
                self.item_names.add(attr["end_trigger"]["item_trigger"].get("trigger_item"))
                if attr["end_trigger"]["item_trigger"].get("trigger_location"):
                    self.item_name_to_loc[attr["end_trigger"]["item_trigger"].get("trigger_item")] = attr["end_trigger"]["item_trigger"]["trigger_location"]

        #self.effects = attr.get("effects")
        if attr.get("effects"):
            for effect in attr.get("effects"):
                if effect_attrs.get(effect):
                    for entry in attr["effects"][effect]:

        # =   attr["effects"]["hidden_items"]["0"]"iron key"
                        self.item_names.add(attr["effects"][effect][entry].get("item_name"))
                        self.item_name_to_loc[attr["effects"][effect][entry].get("item_name")] = attr["effects"][effect][entry].get("item_location")
                        getattr(self, effect).add(attr["effects"][effect][entry].get("item_name"))
                        print(f"self.effect `{effect}` just had an item added: {getattr(self, effect)}")

                else:
                    setattr(self, effect, attr["effects"][effect])
                    if effect == "limit_travel":
                        self.limit_travel = True
                        if attr["effects"]["limit_travel"].get("cannot_leave"):
                            self.travel_limited_to = attr["effects"]["limit_travel"]["cannot_leave"]

        self.messages = attr.get("messages")

        if self.is_generated_event:
            if self.start_trigger_is_item:
                self.match_item_to_name_only = attr["start_trigger"]["item_trigger"].get("match_item_by_name_only")
                #events.generate_event_from_item[attr["start_trigger"]["item_trigger"]["item_name"]] = self
                # Means location etc doesn't matter in this case, only that the item name matches start trigger.
            self.can_repeat_forever = attr.get("can_repeat_forever")

        if self.is_timed_event:
            self.setup_timed_events(attr)
        ## is_generated_event -- does this always mean repeatable? Is there a point after which the event no longer generates?
#            Can I keep drying moss forever?

        """
        Basically I think this should be the base 'structure' of each event. No item instances, no triggerInst, no locInst, just the raw data but processed to be exactly what eventRegistry expects for init.
        Hell, maybe we use this for /all/ events during setup, but only stick around for the generated ones. Can just delete the old ones if we really care that much.
        """
    def __repr__(self):
        return f"<eventIntake {self.name} (start_trigger: {self.start_trigger}), (end_trigger: {self.end_trigger})>"


def add_items_to_events(event = None, noun_inst = None):
    logging_fn()

    def assign_event_keys(event):

        for item in event.items:
            if hasattr(item, "requires_key"):
                if hasattr(item, "key_is_placed_elsewhere"):
                    if isinstance(item.key_is_placed_elsewhere, dict):
                        if item.key_is_placed_elsewhere.get("item_in_event"):
                            event_with_key = item.key_is_placed_elsewhere["item_in_event"]
                            key_event = events.event_by_name(event_with_key)

                            key_item_names = {}

                            for potential_key in key_event.items:
                                if isinstance(potential_key, ItemInstance):
                                    key_item_names[potential_key.name] = potential_key

                            if key_item_names.get(item.requires_key):
                                item.requires_key = key_item_names[item.requires_key]
                        else:
                            print("Later, can add item locations to the event dict and find them through this. For now it only does event-held keys though.")
                else:
                    if events.item_names.get(item.requires_key):
                        item.requires_key = events.item_names[events.item_names[item.requires_key]]

    if noun_inst:
        noun = noun_inst
    else:
        noun = None

    if event:
        if isinstance(event, str):
            event_name = event
            event = None
        else:
            event_name = event.name

        events.get_event_triggers(event, event_name, trigger_check = noun)
        events.get_event_item_names(event)
        assign_event_keys(event)

    else:
        for event in events.events:
            events.get_event_triggers(event) # each loop done separately so event_item_names gets the complete dataset from the previous.

        for event in events.events:
            events.get_event_item_names(event)

        for event in events.events:
            assign_event_keys(event)



class eventRegistrar:

    def __init__(self):

        self.events = set()
        self.by_name = dict()
        self.generate_events_from_itemname = dict()
        self.start_trigger_is_item = dict()
        #generate_event_from_item

        #self.generated_events = set() # really should just be collections made from those event types. This is a bad idea.
        #self.timed_events = set() # really should just be collections made from those event types. This is a bad idea.

        """
        SO: every time_unit, we check if persistent_condition is still met, and if so, amend the constraint tracking. In addition, if the criteria for persistent_contition to end are met, we check (eg if item "moss" is removed from inventory).
        """


        """
        time information will be in end_trigger, because that's the only thing that makes sense. It ends if the timer completes, so we put it there. Start trigger doesn't need to know how long it has to run for.
        """

    def add_to_intake(self, event_name, attr):

        event = eventIntake(event_name, attr)
        self.events.add(event)


        if event.is_generated_event:
            if event.start_trigger_is_item:
                #self.generate_events_from_itemname[event.start_trigger["item_trigger"]["trigger_item"]] = event.name
                events.generate_events_from_itemname[event.start_trigger["item_trigger"]["trigger_item"]] = event.name

        if event.start_trigger_is_item:
            self.start_trigger_is_item[event] = event.start_trigger["item_trigger"]["trigger_item"]

        self.by_name[event.name] = event #one to one match of name to entry, because this is just the basis, no instances etc.

        #print(f"EVENT IN INTAKE: {event}\n{vars(event)}")
        #exit()

        return event, attr

registrar = eventRegistrar()

def register_generated_event(event_name, noun):
    if not event_dict.get(event_name):
        print(f"Cannot generate event `{event_name}` as {event_name} is not in the event defs file.")
        exit()

    intake_event, _ = registrar.add_to_intake(event_name, event_dict[event_name])
    event_inst, event_entry = events.add_event(intake_event.name, vars(intake_event))
    print(f"About to get item instances for {event_inst}, using {noun}")
    events.get_all_item_instances(event_inst, event_entry, noun)
    add_items_to_events(event_inst, noun)
    return event_inst


def initialise_eventRegistry():

    for event_name in event_dict:
        registrar.add_to_intake(event_name, event_dict[event_name])
    """
    So at this point - it has the item  names for all triggers/effects, but no instances.
    """

    for event in registrar.events:
        if not getattr(event, "is_generated_event"):
            event_inst, event_entry = events.add_event(event.name, vars(event))
            print(f"About to get item instances for {event_inst}")
            events.get_all_item_instances(event_inst, event_entry)
            ## NOTE: Should not add the instances to effects/etc, we need to go through those in add_items_to_events after anyway, no? So should just add them then, when we're already going through them to prep the triggers.



    #for event in registrar.events:
    #    if getattr(event, "is_generated_event"):
    #        event_inst, event_entry = events.add_event(event.name, vars(event))
    #    else:
    add_items_to_events()

            #print(f"Started current event: {event_inst}\nvars: {vars(event_inst)}")

if __name__ == "__main__":

    run_full = True#False

    if run_full == True:
        from env_data import initialise_placeRegistry
        initialise_placeRegistry()
        from itemRegistry import initialise_itemRegistry
        initialise_itemRegistry()
        initialise_eventRegistry()
        if events.travel_is_limited:
            #print(f"Travel is limited: {(events.travel_is_limited)}")
            print(events.check_movement_limits())

        #add_items_to_events(None)

