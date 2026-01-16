#item_interactions.py

#Instinctively I want a new script for item interactions, that I can send to from membrane. But isn't that what the itemRegistry is for?
#It kinda is...
from itemRegistry import ItemInstance, registry
from env_data import cardinalInstance, locRegistry as loc
from misc_utilities import assign_colour
from logger import logging_fn

def look_at(response):
    print("[LOOK_AT] in item interactions.")
    print(f"Response: {response}")


def instance_name_in_inventory(inst_name:str)->ItemInstance:
    logging_fn()
    from set_up_game import game
    item_entry = registry.instances_by_name(inst_name)
    if item_entry and isinstance(item_entry, list):
        for entry in item_entry:
            if entry in game.inventory:
                return entry

    #print(f"Did not find entry for {inst_name}")

def look_at_item(item_inst): ## this is just using everything from registry. Should really just be in registry....

    if isinstance(item_inst, ItemInstance):
        #print(f"item_inst.location: {item_inst.location}")
        confirmed, container, reason_val, meaning = registry.check_item_is_accessible(item_inst)
        print(f"Look at item MEANING: {meaning}")
        if reason_val not in (0, 5):
            print(f"Cannot look at {item_inst.name}.")
        else:
            if reason_val == 2:
                extra = " in your inventory."
            else:
                extra = "."
            print(f"You look at the {item_inst.name}{extra}")
            print(assign_colour(registry.describe(item_inst, caps=True), colour="description"))
            children = registry.instances_by_container(item_inst)
            if children:
                print(f"\nThe {assign_colour(item_inst)} contains:")
                from misc_utilities import col_list
                children = ", ".join(col_list(children))
                print(f"  {children}")


def add_item_to_loc(item_instance, location=None):

    if location == None:
        location = loc.current
    if location != None and location != loc.current:
        print(f"You're currently at {loc.current.place_name}. You can't leave {item_instance.name} at {location.name} unless you move there first.")

    if isinstance(location, cardinalInstance):
        registry.move_item(inst=item_instance, location=location)
    else:
        print("add_item_to_location needs a cardinalInstance.")
        exit


#container, reason_val = registry.check_item_is_accessible(noun_inst)
