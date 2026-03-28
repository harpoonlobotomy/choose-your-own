10.28am, 6/3/26

# Working on the 'put battery in device'/'take battery from device' verb_actions sections.

Current issues:
* If other batteries are present, is functionally random which it picks. So if you say 'take battery from watch' (and watch has a battery in it), it could work, or it could pick another unrelated battery and say 'the battery isn't in the watch'. It does this check for containers, need a similar thing for batteries.
* Functionally, the battery_check is doing far more than it was ever meant to. It's just meant to be checking if battery == a potential battery and device uses batteries (or either/or depending on verb/inputs). It's not fit for purpose for the rest of it. will set up something proper.


"""
        if noun2 and not container:
            if hasattr(noun2, "has_batteries") and not isinstance(noun2.has_batteries, bool):
                noun = noun2.has_batteries
                container = noun2
                _, noun_reason, _ = registry.run_check(noun)



                print(f"Noun reason: {noun_reason} // container.has_batteries: {container.has_batteries}")
                """

I need to write a proper glossary of expected formats/grammar usage. That sounds like a nightmare but I think I need one.

Thought: It's going to be a nightmare if I have a container that also takes batteries. I guess 'use x with y' would prioritise battery-usage over parentage, so 'put' should prioritise parentage. For 'take' though. Hm.

I guess if we have a perfect-name match for either if both options exist, go with that, otherwise prioritise... well, parentage I suppose. Will think on it.

10.52am
Eh maybe I should go the other way and make the battery_check more functional instead of less, just with more direction. It can't share most of the container fns anyway. Maybe better to make battery_check a complete 'give me potential battery + device and I'll figure it out for you' type fn instead of just a check.

11:09 Eugh.
Just found a new issue that isn't actually new, I'd just forgotten.
if I have 'watch' and 'watch battery', I can pick up the battery by just calling it 'battery'. But, if I have watch, battery and watch battery, 'pick up watch battery' gives me verb dir noun noun, counting 'watch battery' as individuals.
I thought I'd dealt with that. Oh, only with assumed nouns I think. These are both complete one-part matches, so it doesn't run into any of that.

For now just going to fix the batteries thing.

So, we have two sides:
* Device knows what battery-name it needs (device.takes_batteries) - is 'battery' if True and not str.
* device knows what battery it currently has if any, in device.has_batteries (batt instance)
and
* battery knows it is a battery with item_type["battery"]
* knows if it is in a device with battery.in_use (device instance)

So. It is more likely the device is more specifically named. We should use that as the assumed baseline.

---------

11:32.
Hm.
It's erroring during the move. Or possibly during format_descrip.

Oh. I'm so stupid. I've been setting up in def take but working in def put. Goddamn. Okay.

I'll probably need to add battery-type items to local nouns, otherwise if the only battery is in a device it'll never let me access it via the parser.

12.02pm
Oh, I think it's erroring silently because it's still trying to move the batteries to the 'container' of the watch. I just forgot to change it. Okay.

12.39pm
Mostly working now. Just need to add battery types to local_items if loc==no_place and it should be pretty okay.

1.26pm
Well this is unexpected. take battery from watch is failing because while it finds the watch inst in parser, it loses it in find_local_item_by_name.
Oooh. It's because it's in inventory this time, and the verb rules out inventory items for 'take'. Right.

Partially solved; it now searches for noun2 anywhere, including inventory. So you can 'take x from y' when holding y, when previously you couldn't. access_str2 coming in clutch.
(Still not picking up the batery though. Working on it.)

1.38pm
Okay. Seems to be holding together now. no_place items with in_use are added to local_items, so you can still type 'battery' and have it recognised if there are active batteries. (Currently it doesn't demand that the battery-holding item is accessible, but could do later if it seems necessary.)

1348
hm. This is... annoying.

After I take the watch battery from the watch (which does work now), it claims to be in my inventory:
` <ItemInst watch battery / (41622149de34) / north inventory_place / None / > `
And yet:

You're facing north. There's a dark fence blocking the horizon, prominently featuring a heavy wrought-iron gate - standing strong but run-down, an old dark-metal padlock on a chain, holding the gate closed, and a watch battery.

And if I print all local items:
`{<ItemInst padlock / (f1644ccccca8) / north graveyard / graveyard_gate_opens / ..76724141877a / >, <ItemInst watch battery / (41622149de34) / north inventory_place / None / >, <ItemInst gate / (8fb770bc9d9d) / north graveyard / graveyard_gate_opens / ..76724141877a / >}`

there's only the one, in my inventory. So why is it showing up in the loc description.

I'm really not sure. It gets local_items from self.by_location.get(loc_cardinal), and gets this output:

`LOCAL ITEMS IN DESCRIPTIONS: [<ItemInst padlock / (abebf365d133) / north / graveyard_gate_opens / ..fa109b8f43c4 / >, <ItemInst watch battery / (00f19c5eaebd) / north inventory_place / None / >, <ItemInst gate / (59b991508b18) / north graveyard / graveyard_gate_opens / ..fa109b8f43c4 / >]`

It should be doing this:
# if location != None:
#     if not self.by_location.get(location):
#         self.by_location[location] = set()
#
#     inst.location = location
#     self.by_location[location].add(inst)

and location is given as
# north inventory_place

confirmed:
`Location provided: <cardinalInstance north inventory_place (12edc1da-77f5-48ed-8398-fbf9ae1e070d)>`

So. The battery starts at testing grounds:
`<ItemInst watch battery / (369a2dc9e35d) / north testing grounds / None / >,`
is picked up, and carried to graveyard. On arriving, it is not in the items list:
`LOCAL ITEMS IN DESCRIPTIONS: [<ItemInst padlock / (a1d51ec824e9) / north graveyard / graveyard_gate_opens / ..954eaa2dea56 / >, <ItemInst gate / (c656a3d76d35) / north graveyard / graveyard_gate_opens / ..954eaa2dea56 / >]`

the battery in north inventory_place is moved with the location provided as
`<cardinalInstance north no_place (62a9f803-f989-4317-8c17-f2fc1be5662f)>`

Immediately thereafter, graveyard local items remain consistent:
`LOCAL ITEMS IN DESCRIPTIONS: [<ItemInst padlock / (a1d51ec824e9) / north graveyard / graveyard_gate_opens / ..954eaa2dea56 / >, <ItemInst gate / (c656a3d76d35) / north graveyard / graveyard_gate_opens / ..954eaa2dea56 / >`

... Oh, this is weird.

So, I pick up the battery, take it to graveyard.
When I put the battery in the watch, it's the same watch battery, still in inv_place.

But: if I get local_items immediately after via logging args, I get this:

`input_list: {<ItemInst fashion magazine / (9a608c938f3c) / north inventory_place / None / >, <ItemInst watch / (fccdc24425da) / north inventory_place / None / >, <ItemInst paperclip / (5869d948f261) / north inventory_place / None / >, <ItemInst battery / (7c0111024be4) / north inventory_place / None / >, <ItemInst severed tentacle / (89bc5577722b) / north inventory_place / None / >}`

<ItemInst watch battery / (369a2dc9e35d) / north inventory_place / None / > is gone (correctly, as it's in no_place once it's "in" the watch), but an unrelated battery is not in my inventory:
`<ItemInst battery / (7c0111024be4) / north inventory_place / None / >`
That battery was originally at testing grounds (intentionally, because I like testing the parser), and it only has two mentions: it's initial appearance in testing grounds, and then suddenly appearing in my inventory via recurse_items_from_list.

Okay. So..... When the hell did that happen.

Take battery:
<ItemInst watch battery / (259fdc330d74) / north testing grounds / None / >
locals:
LOCAL ITEMS IN DESCRIPTIONS: [<ItemInst paper scrap with number / (dbc10a013670) / north testing grounds / None / >, <ItemInst mobile phone / (e9a701437f69) / north testing grounds / None / >, <ItemInst watch battery / (52d125737581) / north testing grounds / None / >, <ItemInst phone charger / (f3b66ea47f54) / north testing grounds / None / >, <ItemInst watch battery / (d7bf35416281) / north testing grounds / None / >]

get to graveyard, and print inventory:
  - watch battery <-- is 52d125737581 by the color
  - watch
  - gardening magazine
  - battery <-- was not present at all previously
  - paperclip

But then when I go to put the battery in the watch:
<ItemInst watch battery / (259fdc330d74) / north inventory_place / None / >
Suddenly the original is back. Though I still have 'battery' in my inv.

Alright. So it's init-ing the battery from somewhere.

And even if I get rid of the 'battery' entry in loc_data, I still have duplicates behaving weirdly:
without 'battery' and just the plural 'watch battery' instances, when I put the battery in the watch, all good. (Well 95%; it's printing the wrong colour which I need to fix in colours, but that's minor.) Only one battery shown in inv, 0 batteries in graveyard.
Put the battery in watch, no batteries seen anywhere, can only add one battery to the watch, all good.
But then, remove the battery, and it shows up in loc_desc and local_items. despite still showing its location as inv_place.

Have I failed to return and it's doing a second move? No, the prints are only running once and the logging shows it never repeats move. What the hell...


3.04pm
Have spent the last while trying to figure this out. Not solved it yet.

Have narrowed it down a little at least.

Immediately after 'take battery from watch', it runs get_item_by_location a few times. And on the second run through for north graveyard, the battery is already there.

[<  take battery from watch  >]
 '-                         -'

Getting item by location for `<cardinalInstance north graveyard (0bea7be7-4764-40c4-8491-cd54bd974cdc)>`
Items at cardinal: {<ItemInst padlock / (db430e4866ae) / north graveyard / graveyard_gate_opens / ..11e22029d227 / >, <ItemInst gate / (1b505f541967) / north graveyard / graveyard_gate_opens / ..11e22029d227 / >}
Getting item by location for `north no_place`
Items at cardinal: {<ItemInst watch battery / (b44a63347db9) / north no_place / None / >}
Getting item by location for `<cardinalInstance north graveyard (0bea7be7-4764-40c4-8491-cd54bd974cdc)>`
Items at cardinal: {<ItemInst padlock / (db430e4866ae) / north graveyard / graveyard_gate_opens / ..11e22029d227 / >, <ItemInst watch battery / (b44a63347db9) / north no_place / None / >, <ItemInst gate / (1b505f541967)
/ north graveyard / graveyard_gate_opens / ..11e22029d227 / >}

OH.
It's because I'm including it in local_items for the parser. loc_descriptions is using that same list. oh god that took me /way/ too long to figure out. Okay.

Now to undo a shitload of print statements.

3.07pm
Wait no it's not.
It's just a straight get_from_location, it's not touching membrane.local_items.

Fundamentally, the battery is being given the correct inst.location, but the wrong registry.by_location[cardinal].add(inst). I just can't see where. I've gone over it and it all seems right....

Okay. So it's before move_item.
Before act_on_battery_device.

After the very start of def take.

3.22pm
Okay. It's get_correct_nouns. No idea how/why, but it is.

find_local_item_by_name.
Oh. Does it update loc descriptions using the internal noun_list. Probably. So I was close before, I just forgot for a moment that it could be triggered another way.

Oh - I think perhaps it's adding it retrospectively to loc items. Not the list of items, but the location itself.

Yeah, it is.

loc_items = registry.get_item_by_location(location)
...
final_items = loc_items
...

    no_place_items = registry.get_item_by_location("north no_place")
    if no_place_items:
        for item in no_place_items:
            if "battery" in item.item_type and hasattr(item, "in_use") and item.in_use:
                final_items.add(item)

I wouldn't have  thought that this:
items_at_cardinal = self.by_location.get(loc_cardinal)
(which is what is returned from `get_item_by_location`) would feed back that way. I'm not editing a dict, am I? I mean I must be based on the behaviour.

Yeah, that was it.
Output a set(i for i generator) instead of the immediate result and suddenly it stopped happening.

So, I think generally, when there are containers, etc etc, it ends up running through some kind of iterator/generator to add different datapoints. But the specific criteria and lack of containers/etc in that specific location meant that it was the raw set directly from the dict. So then I was adding to the set, which was exactly the same set as held by the dict. Okay.

I had a feeling that's where it was going I just couldn't track it down.

Need a little break now. Bit late for lunch but I need to blink for a minute or two.

Okay. Cleaned up most of the print statements. Little break.

4.40pm
new issue: the command 'east' errors with
`Failed to find the correct function to use for None: object of type 'NoneType' has no len()`
Well not the comand specifically, but moving to east graveyard from elsewhere. 'go to east graveyard' and 'east' both work after you've arrived there, but error again if you go west then go east again.

4.45pm fixed that one. Had to account for multiples.get(item_name) == None before getting len()


Note on the 'discovered' flag:
an item is discovered if:
* an item is described in loc_desc
* an item is in a container that has been through def describe (ie look at x)
* an item has been read
* an item has been mentioned directly in some way in output (not just user input)

Should also have a 'discovered locations' dict. Thinking of UI again; a little panel on the side with current_loc and a tree of discovered locations.

Todo:
'out of' == direction.
7.05pm Well that wasn't too hard. 'take battery out of watch' works now.

God I'm wiped. Going to stop soon before I break everything.

3.45pm 11/3/26
Had a couple of days off to work on supermarket simulator scripts. Back to it now. So. What was I working on again?
Discovered item flags, maybe. Will work on that today. Need to merge all the watch/battery stuff w/ main first. I think that was finished succesfully?

Fixing a couple of small things first. One, need to update the watch description if it has a suitable description for 'has battery'. Also need to change the description back in the battery is removed.

Also, 'put watch in battery' fails without a proper error print, so I need to redirect it.

Huh. Why does 'use battery to break watch' fail the parser?

It's because watch is also a verb, isn't it...

Also,

[<  use battery to break jar  >]

You slice the watch battery with the glass jar, but glass jar was weaker - glass jar breaks.

While the interaction is right, it's used the wrong order - the battery was the actor here, not the target.
Oh, it's because it's not doing the 'use x to verb y' flip. I wonder why not?

Okay. so the issue is that the nouns aren't switched. Is switches the verb, not the nouns.

Okay goddamn. I just need to redo that whole section. I wish I could remember the original test phrase I was using because clearly I thought it worked at some point.

Also:

`You slice the god hammer with the dried flowers, but dried flowers was weaker - dried flowers breaks.`

`Failed to find the correct function to use for <verbInstance break (b7d5b508-9f25-4c17-8823-3b0807382bfb)>: not enough values to unpack (expected 2, got 1)`

So, the original still fails. I have no idea why I thought it worked earlier.

Tangent time then. Need to sort this.
the swap exclusive to format "'verb', 'noun', 'direction', 'verb', 'noun'". So I'll just use that instead of looping to try to catch word-types.

idx 0: 'verb',
1: 'noun',
2: 'direction',
3: 'verb',
4: 'noun'

idx 0: 'verb',
1: 'noun', <-- is noun2, was noun1
2: 'direction',
3: 'noun' <- is noun1, was noun2

Ah. I reduce the noun2 idx to compensate for the missing second verb, but I could just swap those nouns then. idk why I didn't do that.

Okay so other issue fixed: 'use battery to break watch' now forces noun if there's already 2 nouns, so it no longer assigns 'watch' as a verb in the reorder. (Would still break if you said 'use watch to watch battery' but when it gets to that point the user is just being mean.)

Hm.

`[<  look at watch  >]`

`Sorry, what do you want to look?`

Hm. Because it's not finding perfect (as the watch in this example is 'broken watch'), it assumes it's a verb. If you give the full name ('look at broken watch'), it works fine.

Yeah, it fully just calls 'watch' a verb, it doesn't even assign the possibility of 'noun'.

Hm.
Did it not add 'broken watch' to plural nouns or something? Even if I force it to recognise 'watch' as maybe-noun, it still says 'tehre's no watch around here to look at', but 'look at broken watch' still works.

Oh, it only checks plural nouns if no canonical. So because it finds a canonical with watch (verb), it never finds (broken) watch. But typing 'broken watch' gets the perfect canonical without finding the watch-verb.

Hm.
I can't tell it 'never take the canonical for 'watch'' because then 'look at watch' finds 'watch battery' because it's forced to look for compounds.

Huh.
`You smash the watch with the watch battery, but the watch and the watch battery are evenly matched; nothing happens.`

but:
`You smash the watch battery with the watch, but watch was weaker - watch breaks.`

So there's a logic flaw in def break. Will fix that shortly. #TODO.

Also, 'break' doesn't abide by item locations. 'break x with y' works even if y is not in loc.current.

Hm. Okay so have made a little progress, but still no win. I have it running the compound check again after sequencing if no sequence was found, but in this case we have both 'watch battery' and 'broken watch', and it doesn't know how to pick between them.

Potentially solved, though it might break other things.
Now checks
    if not noun_inst:
        noun_inst = registry.instances_by_name(entry["text"])
if no noun_inst is found, so it gives another chance for assumed_nouns to be identified using the post-sequencer compound attribution. Works in this one case:

# [<  look at watch  >]

# You look at the broken watch:

#    A scratched gold broken watch.

So that works properly. It's arbitrary that it found broken watch instead of watch battery, so it's fragile, but conceptually works.
I think I need to add a list of adjectives it ignores, so it'll choose 'broken x' instead of 'x something' if I tell it to look for 'x'. So it recognises 'variant of x' as separate from 'x thing' (broken watch vs watch battery).

Maybe I should just hardcode 'last word of noun == primary word' as a concept into it. So 'watch' will prioritise 'broken watch' over 'watch battery', and 'battery' would prioritise 'used battery' over 'battery hen'. That might be a good idea. Doesn't solve 'look at watch' == 'look at look' but the post-sequence retest does seem to fix that one well enough.

"[<  use hammer to break watch  >]" still fails though.

On the upside, 'use hammer to break watch' works now. So that's nice.

I should use the slice/bash stats to determine the print line. High slash/low bash == 'x shatters' instead of 'breaks', etc. Maybe.

Oh, 'break' doesn't take the location of the target into account either.

I need to bring some of the error printing back to verb functions. Allowing for all permutations is harder than it needs to be, and the verb fn already worked out which nouns are viable etc. It was a mistake to try to re-parse everything.
Instead, I need to figure out a format to send error messages to the failure printing so the structure matches but is already pre-prepared. Or just break up the failure printing fn into distinct sections based on what it needs (eg is everything provided, is just the input_str, etc etc.)

Going to work on the 'verb action fns picking the wrong noun'. I think it's just that I'm using the old 'get_nouns' instead of the corrected one. If I fix that it should resolve immediately.

Hm. Slight tangent: why does 'put paperclip in jar in graveyard' fail, but 'put paperclip in jar' succeeds? The jar and paperclip are both accessable.

Okay, fixed it. It's because I had a requirement for format_tuple length that excluded the location. Now it accepts that format as long as the location is loc.current.place.

3.55pm, 12/3/26
Hm. 'Enter shed' doesn't work anymore, it gets stuck in get_noun_instances.
Okay, fixed that.

Oop, no I didn't. It's still getting mixed up when I say 'enter shed'. Never even makes it out of the parser, so all my finagling the other day/week in transition_objs does nothing.

Oh, it's because it ends up with:

'location': {'canonical': 'shed door', 'text': 'shed'}

It doesn't save canonical by kind, so even though it recognises both noun and location and found matches for both, it doesn't keep the location name.

Oooh. Okay. So the intermittency is just whether it takes 'shed door' or 'work shed'. The specific failure is that it had [loc][cardinal_str], expecting 'graveyard north', but 'shed door' broke up the same way. I never tested to make sure the split str contained a viable cardinal and wasn't just a compound noun.

Fixed now. If location_str and no location, it checks to see if it's viable in compound_locations, and applies the result to location if found. Also added the check inside get_cardinal_str that ensures the 'cardinal str' is actual a cardinal before continuing.

It only hit that error every 5-6 runs, but now it never should again.

4.37pm
Added a little amendment to the 'enter' print, that specifies you moving to the ext_location before opening the door.

Okay. Back to making sure get_correct_nouns is always used.

Actually - replacing get_noun etc with get_component, they all use the same pattern. Right?

6.40pm
Oh, what the hell.

There's a dark fence blocking the horizon, prominently featuring a heavy wrought-iron gate - standing strong but run-down, an old dark-metal padlock on a chain, holding the gate closed, a watch battery, and a watch battery.

Why. Why are they not blending properly.

Also the watch battery (singular) in inventory doesn't have the right colour. It has the colour of another watch battery.

6.57pm
Okay. Inventory now actively checks for the right item instance to get the colour for, not just matching name.

7.38pm
Loc descriptions now include multiple items. I think it was before, I was testing maybe with preset local items? Whereas this time I dropped the batteries to the loc, so they weren't in loc_desc. Etiehr way it seems done now. God I feel like shit though.

Am now using 'is_plural' nicename for general objects, for when there are multiples in the loc description. So instead of
# You're facing north. There's a dark fence blocking the horizon, prominently featuring a heavy wrought-iron gate - standing strong but run-down, an old dark-metal padlock on a chain, holding the gate closed, and watch battery x3.

you get
# You're facing north. There's a dark fence blocking the horizon, prominently featuring a heavy wrought-iron gate - standing strong but run-down, an old dark-metal padlock on a chain, holding the gate closed, and 3 watch batteries.

Which is just much nicer. May as well use that same field.  Cluster items still retain their custom plural nicenames and aren't affected by this (and still do not get the number-count, as intended).

10.52

[<  open matchbox  >]

Cannot open matchbox because in inventory.

hang on what? goddamn. Okay.

Well fixed that, for some reason I excluded inventory items from being allowed to open.
But next issue: it just lists "match". Not counting or using the plural name for the compound item in inv container. will fix that too.
Okay, fixed it. I lost that plural nicename when I switched to print_names. Have now set it properly to obey when nicenames is set True.

Hm.
Loc descriptions is still giving "watch battery x3" when the batteries are

11.00 13/3/26
Fixed the issue of loc descriptions not properly giving 'x3' versions if the items aren't in loc_desc.
Changed it so that instead of
`watch battery x3`, it says
"3 `watch batteries`".
currently with the colour only applied to the name, not the number, so it's clearer that the `3` isn't part of the item name.

Going to work on def break again, not sure if I finished fixing it last time.

The issue:
* `You smash the watch with the watch battery, but the watch and the watch battery are evenly matched; nothing happens.`
but:
* `You smash the watch battery with the watch, but watch was weaker - watch breaks.`

Also def break didn't get the correct nouns so allowed actors and targets to be remote. That's already fixed now.

Ah, for the above issue, I think I had the nouns switched. It should have been
`getattr(noun2, f"{attack}_attack") < getattr(noun, f"{attack}_defence")`
but I had
`getattr(noun, f"{attack}_attack") < getattr(noun2, f"{attack}_defence")`
So I was literally testing 'is the defender stronger than the attacker, if so the attacker wins'.

I'm not sure if I necessarily want things to break if you use them to break things though. I guess I have the breakable flag for that. 's why I made attack and defense different, but then if I'm using defense to do funtionally 'return damage' then it gets messy. not sure.

Like it makes sense, if you try to break a chest with a glass jar, the jar should break, no? Maybe that's too harsh and only the defender has a risk of breaking. Idk.

Or maybe I need a 'damaged' state? So on the first 'break' it is `damaged`, functionally identical but at risk of breaking next time. that might work.

Oh, I had
"slice_threshold": 1, "smash_threshold": 1
for this kind of thing. Maybe I use that - if the item is an attacker but the diff is greater than threshold in favour of defender, attacker breaks? Otherwise attacker doesn't break. Idk. Maybe? Because the watch breaking the battery is just silly, but the battery should be able to be smushed by a big hammer.

Oh, slice/smash_threshold was just the original term for slice/smash_defence. Right.

Maybe just use the 'fragile' tag, then? If fragile, breaks if defender or attacker and defender's defense is lower than attacker's attack. So the jar would break if you try to break a chest with it, but the battery wouldn't because it's not tagged fragile, it would just fail to break the chest. That might be better.

Will remove Threshold. Or more correctly, rename it to _defence, so that 'fragile' things start with their defences set to 1 instead of the default 5. That works.
Okay. Threshold in item defs now changed to defence values, and the standard defaults added:
fragile: slice/smash defence 1.
books_paper: slice defence = 3, smash defence = 9.

I need to make sure all the checks that use item_type are properly in the defaults. eg 'battery' needs 'in_use', which wasn't there previously. So I only need to check for item_type, and then all checks after that are guaranteed hasattr True.
Added defences of 10 to default walls and floors.

I should really do a conversation setup. Don't have that at all yet. God that feels like it might be a nightmare.
I think I'll need an internal loop that calls the parser but doesn't go through to Router, so conversations can be dealt with separately. Man I have no idea how that'll work yet. Okay. Well I need to keep busy today because my head's a bad place so might as well try it.

First, going to add those checks to def break. Also, make sure that only things that can break are broken.

It's a bit rough but breakage now takes can_break into account.
I need to divide it into slash and smash properly. Paper should never break but can be slashed. I guess that's what the defence values are for though.

Will work on the conversation for a bit.

12.11pm. 13/3/26

So. How does conversation work.
Need to brainstorm.
* Shared information: NPCs can have access to a shared databank, about the world, events, items, etc. May have different ways of phrasing things.
* Specific information: NPC may (should) have unique dialogue.
* Trading? Implement later but would make sense at least sometimes. Will need to add value to items for this to work. Or maybe only items from the table can be traded, and the value comes from the table status. Would be easier than giving every item a value. Maybe when it enters trade state it is assigned a random value from within a loot category limit, and that value is then used thereafter like item.colour is.
* Need conversation to be visually different so it's clear it's a specific context, as meta commands etc won't work like that do usually. Probably just a couple of tabs and/or colouring.
* NPC specific colouring/formatting.
* Need to add NPCs to locations.
* Need to add NPC names/titles to parser. Probably just as nouns, so look/talk/etc can just be used as usual.

I have to remember how the item generator works.
I can't remember how this worked:
`description_dict = item_type_descriptions[def_type]`
I guess maybe it's from when type descriptions were listed separately? Idk. Goddamn.

Making notes in conversation_notes.

Also: currently I have the Raven listed as can_talk, but it's in item_defs. I guess I should move it to NPCs. Anything that can talk goes to NPCs. But we just add NPC defs to noun_list etc so they're still found the same way.
Hm. Will need to add them to noun instances? Or we keep calling them nouns, but give the npc_instance. But that'll break things.... goddamn. I really don't want to have to add verb_dir_npc formats. I guess I could though. Not sure. Or could just add 'npc' as a valid alt to 'noun' for all formats, so 'give paperclip to Father' would automatically pass.

I would just need to make sure npcInstances were allowed in the various isinstance checks. I'm using largely the same formatting as for item defs, just with different itemTypes. So it should be okay.
I think allowing 'npc' to be 'noun' in formats is the best bet. Will need to figure out the best way to do it. I do think it's important to keep them separate, they'll hold conversation data etc that regular items won't.

Also I might keep 'parts_said' in conversations.json, so I have a global tracker per conversation. Not sure though. Thinking on it soon.

6.22pm
Been a decent day of progress. Have set up the classes and their linkages, and am working on the string manipulation.

eg:

`"The church has a history, it says lots of things. Who knows, really. I think it's an interesting thing."`

becomes:

`Ah, the church has a history, it says lots of things. Well, uh, who knows, really. Think it's an interesting thing.`
with no_pronouns and well_um speech traits

or:
`Well, the church has a history, it says lots of things, who knows, really, I guess, I think it's an interesting thing.`
with 'run_ons' and well_um traits.

or
 `I think... the church has a history, it says lots of things... Who knows, really... Well, uh, I think it's an interesting thing.`
with well_um and ellipses

or
`The church has a history... it says lots of things... Who knows... really... I think it's an interesting thing.`
with ellipses and commalipses.

 Note: 'well_um' is randomised, both with how often it adds fillers and which filler it adds, so the sentence will be a little different each time. Will do something similar with ellipses/commalipses, for degrees of ellipsification.

3.47pm 14/4/26

Hm. 'take battery' adds 2 newlines between input and return print, but everything else only adds one. Why.

Fixed. Had a \n in the 'now in inventory' print line. Removing it doesn't seem to cause immediate issues.

3.59pm 16/3/26
Working on conversations. Have not updated here but basic conversations are working, albit rather simplistically.

dammit.

Event: <eventInst learn_about_cult ..bac839a2878f // state: 1>
    Mm... I do miss having her around the place, I suppose... But, needs must, `greater good` and all of that... I suppose I'll see her again someday... Have you seen her around?...

...mother

    We've discussed this topic before... Do you want to discuss it again?...

... y

    Yes, good.

    Oh, that must have been something of a shock... I'm very sorry... I would ask if she was well, but... Well.

that 'yes' should only apply to the 'discuss it again', but its being carried throughg

if you get the the 'mother' conversation part, it should add a new conversation to the list. not just a line, anothe thing you can reference entirely.

Okay. It does that now, ish. If you ask about the cult, it references your mother and if you say you've seen her, then it adds a new conversation topic.

Now I need to figure this out.

# parts_said: {'3'}
# parts_said: {'4', '3'}
#     Mm... I do miss having her around the place, I suppose... But, needs must, `greater good` and all of that... I suppose I'll see her again someday... Have you seen her around?...
#
# ...yes
#
# parts said: {'4', '3'}, type: <class 'set'> // conversation.autoplay_parts: {'1', '2', '0'}
# no parts_said: None
# parts_said: {'4', '3'}
# parts_said: {'4', '3', '5'}
#     Oh, that must have been something of a shock... I'm very sorry... I would ask if she was well, but... Well.
#
# ...
#     It seems like there's nothing else to say about this.
#
# discuss_topic outcome for seen_mother: end_topic
#     It seems like there's nothing else to say about this.
#
# discuss_topic outcome for mother: end_topic
#     It seems like there's nothing else to say about this.
#
# discuss_topic outcome for cult: end_topic
#
#    Nothing else you want to discuss? Alright... Enough for now then, I suppose.
#
# You step aside, leaving the conversation with Father.
#

During, the interaction goes well, but then they all resolve when it's done and they all repeat the end.

6.20pm
Okay. Think it's fixed now though it's probably still tenuous. It seems to loop correctly, ignoring recursed internal loops on leaving the loop cycle so it only officially ends once, as it should. Also conversation threads adding new conversations works nicely too.

10.47am 18/3/26
I'm starting to struggle with this, particularly I think because I don't have a story. Testing little discreet elements is all well and good but it's difficult to think of everything that would come up in genuine use, if not impossible.

Though I did just remember how messy the is_event_trigger fn is. I guess I can just clean that up.

I should read through all the existing scripts and see what needs fixing, what needs removing, etc. Maybe that's today's job.

Man I kinda want a GUI/TUI for item generation. So you can press buttons for item type, fill fields, etc. Like filling out a pdf. That'd be cool.

## Things to work on for existing scripts:
* edit_item_defs: is messy but does work.
* env_data: not sure what 'setattr(self, cardinal, self.cardinal_data)' is doing at env_data ln 50 when self.cardinal_data already exists.
* env_data, ln 66ish. card and place carry 'transition_objs' but it's different data. card is a set of itemInstances, place is a dict specifying int_loc and ext_loc. Need to change it so that one builds the dict, and the other just takes that same dict. I think?
* env_data: remove alt_names from placeInstance init once confirmed it's never used. it's not referenced outside env_data as far as I can see.
* env_data: set_current(self, loc=None, cardinal=None) needs a serious cleanup. It's such a mess.
* env_data: does anything still send by_cardinal_str a dict? I don't think so but need to check.
* env_data: the transition_objs section in init placereg at ln 341 needs reworking (relates to earlier note re: ln 66)
* env_data get_descriptions: is place.overview ever not a str? `if not isinstance(place.overview, str)` ln388
* env_data get_loc_descriptions: was returning after the first get_descriptions(place). Check to find out if this is why I had to redo them later, maybe I can reduce redundancy here.

* is start_trigger_by_item etc in eventRegistrar actually used by eventRegistry? Check.
* why am I adding generated events to add_to_intake before events.add_event? Is it for preprocessing? Probably I suppose. check.
* eventRegistry: event_state_by_int is only used by trigger/event repr.
* eventReg: reg.trigger_items is not used. Remove?
* apparently reg.self.triggers is not used either. Remove also?
* reg.self.start_triggers is not used either. I don't think we use this because we tell the trigger items themselves that they're triggers.
* reg.no_item_restriction also not used.
* reg line 1432: calls 'event' without checking if event exists. but is_event_trigger is such a mess I'm not fixing it yet.
* ln 496, we use registrar's 'start_trigger_is_attr' instead of 'events'. idk why. generate_events_from_itemname is used from eventReg *fixed
* ln 1692, add_to_intake adds the intake event to registrar.events, but adds 'generate_events_from_itemname to 'events' directly. What the hell. Surely they shoul all be in registrar, no? * fixed
* match_item_to_name_only is not used anywhere I can see.
* start_trigger_is_attr is not a set attr for eventInstances. I think it's just set by `for item in attr: setattr(self, item, attr[item])`, along with other things. God I need to redo this whole thing so badly.
* self.start_triggers used to be 'start_trigger_is_item' from registrar.
* > match_item_by_name_only is used here:
`intake_event.start_trigger["item_trigger"].get("match_item_by_name_only")`, ln 1446. But it's after if `registrar.generate_items_from_itemname.get(noun_inst.name)`, which is literally created by
`self.generate_events_from_itemname[event.start_trigger["item_trigger"]["trigger_item"]] = event.name`. So anything in generate_items_from_itemname is definitely an item_trigger start_trigger... So unless there's a route where an item can be generate_events_from_itemname but not be a start trigger item, I don't need that second check.
* event.no_item_restriction is checked once, but I can't see it ever added to. Currently entirely pointless I think.
* need to set item triggers as is_event_key more intentionally.
* get_parts_from_tuple(attr_trigger) is broken. It calls get_parts_from_tuple internally but then still returns tup?
* is_event_trigger only runs after if event.end_triggers, as an elif. So whether it can have start_triggers is defined by it not having end_triggers. That can't be right.
* this line: `if event.no_item_restriction[noun_inst.name] == noun_inst:` doesn't work. if it gets to this point there is no 'event'
* verb_actions: move_a_to_b uses container_limit_sizes to check if something can go into a container. None of the other move functions seem to do that. def move_item should really do that...
* in itemReg, starting_location starts as str but is sometimes cardinalInstance. (It was sometimes placeInstance too but I changed that at least.)
* itemreg does this: `if attr["exceptions"].get("starting_location"):` twice, once inside item init and once immediately after it in init_single.
* itemReg init: remove `for attribute in attr:`, do it intentionally, using item_type for more specific attr.
* itemreg create_base_items, does if cardinal == None: to get card_inst but then checks by_cardinal_str anyway. Silly. just get card_inst from by_cardinal_str if cardinal_str is given
* itemreg adds 'item_data["description]' to the item defs dict if it doesn't exist, arbitrarily, from item_data["descriptions"]. Given I add description later, this feels utterly bizarre to do. Should remove entirely, no? Oh, wait - no, it's because it allows for location specific descriptions. Right. It can stay for now I guess. Has to be a better way of doing it though.
* Can I remove `if hasattr(obj, "is_loc_exterior"):` from ln 1749 in itemReg? Should all be done in item init by that point, no?
* misc_utilites:: check if I still need to run get_loc_descriptions for def look_around (get_loc_descriptions(place=loc.currentPlace)) at all, and/or if I can just run it for cardinal instead of place.
* misc_utilities print_failure_message needs a rework, but needs strenuous testing before applying any changes.
* Why is env_data calling itemReg? OH - because env_data calls misc_utilities, which imports itemInst. Right. Well it does it slightly later now but it still calls misc_util, and I really can't avoid that. It doesn't break anything though, so I'm just going to leave it.
* npcRegistry: need to set self.location at npc init instead of leaving it as the str (ln 84, self.location = data.get("location"))
* have made self.conversation_parts["start"] mandatory; need to add something for it to choose start/ends from a random selection if not given. For now though all will be given. Have added a simple 'hello/goodbye' sample_conversation_parts for now.
* What the hell is `setattr(self, cardinal, self.cardinal_data)` doing in env_data? I'm adding it /to the cardinalInstance/, why am I adding it to cardinal_instance[cardinal_str]? Especially when cardinal_data is already added to self directly.
* verb_actions: line 194~  `for item in local_items_list:` makes a dict from a dict, then checks if a key from the dict is in the enw dict and returns it. Totally arbitrary. Gave it a quick fix but it needs more work.
* can't remember what 'movable_objects' at the top of verb_actions was meant to be for. Clearly it's verbs that require a movable object, but all that's done through get_correct_nouns now.
* get_current_loc is called by verbRegistry, but it returns placeinstance and cardinstance, and verbreg calls it 'current_location' and then tests if a string is 'in' it. Which it will never be... line 315 verbRegistry, should be if word in loc.current.name or word in loc.current.place.name, no? get_current_loc is only ever called twice and it's used incorrectly by one of those. edit: oh, an the other use is a function that is never called anymore. Fixed it and verbReg so it does what was intended.

* I need to remember 'format_list_neatly(list_to_neaten)' exists so i can use it elsewhere (verb_actions, ln 44)
* set_noun_attr: Not messing with it today because it's too important, but I need to better formalise what goes into 'reason'. Even if I need to take it apart and make it a dict first: 'attr_str: ""' or 'noun_action: iteminstance', etc etc. Not just `if it's a string then assume it's (type of event trigger)`, `if it's a tuple then dig into it and get the first tuple in the tuple and use the value of it` etc. Need to properly document what goes into 'values*' so I can figure out the best way to do it.
* get_transition_noun is a terrible mess. Wait, and it's only called by def find()?? See major notes.
* utilise get_component_parts better. Unless there's a good reason to keep all the separate get_x_thing fns. Oh actually, use it /at all/. Currently I'm not.
* five_parts_a_x_b_in_c is still used by def put(), it shouldn't be.
* def put() uses registry.move_item but then also uses move_a_to_b, which does its own printing and item-adding, with different checks in each. Need to take the container_limits section from move_a_to_b and add it to registry.move_item for if container and route everything through that. Though I do like being able to customise the 'you dropped the x down here at the y' message the way this does. Might add that logic to registry.move_item too.
* now i have get_correct_nouns, do I still need can_interact in lock_unlock() / check_lock_open_state / simple_open_close? get_correct_noun is far more sensitive and specified, especially when get_correct chooses the nouns more precisely and also outputs the reason_val. can_interact just runs run_check and outputs a bool, I can't see value in that separate from get_correct_nouns... ln311 verb_actions
* check_lock_open_state ln 320 verb_actions is not accessed.
* do I want get_component /and/ get_component_parts, or just one? _parts always returns (instance, text (str_name|text)), get_component returns instance unless get_str.
* I still use get_nouns in a couple of places. Useful for error printing where I don't need to try to get the 'correct' nouns but anything else should use get_correct_nouns.
* why am I using inst_from_idx to get the cardinal for turn_cardinal? Nothing else uses it. Oh, it's basically get_component but with the idx defined. Okay. Avoids the loop. Oh - see major notes.
* verb_actions line 606 is prospective_cardinal ever a dict? Where/why would it be? check. Can't see anywhere, it's all instances or left/right. Removing.
* ` if noun.location.visited:` at 680 verb_actions confuses me. Why if it's visited to we get told about the closed door but either way still relocate to noun.location. The noun.location == ext_location doesn't apply here, so we might be outside the closed door and going inside, or not, and it doesn't check. I need to clean that up a lot.
* move_through_trans_obj is extremely messy and should be able to be cleaned up. Or at least given better direction, right now there are too many exception catches. and it's so breakable, or at least looks like it.
* def go() needs to be neatened
* if def look(), need to add options for 'look at x on y'.  But need to add 'x on y' more generally first.
* ln 1147 verb_actions, why do we pick a random readable noun to read? Well it's alright I guess, but it needs a printline for `You decide to read the {item} for a while.`
* 1387 in def break_item(), we check if noun2: but don't provide an alternative.
def break_item doesn't check can_break. Needs to.
* ln1459, check if accessible_1, _, _ = can_interact(noun) ever gets useful results now that get_correct_nouns is used.
* ln 1476, I have a function for is_locked and do_open checks but am not using it. Use it here, no?
* misc_utilities ln 539, why are we adding all children? I assume it's intentional but make sure.
* itemReg ln 558 / ln196  change instance_children and starting_children to sets instead of lists. Is generated in generate_children_for_parent(self, parent=None) at ln 543.
* itemreg builts by_alt_names at ln445 but also they get built in itemgen and I think elsewhere too. streamline this.
* 'has_door' never gets used anywhere, we just use transition objects. Remove?
* I still have the wire cutters referred to as 'keys', because they were used to ""unlock"" the wire that kept a jar closed. I need to do that better, they're not damn keys. 'use x to cut wire' needs to be a thing. #TODO this.
* rn only statics have 'can_break' by default. Have added it to 'standard' as True
* 'can_examine' is never used, I have routes in 'descriptions' to deal with items without additional data. Remove this.

# Things fixed:
* All places now have missing_cardinal added at init, so player_movement doesn't need to check for it and provide an alternative.
* removed alt_name 'hotel room' from `city hotel room` because the parser already finds 'city hotel room' from 'hotel room'.
* changed init_loc_items from importing the loc_data json to just using loc_data from locReg. Now it's only imported by env_data and generate_locations.
* added type hinting for place.cardinals and self.places, much nicer.
* also added type hinting for events and eventRegistrar.
* placeInstance was carrying self.current_loc when only locReg needs that.
* moved generate_events_from_itemname to registrar so it matches the rest of add_to_intake
* removed check for 'if generate_event_from_itemname' has start_trigger item_trigger'.
* stopped is_event_trigger from exiting is a noun already had an event, now just returns None, None.
* changed event.no_item_restriction to events.no_item_restricted and updated how that dict works. Now takes an itemName as key and returns an event, for events with by-name-only noun acceptance.
* moved the npc.location to be cardinalInstance during init, will only be str if self.location is a string that fails by_cardinal_str. I think it used to do it later because repr failed otherwise, but I think that was just during isolated testing because the location didnt' exist.
* changed set_up_game to not bother looking for magazine + tentacle instances, but just generate them directly. Otherwise it'll steal them from location if they're ever added to locations at init. This way it generates those items for inv at startup instead of stealing from locs.
* hopefully fixed cluster selection again, not sure when it broke but it should be more rigourous now.
* removed is_loc_current_loc as nothing calls it
* removed verb_requires_noun as it was only used by 'set' (which doesn't work yet) and it did some error printing better left to print_failures.
* removed two_parts_a_b and three_parts_a_x_b
* removed if isinstance(prospective_cardinal, dict) from 606 in verb_actions
* removed a duplicate check for format_tuple len 1 or 2 for look around in def look()
* removed 'event_type' from 'event' item_type.
* removed 'print_children_as_list from glass jar def. It was the only instance of that attr and was false anyway.

(eventRegistry is over 1k lines. Eep.)

Major notes:
* is_event_trigger is just a mess and needs some heavy checking/culling.
* `reason` going into is_event_trigger needs cleaning up. Sometimes it's a str, sometimes it's a tuple, sometimes it's a tuple in a tuple.
* Important one: currently, triggers either start or end, there are no 'contributes to the event' triggers. I need to add those. An event that needs you to collect 5 orbs, and only ends when you've done it. I don't want to check each time 'are you holding 5 orbs now', I want to know 'ah, you've collected all 5 orbs, now let me check if you're holding them'. so I need contribution-triggers to update event attr without ending the event.
* get_transition_nouns is used by def find() only. Anything else uses move_through_trans_obj, but it does the work to identify the noun itself in def enter(). Enter should use get_transition_nouns, no?
* re: avoiding the loop for get_components with inst_from_idx: if it has the format_tuple, it can just get the idx from there for the relevant kind, as well as know if there are multiples. That might be good.

check_triggers only checks start_triggers if there are no end_triggers, whether end_triggers failed or not. And given all events have an end_trigger (and may not have a start_trigger if they `start_current`), that means the 'start_triggers' half of check_triggers just straight up never runs.
So, 'check_triggers' should actually just be 'check_for_end_triggers' but is poorly named (and holds useless code that never runs).

I'm assuming 'no_item_restriction' was for events where say, there are multiple instances of 'magic orb' and any orb can participate in that particular event, instead of being item-instance specific (like the moss).

Updated to meet that idea.

Also """"""'d out the event.start_triggers section to make sure it's never referenced before deleting it.

I'm not touching item_dict_gen for this find-all-the-bad-things, my brain's hurting after just env_data and eventReg.

3.50pm
Hm.
'drop moss' fails because 'you're not holding one', even though I am, because I'm holding 'dried moss', not 'moss', and there's 'moss' nearby.
If i move away from the 'moss' obj, then it works. So I need to check compound_nouns even if it finds a local match.

Going to change itemreg init to apply more attributes manually. eg if electronics in item_type, self.is_charged, etc etc.

re: the moss thing, maybe I need to check using
`from_inventory_name(test:str)` in misc_unilities but also check against plural_nouns, which currently it doesn't do. Hm. This is for if holding 'dried moss' and then trying to do def drop() and not finding moss in inv, so it double-checks the inv items before reporting failure via local items. if no local items match then it correctly reports the compound noun in inv.

itemReg: if can_pick_up, add attr self.contained_in (currently it does this anyway but it doesn't add the attr openly so it's not in item.(attrs list) autofill)

5.27pm
'break jar' claims to break the jar, but the jar is still in tact and no glass shards are present.

Have just checked, and prior to today's edits, the broken items worked properly. So I've broken it somewhere in today's edits. eeeeeeh.

So now I gotta figure out which of the ten million tiny changes I made have broken it. Okay.
Most likely: the by_name switch to set from list.
Working on it.
5.33pm
partial improvement: break jar now separates dried flowers from jar, but the jar is still unbroken. This was in assign_colour.

Oh jeez. If you do 'break jar' again after breaking it the first time, the output is this:
"""
 .-           -.
[<  break jar  >]
 '-           -'

You smash the glass jar on the ground.





"""
All those blank lines.

Oh - turns out that's what the 'elif start_triggers' was for. For immediate_actions. Fixed now, all breaking properly again.

5.46pm
Oh, interesting.

 .-           -.
[<  drop moss  >]
 '-           -'

Failed to find the correct function to use for <verbInstance drop (9683c64b-047c-4976-9011-75dbbbe3ed1a)>: 'NoneType' object is not iterable

drop moss fails in the church.

1: church has no items.
2: only church north really has anything of note at all

Oh, I think the church was from an earlier iteration where I had to make sure every cardinal exists. Whereas now, it allows nonexisting cardinals and just makes appropriate arrangements. So it's breaking because it says 'this cardinal exists' but it doesn't have any of the expected data. Okay.

Oh, actually it's not the church being the bad thing, it's something in clusters specifically.

#   While fixing that, more moss issues:

pick up moss, works
drop moss: does not print any 'you drop the moss' print even though the event just failed. It should print the event failed text. Why didn't it?
pick up moss: finds the existing "Not new noun", but picks up something else instead.
drop moss: still doesn't print the failure text
pick up moss: now finds the original dropped moss. Should have found it the first time.

6.12pm
have checked, these errors are present in the last commit on main. So at least I haven't newly broken things.

Hm. I can get a total of 4 mosses now. Yeah it's broken, just slightly. Why is it not always taking the singular moss? I thought it did before...

Oh, now I have 7 mosses. Oops.

Okay, so 'pick up moss' is not correctly moving the shard from its current loc. It picks it up and adds to inv, but doesn't move it from current loc.

I think perhaps it's because that first 'drop' doesn't return correctly, if it fails to find an existing compound instance.

6.43pm
Okay, fixed it so it prints the failure message correctly. Need to fix it properly though because it should have the correct state_type already, but state_type is "end", not "failure".

Back to the issue: it's not picking up the single moss by default.
I set up 'singletons' in the separate_clusters fn to try to be more intentional about it.

Hm.

So:

Not new noun: [<ItemInst moss / (b39206f2df1f) / east graveyard / None / 3>, <ItemInst moss / (247433b7dd3d) / east graveyard / None / 0>, <ItemInst moss / (60a01c010fd6) / east graveyard / None / 0>]
SINGLETONS: [<ItemInst moss / (247433b7dd3d) / east graveyard / None / 0>, <ItemInst moss / (60a01c010fd6) / east graveyard / None / 0>]
shard:  <ItemInst moss / (a569f6be6136) / east graveyard / None / 3> //  cluster <ItemInst moss / (b39206f2df1f) / east graveyard / None / 3>
returning <ItemInst moss / (a569f6be6136) / north inventory_place / None / 1>
You pick up the moss, and feel it squish a little between your fingers.

After picking up and dropping 2 mosses (so I have 3 total instances), and taking moss again, if finds the 2 singletons, but generates a new one /instead/ of taking either of those. Whyyyyyy. Now I have 5 mosses again. Blaaaah

6.53pm
Okay, so it seems to be working again now. Will have to test it more thoroughly but it appears to be picking up singletons each time unless only clusters exist.

Also you can drop moss in the church now.

Oh, goddamn it. That quick fix for the event printing didn't work; now if the moss dries properly, it prints the success print, but then also prints the failure when the event ends. Okay. Well I knew I needed to properly fix it to recognise the 'failure' state_change.


Huh. If you take /two/ mosses to the church and try to drop one, it fails.
# [<  drop moss  >]
#
# Failed to find the correct function to use for <verbInstance drop (ceed8e9a-2bd6-45e1-aa1d-228768475eeb)>: cannot access local variable 'local_clusters' where it is not associated with a value

okay fixed that too.

Back to the event failure printing.
event end_type is 'end', not failure. I have a check here that checks the trigger for an end_type, and that should be what tells it it's a failure-type, not an end_type.

Okay, so the trigger just doesn't have end_type at all. It definitely should.

So, at init, the trigger has failure:
trig_data["item_trigger"].get("end_type"): failure

7.25pm
oh ffs. now 'go to shed' fails because nonetype has no attr 'place'.
Okay so it's because it figured that 'shed' meant 'shed door' but it assigned it as 'location'. but with no instance.

Okay. Now it checks compound_locations for the loc_entry text and gets the instance from place_by_name. 'go to shed' was failing occasionally if it found the location before the noun. Still means the parser could use some improvement so it properly gets that location instance, but for now this is a workaround that does the job. It's because it can only have one kind at the end of the parser, so if the sequencer then says 'no, you're a location', it doesn't have the location instance it would have. Thisis just a way of adding it back in.

7.09am 19/3/26
Adding more to the todo list from yesterday. Thing I was roughly up to verb_actions, I kept getting distracted.

7.32am
really, I should get the parts for verb_actions fns according to the format_tuple. Would make for more specific routing but also a lot of doubling up, and room for error. Well, different error; failure to include any possible format (or having to account for all variations) vs it making incorrect assumptions. idk. I do use the format tuples in some places, maybe I just need to formalise it. 'does it have 2 nouns', etc. Then only run it through the full get_correct_nouns if so. Though get_correct_nouns already only gets the second if there's a second noun found, so I guess it's not necessary. Idk. Anything that bulk identifies parts still needs me to untangle the parts that come from it so I'm not sure it helps. Probably depends on the fn.

I keep forgetting about `attributes {itemname}`. It's so handy for quick checks. Really need to remember it exists.

8.33am
Just realised I could rejig get_entries_from_dict to output verb_inst, verb_str, noun_inst, noun_str etc. Would still have to get the nouns separately (so maybe just exclude that from the result) (and it only gets one of each... hmmmmm)

maybe x_val outputs that output. So if x_val=2, outputs noun1 + noun2 instead of just noun2. Less looping.

10.37am
Note: `go into shed` from north graveyard says 'you're facing the west graveyard', but doesn't acknowlege the 'into'. It should mention that the door is closed.
Also, 'enter shed' opens the door even if you're in north graveyard when you write it. Surely it should only be if you're in the same cardinal, no? I think I've gone back and forth on that one.
Oh - maybe it's only if you're in the same cardinal, /unless/ you've observed the shed. So if you've been to west graveyard and left without going in, then 'enter shed' lets you in. If you've not even observed the shed, then it just takes you to the outside. Need to do that later, too braindead today.

11.35am
`look at graveyard` fails with `[not idx_kind and not (noun and verb)]Sorry, I don't know what to do with `None`.` but then prints what I want it to anyway.

5.50pm
hm. Recent changes have made the door not-hidden. .. fixed.

6.11pm
`throw jar at ground` should break the jar if it's weak enough.

6.36pm 'unlock padlock with key'/'use key on padlock' fails if for attribute in attr is off. Not sure what I'm missing.

1.17pm 20/3/26

Ah. 'is_key'. Should really remove that and use the 'key' in itemtype instead...
Also item_type needs to be 'item_types'. It's very rarely singular.

Okay I think I've removed 'is_key' from everywhere, now it just checks item_type directly.

Added check_itemtypes for this kinda thing.

2.20pm
'glass jar contains' is messy. Removed 'print_children_as_list: False' from glass jar. It turns out that if you use that, ln 1349 in itemReg prevents it from adding children to the list (unless it only contains starting children) but it still prints the first section, so it just says 'A glass jar, holding .'. And it still lists the contents of the jar afterwards, so it says:

#   You look at the glass jar:
#
#      A glass jar, holding a paperclip, and some dried flowers.
#
#   The glass jar contains:
#     a paperclip, dried flowers

[Note that the colouring is wrong for 'A glass jar, holding a paperclip, and some dried flowers.', the text is yellow with item-coloured item names, but the `, and` is white. Need to fix that to allow mid-str colouring to be maintained.]

I want to keep the 'a glass jar, holding ...' text, so I guess I need to prevent it printing the 'The {itemname} contains: \n{list}'. One or  the other.

Also, #TODO: I need to add 'A {itemname}, holding ' as a default string to containers if they don't have any_children descriptions provided.

Alright have fixed it, now it only prints that list if told if print_children_as_list is present and true. So if you don't want to have a line of text describing the children in the container and instead want it to print an item description and then list children after, do not add item descriptions and add print_children_as_list:True in the item def. Also amended item descriptions to not use child-including descriptions.

Added a cardboard box item to item defs and placed it in north graveyard, want to see how little data I have to give it before it errors. Just gave it item defs and the 'print_children_as_list' cause I want to test that too. Failed immediately with `Failed to find the correct function to use for <verbInstance look (7ce94335-93ef-4f54-bf87-770a8f2098fe)>: argument of type 'NoneType' is not iterable`
Ah. 'cause init_descriptions failed to apply a default if no description was found.

working on that, and realised that you can put things in boxes even if they're closed, apparently it doesn't check.

but print_children_as_list does work properly now. It either prints the children inline (if missing or false) or as a list below, but not both.

Now to fix the 'box is closed but still put stuff in' part. Ties in with what I saw the other day about only 'move a to b' checking item_size.

Error message is wrong for
`[<  take paperclip from box  >]`:

# There's no paperclip around here to take the cardboard box from.

Also:
'put battery in box' fails if there's already a battery in the box, even if I'm holding a different battery.

Oh. Padlock doesn't get given a size when it becomes pickupable from the gate event. Good to know.

Also, this description:
        "padlock": "an old dark-metal [[]] fffon a chain, holding the gate closedfff<< hanging loosely on a chain>>"
isn't correctly updated at the end of the event.

4.17pm
Fixed the padlock getting a size, and the description now updates properly. Also you can add multiple batteries, it prioritises inventory items when 'put x' so it only finds the local items if nothing else.

Have this:
`Inst has a location but isn't in by_location for old_loc. FIX THIS. old_loc: <cardinalInstance north graveyard (f0761966-b2aa-46f0-89f8-439b062b6810)>`
from picking up the padlock. I assume it didn't remove the item location when picking it up?
The command was 'take padlock', and the padlock was in a container that I didnt' specify (but that was accessible), so maybe it's because I didn't specify 'this is from a container' in def move() so it assumed the current loc == origin? Not sure. Need to look into it once I've had more sleep.

Also added a few lines in failure printing that checks noun open-ness, so even if it fails in the parser stage, it prints 'The x isn't open' and returns instaed of the messy 'there's no padlock to put the box in'.

fixed the missing origin, it only cleared prior loc if the item was in inv because I didn't account for 'put localitem in container', only 'put invitem in container'.

9.47am 22/3/26
I need to figure out how to do the wire cutters. They can't be a key even if the function is similar.

I think I need to either add a similar setup or modify the key/lock setup to include alike interactions. So 'cut wire with wirecutters' functions the same way as 'lock padlock with key' but with adapted output.

Phrasing it like that it makes more sense to just adapt the key/lock setup. It's really more about the resulting print statements than the function. Though it may have more than one possible key, which currently I don't think the locks can support.

Removed 'alt_names' from locations, none of them were used anyway.

Okay. So part of the difficulty with the ivory pot/wire is that you have to 'use wirecutters on pot', not the 'wire' itself, which is nonintuitive.
So I think I need to add a 'lock_item' object attr, so the ivory pot is not locked, but has a lock_item which /is/ locked. Similarly to the graveyard gate, though that stays locked because of the event, not the padlock itself. I don't want to have an event for every object that's locked by another obj. I think lock_item is the thing to do. So the 'wire' becomes the ivory pot's 'lock_item', and the wirecutters can cut/open the wire, which then makes the ivory pot unlockable.

Currently: 'unlock pot with cutters' prints 'you can't open pot with wire cutters'. Should say 'unlock'.

Also not sure why it fails. It has this:
 'requires_key': <ItemInst wire cutters / (75f828c1b0ae) / north testing grounds / None / >,

Ah, it fails because it's found a different wire cutters to the one it needs. Right. I need to either specify which specific item it is or specify 'anything with this name' instead of specific individual items.

Huh. Bizarrely it generated /three/ wire cutters, despite there only being one ever listed in loc_data. Good to know.

Well there are wire cutters inside the metal pot, but none of these three are there either. So it's just a mess all over.

item generation data:

INSTANCE: <ItemInst wire cutters / (fe171b17c12f) / north testing grounds / None / >
INSTANCE: <ItemInst wire cutters / (a6a88704ff1a) / north testing grounds / None / >
INSTANCE: <ItemInst wire cutters / (790f1fc3c073) / north testing grounds / None / >

but only this one is in 'item':

ITEM: (<ItemInst wire cutters / (fe171b17c12f) / north testing grounds / None / >, 'apply_loc_data_to_item')

INSTANCES are from item_dict, but 'ITEM' is from all_item_names_generated. So clearly somewhere is missing that bit. Damn. Will add it back in so I can see at which point it's being generated.

Things covered - 'get_item_from_defs', generate_child from item_defs, "generate_child item_from_str", "generate key from item_defs", "generate key from str", "new_item_from_str", "apply_loc_data_to_item".

Hm. No idea why it isn't adding to al_item_names_generated. Ah, because I added the lock, not the key. Makes sense.

So, in clean_relationships, it gets this:

item.requires key: wire cutters
maybe_key in registry.keys: <ItemInst wire cutters / (bbfaabd309fa) / north testing grounds / None / >

Ah, it failed because the wire cutters don't have the 'lock' listed as 'is_key_to'. Going to update it so it allows 'no is_key_to' as a viable option, so keys don't have to list their locks but if they do, it's followed.
Also set it to break after finding one, it wasn't set to previously. Oops.

Hm. Still doesn't work.

Hm.
apparently hasattr and attr is `maybe_key.is_key_to: None`, and yet ...

Ah, I had 'or' instead of 'and', so it failed that check because the attr does exist. Okay.

10.39am
Well now it only generates two of them. I guess that's something, techinically.
One is `apply_loc_data_to_item`, the other is `generate key from item_defs`.

OH. It's because there are technically two items that can be opened by it, and it's specifying that a key can only go to one lock. That's the issue. Like for when I was generating the iron key I needed to make sure it was generated and not borrowed from elsewhere, but I don't want all keys to be one use only.
Because it sets `setattr(maybe_key, "unlocks", item)`, then this ` hasattr(maybe_key, "unlocks") and getattr(maybe_key, "unlocks"):` is skipped on the next loop. So if it generates one wirecutters and uses that for the first ivory pot, it has to generate more wirecutters for the second ivory pot. Okay.
So I guess I just need to remove that limitation. They should be generated by loc_data, and only in maybe_key if no item exists, not just if it's already used.

Okay, now it's just one wirecutters generated. Goodgood.

So, I need to fix the issue of 'wirecutters have a specific unlock target'.
`'unlocks': <ItemInst ivory pot / (07b87ba25267) / south graveyard / None / >,`

when it should be all items that identify it as a key. I want to be able to tell the target (wire, lock, whatever) 'I can be unlocked by this thing', without having to also tell the key 'you only open this one'.

I imagine the former is more common, that a key-obj can open any suitable targets and not only a specific target. So, maybe I make the default setup 'maybe_key works as long as the lock identifies it as suitable', and have an attr in item_ or loc_defs for 'specific_key' for items that (for some reason) are more specified. Not sure why that'd be the case but useful to have I suppose.

So, locks_keys
(
    self.locks_keys[item] = maybe_key
    self.locks_keys[maybe_key] = item
)

needs to be sets of instances, for any matches.
item.requires_key = maybe_key  maybe needs to be a set too? Or I just use registry.lock_keys instead of storing that set on the key itself.
and for the key, instead of
`setattr(maybe_key, "unlocks", item)`, we just use locks_keys[maybe_key] as it's already generated.

For now I'm going to do it as-is, once it's fixed then I'll adapt it again for lock_objects.

For now, just doing
`item.requires_key = self.locks_keys[item]`
as a transition step so I can make the required changes and have testing being a bit easier.

For the items that have a specific key/lock match, that set will only be one item, for anything else it'll be any viable match.

11.27am
Okay, that seems to be working better now. Set it all up so keys and locks are sets, and the key/lock just carry the locks_keys set with them instead of a) a specific instance and b) a new set.
Still doesn't actually unlock yet  but that's because the verb_action still expects an instance, not a set. Only one pair of wire cutters are generated now. and the iron key still seems to be generated correctly. Will run a test once I've updated the lock fn.

okay, lock fn works again, now it just checks if noun_1 is /in/ requires_key rather than == to it.

Re: set_noun_attr: Just found an example of the 'multiple values'.
in lock_unlock, we send this:
# set_noun_attr(("is_locked", False), ("is_open", True), noun=lock)
and sometimes this:
# set_noun_attr(("is_locked", False), noun=lock)

I think maybe I need to make it a dict?

It gets tricky because in def drop() I send this
triggered, moved_children = events.is_event_trigger(noun_inst = noun, reason = "item_not_in_inv")
directly to is_event_trigger
which is what set_noun_attr sends to:
`if hasattr(noun, "event") and getattr(noun, "event") and hasattr(noun, "is_event_key") and noun.is_event_key:`
    `outcome, moved_children = events.is_event_trigger(noun_inst = noun, reason = values, event_type = event_type)`

Hm. 'leave shed' does work, but it now sends you to east graveyard instead of north. Oh, it's the opposite direction of the shed door - that's correct. oh, good. Okay.

#TODO: I need to change the colour of the event failure text for the moss event. It's ital grn and shouldn't be. Changed my mind on that. The event start text is plain, but the failure text isn't.

Also, just realised that there's no send to attr for 'put'. So if I put the moss somewhere, it likely won't trigger the event.
Tried to test, and 'put moss on ground' tries to 'put' a moss still on the ground (val 2) instead of the one in the inv. I thought I set the inv to prioritise inv items for def put?
Apparently not. 'put' is in `loc_w_inv_no_containers`. So maybe I need to do a run with inv only and then try again if nothing's found.
Really I should be doing that loop internally. For verbs, instead of a single scope, give it an ordered list; 'find one in inventory, if not find one locally' etc, depending on which verb it is.

12.07pm
Hm.
How come '{'noun': {'instance': <ItemInst stony ground / (e03d99df72d2) / west graveyard / None / >, 'str_name': 'stony ground', 'text': 'ground'}}}' is becoming

<ItemInst floor / (6577133071a7) / east graveyard / None / >?
Oh, well for one I suppose we are in east graveyard. Is west graveyard making the wrong one or is it a weird duplicate?
So only the west has the stone floor, everywhere else just has the default. Oops.
Have set a new attr to 'place', 'placewide_surfaces'. Here it's just the floor. Basically will overwrite any default 'True' or missing value for that surface-type for that location. If it specifies False or has a specifed surface, then it does't overwrite.

Reminder: You were doing the 'put moss on ground' thing before this. Finish that.

okay, place-wide flooring works.

have added 'moved_item' to check noun events wherever items are moved from inv more flexibly.

Need to decide if putting the moss in a jar outside ends the event. Instinctively, if the jar is open and it's an outside loc then it should end. But you can't turn the jar to prevent it or anything. Idk how to make it clear enough that it's not the jar that ends it, but the exposure. I can't test it based on 'is the container open', because it has to be open to add the item to it. If I put an item in a container and then close it immediately it should count as closed...
Maybe that's an event. 'moss_in_ext_container', tests to see if the container is_open==False by the next timeblock. If it fails, the moss event fails silently and it just never dries. Maybe.
So how would I want to do that. Clearly it's an exception, like
`"exceptions": ["current_loc_is_inside"],`. For now I'll just do a custom one but I'll need to generalise these later probably.

2.40pm
It's very messy but it does mostly work now. New issue though:
moss in jar. 'take moss from jar' = 'moss is now in your inventory'.
'drop moss' - 'you can't drop the moss, you have to get it out of the jar first'.
But the moss is in the inventory, not the jar. So it's missed an update somewhere.

2.57pm
specifically:
 .-                    -.
[<  take moss from jar  >]
 '-                    -'

OUTPUT NOUN: <ItemInst moss / (fcb870986ebd) / north inventory_place / moss_dries / ..24fc042bbcc2 / 1>

The moss is now in your inventory.
This keeps running over and over and the object never leaves the jar, and is only ever in the jar and my inventory once per.

Okay, fixed it. Issue was that the moves done within move_cluster_item didn't clear parent.children, so if you tried to pick up a singular with no competition from inside a jar it didn't leave children, despite successfully leaving. There's a neater way of doing it but this is good for now.

5.10pm
The glass jar's description doesn't work again. Now it just says 'It's a glass jar' always.

Ah, because of the routing for inst.children in init descriptions. Will fix.

5.33pm
Well it sort of was, but really move_cluster_item just wasn't removing the child from the parent correctly. I'm not sure why. Going to make a reusable 'clear from parent/old_loc' fn I can use as I need to call it a couple of times, though I really shouldn't need to. Too tired today though.

Is better now. Still could be improved, but better.

5.51pm
Hmph. Now wait_one_turn isn't ending properly. How'd I manage to do that?

Okay. so I found it and it makes sense, but does draw attention to flaw in this little event. What happens if I now go outside again? If the event has ended, then the countdown continues. If it hasn't ended, then what, it tracks the inside/outside of the jar forever?

11.07am 23/3/26
Alright. Need to figure out what I'm doing with wait_one_turn.
I think what I need to do is make it flexible itself. So any event can call wait_one_turn and provide its own requirements, instead of wait_one_turn itself declaring 'I care if this container is still open'.

Secondarily, the concept's still kinda bad as described above; if I put a thing in an open container, then take it inside within one turn, wait_one_turn ends. But if I put the thing down in an open container while outside, it doesn't end the event. so:
 - put moss in jar, wait outside, moss doesn't dry
 - put moss in jar, take moss inside, will continue drying
 - put moss in jar, go inside, go back outside, put jar w/ moss down outside, moss still dries.
I think I just need explicit rules for moss_dries as to how it deals w/ being in a container.
I think wait_an_hour is good because it lets you put it in a container, but how do I manage it after that.
Maybe... maybe it tracks the container if it has one? So if in container, then if the container is open in an outside loc it fails (after that initial one hour)? God this is so messy. I need to draw it out.

Okay. So.
initial pickup: run wait_one_turn.
If at end of wait_one_turn, item still in container:
    if container in inv, end with no effect.
    if container not in inv and inside, end with no effect.
    if container not in inv and outside and closed, end with no effect
    if container not in inv and outside and open, end by ending moss_dries
After wait_one_turn, moss_dries applies its rules as per normal:
    if moss not in inv:
        if moss in container:
            if (container in inv or (container outside and closed) or container inside):
                moss_dries continues
            else:
                moss dries ends
        else:
            if moss.loc outside:
                moss dries ends
            else:
                moss dries continues.
So that works, but I still need to track the container. Because what if I take the moss from container and put it directly outside without it ever being added to inventory? Or move it to a different location?
So... We need to track the contained_in, I suppose?

Added testing_locs and testing_events so I can try things out in a more limited environment.

Ah, note:
I have this error again:
`Inst has a location but isn't in by_location for old_loc. FIX THIS. old_loc: <cardinalInstance east graveyard (68b66c58-3692-4621-8327-b8a1393b2970)>` but I think it may only be happening when cluster objs are created. They're not added to the location on generation because they imediately go to inventory, but they inherit their parent's location. I think that's okay.

Oh. Interesting.

put moss in jar and wait 2 days, wait_one_turn runs as it should. But if I wait another 2 days, it still hasn't ended the moss_drying event - the turn taken for wait_one_turn doesn't always apply to moss_dries.
If I wait 3 days then it dries correctly, but wait_one_turn /doesn't/ trigger. It triggers on the /next/ wait.
So... Hm.
wait_one_turn /has/ to run on the next timeblock cycle, regardless of any other factor or trigger. And it has to run first (so the time can't pass if the obj is in an open container outside etc).
If there is also another trigger, it needs to run depending on the outcome of wait_one_turn.
If wait_one_turn... wait, succeeds or fails?
I think 'succeeds' means it is able to end the trigger event. Yes.
So, wait 3 days.
the timeblock change triggers wait_one_turn, which runs its tests. If it succeeds, moss_dries is ended, regardless of the time passed. So moss_dries is ended and no future triggers are enabled.
If wait_one_turn ends ends without succeeding, the timeblock is applied to moss_dries.

Honestly I'm thinking of just having a separate script where I can specify exactly how these events are handled. It's stupid, because I have the JSON for that, but neither the JSON or the eventReg are set up to handle sending/recieving detailed instructions.

Huh. So if I pick up moss again after it fails, and put it in the jar (placed outside), moss_dries ends immediately even though wait_event exists. But the first time it runs, that doesn't happen.

Oh hell no.

Compound target: <ItemInst moss / (22a5a1d82132) / north no_place / None / 0> // shard: <ItemInst moss / (0d0746c4a3d4) / north inventory_place / moss_dries / ..a8fff92676a6 / 1>
AT END OF COMBINE_CLUSTERS: Compound_target: <ItemInst moss / (22a5a1d82132) / north no_place / None / 1> // shard: <ItemInst moss / (0d0746c4a3d4) / east graveyard / moss_dries / ..a8fff92676a6 / 0>
it chose a compound target inside of a container without me specifying. Goddamn it.

take moss
put jar down
put moss in jar
take moss
put moss down

Okay so something's gone wrong here.
was in container: True / parent; <ItemInst glass jar / (a410c2f20e68) / east graveyard / wait_one_turn / ..fec01940a72a / > / parent.children: {<ItemInst dried flowers / (4506260348a3) / north no_place / None / >, <ItemInst moss / (0d0746c4a3d4) / north no_place / moss_dries / ..a8fff92676a6 / 1>, <ItemInst moss / (22a5a1d82132) / east graveyard / None / 1>}
that moss 2132 never got picked up, it's still in the graveyard. So why is it in children? 76a6 is correct (and no_place, but I never picked up another singleton moss.)
And then when I get compound_target to put the mosds down, it is:
Compound target: <ItemInst moss / (22a5a1d82132) / north no_place / None / 0> // shard: <ItemInst moss / (0d0746c4a3d4) / north inventory_place / moss_dries / ..a8fff92676a6 / 1>
So the moss that was in graveyard is now in inventory

But it's not listed in inventory, nor in the jar.
Well, the jar says it's there:
`A glass jar, holding some dried flowers, and a clump of moss.`
but the print return is
`The moss don't seem to be in the glass jar.`. Even though it's identified the correct moss.
Goddamn it...

Okay. So you pick up the jar, put down the jar, put the moss in the jar.
At that moment, moss_dries is still running.
But by the time wait_an_hour is in intake (`Added to eventIntake:`), moss_dries is already ended:

# is_event_trigger: noun event: <eventInst moss_dries ..d58a7da2f141 // state: 1>
# Noun <ItemInst moss / (3987b7859433) / north no_place / moss_dries / ..d58a7da2f141 / 1> is an event trigger for <eventInst moss_dries ..d58a7da2f141 // state: 1>
# trig is timed_trigger: `<[timedTrigger]] 88c9964a-7844-49c1-b88e-c43d67acfb0a for event moss_dries, event state: current/ongoing, Trigger item: moss/3987b7859433>` `<---- still running`
# reason in trig.triggers: item_not_in_inv /// {'item_not_in_inv'}
# trig.exceptions: {'current_loc_is_inside', 'item_in_container_dry'}
# noun.contained_in: <ItemInst glass jar / (ab5d53bd6d33) / east graveyard / None / > // item in ext container
# container: <ItemInst glass jar / (ab5d53bd6d33) / east graveyard / None / > // location: <cardinalInstance east graveyard (8bc9a040-ff3b-48ea-bc9b-dced3e808612)> // inside?: False
# Added to eventIntake: <eventIntake wait_one_turn (start_trigger: None), (end_trigger: {'timed_trigger': {'time_unit': 'hour', 'full_duration': 1, 'required_condition': {'item_is_open': 'trigger_item'}, 'persistent_condition': True, 'condition_item_is_start_trigger': True, 'exceptions': ['current_loc_is_inside'], 'end_type': 'success', 'effect_on_completion': {'end_event': <eventInst moss_dries ..49d494c751f7 // state: 0>}}})>

OH, it's because that's the wrong event.

 <eventInst moss_dries ..d58a7da2f141 // state: 1>
 hasn't ended.
<eventInst moss_dries ..49d494c751f7 // state: 0> has.
and it has <eventInst moss_dries ..49d494c751f7 // state: 0> as the end_event event for wait_an_hour. Okay.

Okay so part of the broader issue is that the moss isn't actually getting put down when it fails the event:

Trigger: <[Trigger]] f739f787-ed85-4662-bb1a-394225db040e for event moss_dries, event state: current/ongoing, Trigger item: moss/5cf3cc80091e> // End_type: failure
You put down the still-damp moss.
Remove event on end and/or failure: <eventInst moss_dries ..5b55a436fe66 // state: 0>
Event ended for noun <ItemInst moss / (5cf3cc80091e) / north no_place / None / 0>
End of event <eventInst moss_dries ..5b55a436fe66 // state: 0> complete.

Which is weird because it's in no_place, which shouldn't fail it. Both because no_place is (or should be) an excluded location, and because even if not, no_place == inside. So it shouldn't fail regardless.

And regardless of all that -

You're facing east. You see a variety of headstones, most quite worn, and decorated by clumps of moss.

# [<  take moss  >]

# Not new noun: [<ItemInst moss / (5cf3cc80091e) / north no_place / None / 0>, <ItemInst moss / (34f5dfc7555e) / east graveyard / None / 2>]
# There's no moss around here to take.

There is clearly moss there. It's failing to find 091e which is annoying and I'll deal w/ that, but it should take from the compound if that's all that's found.

slight diversion to fix this:
# Set noun to <ItemInst moss / (469503f92919) / north no_place / moss_dries / ..dbf9daf412b1 / 1>; matching name, is child of <ItemInst glass jar / (59ca8478ace8) / north inventory_place / wait_one_turn / ..195d81dd5b13 / >
# The moss don't seem to be in the glass jar.

OH, the noun_reason is wrong because the autoselect picked the wrong moss. Right.

Okay, so with that resolved, next:
`<ItemInst moss / (5b2ba42a78e1) / east graveyard / None / 1> is not in inv_place OR NO_PLACE. This is bad, how are we combining if not removing from inventory?`
in contrast to what I said earlier today, this error is actually bad; in this case, we've picked up random moss and added it to jar instead of putting the moss in the jar from inventory.

Why did we not take from inventory first? I thought I decided already that was the intention.

Not sure why it's failing, but for now, have added a quick check above get_correct_cluster_inst in find_local_item_by_name, where if access_str == "drop_subject" it explicitly looks for items in inventory with that name instead of sending to get_correct_cluster_inst

Hm.

'put moss in jar'
'take jar'
'put moss in jar' - moss already in jar
'take moss from jar' - removes blue moss
'put moss in jar' - adds blue moss to jar
'put moss in jar' - adds new singleton pink to jar

So...... why the difference? I assume just random chance, if it picks the inv item or not first changes the routing.

Also, 'put moss in jar' breaks the cluster selection in a weird way:

New noun: <ItemInst moss / (b916a477556e) / east graveyard / None / 2>
You put the moss in the glass jar.
it lets you pick up plural parts, which should never be allowed.

okay, so move_cluster_item output 'process_as_normal', which should only ever happen if it's a singleton.
Hm. It's returning no_local_compound...
Oh, because I'm putting it directly into a jar. It's not looking for a local compound because containers never compound, but also means that it returns a plural because it never hits that check. Okay.

2.48pm
fixed the cluster issue and updated def separate().

3.04pm
Fixed some more but clusters are still weird.

So, I have this:
{<ItemInst moss / (87d14169f2a5) / north no_place / moss_dries / ..46b6aed57105 / 1>, <ItemInst moss / (30ab6ae0d898) / east graveyard / None / 2>}

which is correct. 2a5 is in the jar.
Then if I 'put moss in jar':
`compound_target: <ItemInst moss / (6e307df9fe8f) / north inventory_place / None / 1> // shard: <ItemInst moss / (30ab6ae0d898) / east graveyard / None / 1>`

and the result is
`{<ItemInst moss / (87d14169f2a5) / north no_place / moss_dries / ..46b6aed57105 / 1>, <ItemInst moss / (30ab6ae0d898) / east graveyard / None / 1>, <ItemInst moss / (6e307df9fe8f) / east graveyard / None / 1>}`

which is fine.

but then you do 'put moss in jar' again, and:
`{<ItemInst moss / (87d14169f2a5) / north no_place / moss_dries / ..46b6aed57105 / 1>, <ItemInst moss / (30ab6ae0d898) / east graveyard / None / 1>, <ItemInst moss / (6e307df9fe8f) / north no_place / None / 1>}`
so two successfully moved, but the last one is still in graveyard.
except if you look around:
`You're facing east. You see a variety of headstones, most quite worn, and not much else. It's quite empty here...`

I really need to formalise the 'set locations properly' part. I imagine I've routed around it in the changes to get_cluster.

Also the jar isn't applying the x3 again. God fucking dammit.

okay. So: add new singletons to by_location.
# alt: have changed by_location to just get items by their .location instead of a separate set. Not sure how I feel about it yet.

Oh, damn. I was excluding scenery items from by_location.

Okay so I need the separate by_location set for that least that reason, though I could work around it elsewhere if I need to. For now that's fine.

Alright so the 'this thing is not in by_location' was because I was running clear_parent after the manual loc clearing. Fixed that now.

hmph.  Now 'drop moss' no longer adds it to current loc. God I just keep going in circles....

Fixed that I think. We'll see.
Next:
events broke again. Dropping the moss fails if it's already dropped one. I think it's just a selection issue.

------
8.39pm
have to add the originating event to the event_trigger but I think it'll work after that.
I fixed the issue from above already, I'd missed a place where it still expected events.by_name to be singular instead of a set.

10.33am 24/3/26
Need to remember now what was broken.

Cant' remember. Just running it to find errors. Events are pretty broken. Specifically, wait_an_hour no longer triggers at all; it doesn't add the moss obj to the trigger, though it does add it to the event and the timedTrigger.

11.33am
fixed that.

okay, next issue: It's not adding the exceptions to wait_an_hour, so it never checks the location/state of the event item.

okay so it's

god i don't know. i can't think.

bleh.
take from compound moss 9c52, pick up shard  051.
moss dries starts  f147e1157639 with shard 051.
put moss in jar, wait_one_turn starts for noun `glass jar`
take jar
wait_one_turn still going
moss_dries still going
wait 1 hr
wait_one_turn ends moss_dries because 'effect_on_completion' after finding no exceptions (emptry set)
then wait_one_turn ends itself because it's done.


(trig_data includes all triggers in that category:
trig_data: {'timed_trigger': {'time_unit': 'hour', 'full_duration': 1, 'required_condition': {'item_is_open': 'trigger_item'}, 'persistent_condition': True, 'condition_item_is_start_trigger': True, 'exceptions': ['current_loc_is_inside'], 'end_type': 'success',
'effect_on_completion': {'end_event': 'trigger_event'}}, 'event_trigger': {'trigger_item': 'trigger_event', 'triggered_by': ['event_ended'], 'end_type': 'failure'}}
make sure that's accounted for.)
wait event 6667 exists but,
`Trigger: <[timedTrigger]] 8fef884c-57ba-4896-89b1-40d21e34de7b for event wait_one_turn, event state: current/ongoing, Trigger item: glass jar/38024c57f6e5>`
`Trigger: <[Trigger]] 0dc22a68-dcf9-4006-be43-f1b7f5db444f for event wait_one_turn, event state: current/ongoing, None>`
That second trigger should have the originating event as trigger_item (moss_dries), so if moss_dries fails the event ends.

11.57am
Oh. It seems to work now. Will need more testing this afternoon, but apparently when I indented for-item_in_trig_types I hadn't included timed_trigger in the list of 'for', so it didn't hit that part. Will test more later, support now.

10.49am 25/3/26
Today:
Working on events again. Currently if you pick up moss and put it in the jar, that triggers wait_an_hour. If you then put the jar down and wait 3 days, it immediately succeeds moss_dries, as that is checked first before wait_an_hour can run, and wait_an_hour doesn't run again until the next timeblock.

Issues:
 - wait_an_hour isn't given the trigger_event as trigger_item, so the event ending doesn't end wait_an_hour (eg if you put moss down outside, moss_dries ends immediately, so wait_an_hour should end along with it)
 - wait_an_hour is not given priority, so 'wait 3 days' should be checking wait_an_hour first in case that fails moss_dries, but currently it's the other way around (probably just random chance which comes first).

 - Also, currently (though this won't happen if I fix the above, I should still fix it fundamendally) if you wait an hour after waiting 3 days (so moss_dries is already ended), I get this:
 `Trigger exceptions for trigger <[timedTrigger]] f1aea358-bb1f-44f5-b8c0-9ee21790e43d for event wait_one_turn, event state: current/ongoing, Trigger item: glass jar/7494173e2065>: {'current_loc_is_inside'}`
 `Failed to find the correct function to use for <verbInstance time (c2c32ba7-6573-4eb3-9c89-9a5f2239f141)>: eventRegistry.current_loc_inside() got multiple values for argument 'noun'`

 - also also: 'wait an hour' only starts sometimes. I need to figure out why. Might do that first.

# why does `wait_one_turn` only run sometimes??
 when it does run:
    pick up moss (moss_dries starts)
    put moss in jar (item_not_in_inv triggers the exception in moss_dries and wait_one_turn is started after this:
        `trig is timed_trigger: <[timedTrigger]] 9a38b91b-08bb-4f4c-b4c3-3208aaa1c4b9 for event moss_dries, event state: current/ongoing, Trigger item: moss/03bfcc9731e4>`
        `trig.item_inst == noun: <ItemInst moss / (03bfcc9731e4) / north no_place / moss_dries / ..18be97fae117 / 1> / event: <eventInst moss_dries ..18be97fae117 // state: 1>`)
    with `self.current_loc_inside(self, trigger, event, noun)`
    if I remove the 'self' here, it breaks. Not sure why it needs it but apparently it does?

When it doesn't run:
    Exact same commands.
    pick up moss (moss_dries starts)
    put moss in jar (item_not_in_inv triggers), but this end trigger doesn't trigger:
    `event.end_triggers: {<[Trigger]] a1281dca-1131-4fdf-afaa-e5975f3cc256 for event moss_dries, event state: current/ongoing, None>, <[timedTrigger]] a53bdb4a-a5fb-4766-b814-1c0f70de245f for event moss_dries, event state: current/ongoing, Trigger item: moss/d840be8728d2>, <[timedTrigger]] e8342743-433c-4853-81b2-163ccdb7fca7 for event moss_dries, event state: current/ongoing, Trigger item: moss/d840be8728d2>, <[Trigger]] d714511a-2043-4e61-9f03-d84c035f7d2d for event moss_dries, event state: current/ongoing, Trigger item: moss/d840be8728d2>}`
  in the version where it works, the end_triggers print is:
    `event.end_triggers: {<[timedTrigger]] 3d099f45-4244-4165-ad26-70a5556d0368 for event moss_dries, event state: current/ongoing, Trigger item: moss/279ce495f820>, <[Trigger]] ada9bb2a-388e-44a5-a78e-25440036a34c for event moss_dries, event state: current/ongoing, Trigger item: moss/279ce495f820>, <[timedTrigger]] 78069a65-3f6b-4e4c-aad1-310986d9d517 for event moss_dries, event state: current/ongoing, Trigger item: moss/279ce495f820>, <[Trigger]] d2ac3d41-506b-487d-a3c2-8b0f7013ec14 for event moss_dries, event state: current/ongoing, None>}`
Thoughts:
    Well I've just realised moss_dries has 2 triggers each for timed and standard. So maybe I just fix that first.
These are the triggers for moss_dries:
* <[Trigger]] 388fbcb0-65be-4d6d-be23-963da639799c for event moss_dries, event state: current/ongoing, Trigger item: moss/279ce495f820>
* <[timedTrigger]] 3d099f45-4244-4165-ad26-70a5556d0368 for event moss_dries, event state: current/ongoing, Trigger item: moss/279ce495f820>
* <[Trigger]] ada9bb2a-388e-44a5-a78e-25440036a34c for event moss_dries, event state: current/ongoing, Trigger item: moss/279ce495f820>
* <[timedTrigger]] 78069a65-3f6b-4e4c-aad1-310986d9d517 for event moss_dries, event state: current/ongoing, Trigger item: moss/279ce495f820>
* <[Trigger]] d2ac3d41-506b-487d-a3c2-8b0f7013ec14 for event moss_dries, event state: current/ongoing, None>
There should only be 2.

This is the 'added_to_intake' data for moss_dries:
ADDED TO INTAKE:
eventIntake moss_dries (
    start_trigger: {
        'item_trigger': {'match_item_by_name_only': True, 'trigger_item': 'moss', 'trigger_location': None, 'triggered_by': ['item_in_inv'], 'print_description_plain': True}}),
    (end_trigger: {
        'timed_trigger': {'time_unit': 'day', 'full_duration': 3, 'required_condition': {'item_in_inv': 'moss'}, 'persistent_condition': True, 'condition_item_is_start_trigger': True, 'end_type': 'success', 'effect_on_completion': {'trigger_event': 'finding_dried_moss', 'init_items': {'item_name': 'dried moss', 'use_trigger_inst_location': True, 'use_trigger_inst_colour': True}, 'remove_items': {'item_name': 'moss', 'item_is_trigger_inst': True}}},

        'item_trigger': {'trigger_item': 'moss', 'trigger_location': None, 'triggered_by': ['item_not_in_inv'], 'exceptions': ['current_loc_is_inside', 'item_in_container_dry'], 'end_type': 'failure', 'print_description_plain': True}})

So I'd be expecting a total of three triggers

I'm changing the trigger reprs to give a little more data.

Okay. So one of the wait_one_turn triggers has the exceptions, and the other doesn't.
And it's the same for the timedTrigger(s): there should only be one, but two are aded, with the second missing the exceptions and having an empty set.
For moss_dries it's the same thing; two triggers for each, with the second lacking trigger item, 'triggers' (eg 'item_not_in_inv') and exceptions.

Okay. so the duplication was because of the for loop, I was doing 'if x in trig_data', so each one found each other one regardless of which they were themselves. That part was written before the loop maybe? I'm not sure.

also, if you wait 3 days and it picks the wait_an_hour trigger first, moss_dries never triggers.

I think I need to add priority. So it checks high priority events first, then anything else.

Oh - the meta 'print events by name' is being weird because it'll list 'events.by_name' as including moss_dries, but then get("moss_dries") would fail. Just realised it's 'cause there's no events in that name. Need to remove the name from the dict if the last entry is removed so it's less confusing.

Hm.
So, trigger_dict is still doing the same weird thing.

Trigger_dict after initial generation: {'event': <eventInst [moss_dries] [ID:034eb] [state: 2]>, 'end_type': 'end', 'trigger_model': 'item_trigger', 'trigger_type': 'end_trigger', 'trigger_item': <ItemInst [moss ID:de8f3845e760] [loc:north inventory_place] [event:'moss_dries' ID:034eb state: 2] [clusters: 1]>, 'trigger_item_loc': <cardinalInstance north inventory_place (da8fa984-1787-454e-8eed-9b6235653768)>, 'trigger_actions': ['item_not_in_inv'], 'item_flags_on_start': None, 'item_flags_on_end': None, 'trigger_exceptions': ['current_loc_is_inside', 'item_in_container_dry'], 'timed_trigger': {'time_unit': 'day', 'full_duration': 3, 'required_condition': {'item_in_inv': 'moss'}, 'persistent_condition': True, 'condition_item_is_start_trigger': True, 'end_type': 'success', 'effect_on_completion': {'trigger_event': 'finding_dried_moss', 'init_items': {'item_name': 'dried moss', 'use_trigger_inst_location': True, 'use_trigger_inst_colour': True}, 'remove_items': {'item_name': 'moss', 'item_is_trigger_inst': True}}}}

Trigger_dict after initial generation: {'event': <eventInst [moss_dries] [ID:034eb] [state: 2]>, 'end_type': 'end', 'trigger_model': 'timed_trigger', 'trigger_type': 'end_trigger', 'trigger_item': <ItemInst [moss ID:de8f3845e760] [loc:north inventory_place] [event:'moss_dries' ID:034eb state: 2] [clusters: 1]>, 'trigger_item_loc': <cardinalInstance north inventory_place (da8fa984-1787-454e-8eed-9b6235653768)>, 'trigger_actions': None, 'item_flags_on_start': None, 'item_flags_on_end': None, 'trigger_exceptions': None, 'timed_trigger': {'time_unit': 'day', 'full_duration': 3, 'required_condition': {'item_in_inv': 'moss'}, 'persistent_condition': True, 'condition_item_is_start_trigger': True, 'end_type': 'success', 'effect_on_completion': {'trigger_event': 'finding_dried_moss', 'init_items': {'item_name': 'dried moss', 'use_trigger_inst_location': True, 'use_trigger_inst_colour': True}, 'remove_items': {'item_name': 'moss', 'item_is_trigger_inst': True}}}}

The second one (which I don't know why it exists) is missing data for:
'trigger_actions': None,
'trigger_exceptions': None,

Okay. So it's making two dicts, one for timed_trigger and one for event_trigger. But they're merging their dicts. The event_trigger shouldn't have the timed_trigger data in the dict, surely.

3.02pm
Hm.
The priority kind of works but not completely.

If you immediately wait three days, it does check wait_ first, but then immediately moss_dries succeeds (and then errors because it already ended before succeeding)

End of event <eventInst [moss_dries] [ID:ab8b3] [state: 0]> complete.
^ moss dries is successfully ended by wait_one_turn

3.31pm
Bit more, improved a bit. But -
Now, if you ptu the moss in the jar, and then take the moss from jar, and put the jar down outside, it still fails moss_dries because the jar isn't in inv. So I need a child_obj check, to confirm that the child is still present before checking anything else.

Adding `Required_condition not known: child_obj_is_child // [value (child_item])` to eventReg trigger_actions breaks the jar event, I assume because it's expecting only one item in required_condition.

Okay. So, eventHandling is being used now, I'm just dictating exactly how the item interactions should work there. Far simpler. I'll remove some of the data from wait_one_turn later so make it more flexible, and just base its specific function on which exception it uses.

For now: I still need to solve the mystery of the disappearing moss.
take moss (blue)
put moss in jar (blue)
take jar
put moss in jar (magenta (591))
put moss in jar (magenta2 (7df))
wait 3 days:
    container in inv so continues then ends for the jar and one of the mosses. So one moss is dry, but... then if you print all 'moss' items, there are only two.

Though, if you look for 'dried moss' it exists in no_place - but isn't shown when you print the jar contents.

It seems like maybe the dried moss just isn't properly added as an item for some reason. meta control gives me this:
`Finding instance for `dried moss`...`
`Instance found for dried moss: None`
So it sort of exists. Maybe the moss isn't disappearing then.
Though, it needs to repeat the end_event for each item, not just one per timeblock.

Also it seems like there's more moss than there should be?
We take 588 from 4db to inv
we take --oh, we take 4db from inv to jar which triggers wait_one_turn.
then we take jar
then put moss 4db in jar, leave moss cea behind
then put cea in jar
but then put 4db in the jar again

but then no, they disappear again:
(diff run so diff ids)
<ItemInst [moss ID:2fe49da7e33e] [Container: <ItemInst [glass jar ID:de623b208258] [loc: north inventory_place] [event:'wait_one_turn' ID:4e7ec state: 1] >] [event:None] [clusters: 1]>,
<ItemInst [moss ID:b0da84acf064] [Container: <ItemInst [glass jar ID:de623b208258] [loc: north inventory_place] [event:'wait_one_turn' ID:4e7ec state: 1] >] [event:None] [clusters: 1]>,
<ItemInst [moss ID:957f5545a99b] [Container: <ItemInst [glass jar ID:de623b208258] [loc: north inventory_place] [event:'wait_one_turn' ID:4e7ec state: 1] >] [event:'wait_one_turn' ID:4e7ec state: 1] [clusters: 1]>

^^ put all the mosses into the jar.
Then I do 'take moss from jar' x3, and end up with:
{<ItemInst [moss ID:2fe49da7e33e] [loc: north inventory_place] [event:'moss_dries' ID:a4a6a state: 1] [clusters: 1]>,
<ItemInst [moss ID:b0da84acf064] [loc: north inventory_place] [event:'moss_dries' ID:a426c state: 1] [clusters: 1]>}

On the first 'take moss from jar', this is the children of the jar:
parent.children:
{<ItemInst [dried flowers ID:96083db251f9] [Container: <ItemInst [glass jar ID:de623b208258] [loc: north inventory_place] [event:'wait_one_turn' ID:4e7ec state: 1] >] [event:None] >,
<ItemInst [moss ID:b0da84acf064] [Container: <ItemInst [glass jar ID:de623b208258] [loc: north inventory_place] [event:'wait_one_turn' ID:4e7ec state: 1] >] [event:None] [clusters: 1]>,
<ItemInst [moss ID:957f5545a99b] [Container: <ItemInst [glass jar ID:de623b208258] [loc: north inventory_place] [event:'wait_one_turn' ID:4e7ec state: 1] >] [event:'wait_one_turn' ID:4e7ec state: 1] [clusters: 1]>,
<ItemInst [moss ID:2fe49da7e33e] [Container: <ItemInst [glass jar ID:de623b208258] [loc: north inventory_place] [event:'wait_one_turn' ID:4e7ec state: 1] >] [event:None] [clusters: 1]>}

moss ID:b0da84acf064 is moved and added to inventory.
But then when I do `take moss from jar` a second time:
parent.children:
{<ItemInst [dried flowers ID:96083db251f9] [Container: <ItemInst [glass jar ID:de623b208258] [loc: north inventory_place] [event:'wait_one_turn' ID:4e7ec state: 1] >] [event:None] >,
<ItemInst [moss ID:2fe49da7e33e] [Container: <ItemInst [glass jar ID:de623b208258] [loc: north inventory_place] [event:'wait_one_turn' ID:4e7ec state: 1] >] [event:None] [clusters: 1]>}

Two are gone, not one.
The 'parent.children' list above is the last time that ID is printed, and it's just gone.


Also, the 'trigger_item' only being a single item breaks when it's the event, because the jar can have multiple to-dry mosses in it, and it only has

dir: {'id': '2a5407a3-5ee1-4b28-97a0-f3429f8e0484', 'short_id': 'e0484', 'event': <eventInst [wait_one_turn] [ID:4e7ec] [state: 1]>, 'state': 1, 'triggers': {'event_ended'}, 'exceptions': set(), 'end_type': 'end', 'start_trigger': False, 'end_trigger': True, 'trigger_item': <eventInst [moss_dries] [ID:496f1] [state: 1]>, 'is_item_trigger': False}

Moss 99b still exists as a trigger item, and that event apparently is still going:
Getting `Event triggers`...
* <[Trigger] [ID:a1b92] [event: moss_dries / state: 1 / ID:a1b92] [Trigger item: moss/957f5545a99b]>
* <[Trigger] [ID:2f2df] [event: moss_dries / state: 1 / ID:2f2df] [Trigger item: moss/957f5545a99b]>
* <[timedTrigger] [ID:25842] [event: moss_dries / state: 1] [Trigger item: moss/957f5545a99b]>

* <ItemInst [moss ID:957f5545a99b] [loc: north no_place] [event:'wait_one_turn' ID:4e7ec state: 1] [clusters: 0]>
99b is apparently still in the jar, but looking at the jar's attr it only holds the flowers (which matches the printed description).
So I guess something in the event management is breaking the location/not updating it properly? No errors printed which is kind of the bad version of this happening but I'll sort it.

So, what needs doing:
    - more than one item_inst for events, or better event item management in general (eg a global 'event_items' dict with event[item:role]) or smth
    - clarify how/when items are moved and make sure the relevant loc set is updated. Maybe just set it to print when it moves something for now. Route it through a 'set loc' fn so I can manage that print more readily.

Oh, maybe a direction to figuring out the weird moss duplication(?):

The first 'put moss in jar' prints this:
After combine_clusters: Shard: <ItemInst [moss ID:ddcc314cb965] [loc: east graveyard] [event:None] [clusters: 1]> // compound target: <ItemInst [moss ID:6aeefec14714] [loc: east graveyard] [event:None] [clusters: 1]>
old_container: None / new_container: <ItemInst [glass jar ID:edcffdcfe8c9] [loc: north inventory_place] [event:'wait_one_turn' ID:739dd state: 1] > / location: None
You put the moss in the glass jar.

But thereafter it prints this:
After combine_clusters: Shard: <ItemInst [moss ID:6aeefec14714] [loc: east graveyard] [event:None] [clusters: 1]> // compound target: no_local_compound
no local compound, returning shard from move_cluster_item
old_container: None / new_container: <ItemInst [glass jar ID:edcffdcfe8c9] [loc: north inventory_place] [event:'wait_one_turn' ID:739dd state: 1] > / location: None
Added <ItemInst [moss ID:6aeefec14714] [Container: <ItemInst [glass jar ID:edcffdcfe8c9] [loc: north inventory_place] [event:'wait_one_turn' ID:739dd state: 1] >] [event:None] [clusters: 1]> to new container. Is it in any locations?
You put the moss in the glass jar.

Well, that's the first to put moss in jar after picking it up. But I put moss in the jar the firs time, and it went through the whole event check rigamarole for wait_one_turn because that moss had been in my hand previously. Putting moss directly in the jar without picking it up doesn't trigger moss_dries to generate, though it probably should.

But yeah. Don't know why, but removing one moss from the jar removes two.
Maybe something about how the moss sets its event to wait_one_turn?

Okay. Have stopped it adding the child_item as event_inst, which for now is very specific to wait_one_turn and will need a better route (that dict described earlier, probably) but will do for testing this.

Okay so it really does seem that when it prints

After combine_clusters: Shard: <ItemInst [moss ID:c2831d660f5e] [loc: east graveyard] [event:None] [clusters: 1]> // compound target: <ItemInst [moss ID:0387635721a0] [loc: east graveyard] [event:None] [clusters: 1]>
old_container: None / new_container: <ItemInst [glass jar ID:b86aca4e8c71] [loc: north inventory_place] [event:'wait_one_turn' ID:d213c state: 1] > / location: None
You put the moss in the glass jar.

it's actually failed.
Because after that, this is what we have:
{<ItemInst [moss ID:c2831d660f5e] [loc: east graveyard] [event:None] [clusters: 1]>,
<ItemInst [moss ID:0387635721a0] [loc: east graveyard] [event:None] [clusters: 1]>,
<ItemInst [moss ID:c1623aeb9ef7] [Container: <ItemInst [glass jar ID:b86aca4e8c71] [loc: north inventory_place] [event:'wait_one_turn' ID:d213c state: 1] >] [event:'wait_one_turn' ID:d213c state: 1] [clusters: 1]>}

and these are the local items:
{<ItemInst [headstone ID:514e44b68f52] [loc: east graveyard] [event:None] >, <ItemInst [desiccated skeleton ID:3b69fd7af88b] [loc: east graveyard] [event:None] >, <ItemInst [moss ID:0387635721a0] [loc: east graveyard] [event:None] [clusters: 1]>}

so c2831d660f5e, that was apparently added to jar, is just gone.
Alright. Now I know. Will fix.

Okay, this makes sense now:
Removed <ItemInst [moss ID:306a3733d589] [loc: east graveyard] [event:None] [clusters: 1]> from <cardinalInstance east graveyard (c82da0f2-b44b-4d49-a4a3-8b710b1f9e8d)>. Current location for inst is <cardinalInstance east graveyard (c82da0f2-b44b-4d49-a4a3-8b710b1f9e8d)>

alright so specifically:
if compound_target == "no_local_compound", then the move gets done after the cluster section, and it works properly.

Hm.
You still loose a moss when taking from jar. But you do only add a total of 3 now, so that's an improvement ish.

Yeah. So it starts with

<ItemInst [moss ID:874951abb31b] [Container: <ItemInst [glass jar ID:ddc35155a44f] [loc: north inventory_place] [event:'wait_one_turn' ID:303b0 state: 1] >] [event:'moss_dries' ID:16375 state: 1] [clusters: 1]>,
<ItemInst [moss ID:6383e8f99ddd] [Container: <ItemInst [glass jar ID:ddc35155a44f] [loc: north inventory_place] [event:'wait_one_turn' ID:303b0 state: 1] >] [event:None] [clusters: 1]>,
<ItemInst [moss ID:45a70b6b5a6a] [Container: <ItemInst [glass jar ID:ddc35155a44f] [loc: north inventory_place] [event:'wait_one_turn' ID:303b0 state: 1] >] [event:None] [clusters: 1]>}

in the jar. You take `moss ID:874951abb31b`
and immediately after that the jar contains
parent.children: {
<ItemInst [dried flowers ID:89c373d2ef35] [Container: <ItemInst [glass jar ID:ddc35155a44f] [loc:
north inventory_place] [event:'wait_one_turn' ID:303b0 state: 1] >] [event:None] >,
<ItemInst [moss ID:45a70b6b5a6a] [Container: <ItemInst [glass jar ID:ddc35155a44f] [loc: north inventory_place] [event:'wait_one_turn' ID:303b0 state: 1] >] [event:None] [clusters: 1]>}

So 6383e8f99ddd is just gone.
Named items:
{<ItemInst [moss ID:45a70b6b5a6a] [loc: north inventory_place] [event:'moss_dries' ID:aabc2 state: 1] [clusters: 1]>, <ItemInst [moss ID:874951abb31b] [loc: north inventory_place] [event:'moss_dries' ID:16375 state: 1] [clusters: 1]>}

Okay, so it's  this:
Success (<ItemInst [moss ID:19cf61e2bddc] [Container: <ItemInst [glass jar ID:c31a4f9a53f1] [loc: north inventory_place] [event:'wait_one_turn' ID:11688 state: 1] >] [event:None] [clusters: 0]>) has multiple instances of 0 and will be removed.
Ah, it's the compound test. It tries to find local by name instead of using the container data.

Oddly I've made it so it's merging the moss in the inventory. Need to fix that. And only some of them, so twice as odd.

`A glass jar, holding a few moss clumps, some dried flowers, and a clump of moss.`

8.55pm
Okay. So what it's doing now is adding the first moss fine, but then it's combining the next two mosses to a cluster, so when you take the second moss from the jar, it takes a cluster of val 2.

Bleeeeeh. Everything just breaks something else, goddamn.
I've tried to be generalist about it but I think it's just making it worse. Maybe I just need a clearly defined route for 'move cluster items from a to b', moreso than I do now. It's the cluster obj selection that's broken, it's trying to find a cluster item for 'put moss in jar' but it's finding items already in the jar, or multiples that it doesn't break down correctly. goddamn.

9.14pm
{<ItemInst [moss ID:dbd67c7dfafd] [loc: north inventory_place] [event:'moss_dries' ID:2f667 state: 1] [clusters: 1]>, <ItemInst [moss ID:55007b892fa8] [loc: north inventory_place] [event:'moss_dries' ID:89e12 state: 1] [clusters: 1]>, <ItemInst [moss ID:fe07dc435fb9] [loc: north inventory_place] [event:'moss_dries' ID:a2709 state: 1] [clusters: 1]>}

Okay. Took me all afternoon and then some but it's right again now. Can add mosses to the jar either directly or by picking the mup then adding to the jar. Still need to sort out the specifics of the events; if I put the jar down, only one event for wait_one_turn is generated.

Also, when I put the moss down, it moves
{<ItemInst [moss ID:fe07dc435fb9] [loc: north inventory_place] [event:'moss_dries' ID:a2709 state: 1] [clusters: 1]>,
with it, despite the moss still claiming to be in inv.

Hm.
So, with testing: seems that 'put moss in jar' only works if there's more than one cluster val on the ground? 'pick up moss' works fine, but 'put moss in jar' reverts to the existing jarred mosses and refuses to pick up more.

Odd.
Item in loc.inv_place to use instead of noun: <ItemInst [moss ID:fda3d8a17cb5] [Container: <ItemInst [glass jar ID:663497173420] [loc: north inventory_place] [event:'wait_one_turn' ID:a43f8 state: 1] >] [event:'moss_dries' ID:c80e2 state: 1] [clusters: 1]>
explicitly took items from loc.inv_place, seems they're not always being cleared properly when added to containers.

Have hit another wall, this time it's with the trigger check returning success when nothing's happened.

Failed to find the correct function to use for <verbInstance put (6a98e4fe-2af0-4969-885b-2be38f3bde72)>: 'NoneType' object has no attribute 'location'
this is hitting again. Need to fix it properly. I'm so much too tired for this. I need to gut all of it tbh. The three scripts I'm working on today are 7k lines alone, surely it doesn't need to be. Need to rest for a while.

11.13am 26/3/26
Okay. I imagine the nonetype location error perhaps is because it's trying to add items to the container that are already in them. In trying to avoid it picking the wrong moss it's picking the wrong one from inside the container instead (in this case there was no other option, but it keeps finding items in inv_place when they're actually in the jar.)

So, I think the key issue is that things being added to containers are being added to inv_place for some reason. Idk why.

I do think I need to remove the set for inv_place.items and just to a generator to build each time. idk.

11.41am
wrote a new item-movement fn just for the actual moving part. Mosses seem to work now but will need to test some more.

Also, 'break items' is a little broken, I assume with the changes I made to trigger returns. 'break jar with paperclip' breaks the paperclip instead of the glass which is hilarious, but the event doesn't trigger properly; it recognises the trigger
# ELIF EVENT.START_TRIGGERS FOR <eventInst [item_is_broken] [ID:0d8da] [state: 2]>
# start trigger: {'id': 'ee88dacb-2e55-4f0e-a67e-aea127298cc7', 'short_id': '98cc7', 'event': <eventInst [item_is_broken] [ID:0d8da] [state: 2]>, 'state': 2, 'triggers': {'item_broken'}, 'exceptions': set(), 'end_type': 'start', 'start_trigger': True, 'end_trigger': False, 'is_item_trigger': False}
# end of check_triggers
# After is_event_trigger: 0, None

but then nothing happens; the paperclip is still in inventory and unbroken.
I think I'll move the break_item details to the eventHandling script so I can just detail it as much as I want.

break paperclip with jar works fine (to break the jar)

Hm.
Except, when it breaks the jar and the contents fall out, 2 of the mosses merge but the third is standalone (despite all the items being correctly located).

Hm. So the glass jar when being moved is intersting:

* Inst has single instance val and not a physical target location, sending  for regular processing.
* About to hit do_move for <ItemInst [moss ID:c9e998bf814c] [Container: <ItemInst [glass jar ID:2c08270464e8] [loc: north inventory_place] [event:'wait_one_turn' ID:66252 state: 1] >] [event:'moss_dries' ID:6fb82 state: 1] [clusters: 1]> with vals:
* location: <cardinalInstance east graveyard (c2aae1a5-9bf5-411c-b5d3-23b3c0f9a4c5)>
* new_container: None

That's the last bit of moss that was the standalone that didn't merge.


It /does/ have a physical location though. So why is it returning there?

Somehow it's hitting this:
# if inst.has_multiple_instances in (0, 1) and (not location or location == loc.inv_place or loc.no_place)
Oh, right. Because I'm not asking if location == loc.no_place, I'm just asking is loc.no_place exists. Okie.

Oh, okay, so fixed that and now I have:

Not process as normal. All moves need to be done already.
old_container: <ItemInst [glass jar ID:2054106f87e3] [loc: north inventory_place] [event:'wait_one_turn' ID:d1ddb state: 1] > / new_container: None / location: <cardinalInstance east graveyard (d58508a3-b2f6-4036-9f52-c635506eb10b)>
Failed to find the correct function to use for <verbInstance break (cb28e8a8-efe5-4983-84b8-2c72e8b663b6)>: 'NoneType' object has no attribute 'children'

So because the jar is already broken it doesn't have children anymore, I'm assuming. Will look into it after support.

Okay, fixed now. It wasn't about the jar being broken, I had a log error in itemReg so it was allowing the new_container branch even if no new_container. Now if you break the glass jar the moss re-compounds properly as intended.

2.45pm 26/3/26
So. For break_item. For some reason, item_is_broken is generated for the paperclip but never starts, and the 'paperclip' item doesn't actually break. It does have the is_broken flag, but nothing happens to it.

So. item_is_broken should be initing a new item and removing the old one. But it's simply never starting.

Gradually progressing. Fixed the route a little and now it at least tries to get to the part where it generates the broken item. Now it's struggling because it's getting a target itemname from 'noun.on_break', which is giving it 'generic' (the material name). So I need to manage where it's applying that. on break/on_burn should really only apply when it's something like 'broken glass shards', not just material type.

3.31pm
Okay, broken paperclip works now. Figurd it out.

So, next: fix the 'x3' in container contents.

Also, I need to fix the colour printing.
eg for this:
A glass jar, holding some dried flowers, a clump of moss, a clump of moss, and a clump of moss.
it's yellow (intended) until 'some dried flowers' where it goes cyan for the item.col,  and the same for other items, but the ',' and ', and' are just white. I assume its because the items have formatting end codes. So perhaps I do a  str replace w/ the col code from the start of the msg for all but the last closing col code.
as in take:
`yel(cyan/end, blue/end, magenta/end, magenta/end)/end`
and make it
`yel(cyan/yel, blue/yel, magenta/yel, magenta/yel)/end`


Hm. Testing this out, and... why does

"The glass jar is now in your inventory.", with one colour in it, print
        `print("If cls.END in text more than once:")`
        `return f"{start}{text}{end}"`

some 40 times?

`If cls.END in text more than once:`
`If cls.END in text more than once:`
`You put the moss in the glass jar.`
prints it twice.

Is it checking every character in "The glass jar is now in your inventory."?
Here it prints 3 times:
If cls.END in text more than once:
If cls.END in text more than once:
If cls.END in text more than once:
You pick up the moss, and feel it squish a little between your fingers.
The command is coming from
`print(f"{assign_colour(msg, colour=state_type, noun=noun)}")` ln 1031 in eventReg

And this:
`Not process as normal. All moves need to be done already.`
with no colour at all is also printing it, and it's even more lines.
that one's after
`Inst <ItemInst [moss ID:13fa9baf9326] [loc: east graveyard] [event:None] [clusters: 3]> is not multiple instance val of 1 and/or does not have a target location of inv_place or no_place.`
`origin: <cardinalInstance east graveyard (e07279ec-07e9-40b7-bfb0-ccc733a60bdd)> // shard: <ItemInst [moss ID:44bc4c113d62] [loc: north inventory_place] [event:None] [clusters: 1]>`

I guess it's perhaps for all the coloured reprs and the lines are just out of order, that's reasonable. Will assume that for now.

Oh, it's the cardinals, being updated for loc_desc changes. Right.
I don't know why it's checking cardinal colours so many times, though. It gets 'graveyard', but then it gets 'north' ten times.

just before get_loc_descriptions
If cls.END in text more than once: text: graveyard
If cls.END in text more than once: text: north
[... 42 lines here for the cardinals.]
in loc_descriptions after init_loc_descriptions for place <placeInstance graveyard (276e65c9-a950-42f5-b2e1-ddba7d7648dc)> and card_inst: <cardinalInstance east graveyard (fbe9f48a-16ed-4f14-a383-654514aa0c38)>

Okay, well now it has a little cardinals dict that gets the colours, so it's only

If cls.END in text more than once: text: graveyard
If cls.END in text more than once: text: north
If cls.END in text more than once: text: east
If cls.END in text more than once: text: south
If cls.END in text more than once: text: west
If cls.END in text more than once: text: west
If cls.END in text more than once: text: gate
If cls.END in text more than once: text: padlock
If cls.END in text more than once: text: cardboard box

instead. Better.
It takes west twice because... or some reason. Idk.But the printed description is the same as it was previously. I think it's because of the variations dict (desc_print_dict), where each one had assign_colour(cardinal). Now each just calls that dict so it doesn't have to repeat the pull.

So, anyway:

`You put the moss in the glass jar.`

For this, if it's meant to yellow, it's something I can't do within assign_colour, because assign_colour is only being used internally (`f"You put the {assign_colour(noun)} in the {assign_colour(noun2)}."`). So it needs an intermediate print step between print() and assign_colour() for it to reformat print lines if they start with a non-neutral colourcode.

Also, my silly correction attempt didn't exactly fix it:

ORIGINAL TEXT: A glass jar, holding some dried flowers, and a clump of moss.
Corrected text: A glass jar, holding some dried flowers33, and a clump of moss33.

Because the 'text' it's correcting doesn't actually have the overall colour applied yet when it runs. The yellow is applied later, perhaps?

![colour sections in str](image-5.png)

Oh, I fixed it. I just needed to add the escape code to the fg_code. That was easy.
Oh it looks awful though. That's unfortunate.

![working but looks awful](image-6.png)
Well I'm glad it works, but yeah. Might have to rethink the yellow.

Okay - x3 is working for container contents now:
    `A glass jar, holding moss x3, and some dried flowers.`

5.28pm
and a little more improved, now it maintains the bold that items should have. And the order is switched, so it's
    `A glass jar, holding 3x moss, and some dried flowers.`

Just feels more natural that way. Locations + inventory will still print x3.

Oh damn. I just rewrote the x3 fn and now I remember I already wrote it for the inventory. Damn. Oh well.
For future reference, it was here:
    `generate_clean_inventory(inventory_inst_list:list[itemInstance]=None, will_print = False, coloured = False, for_children=False)`

Hm.
Putting the moss in the jar from inventory doesn't have a print line. It does succeed but it doesn't print.
So it's because move_a_to_b just returned "success"
So that 'success' is because it triggered '1' when it went through is_event_triggered. Theoretically that was a way to pass through if an event printed something, so it would't print an event printline and then also the default move line. But apparently no.

6.00pm
Okay, fixed. I was returning a tuple at one point which meant that a later check failed. Done now.

2.50pm 27/3/26
Next, I want to add usage of the 'encountered' tag. Currently it's checked in a couple of places but it's never applied.
So where do I need to add it?
* when items are included in location descriptions (and that description is printed, so not inside of loc_desc which is in some circumstances generated in advance of printing) - so, 'look around', and 'relocate' I believe should cover those. Then you choose to look around and when you arrive.
* when items are listed as contents in containers
* when a singleton is generated from a cluster
* when an item is picked up/interacted with (maybe use set_noun_attr as the throughpoint)
* when an item is unhidden

Hmm. Okay, so - not quite. There's the headstone in graveyard east, that isn't in the description per se so I don't want it 'encountered' until it's been read.

Well aside from the initial generation, it seems like all the loc_descs are only done for the current loc. So I will do that instead of relocate.

[Also, item_is_broken is not removed from the paperclip after it's broken.] #TODO

I think I'm going to exclude npcs from the 'automatically encountered' setup; you have to talk to them/otherwise interact for it to count.

Also, this warning:
`No event found with this attr trigger reason: item_in_inv. Cannot generate event. (Not a problem if it wasn't expected. Tailor this later.)`
is printing now every time I pick something up. Which is good, in a manner, because it is accurate. It just means I need to clean the routing so only things that should end up there, do. It's an expected failure, just means it's messy. though I knew that already. Carrying on.

Hm. 'use key on padlock' failed, apparently it tried to iterate on an itemInstance.
I'm guessing this:
    `if noun_1 in noun_2.requires_key:`
is what it hit.
noun_2.requires_key is meant to be a set, I'm assuming I haven't updated that somewhere.

I don't use `self.locks_keys` anywher outside of itemReg. Really should use it in verb_actions. I have far too many places where I'm registering keys and locks.

Hm.
So at some point, the lock is changing requires_key from a set to an instance. I can't see where.
Oh, I bet it's eventReg.

Ah, yeah. This is the one. It does a separate pass for event.items to make sure they have keys if needed.

Hm. Okay.
So:
At the end of item reg, we have this:
`ITEM.REQUIRES_KEY at end of cleaning loop: `<ItemInst [padlock ID:198ce2c6456d] [loc: north graveyard] [event:None] >` // `{<ItemInst [iron key ID:1958cfa8abdc] [loc: north work shed] [event:None] >}`, requires_key type: <class 'set'>`

Great.
But when the padlock is initialised in eventReg, we have this:
padlock requires key and key_is_placed_elsewhere. {'item_in_event': 'reveal_iron_key'}
item.requires_key: iron key / type: <class 'str'>

OH. I bet it's because 'requires_key': 'iron key' is an item_flags_on_start for the padlock.

Okay, fixed that. Now it runs a check if requires_key is flagged and if a key instance already exists that meets those qualifications, it doesn't overwrite it with the str. Currently it only works though if the event item does already exist.
God this is so redundant. I'm doing this so it doesn't error but it still runs the 'assign_event_keys' fn later which does this same check but on the item in events as opposed to the item on the trigger (which is same item). Goddamn.

I need to add held_by to can_pick_up items so NPCs can carry inventory. (That makes me want to add pickpocketing)

Adding a danger zone so I can run code from within the game without having to write a meta section for it each time.

Took me a little bit to figure it out but it works now. It's basic but means if I want to check 'how many items are currently encountered=True' I can just type out the commands directly. Which is v nice.

8.18pm
I think some of the inconsistency in how conversations is treating the requirements is because it depends if you have the requirements to /have/ the dialogue, or if you failed a check. Perhaps.

autoplay_in_said at start: []
autoplay_failed: set()
are not filling properly. They should be holding the existing conversation data, but on repeat it just starts anew.

Also, it only properly checks the requirements speech part in `holy book` about half the time, and I don't know why.

8.33pm
okay fixed that part.
Now, need to fix that it's started playing parts even if they're not autoplay just because they have no requirements. Need to differentiate between no requirements vs succeeded, because autoplay applies in the former.

Hm.
Why is it reporting the failed check as '0'?
0 is already in parts_said, it's already been done.

Goddamn. Now the inner loop is broken again:

`    I think that's all there is of interest to you on this.`


`   Yes, good... Let's discuss the missing holy book.`

I need to work on this tomorrow, put some proper time into it.

Why does it do this half the time?

#   ... missing book
#   getting autoplay in said
#   autoplay_in_said at start: []
#   autoplay_failed: set()
#   len(conversation.autoplay_parts): 2
#   Keyword part: 0
#   no parts_said: None
#   parts_said from npc.conversations: None
#   Adding 0 to parts_said
#
#       There's a book, and it's missing... And this missing book is holy.
#
#   ...
#   failed checks: set()
#   Parts said: {'0'}
#   conversation.autoplay_parts: {'1', '0'}
#   AUTIOPKAY IN SAID: ['0']
#       What do you want to talk about?
#
#         - the history of the Church
#         - the missing holy book


Ooooh.
I think maybe half the time I'm writing 'holy book' and the other half, 'missing book'. The latter goes via the keyword route, while the former goes the conversation route.

Okay, kinda fixed it I think.

But now: why does completing the currently availble content of 'history' trigger the 'discuss missing holy book' again? I assume it's not returning properly or something?

Okay. So it seems to be when it returns after saying no to 'discuss it again'.
it returns
return "end_topic"

It has to be because of the form of def conversation_loop(). There are three different entry points to discuss_topic (which is also recursive)

Hm. Okay. So:
ask about holy book, 'not found after first discuss topic' so ut gies ti the second discuss topic loop because test was in label.lower of convo_dict.
It prints the available line, then comes to the 'after second discuss topic with user_input 'end_topic', going immediately back to 'what do you want to talk about'. I say 'history', but history isn't found in keywords so it goes right back to the second discuss_topic. It loops through and prints the available content. I then say 'history' again, but it skips right through and doesn't print anything or give me the option to start over.
0, 1 and 2 are all autoplay, with 2 checking for a paperclip in inv.
`failed checks in advance` didn't pick it up.

1.23am
Fixed a few more little things. working properly with keyword-only speech parts again and responds a bit better to keywords. Still needs work but it's something.
I think I fixed that loop where it would duck back out of the conversation and try to resume a previous one but I need to do more  testing.
