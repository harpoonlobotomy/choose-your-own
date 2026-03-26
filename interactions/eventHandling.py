# eventHandling.py for specific event management beyond what hte JSON offers.

def moss_dries_handling(event, trigger, moss):
    container = None
    if hasattr(event, "child_item"):
        print(f"Event has a child item: {event.child_item}")
        if moss != event.child_item:
            print(f"Moss is not the child item: \n   moss: {moss} // child_item: {event.child_item}.")
            if "container" in moss.item_type:
                print("moss is a container")
                if moss.children and event.child_item in moss.children:
                    print("child_item is in container")
                    container = moss
                    moss = event.child_item
                else:
                    if moss == trigger.item_inst:
                        # we say container == none because we don't care about the container anymore, because the item isn't in it.
                        container = None
                        moss = event.child_item

    if not container:
        container = moss.contained_in if hasattr(moss, "contained_in") and moss.contained_in else None

    if not container:
        print("Moss is not in a container.")

    from env_data import locRegistry as loc
    if moss.location != loc.inv_place:
        print(f"moss location != loc.inv_place: {moss.location}")
        if moss.contained_in:
            container = moss.contained_in
            if (container.location == loc.inv_place or container.is_open == False or container.location.place.inside == True):
                print("container in inv or closed or inside")
                event_state = "continues"
            else:
                print("container not in inv or open or outside")
                event_state = "failure"
        else:
            if moss.location.place.inside == False:
                print("moss location is outside")
                event_state = "failure"
            else:
                print("moss.location is inside")
                event_state = "play_exception"
    else:
        print("moss in inv")
        event_state = "continues"

    return event_state

def break_item_handling(event, trigger, item):
    print("Here we break an item if breakable, remove it and replace it with an appropriate broken version.")
    from itemRegistry import itemInstance
    item:itemInstance = item
    if not hasattr(item, "can_break") or not item.can_break:
        print(f"Item {item} cannot be broken. Returning.")
        return None # if succesful, return the new broken obj, else return None if nothing happened and the old obj remains.

    if hasattr(item, "material_type") and item.material_type:
        mat_type = item.material_type
        print(f"Item `{item.name}` has material type {mat_type}")

