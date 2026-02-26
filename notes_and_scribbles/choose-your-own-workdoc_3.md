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

In the course of that, for fragile, instead of just 'can_break', am adding

    "fragile":
        {"is_broken": False, "slice_threshold": 1, "smash_threshold": 10},

the ints for slice and smash threshold are just sharp vs blunt damage, which will do for now. So, curtains are smash threshold 10 (virtually unsmashable (or 11 for 'literally unsmashable'), and slice threshold of 1, because they're easy to cut. Should work I think. No idea if it'll ever actually get used. Haven't even got 'cut' as a verb yet. Should do that.)

Have also added slice and smash threshold of 5 to 'standard' items, so unless otherwise written, all items are 5 across the board.

5.15pm
Swapped event flag can_repeat_forever for just using the preexisting "repeats" an assiging val of "forever". Neither was implemented yet anyway.

6.34pm
Cleared some unnecessary work from generate_descriptions, it was getting the description for every cardinal every time, including item_desc, even if only one cardinal was used.
Have set it up now so it does the full run once (like it does with items), then only get the item_desc for the facing cardinal (as that's all that will be printed anyway). It was needless busywork to do it the other way. Might still be able to clean it up further, but this is good for now.

9.56pm
Hm.
read magazine for a while
Failed parser: 0

Interesting. Why 0?

10.07pm
So. No answer yet but:

(  Func:  verbReg_Reciever    )
values: ([Token(idx=0, text='read', kind={'verb'}, canonical='read'), Token(idx=1, text='puzzle', kind=('noun',), canonical='puzzle mag'), Token(idx=3, text='for', kind={'direction'}, canonical='for'), Token(idx=4, text='update_json', kind={'meta'}, canonical='update_json'), Token(idx=5, text='while', kind=set(), canonical=None)],)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=0, text='read', kind={'verb'}, canonical='read') // kinds: {'verb'}",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=1, text='puzzle', kind=('noun',), canonical='puzzle mag') // kinds: {'noun'}",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=3, text='for', kind={'direction'}, canonical='for') // kinds: {'direction'}",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=4, text='update_json', kind={'meta'}, canonical='update_json') // kinds: {'meta'}",)

(verbReg_Reciever is just a function I made that I can send vars to so they'll print when I print logging args. There's a better way no doubt but it works temporarily, I can just throw it wherever I want and it prints only when I print args. Later can add a bool to config to turn it on/off.)

But what's interesting is that 'a' ended up with kind meta and test update_json. Assumedly that's just the last option it checks, but it shouldn't be applied. Especially when 'a' should be excluded as 'null' anyway.

Okay so that's because I had told it to always use second_ results even if not second canonical. So it was just filling with whatever it could even if it didn't match.

Okay so the apparent issue is here

                    if not viable_sequences:
                        meta = meta_instances[0]
                        token = meta[0] <--
                        instance = Parser.get_viable_verb(token)

But that issue is only happening because it applied
meta from meta_instances: {3: Token(idx=3, text='update_json', kind={'meta'}, canonical='update_json')}

to what was actually "a".

Fixed it now, alt_words were just strings, not list as they should be, so it was matching 'a' to the alt_word 'update'.


1.22am 9/2/26
Okay so why:

values: ("Tokens after tokenise: [Token(idx=0, text='read', kind={'verb'}, canonical='read'), Token(idx=1, text='mag', kind={'noun'}, canonical='gold key'), Token(idx=2, text='for', kind={'sem'}, canonical='for'), Token(idx=3, text='a', kind={'null'}, canonical='a'), Token(idx=4, text='while', kind={'sem'}, canonical='while')]",)

Why does 'read mag for a while'
end up with 'mag' being 'gold key'????

values: ('Tokenise: idx: 1, word: mag',)
item in local_named: gold key

Okay so why

current_loc_items: None
local nouns: set()

are these both empty?

it's past midnight, I need sleep, but fix this tomorrow. verbRegistry, around ln 192.


10.58am 9/2/26
Huh so this is odd:

locRegistry.current: <cardinalInstance south work shed (2df43f0c-f7c3-46f1-a034-620414af2c13)>
current_loc_items: None
local nouns: set()

Added a print to check what 'current' was at the time of init, and apparently it's south work shed?
When it comes to print the game it's graveyard, I'm not sure where south work shed is coming from.

I'm not sure where the location is actually being set. It used to just be in set_up_game, but this runs before that, so I don't know. I assume it's just the last location to be init'd.

11.09am
Yes - so it was actually working before, but because it was randomly setting current to the last created location (still need to figure out exactly why, but that's what's happening) it was correctly finding no local items. If I set the starting location to east graveyard, it finds the items it should.


Okay. So, I do need to change plural_words_dict, or change how the parser deals with local/accessible items.
Currently it only deals with local/accessible items at the end, which is preferable in some ways. But, it makes it inconsistent - if there's no magazine and I say 'read mag', it says 'can't find any 'mag' to work with', which is a failure within compound_words, which is different to the error it would have if I said 'read alien', because 'alien' wouldn't be recognised as a noun, so the error would be at the sequencer level (or earlier if I tell it not to simply nullify not-found nouns.)

The trouble is, it doesn't know if it's actually a noun that just isn't accessible (as in there is a jar, but it's somewhere else) or if you wrote djkhskj and that's why it can't find it locally. If you give it the full noun list, then you get more custom messages like 'you can't pick up something that isn't near you' (trying to pick up a thing in a different place) which I like, but also means you get messages using that item's full name. I don't like that it gives different messages either way. Like if you randomly got a spawn with the catalogue and said 'throw catalogue', you'd get an error about how it can't throw the mail order catalogue yet because I haven't written it. But in that same game if you wrote 'throw magazine', it'd error because magazine isn't a word.

So idk.

Maybe we give it the full word list, but if no instance found we /don't/ let it update the cardinal. So we say 'yes this is a noun, but it's only called 'catalogue' like you typed and we don't know any more about it'. Still means you have a difference between 'catalogue' (if it exists in the item_defs) and 'dogalogue' (if it doesn't), but it's better than it saying 'there's no mail order catalogue to touch' when you didn't give it 'mail order', nor see that anywhere.
I think that's better.

I think the trouble is that it doesn't assign the noun instance at that point in the parser. Maybe I need to add another field to tokens for 'originally typed', bc right now we have what, 'kinds', 'canonical', 'instance', and nouns don't fill instance until later. I guess there's no real reason why not? idk.

But it's good to know the verb membrane is correctly generating the local items dict.

So. We identify noun-kind via the full item_defs, not just instanced things, so that's our full noun list. But, we preserve the original text, not the final item name, and print that for any errors where the instance is unavailable. I think.

Oh, I forgot this:

values: ("token_role_options: Token(idx=1, text='mag', kind={'noun'}, canonical='gold key') // kinds: {'noun'}",)

it was assigning 'gold key' to a noun if it couldn't find it. That's not good.

values: ('Tokenise: idx: 1, word: mag',)
item in local_named: gold key

11.24am
I really broke this yesterday.

values: ('Tokenise: idx: 1, word: mag',)
item in local_named: gold key



Okay so that was happening because I told it to match basically anything to local items, entirely my fault and very obvious. That bit's fixed now.

So, now the question is, why this:

(  Func:  instances_by_name    )
definition_key: gardening mag
noun_name: None
(  Func:  router    )
viable_format: ('verb', 'noun', 'sem', 'sem')
inst_dict: {0: {'verb': {'instance': <verbInstance read (8f60f640-bda8-45bf-844b-78865b0134e2)>, 'str_name': 'read'}}, 1: {'noun': {'instance': <ItemInstance gardening mag (8d0eb771-e162-4339-84b1-972e46813108)>, 's[[  read gardening mag for while  ]]m': {'instance': None, 'str_name': 'for'}}, 3: {'sem': {'instance': None, 'str_name': 'while'}}}


^ hard to make sense of but it worked for 'read mag for a while'.

But then next time:

(  Func:  verbReg_Reciever    )
values: ("top of token_role_options: Token(idx=4, text='while', kind={'sem'}, canonical='while')",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=4, text='while', kind={'sem'}, canonical='while') // kinds: {'sem'}",)
(  Func:  verbReg_Reciever    )
values: ("return for sequences: viable sequences: [['verb', 'noun', 'sem', 'sem']]",)
(  Func:  verbReg_Reciever    )
values: ("sequences after sequencer: [('verb', 'noun', 'sem', 'sem')]",)
(  Func:  instances_by_name    )
definition_key: gardening mag
[ Couldn't find anything to do with the input `read mag for a while`, sorry. ]


Okay so, rerunning it, sometimes it works, sometimes it doesn't. I don't know why.

11.43am
Added more prints:

fashion mag is in inventory before this runs.
item in compound matches: fashion mag
item not in local named

So it's not finding it for some reason.

And for catalogue (which is not in item defs at all)
values: ('Tokenise: idx: 1, word: catalogue',)
WORD: catalogue, PARTS: ['read', 'catalogue', 'for', 'a', 'while']
WORD: catalogue, PARTS: ['read', 'catalogue', 'for', 'a', 'while']

it doesnt' even get to that point, because there's only one potential match to 'catalogue'.

Oh, so inventory isn't init'd until later, so local_named doesn't include it. Not sure then why the mags are sometimes found. Very odd.

What I should do is add a type called 'error', so I can add an error type (as in 'this is part of a non-present compound word'), but it can still carry on and be processed in case it's a location etc, the way I do with null; a thing can be null + something else, then the something else just takes priority. So should do the same with nouns. Because right now, it can't find 'gardening mag' because there's no gardening mag instance, but from 'read mag' we get this

Token(idx=1, text='mag', kind={'noun'}, canonical='gardening mag'), because it's in the item_defs.

So, two issues - one, need to add inventory to local_items (and will need update local_items - I don't think it'll update currently, it's just assigned at init. Hm.)

11.58am
Okay, so now it updates local_nouns each time parser runs, and includes current inventory and locational items.


12.09pm

Okay, so - during tokenisation, we have 'text' as the raw input that was being converted.
But, when it gets into token role options/dict_from_parser, we lose the 'text' field and only have instance and str_name, which is the proper name of the found instance/item_defs entry. So I need to preserve the 'text' field, so we still have the inputted str to print in errors even in the later stage.


12.48pm
That's fixed now.

Next:

Two things show up when I run and rerun the current set of instructions.

1: (it follows through to 'option', when usually, it doesn't. That function is basically unused entirely now. (Need to erase it entirely unless it has some use, but right now it just exists to feed immediately back to run_membrane, BUT only sometimes. ie, the first time I ran these instructions, it didn't hit def option() once. And the second time, only sometimes.))
#   (  Func:  get_item_by_location    )
#   gate is already open.
#
#   (  Func:  option    )
#
#
#
#   USER INPUT FN
#   run tests on
#   (  Func:  loop    )

2:
#   Heavy wrought iron bars with little decoration, now slightly ajar.
#   [[  unlock padlock with iron key  ]]
#
#   Cannot process {0: {'verb': {'instance': <verbInstance unlock (57d37a26-6b72-46e8-99e6-da4e00407af3)>, 'str_name': 'unlock', 'text': 'unlock'}}, 1: {'noun': {'instance': <ItemInstance padlock (77e9ee3e-f19f-4116-8ff9-7ab852150730)>, 'str_name': 'padlock'}}, 2: {'sem': {'instance': None, 'str_name': 'with', 'text': 'with'}}, 3: {'noun': {'instance': <ItemInstance iron key (7fd30db1-fd40-4793-9526-f8845c9cdf57)>, 'str_name': 'iron key'}}} in def lock() End of function, unresolved. (Function not yet written, should use open_close variant instead)
#   [[  look at gate  ]]



For 1:

So we start in option here,
def inner_loop(speed_mode=False):
    logging_fn()

    loc.currentPlace.visited = True
    loc.currentPlace.first_weather = game.weather

    while True:
        test=option()

And it only goes there because test_runme goes through the inner loop, which only exists to set current visited, first_weather and go to option, which feeds immediately to run_membrane, which then loops

loop(input_str)

So I need to figure out where/why it's 'escaping' that loop and going back to 'optin', because it really... shouldn't.

Oh - it's because it finished the loop via test strings, and when it finished the loop was over, so it returned to options and then reentered. Okay. So actually it's good that it feeds through options, though I need to rename it etc to make its function clearer, as it used to be where the input parsing was directed.

So, ignore 1. It's not an error, just an oddly designed leftover that actually serves a useful purpose.

In that case, 2:

It can't unlock the padlock because it's already unlocked and in my pocket (as it was unlocked in the first loop). It should just say that instead of erroring, I need to check why.


Okay. The above is now fixed, and I've fixed the input printing too. print_input_str now works, so instead of automatically changing what you typed from 'look at jar' to 'look at glass jar', it prints:

#   [[  look at jar  ]]
#
#   You look at the glass jar:
#   A glass jar, holding some dried flowers.
#
#   The glass jar contains:
#     dried flowers

So that's better.

Fixed the config file with a couple of other minor things too, basically centralising testing/printing settings there instead of within the scripts themselves. More to do but it's good.

So, nouns/local nouns is fixed. plural_nouns is always made from all nouns, but then I believe nouns are tested against local whether they're compound or not.

Next thing:

Failed parser: 'eventInstance' object has no attribute 'generate_on_start'

Need to re-add that flag, was likely removed in the flag edits I made. Will commit all this first though, these were some solid fixes.

2.52pm
Finally figured out why some of my print lines have a random space at the start of them.

            if print_text:
                print("\n", assign_colour(msg, colour="event_msg"))
^^ leaves a space at the far left.

            if print_text:
                print()
                print(assign_colour(msg, colour="event_msg"))
^^ doesn't leave a space at the far left.

also
            print(f"\n{assign_colour(msg, colour='event_msg')}")
^^ doesn't leave a space at the far left.

3.25 Added some minor function to def burn, and updated the parser a little to allow for 'set x on fire', as well as 'set x down'.

Oh - seeing as membrane now updates local_items every time, I really should reuse that during the item checks, instead of rerunning it over and over. If I save both sets to membrane, then I only ever check against those, not getting those lists over and over from itemReg/inventory for accessibility checks. Yes?

Will look into it later. Braindead today.

4.38pm

[[  take matchbox  ]]

The matchbox is now in your inventory.

[[  look at matchbox  ]]

You look at the matchbox:
NoneNone.

Need to re-implement the default description in the new 'descriptions' setup. (fwiw, the first 'None' is yellow, the second is blue. I imagine the second is the children list, maybe?)

4.42pm
#   [[  look at matchbox  ]]
#
#   You look at the matchbox:
#   NoneNone.
#
#   The matchbox contains:
#     matches
#
#   [[  look at matches  ]]
#
#   You can't see that right now.
#
#   [[  open matchbox  ]]
#
#   You can't open a locked matchbox.

So - need the descriptions for the matchbox, and I'm not sure why they're broken (have added generic desc to the matchbox entry now)
Also, I can't open the matchbox because it's locked (need to change that in the item defs, but useful for the error for now), but I can see the matches inside it. I thought I'd properly updated containers to check item.is_hidden, but maybe I undid that at some point when I changed the setup for checking local_items. Ooooh. Yeah that local_items check doesn't consider hidden items. Though that doesn't explain this, because the matches aren't hidden, they're inside a container. Shouldn't be counted as 'in the local area' if they're inside a container and not mentioned otherwise.

Why is 'description' like this?
 #  'description': 'None\x1b[1;34mNone\x1b[0m.',

Oh, maybe the assign_colour thing is going wrong? Doesn't seem it though. idk. Yeah the moss works properly, and that has the same [[]] formatting, so it's not that.

5.51pm
Okay. So the fix is messy, my brain is everywhere today and I can't think straight but it does work now. But just a note to myself on a better day, make it nicer. Messiness and spaghetti aside, it does work now to:
> Get item defs from alt_names (eg a child named 'matches' will still be called 'matches', but will get the item_def from item 'match')
> properly allocate descriptions (inc using alt names also, and fixed logic issues with the various descriptions options),
> also checks for whether a container is open or not when deciding to print the children.


10.14pm
long_desc with child: ['a glass jar, holding ', '\x1b[31m<ItemInstance dried flowers (dd3545a4-ecf0-4b09-862e-f4912acfb288)>\x1b[0m']
DESCRIPTION: a glass jar, holding <ItemInstance dried flowers (dd3545a4-ecf0-4b09-862e-f4912acfb288)>.
Need to check to see if this error persists. Running itemReg on its own to set up some tests, not sure if this error appers in the main run or if it's because I'm running it in isolation.

10.49pm
Working on the test still.
Found this error:
(  Func:  get_transition_noun    )
noun: <ItemInstance work shed (6545a662-f6d2-4f08-adc1-2622b181e45d)>
format_tuple: ('verb', 'noun')
input_dict: {0: {'verb': {'instance': <verbInstance enter (38279a08-5f12-4e78-ac6f-78afbf4bef04)>, 'str_name': 'enter', 'text': 'enter'}}, 1: {'noun': {'instance': <ItemInstance work shed (6545a662-f6d2-4f08-adc1-2622b181e45d)>, 'str_name': 'work shed', 'text': 'shed'}}}
(  Func:  get_item_by_location    )
loc_cardinal: <cardinalInstance west graveyard (01194da9-48df-4f54-99b0-7ff6f6c94c42)>
(  Func:  turn_around    )
new_cardinal: <cardinalInstance north everything (bed9b124-e226-4eca-83bd-6e8f2277dc25)>
Failed parser: 'NoneType' object has no attribute 'get'


Probably only an issue because I've randomly added a heap of shit in a weird way, but still. Should avoid errors like this even if they shouldn't happen in ideal typical play.

also:

(  Func:  instances_by_name    )
definition_key: old gold key
(  Func:  router    )
viable_format: ('verb', 'noun')
inst_dict: {0: {'verb': {'instance': <verbInstance take (42dc4d6a-e91d-4707-856b-5c2b6540a089)>, 'str_name': 'take', 'text': 'take'}}, 1: {'noun': {'instance': <ItemInstance old gold key (9df38fa3-7830-494d-95de-d60[[  take key  ]]r_name': 'old gold key', 'text': 'key'}}}

instead of the local iron key, it's chosen old gold. Usyally its not been inits at this point but because of the test it has. Need to fix this too.

(  Func:  get_item_by_location    )
loc_cardinal: <cardinalInstance west graveyard (01194da9-48df-4f54-99b0-7ff6f6c94c42)>
(  Func:  turn_around    )
new_cardinal: <cardinalInstance north everything (bed9b124-e226-4eca-83bd-6e8f2277dc25)>
Failed parser: 'NoneType' object has no attribute 'get'

So this is odd.

It describes being in the graveyard (Even though I told it to start in the Everything), gives the description for east graveyard,  goes west in graveyard, opens the door,  but then fails to get the transition noun:

(  Func:  router    )
viable_format: ('verb', 'noun')
inst_dict: {0: {'verb': {'instance': <verbInstance enter (38279a08-5f12-4e78-ac6f-78afbf4bef04)>, 'str_name': 'enter', 'text': 'enter'}}, 1: {'noun': {'instance': <ItemInstance work shed (6545a662-f6d2-4f08-adc1-262[[  enter shed  ]]name': 'work shed', 'text': 'shed'}}}

#   (  Func:  enter    )
#   format_tuple: ('verb', 'noun')
#   input_dict: {0: {'verb': {'instance': <verbInstance enter (38279a08-5f12-4e78-ac6f-78afbf4bef04)>, 'str_name': 'enter', 'text': 'enter'}}, 1: {'noun': {'instance': <ItemInstance work shed (6545a662-f6d2-4f08-adc1-2622b181e45d)>, #  'str_name': 'work shed', 'text': 'shed'}}}
#   (  Func:  get_noun    )
#   input_dict: {0: {'verb': {'instance': <verbInstance enter #    (38279a08-5f12-4e78-ac6f-78afbf4bef04)>, 'str_name': 'enter', 'text': 'enter'}}, 1: {'noun': {'instance': <ItemInstance work shed (6545a662-f6d2-4f08-adc1-2622b181e45d)>, 'str_name': 'work shed', 'text': 'shed'}}}
#   (  Func:  get_transition_noun    )
#   noun: <ItemInstance work shed (6545a662-f6d2-4f08-adc1-2622b181e45d)>
#   format_tuple: ('verb', 'noun')
#   input_dict: {0: {'verb': {'instance': <verbInstance enter (38279a08-5f12-4e78-ac6f-78afbf4bef04)>, 'str_name': 'enter', 'text': 'enter'}}, 1: {'noun': {'instance': <ItemInstance work shed (6545a662-f6d2-4f08-adc1-2622b181e45d)>, #  'str_name': 'work shed', 'text': 'shed'}}}
#   (  Func:  get_item_by_location    )
#   loc_cardinal: <cardinalInstance west graveyard (01194da9-48df-4f54-99b0-7ff6f6c94c42)>
#   (  Func:  turn_around    )
#   new_cardinal: <cardinalInstance north everything (bed9b124-e226-4eca-83bd-6e8f2277dc25)>
#   Failed parser: 'NoneType' object has no attribute 'get'


1.38am

(  Func:  get_item_by_location    )
loc_cardinal: <cardinalInstance west graveyard (83bb516f-caea-4995-8051-e7191f0473e0)>
local items in get_transition_noun: {<ItemInstance work shed (7b3e6098-29b4-4a87-a474-f56577b515ae)>, <ItemInstance wooden door (c72ee11e-4851-4a72-bdc8-4facf172a9c0)>}
has noun.in_loc_ext: True
1 noun.transition_objs
neW_noun: <ItemInstance wooden door (4ff5c570-afe8-4575-9c92-37a2f20b33e8)>
NOUN after get_transition_noun: <ItemInstance wooden door (4ff5c570-afe8-4575-9c92-37a2f20b33e8)>

Not sure if these lines just weren't printing before or if it wasn't happening.

Well no, it definitely wasn't working before, because it said noun None.

1.40am
HAs loc item: <ItemInstance wooden door (c8508711-2ba5-4c9e-a808-d79abb3eb153)>
NOUN after get_transition_noun: None
This None doesn't lead anywhere
Yeah. Sometimes it just doesn't. Hmph.


HAs loc item: <ItemInstance wooden door (6ceaff9a-152a-4dac-b0c1-bd9d74295ea8)>
local_items_list: {<ItemInstance work shed (bba9cc1b-493a-4a2c-b605-10b8c20b6e28)>, <ItemInstance wooden door (12455160-23d5-4bae-91fe-b9b1966d133b)>}

Hmph. It's finding the wrong door, apparently there are  two. That's why it works sometimes.

Well, temporarily for now,
HAs loc item: <ItemInstance wooden door (8400dce4-4116-4067-87eb-83a5049d2cf6)>
local_items_list: {<ItemInstance work shed (17a28e58-556f-443d-bd44-9000756a9f11)>, <ItemInstance wooden door (2f9709db-e182-4b41-8411-b37683a50dbc)>}
NOUN after get_transition_noun: <ItemInstance wooden door (2f9709db-e182-4b41-8411-b37683a50dbc)>

I've just got it to say 'if you have something of the expected name in the current loc, use that instead'. Not a good fix but works for the moment.

2.14am
Running the original test set of 50 instructions reveals a heap of interesting errors.

Not an 'error' but a downside of using the input string instead of the noun name:

[[  investigate exact  ]]
printing when

"investigate the exact thing",

was typed. 'thing' didn't get a token because it was skipped as part of the parser's omit_next. So I guess I do need to pass the typed str itself through, not just reconstruct it from token.text entries.

The rest are generally actual errors.

Hm. Thinking that, seeing as I store the locations on the instances, maybe I should just check that instead of getting local_items if I already have the target instance...

7.39am 10/2/26
Going to just run it over and over until all the errors are cleared.
Had to turn off events otherwise everything breaks as I've moved all items to Everything location.

Puting detailed notes in a separate doc. Will just summarise found issues here.

* Failed parser: 'NoneType' object has no attribute 'add' in move_item, think it's fixed (no 'children' set to add to.)

* place dried flowers on headstone - no real mechanism to place things on things. Need to add a proper error message for the moment, add a 'place on surface' later.

* No item descriptions for north graveyard. Should have the gate and padlock. Possibly just a result of moving all items to Everything North for the test, will check.

* 'too many values* when trying to parse `approach the forked tree branch`.
>   Same for `read the fashion mag in the city hotel room`.

* `read the fashion mag in the city hotel room` counted 'city' and 'hotel' as separate tokens instead of combining the compound_word into one. Check if omit is broken.

* 'What do you want to break the TV set with?' doesn't return, so it prints the end of fn error msg.

* 'break jar' just errors immediately. It should be breakable, maybe I didn't add  the tag.


## random note: Decide if I'm using noun_2, noun2, etc. Just use the same one all the time.

# Other random note: Set all the instance colours once. If I don't need nicename or other formatting, surely I can just have a much smaller, simpler function that just applies the colour from item.colour. Or just use the colour class directly? Not sure, just a note for later.


* clean x now checks for is_dirty and responds appropriately.
* combine x with y has some basic rerouting, will see if it works.
* Fixed `Failed parser: set.pop() takes no arguments (2 given)`, which was a remnant of very old code I'd never used.

* 'a pile of rocks' fails in a unique way, because it omits both non-nouns and keeps the 'of'. Might need a way of tracking 'missing-dir/sem-missing' compounds. Hm. Not today though.
* Added slice_attack/smash_attack, and changed slice_threshold to 'slice_defence', even if I prefer the word 'threshold'. Defence is clearer. Wrote simple 'x breaks y if x thrown at y and y is weaker'.
* Added simple 'set the time on the watch' (though only with 'set the watch'. Seeing as I have a separate verb for 'time', that may cause issues... Nothing is compatible with two verbs yet).
* lock/unlock noun did not return after printing, easy fix.

8.57am

Wrote a placeholder in def move because 'move headstone' errored (previously 'move' only redirected to def go, for 'move to graveyard east' type commands. Now it has a noun section, checks if static and refuses if so, but doesn't do anything else otherwise. Things don't have placement within the local area, so I'm not sure how to deal with 'push'/'move' commands unless something's being covered/uncovered/etc. Need to think on it.)

Added barricade to verb_actions and defs, removed it from 'close' because they're different actions and that's silly. No actual barricading yet, but the fn should work with appropriate prints.

Fixed 'observe graveyard' failing because 'look place' wasn't valid, it expected a cardinal or 'look /at/ place' (or just 'look').

* another failure to get sequence and city + hotel being separate tokens again.
* 'depart' doesn't print anything. It directs to 'go', gets entries, then just stops.

* pure 'go' also failed, need to check in the parser around ln 326, think it's probably there. Have added prints.
* 'go to a pile of rocks' fails weirdly, 'more than one viable sequence' despite only one sequence in sequences.
* realised 'forked tree branch' also uses two tokens instead of compounding correctly, need to check if omit_next is working properly. May have broken it.

9.52

* `put batteries into watch` - need to add 'if noun2 == electronics and noun2.takes_batteries', and noun.is_battery' into 'put x into y'/use_item_with_item/whatever fn. Don't want to make everything that uses batteries into a container, esp as we don't want the batteries appearing to be in the container-watch in that context.


10.00. Okay, have run through the full test list. Not too bad. Failed mostly where I expected. Going to run edit_item_defs again to add the new type_defaults, then run it again to see how many issues persist.

11.09am
Took me a while but fixed the issue of it not finding the compound locations correctly (adding multiple tokens for single locations). I wasn't updating omit_next from second_omit_next if it found second_perfect.

Probably never found it myself because I just type the one word names when I'm typing it for little interstitial tests.

Okay, big test again now.

This one:
#   paperclip is already in your inventory.
Needs working on.
Because whether it takes one from the inventory or local_items (which in the parser includes inventory) depends on the verb.
so I guess def take should check to see if there's another instance of that name in the location, and if so, take that instead. That'll work.

1.21pm 11/2/26

Working agains on that damn paperclip. So it turns out there are three paperclips in existence in this run, one of them in my inventory, the others have no location.

I'm really thinking of adding 'inventory' as a location, except it'll fuck the parser. But like, I know one of these paperclips is in my inventory (and because of previous print lines I know which it is), but there's no indication on the item instance that it's anywhere.

Thought:
A non-place ('no_place') location instance where all new item instances are 'put' during generation before the new location is applied.
An 'inventory_place' location instance that holds the inventory.

Use words like no_place and inventory_place, so they won't accidentally be triggered by the parser, and only used on the back end. And explicitly rule them out as travel locations, so we don't get a 'room of all items' bug or smth. Not that it matters if there was one, would be kinda neat. But anywho.



1.43pm

Okay so I thought I fixed the issue of omit_next, but now:

values: ("top of token_role_options: Token(idx=3, text='glass', kind=('noun',), canonical='glass jar')",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=3, text='glass', kind=('noun',), canonical='glass jar') // kinds: {'noun'}",)
(  Func:  verbReg_Reciever    )
values: ("top of token_role_options: Token(idx=4, text='jar', kind={'noun'}, canonical='glass jar')",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=4, text='jar', kind={'noun'}, canonical='glass jar') // kinds: {'noun'}",)

glass jar now takes two tokens.

So, gets to idx 3, noun:

#   word: glass
#   parts: ['pick', 'up', 'the', 'glass', 'jar']
#   idx: 3
#   word_type: noun

after which:
omit_next:  1
omit_next after first check compound words: 1

but then it checks compound words /again

#   word: glass
#   parts: ['pick', 'up', 'the', 'glass', 'jar']
#   idx: 3
#   kinds: {'noun'}
#   word_type: location
#   omit_next: 1

and then:
#   word: jar
#   parts: ['pick', 'up', 'the', 'glass', 'jar']
#   idx: 4
#   word_type: noun
#   omit_next: 1

omit_next:  1
omit_next after first check compound words: 1

#   word: jar
#   parts: ['pick', 'up', 'the', 'glass', 'jar']
#   idx: 4
#   kinds: {'noun'}
#   word_type: location
#   omit_next: 1

Then it resolves with no sequences, and the tokens

values: ("token_role_options: Token(idx=3, text='glass', kind=('noun',), canonical='glass jar') // kinds: {'noun'}",)
values: ("token_role_options: Token(idx=4, text='jar', kind={'noun'}, canonical='glass jar') // kinds: {'noun'}",)


Think I fixed it now. I had omit_next only operating when it was > 1. I don't know why. probably a reason but I can't think of a good justification now. So for now, have just set it to if >= 1.

2.34pm
Next:
You smash the glass jar on the ground.
long_desc with child: ['a glass jar, holding ', '\x1b[1;31msome dried flowers\x1b[0m']

That's not an error, just a print that I had set up for testing. But, does make me realise - if a container breaks, the contents have to fall out. Only makes sense.


What to do with broken things? Remove the original instance from itemReg and generate a new 'broken x' instead? Or should particular items leave specific parts, eg glass jar becomes 'broken glass shards'.

Maybe it's an event. Specific items (eg those that would leave behind glass) trigger an immediate_event, that removes that item from the registry and adds a new 'broken glass' item in its place. Similarly, things that burn can leave behind burned versions, etc.

Simply something like

  "glass jar": {
    "on_death": "broken glass",

and then set up the event accordingly.


Have done this up for now, will need to edit event_defs around it:

"item_leaves_broken_glass": {
    "is_quick_event": true,
    "repeats": false,
    "starts_current": false,
    "immediate_action": {
        "attribute_trigger": {
            "item_attribute": {"on_death": "broken_glass"},
            "triggered_by": ["item_broken"]
        }
    },
    "effects": {
        "init_items": {
            "0": {"item_name": "broken glass shards"}},
        "remove_items": {
            "0": {"item_name": "trigger_item"}}},

    "messages": {
        "start_msg": "As the [[]] breaks, it shatters into a clutter of glass shards."
    }
  }

Which means I can't test it yet, because events are turned off entirely for the existing testing battery. So, once this is done.

Running the testing battery one last time, anything that doesn't do what it should:

'consume fish food'
#   You decide to consume the fish food.
#   something something consequences
#   Failed parser: 'd05b2f77-d30b-4822-8827-0c67b49ad611'
#   Press any key to continue to next.
At some point it's got an item_id and doesn't know what to do with it.
Fixed. It thought instances were stored as IDs in itemReg.instances, but they aren't.

#   You throw the pretty rock at the window
#   The window hits the window, but doesn't seem to damage it.
Okay that error is pretty obvious...


So I want to rejig the logic a bit for def take.

Right now,
#   remove batteries from TV set
gets me:
#   REASON: 5 / in inventory
#   Sorry, you can't take the batteries right now.
Which isn't an error necessarily, but also isn't the relevant part. Whether I'm already holding batteries or not, the point is first 'are there batteries in the TV and can I have them'. I can't let def take especially think I always mean the thing I'm holding, that's likely not the intended target.

So, if I hit def take with two nouns and the dir_or_sem indicates I'm taking x from y, first I need to check
    a) if y is a container
    b) if y contains the thing I'm looking for

Now the TV is tricky. I had to make it a container because it can take a DVD, but it's not a container in the typical sense. I have
    "children_type_limited": [
      "DVD"
    ],
so maybe if the child/potential_child is not that name, it treats it like it's not a container? So if I'm not a DVD, the TV is not a container in those interactions. Might work but it's still messy. I just use the container because for the parser, we're much more likely to say 'put the DVD into the tv' than 'combine the dvd with the tv'. (Though really we're probably say 'play the dvd on/with the tv')



[[  separate costume jewellery  ]]

get_dir_or_sem failed to find the dir/sem instance: {0: {'verb': {'instance': <verbInstance separate (3835521f-11b3-4477-a355-1c5d5f71e26d)>, 'str_name': 'separate', 'text': 'separate'}}, 1: {'noun': {'instance': <ItemInstance costume jewellery (60c03978-b1be-416d-9938-09dbb74fbe25)>, 'str_name': 'costume jewellery', 'text': 'costume'}}}
inst: <ItemInstance costume jewellery (60c03978-b1be-416d-9938-09dbb74fbe25)> / meaning: accessible
The costume jewellery is now in your inventory.
This shouldn't work, the costume jewellery wasn't part of anything so the instruction makes no sense, it shouldn't just convert into 'take'.


#   [[  leave graveyard  ]]
#
#   You're now in the graveyard, facing north.
#
#   You're in a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
#   The entrance gates are to the north. To the east sit a variety of headstones, to the south stands a mausoleum, and to the west is what looks like a work shed of some kind.
#
#   There's a dark fence blocking the horizon, prominently featuring .

Two issues here - one, I didn't leave the graveyard, I went to it, I was in North Everything. Second, still need to fix the descriptin. I think it's because I moved all the items away, but doesn't the graveyard have no_items? Oh, it's north graveyard, so it has the gate etc whch I never expected to leave. Fair enough.


#   {0: {'verb': {'instance': <verbInstance leave (5db74d47-2aa3-4f61-a36b-8f2d1a2a06ce)>, 'str_name': 'depart', 'text': 'depart'}}}
#   [[  depart  ]]n dict_from_parser, error
#
#   Where do you want to go?
#   Press any key to continue to next.
#
#   Failed parser: list index out of range

Hm.

#   {'verb': {'canonical': 'examine', 'text': 'examine'}}
#   {'noun': {'canonical': 'damp newspaper', 'text': 'damp'}}
#   reformed_dict {0: {'verb': {'canonical': 'examine', 'text': 'examine'}}, 1: {'noun': {'canonical': 'damp newspaper', 'text': 'damp'}}}, sequence ('verb', 'noun')
#   After input_parser
#   {0: {'verb': {'instance': <verbInstance look (f4eae8b0-b19b-4567-b816-d0723e49f78b)>, 'str_name': 'examine', 'text': 'examine'}}, 1: {'noun': {'instance': None, 'str_name': 'damp newspaper', 'text': 'damp'}}}
#   About to return dict_from_parser, error
#   Nothing found here by the name `damp`.

Also hm.
I think this comes into an earlier thing I mentioned, where I want to be able to match all parts of not-found input strings. So I don't want to return the whole 'damp newspaper' from instance name, because what if I only wrote 'key', I don't want it to give me the full name of a non-local key. But If I wrote 'damn newspaper', I don't just want it to give me 'cannot find 'damp'. Hmmmmmm.
Maybe for parser/compound_words I need an extra thing of 'matched words', so it counts 'damp + newspaper' if both are matched, but not 'iron + key' if I only gave 'key'. Need to think on that.

And it's weirdly inconsistent. Because then, next:

{'verb': {'canonical': 'open', 'text': 'open'}}
{'noun': {'canonical': 'glass jar', 'text': 'glass'}}
reformed_dict {0: {'verb': {'canonical': 'open', 'text': 'open'}}, 1: {'noun': {'canonical': 'glass jar', 'text': 'glass'}}}, sequence ('verb', 'noun')
After input_parser
{0: {'verb': {'instance': <verbInstance open (e2180861-ec8c-4bd9-b6cd-2159c394250b)>, 'str_name': 'open', 'text': 'open'}}, 1: {'noun': {'instance': None, 'str_name': 'glass jar', 'text': 'glass'}}}
[[  open glass jar  ]]rom_parser, error

not confirmed inst: <ItemInstance glass jar (8ec72014-93f6-4a6b-b6b8-6304a2d7588d)> / meaning: not at current location}
You can't open something you aren't nearby to...

So the glass jar was selected as the instance, and the error came via verb_actions. But the damp newspaper errored inside of the parser. I'm assuming because the damp newspaper doesn't exist as an instance (I turned the parser test off, so it hasn't moved all the objects to the current loc). But it feels weird that it's not consistent.

Well for the 'cannot find damp', maybe we check - if " " in canonical:/ not_found = list()/parts = canonical.split()/ for part in parts: if part in input_str: not_found.append(part) /
if not_found: / token.text = " ".join(not_found)

Will still have problems but might be better at least.

Hm.

About to return dict_from_parser, error
ERROR: ("No found ItemInstance for {'instance': None, 'str_name': 'damp newspaper', 'text': 'damp'}", (1, 'noun'))
inst_dict[idx][kind]: {'instance': None, 'str_name': 'damp', 'text': 'damp'}

So the error isn't strictly accurate to what's actualyl found. BEcause 'damp newspaper' isn't the str_name anymore...
Ah. I had hard-set str_name to be 'text', in an earlier attempt to not print unknown item names I think. Had forgotten about the existing text field. (Or no, I think the text field wasn't originally included.)

Okay. Seems fixed:

inst_dict[idx][kind]: {'instance': None, 'str_name': 'damp newspaper', 'text': 'damp'}
PARTS: ['damp', 'newspaper']
Nothing found here by the name `damp newspaper`.

If you type 'damp newspaper', even if there's no such item in the location, if it knows that it /could be a noun/, and you typed all the parts, if gives it to you. Will test further.

--------

4.06pm
'go to north graveyard'
After input_parser
{0: {'verb': {'instance': <verbInstance go (8d0b0dc4-0cee-46c5-9270-179ee5526685)>, 'str_name': 'go', 'text': 'go'}}, 1: {'direction': {'instance': None, 'str_name': 'to', 'text': 'to'}}, 2: {'cardinal': {'instance': None, 'str_name': 'north', 'text': 'north'}}, 3: {'location': {'instance': None, 'str_name': 'graveyard', 'text': 'graveyard'}}}
Failed parser: tuple index out of range

gives this error, and really shouldn't.

next error:

[[  go to shrine  ]]04-863c-9af307c45e49)>, 'str_name': 'shrine', 'text': 'shrine'}}}

Failed parser: cannot access local variable 'end_type' where it is not associated with a valu

That should fail because I haven't lifted the travel restriction yet. idk know why it's even looking for end_type.

Oh, it's attempting the held msg:

msg_type: held
event: <eventInstance graveyard_gate_opens (61f1a346-2361-4222-bd2b-2cbbc090874e, event state: 1>
Failed parser: cannot access local variable 'end_type' where it is not associated with a value


Anyway. That's fixed now.

I like my little fix for the 'damp' vs 'damp newspaper' thing. Testing now, and:

PARTS: ['damp', 'newspaper']
Nothing found here by the name `newspaper`.
Because I only typed 'newspaper'.

PARTS: ['damp', 'newspaper']
Nothing found here by the name `damp newspaper`.
because I typed 'damp newspaper'.

PARTS: ['damp', 'newspaper']
Nothing found here by the name `newspaper`.
because I typed 'red newspaper'.

Those are all expected. Good.


Okay.
5.01pm
So, task.

Going to implement inv_place into all the scripts, starting with itemRegistry.
Also - itemReg sometimes uses 'locRegistry', and sometimes uses 'loc', and sometimes uses 'loc' for other things. So I need to change that first.

place = placeinstance
loc = locRegistry imported as loc


6.04pm
Think that's mostly done tbh.

Running into an odd issue while testing though:


open jar in inventory
omit_next:  0
omit_next after first check compound words: 0
#   Failed parser: 0
> interesting failure.

open jar
omit_next:  0
omit_next after first check compound words: 0
{'verb': {'canonical': 'open', 'text': 'open'}}
{'noun': {'canonical': 'glass jar', 'text': 'jar'}}
reformed_dict {0: {'verb': {'canonical': 'open', 'text': 'open'}}, 1: {'noun': {'canonical': 'glass jar', 'text': 'jar'}}}, sequence ('verb', 'noun')
After input_parser
{0: {'verb': {'instance': <verbInstance open (27299f76-f160-43d4-b057-a6d6f3746a48)>, 'str_name': 'open', 'text': 'open'}}, 1: {'noun': {'instance': None, 'str_name': 'glass jar', 'text': 'jar'}}}
About to return dict_from_parser, error
error: None // inst_dict: {0: {'verb': {'instance': <verbInstance open (27299f76-f160-43d4-b057-a6d6f3746a48)>, 'str_name': 'open', 'text': 'open'}}, 1: {'noun': {'instance': <ItemInstance glass jar (81575b44-8e45-4[[  open glass jar  ]]>, 'str_name': 'glass jar', 'text': 'jar'}}}

# You can't open the glass jar
>  this one is accurate.

open jar in graveyard
omit_next:  0
# [ Couldn't find anything to do with the input `open jar in graveyard`, sorry. <after get_sequences_from_tokens>]
After input_parser
None
About to return dict_from_parser, error
error: No dict_from_parser // inst_dict: None
Error: No dict_from_parser

So open jar in graveyard and open jar in inventory both fail in different ways, which is interesting.


Reminder - currently location is added to the sequence but not the dict, so it just fails slightly later. May need to rethink this fix method but it might work.

I nee to be able to reference the inventory, as in 'remove x from inventory'. Currently that just fails, because it only references inventory in the sense of 'type inventory and it shows you the inventory'. But I'm trying to make 'inventory' more... sensible.

Might actually remove 'inventory' from the meta setup and just divert it from location. Might mess with the formatting too much tho. Idk.


Think I fixed the above. Seems to be fixed, will test more tomorrow.

Also, have added a little more depth to the verb_action functions.

Added 'find x'. find() will look for a given noun in the current area and report back if that item is found there. If a location  is given, will look there. 'go' also diverts to 'find'; previously, 'go to noun' only worked if the noun was a transition obj. Now, if you say 'go to gate', it tells you `There's a gate at north graveyard, is that what you were looking for?`, and if  that's where you currently are, describes the gate to you. If it's at another location, it tells you that.

Or at least it should. This is odd:

"find tv set":
#   CANONICAL AFTER PERFECT CHECKS: TV set
#   seq: [] // sequences: [[]]
#   seq: ['verb'] // sequences: [['verb']]
#   seq: ['verb', 'noun'] // sequences: [['verb', 'noun']]
#   VERB FORMATS: [('verb', 'noun'), ('verb', 'noun', 'direction', 'location'), ('verb', 'location')]
#   VERB FORMATS: [('verb', 'noun', 'direction'), ('verb', 'noun', 'sem', 'noun'), ('verb', 'noun')]
#   SEQUENCES: [['verb', 'noun', 'sem'], ['verb', 'noun', 'verb']]
#   VERB FORMATS: [('verb', 'noun'), ('verb', 'noun', 'direction', 'location'), ('verb', 'location')]
#   [ Couldn't find anything to do with the input `find tv set`, sorry. <after get_sequences_from_tokens>]


Oooh. 'find tv set' breaks things because 'set' is also a verb and a semantic, so  it comes out weird.

Also,
find tv set
omit_next:  -1
omit_next after first check compound words: -1
omit_next after second check compound words: -1
how did omit_next get to -1?

Maybe this is why I had to set to only work when it was at least 1. Need to figure out why it does that though.

Tomorrow. Too tired today.

11:04am 12/2/16

Have just changed 'tv set' to be 'TV'. It's a cheap cop-out but I don't have the brain right now.

Not sure why omit_next is like that. Really do need to figure it out.

Okay. So, 'go to work shed' now causes an error, because it /isn't properly skipping/.

it finds 'work shed' as both noun and location, and I set it to pick location when that's the case. But then it comes out with the sequences of

#   SEQUENCES: [['verb', 'direction', 'noun', 'location'], ['verb', 'direction', 'location', 'location']]

neither of which are valid.
It finds the perfect answer with 'work shed'.

The omits look like this:

omit_next:  1
omit_next after first check compound words: 1
omit_next:  2
omit_next after second check compound words: 1
CANONICAL AFTER PERFECT CHECKS: work shed

That '2' is wrong, need to figure out why. And I like that it checks both noun and location, otherwise it never finds perfect locations.

Hm.

Okay so editing the top line and moving the decision to here:
                    if (not canonical and second_canonical) or (perfect and second_perfect):
                        idx = second_idx
                        word = second_word
                        kinds = second_kinds
                        canonical = second_canonical
                        potential_match = second_potential_match
                        omit_next = second_omit_next
                        tokens.append(Token(idx, word, kinds, canonical))
                        continue
makes it work properly.

OH.
It's because the previous one added two tokens, that's why. The original token from `if perfect and second_perfect`, and the second one for if not canonical and second_canonical. By moving the job only into that second function (and making it `if (not canonical and second_canonical) or (perfect and second_perfect):` instead of just the first part), it only makes one token and it just has to pick between location and noun for that one token, so it works.

I wonder if 'tv set' would work again now...

Hmph. Now `go to shed door` doesn't work. I assume it did before.
Yeah I think it did, right?

Though I get the confusion with that one. the obj is 'wooden door', and the obj/location is 'work shed'.

So maybe adding 'noun dir loc noun' isn't too bad, I can just check if noun is in/trans obj for loc within the func. Not sure why I didn't have to before though? Wish my brain wasn't so insanely foggy and I could just... figure it out. Bleh.

I think beforehand I was using 'go to shed' or similar though. Will leave it for now.

changed 'tv set' back to 'tv set' from 'tv'.

CANONICAL AFTER PERFECT CHECKS: TV set
(  Func:  verbReg_Reciever    )
values: ('Tokenise: idx: 2, word: set, omit_next: -1',)

parts: ['find', 'tv', 'set']
idx: 1
word_type: noun
local_named: {'local map', 'iron key', 'puzzle mag', 'severed tentacle', 'paperclip', 'padlock'}
omit_next:  -1
omit_next after first check compound words: -1

Oh, it's not finding the TV because I didn't add the object to the location, I only wrote that it was there. Haven't updated the city loc in /ages/. But that doesn't explain omit_next getting to /minus one/. No reason for that at all, that needs fixing even if this particular error is because I don't have a TV obj for it to find.

So maybe I re-remove the local_named from the parser. I really prefer it not to exclude/include words based on what is around, but when I have things like 'find x' for searching the local area, it makes sense to have it. Because I arrive in the hotel room to the north, there's nothing there, and it fails to parse 'find tv set'.

Maybe it /does/ recognise 'tv set' as a noun, but maybe because it's not local it doesn't consider it perfect? Let me check what actually makes it count for perfection.

Okay so perfect_match only requires both parts of the name are found, so it's not that.

Looking at omit_next:

omit_next at top of compound_words: 0
Word: TV / omit_next before += matches_count: 0
Word: TV / omit_next after [+= matches_count-1]: -1 // matches_count = 0
omit_next after first check compound words: -1

Oh. I think it's because 'TV' is a valid alt_name for 'tv set', so... but shouldn't 'matches_count' be 1?

OK, so I fixed it, ish.
It was erroring in this specific way because I had 'if word == tv, word = TV' at the top. And the compound_word entry is 'tv set', so it never found the compound word, and so matches_count never added anything.

So without that, now it works:
#   omit_next at top of compound_words: 0
#   word tv in word parts: ('tv', 'set')
#   Matching word segment: tv
#   Matching word segment: set
#   Perfect match: tv set, word parts len: 2
#   Word: tv / omit_next before += matches_count: 0
#   Word: tv / omit_next after [+= matches_count-1]: 1 // matches_count = 2
#   omit_next after first check compound words: 1

and it properly works:
#   [[  find tv set  ]]
#   There's a tv set at east city hotel room, is that what you were looking for?

Okay. Now I'm going to get rid of some of the many extraneous print lines that I hopefully don't need anymore.

Also it does properly recognise 'city hotel room', which is a relief.

word city in word parts: ('city', 'hotel', 'room')
Matching word segment: city
Matching word segment: hotel
Matching word segment: room
Perfect match: city hotel room, word parts len: 3

5.03pm
I'm not sure why

There's a tv set at east city hotel room, is that what you were looking for?
[[  look at tv set  ]]

You can't see the tv set right now.

[[  go west  ]]

You turn to face the west city hotel room
There's a standard hotel room door, with the fire escape route poster on the back and an empty coat hook.
[[  open door  ]]

the spacing is off.
Why does 'You can't see the tv set right now' get a newline after it, but the description doesn't.

Also, the test has started repeating infinitely. Not sure why. It just loops forever.
Oh, because I made run_tests import inside the loop, so it's always true or always false. Right.

3.33pm
Okay, new thing.

I cleaned the print lines, and have been trying to get the input_str line alignment right.
In the loop test, it prints correctly;
#   [[  look around  ]]
prints over the top of
#   look around

But then, once the loop is over, it prints like this:

#   look around
#
#   [[  look around  ]]

I know how to fix it, I just need to add the MOVE_UP back to the print line.
But why doesn't the loop print need it??

When running run_test, input str is just

loop(input_str)

Oh, I guess

        while input_str == None or input_str == "":
            input_str = input("\n")

would be part of it, but not the second newline...

Nope. If I remove that newline, it still prints

#   look around
#
#   [[  look around  ]]

I can't see why the loop would remove newlines.

Anyway. Have made some minor edits to compensate, and it works now regardless. Assumedly it was the user input that threw it out of alignment even though I'm not convinced that should add two lines. But I guess the evidence says it does, regardless.

4.19pm
Okay, that's done. And removed those excess print lines, so it's the proper output again now.

So, next: I want to set up the 'broken glass' immediate_event for when glass-type things break.

Need to implement

        "attribute_trigger": {
            "item_attribute": {"on_death": "broken_glass"},

data in event_intake:

#   self.match_trigger_to_attr_only = attr["immediate_action"]["attribute_trigger"].get("item_attribute")

#   if trig == "attribute_trigger":
#       setattr(self, f"start_trigger_is_attr", True)
#       if trigger_type == "immediate_action":
#           #print(f"Immediate action: {trigger_type}")
#           if not self.start_trigger:
#               self.start_trigger = (attr.get("immediate_action"))
#       self.attr_triggers.add(val.get("item_attribute"))

Finding the events triggered by an attr trigger:
use this function:
get_event_by_attr_trigger(self, attr_trigger)

Need to add this to events that use attr_trigger:
                        print(f"VAL: {val}")
                        if val.get("triggered_by"):
                            for item in val["triggered_by"]:
                                self.attr_triggers.add(item)

Hm.

(  Func:  get_current_loc    )


(  Func:  loop    )

get_current_loc adds two lines even if it doesn't do anything. Not ideal.

Okay.
So, glass shard is... working?
Break glass jar, it is removed, and 'broken glass shards' is added in its place.

One issue though:

You're facing east. You see a variety of headstones, most quite worn, and decorated by clumps of moss, a glass shard, and some dried flowers.

[[  pick up glass  ]]

The broken glass shards is now in your inventory.

It has 'a glass shard' in location descrip, and 'broken glass shards' in text desc. It's the issue of plurals, I haven't actually implemented the 'cluster' thing yet so this is expected. But that's something to fix next.

10.11am, 13/2/26
Okay. So I want to try to fix the 'cluster' noun name printing etc. And also set up the plural item pickup.
Notes:
    * Do not apply the cluster name printing in the inventory. In inventory, treat it as multiple single items.

    * In location descriptions, always use the cluster descriptions.
    * in pick up, use the multiple_instances number as availability.
    * in look at, use the cluster descriptions.


Currently:
location description:
    You see a variety of headstones, most quite worn, and decorated by clumps of moss, some dried flowers, and a glass shard.

Description:
   A scattering of broken glass.

Now, 'a glass shard' == nicenames[if_singular]

while 'a scattering of broken glass' == descriptions[if_plural]

So I guess I need to update nicenames, because apparently descriptions is already doing it.

10.26am
Okay, nicenames now update when descriptions update.

Now I just need to deal with the multiple instances on pickup part.
Right now, 'broken glass shards' is just one item.
So... what do I do.
How do I separate them?

Maybe if I try to pick up a cluster, it generates a new one (if I'm not already holding one), and subtracts one from the original cluster, unless the multiple_instances count == 1 in which case it just picks it up and adds it to however many I'm holding.

Now sure how to go about picking up/dropping all at once, maybe I add 'all' as a semantic and deal with it in verb_actions. Will do that later though.

10.42am

Basic intent for when a cluster item is picked up:

 if hasattr(inst, "has_multiple_instances") and inst.has_multiple_instances > 1:
#    generate a new item (new_inst) with multiple_instances = inst.multiple_instances -1
#    reduce inst.multiple_instances by 1
#    add new_inst to old_loc/old_container
#    update descriptions for inst and new_inst.
#    Add both to updated set so that descriptions/nicenames are updated immediately.
so: The original is the thing picked up (important so that the check to make sure it arrived in the inventory still passes). The new one is left behind.

Going to do this in a separate function and just refer clusters there on pickup/drop.
On drop, it's going to behave... differently. If you have a cluster of glass pieces in your inv, and you say 'drop glass', are you intending to drop all or one?

Def going to have to add 'drop all glass' or 'drop single glass' (noone would use that wording though). This is the same isue I have for all plural items though. (I think) currently it just drops one at a time.

"""
NOTE:
(  Func:  move_item    )
inst: <ItemInstance paperclip (af8bf3cf-eae6-4d5c-ade8-1359e9fdb9a9)>
location: <cardinalInstance east graveyard (603e07ab-6784-4e89-bab3-9703aaf1d9de)>
Failed to find the correct function to use for <verbInstance drop (388ff9da-bb2b-457d-abe3-7b39e3642cfc)>: <ItemInstance paperclip (af8bf3cf-eae6-4d5c-ade8-1359e9fdb9a9)>

Currently erroring this in move_item. Not sure why.

Okay, fixed. It's because it was trying to remove it from inv_place.items twice.

And yes, can confirm it drops a single paperclip. Intended behaviour. Just trickier with clusters because they can be intentionally grouped.

Also, the parser can't deal with plurals. If I say 'drop paperclips' it can't do anything because 'paperclips' isn't a noun.

Maybe I can do a plural check after it's checked compounds. If it's not found /anything/ by that point, then we check if endswith("s"), if so we cut off the s and check for item names.
"""

11.22am
My meds still aren't here. Not ideal.

But.
Clusters are set up at the minimum. new instance is generated on pickup, instance counts are correct, but the descriptions aren't updating properly.

multiple_instances count: 1
item location: <cardinalInstance north inventory_place (2c2ba815-07e5-4a3f-95de-7082d670e045)>
the one in the inventory has one, the instance in the graveyard has 2. Correct. And yet:

iron key
padlock
broken glass shards
paperclip x2
local map
mail order catalogue
severed tentacle

Oh. Because inventory uses name, not nicename. So that doesn't update. Hmmmmm.

So how... do I do this.
I guess I can just... rename it when the description updates? Because so many things do search by name. 'glass' or 'broken glass' would find it anyway...

Maybe I do need that 'print_name'. But idk, that feels like it'll jsut cause more problems. It solves: the item name changing. It breaks: if the print_name diverges from the item_name, and you type the item_name perfectly, it might not find it. Not good.

Okay. So - I quite like it saying 'broken glass shard x2' in the inventory.
So perhaps in the inventory, we keep them as individual multiple_instance = 1 items. But when they're dropped, we merge them with any named item at that card_inst. So it's a cluster on the ground, it's 3x glass shards in the inventory. I like that.

Do still need to rename it though.

Or... if the only place that really prints the bare name is inventory, maybe just name it for the single. So the location description etc all finds it as plural.
But then if you type 'glass shards' it wouldn't find it.
Alt_name. That should work. Okay.

Okay, basically works. Had to pull in the generator dict for it to find the item def, but it works. Should probably just bring that generaor.alt_names dict directly in to the original item defs but it works as proof of concept.

Issue with the parser:
#   [[  look at shards of glass  ]]with the input `look at shards of glass`, sorry. ]
#
#   You look at the broken glass shard:

It was partially overwritten but it's the error
print(f"{MOVE_UP}\033[1;31m[ Couldn't find anything to do with the input `{input_str}`, sorry. ]\033[0m")
from ln 405, verbRegistry.

The issue is that it prints if there's no cardinal, but that can happen and still have it find the item from other input_str parts.

If I don't have that print, then I get

#   [[  look at shards  ]]
#
#

with no error message. If I have it printing but it's found somewhere else, then I get that overlap error but a successful outcome.

Added a fn but it doesn't trigger as the error is too early.

Also, the 'inventory' bits I added in the parser don't work as broadly as I need them to:
#   [ Couldn't find anything to do with the input `look at glass in inventory`, sorry. <after get_sequences_from_tokens>]

'look at inventory' works fine, but I want to be able to specify 'look at thing in inventory'.

`look at shard of glass` doesn't work, but `look at shards of glass` does.

Both are given as alt_names, so I'm not sure why only one works:

"broken glass shards", "shards of glass", "shards of glass, "shard", "shards"

Okay:
So, in the parser, 'look at shard of glass' gets

'verb', 'direction', 'noun', 'noun'

but 'look at shards of glass' gets
values: ("sequences after sequencer: [('verb', 'direction', 'noun')]",)

looking at the parser passes, it's because it's looking at the compound_word, and apparently compound_words doesn't include compounded alt_names. So because 'shard' is in the item_name, it gets found even if 'shard of glass'.

So, looking into it:
compound_nouns = membrane.plural_words_dict

which comes from
        self.plural_words_dict = registry.plural_words

lmao wtf is this
    def add_plural_words(self, plural_words_dict):
        self.plural_words = plural_words_dict

So that's everything in item_defs at init.

So I need to update that... But that won't update membrane. Hmph.

Maybe I shouldn't init plural_words in membrane and should just get it directly from itemReg on call.

Okay. so, when I init a new item (possibly only when I have to use the generater def to do it), I check if it's in item_defs, if not, we check for compound word. And we have to include alt_names in compound words, because I don't think I do at all, currently.

Oh shit. Just doing it on the initial intake was all it needed, it was just that I never included alt_names in plural_words.

look at shards/look at shard now both work correctly.

# Slight potential improvement:
Currently, either way it returns 'a scattering of broken glass'. I want to run a check to see if local_items (inc inv) has > 1 broken glass, and if so, use the single/plural depending on whether it's plural or not. So if I say 'look at shard' and I'm holding a singular shard, it should look at that and use the singular desc.
That's gonna be messy but I want it anyway.

Have added
    "single_identifier": "shard"
    "plural_identifier": "shards"

will add them to item_defs for compounds. Then, if noun_entry.text contains plural, noun_inst == singular.

Oh I could probably do that within gen_noun_instances actually. Would be better than doing it in look_at_item.

Added
get_local_items(self, include_inv = False)

So it can optionally get inv items too. Also, added a return for includes_inv, which only returns true if include_inv was true /and/ items were found. So it should be multipurpose. Should save me getting both parts separately all the time.

Also I need to rename 'get_loc_items', because it's an init fn.

1.06pm
Okay. Getting there.

Currently the issue is with the line 'you look at the broken glass shard'. It's just the item name. Maybe I really do need that print_name, but we just make it so that print_name is always either the def key or an alt_name.

The 'you look at' is just taken from
print(f"You look at the {assign_colour(item_inst)}{extra}"), so whatever change I make here really needs to be done in assign_colour.

1.12pm
## this one needs fixing:
currently, 'take moss' picks up the moss, but 'take moss' again /puts down the moss/. This is bad. Need to update 'take' so it can never remove from inv (unless it's like 'take moss from inventory' but you'd never write that.)

Also:
loc_descriptions breaks here.

#   You're facing east. You see a variety of headstones, most quite worn, and not too much else - , a few shards of glass, and some dried flowers.

That comma is bad. Maybe I just need to remove 'and not too much else', otherwise fix it some other way.

Also picking up the moss doesn't trigger multiple_instances, and it should. Need to figure out why not.

Hm. Now it does. No idea why not before. Maybe I hadn't restarted the run?


1.51pm
okay this is good though:

# look at shard
#
# You look at the shard:
#
#   A shard of broken glass.
#
# look at shards
#
# You look at the shards:
#
#   A scattering of broken glass.

2.35pm
okay so the separate/combine clusters works. I'm honestly excited.

Break the glass, it becomes a cluster of glass shards (single item with 3 multiple_instances). Pick up glass, you have 'shard of glass' in inventory, and 'cluster of glass shards' has 2 multiple_instances. Drop the one  you're holding, the inventory one is deleted and you just have the cluster, with 3 multiple_instances again.
But, pick up 2, and you have 'shards of glass x2'.
And the names update properly in line, and if you have a shard in your inventory and a cluster on the ground, 'look at shards' will describe the cluster, not the single shard, and the inverse applies as well.

Really pleased with this. It's so tiny and probably not something anyone will ever notice (if they even play this) but I'm proud tbh.

NOTE: Shouldn't update plural_identifier during the parser, should do it during description update along with the name. Which I think I already do, in which case the parser update is just a dupe and should be removed regardless.

Moving most of the readme text to here, I never update it so it's just taking up space. Wrote a little summary of the project to sit there instead.

"""
NOTES:
- 'locations' only needs to contain basic data for initial setup and (currently disabled) location nesting. All detailed location data, descriptions etc is handled in 'env_data', along with weather and whatnot. Potentially it'd be better to do away with 'locations' entirely and do it all within env_data, but for now that's how it is.

'choose_a_path' is the script that actually runs the 'game'. This isn't clear at all, I realise now.


THOUGHTS:

I'm not sure if 'choices' and 'env_data' should merge. Is it better to keep minimal external files, or to keep clarity between their function? At this scale I'm sure it doesn't matter, but I'm not sure what the answer actually is.

Need to so some actual story planning. So far it's just been vague outlines of locations, with no through-roads between.
Will draw out some plot ideas and how the locations contribute.
Theoretically I'd like 3 layered plots, independent but interlinked (at least thematically). Had the idea of basically colour-coding the clues; everything for plot A is somehow blue, everything for plot b is somehow green, etc. Not sure how to work it in but it'd be a way to differentiate between the clues, but with the colour-coding itself needing to be recognised as significant. Will think on it.

----------
Well it's 21/1/26, and while I've worked on this a lot, I've not updated this at all.
The game is now instance-based, and while I'm reworking how the locations + items work again at present, it's coming along well. Currently there's still no game, but once the established (basic) mechanics are sturdy, then I'll start working on that.

---

3/2/26
Wow I've been terrible at updating this readme.

Currently working on:
    * Reworking item_defs and loc_data so they can both serve their roles better, currently there's bits of data coming from random places and it needs to be better defined.

Planned things:
    * mini events, things that start, do a task and then end in the same turn. Current function won't allow for that, so just need to write an additional route for one-turn events. (There aren't really "turns", but it makes sense thematically.)
    * randomised item placement for generic required items (minor locked item requires a key, key is placed in one of a selection of items and/or places when the locked item is init'), could be useful.
    * moving a bunch of files. Need to put all my definitions files in one place, and move a bunch of old ones to archives or bin them.

13/2/26
    * Mini events implemented (`immediate_events`).

"""

3.17pm
Hm.

[[  read map  ]]

You can't see a map to read.

[[  look at map  ]]

You look at the local map:

=======
Also, it's not properly fixing the description, at some point I broke it slightly:
 A yellowed [[]] showing the region surrounding the graveyard.

So this is where the [[]] is coming from:
print(f"\n   {assign_colour(registry.describe(item_inst, caps=True), colour="description")}")

4.15pm
description fixed.

4.21pm fixed 'read map' not working. Had a logic error.

So, next:
I want to set up the timed events. For that I need to set up the passage of time again, which has been completely removed I think.

I thought I had a 'world state' class or smth but I can't see it. Maybe it was removed.

Might rename set_up_game and the game class to be worldstate.

Or maybe not. Maybe it's better to have it just be the startup.

I'm not sure. I mean it doesn't do much.

4.55
So this is... odd.

[[  take glass  ]]

The broken glass shard is now in your inventory.

[[  take glass  ]]

The broken glass shard is now in your inventory.

[[  take moss  ]]

The moss is now in your inventory.
Event must have condition maintained until completion of 3 days.
Add something to set_up_game to manage 'when day changes, add to duration'.
I feel like the duration should be tracked on the event, not the trigger, though.
You pick up the moss, and feel it squish a little between your fingers.

[[  take moss  ]]

The moss is now in your inventory.
You put down the still-damp moss.

I'm still holding moss x2. I didn't put it down.

Okay, so with logging on - Oooh. It's the cluster. The specific moss that was the event trigger left my inventory because it joined the cluster? But it doesn't cluster in the inventory...

[imagine lots of logs here]

Oooooh. The event is being triggered by the one we try to pick up, so /it/ isn't in the inventory.

'is_event_trigger' is using
noun_inst: <ItemInstance moss (b9163d57-49c8-45eb-b7f4-9ef7e1333420)>
which is the original, but should use

inst: <ItemInstance moss (5e712f4e-7dfb-4dc3-aba2-33d69725bb1e)>
which is the produced individual instance in the inventory.

Also, verb_actions is still using game.inventory everywhere. Need to fix that.


#   [[  take moss  ]]
#
#   The moss is now in your inventory.
#   Event must have condition maintained until completion of 3 days.
#   Add something to set_up_game to manage 'when day changes, add to duration'.
#   I feel like the duration should be tracked on the event, not the trigger, though.
#   You pick up the moss, and feel it squish a little between your fingers.
#
#   [[  take moss  ]]
#
#   The moss is now in your inventory.
#   You put down the still-damp moss.
#
#   [[  take moss  ]]
#
#   The moss is now in your inventory.
#   Event must have condition maintained until completion of 3 days.
#   Add something to set_up_game to manage 'when day changes, add to duration'.
#   I feel like the duration should be tracked on the event, not the trigger, though.
#   You pick up the moss, and feel it squish a little between your fingers.


Why every other time. What on earth...

Ugh. So I don't know why it's every other time yet (I assume having one already in the inventory changes things, but why not the second time?), will keep looking, but another note:

[[  drop moss  ]]

You can't drop the moss; you aren't holding it.

inventory

severed tentacle
moss x2
fashion mag
paperclip


So - 'drop' needs to check inventory first and choose from those named items.

'take' needs to look only at items not in inventory.

Take moss:


[[  take moss  ]]

CAN_TAKE: <ItemInstance moss (84fbba5f-4b48-4175-b86c-ba5c9374df35)> / meaning: accessible / reason_val: 0
The moss is now in your inventory.
ITEM: <ItemInstance moss (84fbba5f-4b48-4175-b86c-ba5c9374df35)>

You pick up the moss, and feel it squish a little between your fingers.

[[  take moss  ]]

CAN_TAKE: <ItemInstance moss (84fbba5f-4b48-4175-b86c-ba5c9374df35)> / meaning: in inventory / reason_val: 5
LOCAL ITEM NAMES: {'moss': <ItemInstance moss (df9abb25-96d7-4967-a83f-dfdc71080b76)>, 'glass jar': <ItemInstance glass jar (8ead9c76-609b-44e0-aacf-34e43a9fa1ed)>, 'desiccated skeleton': <ItemInstance desiccated skeleton (7264c008-5f20-4339-8bc0-2bdb96a90b5b)>}
CAN_TAKE: <ItemInstance moss (df9abb25-96d7-4967-a83f-dfdc71080b76)> / meaning: accessible / reason_val: 0
The moss is now in your inventory.
ITEM: <ItemInstance moss (84fbba5f-4b48-4175-b86c-ba5c9374df35)>
You put down the still-damp moss.

[[  take moss  ]]

CAN_TAKE: <ItemInstance moss (af2c6c90-c04a-4889-b011-abe3af03455e)> / meaning: accessible / reason_val: 0
The moss is now in your inventory.
ITEM: <ItemInstance moss (af2c6c90-c04a-4889-b011-abe3af03455e)>
Event must have condition maintained until completion of 3 days.
Add something to set_up_game to manage 'when day changes, add to duration'.
I feel like the duration should be tracked on the event, not the trigger, though.
You pick up the moss, and feel it squish a little between your fingers.

Current plan:
Smuggle the new single instance/local noun_inst through 'added to inv', then run the trigger check on that. Because it's /finding/ the new single instance, but still running the trigger check on the original noun.

Not sure why it's doing something different on the third one. I'm not sure where af2c6c90-c04a-4889-b011-abe3af03455e is even coming from.

5.38pm
Okay, that seems to work.
Now moss x3 in inventory, all with the /start/ of the event, not intermittent. No event ending.

5.54pm but ending the events is still wrong.
Hm.

So,
[[  drop moss  ]]

Dropped the moss onto the ground here at the eastern graveyard
DROPPED INST: <ItemInstance moss (6e5ccc5a-4ddd-478a-9f8d-05bf3e70b0bc)>
Noun has event; <ItemInstance moss (6e5ccc5a-4ddd-478a-9f8d-05bf3e70b0bc)> / <eventInstance moss_dries (7fae74f1-30d7-4e97-ae77-00abe5b579fd, event state: 1>

Dropping does trigger that it's an event. But it's not actually ending here.

But if I take the moss again,

[[  take moss  ]]

CAN_TAKE: <ItemInstance moss (fb8695ec-8567-410d-ac16-862b0461e7d6)> / meaning: accessible / reason_val: 0
You put down the still-damp moss.

Okay, so - when I take that last bit of moss, that's the 'cluster' that it found initially.  So it fails because it realises that moss (the cluster) is not in inv.

Weirdly, if I then drop the moss again,

[[  drop moss  ]]

Dropped the moss onto the ground here at the eastern graveyard
DROPPED INST: <ItemInstance moss (fb8695ec-8567-410d-ac16-862b0461e7d6)>
Noun has event; <ItemInstance moss (fb8695ec-8567-410d-ac16-862b0461e7d6)> / <eventInstance moss_dries (e7c70554-ddfc-43d0-9749-e4a94e3013a9, event state: 2>
Failed to find the correct function to use for <verbInstance drop (f5c59d58-2e73-4ae0-8d61-81a9cf964d21)>: cannot access local variable 'event' where it is not associated with a value

So...
Tracking the moss to see exactly where I need to switch them out.

The original moss clump(s):

<ItemInstance moss (6942db98-4250-4fe3-8f0f-afb9afaea023)>

We find we can take it:
CAN_TAKE: <ItemInstance moss (6942db98-4250-4fe3-8f0f-afb9afaea023)> / meaning: accessible / reason_val: 0

realise it's a cluster:
(  Func:  separate_cluster    )
inst: <ItemInstance moss (6942db98-4250-4fe3-8f0f-afb9afaea023)>

But then it's the original that gets sent through to check event triggers
(  Func:  is_event_trigger    )
noun_inst: <ItemInstance moss (6942db98-4250-4fe3-8f0f-afb9afaea023)>

6.23pm

Hm.

Done (new cluster): <ItemInstance moss (0f735c90-f7ea-47a3-a881-a8fd29370699)>
DONE: <ItemInstance moss (0f735c90-f7ea-47a3-a881-a8fd29370699)>
Picked up <ItemInstance moss (0f735c90-f7ea-47a3-a881-a8fd29370699)> instead of <ItemInstance moss (082c9a2a-e62a-4373-a28b-3541bed618f9)>.
Outcome: <ItemInstance moss (0f735c90-f7ea-47a3-a881-a8fd29370699)>, noun_inst: <ItemInstance moss (082c9a2a-e62a-4373-a28b-3541bed618f9)>
noun_inst is in inventory.

So, it makes the new instance. Recognises it as separate. But apparently the outcome is /not/ the one in the inventory.

It's breaking somewher in pick_up.

Though honestly why do I need pick_up at all? Why not just

self.move_item(inst, location = loc.inv_place)?

6.53pm
okay. Removed pick_up, just using move directly.

Some improvement - drop now drops reliably, although I have this issue:

#   You're facing east. You see a variety of headstones, most quite worn, and decorated by clumps of moss, decorated by clumps of moss, and a glass jar being used as a vase in front of one of the headstones, with some dried flowers left long ago.

So it's not combining properly.

7.02
because:
list(self.get_local_items(by_name=inst.name))[0]: <ItemInstance glass jar (43e33721-b1a1-4c3f-b490-f977ca4c6aed)>

it's only finding the glass jar, and not the two mosses still present. So they're not being properly added to the location.

Now it's getting all recursive. Bleh.

Need to... make sure it's settting location properly. At some point I think I've twisted things so it's thinking one is the singular when it's actually the compound.

So to remind myself:

separate_cluster(self, inst:ItemInstance, origin, origin_type:str)

==

inst.has_multiple_instances = 1
new_inst.has_multiple_instances = starting_instance_count - 1

the output of separate_cluster /is the singleton/, not the cluster. The input is the cluster.


8.11, 14/2/26

Working on the multiple_instances again.

Currently it errors here:

local items: {<ItemInstance moss (464b466e-db32-4023-ae88-80679778d7b0) north inventory_place // 1>, <ItemInstance moss (d1446f4a-b110-4aaa-aac7-c5a2d02b1e03) east graveyard // 1>}
Combined inst: <ItemInstance moss (464b466e-db32-4023-ae88-80679778d7b0) north inventory_place // 2>, location: <cardinalInstance north inventory_place (3dff0621-bd4d-4cf7-9eb0-e68871618ad1)>
Original inst: <ItemInstance moss (e59a3192-3727-4d4c-b5a2-3afd8db81f5a) east graveyard // 0>, location: <cardinalInstance east graveyard (32650f16-d179-4a9a-9575-f7bec9431393)>
This instance [<ItemInstance moss (e59a3192-3727-4d4c-b5a2-3afd8db81f5a) east graveyard // 0>] has no multiples left; deleting.
DONE: <ItemInstance moss (464b466e-db32-4023-ae88-80679778d7b0) north inventory_place // 2>
DROPPED(really): <ItemInstance moss (e59a3192-3727-4d4c-b5a2-3afd8db81f5a) east graveyard // 0>

Cannot process {0: {'verb': {'instance': <verbInstance drop (50064d1d-ce5f-4953-8e20-49740267e943)>, 'str_name': 'drop', 'text': 'drop'}}, 1: {'noun': {'instance': <ItemInstance moss (464b466e-db32-4023-ae88-80679778d7b0) north inventory_place // 2>, 'str_name': 'moss', 'text': 'moss'}}} in def drop() End of function, unresolved.

### summary:
There should be a total of 3 multiple_instances in local_items if including inventory. One's gone missing at some point I guess. Will look into it today, was too braindead to look into it yesterday.

8.38am
okay so:

I go east, I pick up two pieces of moss.

inventory:
paperclip
moss x2
gardening mag

great.

look around:

You're facing east. You see a variety of headstones, most quite worn, and decorated by clumps of moss, decorated by clumps of moss, decorated by clumps of moss, and a glass jar being used as a vase in front of one of the headstones, with some dried flowers left long ago.

so I'm guessing it's adding the picked up inst to the loc. Will find that portion.

[[  take moss  ]]emInstance moss (34365ba3-e992-486e-a4e8-0e9b1c619c18) east graveyard // 3>}

CAN_TAKE: <ItemInstance moss (34365ba3-e992-486e-a4e8-0e9b1c619c18) east graveyard // 3> / meaning: accessible / reason_val: 0
is cluster and location is not none.
there are local items with this name: {<ItemInstance desiccated skeleton (5b1fe450-8150-4dd7-9e63-aaba2ff43c5e) east graveyard // >, <ItemInstance glass jar (27fdcead-7c14-449e-bae4-493c738f9061) east graveyard // >}.
New inst <ItemInstance moss (913c9a51-cd4d-4815-a8d9-40dd13076361) east graveyard // 3> generated from cluster <ItemInstance moss (34365ba3-e992-486e-a4e8-0e9b1c619c18) north inventory_place // 3>
Done (new cluster): <ItemInstance moss (913c9a51-cd4d-4815-a8d9-40dd13076361) east graveyard // 1>
DONE: <ItemInstance moss (913c9a51-cd4d-4815-a8d9-40dd13076361) east graveyard // 1>
Outcome: <ItemInstance moss (913c9a51-cd4d-4815-a8d9-40dd13076361) east graveyard // 1>, noun_inst: <ItemInstance moss (34365ba3-e992-486e-a4e8-0e9b1c619c18) north inventory_place // 2>

Yeah they're being switched. north inventory_place instances should only ever be singular.

9.11am
okay, straight errors are fixed but still,

You're facing east. You see a variety of headstones, most quite worn, and decorated by clumps of moss, decorated by clumps of moss, decorated by clumps of moss, and a glass jar being used as a vase in front of one of the headstones, with some dried flowers left long ago.

fashion mag
paperclip
severed tentacle
moss x2

Okay so that's fixed, but now when I drop them they don't remove from the inventory. Well, the first does, but not later ones.

First one goes through the whole local items/combine cluster.

But the later ones:

[[  drop moss  ]]emInstance moss (c3364b3d-a13b-434d-9d13-7087529aa15e) east graveyard // 1>, <ItemInstance moss (410817c9-1390-4080-b12d-1e9d980ec5a7) north no_place // 1>}

reason val: 5, meaning: in inventory, for item: <ItemInstance moss (c3364b3d-a13b-434d-9d13-7087529aa15e) east graveyard // 1>
is cluster and location is not none.
Item <ItemInstance moss (c3364b3d-a13b-434d-9d13-7087529aa15e) east graveyard // 1> is cluster.
ORIGIN: <cardinalInstance east graveyard (88bd1817-de56-40d6-b2e9-f6e114c7717b)>
DONE: <ItemInstance moss (c3364b3d-a13b-434d-9d13-7087529aa15e) east graveyard // 1>
DROPPED(really): <ItemInstance moss (c3364b3d-a13b-434d-9d13-7087529aa15e) east graveyard // 1>
Dropped the moss onto the ground here at the eastern graveyard
DROPPED INST: <ItemInstance moss (c3364b3d-a13b-434d-9d13-7087529aa15e) east graveyard // 1>

So drop moss is trying to /separate/ a cluster...?
I guess that means it failed to combine earlier, because it means Done failed. Which tracks.

Okay so

                if self.get_local_items(by_name=inst.name):
                    print(f"there are local items with this name: {self.get_local_items(by_name=inst.name)}.")
this is failing.

Yeah it's trying to generate a cluster from the shard in the inventory instead of just putting it down.

Okay. So - I need to keep a separate 'drop' function so these two don't get tangled, at least for now. It wouldn't be an issue if it wasn't failing earlier but it's just a pain.

12.33pm
Gradually working through it.
Improving; now removes the compound inst once it's exhausted.

Correction to make:
reason val: 5, meaning: in inventory, for item: <ItemInstance moss (8d4b6be2-5c79-44c3-b44f-908158a98307) east graveyard // 1>

<ItemInstance moss (8d4b6be2-5c79-44c3-b44f-908158a98307) east graveyard // 1> is not in inv_place. This is bad, how are we combining if not removing from inventory?

It found the item in the inventory, but it's not in inv_place. Given it's a moss clump that was created by separate_cluster, that means it's not properly adding to inv_place.

Oh - it's because I had shard.location added as loc.no_place, but it should just go to loc.inv_place. Fixed now.

12.39pm

Okay, so

BY_ALT_NAME[NAME]:
[<ItemInstance moss (d2d7a248-c562-4c22-965a-bb7b75b80313) north no_place // 0>, <ItemInstance moss (ec5bf7a4-7aaa-4f0e-b921-eb315e4014c1) east graveyard // 3>, <ItemInstance moss (95bd70ea-bdf5-459b-9966-6858cc50d867) north no_place // 0>]

Two of the moss instances still exist, though nowhere.

0313 was the last instance I droppped, and d867 was the second to last.
So it's not properly removing the shards after they're combined into the cluster. Doesn't really matter but it's bad practice to just have them hanging around so will fix it now.

Okay, better -

IMMEDIATE COMMAND: print named items
Entry name here:  moss
BY_ALT_NAME[NAME]:
[<ItemInstance moss (f3a4c54d-a383-4dd4-acda-fb9d98f8753a) east graveyard // 3>]

Now, if there's a shard and compound_inst after combine_cluster and both are the appropriate type, it delete the shard.

So the main thing now is to set it up again so it works with the events.

12.51pm
Hmmmmm. This is interesting...


event.state and event_by_state give different results:
event_by_state(1):
[<eventInstance reveal_iron_key (5bd8a8e3-199f-4d2c-89a5-9ca310bbb4a3, event state: 2>, <eventInstance graveyard_gate_opens (809caf12-5638-4b04-82e6-e9b8a3f808b9, event state: 1>]

event.state == 1:
[<eventInstance graveyard_gate_opens (809caf12-5638-4b04-82e6-e9b8a3f808b9, event state: 1>]

Reveal_iron_key shouldn't be there. Or possibly should have its state set to one but hasn't.

Well both events are "starts_current":true, so both should be 1.

Oh, I think I'd added a subclause in add_event that broke things.
Instead of 'if starts_current, ... else: event.state=2'
it was 'if starts_current, ... if unrelated: ... else: event.state=2

Doesn't really explain why event_by_state is correct, but hopefulyl it's fixed now anyway.

Yes, both are now correctly current.
Good.

Wrote myself def immediate_commands(input_str): for specific tests. Instead of the broad logging args (which has great usefulness to be fair), print local items/print inventory items/print named items/print current events lets me get specific details when I need them. handy lil thing. Doesn't go through the parser at all which is just nice. Really should move 'meta' etc to here too really, deal with that outside of the parser. Well no, because then 'look at inventory' wouldn't work. Eh. Anyway.

Okay, so where was I.
Right. Ending the events correctly.

Now the compound instances are working far better than they were, time to realign verb_actions.
 Well def take is fine. It's def drop that needs the update.

Oh, nice surprise. The shards do all have the event properly assigned.
(This example is moss, not glass shards, but 'cluster' and 'shard' is just pleasant.)

The moss event now properly ends when you drop the moss.

Setting it up now to delete the event + its assignments if it's failed. May do it for all generated events perhaps, but for now I'm keeping it as non-standard and just using the "remove_event_on_failure" flag added to event_defs.

Okay, done I believe. Events with the appropriate flag are now removed from events, their items removed from event.items and triggers from event.triggers. I'm not sure if those last two are entirely pointless or not, will look it up later. (~ln 1030 eventReg.) But it does mean that once you've dropped the moss, it's entirely gone, not just 'completed'. For many quests this is not the desired outcome, but for disposable quests like this is it.
I may at some point change the moss quest so it tracks individual mosses through pick_up/put_down, but not sure.

Oh. I should really amend it to 'if put down outside'. So you can put it down inside and the counter continues.....

So if not_in_inv and loc.current == is_inside=False. That's good.

Oh right. I was going to add the time back in.

1.55pm
... Just realised I was running move_item on noun, not noun_inst. Shouldn't change anything because it was getting noun from the parent fn but goddamn.

Have added
    "inside": false,
    "electricity": false,
    "nature": true
to the locations.

2.19pm
that works now. If you drop the moss in the shed, the event doesn't end.
Notes:
currently the prints are different; if the event ended, it has the end_event line, otherwise it has the 'you drop the {item} at {placename}'. Really if it's the event drop it should play that instead of the drop printline.
Also maybe an 'if exception' print, which in this case would be the same as the failure end; 'you drop the still-damp moss'.

Also:
It's still printing a few moss clumps if you drop the moss at the shed, even if there's only one multiple_instances count.

 <ItemInstance moss / (95015684-05df-4ab4-8bf4-d828350f2057)

Start of is_event_trigger:
 <ItemInstance moss / (fb087d3d-21c1-4a19-bfa6-4934093edc51) / north inventory_place / None/ 1> <cardinalInstance north work shed (c355b91b-8c52-4f8e-8ffb-f04ab3efe76e)> item_in_inv
Trigger exceptions:
Ooooh.
Right.
So, even though there was no cluster to combine it with, it still deleted the 'cluster' and generated a new instance. That's just unnecessary.
So, #TODO, if no existing cluster, just change the attrs on the existing one, don't do the whole init session.
It works out okay, because the new instance (dc51) is still connected to the event (e1c5).
I wonder if I drop it outside will it break though, because it's not the item in event.items...
Testing.

Oh dammit.

LOC INST: None, type: <class 'NoneType'>
Failed to get placeInstance for shed door. Please investigate. Exiting from env_data.

'leave shed' failed. Bleeeeh.
Okay will check that first, that's a worse failure.

Ah,
leave shed
loc name: shed door
That'd be why.

So 'enter shed' checks for the transition_obj properly, 'leave shed' doesn't. Noted, will fix.


enter shed:

input_dict: {0: {'verb': {'instance': <verbInstance enter (0f004c05-7f22-45e8-a7a3-5dbe6d5d44c6)>, 'str_name': 'enter', 'text': 'enter'}}, 1: {'location': {'instance': <placeInstance work shed (c23f1151-5c50-465d-a694-10ac44ee063b)>, 'str_name': 'work shed', 'text': 'shed'}}}
values: ("Tokens after tokenise: [Token(idx=0, text='enter', kind={'verb'}, canonical='enter'), Token(idx=1, text='shed', kind={'noun', 'location'}, canonical='work shed')]",)
(  Func:  verbReg_Reciever    )
values: ("tokens before sequencer: [Token(idx=0, text='enter', kind={'verb'}, canonical='enter'), Token(idx=1, text='shed', kind={'noun', 'location'}, canonical='work shed')]",)

leave shed:



values: ("sequences after sequencer: [('verb', 'location')]",)
values: ("token_role_options: Token(idx=1, text='shed', kind={'noun', 'location'}, canonical='shed door') // kinds: {'noun', 'location'}",)


I updated the verb defs but that wasn't the issue.

From inside, it always finds shed door as canonical. But because it has both  noun and location, if it takes the location kind (which I told it to do by default if it's ever unclear), it ends up looking for the location 'shed door'.
Maybe we check if canonical if first or second canonical when we set that arbitrary kind.

Well adding 'verb noun' to 'leave' defs actually made it worse:

[[  leave shed  ]]

verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry:  {'instance': <verbInstance leave (16d004a5-2763-4344-a68b-bb2f3fa7159d)>, 'str_name': 'leave', 'text': 'leave'} {'instance': <ItemInstance wooden door / (c6e46dd3-bd81-4849-b3df-e4e24c4de3d7) / west graveyard / None/ >, 'str_name': 'shed door', 'text': 'shed'} None None None None


And nothing after that.

Okay, fixed. Moved the move through transition obj part to a separate function and added it to the top of go, now you enter/leave the exact same way and it seems to work well. Previously I had 'go /to/ shed' working, but not 'leave shed', so just an oversight.

Okay:
You're facing north. The work shed is simple structure, with a dusty window in one wall over a cluttered desk. On the desk, there's a yellowed local map showing the region surrounding the graveyard, a clump of moss, and a pair of secateurs.
Singular description works now. Goodgood.  I just wasn't updating it because it was routed back to the regular move_items and wasn't added to updated set().

3.16

Ehhh. Got the instance colours working with the event msg prints. Now it sends the noun inst through to the print command, and assign_colour applies the specific noun, not just the noun_name it finds first from registry. Previously it only worked if the noun inst was 'item', it couldn't have other str. Now, it applies the noun into the str. (In this case, 'you drop the [[moss]]' finds it by the `[[`.) Really pleased with that.

So yes. Now the event tracking will track an individual piece of moss, not end the event unless the moss is put down outside (later can add weather to that if I feel like it, the system exists it's just not plugged in/updated to all the changes, like time passage), and even use the correct instance's colour in the event print lines. I'm pleased with that. Did some good work today.

We'll see in a couple of hours how much I broke and haven't noticed yet, but it feels pretty solid.

Oh, and moved the drop print line so it only prints if the event didn't succeed, which works for now. Can output a specific 'print verb text' if I need to but this works for now.

Note:
'take x' should print... it's not.

Fixed.

Next:

You're facing east. You see a variety of headstones, most quite worn, and decorated by clumps of moss, a few shards of glass, and some dried flowers.

[[  take glass  ]]

The broken glass shard is now in your inventory.

[[  look around  ]]


You're in a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east sit a variety of headstones, to the south stands a mausoleum, and to the west is what looks like a work shed of some kind.

You're facing east. You see a variety of headstones, most quite worn, and decorated by clumps of moss, and some dried flowers.

Now in this last description before all the shards are picked up, it should be singular in the loc description, but it's not. Need to make an adjustment.
Oh, currently if multiple_instances == 0 we delete it, but should be if == 1 we update description. Thought we did, but I guess that's the item desc, not the loc desc.

Fixed now.

2.44pm 15/2/26

Want to remove 'is_burned': False from flammable objects. When an object is burned, it should have an event that replaces it.
Well, maybe use is_burned as an item name, instead of a bool? Or no. Not sure.
Options:
    * provide is_burned name
    * provide (becomes_burned_item, and then it autogenerates "burned {itemname}" item) or ("becomes_ashpile", and if the item is burned it generates item 'ash pile'.)
        > If the former, maybe 'burned_item' becomes_ashpile if it is burned again?

 I like the latter. Can always add a specific name if needed, but I think this works. The item can specify a burned name if needed, otherwise the 'flammable' event will apply (burned + {item.name}).

I need to specify the event-type which is just 'something happened to the item, so this happened'. event type 'item_state_change'? Because right now it's all higgledy.

Also I don't think I use

is_quick_event
anywhere, will just remove that field entirely.

Also, 'is generated event' will always be starts_current = false. They're generated by a trigger. So will just set it up to apply that internally so I don't have to write it every time.

Also, I should just have a setup where I can add an event and have it give me the clean template. I kinda did that for locations + locations but it was messy and I never used it. Maybe I should set up the editor tools properly, though that feels like a significant undertaking. Probably worth it though.


3.41pm

Hm.
Cannot process {0: {'verb': {'instance': <verbInstance use (1ed34125-688f-4370-8e65-853d90d72b0b)>, 'str_name': 'use', 'text': 'use'}}, 1: {'noun': {'instance': <ItemInstance iron key / (7db8c5b8-08f2-4ad9-8824-351df2439731) / north inventory_place / <eventInstance reveal_iron_key (c477ebdc-4b5f-4560-a175-cc54b023efa9, event state: 2>/ >, 'str_name': 'iron key', 'text': 'key'}}, 2: {'noun': {'instance': <ItemInstance padlock / (64ad87b8-3263-4921-aa07-07bc6003ea14) / north graveyard / <eventInstance graveyard_gate_opens (fa161918-3798-4b4a-b02e-141ac4b0fa2e, event state: 1>/ >, 'str_name': 'padlock', 'text': 'padlock'}}} in def use_item() End of function, unresolved. (Function not yet written)

'use key on padlock' gave this error.

Oh. 'use key on padlock' errored because 'on' isn't counted as a... well in this context it's sem. is verb_noun_sem_noun valid for 'use'? Yes.

Fixing that, have realised this:

[[  take key  ]]

Sorry, you can't take the iron key right now.

it /names the iron key/ while still hidden. Parser isn't accounting for hidden.
(I really need a better todo board. I make so many notes and never see them again. Maybe I should actually use the git issues tab... Have set it up as an issue, will see if I remember it exists later.)

OH - it's skipping 'on' not because of a dir/sem issue, but because of omit_next.

word: key
parts: ['use', 'key', 'on', 'padlock']
idx: 1
kinds: {'noun'}
word_type: location
omit_next: 1
local_named: {'local map', 'iron key', 'paperclip', 'padlock', 'fashion mag', 'gate'}
(  Func:  verbReg_Reciever    )
values: ('Tokenise: idx: 2, word: on, omit_next: 1',)

So because 'key' is len2, it's omitting next, even though we found word2, not word1. Okay, I need to fix that.

Okay. So let's work through this.

We have matches_count set to 0 at the start of each compound word.
It does

for i, bit in enumerate(word_parts):
    if len(parts) > idx + matches_count and bit == parts[idx+matches_count]:
        #if bit == parts[idx+matches_count]: # gives list out of range errors but does give the right results. Fix this later.
        #print(f"Matching word segment: {bit}")
        matches_count += 1
        if matches_count == len(word_parts):# and matches_count == parts - idx:
            perfect_match = compound_word
            break

OH, it was here:
            if match:
                canonical = match
                kinds.add(word_type)
                potential_match=True
                print(f"if_match near end: matches_count: {matches_count}\n")
                omit_next = matches_count
If there are multiple compound_matches and it's making its best guess, I had omitted the -1 from `omit_next = matches_count -1` (and also made it = instead of +=, though that didn't matter here). So if it was a perfect match it was correct (always 'omit_next += matches_count -1'), but an impefect match would be one count too high. With that fixed, 'use key on padlock' works again.

And the variations still work (lock padlock with key/unlock padlock with iron key, etc.)

Okay. That's fixed. What was I doing?

Oh, right. Setting up burned items.

Goddamn I just thought of something unrelated I wanted to start an issue about but I forgot. Have to write it /here/, then add the issue, otherwise this will happen a thousand times.
Oh, I wanted to add a godmode item spawner so I could test specific items without having to edit the locations.


LOCAL ITEMS:
{<ItemInstance wooden door / (af585e0e-1ab1-45c8-9359-8bba736b3341) / north testing grounds / None/ >, <ItemInstance wooden door / (361a1805-43ff-4e56-9541-42b8be782013) / north testing grounds / None/ >}

[[  look around  ]]


~~TESTING GROUNDS~~.
It's a place for testing, with nothing to the north.

You're facing north. A place to test things. Nothing here by default.
I don't know why these doors just refuse to show up.  Assumedly because `'not_in_loc_desc': True,` but that's not usually a problem, it's only because I'm trying to spawn them in and I haven't compensated for that flag.

As it's an issue of the spawner and not the mainframe, going to leave it for now.

[[  break ivory pot with hammer  ]]

Failed to find the correct function to use for <verbInstance break (b81fc6f8-d7ad-4d6a-8b5f-648d7de8c74c)>: '>' not supported between instances of 'str' and 'int'


Also:

#   [[  break jar with hammer  ]]
#
#   There's no glass jar around here to break.

But.....
#   You're facing north. A place to test things. Nothing here by default.a god hammer, and an ivory-coloured jar.

So yes. It needs to prioritise noun selection better. ivory-coloured jar /is local/. It shouldn't care about all about the glass jar.
I can only think that because I spawned it in in godmode it's not properly allocated to items, but it should be, it was moved to this place. Will have to look into it.

Oh, wait, no. It's because the ivory pot had the nicename 'an ivory-coloured jar'. Not 'pot'. So that's why it kept finding 'glass jar' instead.

But, 'break ivory jar' fails because it thinks I'm saying 'break ivory pot glass jar'. That's probably a reasonable error, though.

Okay. So, next issue:
    get_noun (and the parser before it) doesn't necessarily choose the right item.

we get:
#   You're facing north. A place to test things. Nothing here by default.a few shards of glass, and an old scroll.
#
#   [[  break scroll with hammer  ]]
#
#   There's no scroll around here to break.
because it finds the scroll at the shrine and says it's not here, but ignores the scroll that /is/ here.

Okay, fixed that. Now if there's more than one named instance returned, it checks and returns the one at current loc.
So, the actual issue I was trying to test:
#   You smash the scroll with the god hammer, and it breaks.
#   As the scroll breaks, it shatters into a clutter of glass shards.

Currently it only checks 'did the item break'. Not how it broke or what kind of item.
I did previously have 'on_death: "glass shards' as an item attr, but removed it because it wasn't implemented. Will re-add it.

So, if book_paper, it becomes ash. if glass, becomes glass_shards. I guess I really need a material_type, huh.
If container: stops being a container, any contents fall to current loc.
once broken cannot be broken again.

7.47pm
Setting it up.

        if k != "on_death":
            print(f"Expected 'on_death' in material_type but didn't find it: `{k}`")
        if "[[" in v:
            cleaned = v.replace("[[item_name]]", item_name)
            cleaned_dict[k] = cleaned
So,
item_def[item_name]["on_death"] = the item depending on item_type.


NOUN: <ItemInstance ivory pot / (5105da78-0ac0-4742-9d7b-7319062ceff9) / north testing grounds / <eventInstance item_is_broken (fa4c8205-b1c7-4eda-9721-19f9db43a411, event state: 2>/ >, broken ceramic shard

I can't remember where I told it to replace the name `[[itemname]]` with <itemname>. I did it a step too early and now I can't figure out where it's happening, which is ridiculous.

I need it to happen later, so I can readily identify the original as converted without having to un-parse the processed version. Cannot see it. Will figure it out tomorrow I think.

Searching through. 'broken ceramic shard' is applied already by the end of item defs.

Oh. I'm very silly. 'broken ceramic shard' is the generic answer to ceramic type. Right.

6.06am 16/2/26
Okay, fixed that.

New issues:
can break the jar with the hammer, even though the hammer is in a different location.
issue 2:
'break jar' expects 'metal jar' despite 'glass jar' being local. Same issue I've mentioned before. But the event message works, and the 'as the x breaks' msg now applies to whichever item is being broken.
Oh - the glass jar didn't drop its contents. I may have forgotten that part? Must've.

7.08am
[[  break jar with hammer  ]]

#   You smash the glass jar with the god hammer, and it breaks.
#   Removed dried flowers from glass jar.
#   As the ivory pot breaks, it shatters into a clutter of glass shards.

I want to remove that 'remove x from y' message, and add it after the event end msg. '{item}, {item} and {item} fall from the broken {container}.' instead.


10.27am back from appt.
So, today:

#   break must require noun2 be local.
#   > important: The noun checks in verb_actions just take instance from the parser, which is not always the local one if an imperfect match. Want to change it within the parser, not compensate in verbActions.
#   remove 'removed x from y' message and add replacement message as drafted above instead. Need to send a message back to def drop for when to/not to print it.

So first off, will work on the noun selection. Must prioritise things in current loc first, /then/ select whatever else might match if none.

# if you're facing east and go to graveyard, you should arrive facing graveyard east, no? I know logically it makes more sense to face away from the entrance (though that should be south in the case of the graveyard) but it makes more sense to me to treat it like teleporting; you're still facing the same way, even if 'realistically' that's not how it goes.

# And still, this persists:

take hammer
[[  take hammer  ]]', 'broken glass shard', 'gardening mag', 'dried flowers', 'desiccated skeleton', 'paperclip'}

Sorry, you can't take the god hammer right now.

There's no god hammer nearby. Why do this? I had this fixed before, why did I change it?
Oh, because it broke compound words and only gave the first bit. I had to combine the text field of perfect matches so it printed correctly, don't think I ever did that.

Going to put these as a combined issue on the github, hopefully remember them that way.

so, the 'hammer/god hammer' issue.
If perfect, make canonical == text, otherwise text == text?

11.24am
Maybe I should replace the 'make local_item_names then check if the names match' thing around 1436, verb_actions, and instead just check the location of inst by name directly. Would probably make far more sense...

Anyway. For now: fixing the broken items. Couple of things:
1: When the cluster of broken glass is made, it has the material type of generic. It needs to inherit from parent, all the broken variants do.
on_break needs to be None, as broken items (currently) cannot re-break.
Need to add 'is_broken' flag to item. Use the same flag as the reason_str in 'acts' (eventReg) so I can check directly.

12.09
replacing "on_break_item" in event_data with "is_broken" so it matches 'acts'. Could use trigger_acts but I'm using 'acts' elsewhere in this section. Will refine later.

1.19pm
Need to amend this later to work for plural nouns:
`"As the [[]] breaks, <material_msg>"`
==
`As the dried flowers breaks, it crumples into a broken echo of its former self.`

Not exactly right.

But, the autogenerated broken items seem to be starting to operate properly. Ish.

1.27pm
So. After the 'broken dried flowers' (not going to be a thing, but they're there so I'm using them for testing) are generated, the local_named looks like this:

local_named: {'desiccated skeleton', 'broken glass shard', 'broken dried flowers', 'mail order catalogue', 'moss', 'paperclip'}

And the description looks like this:
You're facing east. You see a variety of headstones, most quite worn, and decorated by clumps of moss, some broken dried flowers, and some broken glass shard.

But, this:
#  `look at broken dried flowers`
errors:
[ Couldn't find anything to do with the input `look at broken dried flowers`, sorry. <after get_sequences_from_tokens>]

Because it finds

values: ("token_role_options: Token(idx=2, text='broken', kind={'noun'}, canonical='broken glass shard') // kinds: {'noun'}",)
values: ("token_role_options: Token(idx=3, text='dried flowers', kind=('noun',), canonical='dried flowers') // kinds: {'noun'}",)

broken glass shard + dried flowers.

Which is bad because 1: why is the perfect match not being found despite being present? and 2: dried flowers were meant to be deleted after the 'breaking', so why is it still coming up with them?

Man I'm too tired for this.

Okay. Going to take a short break, then come back and have a shot at getting the parser to properly prioritise longer matches. I thought it already did but clearly I missed something.

OOOH. The new instance isn't added to item_defs and/or compound_words, so it's simply not in the running to be found in the parser even if it's found locally, because it'll never check locally for it if it doesn't exist. Okay, that makes sense. Good good. That I can fix.

Okay, yes.

#   [[  pick up broken dried flowers  ]]
#
#   The broken dried flowers is now in your inventory.

Again the plural is a pain, but I did make something to fix that a while ago. Will dig it out.

Okay, now break. Should eat.

Next:
Get back to the 'broken items'. Make sure you can't break the already-broken. Maybe draw out some plans for cleaning up the attr table.

Currently it does this:

You smash the broken dried flowers with the god hammer, and it breaks.
Item already is_broken, continuing.

So the def_break prints before the event has time to respond. Can fix that alright, most of the way there.

now break. 1.45pm

6.56pm
Currently,
[[  break flowers with hammer  ]]

You smash the dried flowers with the god hammer, and it breaks.

but the dried flowers stay there, no change. Need to refix it.

Working on the break messages, passing moved children back out to print after the event is done. Will fix the dried flower instance after.

7.48pm
Neatened it up some more, added the removal of deleted instances from membrane.plural_words_dict so 'dried flowers' directs to 'broken dried flowers', not the nonexistent original entity.

But, annoyingly, 'broken flowers' refers to 'broken glass shard', not 'broken dried flowers'. Really need to do that tally-comparison - you might both be partial matches, but one of you has 1/3, the other has 2/3; 2/3 should always win.

Maybe not tonight but tomorrow.

8.11pm
Well I did start implementing it a while ago it seems:
#   compound_matches[compound_word]=tuple(((compound_match, len(word_parts))))  ## if input == 'paper scrap': "paper scrap with paper":(2,4)

8.21pm

[[  look at dried flowers  ]]

You look at the broken dried flowers:
Hey, did it. Nice.

So now it checks how many matches vs misses and picks the best match, not just whichever it finds first.

12.35, 17/2/26

Working on https://github.com/harpoonlobotomy/choose-your-own/issues/7 :
#   [[ take key ]]

#   Sorry, you can't take the iron key right now.

So this is happening because if only perfect_match or only one match, it doesn't check against local names. It only does that when it needs to pick the best option from multiple.

So maybe I need to just make the compound_noun list from plural local nouns directly, instead of compound_nouns then checking against local_items.

Also, need to make sure to include transition items in local_nouns if the exit/entrance is local.

Have added transition_objs as a dict to registry; registry.transition_objs[cardinal_inst] = transition_item_inst

Changed transition objs from having the enter/exit location as placeInstance to cardinalInstance.

Okay. Back to the core 'can't take iron key' thing.

So, there are three different versions of this error message, all coming from different places:


#   [[  take hammer  ]]
#
#   Sorry, you can't take a hammer right now.
#
#   take key
#   Nothing found here by the name `key`.
#
#   take iron key
#   [[  take iron key  ]]
#
#   Sorry, you can't take a iron key right now.

So. First and last differ in that the first is unbolded red (no item instance in assign_colour), and 'iron key' is bolded and in the iron key.colour because the instance was found but wasn't local.
The 'Sorry, you can't take a x right now' is in def take():
#   print(f"Sorry, you can't take a {assign_colour(text)} right now.")

I think `Nothing found here by the name `key`.` is what should be aimed for, instead of letting it go all the way through the parser. Except, "There's no hammer around here to break anything with." makes a lot of sense, because the flowers /were/ local.

Really, I think I need an 'ending parser because no result' function to send results through for formatted printing etc instead of printing it mid-process.

It's just tricky because knowing 'key' is a noun is helpful.

So: we need to know if x is a noun (local or not) to determine acceptable verb_format options. So for that, we use the full noun list. (NOTE: the full noun_list needs to be updated if items are added through events/godmode/etc.)

Currently, 'take key' fails inside the parser because there are multiple potential options. But 'hammer' doesn't, because there's only one option.

#   break hammer with key
#   Nothing found here by the name `key`.
#
#   break hammer with iron key
#   [[  break hammer with iron key  ]]
#
#   There's no god hammer around here to break.

I like the formatting of 'no x around here to break', because it acknowledges the verb. But we only get that error if we accept 'hammer' as a noun.

That error messages comes from def verb_requires_noun in verb_actions:
#   print(f"There's no {assign_colour(noun)} around here to {verb_name}.")

So maybe...
Move the 'you can't {verb} a {noun} right now // 'sorry, you can't {verb} a {noun} right now' message to somewhere else. Whether the noun just isn't matched (in the case of 'key') or isn't local (in the case of hammer) it's routed the same way. The inconsistency between 'break hammer with key/break hammer with iron key/take iron key' is really annoying to me.

So how about: Currently the parser fails if it can't find the item. Maybe if nothing found after all compound_word tests, we just say 'assume it's a noun', so it can continue through the parser to check for formats etc. Then at the end, we can make the error message from that. Or maybe we have a new category for 'assumed_noun', where we use it to print error messages but skip the noun instance checks as they'll always fail.

But, I need to allow for sem/dir words here too. Right now if I type 'get the key from the table', it'll error on 'key'. But if there's no table, maybe that should be counted too. Though it makes sense enough to error on the first one I guess.

Okay. So currently:

In compound_words, if nothing, we add:
#    kinds.add("noun")
#    canonical = "assumed_noun"
and output the token as usual.

And we do the same thing at the end of the parser after compound words, so it should catch 'iron key' and 'key' the same way.

2.33pm
Pretty happy with `def print_failure_message(input_str, message=None, idx_kind=None, init_dict=None)` in misc_utilities. It calls it at the end when it's been caught by the nouns, and also gets called directly if there's a total failure in sequencer (so if you just type 'bleh' it prints `Sorry, I don't know what to do with `bleh`.`), and if you type 'take key' it prints 'There's no key around here to take', whether there's a key elsewhere or not - 'take bleh' prints `There's no bleh around here to take.`, which I like a lot better. It recognises a verb if you used one, and assumed a word in that format where a noun would fit would be a noun for the sake of the error message, but doesn't change error messages whether it's nearby or not a real word. Which I like.

Still have to work on the 'hammer' example, though. Because there's only one match for hammer, it still recognises it;

entry.items(): dict_items([('instance', None), ('str_name', 'god hammer'), ('text', 'hammer')])
[[  take hammer  ]]

Sorry, you can't take a hammer right now.

So while it does only print 'hammer' instead of the str_name now, it still gets all the way through to 'def take' before erroring out. So I think, unless cardinal, it fails anyway, even if there's only one possible option /unless/ that option is local. Because 'hammer' finding 'god hammer' is great, /if/ there's a known god hammer to be found.

Because currently, if it's a single word, it just checks
if word in items:
    kinds.add("noun")
    canonical = word

and 'items' is just registry.item_defs.

3.07pm
Okay so partway there;

#   [[  break flowers with hammer  ]]
#
#   There's no hammer around here to break.

So it's working better, but the message is clearly wrong. Okay.
I guess I can just go get_noun and format the message using that. Would have done that anyway if it got through to def_take/break/etc. Just having all the error messages going through the same place feels a lot better.

Although...

'use hammer to break flowers' errors
Sorry, I don't know what to do with `use hammer to break flowers`.
for an entirely different reason - I've not set up multiple-verb parsing at all. Damn. That would actually be useful.
I'd not been able to think of a time when multiple verbs would actually be useful, but 'use x to verb y' is actually the thing, huh.

Maybe I do that part inside parser. If there's two verbs and the first is 'use', then just rearrange the dict to be 'break flowers w hammer' so that verb_actions can deal w it.

Okay so the 'break flowers with hammer' - now outputs:

[[  break flowers with hammer  ]]

There's no hammer around here to break the dried flowers with.
with the formatting
There's no <yellow>hammer</y> around here to <green>break</g> the <inst.col>dried flowers</inst.col> with.

And I'm quite pleased with that.

Also added an exception to the error print for verb.name == drop, so the drop message matches.

#   [[  drop paperclip  ]]
#
#   You can't drop the paperclip; you aren't holding it.
 == paperclip is local but not in inv.

#   [[  drop hammer  ]]
#
#   You can't drop the hammer; you aren't holding it.
== no item 'hammer' found

I like that it's the same either way. The error message is consistent. From a meta perspective it's useful to know if 'hammer' is an item in the world or not, but that's not data for the player to know unless there is one accessable to them.

## thing to remember if I can:
` I could add a god mode where there's some item or smth that gives you the ability to know all items anywhere, so if you type 'get hammer' it'd be like 'there's a hammer in north testing grounds - you bring it to yourself, and find it in your backpack'. It'd be some ability or smth, not a general part of the game. It'd be kinda neat. Not something I'm doing now though. `


Issue I caused myself now:

FAILURE IN SEQUENCES: [Token(idx=0, text='go', kind={'verb'}, canonical='go'), Token(idx=1, text='to', kind={'direction'}, canonical='to'), Token(idx=2, text='assumed_noun', kind=('location',), canonical='assumed_noun'), Token(idx=3, text='hotel', kind={'noun'}, canonical='assumed_noun'), Token(idx=4, text='room', kind={'noun'}, canonical='assumed_noun')]

'city hotel room' comes back with 'city (kind=location, but text == 'assumed noun')', and doesn't properly omit because it's adding nouns. fffff.

(Have made the loc/noun work better though, now in both places it checks if noun.name == loc.name and uses that as the intent if matching.)

Now to work on the `'city hotel room' is three unknown nouns` issue.

4.56pm
okay so it finds:
second_perfect: city hotel room
but then immediately:

#  ('Tokenise: idx: 3, word: hotel, omit_next: 0',)
second_perfect: city hotel room
second_omit_next after second_perfect: 0
Hm. Why.

Okay, I think it was because of this:

if perfect_match and ((word_type == "noun" and perfect_match in local_named) or word_type == "location")

previously was just

if perfect_match and perfect_match in local_named, which obviously the locations never were.
So with that fixed, it now goes to the city hotel room correctly.

Hm. Well if you give it the full name.

If not the full name, if just 'hotel room' or 'city room' etc:

FAILURE IN SEQUENCES: [Token(idx=0, text='go', kind={'verb'}, canonical='go'), Token(idx=1, text='to', kind={'direction'}, canonical='to'), Token(idx=2, text='hotel', kind={'noun', 'location'}, canonical='city hotel room'), Token(idx=3, text='room', kind={'noun', 'location'}, canonical='city hotel room')]

Hmm.

5.30pm
okay, 'go to hotel'/'go to hotel room' works again now.

Hm.
So the error messages still need work.

# [[  look at tv  ]]

input_dict: {0: {'verb': {'instance': <verbInstance look (d9bea324-c4ba-499d-8e81-1b015954d09c)>, 'str_name': 'look', 'text': 'look'}}, 1: {'direction': {'instance': None, 'str_name': 'at', 'text': 'at'}}, 2: {'noun': {'instance': 'else in if kind == noun', 'str_name': 'assumed_noun if not matches', 'text': 'tv'}}}

# There's no tv set around here to look.

1: need to change the error print to 'to look for' if verb.name == 'look'.

but also it's giving me the noun.name.

Hm.
As well as the print.name error, I have this:

Compound matches: {'tv set': (2, 2)}

'tv set' is a perfect match, but the tv set isn't local.

But, 'set' is a verb.

Because 'set' is a verb, it makes the format 'verb_dir_noun_verb', which breaks.

Honestly I might make an exception specifically for 'tv set' because it's not likely an issue with other things. Idk.

Well fuck me. I had 'go to hotel room' working; and now it's broken again and I hadn't committed yet. fml.

Okay think I rescued it, hopefully. Committing now regardless.

Really need to formalise it more instead of just a long run of if branches but it works alright for now.


Hm.
[[  look at tv set  ]]

dict: {0: {'verb': {'instance': <verbInstance look (2cc38475-3079-4823-9503-c062b9d84743)>, 'str_name': 'look', 'text': 'look'}}, 1: {'direction': {'instance': None, 'str_name': 'at', 'text': 'at'}}, 2: {'noun': {'instance': 'assumed_noun', 'str_name': 'assumed_noun', 'text': 'assumed_noun'}}}
There's no assumed_noun around here to look at.


[[  look at tv  ]]

dict: {0: {'verb': {'instance': <verbInstance look (2cc38475-3079-4823-9503-c062b9d84743)>, 'str_name': 'look', 'text': 'look'}}, 1: {'direction': {'instance': None, 'str_name': 'at', 'text': 'at'}}, 2: {'noun': {'instance': 'assumed_noun', 'str_name': 'assumed_noun', 'text': 'tv'}}}
There's no tv set around here to look at.

So why did 'tv' get to keep the text 'tv', with instance assumed_noun and str_name 'assumed_noun', but 'tv set' got all three 'assumed_noun'?

Because I mean this:
'instance': 'assumed_noun', 'str_name': 'assumed_noun', 'text': 'assumed_noun'
is not useful.


"Failed to find the correct function to use for <verbInstance unlock (e97c8c31-6666-4212-bfbd-cb2c98784fd1)>: argument of type 'NoneType' is not iterable

[[  look at gate  ]]
"
^^ This happens inside is_event_trigger. Need to remember to look into this properly. Possibly children related if I accidentally rolled back one of the changes that stopped it iterating 'children' if inst not hasattr children.

When it hits that error the action still completes, it's just the event check that fails.

Oh this is an issue though:

[[  take key  ]] canonical: assumed_noun, word: key at end

<ItemInstance iron key / (123bac1a-dfec-4a50-96eb-59cc69127a1f) / north work shed / <eventInstance reveal_iron_key (e4bb8e29-a1a2-4f8a-b324-9328275cb532, event state: 2>/ > can be picked up.
after can_take: cannot_take: 0 // added_to_inv: <ItemInstance iron key / (123bac1a-dfec-4a50-96eb-59cc69127a1f) / north inventory_place / <eventInstance reveal_iron_key (e4bb8e29-a1a2-4f8a-b324-9328275cb532, event state: 2>/ >
about to check event triggers.
The iron key is now in your inventory.

iron key's event is still in the future: I picked up the map, it failed the trigger so didn't start the thing, and yet the key is here. Wonder if the key was hidden and then unhid with the event and just the event text didn't print, but that's not true because the event state is still 2. Will look into that too.....


6.36pm
Oh come on, what?
#   [[  go to hotel  ]]
#
#   dict: {0: {'verb': {'instance': <verbInstance go (33932276-b87a-4e30-a1b2-41c2615e68d9)>, 'str_name': 'go', 'text': 'go'}}, 1: {'direction': {'instance': None, 'str_name': 'to', 'text': 'to'}}, 2: {'noun': {'instance': '4', 'str_name': 'city hotel room', 'text': 'hotel'}}}
#   There's no hotel around here to go.

okay fixed again, I think. Still v v scrappy though. But I guess while it's still developing keeping it scrappy is okay, otherwise I'll rebuild the whole thing every week when it needs something new.



#   [[  take tv  ]]
#   You can't pick up the tv set.
#
#   [[  take television  ]]
#
#   There's no tv set around here to take.

Well shit. So much for consistent error messages.

`take tv`:
#   kinds: {'noun'}, canonical: tv set, perfect: None, word: tv at end
`take television`:
#   kinds: {'noun'}, canonical: assumed_noun, perfect: None, word: television at end

Oh, does local_nouns not include alt_words? Probably not, huh. Okay. Can fix that.

Okay, done.
'look at television' and 'look at tv' now both work again in the new setup, though 'look at tv set' still doesn't. That 'tv set' is a perfect match /should/ mean the omit_next is used to skip 'set' but it doesn't, will figure out why.

okay I need to put assumed_noun somewhere else. Now I have variation I don't want between look at tv/look at television.

The previous error was because 'tv set' had 'tv' as a alt_name, so it would be complete after 'tv', which is why it didn't skip 'set'.

But yes, now I need to get the assumed_noun thing right.
It's meant to be entry[text] every time, but:

dict: {0: {'verb': {'instance': <verbInstance look (246b0663-81d2-4db6-bba6-3016c15d6ae7)>, 'str_name': 'look', 'text': 'look'}}, 1: {'direction': {'instance': None, 'str_name': 'at', 'text': 'at'}}, 2: {'noun': {'instance': 'assumed_noun', 'str_name': 'assumed_noun', 'text': 'television'}}}
==
There's no tv set around here to look at.

7.32pm
The issue was in assign_colour, as it took strings and got the instance (but not by alt_names, via the inconsistency). Have changed it so it doesn't get the item instance if a colour is provided, so now 'there is no tv' and 'there is no television' presents identically.]

Okay, the issue of iterating None at event_end was in clean_messages, I failed to account for message that /didn't/ have [[]] in them. Fixed now.

10.41
Fixed spacing of event msgs with newlines.

Wonder if I can do a version of init_loc_descriptions that doesn't draw from the json again. Or if that's even something I want to do.

Could just get the JSON once and have it in memory, but I worry about having too much stuff in memory. Should look into how to check.

11.07am

Trying to run memory_profiler's memory_usage because I'm curious, just running it on initialise_all.
In event_registry, it gets this:

Multiple instances in {<eventInstance reveal_iron_key (2f7c76bc-a230-4414-bdfc-fe43856c348f, event state: 1>, <eventInstance reveal_iron_key (f9177e6c-57af-4003-abff-9ecc272d4451, event state: 1>, <eventInstance reveal_iron_key (9e432c1b-7796-4a6d-9b18-aa03eae990ea, event state: 1>} for name reveal_iron_key. Haven't dealt with this yet.

Oh, it's because it runs it several times, and because it's already been initialised, it's adding the new to the previously initialised. Fair enough.

Memory usage: 0.0 MB
Not sure useful though.

12.10
Some interesting error logs while trying  to run memtests. (Got a memory result, Memory usage: 2.91796875 MB for test_runme, including initialisations. So that's not terrible I think?)

Interesting logs in question:


[[  go west  ]]

You turn to face the west graveyard

Standing in unkempt long grass, you see what looks like a work shed of some kind, with a wooden door that looks like it was barricaded until recently.

[[  go north  ]]

You turn to face the north graveyard

There's a dark fence blocking the horizon, prominently featuring a heavy wrought-iron gate - standing strong but run-down, and an old dark-metal padlock on a chain, holding the gate closed.

[[  go to shed  ]]

You're now in the work shed, facing north.

Around you, you see the interior of a rather run-down looking work shed, previously boarded up but seemingly, not anymore.
There's a simple desk, hazily lit by the window over it to the north.

The work shed is simple structure, with a dusty window in one wall over a cluttered desk. On the desk, there's a yellowed local map showing the region surrounding the graveyard, and a pair of secateurs.
## NOTE: This should not go into the shed. One, because the gate event should stop travel away from the graveyard, and two, because the door isn't open and thus shouldn't allow inside (<!FALSE! the shed is allowed under the gate event.>). I'm assuming this is because I told it to assume 'shed' is a location, but it needs to add a check for 'if location has transition_obj, is transition_obj open'. And or, if location.name is also a noun_name, 'go to' goes to the ext, 'go into' goes to the internal (if trans obj allows). I really thought I already had the trans obj in place, but maybe the rerouting for noun+loc obj avoids it. Will check.
[[  go north  ]]

You're already facing the northern work shed.


[[  go to work shed  ]]

You're already in the work shed

[[  go north  ]]

You're already facing the northern work shed.



[[  go to shed door  ]]

There's no shed door around here to go.
# NOTE: 'go to shed door' is a bit nonsense, but a) there is a shed door, it's 'wooden door' and it's the trans object for that location, and should be found locally.
# Also: Need to edit the error message to 'to go to' for verb.name 'go'.

[[  go to work shed door  ]]

You're already in the work shed
# NOTE: 'work shed door' should == 'shed door'. Might have to add it as an alt name.
# followup: added 'work shed door' to alt_names, and still:
`[[  go to work shed door  ]] > You're already in the work shed`


[[  open door  ]]

There's no door around here to open.
# NOTE as above, it should absolutely be finding this door. Need to fix the local_items setup because it's failing to catch this. Assumedly because the door is technically located outside the location, but it should be catching both
#          "enter_location": "north work shed",
#          "exit_to_location": "west graveyard",
# in the local_items setup. Will look into it.


[[  close door  ]]

There's no door around here to close.


[[  open shed door  ]]

There's no shed door around here to open.


[[  close shed door  ]]

There's no shed door around here to close.

[[  go into shed  ]]

Failed to find the correct function to use for <verbInstance go (692f0e53-0536-43b7-9e34-c56bc6e7aad6)>: maximum recursion depth exceeded
# NOTE: Well this issue is obvious. Just need to fix the function so it doesn't recurse.

[[  open door  ]]

There's no door around here to open.

[[  go into work shed  ]]

Failed to find the correct function to use for <verbInstance go (692f0e53-0536-43b7-9e34-c56bc6e7aad6)>: maximum recursion depth exceeded

[[  go into work shed  ]]

Failed to find the correct function to use for <verbInstance go (692f0e53-0536-43b7-9e34-c56bc6e7aad6)>: maximum recursion depth exceeded

[[  leave shed  ]]

You can't leave without a new destination in mind. Where do you want to go?

[[  drop mag at church  ]]

You want to drop at church but you aren't there...

[[  go into work shed  ]]

Failed to find the correct function to use for <verbInstance go (692f0e53-0536-43b7-9e34-c56bc6e7aad6)>: maximum recursion depth exceeded

Failed to run input_parser: 'NoneType' object is not subscriptable
Failed get_noun_instances: cannot access local variable 'dict_from_parser' where it is not associated with a value
Failed parser: cannot access local variable 'error' where it is not associated with a value

So, today:
#   'go to shed' needs to check if 'shed' == a trans obj nounname and if that trans obj is connected to the loc. If so, if trans obj not open, cannot enter; instead go to ext loc and describe trans obj.

#   fix recursion in def go() for [[  go into shed  ]]

#   trans objs should be 'visibile' from inside the trans obj's enter_location, eg:
#          "enter_location": "north work shed",
#          "exit_to_location": "west graveyard",
# so if at north work shed, 'shed door' should be present even if technically located elsewhere.

#   "[[  leave shed  ]]": As 'shed' is a location with an outside, 'leave shed' should be valid.


also:
[[  look around  ]]


You're in a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east sit a variety of headstones, to the south stands a mausoleum, and to the west is what looks like a work shed of some kind.

You're facing east. You see a variety of headstones, most quite worn, and not too much else - , and some broken glass shard.

Need to fix the card description for graveyard east. One: the obvious 'else - ,', and 'some broken glass shard' - some + singular? Bad.
It's getting 'some' correct (assumedly a plural checker, will need to remind myself) but it should be using nicename, which would be
    "nicenames": {
      "if_singular": "a glass shard",
      "if_plural": "a few shards of glass"
, but apparently it's not. Hm.


Memory usage for the whole thing (running the entire 27 command loop inside the memory checker):

Memory usage: [25.203125, 25.97265625, 28.82421875, 29.48046875, 29.4921875, 29.50390625, 29.51171875, 29.5234375, 29.53125, 42.78515625, 47.484375, 50.3671875, 50.42578125, 52.73046875, 53.21875, 53.171875, 52.0390625, 52.0546875, 52.0625, 52.07421875, 52.08203125, 52.09765625, 51.78515625, 52.0390625, 52.08984375, 52.08984375, 52.08984375, 52.08984375, 52.08984375, 52.08984375, 52.08984375, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.09765625, 52.109375]
Peak increase: 28.015625 MB
USAGE AFTER TEST: Peak increase: 28.015625 MB

Removing the map opening:

Memory usage: [25.4375, 26.140625, 28.85546875, 28.85546875, 28.85546875, 28.85546875, 28.85546875, 28.85546875, 28.85546875, 28.85546875, 28.85546875, 28.85546875, 28.85546875, 28.85546875, 28.85546875, 28.86328125, 28.87109375, 28.87109375, 28.87109375, 28.87109375, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.921875, 28.9375]
Peak increase: 3.5 MB

So that's nice. 3.5mb for the full initialisation and run isn't too bad, I think. Need some comp sci major to let me know.

2.43pm
Hm.

'look around' has an extra newline. Need to fix that.
I wouldn't mind adding another newline before the input print though. It's a bit claustrophobic.

...

The newlines overall are inconsistent.
...
So is it 'the following one succeeded' that does it?

It was the extra \n in print_failure_message.

Also:
[[  take dried flowers  ]]

dried flowers is already in your inventory.
vs
Dried flowers fall from the broken glass jar.

Need to add caps to the 'already in inventory' print.

3.14pm
For the moment, going to fix descriptions. Should be easy enough.

So, the issue is:

 "no_starting_items": "not too much else - ",

 It's because it does

if len(long_desc) == 1 and no_items_text:
    if local_items:
        if no_starting_items:
            long_desc.append(no_starting_items)
and then appends the item(s), which means when it comes to the formatter, it has three parts.

Maybe I merge the start text with no_starting_items so it only counts for one. With one item and a total of two it would print

        item_description = (f"{long_desc[0]}{long_desc[1]}")

But no, then it would still be broken if there was two extra items. Maybe I just remove the starting_items print if there are additional items at all.

Okay. Have just removed starting_items print entirely, so it's just
#   You see a variety of headstones, most quite worn, and some broken glass shard.

Now to deal with 'some broken glass shard'.
the item name is 'broken glass shard'. So I assume it's checking for plurality to get the 'some' (as it's not part of the item def) but not using the plural nicename properly. Assign_colour /does/ request nicename for loc_items

ITEM: <ItemInstance broken glass shard / (0c469e89-d79f-4835-8f71-b349f4492508) / east graveyard / <eventInstance item_is_broken (f8963d8e-9998-4c96-b105-20f7529e159b, event state: 0>/ 3>, print_name: broken glass shard, nicename: some broken glass shard

Okay so in init_descriptions (itemReg):
Not description: broken glass shard, description: None // descriptions: {'if_singular': 'a shard of broken glass.', 'if_plural': 'a scattering of broken glass.'}
ITEM: <ItemInstance broken glass shard / (09ff5abc-dc80-4674-bb73-cece5612eba8) / north no_place / None/ 0>, print_name: broken glass shard, nicename: some broken glass shard

Oh, it's because nicenames is wrong:
NICENAMES: {'generic': 'some broken glass shard'}

Hm.
self.nicenames: {'generic': 'some broken glass shard'}
Even printing it in init. Maybe it's wrong in item_dict_gen.

3.35pm
generator item defs: {'alt_names': ['broken glass shards', 'glass shards', 'shards of glass', 'shard of glass', 'shard', 'shards'], 'can_pick_up': True, 'descriptions': {'if_singular': 'a shard of broken glass.', 'if_plural': 'a scattering of broken glass.'}, 'has_multiple_instances': 3, 'single_identifier': 'shard', 'plural_identifier': 'shards', 'item_size': 'small_flat_things', 'item_type': ['can_pick_up', 'is_cluster', 'standard'], 'nicenames': {'if_singular': 'a glass shard', 'if_plural': 'a few shards of glass'}, 'slice_attack': 10, 'slice_defence': 4, 'smash_attack': 2, 'smash_defence': 2, 'material_type': 'generic', 'on_break': 'broken [[item_name]]'}
Nope, generator has it right.

Okay. So by the end of itemreg init_single, it's already
`'nicenames': {'generic': 'some broken glass shard'}`

okay, fixed:
You see a variety of headstones, most quite worn, and a few shards of glass.

It was the compound instancing in event_reg; it disregarded the base item's nicenames.
Now, it only does that if there's no existing 'nicenames'.
Now that might not be suitable. In this case, the resulting object was its own object. But if I'm going
'break lamp'
the nicename should be 'a broken lamp'

Okay. So now it checks if the thing is a cluster and if it doesn't have is_broken already - if it does, then it's a premade 'broken' item, otherwise it's 'broken x'. Might need adjustment but it's better. Also fixed the 'dried flowers already in inventory', made it
#   (f"The {assign_colour(noun_inst)} {is_plural_noun(noun_inst)} already in your inventory.")
so that's a solid improvement.

With the descriptions done:
find x: I'd like to expand it. I think we need to route from the error print fn back to find, which is weird but I think necessary for it to work, otherwise I have to allow non-local for the entire parser or start judging nouns based on verb mid-parse, which I don't want to do.

Fixed a random check for game.inventory that was still in verb_actions. Need to clear out any more of those.

Hm.
'find branch' fails for a specific reason. It makes it through the parser, because 'branch' finds 'forked tree branch' loc. There is a branch noun, but it's not found because it's not local.
Oh wait, it's not called branch at all. Oops.

5.07pm
Have updated def find(), it now checks for noun.text and checks for a word/compound word against that text, and produces the output accordingly. If it finds nothing (so your input isn't an item anywhere), then it goes back to print_errors for 'There's no x to find'. Pleased with that.

Okay. Have re-fixed the event messages for the moss, the formatting was a little broken and I was getting errors from that particular branch of eventReg.

>>> set("Hello!")
{'H', 'l', 'e', '!', 'o'}

>>> {"Hello!"}
{'Hello!'}

I need to keep this in mind. {"hello"} adds it as a component to a set, set("hello") creates a set with each of the iter elements as a component.


Hm. Why this:

[[  find carved stick  ]]


[[  take carved stick  ]]
?
No error, just nothing printed. Not ideal...

Oh, it's if it runs 'find' while actually at the location of the item.

[[  find carved stick  ]]

You can't see the carved stick right now.
Hm. Not an improvement.

Okay. Fixed it now. Now it only converts 'find' to 'look' if item is in current cardinal, else it just reports the location of the first found by name.

Next:
#   [[  burn magazine with matchbox  ]]
#
#   There's no magazine around here to burn the matchbox with.

so close but not cigar.

Okay. Fixed now.

[[  burn magazine with matchbox  ]]

There's no matchbox around here to burn the magazine with.

Now a permanent fix as I've switched the order and it won't always fit, but it'll do.
I think I'll just have to do a format library up properly to define noun1/noun2 for the formats, so based on format_str it automatically delegates which noun is which for print formatting etc. Would be useful. Also useful for lock/key interactions etc.

Hm. That fix isn't working perfectly...

[[  burn magazine with matchbox  ]]

There's no matchbox around here to burn the mag with.
Now here, we /do/ have 'matchbook', but we /don't/ have 'mag'. I need to tailor the message to which has failed if I have enough data in the dict to know there are two nouns, especially if I have one fully identified.

#   NOTE: That error only shows up like that when there's no magazine.

Now, in the runs where I do have a magazine, it claims the gardening mag can't burn. Clearly I'm checking the wrong thing.

6.47pm
This is odd.

The matchbox contains:
  matches

[[  take match  ]]

There's no match around here to take.

But,
  "match": {
    "alt_names": [
      "matches"
    ],
Matches is the alt_name. Why is it not 'finding' it?

Changing the child name in item_defs doesn't help, it just makes it "match" everywhere.
I guess maybe when we print children we're not checking the multiple_instances state of the children. Will have to add that.

Or ffs just assign them at init_single...

Oh, apparently I already do. Idk why it's failing then.
Needed to set print_name as that's what assign_colour is, and I forgot.

That's fixed, so I have this:
The a matchbox contains:
  a few matches

but:

[[  take match  ]]

There's no match around here to take.

[[  take matches  ]]

The a matchbox is already in your inventory.

local_named: {'puzzle mag', 'matchbox', 'clumps of moss', 'moss', 'dried flowers', 'clump of moss', 'severed tentacle', 'local map', 'gate', 'padlock', 'iron key', 'box of matches', 'paperclip'}

So I can't take the matches, because they're in a container. Bleeeeh.

So I guess.... I need to include one level of container-children in local_nouns. Damn.

![alt text](image.png)
Okay why are the colours wrong.

The match is now in your inventory. <- cyan

[[  inventory  ]]

moss x2
dried flowers
padlock
matchbox
mail order catalogue
iron key
match <- blue
paperclip
local map

You look at the match: <- cyan


Also the match's description is wrong:
[[  look at match  ]]

You look at the match:

   A number of matches, all unused.

Should be singular, I only picked up one.

Bleeeeh

[[  take match  ]]

The match is already in your inventory.

Okay so, I have it checking local items to see if there's already something existing before refusing to take, but I guess it's /not/ taking available container contents. Okay. Will work on that tonight/tomorrow.

# NOTE: LOCAL ITEMS MUST INCLUDE ACCESSIBLE CONTAINER ITEMS FOR TAKE/ETC.

I think I need a fn for 'is_acccessible_by_name'. Because check_item_is_accessible just gives y ou the outcome for that noun, but doesn't check 'but is there another one with the same name that /is/ viable for the context'.

Also it needs to be context aware. pick up == cannot include inventory. drop == cannot include non-inventory excluding inventory-containers, etc.

Parser issue:

values: ("token_role_options: Token(idx=1, text='shed', kind=('location',), canonical='work shed') // kinds: {'location'}",)
(  Func:  verbReg_Reciever    )
values: ("return for sequences: viable sequences: [['verb', 'location']], verb_instances: [{0: <verbInstance take (a41076b0-8ffd-43ff-8bbb-94e064b876c3)>}, {1: <verbInstance go (9902029e-9a51-4397-80f9-7bc729adc6fb)>}], sequences: [['verb', 'location']]",)
(  Func:  verbReg_Reciever    )
values: ("sequences after sequencer: [('verb', 'location')]",)
Failed to run input_parser: 'NoneType' object is not subscriptable
Failed get_noun_instances: cannot access local variable 'dict_from_parser' where it is not associated with a value
Failed parser: cannot access local variable 'error' where it is not associated with a value

This isn't even related to what I'm doing this afternoon...
Issue caused because I'm not there, and can't 'take shed' when I'm not near it. But idk why it's not just going through the regular error channel. Need to dig into it later.


ANS ITEM: wooden door, item_type: <class 'str'>, val: {'enter_location': 'north work shed', 'exit_to_location': 'west graveyard'}

Hm.

Why is the wooden door not found inside the shed. It's just failing entirely at the parser stage; it should be found by the updated local_nouns and it's not.

Wooden door just straight up isn't mentioned:
local_named: ['paperclip', 'moss', 'dried flowers', 'padlock', 'iron key', 'match', 'matchbox', 'fashion mag', 'local map', 'secateurs', 'clumps of moss', 'clump of moss', 'box of matches', 'matches', 'few matches', 'single match']

ItemInstance shuold already have:

            registry.transition_objs[self.enter_location] = self
            registry.transition_objs[self.exit_to_location] = self

(So for that matter I don't know why it's giving me strings for these values:

TRANS ITEM: wooden door, item_type: <class 'str'>, val: {'enter_location': 'north work shed', 'exit_to_location': 'west graveyard'})

item and both locations, all strings.

At initialisation:

EXIT TO LOCATION: <cardinalInstance west graveyard (a7408964-8ada-49e6-b323-3fb6d9a7b639)>
self.ENTER_LOCATION: <cardinalInstance north work shed (bec03201-e040-46ee-a89c-59a2a3a979ad)>

I do have to remember though I have
"exit_item" and "entry_item" that should  refer to the trans obj.

And registry.transition_objs[self.enter_location] = self should directly connect the card inst to the item inst.

Okay well according to the actual object data, it's:
 'enter_location': <cardinalInstance north work shed (61f7da6f-1f46-42fc-86e3-44058bc5a7b6)>,
 'exit_to_location': <cardinalInstance west graveyard (8f7fdf22-94a2-42a0-b02d-69226bfaedb8)>,

So that part's working, I'm just not sure why it's printing as a string.....

Oh, is it because we have to init the cardinals before the items, so there's no names. But... Well I guess when the items are init'd they add their own details, but the loc_dict... doesn't get updated, I guess?

So yeah, self.transition_objs[item] gets written up at the start, before the items/instances exist yet. So it's just names.


EXIT TO LOCATION: <cardinalInstance west graveyard (b74afc7c-e15e-4c7b-904f-c47bf9712ae3)>
registry.transition_objs[self.exit_to_location]: <ItemInstance wooden door / (a327c63b-52a8-4621-99fc-38fa7a777516) / north no_place / None/ >
self.ENTER_LOCATION: <cardinalInstance north work shed (29929ef0-1484-4c65-ab88-2215ca859c57)>
registry.transition_objs[self.enter_location]: <ItemInstance wooden door / (a327c63b-52a8-4621-99fc-38fa7a777516) / north no_place / None/ >


So this works, dammit:
registry.transition_objs[self.enter_location]

Except when I come here:

.......

Oh.

The one that works is registry, not location. I've been confusing the two.

right. Okay.

Well. # TODO: After init, replace env_data's transition_objs with itemReg (or just don't add it to itemReg at all, just do it straight to env_data). It makes more sense that way because env_data already has the damn cardinals.


Oh fuck right off.

Around you, you see the interior of a rather run-down looking work shed, previously boarded up but seemingly, not anymore.
There's a simple desk, hazily lit by the window over it to the north.

You're facing north. The work shed is simple structure, with a dusty window in one wall over a cluttered desk. On the desk, there's a yellowed local map showing the region surrounding the graveyard, an old iron key, mottled with age, a pair of secateurs, and a clump of moss.

It's mixing up descriptions again. God dammit.....


Okay - little progress again.

location from current_loc: <cardinalInstance north work shed (a241856c-da8e-4b97-b2f8-d16e05be1d4b)>
LOCATION: TRANSITION OBJS: {<ItemInstance wooden door / (aee1ab4e-0f39-41a6-b4f5-23ec9e65ae58) / west graveyard / None/ >}
TRANS ITEM: <ItemInstance wooden door / (aee1ab4e-0f39-41a6-b4f5-23ec9e65ae58) / west graveyard / None/ >, item_type: <class 'itemRegistry.ItemInstance'>

Seeing the door from inside the shed. Okay.

10.35

Okay - finally it's less broken. Door is accessible from inside. Have just replaced the original local_nouns in verb_membrane with the new version. Will take some time tomorrow to do that across the board. It includes items in containers (though I can exclude those later and/or just rerun it to recollect.

Getting v v tired. Might have to leave it a bit.

8.51am
Okay, back at it today.

Have figured out the issue here:

Transition objs at west graveyard: {'wooden door', <ItemInstance wooden door / (2e57aa44-e334-4242-8b0b-df0afd5d8066) / west graveyard / None/ >}
ITEM: wooden door
Failed to run input_parser: 'str' object has no attribute 'name'

I missed the vital point yesterday.
here:
#   transition objs at west graveyard: {'wooden door', <ItemInstance wooden door / (2e57aa44-e334-4242-8b0b-df0afd5d8066) / west graveyard / None/ >}

That's two items, not one. One str, and one instance. The str was added by locRegistry at init, and the inst was added by itemReg at init. That's why it's suddenly claiming there's a string.

Not going to fix that in this function though, going to fix it in itemReg.
When it's adding things to locReg transition_objs, if there's an existing str with inst.name, replace the str with the inst. And there should /always/ be an inst to match the str, because that's where the need for the inst comes from. God I'm so tired I can barely see.

8.57
eyyy, I fixed it. [[  enter shed  ]] works again immediately.
Ey 'look at door' from inside works too. Thank goodness.

And it works the way I want, too. When the parser starts, the full local runs.

the only thing I'm thinking is whether I want to store the various options (not_inv/not local, etc) during that initial run, or rerun it with those constraints once it hits the verb.

11:50
Have fixed a few more minor things. Forgot what they were already though.

Re the last note, having thought about it: Use get_local_nouns exactly as originally intended. Full set for the parser, then the verb actions send specific requests for the subset of nouns they require as they require them. It just makes sense.

Though I wouldn't mind a 'get_nouns_w_str(input_dict)' like

def get_nouns_w_str(input_dict):

2.32pm
Added def get_nouns_w_str(input_dict): to verb_actions. Happy with it.

Okay. So.

I need to remove verb_requires_noun, it was an okay concept but doesn't do its job well, esp compared to get_local_nouns now.

Oh. I confused myself.

The one I wrote today/yesterday is get_local_nouns(self) in verb_membrane.

There is a similarish fn in itemReg called get_local_items.
get_local_items performs what looks like an almost identical task, including the inventory or not, optional by_name (that never worked properly.) It's only used 4 times throughout but I should be able to just directly replace it with get_local_nouns.

get_local_nouns currently builts a dict, it doesn't really have to. Not sure if I'll use it or not. Maybe I will in the verb actions. leaving it there for now, maybe delete later.


Things to work on:

1: can enter shed even if door is closed. Need to fix.
2 "go to door" returns `You can't go enter something unless you're nearby to it.`, when I'm standing in the shed. This will be resolved with get_local_nouns though I think.

no wait where's the function I wrote today. Did I write two and get confused? Because this one doesn't have the noun, excluded str, verb...

OH.
It was

def find_local_item_by_name(noun:ItemInstance=None, verb=None, access_str:str="all_local", current_loc:cardinalInstance=None)
in item_interactions that I was thinking about. Goddamn... So I have three?

Let me check this.

so, find_local_item_by_name is the one I was pleased with. Ignore the fn names given above.
It's in item_interactions.

VerbRegistry uses once to get local_nouns, where weirdly it makes a dict and a list...?

# Note: No longer using all_nouns_list in the input_parser. Consider removing it entirely once some more testing's been done.

So this is the one I want to use everywhere. Seems the most consistent and flexible. Run with no args and get the full local_nouns list, add verb or access_str to set limits on which categories are added to the set,add a noun to get name matches.

find_local_item_by_name(noun:ItemInstance=None, verb=None, access_str:str="all_local", current_loc:cardinalInstance=None)

Okay so, we get instances here:

registry.instances_by_name(name)
at ln 123 in verb_membrane/get_noun_instances.


Then we do this and try to find item in local_named_items, which looks like a poor man's find_local_item_by_name
local_named_items = registry.get_local_items(include_inv=True, by_name=noun_inst.name)

I need to fix this part:
 elif noun_inst.single_identifier in entry["text"]: (ln 167 verb membrane)
 because that's far messier than it needs to be.

Yeah get_local_nouns is what adds to membrane

        self.local_nouns = list(local_items)#local_named
        self.local_dict = local_items
        #print(f"\nlocal nouns: {self.local_nouns}")
        logging_fn(note = "end of get_local_nouns")

But I overwrite it with

    membrane.local_dict = clean_nouns
    membrane.local_nouns = list(clean_nouns)???
from find_local_items_by_name anyway.

God I was tired. Okay.

Then we have

registry.get_local_items(include_inv=True, by_name=noun_inst.name)
which is invoked around ln 158 getting the clister identifiers in get_noun_instances.

Oh, just found where 'instance = "4" came from:
# dict_from_parser[idx][kind] = ({"instance": "4", "str_name": entry["str_name"], "text": entry["text"]})
No idea when or why...

So instead of instances_by_name, it should be the new one with the name. But it requires an instance, doesn't it... Okay.
Well I do get a name...
Or I guess, could just grab the first instance by that name and just use that for the process. It won't return if it's not a match anyway.

Or no, maybe we just don't get any instances inside membrane at all.
Or no, maybe we just use the dict that is already stored in membrane from this current run. Go with that, assume it's correct, then do all the proper checks for verbs once we're out. So we get a placeholder noun if there is one, without extra checks. That's probably best I think.

Hm. when combining clusters, maybe we just hide the singular one instead of removing it. Otherwise we don't know where that particular one was moved /to/ and have no way to track it. So, put it down, the event plays as usual, but it's invisibly still present, and we pick it up next time we try to pick up an item at that loc. That works.  # TODO

Realised I still haven't actually implemented the 'burning' yet, which was the whole point of this branch. Oops.

deleted a bunch of logs from trying to fix descriptions again, no real info here.

8.18pm
Okay. So it is correctly identifying single/plural, but the descriptions aren't updated.

noun_inst singular identifier in text
#   [[  look at glass shard  ]]
#
#   You look at the shard:
#
#      A scattering of broken glass.

Ey, fixed it.

#   [[  look at glass shard  ]]
#
#   You look at the shard:
#
#      A shard of broken glass.

Now it updates the descriptions when it sets the print name. Might be wasteful and may have to change it later but it fixes it, so I can carry on with other things.

New error:

#   go to work shed
#   Failed to run input_parser: unsupported operand type(s) for |: 'set' and 'NoneType'
#   Failed get_noun_instances: cannot access local variable 'dict_from_parser' where it is not associated with a value
#   Failed parser: cannot access local variable 'error' where it is not associated with a value

At least I already know what this one's from, will fix now.

Oh, huh.
Going from the church to the workshed gets me the error, but going straight to the work shed doesn't. Hm.

Okay, done. Just had to fix it so the no-items church didn't break things.

I godmode-d in a new glass jar, and I think it came with its own flowers.

Yup.
[<ItemInstance dried flowers / (2af695fb-69ed-4b11-8928-945c5ca1acc4) / east graveyard / None/ >, <ItemInstance dried flowers / (3e3f98d9-6961-4537-836f-6734e89d9848) / north no_place / None/ >]

#   Do you want a specific instance, or will any do?
#   Press enter to default to the first option, or enter 'loc' to choose by item location, or 'inv' to choose from inventory items.

#   Instance found for dried flowers: None

Hm.

Notes for tomorrow:
* can't pick up the flowers from a godmode added glass jar; there's one lot of flowers in no_place and another local, need to figure out which.
* Need to add find_local_item_by_name to verb_action functions, currently they all still do their old things.

Trying to figure out the best way to do get_correct_cluster_inst(noun_inst:ItemInstance, entry:dict).
I'm not sure if I want to have on its own, or  have it above find_local_by_name and call it as part of that function.

Only thing is, the cluster fn requires the input text. But that gets stored as noun.text, so I guess I can just feed that into find_local.

Going to try it out. Right now I'm doing the cluster search in get_noun_instances.  Not ideal. It's better I think to just let it pick one instance as a sample if there is one, and let the specific noun finding happen as required by the function.

10.06am 20/2/26
Hey, got it working again:

# [[  look at glass shard  ]]
# You look at the shard:
#    A shard of broken glass.

# [[  look at glass shards  ]]
# You look at the shards:
#    A scattering of broken glass.

get_correct_cluster is now inside the main noun getter. It sends noun_text through if it has it.
If I specifically need a cluster noun, I can send noun_text as noun.plural_identifier.

It prioritises multiple instances if nothing else specified.
Whether that's right or not depends, though. If it's pick_up, should prioritise 'single + not in inv' but accept plurals. If drop, should prioritise compound+ not in inv for target, but base noun should be single + in inv. I need to write this out properly.
Note: Need to change how single items are dropped, because they need to be able to be picked up. So allow hidden singles to be targets for drop/pickup.

## cluster_noun operations:
#   to pick_up:
*       mandatory: Must be not_in_inv. Allow hidden.
        prioritise single inst, accept multiple inst.
#   to drop:
        for subject (noun being dropped):
*           must be in inventory/inv container
                (Will be single because only singles are allowed in inv)
        for target:
            must be in location, not inv, allow hidden.
            prioritise multiple. Only allow single if no multiple.
#            if single: have to write a fn to make one of them into the new non-hidden compound.

Have added "priority" to fn sig, so I can specify if I need to. Noun_text somewhat shares this use, but not completely; for def look, noun_text is telling what it wants to look for, so we don't allow hidden and prioritise whatever noun_text says.

I guess really we probably prioritise single always, right? Unless noun_text overrides. Yeah. Okay, that's actually much simpler. We always prioritise single if possible. Actually I can't think of a case where we'd want to prioritise multiples, in the world where we don't destroy dropped singles. I need to set that up.

Okay, that seems to work.

So, the main functions:

`find_local_item_by_name(noun:ItemInstance=None, noun_text = None, verb=None, access_str:str=None, current_loc:cardinalInstance=None, allow_hidden=False)`

Which internally runs
`noun = get_correct_cluster_inst(noun, noun_text)`
if the noun is a cluster and noun_text is called. If no noun_text it just returns the best found via the main noun finder.

My eyes are doing that fun thing where I can't see clearly again. Goddamn.

Changed it to always get correct cluster, not only if noun_text is given, it'll just prioritise single. So noun_text is only used if called directly from a main function.

Note though - I can specify which noun I need from def move, so why do I also do it inside the move function?
Not sure which is better.

Well with 'drop', if I just say 'drop glass' it gets the target compound from the location, so it /has/ to be internal there.

Okay so, for 'drop', we get the right compound in def drop, and it finds the target itself in combine_clusters. So that works. Any named nouns we get in the verb-action fn, otherwise we get it internally. That's okay.

NOTE: combine_clusters allows for you to give a target of iteminstance type, but nothing in the function allows for that.
Ah, it can be a container. Okay. As in, 'put  glass in box', where box already has glass in it.

So I need to change

# success, shard = self.separate_cluster(inst, origin=origin, origin_type="container" if was_in_container else "location")

to pick up singles instead of always separating, as well as stopping them from being deleted afterwards, and instead making them invisible.

11.31am
Hmph.

[[  drop glass  ]]

You can't drop the broken glass shard; you aren't holding it.

And we're back here to looking at nouns that aren't near us.

Oh, I guess I didn't add the new function to def drop yet. Okay.

Also, am rerouting immediate failures (eg there is no noun present to act on) to failure printing in misc utilities.

Hmph.

Compound target: <ItemInstance broken glass shard / (234315fb-2863-4461-a7fd-10bc9aeba09c) / north inventory_place / None/ 1>. Shard: <ItemInstance broken glass shard / (234315fb-2863-4461-a7fd-10bc9aeba09c) / north inventory_place / None/ 1>

It's 'finding' the one I sent it.

12.51pm
fixed now. Dropping single into cluster adds to cluster, dropping single with no cluster drops single, picking up works.

Okay. I need to make this far cleaner. Trying to re-usilise access_str and priority is going to make it a headache, especially since there's a low degree of recursion so I have to be able to send the same commands in the round.

1.19pm
Oh, I just hit this error for the  first time:

Compound_target <ItemInstance broken glass shard / (141ce1fc-1c0f-4ee4-a5b4-38bf18f769a9) / east graveyard / None/ 0> is exhausted, removing from everywhere. compound_target.has_multiple_instances == 0 in itemReg.

So there was a cluster with three, I picked one up, but when I dropped it it found a single cluster t oadd to. And the 'compound target' it found was... in the inventory. Which should not happen.


So, we drop, run
# outcome = item_interactions.find_local_item_by_name(noun=noun, access_str="drop_subject")
to get the one we're dropping (from inv only)

Then we go through def move, and referred to combine_clusters for it to check for existing clusters.
# compound_target = find_local_item_by_name(noun=shard.name, access_str="drop_target", allow_hidden=True, current_loc=target)

And there, it goes through find_local again, which goes to get_correct_cluster again, and it loops. It's not truly recursive but I need a way to tell it 'hey, don't check clusters again, you already got delivered it'. Or maybe I just skip it. Idk. I just need to be able to pass the specificity. I think it's because it's prioritising single, but it shouldn't even have local nouns as options, so idk how it's picking it. Something's getting dropped.

It's just tricky because the call for find_local is inside of get_correct_cluster inside of get_local, which gets called from everywhere. Bleh.

Well I should at least call get_correct_cluster at the beginning, before local items gets made. Because it gets made again immediatly anyway.
Well for now I'm just passing allow_hidden and access_str directly through to compound, so I can pass them t hrough directly instead of trying to interpret.

2.47pm
Hm.

They're there, but they don't show up when I search. Not sure where I'm excluding hidden but apparently I am.
[<ItemInstance broken glass shard / (94c97bb2-bcb3-43f0-8740-465f16c4838c) / east graveyard / <eventInstance item_is_broken (27b94c6f-2819-4448-9cc5-8ff1f88661a9, event state: 0>/ 2>,
<ItemInstance broken glass shard / (0cc0b296-319c-4e9c-8a48-2ed8b2406b46) / east graveyard / None/ 0>,
<ItemInstance broken glass shard / (f2f4c617-cd59-4d0c-b46b-2d79daa0f570) / north inventory_place / None/ 1>]

but if I print local:
LOCAL ITEMS:
{<ItemInstance broken glass shard / (94c97bb2-bcb3-43f0-8740-465f16c4838c) / east graveyard / <eventInstance item_is_broken (27b94c6f-2819-4448-9cc5-8ff1f88661a9, event state: 0>/ 2>, <ItemInstance desiccated skeleton / (aa263abc-dbc5-4abe-8716-4fe85a250116) / east graveyard / None/ >, <ItemInstance moss / (6d0021d4-3a16-4854-9796-392e56a04ad1) / east graveyard / None/ 3>, <ItemInstance dried flowers / (f6007de2-0cf5-41eb-85ea-be6ffefdbbf5) / east graveyard / None/ >}

So 6b46 should show up, but doesn't.
OH i didn't add it to the location. Goddamn, okay.

Okay so now it does get added to location:
FINAL ITEMS: {<ItemInstance broken glass shard / (4c34a943-26ac-426e-9af3-5a29e590bc21) / east graveyard / <eventInstance item_is_broken (ae8b6699-32a7-4108-beea-a1d104c45be8, event state: 0>/ 3>, <ItemInstance broken glass shard / (d5758478-3af6-4f4e-9f9d-2cf69ee03c77) / east graveyard / None/ 0>, <ItemInstance desiccated skeleton / (fbcc643d-5be2-48bd-8cb0-5adbe204dc5e) / east graveyard / None/ >, <ItemInstance moss / (8c5daf29-f53f-429b-b9db-6df3a5cc771d) / east graveyard / None/ 3>, <ItemInstance dried flowers / (5abb9984-870f-43d1-9d71-12497ba1c3e7) / east graveyard / None/ >}

And it has both options when get sto choosing the right cluster.

Okay. So - partial success. cluster choosing now works properly, BUT it gets caught by run_check refusing clusters.

I fixed that, but now realised my error.
The original cluster search has to find the plural if there is one

ITEM: <ItemInstance broken glass shard / (1d9b07a6-fffe-4764-ad1a-b309a6018ba8) / north inventory_place / None/ 1>
ITEM: <ItemInstance fashion mag / (a773fc69-18a0-4681-9807-b3a1d50a9a04) / north inventory_place / None/ >
You can't drop a glass; you aren't holding one.
Hm.
Oh, probably didn't inhide when I picked it up.

3.25pm
Got it. Now you can drop/pick up the same cluster item each time.

Dropped items still drop to 0 count, and the count is added back to the cluster, but the 0 count ones are picked up first. So 'broken glass' always starts with 3 cluster parts, and the total number of glass parts from that cluster is always 3, whether they're in inventory or invisible or plain in loc. The shard/shards plural names still update properly.
Really pleased with that.

7.24pm
Back to burning things now.

##
 .-            -.
[<  look at tv  >]
 '-            -'


Hm.
Outcome: None, noun: <ItemInstance match / (1c125b4a-ad8b-41c2-8d7e-7a115f1746f3) / north no_place / None/ 12>

Okay, fixed that, ish.

values: ("top of token_role_options: Token(idx=1, text='fashion mag', kind=('noun',), canonical='fashion mag')",)
values: ("top of token_role_options: Token(idx=4, text='match', kind={'noun'}, canonical='match')",)
For some reason, 'burn fashion mag with match' skips the 'with', so the sentence breaks. 'Burn mag with match' works fine. Need to check why it adds too many omit_nexts...

I wonder if it was the addition of local_nouns that made the difference here. Because one of those would have worked, but it's not getting the correct one because it's only comparing to item defs I think.

10.02pm
Okay. Fixed again now. Omit_next is proper again, and matches and magazines work again. Really need to eat though.

12.05pm 21/2/26

[<  open matchbox  >]
You open the matchbox.

[<  close matchbox  >]
You close the matchbox.

[<  take match  >]
The match is now in your inventory.

So apparently it doesn't close things properly, because you can still get stuff out after closing them. Oops.

# Cannot process {0: {'verb': {'instance': <verbInstance use (782e8a54-0f03-43c4-bcd0-4296b07e8695)>, 'str_name': 'use', 'text': 'use'}}, 1: {'noun': {'instance': <ItemInstance iron key / (75d55d24-6899-4363-9565-27fe32cdd4de) / north inventory_place / <eventInstance reveal_iron_key (322c24cd-ee8d-4a68-be8e-8a3a2a05fa6e, event state: 2>/ >, 'str_name': 'iron key', 'text': 'iron key'}}} in def use_item() End of function, unresolved. (Function not yet written)

# Failed to find the correct function to use for <verbInstance drop (61e2f469-0742-406e-be1e-07aa128f7e67)>: eventRegistry.is_event_trigger() got multiple values for argument 'reason'

move noun-getter for 'use key on lock' to def use_item, and send noun/noun2 directly to lock_unlock.

4.25pm
"hidden_cluster=True" Should be able to be determined by verb + noun attr, right? Idk. I mean really the only time hidden is allowed (currently at least) is for clusters. So maybe 'if is_hidden and not is_cluster in item_type?'

`if item.name == noun_name and (not has_and_true(item, "is_hidden") or "is_cluster" in item.item_type)`
That should cover it, I think. I'll leave the 'is hidden' part in for now but at least until I add other hidden things it'll do. At that point I'll need a separate 'hidden_cluster' flag or something to say 'treat it as hidden but only in this context'.

Am writing another get noun fn, but this one will replae others in verb_actions:

get_correct_nouns(verb, input_dict)

runs get_nouns_w_str, then if noun, runs find_local_item_by_name for that noun/verb.

Certain cases will need the nouns gotten separately, such as 'drop' which needs different access_str whether it's the subject or target, but it works.

Added access_str, so now even those can call it. So now each verb can call for both (potential) verbs with specific access_str for each if needed. Will need to test it but seems to work.

Need to implement it across the board. Will do that today.

Also, need to fix this:
Failed to find the correct function to use for <verbInstance drop (bb32db4a-4491-4d13-8345-cfd20b41a9ca)>: eventRegistry.is_event_trigger() got multiple values for argument 'reason'

Fixed now, had forgotten to remove noun.location from is_event_trigger.


 .-                          -.
[<  take match from matchbox  >]
 '-                          -'

There's no match around here to take.

I really want to say 'you can't take anything from the matchbox, it's not open'. But the downside is explicitly revealing that the target is a container.

--
5.25pm
Okay, have got the burning half working. The 'item burns' event runs, but no renaming.
I guess with the breaking I didn't rename, I just replaced, but I suppose I made the 'broken glass' items, I don't think I actually finished the 'broken [x]' setup. Will do it now so it works with broken + burned both.


5.41pm
The issue I'm having now is that `if isinstance(reason, tuple):` in is_event_trigger sets the attribute sets the attribute immediately. So then when it gets to do_immediate_actions, it's already burned.

But I guess I should check in def burn if it's already burned, not leave it to the event... Still. Feels like a bad way of doing it. Maybe #TODO fix this later.

Oh goddamn.

(  Func:  verbReg_Reciever    )
values: ("top of token_role_options: Token(idx=2, text='fashion', kind={'noun'}, canonical='burned fashion mag')",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=2, text='fashion', kind={'noun'}, canonical='burned fashion mag') // kinds: {'noun'}",)
(  Func:  verbReg_Reciever    )
values: ("top of token_role_options: Token(idx=3, text='mag', kind={'noun'}, canonical='burned fashion mag')",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=3, text='mag', kind={'noun'}, canonical='burned fashion mag') // kinds: {'noun'}",)

We're here again. 'burned fashion magazine' takes two tokens

But specifically, this happens because I wrote 'magazine', but the actual name is 'mag'.

I guess I need to explicitly make that an alt_name, and then ensure that burned items inherent 'burned {alt_name}' to some degree. They should by default anyway.

Also, the burned magazine is /not/ burned:
 'is_burned': False,

 ??

Oh, I didn't change it from the 'broken', apparently, because
 'is_broken': True,

Also, this:
"paper": "it is torn, left a shadow of its former self.",
message is poor. Makes no sense when
#   As the mail order catalogue burns, it is torn, left a shadow of its former self.

Need to split material_msgs into generic, break, burn etc.

Also maybe I should just rename the magazines to 'magazine' instead of 'mag'. Don't know why I'm so stuck on that. Can still add 'mag' as an alt_name....

Working on ~565 in verbReg to try to deal with the 'if no sequences and noun,noun in format, just omit one'. It's only partially done.-

9.23am
Have added
  "ash pile": {
    "can_pick_up": "requires_scoop"

Everything else just has 'can_pick_up' as a bool but it feels like this makes more sense. Can just add a check to def take like I do for def burn.

Also just changed 'x mag' to 'x magazine' and gave 'mag' as an alt_name. Far easier.

********************
I need to solidify the phrasing for the break/burn/etc.

Right now I have:

"can_break": true,
"descriptions": {
    "if_broken": ""}
"is_broken": false,

(currently nicename + if_broken are just the old one with the name replaced with 'broken {name}', but that's just 'cause I've not written anything else yet.)


for burned, it's the same.

"is_burned": false,
"flammable": false,

That's not the worst of it, the worst is the series of dicts for assigning/evaluating states. That's where the work needs to happen. But first, going to just replace 'if_broken' with 'is_broken', then I can just use the state to define the description, not need some arbitrary 'if is_broken, description = is_broken'.

I think for the magazines/papers, I just need instead of doing this for each:

      "generic": "It's a puzzle magazine",
      "is_burned": "It's a burned puzzle magazine, barely legible with half the paged burned away"

Just have somewhere 'burned_magazine' with
`It's a burned [[]], barely legible with half the paged burned away`
unless I want a specific description for a particular item.

Note: If I want to add descriptions to burned, I need to make sure it doesn't overwrite the descriptions for container if present. Need to add additional container attrs/vals, not just replace 'descriptions'.

Ahh see currently it would:
    if flag not in item_dict:
        item_dict[flag] = val

Okay.
Oh, this is what I was using 'item_type_descriptions' for earlier. but that was only in edit_item_descriptions, not part of the main script.

Well, should be able to just add them to item_defaults now and have the descriptions merge without just overwriting previous. Will test.

Also, going to change

            {"if_closed": "", "if_open": ""},
        "nicenames": {
            "if_closed": None, "if_open": None},

to {generic: "", "is_open": ""}
Or no, actually. No generic in this section. Add 'generic' to 'standard', then just add `is_open` to desc/nicenames.

Also adding optional description for is_locked.
(Changing all these from 'if_x' to 'is_x' to match the attr formatting. No reason not to. It means that the base attr is is_open and the description is [description]["is_open"], and I don't think that's a problem.)

Thinking of changing 'flammable: True' to 'can_burn' to match 'can_break'.

Also adding 'requires_powered_location' to 'electronics', for things like the TV. Not that it can currently be moved, but feels like it should be there.

I also really want to fix the phrasing for
    "transition":
        {"is_transition_obj": True, "enter_location": None, "exit_to_location": None},
Aside from enter_loc and exit_to_loc not having the same structure, 'enter location' sounds like an action, not an assignment.
I was avoiding 'int_location' and 'ext_location' because what if something is a substructure, but it still makes sense I think. the mall is the ext_location of a shop in that mall.

So, changes so far:

enter_location == int_location
exit_to_location == ext_location
flammable == can_burn
if_x == is_x
"if_closed" == "generic" in "standard"

Apparently I don't use flag_actions in verb_membrane anymore? commenting it out for now to check for sure but it doesn't seem to be used anywhere. // wtf I also have the same thing in verb_actions, also unused. I guess that was earlier in the parser development?

Yeah, I have this:
get_action_flags_from_name(self, name):
in itemRegistry that isn't used either.

I could probably change item_burned to is_burned in eventRegistry too.

Oh, also 'if_singular' and 'if_plural' should be is_ as well. Just make it is_x always.

Yeah, using the 'closed' description as the generic works well. A thing that can be open/closed is always one of the two, so using generic as closed means

    elif hasattr(inst, "is_open") and not getattr(inst, "is_open") and inst.descriptions.get("if_closed"):
        description = inst.descriptions["if_closed"]
that goes way entirely, because unless it was closed, it would just stick with generic.

So, `if_open, if_closed, if_singular, if_plural` are the ones I've found so far that need changing.

# Need to update item_defs to make any 'is_closed/if_closed' description the generic instead.

Wait I added an is_closed flag?
    if (hasattr(confirmed_container, "is_closed") and getattr(confirmed_container, "is_closed")):
        reason = 1
It's inside of run_check.


# NOTE: CAN PICK UP ITEMS NOT LOCAL. At least in testing_grounds. TESTED: only in testing grounds. Things work differently there.

Have fixed the 'burned magazine' returning a big error even if 'magazine' is found because 'burned' becomes its own noun and breaks the sequencer. Have added a workaround where it simply removes the assumed_noun if the other noun is confirmed and combines their name in the token.text (so an error message will still say 'burned magazine', not the found-inst's name that you didn't type) but if you have a not-burned magazine, it does that.

Well have changed the assumed_noun's kind to adjective and set its idx to *10, but it remains a token.

Okay, and have added it to the dict. So now we get this:

dict: {
    0: {'verb': {'canonical': 'look', 'text': 'look'}},
    1: {'direction': {'canonical': 'at', 'text': 'at'}},
    20: {'adjective': {'canonical': 'assumed_noun', 'text': 'burned', 'str_name': 'burned'}},
    2: {'noun': {'canonical': 'fashion magazine', 'text': 'burned magazine'}}}

The adjective is ignored in the sequencer, and ignored by verb_actions entirely so far. But having it there means I could add it to the error message if I wanted, etc. Relatively happy with that.

Now back to the other horde of errors.


Hm. Weird inventory/opening errors.

#   [<  open jar  >] (in local area)
#
#   interactable, val, meaning:  1 0 accessible
#   You can't open the glass jar
#
#   (so i picked it up)
#
#   [<  open jar  >]
#   interactable, val, meaning:  1 5 in inventory
#   You can't open the glass jar

Fixed that now.

Now an event error:

Picking up the moss. All three start their events.
Red moss first, then blue, then cyan.

But when you drop the moss - red moss doesn't print the trigger messages I'd expect. Investigating.

---------

So I dropped three mosses, all of which started events.

This time, two of them printed this:

Noun moss is an event trigger for <eventInstance moss_dries (b3bf4e01-629e-419d-beb8-37516e4fdc67, event state: 1>
After if trig.is_item_trigger and trig.item_inst == noun:
You put down the still-damp moss.

but one printed

Noun moss is an event trigger for <eventInstance moss_dries (54b21e2b-074c-4d56-a5e8-52422d4e94bf, event state: 1>
You put down the still-damp moss.

Red moss failed this:
    if noun_inst.event and hasattr(noun_inst, "is_event_key") and noun_inst.is_event_key:
        print(f"Noun {noun_inst.name} is an event trigger for {noun_inst.event}")
But it went through this process just like the others:
#   generate events from itemname: moss / moss_dries
#   Reason item is in this check? item_in_inv
#   INTAKE EVENT:
#   {'name': 'moss_dries', etc}

It seems random; sometimes they all have the right print, sometimes only two, and the order is random. But they do all print the end event message. So maybe it's that terminal error where it skips lines, not an actual logic error.
Adding a temporary print for event state after it runs.

Oh, they all had the event removed so event.state errored. Well that's good.

Oh it probably doesn't remove the /event itself though, does it. So they'll all be floating around. Should deal with that.

But at least it confirms they were all processed.

Oh, no, the event is removed entirely. Okay, good

 .-           -.
[<  take moss  >]
 '-           -'

INST is_hidden in run_check.
Sorry, you can't take a moss right now.

Oh I forgot to compensate for that, oops. Easy fix though.

Hm. So this is odd.

[<ItemInstance moss / (aa20a404-fb25-4733-b608-d51175cc0a96) / east graveyard / None/ 1>, <ItemInstance moss / (63ccb5b3-2915-445a-9a4f-637b98ddbd20) / east graveyard / None/ 0>, <ItemInstance moss / (bcf03142-2441-4186-af9d-b172e25fdbc5) / east graveyard / None/ 2>]

This moss was dropped, but didn't become part of the compound. That's very odd...

Hm. No idea why that was happening, but it seems to be fixed now:
[<ItemInstance moss / (0792773e-8c8b-4889-921c-8e094975222e) / east graveyard / None/ 0>, <ItemInstance moss / (a4007fb9-17b1-475c-a568-86b3d445acbb) / east graveyard / None/ 0>, <ItemInstance moss / (7d02f6f5-69b8-4d70-a9e1-1ab834f7f069) / east graveyard / None/ 3>]

Very odd.


---------
12.29pm
Hm. The 'maintain timed event after item dropped if conditions met' is not working.

 .-           -.
[<  drop moss  >]
 '-           -'

Noun moss is an event trigger for <eventInstance moss_dries (10eae62a-5adf-43df-87e3-69e926d75a45, event state: 1>
You put the still-damp moss down in a nice dry spot.


 .-           -.
[<  drop moss  >]
 '-           -'

You can't drop a moss; you aren't holding one.


 .-           -.
[<  take moss  >]
 '-           -'

generate events from itemname: moss / moss_dries
Reason item is in this check? item_in_inv
intake_event.triggered_by: ['item_in_inv']
You pick up the moss, and feel it squish a little between your fingers.

The dropped moss was magenta. The moss picked up was blue, and it started a new event.

So, the existing event/noun:

These are the moss clumps after a pick up/put down cycle:
[<ItemInstance moss / (4c9f7bb0-5f61-44fc-b15c-dc1b95275a05) / east graveyard / None/ 0>, <ItemInstance moss / (133e7319-3095-4b7f-beb0-65adf1b392eb) / east graveyard / None/ 0>, <ItemInstance moss / (418d3934-8c69-42e7-a603-0c408390dc96) / east graveyard / None/ 3>]
That's all correct.

But, if I pick one up:

[<ItemInstance moss / (4c9f7bb0-5f61-44fc-b15c-dc1b95275a05) / north inventory_place / <eventInstance moss_dries (049f7b79-279e-4c2a-901f-703187c2abf3, event state: 1>/ 1>, <ItemInstance moss / (133e7319-3095-4b7f-beb0-65adf1b392eb) / east graveyard / None/ 0>,
<ItemInstance moss / (418d3934-8c69-42e7-a603-0c408390dc96) / east graveyard / None/ 2>]

Oh, it's right. Okay.

Well then I go to shed with two mosses:

... Or I would, but:

 .-            -.
[<  go to shed  >]
 '-            -'

Failed to find the correct function to use for <verbInstance go (19b6dc16-594b-44e9-92e1-c73679ff3e8b)>: maximum recursion depth exceeded

Ah. Because 'go' sends to enter, and enter sends to go.

Hm.
Fixed the recursion, but now I have the issue of two separate paths for 'go to shed'. Either it picked the noun, and then we deal with transition objs etc, or it picked the location, and we just go directly there.

Hm.
Why does it not have transition objects...

{'id': '104bf9f9-3666-4fac-84d2-b76132e15ee5', 'material_type': 'generic', 'on_break': 'broken [[item_name]]', 'can_break': False, 'can_examine': False, 'descriptions': {'generic': 'a simple shed, with wood panelled walls and a simple wooden door.'}, 'has_door': False, 'is_loc_exterior': True, 'is_vertical_surface': True, 'item_type': {'wall', 'static', 'loc_exterior'}, 'nicenames': {'generic': 'a work shed'}, 'slice_attack': 5, 'slice_defence': 5, 'smash_attack': 5, 'smash_defence': 5, 'transition_objs': None, 'description': 'a simple shed, with wood panelled walls and a simple wooden door.', 'starting_location': <cardinalInstance west graveyard (af785dad-c352-4875-978a-706d2110b4a7)>, 'name': 'work shed', 'print_name': 'work shed', 'nicename': 'a work shed', 'is_transition_obj': False, 'colour': 'cyan', 'verb_actions': set(), 'location': <cardinalInstance west graveyard (af785dad-c352-4875-978a-706d2110b4a7)>, 'event': None, 'is_event_key': False, 'alt_names': None}

this is confusing. Didn't expect to spend so long on this.

Honestly considering removing the item-named-shed and just keeping it as descriptions. I can always add 'shed wall' etc if I need it later.

Ugh that's going to take the rest of the day. Probably needs it though. It was always a bit silly.

2.22pm
Tried it, then realised the error was because I never finished updating ext_location and rolled it back.

Now:
transition_objs': None
Why does work shed (noun) not have instance objs?
Oh we put them on the location, don't we, not the noun inst.
It makes no sense to have
'transition_objs': None,
on the work shed noun obj tho when half the time that's what gets pulled. Should apply it to both. It's a static state so it's not like I need to track the changes.
TODO: Add transition_objs to is_loc_exterior noun inst as well as the location.

2.27pm
But randomly I still get this:

format: ('verb', 'direction', 'location')
 .-                 -.
[<  go to work shed  >]
 '-                 -'

def go len2 or len3
No noun.
Failed to find the correct function to use for <verbInstance go (68b48fa1-e6d7-4fbe-897d-622828d25935)>: 'cardinal'

I don't know why it works most of the time and then just breaks.

format: ('verb', 'location')
 .-            -.
[<  enter shed  >]
 '-            -'

It would go to 'go' here but it recurses.
Still.

Okay so the reason it's broken is because at some point I changed it so transition_objs were on the cardinal, not the place obj. Which is a suitable improvement, but I didn't update initialise_placeRegistry.

#   if hasattr(place, "transition_objs"):
#       for item in place.transition_objs:


Well, changing transition_objs back to a set, because there's literally no reason to have it be a dict to store the location of the item, whe the item carries it and that item is being carried /by the cardinal/.

Getting rid of exit_to_item and entry_item.

Okay so currently, the cardinal has a set of transition_objs.

the /place/ has transition_objs[item][int_location] and [ext_location]

Huh, this is interesting.

When 'shed' is a location:

nuon has ext_location: <cardinalInstance west graveyard (a224c2e2-a73b-4bd0-bf96-fa63ac5ebdac)> and int_location: <cardinalInstance north work shed (a4c91cd5-9ee4-40fa-a9b3-ec74eb9ef6a2)>
You can't enter through a closed door.

Think it's fixed now. Seems it. 5.59pm
Added 'door_opens to itemReg, want to use more random-from-a-list descriptions. Not today though.

I think trans_nouns etc should work better now.


Hm.
Was in testing grounds.
Said go to graveyard.
And because graveyard hasattr location_entry it was directed through entry.

[<  go to graveyard  >]
move_through_trans_obj
You're now in the testing grounds, facing north.

So I need to check. If current loc == int_loc or to_loc == int_loc, an same for ext. If there's not a connection, we don't do it. This is going from 'random place to location that happens to have a door on it going somewhere else', we don't use the door for that. Shed is different because it's internal and behind the door. Need to formalise that.

22.13pm
Okay, so 'go to work shed' should absolutely go inside if I've been there already and it's open. Otherwise it's just frustrating.


9.22am 23/2/26

'take moss' is sometimes putting things down.
Picked up three moss, went to shed, drop [purple] moss, take [cyan] moss, drop [cyan] moss, drop [red] moss, all good.

Then I 'take moss', but
"You put down the still-damp moss." and the event was ended, which is wrong on two fronts - one, I already put the red moss down. Two, it shouldn't have ended the moss. I'm inside, and the previous time I put the red down moss it gave the proper "You put the still-damp moss down in a nice dry spot." exception print.

It's the same moss.

I think maybe what happened is that it chose a moss already on the ground for pickup which is correct, but then it ended the event as if I had put it down outside.

![drop_moss_take_moss_error](image.png)

Okay, so:

It looks like the moss wasn't actually dropped in the second case when it was meant to take it, just the event said so. The event message was just lying.

I'm going to change the reprs for events/nouns for a min so I can compare ID numbers more easily.

Changed and added some more colours to make it easier to see what's going on.

Issue 1:
'outcome' for 'take' often pics items that are in the inventory, which it shouldn't do. // fixed already

Issue 2:
Drop moss e4f4 in shed.
immediately pick up:
it finds e4f4, but the intake event is still triggered and it generates c2e1.

10.14am
I think the issue with the moss is the various paths through is_event_trigger. On the second pickup, the moss is triggering noun.event, on the first time it's triggering generate_from_name.

Oh, I think the trigger is only triggering on 'not in inv'. So because I've picked up the moss, the exception doesn't trigger. But the trigger shouldn't be triggering at all. But at least I should be able to fix it now.

OH it's triggering the timed trigger.
Weirdly, this:
{<triggerInstance 2ea897b2-554c-4c85-a0e6-77a3f4b90dc9 for event moss_dries, event state: current/ongoing, Trigger item: moss>
doesn't have the trigger item. Oh nvm, it was just a repr formatting thing.

10.35
Anyway. I think it's because it doesn't check if a trigger is start_ or end_trigger. So it just goes 'ah, this thing being in inventory is an event trigger', doesn't find an exception because the exception only applies when putting it down, and so the event ends. Was just not an issue before because picking things down always ended events.

On the upside it does keep the right number of total mosses. It just needs to pick up the existing ones instead of generating new if existing exists.

Fixed the issue where it ended because it had a timed trigger; it now has a slight diversion for those. It didn't trigger before because I'd change the verbiage.

----
11.39am
The issue was can_take finding a different noun. Fixing.

12.04pm
Oh, it was twofold: can_take was looking up nouns again and often picking the wrong one, but move is also generating a new one. I assume it's because if you put down a thing in a new place, it has a no-0 value which it doesn't count as a singleton.

-- deleted a bunch here because I was looking at event id and not noun id. I am too tired --


It finds one, the one it should take. After first can_take finds the one in ny inventory, which is already a problem. But then the event generates a brand one one and adds that to my inventory.

It does at least remove the old moss from my inventory, but still. Broken.

Now def take finds inventory items when it shouldn't. Bleh.

in_inv_children = ["local_and_inv_containers_only"] isn't being applied properly.

Ahh. I didn't have it set to apply if there were children.

So if no children, then it kept the full inventory. If there were children then it would apply properly. Seems fixed now.

So, for commands ["go east", "take moss", "take moss", "take moss", "go to shed", "enter shed", "drop moss", "take moss", "drop moss", "drop moss", "take moss"]

take red 3
receive cyan 1

take red2
receive magenta 1

take red1
receive red 1

Go to shed

drop red1

take red1, event continues

drop red1 event continues (assume this continues)

drop cyan 1

take cyan 0 from red2

drop cyan moss 1

drop magenta moss 1

take moss -- oh, finally found an error:

[OUTCOME from def take: `<ItemInst moss / (a2d4541bb663) / north work shed / moss_dries / ..ac6c77bb96f2 / 1>`]
hidden inst multiple instance count: 1
INST is_hidden in run_check; not a singleton multiple_instances.
Sorry, you can't take a moss right now. # Note: This line is referencing red moss.
After first can_take: None // original noun: <ItemInst moss / (a2d4541bb663) / north work shed / moss_dries / ..ac6c77bb96f2 / 1>

So there should have been 2 mosses on the ground, but instead I have a 1.

<ItemInst moss / (a2d4541bb663) / north work shed / moss_dries / ..ac6c77bb96f2 / 1>,
<ItemInst moss / (31af99158ed4) / north work shed / moss_dries / ..bd1ee7a8603b / 2>,
<ItemInst moss / (67e49433f020) / north work shed / moss_dries / ..870737c12b84 / 0>

663 is cyan.
ed4 is red
020 is magenta

So for some reason, the last time I dropped cyan it didn't merge with red. But magenta did, properly removing the compound count and invisibling.

See this run-through it worked properly.

Tested, every few runs it doesn't properly merge. Need to figure out why. At least the triggers are working properly.

12.55pm
Oh, this is odd.
Compound target: <ItemInst moss / (2e5adaa2be23) / north work shed / moss_dries / ..4bf5154b26df / 1> // shard: <ItemInst moss / (bec23d031e24) / north inventory_place / moss_dries / ..66b39f71f17f / 1>

AT END OF COMBINE_CLUSTERS: Compound_target: <ItemInst moss / (2e5adaa2be23) / north work shed / moss_dries / ..4bf5154b26df / 2> // shard: <ItemInst moss / (bec23d031e24) / north work shed / moss_dries / ..66b39f71f17f / 0>

So, e23 becomes cluster, e24 is singleton. All good.

But, then I drop blue (9f1):
Compound target: <ItemInst moss / (bec23d031e24) / north work shed / moss_dries / ..66b39f71f17f / 0> // shard: <ItemInst moss / (2afaa4bdea24) / north inventory_place / moss_dries / ..2b183a3129f1 / 1>
AT END OF COMBINE_CLUSTERS: Compound_target: <ItemInst moss / (bec23d031e24) / north work shed / moss_dries / ..66b39f71f17f / 1> // shard: <ItemInst moss / (2afaa4bdea24) / north work shed / moss_dries / ..2b183a3129f1 / 0>

It finds e24 as compound instead of e23, so I end up with the previous-0 at 1, and the previous-2 still at 2.

Okay, so the issue is here:

[OUTCOME from def take: `<ItemInst moss / (65380ca8732d) / north work shed / moss_dries / ..0d522625fd50 / 2>`]
is_cluster in item_type, going to move_cluster_item
AT END OF SEPARATE_CLUSTERS: Compound_target: <ItemInst moss / (65380ca8732d) / north work shed / moss_dries / ..0d522625fd50 / 1> // shard: <ItemInst moss / (bd09b9b8e42b) / north inventory_place / None / 1>

Outcome after move_items: <ItemInst moss / (bd09b9b8e42b) / north inventory_place / None / 1>

But, I just dropped
 <ItemInst moss / (97639afd81aa) / north work shed / moss_dries / ..803cac5bd310 / 0>

 So it took from the compound instead of taking the invisible singleton.

Okay, so sometimes it says no compound target if dropping a 1 onto a 1.

So it seems to be working now. But it was so inconsistent it's honestly hard to tell. But i have it doing an extra loop now so it only picks up an item >0 if there's no items with 0 present, and if you're dropping an item and the incoming noun is in inventory it just uses that and skips the correct_cluster bit.

Okay, improved a little again. It was the plural_id that was making it fail to pick the right moss, so now it ignores plural_id if priority == plural or if there are no other options. Otherwise it was just picking the first option in local_clusters, that's why it was random.
 There's a lot of wasteful code but it'll do for now.

I think this is why:

Not new noun: [<ItemInst moss / (186626d3fb85) / north work shed / moss_dries / ..75b49a38b221 / 0>, <ItemInst moss / (0b6e9b000e9b) / north work shed / moss_dries / ..b9c31e46bbb9 / 3>]
AT END OF SEPARATE_CLUSTERS: Compound_target: <ItemInst moss / (186626d3fb85) / north inventory_place / moss_dries / ..75b49a38b221 / 1> // shard: <ItemInst moss / (186626d3fb85) / north inventory_place / moss_dries / ..75b49a38b221 / 1>

it fails to get the plural.

Oh, now this is the inverse:

[OUTCOME from def take: `<ItemInst moss / (22f1e0ae1ce9) / north work shed / moss_dries / ..e3d511f78ef2 / 0>`]
Going to move_item for <ItemInst moss / (22f1e0ae1ce9) / north work shed / moss_dries / ..e3d511f78ef2 / 0>

allow_hidden:  False // access_str: pick_up // noun_text: moss
Adding to plurals: <ItemInst moss / (208ca72d46ff) / north work shed / moss_dries / ..e8b87096d989 / 3>
Not new noun: [<ItemInst moss / (22f1e0ae1ce9) / north work shed / moss_dries / ..e3d511f78ef2 / 0>, <ItemInst moss / (57457e231976) / north work shed / moss_dries / ..1c869ff6ecb9 / 0>, <ItemInst moss / (208ca72d46ff) / north work shed / moss_dries / ..e8b87096d989 / 3>]
AT END OF SEPARATE_CLUSTERS: Compound_target: <ItemInst moss / (22f1e0ae1ce9) / north inventory_place / moss_dries / ..e3d511f78ef2 / 1> // shard: <ItemInst moss / (22f1e0ae1ce9) / north inventory_place / moss_dries / ..e3d511f78ef2 / 1>

Outcome after move_items: <ItemInst moss / (22f1e0ae1ce9) / north inventory_place / moss_dries / ..e3d511f78ef2 / 1>
After first can_take: <ItemInst moss / (22f1e0ae1ce9) / north inventory_place / moss_dries / ..e3d511f78ef2 / 1> // original noun: <ItemInst moss / (22f1e0ae1ce9) / north inventory_place / moss_dries / ..e3d511f78ef2 / 1>
ADDED TO INV: <ItemInst moss / (22f1e0ae1ce9) / north inventory_place / moss_dries / ..e3d511f78ef2 / 1>, noun: <ItemInst moss / (22f1e0ae1ce9) / north inventory_place / moss_dries / ..e3d511f78ef2 / 1>
noun going tyo trigger check: <ItemInst moss / (22f1e0ae1ce9) / north inventory_place / moss_dries / ..e3d511f78ef2 / 1>
Noun <ItemInst moss / (22f1e0ae1ce9) / north inventory_place / moss_dries / ..e3d511f78ef2 / 1> is an event trigger for <eventInst moss_dries ..e3d511f78ef2>
After if trig.is_item_trigger and trig.item_inst == noun:
The moss is now in your inventory.


 .-           -.
[<  drop moss  >]
 '-           -'

allow_hidden:  True // access_str: drop_target // noun_text: moss
Adding to plurals: <ItemInst moss / (208ca72d46ff) / north work shed / moss_dries / ..e8b87096d989 / 3>
priority == plural. plurals: {<ItemInst moss / (208ca72d46ff) / north work shed / moss_dries / ..e8b87096d989 / 3>}
Compound target: <ItemInst moss / (208ca72d46ff) / north work shed / moss_dries / ..e8b87096d989 / 3> // shard: <ItemInst moss / (22f1e0ae1ce9) / north inventory_place / moss_dries / ..e3d511f78ef2 / 1>
AT END OF COMBINE_CLUSTERS: Compound_target: <ItemInst moss / (208ca72d46ff) / north work shed / moss_dries / ..e8b87096d989 / 4> // shard: <ItemInst moss / (22f1e0ae1ce9) / north work shed / moss_dries / ..e3d511f78ef2 / 0>

For the first time ever, conceptually infinite moss.

17.28pm
Not sure how that actually happened but I did some more reinforcing and haven't seen it happen again.
Also fixed and reformatted the inventory slightly, just a little prettier and getting rid of needless ties to old script parts.

6.18.pm
I want to add a line when travelling from outside the graveyard to the shed. 'You travel back to the graveyard and through the gates, and west until you return to the shed.' #TODO.

Right now just clearing out old functions etc that aren't used anymore. Hoping not to break things.

Ooh - "look in jar" breaks it and gets me an instant exit. Interesting.
Specifically, if the jar is in the inventory. If not in inventory, then no error.

6.28pm fixed

Minor issue:

 .-            -.
[<  go to shed  >]
 '-            -'

def go len2 or len3. Format tuple: ('verb', 'direction', 'noun'), dict: {0: {'verb': {'instance': <verbInstance go (8b04e88b-f122-4fc6-bcc5-0fa8ab881fe5)>, 'str_name': 'go', 'text': 'go'}}, 1: {'direction': {'instance': None, 'str_name': 'to', 'text': 'to'}}, 2: {'noun': {'instance': <ItemInst work shed / (0bc140890a6a) / west graveyard / None / >, 'str_name': 'work shed', 'text': 'shed'}}}
noun transition
You see the closed wooden door in front of you; you can't phase through a closed door.


 .-              -.
[<  look at door  >]
 '-              -'

You can't see the door right now.

'go to shed' apparently didn't actually move me. Need to fix that.

"go to graveyard" >> "You're already in work shed".
I need to rework transitional objects again. Damn.

Added a specific check for 'if leaving words + already inside + destination != inside. Seems to work okay but given how often it breaks I don't want to speak too soon again.

Hm.

 .-            -.
[<  go to shed  >]
 '-            -'

You see the closed wooden door in front of you; you can't phase through a closed door.

 .-            -.
[<  enter shed  >]
 '-            -'

The door creaks, but allows you to head inside.

You're now in the work shed, facing north.

The work shed is simple structure, with a dusty window in one wall over a cluttered desk. On the desk, there's a yellowed local map showing the region surrounding the graveyard, and a pair of secateurs.

But, then if I look at the door, it's still closed. So it's printing the entrance text but not actually opening the door.

Fixed now.

3.55pm
Hm.

Enter shed plays the proper message. But 'leave shed' doesn't. You move, but it doesn't respect the door being open/not.

4.10
It's because it's failing the if and ending up in def turn, avoiding the new_relocate clauses. Okay. So that's another issue, which is good to know. 'turn around' should never be called if we're changing loc.place.

Okay. So I think I need to break down move_through_trans_obj.

First, we establish target location. We can hardcode behaviours for 'enter location/leave location'.

And really I need to break the function up so 'check the door is open' is a defined throughpoint of any travel to internal locations. Hell, maybe put it in turn/relocate directly.


Okay. So, 'leave shed' is verb_noun
leave_shed works properly; if you try to leave again, it tells you you're already outside. But enter works like a toggle, and you just enter/leave repeatedly with every 'enter shed' command.

Okay it seems more fixed now. go to shed/enter shed/leave shed all seem to work as you'd expect. The fn could still do with some more cleanup as it's a real mess.

5.14pm
Hm.
'leave shed' makes you face west graveyard. 'go to graveyard' makes you face north graveyard.

Oh, it's because 'leave x' is dependent (often) on the noun?

Yeah that was it. Okay so now, both options send you north, so 'leave shed' just sends you to 'graveyard' which then defaults to north.

Buuuuut that's still not exactly right. It should probably specify the opposite of the current cardinal, no?

Right now, any time you give just location with no cardinal, it uses your current cardinal and just applies it to the new location, or finds an alternative if the new loc doesn't have that card. Which works in general, but when leaving an interior, you really should be either facing that door again as if you left and immediately looked at it, or the opposing cardinal (so you leave a door in the west, and arrive at the east).

Okay. Once again, it seems to be working better. If you're not right at the shed an the door is shut and you've not been inside before, it stops you at the door. Thereafter if you enter/leave again, it no longer requires you to manually open the door, but plays the door opening text automatically and opens the door for you.

5.55pm
Oh, I should add 'go outside'/'go inside', for when you're at a transitional object loc.

Also, 'look at shed' should move you to the shed location. Well, not 'shed' specifically, but external location nouns.

8.33pm
New one:
unlock padlock with key fails with no proper error because the iron key is still in the shed.

Oh, interesting:
'enter map' goes through to def find, and responds with
`There's a local map at northern work shed, is that what you were looking for?`.


---
move_through_trans_obj, noun: <ItemInst wooden door / (efb3a9e95fdc) / west graveyard / None / >
VERB: enter // location: None // noun: <ItemInst wooden door / (efb3a9e95fdc) / west graveyard / None / >
NOUN for move_through_trans_obj: <ItemInst wooden door / (efb3a9e95fdc) / west graveyard / None / >. is_open: True, leaving_words: ('leave', 'depart', 'exit')
Failed to find the correct function to use for <verbInstance enter (93228f87-2a89-43c9-b5e9-372413d52c50)>: 'cardinalInstance' object has no attribute 'visited'
---

[[  unlock padlock with eky  ]]

There's no padlock around here to unlock the eky with.

The order of the nouns here is wrong in failure printing.

---

I think 'enter shed' should only work if you're in the same location.place. 'Go to shed' should take you to the external, unless you're in the same place in which case it depends on whether the door is open or not. 'Enter shed' from the Church.place should fail with 'there's no shed around here'.

I need to make more use of this:

get_transition_noun(noun, format_tuple, input_dict, take_first=False):

Need to test, how does just typing 'shed' get directed?

Oh - I can't flip the cardinals when going in. Entering the internal has to go to int_location. Inverting gets messy.

Also,

This <cardinalInstance south work shed (c40eb052-ccaa-41ee-972c-4c1bdae092a3)> is not a viable direction for <placeInstance work shed (55c8843f-ece6-474e-b575-2495c2d40bc1)>
There's not much else to see around here. Dusty and largely disused, nothing really catches your eye.
new_card_inst: <cardinalInstance north work shed (df431bbd-ddfa-4e26-893b-98c2a7f84d13)>
There's not much else to see around here. Dusty and largely disused, nothing really catches your eye.

That message shouldn't print twice. And we should still arrive somewhere. Because while yes, we arrive at south work shed which isn't a legit destination, should have moved us to a legit destination instead. But despite it giving a new_card_inst, when the next command 'leave shed' runs, it says we're already outside.

Changed 'ItemInstance' to 'itemInstance' so it matches the rest of the instance classes.

8.24am 25/2/26
Another issue with word ordering:

 .-                        -.
[<  put paperclip into jar  >]
 '-                        -'

glass jar is already in <ItemInst paperclip / (c0276eaf270c) / north no_place / None / >

1: reversed from input intention.
2: Not even accurate, the paperclip is the thing in the jar, as one would expect.

Okay, easy fix, I'd just mixed it around in def put.

Today's thing:
I want to implement 'use key to unlock padlock' type order switching. Going to commit everything from the last few days to main first though.

I need to set up a better test setup. Right now, I have everyting, which is useful for specific tests but not most, and Testing Grounds, but that seems to break things in weird ways.

8.42am
Hm. This is unexpected.

 .-            -.
[<  enter shed  >]
 '-            -'

Failed to find the correct function to use for <verbInstance enter (204b0530-137a-48cb-94fe-ef3f78b9d554)>: cannot access local variable 'noun_str' where it is not associated with a value

Also,

 .-            -.
[<  go to shed  >]
 '-            -'

You see the closed wooden door in front of you; you can't phase through a closed door.

-- it should be printing the location description, not just stopping at the door. How the hell did this break?

Ah, right. Because it's passing the door to move_through_trans_obj, so if not noun isn't passed.

What the hell has changed????? 'Go to shed' now directs me outside and describes the /door/, not the shed. After fixing the logic error, now while standing /at the shed/, it gives me 'There's no shed here to enter.'.

Okay why the hell is this:

            if loc.current.place == outside_location.place or verb == "go":
                print("loc current place == outside loc place or verb == go")

not triggering.

Ooooh. Okay. So the error is not exactly what I thought. The `You see the closed wooden door in front of you` was correct, it's 'go to shed' that errored.

I set the game to start in testing grounds.

`verb in entry_words and no location or location == inside location`
`current.place: <placeInstance testing grounds (2ed41085-4743-40d4-b63b-9b863b3f33cf)>, outside_location.place: <placeInstance graveyard (a435daab-6b2f-479e-a2c9-1efb50340127)>`
`loc current place == outside loc place or verb == go. Print current.place: <placeInstance testing grounds (2ed41085-4743-40d4-b63b-9b863b3f33cf)>, outside_location.place: <placeInstance graveyard (a435daab-6b2f-479e-a2c9-1efb50340127)>
You see the closed wooden door in front of you; you can't phase through a closed door.`

So the actual issue is that it described the door being closed as if you moved there, but it didn't actually move player to the shed location.

8.59am Okay, re-fixed I think. I hadn't added new_relocate if the door was closed, now it does new_relocate to noun.location, so you arrive at the correct cardinal.

Ooh, good to find:
[<  go north graveyard  >]

Failed to find the correct function to use for <verbInstance go (efb78887-73fe-422d-91e9-36652ca7e5a7)>: 'NoneType' object is not subscriptable

Omitting the dir kills it. Will fix.
Okay, fixed. Was missing a check for direction_entry existing at all.

Ooooh dammit.
[[  use key on padlock  ]]

There's no iron key around here to use the padlock with.

I don't have the iron key, it shouldn't be naming it.

Oh wait it's slightly weirder. The iron key is local, because I'm actually in the shed. But it's invisible, I've not picked up the map yet.

Okay, better:

[[  use key on padlock  ]]

There's no padlock around here to use a key with.

10.20am

Hey it works~~

[[  use key to unlock padlock  ]]

There's no padlock around here to use a key with.

Needs more extensive testing, but manually rejigging the tokens seems to have done the job. Need to test for edge cases because it's probably weaker than it looks, but seems to work.

Now the downside to the way it's done (assuming it works more broadly in further testing) is that it permanently changes the tokens; the original data is simply gone. So it needs to be absolutely sure to work, I can't just loop it to a different verb_actions fn.

Okay, it properly works:

#   [<  use key to unlock padlock  >]

#   lock_unlock: noun, noun_str, noun2, noun2_str:  <ItemInst iron key / (3e6121345430) / north inventory_place / reveal_iron_key / ..6cd2069de13c / > key <ItemInst padlock / (54839ef394fa) / north graveyard / graveyard_gate_opens / ..9d5eca0e93db / > padlock
#   Format is len 4: ('verb', 'noun', 'sem', 'noun')
#   <ItemInst iron key / (3e6121345430) / north inventory_place / reveal_iron_key / ..6cd2069de13c / > and <ItemInst padlock / (54839ef394fa) / north graveyard / graveyard_gate_opens / ..9d5eca0e93db / > are both accessible.
#   KEY: <ItemInst iron key / (3e6121345430) / north inventory_place / reveal_iron_key / ..6cd2069de13c / >, LOCK: <ItemInst padlock / (54839ef394fa) / north graveyard / graveyard_gate_opens / ..9d5eca0e93db / >
#   You use the iron key to unlock the padlock
#   Noun <ItemInst padlock / (54839ef394fa) / north graveyard / graveyard_gate_opens / ..9d5eca0e93db / > is an event trigger for <eventInst graveyard_gate_opens ..9d5eca0e93db>

#   As the padlock falls to the ground and the chain unravells, the graveyard gate creaks open.

#   You see beyond the threshold of the graveyard, a variety of locations to explore.
#
#       [Look at your map to see where else you can go.]


Hm.

[[  unlock padlock with key  ]]

There's no padlock around here to unlock a key with.

Okay:
[[  unlock padlock with key  ]]

There's no key around here to unlock a padlock with.


[[  use key to unlock padlock  ]]

There's no key around here to unlock a padlock with.

So now it works the same way when it errors. Now to test if it works the same way when it works.

Yeah, it does. Goodgood.

11.31am
I think I want to change it to not pre-setting the colour for nouns.

Okay, changed it. Now it gets the colour when the item is encountered or loaded for location description. Also, changed it so it only runs init_loc_description for the current cardinal if you're at loc.current.place, instead of the full location.

[neatened_the_input_decoration](image-1.png)

12.46pm
I need to clean the print lines again.

After the intro text prints, it adds a line. But if you print that same text again later, it doesn't print a line.

Okay. Think it's cleaned up now. Always adds 2 newlines before input str, and prints the fancy input_str on the same line (unless decorations are on).

9.01am
Going to work on the time passage now to properly implement timed triggers. Currently time passage doesn't happen at all so it's not implemented beyond a print line, let alone testable.
