#item_interactions.py


from re import I
from interactions.player_movement import relocate
from itemRegistry import itemInstance, registry
from env_data import cardinalInstance, locRegistry as loc
from misc_utilities import assign_colour, has_and_true
from logger import logging_fn
from printing import print_green
import verb_actions

def look_at(response):
    print("[LOOK_AT] in item interactions.")
    print(f"Response: {response}")


def show_map(noun):
    #bring the noun in here in case there are multiple maps later.
    from config import show_map, map_file
    if show_map:
        print()
        print_green("<     Showing Map.     >", invert=True)
        import os
        os.startfile(map_file)


def look_at_item(item_inst, entry): ## this is just using everything from registry. Should really just be in registry....
    """Checks an item is viable to be seen, then looks at the item. If the item is a loc_exterior that is nearby to the player, instead turns to face that cardinal and prints the description. If the item has children, they will be printed in a list. If the item is a map-item and show_map==True, it will open the map image externally."""
    logging_fn()
    if isinstance(item_inst, itemInstance):
        #print(f"item_inst.location: {item_inst.location}")
        container, reason_val, meaning = registry.run_check(item_inst)
        logging_fn(f"reason_val: {reason_val}")
        #print(f"Look at item MEANING: {meaning}")
        if reason_val not in (0, 5, 8):
            text = entry["text"]
            print(f"You can't see the {assign_colour(text)} right now.")
            return
        else:
            if reason_val == 8:
                relocate(new_cardinal=item_inst.location)
                return

            if reason_val == 2:
                extra = " in your inventory:"
            else:
                extra = ":"

            print(f"You look at the {assign_colour(item_inst)}{extra}")

            print(f"\n   {assign_colour(registry.describe(item_inst, caps=True), colour="description")}")
            if hasattr(item_inst, "is_open") and item_inst.is_open:
                verb_actions.print_children_in_container(item_inst)

            if hasattr(item_inst, "is_map"):
                show_map(item_inst)


def set_attr_by_loc(attr = "is_hidden", val = "False", location=None, items=None):
    """Sets item attributes to all items in a given location. Used to set location-wide states (eg items hidden if location is made dark, etc.)"""
    logging_fn()
    from itemRegistry import registry
    instances = set()

    if items and isinstance(items, itemInstance):
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
    """Old function for moving an item to a location. Not sure why it doesn't just use move_item directly; need to remove this later."""
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

def is_loc_ext(noun:itemInstance, return_trans_obj=False) -> str|None:
    """Used for finding and/or referring to transition objects for location exterior objects."""
    if hasattr(noun, "is_loc_exterior") and hasattr(noun, "transition_objs"):
        for trans_obj in noun.transition_objs:
            if return_trans_obj:
                return trans_obj
            return f"You can't enter the {assign_colour(noun)}, but maybe the {assign_colour(trans_obj)}?"

    return None


def get_correct_cluster_inst(noun:itemInstance, noun_text=None, priority="single", local_only=False, access_str = None, allow_hidden=False, local_items:set=None) -> itemInstance: ## Not implemented yet. Moving from verb_
    """For determining the correct ItemInstance to select when interacting with cluster-type items. Will prioritise 0-val cluster items when picking up, will prioritise multiple-val cluster items when looking for a drop target to merge with, etc. Can allow hidden objects to be selected.\n\nIf no local items are provided, will generate with find_local_item_by_name using the criteria it was given."""
    logging_fn()

    if not (hasattr(noun, "has_multiple_instances") and hasattr(noun, "single_identifier") and hasattr(noun, "plural_identifier")):
        print(f"Noun {noun} does not have the identifiers required for get_correct_cluster_inst. Returning.")
        return

    plural_id = noun.plural_identifier
    single_id = noun.single_identifier

    if not noun_text and priority:
        if priority == "single":
            noun_text = single_id
        else:
            noun_text = plural_id

    if not local_items:
        local_items = find_local_item_by_name(current_loc=loc.current, hidden_cluster=allow_hidden, access_str=access_str)

    local_clusters = list((i for i in local_items if i.name == noun.name))
    if local_clusters and len(local_clusters) == 1:
        #print("Only one item in local_clusters, returning.")
        return local_clusters[0]

    if local_clusters and (not noun_text or (noun_text and (plural_id in noun_text or single_id in noun_text))):
        singles = set()
        plurals = set()

        hidden_singles = list(i for i in local_clusters if i.has_multiple_instances == 0)
        #print("allow_hidden: ", allow_hidden, f"// access_str: {access_str} // noun_text: {noun_text}")
        if access_str in ("local_and_inv_containers_only") and allow_hidden:
            for item in hidden_singles:
                if hasattr(item, "is_hidden") and item.is_hidden:
                    #print("item is_hidden: ", item.is_hidden,"; returning immediately.")
                    return item

        for item in local_clusters:
            if (item.has_multiple_instances <= 1 if allow_hidden else item.has_multiple_instances == 1):
                singles.add(item)

        if not singles or priority == "plural":
            for item in local_clusters:
                if item.has_multiple_instances >= 1:
                    plurals.add(item)

        new_noun = None
        if priority == "plural" and plurals:
            for item in plurals:
                if item.has_multiple_instances > 1: # only accept +1 for the first round. Shouldn't be necessary because it should always find the right one when dropping, but for now it's belt and bracers.
                    new_noun = item
                    break
            if not new_noun:
                for item in plurals:
                    new_noun = item
                    break

        if priority == "single" and singles:
            for item in singles:
                if item.has_multiple_instances == 0:
                    new_noun = item
                    break
            if not new_noun:
                for item in singles:
                    new_noun = item
                    break

        if not new_noun:
            print(f"Not new noun: {local_clusters}")
            new_noun = local_clusters[0]
        noun = new_noun

    return noun


def recurse_items_from_list(input_list:list) -> set:
    """ Gets the first level of children from any provided list. Excludes hidden children and only searching in unlocked and unhidden containers."""
    logging_fn()
    children = set()

    for item in input_list:
        if "container" not in item.item_type or has_and_true(item, "is_hidden") or has_and_true(item, "is_locked"):
            continue
        if has_and_true(item, "children") and item.is_open:
            for child in item.children:
                if not has_and_true(child, "is_hidden"):
                    children.add(child)
    return children

#container, reason_val = registry.check_item_is_accessible(noun_inst)
no_containers = ["only_loc_no_containers", "loc_w_inv_no_containers"]
no_inventory = ["not_in_inv", "only_loc_no_containers", "combine_cluster", "drop_target", "pick_up"]
no_local = ["inv_and_inv_containers", "drop_subject", "inventory_only"]
in_inv_children = ["local_and_inv_containers_only"]

## Put strings here to use as 'search terms' to look for in no_containers/no_inventory/no_local. Eg for drop, whether it's subject or target changes things, so just using the verb doesn't work.
simple_assignments = ["drop_subject", "drop_target", "pick_up", "inventory_only"]

scope_to_verb = {
    "inv_and_inv_containers": ["drop"], # only things in inventory, including recursion.
    "all_local": ["look", "find", "burn", "fire_source", "use"], # everything accessable, carried/ local/etc
    "local_and_inv_containers_only": ["take"],
    "not_in_inv": ["pick_up"], # includes local containers, just nothing I'm already carrying.
    "only_loc_no_containers": [""], # No idea what would call for this tbh. It's just 'stuff you can see around you'.
    "loc_w_inv_no_containers": [""], # this one either. This'll take some development.
    }

def build_relevant_items_set(verb=None, noun=None, access_str=None, current_loc=None) -> set: # moved this to be its own thing so I can use it elsewhere.
    """Builds a set of itemInstances based on the verb and access_str provided. Will generate the access_str from the verb if needed.\n\nDoes not pay attention to names, only the categories to allow/ignore."""
    logging_fn()
    location = None

    if not access_str and verb:
        for kind, values in scope_to_verb.items():
            if verb in values:
                access_str = kind
                break
        if not access_str:
            print(f"Verb `{verb}` could not find a match in verb allocation.\nExpected one of:\n{list(scope_to_verb)}. Cannot continue.")
            exit()

    elif access_str:
        if not scope_to_verb.get(access_str) and not access_str in simple_assignments:
            print(f"find_local_items access_str is not a valid key: {access_str}. Expected one of:\n{list(scope_to_verb)} or \n{simple_assignments}. Cannot continue.")
            exit()
    else:
        access_str = "all_local"

    inv_items = None
    if access_str in no_inventory:
        inv_items = None
    else:
        inv_items = loc.inv_place.items
    if inv_items and access_str not in no_containers:
        children = recurse_items_from_list(inv_items)
        if children and access_str not in in_inv_children:
            inv_items = set(children|set(inv_items))
        elif children and access_str in in_inv_children:
            inv_items = children
        elif not children and access_str in in_inv_children:
            inv_items = set()

    if access_str in no_local:
        loc_items = None
    else:
        if current_loc and isinstance(current_loc, cardinalInstance):
            location = current_loc
        elif current_loc and isinstance(current_loc, str):
            location = loc.by_cardinal_str(current_loc)
        elif (not current_loc or not location) and noun and isinstance(noun, itemInstance):
            location = noun.location
        from env_data import locRegistry
        if not location or location == locRegistry.inv_place: #assume current.
            location = locRegistry.current

        loc_items = registry.get_item_by_location(location)
        if loc_items and access_str not in no_containers:
            children = recurse_items_from_list(loc_items)
            if children:
                loc_items = set(children|set(loc_items))

        if access_str in no_inventory and not loc_items:
            return None, access_str

    if not inv_items and not loc_items:
        return None, access_str
    if inv_items and not loc_items:
        final_items = inv_items
    elif loc_items and not inv_items:
        final_items = loc_items
    else:
        final_items = ((inv_items | (set(loc_items))) if inv_items else set(loc_items))

    if hasattr(location, "transition_objs") and location.transition_objs:
        for item in location.transition_objs:
            final_items.add(item)
    return final_items, access_str

def find_local_item_by_name(noun:itemInstance=None, noun_text = None, verb=None, access_str:str=None, current_loc:cardinalInstance=None, hidden_cluster=False, priority="single") -> itemInstance|set:
    """
    Builds relevant items set using verb scope derived from `access_str` or `verb`'s status in `verb_to_noun_access`. If `noun` provided, returns the relevant `ItemInstance` of that name if found. If no `noun` provided, returns the full set.

    priority == ('single' | 'plural')
    """
    logging_fn()

    if verb:
        from verbRegistry import VerbInstance
        if isinstance(verb, VerbInstance):
            verb = verb.name

    if isinstance(noun, str):
        if noun_text and noun != noun_text:
            print(f"Noun is a string: {noun}. Noun_text is also present: {noun_text}.")
        if noun == "assumed_noun" and noun_text:
            noun = noun_text

    final_items, access_str = build_relevant_items_set(verb, noun, access_str, current_loc)

    #print(f"Access str: {access_str}\nFINAL ITEMS: {final_items}\n Hidden: {hidden_cluster}")
    if not final_items:
        return None

    if noun:
        if isinstance(noun, itemInstance):
            if noun in final_items and "is_cluster" in noun.item_type:
                if access_str in ("pick_up", "not_in_inv", "local_and_inv_containers_only"):
                    single_and_local = True
                else:
                    single_and_local = False
                if access_str == "drop_target":
                    priority = "plural"
                if noun.location == loc.inv_place and access_str == "drop_subject":
                    #print(f"ACCESS STR for noun in inv_place: {access_str}\nnoun is in inventory and we want a noun to drop, skip get_correct_cluster_inst")
                    return noun

                #print(f"Sending {noun} to get_correct_cluster_inst. Access str: {access_str}")
                test = get_correct_cluster_inst(noun, noun_text, local_items=final_items, local_only = True if single_and_local else False, access_str = access_str, allow_hidden=hidden_cluster, priority=priority if priority else "single")
                if test:
                    noun = test
                    return noun

            noun_name = noun.name
        elif isinstance(noun, str):
            noun_name = noun

        if registry.by_alt_names.get(noun_name):
            noun_name = registry.by_alt_names.get(noun_name)

        for item in final_items:
            if item.name == noun_name and ((not has_and_true(item, "is_hidden") or "is_cluster" in item.item_type)):
                return item
    else:
        return final_items

def find_local_items_by_itemtype(item_type, access_str):

    temp_str = None
    if access_str == "inv_then_local":
        temp_str = access_str
        access_str = "inventory_only"

    local_items, _ = build_relevant_items_set(verb=None, noun=None, access_str=access_str)
    #print(f"LOCAL ITEMS: {local_items}")
    local_items = list(i for i in local_items if item_type in i.item_type)
    if local_items:
        return local_items

    if temp_str and temp_str == "inv_then_local": # belt and braces
        access_str = "not_in_inv"
        local_items, _ = build_relevant_items_set(verb=None, noun=None, access_str=access_str)
        #print(f"LOCAL ITEMS: {local_items}")
        local_items = list(i for i in local_items if item_type in i.item_type)
        if local_items:
            return local_items
        print(f"No items of type `{item_type}` found using `{access_str}`")
        return None
    #print(f"LOCAL ITEMS WITH `{item_type}`: {local_items}")


