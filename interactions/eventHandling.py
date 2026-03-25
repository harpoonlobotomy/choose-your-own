# eventHandling.py for specific event management beyond what hte JSON offers.


from ..itemRegistry import itemInstance


def moss_dries_handling(event, moss:itemInstance):

    container = moss.contained_in if hasattr(moss, "contained_in") and moss.contained_in else None
    if not container:
        print("Moss is not in a container.")

    "end_trigger" = {
        "timed_trigger": {
            "time_unit": "hour",
            "full_duration": 1,
            "required_condition": {"item_is_open": container},
            "persistent_condition": True,
            "condition_item_is_start_trigger": True,
            "exceptions": ["current_loc_is_inside"],
            "end_type": "success",
            "effect_on_completion":
                {"end_event": "trigger_event"}},
        "event_trigger": {
            "trigger_item": "trigger_event",
            "triggered_by": ["event_ended"],
            "end_type": "failure"}
        }

    from ..env_data import locRegistry as loc
    if moss.location != loc.inv_place:
        if moss.contained_in:
            container = moss.contained_in
            if (container.location == loc.inv_place or container.is_open == False or container.location.place.inside == True):
                event_state = "continues"
            else:
                event_state = "ends"
        else:
            if moss.location.place.inside == False:
                event_state = "ends"
            else:
                event_state = "continues"
    else:
        event_state = "continues"

    if event_state == "ends":
        from eventRegistry import events
        events.end_event(event, e)
