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
