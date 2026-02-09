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
