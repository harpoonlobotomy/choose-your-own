#script to initialise the verb/item/etc classes just the once, so they can't fuck with each other out of order.

#import time


def initialise_all():

    ## The order here matters. Need to have the locations done first, so the items can use the location objects. Then items, so verbRegistry can use the itemRegistry.
    import env_data
    env_data.initialise_placeRegistry()
    print("initialised placeregistry")

    import itemRegistry
    event_data = itemRegistry.initialise_itemRegistry()
    print("initialised itemregistry")

    env_data.get_loc_descriptions()

    import verbRegistry
    verbRegistry.initialise_verbRegistry()
    print("initialised verbregistry")

    import eventRegistry
    eventRegistry.initialise_eventRegistry()
    eventRegistry.add_items_to_events(event_data)
    #time.sleep(.5)
