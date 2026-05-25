"""Save and load gamestate data"""

"""
Plan: 3 save slots. 'Continue' on opening screen will just open the last played saveslot (last played saveslot saved in config file)

on load, load savedata and recreate worldstate.
on save, save savedata to json file.
on exit, prompt to save or not save. and/or autosave pref.
Have to decide on autosave. Autosave y/n, and/or player decision saved in config.

"""
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

    for item in registry.instances:
        id = item.id
        name = item.name # so I can get the item data from item_dict_gen on load
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
# attrs that are definitely variable and will need adding to the save file if not matching default:
        colour = item.colour# = if not None, save, so an item's colour is consistent across play sessions
        item.encountered
        item.event # do I ever use item.event? Wouldn't it be better to check the events to see if this item is on it? I guess this is more direct in a situation where there are many events and lookin through each for each item just to check is ridiculous. Okay yes, we keep it.
        item.children
        item.can_break
        item.can_burn
        item.contained_in
        item.in_use
        item.is_broken
        item.is_burned
        item.is_charged
        item.is_charging
        item.has_batteries
        item.has_multiple_instances
        item.held_by
        item.is_event_key
        item.is_hidden
        item.is_key_to
        item.is_locked
        item.is_on
        item.is_open
        #item.key_is_placed_elsewhere # only applicable when am item is required for an event, so as long as the event state is correctly saved, the default can stay as is.
        item.location

        """
        Do I need to change 'False' for 'None' or can I save 'False' to json? Ah, right, it'll save as 'false' and python does what switch automatically. Okay good. So None/False are both fine."""
