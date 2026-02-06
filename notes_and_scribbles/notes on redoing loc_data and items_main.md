notes on redoing loc_data and items_main. (I will refer to items_main as item_defs throughout.)

# Important notes at the top to fill in as I go:
  ###     fields removed/renamed/added     ###

    Remove 'item_definitions.py', not in use by game scripts (though edit_item_defs and test_class use it, so remove the dependency from those to make sure nothing dies weirdly )and just makes things needlessly confusing.

Remove from items_main:
    hidden=False
    (item_type) 'all_items'
    renamed "name" to "nicename" so it matches the scripts' usage.

Removed from loc_data entries:

    "event_item"
    "event_key"
    "long_desc" - replaced with item_desc[generic] in all cases, uniformly.

Added to loc_data entries:

    "is_container" -- if an item is not usually a container (eg the scroll a key falls out of; not a typical container.)
    "container_limits" - if is_container is present.


Changed in event_defs:

    rename "trigger" to "triggers_on" (maybe?) Bit less confusing. That or 'trigger_action', but that makes it sound like it triggers this action, not like this is the action triggering the trigger. Triggers_on might best. Oh - 'triggered_by'? Not sure.
#   Going with 'triggered_by' for now.




Need to move a lot of parentage data from items to loc_data, where it should be. Going to keep notes here to try to keep track.

Default attrs for items in [loc][card]["items"]:

"description": null, # really description is the only one it truly needs. Anything missing we just take directly from item_defs, so the only things tha need listing here are things that vary for this specific instance of {item}. So if they can usually be picked up, we don't need to add item_type[can_pick_up] etc.


"is_hidden": false,
"is_container": true

Now, I don't think I need is_hidden if it's false. we can assume false if not hasattr(inst, "is_hidden") instead. (I think that was an artifact of item_defs, its not done in loc_data.)
(Note: Some items have all those fields in loc_data, that's because it was added to generated items then added to item_defs from there. Can clear it out later if I can be bothered.)


NOTES ON ATTRS IN LOC_DATA:

          "event_key": true,
          "event": "graveyard_gate_opens",
vs
          "event_item": true,
          "event": "graveyard_gate_opens"

'event_key' == a trigger item.
'event_item' == an item effected by the event.
I don't think I properly implemented that in eventsReg tbh. Need to look into it later.
idk if it's helpful to separate keys and items here. We define what the triggers are in event_defs, let's just say 'event': {event_name: <name>}' and leave it at that. Obviously it's an event item, it's an item with the event flag. Actually no, it doesn't even need to be event>event_name>name. Just event: {event_name} directly. No needless nesting. Obviously it's an event name, what else would it be.

So, if an item is an event item:

loc: {
    card: {
        items: {
            <item_name>: {
                "description": "description of the thing if locally relevant, else 'null' and use item_defs.
                "event": <event_name>

if is_locked:
                "is_locked": true,
                "key_is_placed_elsewhere": true

    # NOTE: #key_is_placed_elsewhere means 'the key is listed as an item in another location, so don't just create a new one.
    But... fuck. If it doesn't have that, what, it just creates an instance and puts it... nowhere?
    I guess I could add a random spawn func. If a thing needs a key, that key will be... somewhere. That could be fun.

NOTE: I also have lock/key data in event_defs. That kind of makes sense though, because the lock would theoretically still use the same key, probably.
Alright - if the event stops the combination from working, then it's only in event_defs. If the lock and key are a pair outside of the event, then it should be given in loc_data too. Though there should be a way to combine those datasets so we don't have to find the data for each twice. (This would be where the item_defs from Registry come in, which I briefly imported to eventReg.)

What I should do though, is unify the language, so functionally-alike flags in event_defs resemble those in loc_data (and item_defs).
Will need to keep track of these changes so I can fix the relevant scripts later.

eg iron_key:

>   Mentioned in event_defs:

#   [event effects]:
#           "hidden_items": {
#               "0": {
#                   "item_name": "iron key",
#                   "item_location": "north work shed"}}},

   and tertiarily:
#       "end_trigger":
#           {"item_trigger": {
#               "trigger_item": "padlock",
#               "trigger_location": "north graveyard",
#               "trigger": ["item_broken", "item_unlocked"],
#               "on_event_start": {
                    "requires_key": "iron key",
#                   "key_is_placed_elsewhere": {
#                       "item_in_event": "reveal_iron_key"}
#                   }

>   in loc_data:
#       [loc][card]:
#           "items": {
#               "padlock": {
#               "event_key": true,
#               "event": "graveyard_gate_opens",
#               "is_locked": true,
#               "requires_key": "iron key",
#               "key_is_placed_elsewhere": true
#               },

    and as its own item in loc_data:
#        "iron key": {
#          "description": "An old iron key, pitted on the surface but still appears functional.",
#          "is_key_to": "padlock",
#          "lock_in_same_event": true,
#          "is_hidden": true,
#          "event": "graveyard_gate_opens"
#        }

    and in items_main:
#     "iron key": {
#       "name": "iron key",
#       "item_type": "{'key', 'can_pick_up'}",
#       "is_key": true,
#       "can_pick_up": true,
#       "item_size": 0,
#       "description": "An iron key, handy for a quest or something, probably.",
#       "is_key_to": "padlock",
#       "is_hidden": false

[[ Note: I need "container_limits" if is_container is present for an item. But what if it's not /really/ a container? Like the scroll. tbh I guess it could be a mini event, though the system isn't really set up for that, tiny little item interactions that happen once and then end. Hm.

I've made so many changes the shrine doesn't actually work anymore so I can't even test how it used to work, hah.

Will set up an event route for it. ]]

back to iron key:
    Need to remove is_key_to from item defs, and make the description something a little more usable.
    Also need to remove is_hidden: False from the dict, I can add that in item_dict_gen if I really need to.


Note: For glass jar:

All of these need changing:
    Description needs to be generalised ('Holds [...]'/ "you see [...]', something like that.)
    Name should just be about the glass jar, as much as I enjoy seeing the flowers. Maybe I can set that as an event type? remove_children type or something; the name is x /description is y while starting_children are present, becomes z/a when removed.

 "name": "a glass jar with flowers"
 "description": "a glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers."
"starting_children": [
"name_no_children": "an empty glass jar",
"description_no_children": "a glass jar, now empty aside from some bits of debris.",


Going to trial this:

    "child_removed_name_desc": {
        "starts_current": false,
        "immediate_action": {
            "item_trigger": {
                "container_name": "glass jar",
                "trigger_item": "dried flowers",
                "trigger_location": "east graveyard",
                "triggered_by": ["removed_from_container"]},

            "container": {
                "container_name_w_child_removed": "a glass jar",
                "container_desc_w_child_removed": "a glass jar, looks like it had jam in it once by the label."

Though those last two lines make me think it should be an event that starts at init and runs until the flowers are removed, buuuut that might never happen, don't want to add more to events.current than I need to.

Actually no, it doesn't need to be an event.

Just do like this:

if hasattr(inst, "description_no_children") and inst.description_no_children != None:
    description = inst.description_no_children

    but when the children are removed, change the inst.name. Though that might fuck things up elsewhere...

I mean I do already have
    def nicename(self, inst: ItemInstance):
        logging_fn()
        if "container" in inst.flags:
            children = self.instances_by_container(inst)
            if not children:
                return inst.name_children_removed

that does exactly that but only for nicename (which is the one that mentions the flowers, soooo it's already doing it.).
Actually I need to rename 'name' in items_main to 'nicename', because that's what it is in every script. 'inst.name' is just the dict key.


Okay. So, for this one:

    "scroll_drops_key": {
        "starts_current": false,
        "immediate_action": {
            "item_trigger": {
                "trigger_item": "scroll",
                "trigger_location": "north shrine",

The trigger item location is north shrine (originally), but it doesn't need to be there for the event to happen. I need a way to specify that. Because sometimes an event can only trigger in a specific place.
For now have renamed the line to
                "trigger_item_location": "north shrine",
so trigger_location will be nulled, indicating the location doesn't matter.

So:

    "scroll_drops_key": {
        "is_quick_event": true,
        "starts_current": false,
        "immediate_action": {
            "item_trigger": {
                "trigger_item": "scroll",
                "trigger_item_location": "north shrine",
                "triggered_by": ["item_opened"]}
            }
        },
        "effects": {
            "held_items": {
                "0": {
                    "item_name": "old gold key"}},
            "hidden_items": {
                "0": {
                    "item_name": "old gold key"}}

No item location for old_gold_key - item is generated in event run, and placed in whatever location you're currently in.

Have added "is_quick_event": true to both the scroll and the child_removed_name_desc.

Probably going to wipe the child_removed_name_desc tho, it already does it it turns out. It was just broken beause of the child/container mismatch.

For prosterity:
,
    "child_removed_name_desc": {
        "is_quick_event": true,
        "starts_current": false,
        "immediate_action": {
            "item_trigger": {
                "trigger_item": "dried flowers",
                "container_name": "glass jar",
                "trigger_location": "east graveyard",
                "triggered_by": ["removed_from_container"]},

            "container": {
                "container_name_w_child_removed": "a glass jar",
                "container_desc_w_child_removed": "a glass jar, looks like it had jam in it once by the label."
            }
        }
    }
