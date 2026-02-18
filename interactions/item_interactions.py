#item_interactions.py


from interactions.player_movement import turn_around
from itemRegistry import ItemInstance, registry
from env_data import cardinalInstance, locRegistry as loc
from misc_utilities import assign_colour, has_and_true
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
no_containers = ["only_loc_no_containers", "loc_w_inv_no_containers"]
no_inventory = ["not_in_inv", "only_loc_no_containers"]
no_local = ["inv_and_inv_containers"]

verb_to_noun_access = {
    "inv_and_inv_containers": ["drop"], # only things in inventory, including recursion.
    "all_local": ["look", "find"], # everything accessable, carried/ local/etc
    "not_in_inv": ["take"], # includes local containers, just nothing I'm already carrying.
    "only_loc_no_containers": [""], # No idea what would call for this tbh. It's just 'stuff you can see around you'.
    "loc_w_inv_no_containers": [""] # this one either. This'll take some development.
    }
#note: inv_containers must be open.
def recurse_items_from_list(input_list:list) -> set:

    children = set()

    for item in input_list:
        if "container" not in item.item_type or has_and_true(item, "is_hidden") or has_and_true(item, "is_locked"):
            continue
        if has_and_true(item, "children"):
            for child in item.children:
                # Possibly we get cluster names /here/ rather than at print-time.
                #Or, we do that when things open. When you open a container w/ children, check cluster status. Probably better to do it then  rather than just when looking.
                if not has_and_true(child, "is_hidden"):
                    children.add(child)
    return children


def find_local_item_by_name(noun:ItemInstance=None, verb=None, access_str:str="all_local", current_loc:cardinalInstance=None) -> set:
    ## DO NOT FORGET ABOUT place(/or card, which is it).loc_exterior_items
## First we have to build the relevant local_items for the search. This should probably be a primary function to use elsewhere tbh but this'll do for now.
    location = None
    if access_str and verb:
        for kind, values in verb_to_noun_access.items():
            if verb.name in values:
                if access_str != kind:
                    print(f"Conflict between access_str `{access_str}` and the verb's allocation: `{kind}`. Will continue with access_str, but the conflict should be remedied.")
                break

    elif not access_str and verb:
        for kind, values in verb_to_noun_access.items():
            if verb.name in values:
                access_str = kind
                break
        if not access_str:
            print(f"Verb `{verb.name}` could not find a match in verb allocation.\nExpected one of:\n{list(verb_to_noun_access)}. Cannot continue.")
            exit()

    elif access_str and not verb:
        if not verb_to_noun_access.get(access_str):
            print(f"find_local_items access_str is not a valid key: {access_str}. Expected one of:\n{list(verb_to_noun_access)}. Cannot continue.")
            exit()

### Processing starts now we have an access_str to work with. ###
## Get inventory items.
    inv_items = None
    if access_str in no_inventory:
        inv_items = None
    else:
        inv_items = loc.inv_place.items
    if inv_items and access_str not in no_containers:
        children = recurse_items_from_list(inv_items)
        if children:
            inv_items = set(children|set(inv_items))

    if access_str in no_local:
        loc_items = None
    else:
        if current_loc and isinstance(current_loc, cardinalInstance):
            location = current_loc
        elif current_loc and isinstance(current_loc, str):
            location = loc.by_cardinal_str(current_loc)
        elif (not current_loc or not location) and noun:
            location = noun.location
            if not location:
                #assume current.
                from env_data import locRegistry
                location = locRegistry.current
       #else:
        #    print("Cannot get location: no location provided and no noun to take location from. Cannot continue; exiting.")
        #    exit()
        loc_items = registry.get_item_by_location(location)

        if loc_items and access_str not in no_containers:
            children = recurse_items_from_list(loc_items)
            if children:
                loc_items = set(children|set(loc_items))

        if access_str in no_inventory and not loc_items:
            print("No local items at all. Returning.")
            return

    final_items = ((inv_items | (set(loc_items) if isinstance(loc_items, list) else loc_items)) if inv_items else set(loc_items))

    if hasattr(location, "transition_objs") and location.transition_objs:
        #print(f"LOCATION: TRANSITION OBJS: {location.transition_objs}")
        for item in location.transition_objs:
            print(f"TRANS ITEM: {item}, item_type: {type(item)}")
            final_items.add(item)
        #for item, val in location.transition_objs.items():
        #    print(f"TRANS ITEM: {item}, item_type: {type(item)}, val: {val}")

            #TRANS ITEM: wooden door, item_type: <class 'str'>, val: {'enter_location': 'north work shed', 'exit_to_location': 'west graveyard'}
    print(f"FINAL ITEMS for location {location} for noun {noun}:::\n{final_items}\n\n")
    if noun:
        print("Here is where we check the set we've made against the name")
    else:
        print("No noun given, will just return the set wholecloth.")
        return final_items
    #exit()
        #if hasattr(location, "transition_objs") and location.transition_objs:
        #    for item, val in location.transition_objs.items():
        #        print(f"ITEM `{item}` type: {type(item)}")
        #        exit()
        #        loc_items.append(item)



        # includes trans obj, inv and inv containers, local items + items in open local containers (I don't yet have the discovered tag but need it for this, really - I don't want to tell you 'that open jar has a thing in it', but if you've already found it then I don't mind listing it as an option. For now I'll just use open containers but that needs doing, #TODO at some time.)


    #from verb_membrane import membrane
    #if membrane.local_dict.get(noun.name):
