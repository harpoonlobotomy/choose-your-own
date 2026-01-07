#script to initialise the verb/item/etc classes just the once, so they can't fuck with each other out of order.

def initialise_all():

    from os import system
    system("cls")

    import itemRegistry
    import verbRegistry

    itemRegistry.initialise_itemRegistry()
    print("initialised itemregistry")
    verbRegistry.initialise_verbRegistry()
    print("initialised verbregistry")

    import env_data
    env_data

    from set_up_game import set_up
    test=True
    if test:
        set_up(weirdness=True, bad_language=True, player_name="Testing initialise_all")

