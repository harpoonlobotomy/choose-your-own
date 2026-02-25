#script to initialise the verb/item/etc classes just the once, so they can't fuck with each other out of order.

#import time


def initialise_all():
    """Initialises `placeRegistry`, `itemRegistry` and `verbRegistry` in that order, then initialises `eventRegistry` and adds items to events, then runs `get_loc_descriptions`."""
    ## The order here matters. Need to have the locations done first, so the items can use the location objects. Then items, so verbRegistry can use the itemRegistry.
    import env_data
    env_data.initialise_placeRegistry()
    print("initialised placeRegistry")

    import itemRegistry
    itemRegistry.initialise_itemRegistry()
    print("initialised itemRegistry")

    import verbRegistry
    verbRegistry.initialise_verbRegistry()
    print("initialised verbRegistry")

    import config
    if not config.parse_test:
        import eventRegistry
        eventRegistry.initialise_eventRegistry()
        eventRegistry.add_items_to_events()

    #print("get_loc_descriptions() being run in initialise_all")
    #env_data.get_loc_descriptions() # Moved here so the event data is in place. No idea how it works before but not now, I can't see which change affected it, but it seems to work as long as I init the descriptions at the end (which makes sense anyway).
    #time.sleep(.5)

if __name__ == "__main__":
    initialise_all()
