"""Save and load gamestate data"""

"""
Plan: 3 save slots. 'Continue' on opening screen will just open the last played saveslot (last played saveslot saved in config file)

on load, load savedata and recreate worldstate.
on save, save savedata to json file.
on exit, prompt to save or not save. and/or autosave pref.
Have to decide on autosave. Autosave y/n, and/or player decision saved in config.

"""
from env_data import cardinalInstance
from eventRegistry import Trigger, eventInstance, timedTrigger
from itemRegistry import itemInstance
from npcRegistry import npcInstance


save_file = "savegame.json"

def save_game():
    """
    Save items/npcs/events/etc. Note: Keep generated IDs and reuse those same ids, so tracked items will still track (eg if an event has a particular piece of moss tied to it, it should re-track to the same ID, and the loaded moss entity should be assigned that same ID.)
    For items: locations, cluster val if cluster, broken/burned/etc state if found, encountered state.
    for npcs: encountered state, state of conversations, trade items/inventory.
    for events: event state, current duration if timed, names/identifiers of items. (Save item IDS and reuse, so a specific item tied to a quest still has that same ID tied to it - easier and vastly more reliable than trying to match by metadata)

    I don't know if there are any sets involved in anything that needs saving but if so need to change them to lists.

    """
    from itemRegistry import registry
    from env_data import locRegistry
    from npcRegistry import npc_Registry
    from eventRegistry import events

    """ Will need to write a new initialiser for each of these. The current one won't work, and if I run a new version + the current, it'll likely be more complicated than otherwise. Current initialisers are only for first init with no savegame."""

    save_dict = {}

    def get_item_data(save_dict):
        save_dict["items"] = {}
        for item in registry.instances:
            save_dict["items"][item.id] = {}#{"name": {item.name}, "location": {item.location.place_name}}
            #print(f"item name: {item.name}")
            #("location": {item.location.place_name})
            """ Nicename/nicenames, can_be_charged etc are all static qualities that cannot change across saves. Need to more clearly define which attributes of an item are static and which are variable.
            For each variable attribute, if the variable is different to the baseline default, it needs to be listed in the save file. So if a cluster type has a cluster val of 1, it needs to list that in the save file, but it doesn't need to list the description, as that is static.

            item.__dict__ entries for itemInstance:
                id
                short_id
                material_type
                on_break
                verb_actions
                item_type
                is_hidden
                can_break
                slice_attack
                slice_defence
                smash_attack
                smash_defence
                details
                has_datapoint
                not_in_loc_desc
                can_burn
                is_burned
                can_be_opened
                is_open
                can_be_closed
                name
                print_name
                nicenames
                nicename
                colour
                descriptions
                description
                starting_location
                location
                event
                is_event_key
                encountered
                held_by
                trade_value
                alt_names
    """
            for attr in ("name", "starting_location", "location", "requires_key", "held_by", "is_locked", "is_open", "colour", "event", "encountered", "contained_in"):
                value = getattr(item, attr) if hasattr(item, attr) else None
                if value or (hasattr(item, attr) and not getattr(item, attr)):

                    if value == item.start_dict[attr] and attr not in ("location", "name"):
                        continue#print(f"Attr {attr} matches at save")

                    if isinstance(value, itemInstance|npcInstance):
                        #id = value.id
                        value = value.id
                    elif isinstance(value, eventInstance):
                        #id = value.id
                        value = value.id
                    elif isinstance(value, cardinalInstance):
                        #cardinal_name = value.place_name
                        value = value.place_name
                    elif isinstance(value, bool):
                        #boolean = value
                        value = value
                    elif isinstance(value, str):
                        #boolean = value
                        value = value
                    elif isinstance(value, set|list):
                        if isinstance(list(value)[0], itemInstance|npcInstance):
                            #value_list = [list(i.id for i in value)]
                            value = list(i.id for i in value)
                            print("values now ids")
                        if isinstance(value[0], list) and len(value) = 1:
                            print("value = value [0]")
                            value = value[0]
                        else:
                            print(f"value is a set|list, but not of items: {value}")

                    else:
                        print(f"Attr {attr} does not match at save")

                    save_dict["items"][item.id][attr] = value

        return save_dict

    def get_event_data(save_dict):
        event_elements = {}
        elements_to_save = ("priority", "triggers", "start_triggers", "end_triggers", "items", "event_keys", "held_items", "hidden_items", "locked_items", "remove_items", "start_trigger_location", "end_trigger_location", "condition_items", "no_item_restriction", "constraint_tracking", "timed_triggers", "child_item", "is_generated_event", "start_trigger_is_item", "end_trigger_is_item", "start_trigger", "end_trigger", "item_trigger_is_item", "travel_limited_to")
        from eventRegistry import registrar
        for event in events.events:

            event_elements[event.id] = {"state": event.state}

            for attr in elements_to_save:
                value = getattr(event, attr) if hasattr(event, attr) else None
                new_value = value
                if not hasattr(registrar.by_name[event.name], attr):
                    if not value:
                        continue
                    #print(f"registrar.by_name couldn'#t find attr [`{attr}`] for {event.name}, value is {value}")
                elif value == getattr(registrar.by_name[event.name], attr):
                    #print("Value is same in registrar, continuing")
                    continue

    # now we've stripped the things we don't need to save, continue to get something saveable.

                if isinstance(value, list|set):
                    new_value = []
                    for item in value:
                        if not isinstance(item, Trigger|timedTrigger|itemInstance|cardinalInstance):
                            print(f"item `{item}` of value {value} is not Trigger, timedTrigger, itemInstance, or cardinalInstance. Value: {item}/type: {type(item)}")
                        else:
                            if isinstance(item, Trigger|timedTrigger|itemInstance):
                                new_value.append(item.id)
                            else:
                                new_value.append(item.place_name)
                            #pass#print(f"Itme [{item}] in {value} is an establisehd type.")

                elif not isinstance(value, Trigger|timedTrigger|itemInstance|cardinalInstance):
                    print(f"Value is not Trigger, timedTrigger, itemInstance, or cardinalInstance. Value: {value}/type: {type(value)}")

                else:
                    if isinstance(value, Trigger|timedTrigger|itemInstance):
                        new_value = value.id
                    else:
                        new_value = value.place_name

                event_elements[event.id][attr] = new_value

            event_elements[event.id]["name"] = event.name
        #print(f"event elements: {event_elements}")
        save_dict["events"] = event_elements
        return save_dict
        """
keys with types:
    [`triggers`]: Trigger
    [`end_triggers`]: Trigger
    [`items`]: itemInstance
    [`event_keys`]: itemInstance
    [`end_trigger_location`]: cardinalInstance
    [`triggers`]: Trigger
    [`start_triggers`]: Trigger
    [`items`]: itemInstance
    [`event_keys`]: itemInstance
    [`triggers`]: Trigger
    [`end_triggers`]: Trigger
    [`items`]: itemInstance
    [`event_keys`]: itemInstance
    [`end_trigger_location`]: cardinalInstance

                """

                    #print(f"Registrar has this attr [`attr`] but it's different:\n{getattr(registrar.by_name[event.name])} / value on event currently: {value}")
            #for item in event.__dict__:
            #    if item not in event_elements:
            #        event_elements[item] = event.__dict__[item]
            #        print(item, f"value is type: {type(event.__dict__[item])}")


# [`triggers`]: Trigger #{<[Trigger] [ID:0d791] [event: graveyard_gate_opens / state: 0 / ID:0d791] [Trigger item: padlock/1fbc38360941]>}
# [`end_triggers`]: Trigger #{<[Trigger] [ID:0d791] [event: graveyard_gate_opens / state: 0 / ID:0d791] [Trigger item: padlock/1fbc38360941]>}
# [`items`]: itemInstance #{<ItemInst [padlock ID:1fbc38360941] [loc: north graveyard] [event:'graveyard_gate_opens' ID:284d6 state: 0] >, <ItemInst [gate ID:39c03f0325b1] [loc: north graveyard] [event:'graveyard_gate_opens' ID:284d6 state: 0] >}
# [`event_keys`]: itemInstance #{<ItemInst [padlock ID:1fbc38360941] [loc: north graveyard] [event:'graveyard_gate_opens' ID:284d6 state: 0] >}
# [`end_trigger_location`]: cardinalInstance # <cardinalInstance north graveyard (d2484467-d0b4-4cc8-a7af-604301cce5de)>
# [`triggers`]: Trigger #{<[Trigger] [ID:04596] [event: scroll_drops_key / state: 2 / ID:04596] [Trigger item: scroll/527b8cb0375f]>}
# [`start_triggers`]: Trigger #{<[Trigger] [ID:04596] [event: scroll_drops_key / state: 2 / ID:04596] [Trigger item: scroll/527b8cb0375f]>}
# [`items`]: itemInstance #{<ItemInst [scroll ID:527b8cb0375f] [loc: north shrine] [event:'scroll_drops_key' ID:5d875 state: 2] >}
# [`event_keys`]: itemInstance #{<ItemInst [scroll ID:527b8cb0375f] [loc: north shrine] [event:'scroll_drops_key' ID:5d875 state: 2] >}
# [`triggers`]: Trigger#{<[Trigger] [ID:cf5e6] [event: reveal_iron_key / state: 0 / ID:cf5e6] [Trigger item: local map/afc0feb7a1fe]>}
# [`end_triggers`]: Trigger#{<[Trigger] [ID:cf5e6] [event: reveal_iron_key / state: 0 / ID:cf5e6] [Trigger item: local map/afc0feb7a1fe]>}
# [`items`]: itemInstance #{<ItemInst [local map ID:afc0feb7a1fe] [loc: north inventory_place] [event:'reveal_iron_key' ID:2420e state: 0] >, <ItemInst [iron key ID:0c699c7d3ae4] [loc: north inventory_place] [event:'reveal_iron_key' ID:2420e state: 0] >}
# [`event_keys`]: itemInstance #{<ItemInst [local map ID:afc0feb7a1fe] [loc: north inventory_place] [event:'reveal_iron_key' ID:2420e state: 0] >}
# [`end_trigger_location`]: cardinalInstance # <cardinalInstance north work shed (721a0bfe-d20a-4b21-944c-95eb4417f604)>



        """ All event datapoints:
#   Will need to at some point set up a proper 'state' system, where it can reset triggers etc automatically. So instead of having to record all trigger IDs, knowing that at x state, there are y triggers, and regenerate them. Though the triggers do need the correct items, so maybe keeping IDs is fine for now even if it feels messy.

            Things to save:
                    id > always save  [type: <class 'str'>]
                    priority > save if not default  [type: <class 'int'>]
                    triggers > save trigger IDs if any else None - if None, still overwrite. Current is extremely important.  [type: <class 'set'>]
                    start_triggers > save trigger IDs  [type: <class 'set'>]
                    end_triggers > as above  [type: <class 'set'>]
                    items > if any, save item IDs  [type: <class 'set'>]
                    event_keys > as above  [type: <class 'set'>]
                    held_items > save if differs  [type: <class 'set'>]
                    hidden_items > save if differs  [type: <class 'set'>]
                    locked_items > as above  [type: <class 'set'>]
                    remove_items > will not differ  [type: <class 'set'>]
                    start_trigger_location save placename if placename not default  [type: <class 'NoneType'>]
                    end_trigger_location save placename if placename not default  [type: 'env_data.cardinalInstance'>]
                    condition_items > item ids  [type: <class 'set'>]
                    no_item_restriction > don't remember what it is  [type: <class 'dict'>]
                    constraint_tracking > don't remember what it is, should stay default  [type: <class 'dict'>]
                    timed_triggers > timed ids  [type: <class 'set'>]
                    child_item > item ids if used at all  [type: <class 'NoneType'>]
                    is_generated_event > autopopulate  [type: <class 'NoneType'>]
                    start_trigger_is_item > item id if anything  [type: <class 'bool'>]
                    end_trigger_is_item > item ID if anything  [type: <class 'bool'>]
                    start_trigger > trig id if any  [type: <class 'NoneType'>]
                    end_trigger > trig id if any  [type: <class 'dict'>] # NOTE: end_trigger is a dict.
                    item_trigger_is_item > item id  [type: <class 'bool'>]
                    travel_limited_to > list of places, store as list of str place_names.  [type: <class 'list'>]


            name  [type: <class 'str'>]
            id > always save  [type: <class 'str'>]
            short_id  [type: <class 'str'>]
            state > always save  [type: <class 'int'>]
            priority > save if not default  [type: <class 'int'>]
            triggers > save trigger IDs if any else None - if None, still overwrite. Current is extremely important.  [type: <class 'set'>]
            start_triggers > save trigger IDs  [type: <class 'set'>]
            end_triggers > as above  [type: <class 'set'>]
            items > if any, save item IDs  [type: <class 'set'>]
            event_keys > as above  [type: <class 'set'>]
            generate_on_start   > should always be default.  [type: <class 'set'>]
            effects_on_start > should always be default  [type: <class 'dict'>]
            item_name_to_inst > Regen from existing item associations.  [type: <class 'dict'>]
            msgs > will be default.  [type: <class 'dict'>]
            limits_travel > save if differs  [type: <class 'bool'>]
            init_items > will not differ  [type: <class 'dict'>]
            held_items > save if differs  [type: <class 'set'>]
            hidden_items > save if differs  [type: <class 'set'>]
            locked_items > as above  [type: <class 'set'>]
            remove_items > will not differ  [type: <class 'set'>]
            start_trigger_location save placename if placename not default  [type: <class 'NoneType'>]
            end_trigger_location save placename if placename not default  [type: 'env_data.cardinalInstance'>]
            condition_items > item ids  [type: <class 'set'>]
            no_item_restriction > don't remember what it is  [type: <class 'dict'>]
            constraint_tracking > don't remember what it is, should stay default  [type: <class 'dict'>]
            timed_triggers > timed ids  [type: <class 'set'>]
            child_item > item ids if used at all  [type: <class 'NoneType'>]
            is_generated_event > autopopulate  [type: <class 'NoneType'>]
            start_trigger_is_item > item id if anything  [type: <class 'bool'>]
            start_trigger_is_attr > will always be default, no?  [type: <class 'bool'>]
            attr_triggers > will always be default  [type: <class 'set'>] NOTE: attr_triggers is a set
            end_trigger_is_item > item ID if anything  [type: <class 'bool'>]
            item_names > autopopulate  [type: <class 'set'>]
            item_name_to_loc > autopopulate  [type: <class 'dict'>]
            print_description_plain > auto  [type: <class 'set'>]
            starts_current > will always be default  [type: <class 'bool'>]
            is_timed_event > auto  [type: <class 'NoneType'>]
            remove_event_on_completion > auto  [type: <class 'NoneType'>]
            remove_event_on_run > auto  [type: <class 'NoneType'>]
            remove_event_on_failure > auto  [type: <class 'NoneType'>]
            start_trigger > trig id if any  [type: <class 'NoneType'>]
            end_trigger > trig id if any  [type: <class 'dict'>] # NOTE: end_trigger is a dict.
            item_trigger_is_item > item id  [type: <class 'bool'>]
            end_type > will be default  [type: <class 'str'>]
            limit_travel > will always be default, is a bool of effects travel/doesn't  [type: <class 'bool'>]
            travel_limited_to > list of places, store as list of str place_names.  [type: <class 'list'>]
name value is type: <class 'str'>
id value is type: <class 'str'>
short_id value is type: <class 'str'>
state value is type: <class 'int'>
priority value is type: <class 'int'>
triggers value is type: <class 'set'>
start_triggers value is type: <class 'set'>
end_triggers value is type: <class 'set'>
items value is type: <class 'set'>
event_keys value is type: <class 'set'>
generate_on_start value is type: <class 'set'>
effects_on_start value is type: <class 'dict'>
item_name_to_inst value is type: <class 'dict'>
msgs value is type: <class 'dict'>
limits_travel value is type: <class 'bool'>
init_items value is type: <class 'dict'>
held_items value is type: <class 'set'>
hidden_items value is type: <class 'set'>
locked_items value is type: <class 'set'>
remove_items value is type: <class 'set'>
start_trigger_location value is type: <class 'NoneType'>
end_trigger_location value is type: <class 'env_data.cardinalInstance'>
condition_items value is type: <class 'set'>
no_item_restriction value is type: <class 'dict'>
constraint_tracking value is type: <class 'dict'>
timed_triggers value is type: <class 'set'>
child_item value is type: <class 'NoneType'>
is_generated_event value is type: <class 'NoneType'>
start_trigger_is_item value is type: <class 'bool'>
start_trigger_is_attr value is type: <class 'bool'>
attr_triggers value is type: <class 'set'>
end_trigger_is_item value is type: <class 'bool'>
item_names value is type: <class 'set'>
item_name_to_loc value is type: <class 'dict'>
print_description_plain value is type: <class 'set'>
starts_current value is type: <class 'bool'>
is_timed_event value is type: <class 'NoneType'>
remove_event_on_completion value is type: <class 'NoneType'>
remove_event_on_run value is type: <class 'NoneType'>
remove_event_on_failure value is type: <class 'NoneType'>
start_trigger value is type: <class 'NoneType'>
end_trigger value is type: <class 'dict'>
item_trigger_is_item value is type: <class 'bool'>
end_type value is type: <class 'str'>
limit_travel value is type: <class 'bool'>
travel_limited_to value is type: <class 'list'>
Exiting now.ue is type: <class 'dict'>
        """
        #print(f"EVENT ELEMENTS: {event_elements}")

    #def get_npc_data(save_dict):
        #for npc in npc_Registry.npcs:


    save_dict = get_item_data(save_dict)
    save_dict = get_event_data(save_dict)

    with open(save_file, mode="w+") as f:
        import json
        json.dump(save_dict, f, indent=2)

def load_game():

    with open(save_file, mode="r") as f:
        import json
        save_data = json.load(f)

    item_data = save_data["items"]
    event_data = save_data["events"]
    ## Now this should be every established item + event. Which is fucking stupid but the best I have for now. Without getting all of them there's no reliable way to check if they're default or not, so it's just everything. (I can check if an equvalent exist, but what if I picked up thing_a and put in in place_a, removing thing_b from that place. If thing_b and thing_a share default metadata, I can't track that they've swapped by just 'is location start location'. So, will take all items id, name and location, then rebuild specific instances from there.)

    from item_dict_gen import generator
    from itemRegistry import registry
    from copy import deepcopy
    for id, data in item_data.items():
        name = data["name"]
        item_dict = deepcopy(generator.item_defs[name])

        for attr, val in data.items():
            if val == item_dict.get(attr):
                print(f"Is default, why was this saved?: {attr}: {val}")
            else:
                item_dict[attr] = val

            #if attr == "item_type":
            #    if "container" in data[attr] and not "electronics" in data[attr]:

            #if inst.print_children_as_list:

        new_item = registry.init_single(name, item_entry=item_dict, apply_location=data["location"], discover=(data["encountered"] if data.get("encountered") else False))

