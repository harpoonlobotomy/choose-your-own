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
[[  go east  ]]

You turn to face the east graveyard

You see a variety of headstones, most quite worn, and decorated by clumps of moss, and a glass jar being used as a vase in front of one of the headstones, with some dried flowers left long ago.

[[  look around  ]]


You're in a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east sit a variety of headstones, to the south stands a mausoleum, and to the west is what looks like a work shed of some kind.

'look around' has an extra newline. Need to fix that.
I wouldn't mind adding another newline before the input print though. It's a bit claustrophobic.

Hm. the newlines overall are inconsistent.

#   [[  take padlock  ]]
#
#   The padlock is now in your inventory.
#
#
#   [[  look at door  ]]
---
#   [[  find carved stick  ]]
#
#   There's no carved stick around here to find.
#
#
#   [[  take carved stick  ]]
#
#   There's no carved stick around here to take.
#
#   [[  go to east graveyard  ]]
---
#   [[  go east  ]]
#
#   You turn to face the east city hotel room
#
#   Against the wall is a large television, sitting between two large windows overlooking the city.
#
#   [[  look at tv  ]]
#
#   You look at the tv set:
#
#      A decent looking TV set, probably a few years old but appears to be well kept. Currently turned off. This model has a built-in DVD player.
#
#   [[  go to tree  ]]

Need to work on that. Really just need to define the surrounding newlines in def router and not touch them otherwise. Well router and the failure print. Those are the two terminal points for any command.

#   [[  take matchbox  ]]
#
#   The matchbox is now in your inventory.
#
#
#   [[  burn magazine with matchbox  ]]
#
#   There's no magazine around here to burn the matchbox with.
#
#   [[  go to north testing grounds  ]]

So is it 'the following one succeeded' that does it?

I think so. It was the extra \n in print_failure_message.

Also:
[[  take dried flowers  ]]

dried flowers is already in your inventory.
vs
Dried flowers fall from the broken glass jar.

Need to add caps to the 'already in inventory' print.

