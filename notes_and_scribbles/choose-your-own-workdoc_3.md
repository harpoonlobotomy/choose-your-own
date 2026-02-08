[Another new file because they just get too long. Really should make cleaner logs.]

12.22pm 7/2/26
def push is checking 'if "door_window" in noun.item_type:', but failing, for `wooden door`.
Looking into it, that... isn't used, anywhere. Assumedly I was going to add that at some point. Seems superfluous when is_open/is_locked etc exist, but, a thing can be an open container but not be able to close, so I still want it. So, will just... implement that now.

If I knew all transition objs would be doors/windows I would just use that, but there's a chance they won't, and I don't want to make arbitrary associations like that if I can avoid it.
Huh. I also have 'is_door' but literally nothing in item_defs has that either. Maybe that was something that never made it past generated_items and got wiped. Eh.

I mean I do have

    "transition": {"is_transition_obj": True, "enter_location": None, "exit_to_location": None},
Could just add is_door/is_window to that. Might be a better idea.
Have done that for now, will implement those and see how it goes.

Although no. Doesn't work. Because there might well be doors/windows that /aren't/ transition objects. Okay, door_window type_default it is.

I need to make item defs more expansive, with intention.
Instead of
    "description": "a yellowed [[]] showing the region surrounding the graveyard.",
when an item can be burned/broken/etc, I really need 'description' to be a tree, set depending on item state.

Also - is it better to update the descriptions whenever a change is made, or update them when the description printing is called. Because right now it's the latter, but descriptions get called at every scene change, even without explicit 'look around' input.
For item descriptions it's easy enough; if an item is broken, we change item.description to be descriptions["broken_desc"] and move on. But the scene descriptions are trickier.

Though I can probably decouple those a bit. I did notice the other day that it's basically impossible to just generate one cardinal's description, even if that's all you need.
Idk the best way to manage it. Keeping an extra reference of some kind to check if anything's happened since last description update just feels silly. And redoing the entire descriptions routine, well that I can fix, just need to modularise it a bit.

So, for the 'items having multiple descriptions, currently I have things like this:

#   "if_open_description": "a plain wooden door, sitting slightly ajar",
    "description":

(plus similar in loc_data).
Instead of that, it should be descriptions: {"general": {"a closed wooden door", "if_open": {a plain wooden door, sitting slightly ajar"}}}
etc.
And if it only has the one, then fine. If it has multiple, then we update those if they're relevant. So the item description only ever gets checked when something of it might change.

That doesn't help the scene descriptions, though.

Main thing for that is, be able to only get desc for the current cardinal, because often that's all that's asked for and needed.

12.51pm
Working on the attr setup and got distracted when I realised I was adding attrs from itemReg + locdata repeatedly (flags for type_default entries from item_type). Looked into it, and it's necessary because
        for flag in type_defaults[category]:
            print(f"FLAG: {flag}")
            if flag not in item_dict: # so it doesn't overwrite any custom flag in a loc item entry
                print(f"{flag} WAS NOT IN ITEM DICT")
                item_dict[flag] = type_defaults[category][flag]

always gives `item_dict[flag] == None`.

So, going to figure out why now.
Oh, right. Because I was only ever pulling the key. Okay. Should be an easy fix...


So, paperclip in item_dict_gen:

NOW item_dict: {'nicename': 'a paperclip', 'description': 'a humble paperclip.', 'item_type': "{'can_pick_up'}", 'alt_names': {}, 'is_hidden': False, 'can_pick_up': True, 'item_size': 'small_flat_things', 'loot_type': 'starting', 'started_contained_in': None, 'contained_in': None}
(now that I fixed the dict access)

But then, in item defs:

<ItemInstance paperclip (8b18bd14-5b26-4036-a856-e1c9edcc6cd6)>  ITEM TYPE: can_pick_up
FLAG started_contained_in not in attr for paperclip
FLAG contained_in not in attr for paperclip

Hm.
So:
#   [init_single] ITEM NAME: paperclip
#   [init_single] ITEM ENTRY: {'nicename': 'a paperclip', 'description': 'a humble paperclip.', 'item_type': "{'can_pick_up'}", 'alt_names': {}, 'is_hidden': False, 'can_pick_up': True, 'item_size': 'small_flat_things', 'loot_type': 'starting'}

At the start of init for the item instance, it's seeming using the raw item_def data, not item_dict_gen. Which... was the whole point of item_dict_gen. (Not that I'm entirely convinced of it, but it makes sense in my head to have a reference of the dynamically-updated item data, separate from the instances. Idk, could be wrong on that.)
But either way, right now item_dict_gen is meant to be used, and apparently it's not. That's not exactly ideal. Will figure out why and try to fix.

Oh ffs. It's because I was explicitly removing those fields, only to add them back in later. They're meant to have the vals removed if they're exported/saved, but the fields should stay, ffs. Okay.

Okay. So now I believe it's only the work shed that for some reason has fields missing;
#   FLAG is_loc_exterior not in attr for work shed
#   FLAG transition_objs not in attr for work shed
#   FLAG has_door not in attr for work shed

Ah, it's because I gave it the loc_exterior item_type in loc_data, not item defs. Okay.

Okay, fixed. Now the duplicate section has been removed from itemReg. Will remove more later, there's so much duplicate work there because much of it is done by item_dict_gen and/or item_interactions now. I really want itemReg to just be the place that creates and manages the instances themselves, not how they act in the world and not drawing data from files raw etc.


**So - descriptions. (So distracted but I'm getting something done at least...?)**
Right now, whenever you call registry.describe() for an item, it goes through the children check, compiles the long_desc, checks for open-state, etc, then capitalises and returns.

Seeing as there aren't /that/ many things that actually change item descriptions, I'm thinking of adding a check to those functions (that add/remove children, that open/close, etc; will have to make a shortlist) and updating the description at that point. It feels like it introduces risk, as if a new function misses that section, the description won't update. But, it does mean def describe() just has to take the current (and assumed to be correct and up-to-date) description and make it pretty, instead of going through all the children, compilation etc.  We run the full current descrip once on init, then just update the descrip when something that could alter it is altered. So if we open something, we check for is_open description, etc.

Now, a quirk that hasn't come up yet (but would apply to either the current system or the one described) is what if something is open /and/ has children/no children/etc. So, clashing/simultaneous descriptions. Will just have to make sure they work together, or add specific ones for open_with_children etc. Can always make it formulaic.


Also, not right now but TODO: add more to def read(). No time action yet so it can wait but will be good to test that soon.


item_type `container`:

    "descriptions": {
        "starting_children_only": "a glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers",
        "any_children": "a glass jar, holding ",
        "no_children": "a glass jar, now empty aside from some bits of debris.",
        "open_starting_children_only": "a glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers",
        "open_any_children": "a glass jar, holding ",
        "open_no_children": "a glass jar, now empty aside from some bits of debris"},

If something can have children, it needs at least 'any_children' and 'no_children'. 'no_children' can just be 'it's a simple glass jar', it doesn't have to reference the lack of children, but it should be there. Can formulate this part if I need to, so if it's missing just take the name and do x. A clearly outlined formula of what's expected will be good. (Currently I play a bit loose with these so they sound good, which works on a small scale and I'll probably keep doing, but there should be a 'default' setup that works nicely for the things I don't want to spend so much time on.)


3.06pm
Okay, so the 'update on change' instead of 'update on print' is implemented for containers. Need to do the same for other things that open/close (the only real other example I have currently for 'items with different description states'; door, gate, padlock, etc) so will do that next.


4.51pm open/close done.


1.37pm
Working on the item editor script, just want to clean up the dict now I've changed flags etc and having this set up going forward is just a good plan. It was kind of already set up but not in the way I need, its old function was largely replaced by meta commands.

Oh, need to set up a change name fn in itemReg too. So if an item is broken it becomes 'broken {item}', and updates by_name etc accordingly. If I want to, can always just change the description and the nicename or smth. Or go with the idea I had the other day of storing a 'print name' separately from the item name. Will see. Trouble with that idea is again, someone has to type it in, i the name they see isn't the name they have to type that just feels like a nightmare.

1.38pm
Hey here's a question. Why am I storing item_types as str in itemRef then remaking it into a list every single time? Why not just make it a list? It's only a set in the live file because it automatically deduplicates. Should just make it a list when exporting instead of a str. ffs. DO THIS.

1.50pm
Trying to figure out the best thing to do with descriptions. Because I've added `descriptions: {generic: None}` to the 'standard' item (better to have a single entry dict and use the descriptions for all items than have some use the dict and others use 'description', I think? though maybe not, idk), but containers still have
    "container": {"is_open": False, "can_be_opened": True, "can_be_closed": True, "can_be_locked": True, "is_locked": True, "requires_key": False, 'starting_children': None, 'container_limits': 4, "name_no_children": None, "name_any_children": None, "description_no_children": None, "description_any_children": None},
their descriptions given as separate tags.

so maybe I add 'descriptions' in 'container' too? So I don't have to later convert those tags into descriptions: entries, but they're still included.
Though wait, no, that's /names/. Aw fuck. Okay. No more custom names. It's nice having 'glass jar with flowers' vs 'glass jar' but idk if it ever actually updated.
Or, I have `names: {with_starting_children: "glass jar with flowers"}`. But I really don't want a dict for each name. Really I should just... not change the names. As much as I like it. Idk.
For now will add a separate 'names' dict and just not implement it.

No, that's just silly.
Adding
<container_name>: {
    "names": {starting_children_only: "container with starting_children name"}
}
just for starting children is silly. Okay. Will leave starting_children name there.

OOOOH. it didn't update item.name, it updated /nicename/. Okay we can keep that.
So in that case we can add a dict for nicename.

    "nicename": "a simple glass jar",
    "nicenames": {
        "name_no_children": "an empty glass jar",
        "name_any_children": "a simple glass jar",
        "name_starting_children_only": "a glass jar with dried flowers in it"
    }

So I'll remove 'nicename', and will add a check in the nicename section for if not hasattr(item, "nicename"), use the relevant nicenames entry.

### THING TO REMEMBER ###
Containers may not have nicename entry. Use empty/not empty/start_children_only name respectively.
Also in this case, update the description-update section to also update the container's nicename so it's always just 'item.nicename'.

Removed 'name_' from the
    "nicenames": {
        "name_no_children": "an empty glass jar",
        "name_any_children": "a simple glass jar",
        "name_starting_children_only": "a glass jar with dried flowers in it"
    }
entries, so the formatting matches descriptions. So instead of nicenames:name_no_children then
descriptions: no_children,
it can do the exact same operation for nicenames and descriptions.

Have added
"descriptions":
            {"if_closed": "", "if_open": ""}
to door_window. So it's a little messy because containers can also be open/closed, but are only described by their contents. But I think it makes enough sense.

Actually no. Adding that description to can_open instead, and will just set it up so the descriptions of 'container' override the descriptions of can_open.

## NOTE ##
wire cutters item def has
"key"
but also
requires_key:None.
Replacing 'key' with 'requires_key'. May have to update itemReg/gen item dict.

Now the trouble with
 "requires_key": "wire cutters",
 is that the wire cutters aren't actually a key. So though it'll work in the code properly as they function as keys, the description 'you unlock x with y' won't apply. Also, you wouldn't write 'unlock jar with wire cutters'. So maybe they shouldn't be a key in that sense. idk. Will have to look at that one. TODO: how to implement 'open jar wrapped in wire using wire cutters' and figure out how that'll work.

Really, if I type 'open jar with wire cutters', even if I don't write 'unlock', if y is a key to x, it should unlock. Implement that.

Removed
    "special_traits": "After 3 ingame days, after being picked up and kept in inventory, will dry. If dry, no longer suitable for commerce with bridge goblin.",
from moss' item def.

# Also TODO: I hvae 'has_multiple_instances' in the moss entry but it doesn't do anything anywhere.

Have added
    "nicenames": {
        "if_singular": "a clump of moss",
        "if_plural": "a few moss clumps"},
    "descriptions": {
        "if_singular": "a small clump of moss, mostly green with brown specks.",
        "if_plural": "a few clumps of mostly green moss."},
to implement later for the multiple_instances.

Because the event desc only applies because of the open door, changing
   "event_ended_desc": "Heavy wrought iron bars with little decoration, now slightly ajar.",
   to just be the if_open description. Will need to adapt itemReg and/or generate_descriptions accordingly.

NOTE:
# Should remove "is_key": True, from key type_default, because if item_type.get("key"), then is_key is always true.


Also:
I should move the detailed descriptions for magazines etc to item defs unless they need to be rolled for. Not even really sure I want to keep the rolling tbh. Maybe on repeated reads, instead? So, you read it bit by bit. Or both, you read it bit by bit and each time it rolls, so it makes sense that you have the chance to get the information. With better odds each time, until it's guaranteed on the last go. Maybe. idk.


Also, I should remove 'flammable: true' from entries, and just use the presence of 'item_type: flammable'. I use item_type so heavily already, makes sense to just /rely/ on the existing of an item_type tag instead of checking for the presence and value of 'is_flammable'.
