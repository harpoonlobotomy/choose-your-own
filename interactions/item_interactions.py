#item_interactions.py


from interactions.player_movement import turn_around
from itemRegistry import ItemInstance, registry
from env_data import cardinalInstance, locRegistry as loc
from misc_utilities import assign_colour
from logger import logging_fn
from printing import print_green
import verb_actions

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

def show_map(noun):
    #bring the noun in here in case there are multiple maps later.
    from config import show_map, map_file
    if show_map:
        print()
        print_green("<     Showing Map.     >", invert=True)
        import os
        os.startfile(map_file)

def look_at_item(item_inst, entry): ## this is just using everything from registry. Should really just be in registry....
    if isinstance(item_inst, ItemInstance):

        #print(f"item_inst.location: {item_inst.location}")
        confirmed, container, reason_val, meaning = registry.check_item_is_accessible(item_inst)
        #print(f"Look at item MEANING: {meaning}")
        if reason_val not in (0, 5, 8):
            text = entry["text"]
            print(f"You can't see the {assign_colour(text)} right now.")
            return
        else:
            if reason_val == 8:
                turn_around(item_inst.location)
                return

            if reason_val == 2:
                extra = " in your inventory:"
            else:
                extra = ":"

            print(f"You look at the {assign_colour(item_inst)}{extra}")

            print(f"\n   {assign_colour(registry.describe(item_inst, caps=True), colour="description")}")
            if hasattr(item_inst, "is_open") and item_inst.is_open:
                verb_actions.print_children_in_container(item_inst)

            #print(f"game.map_item id: {game.map_item.id}")
            #print(f"item_inst id: {item_inst.id}")
            if hasattr(item_inst, "is_map"):
            #from set_up_game import game
            #if item_inst == game.map_item:
                #print("item inst is map")
                show_map(item_inst)


def set_attr_by_loc(attr = "is_hidden", val = "False", location=None, items=None):
    logging_fn()
    from itemRegistry import registry
    instances = set()

    if items and isinstance(items, ItemInstance):
        if hasattr(items, attr) and getattr(items, attr):
            print(f"Items {items} is an instance and will be set directly.")
            setattr(items, attr, val)
            return
        print(f"Item(s) were provided but failed to set attributes: {items}. Continuing by using location.")

    if location:
        named_local = {}
        local_items = registry.get_item_by_location(location)
        if local_items:
            for item in local_items:
                named_local[item.name] = item

        if items:
            if isinstance(items, str):
                if items in named_local:
                    #print(f"Found local item: {items}")
                    instances.add(named_local[items])


            elif isinstance(items, set):
                for item in items:
                    if isinstance(item, str):
                        if item in named_local:
                            #print(f"Found local item: {item}")
                            instances.add(named_local[item])

    for item in instances:
        #print(f"Instances: {item}")
        if hasattr(item, attr) and getattr(item, attr):
            setattr(item, attr, val)
            #print(f"SET ATTRIBUTE: {item}, {attr}, {val}")

def add_item_to_loc(item_instance, location=None):

    if location == None:
        location = loc.current
    elif location != loc.current:
        print(f"You're currently at {loc.current.place_name}. You can't leave {item_instance.name} at {location.name} unless you move there first.")

    if isinstance(location, cardinalInstance):
        registry.move_item(inst=item_instance, location=location)
    else:
        exit("add_item_to_location needs a cardinalInstance.")


### Now a whole bunch of functions for parsing out open/close actions.
#Kinda wish this was a class of lil functions. Might be an idea? idk. I'm used to classes holding data sets, not functions. Will have to look into it.

def is_loc_ext(noun:ItemInstance, return_trans_obj=False) -> str|None:

    if hasattr(noun, "is_loc_exterior") and hasattr(noun, "transition_objs"):
        for trans_obj in noun.transition_objs:
            if return_trans_obj:
                return trans_obj
            return f"You can't enter the {assign_colour(noun)}, but maybe the {assign_colour(trans_obj)}?"

    return None

#container, reason_val = registry.check_item_is_accessible(noun_inst)
