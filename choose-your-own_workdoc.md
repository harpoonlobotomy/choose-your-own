choose-your-own workdoc

Currently figuring this out:

    "a graveyard": {"glass jar": {"name": "a glass jar", "description": f"a glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers.",
                    "description_no_contains": "a glass jar, now empty aside from some bits of debris.", "contains": "dried_flowers"},

I need to figure out the best way to specify 'give hte description with or without hte contained obj, depending on whether the obj has been removed or not.
Planning ot make it easier, in that you can only remove it by putting it in the inventory.
Then it has to be marked for both the contained and container that it's been removed, so it's not relying on current inventory (otherwise if the flowers are dropped from inventory, they'll reappear back in the jar.)

10.12am, 18/11/25
Working on plot outline/implementation in a new doc.

Settings: Need a settings json. On run, check if that JSON exists, if not, ask to set settings (with defaults). Making changes in 'settings' in-game updates the JSON.

[[{todo // set up textspeed and luck settings to work within game without a separate function}]]

[[{todo // figure out how to remove flowers from jar and have them behave differently.}]]

main points re: flowers/jar:
    1: parent/child relationships between objects
    1.5: Location origin of objects (so I can add 'Found this at {location}'. Would be useful.)
So the parent/child relationship:
    If you pick up the parent, you pick up the child.
    If you pick up the child, the parent remains, childless.

11.33am, 18/11/25
trip_over={"any": ["some poorly lit hazard", "your own feet"],
           "outside": "a small pile of debris",
           "inside": "a small pile of clothes"}
Adding some randomness to the 'tripping over in the dark' section.

11:43am
hey it works. Nice.

11:46
The weather/time changes randomly. I went from graveyard to graveyard and it went from late evening to midday.

Also, there's no point in this:
`Do you want to look around the graveyard, or sit for a while?` (ln )

The check for 'rest' should be at the moment where you choose whether to stay or relocate, not after relocating.

Maybe weather changes by +/- 1 from where it currently is. So when you relocate, maybe it goes from raining to cloudy, but not raining to heatwave.

Need to overhaul 'relocate()' majorly. Making notes directly.

12:04
have changed the times to advance by one for each relocation. Makes the day go /really/ fast, but it's better than randomness. Maybe do it every second relocate or something, idk. Or maybe we assume things are super far apart. Or just add more times of day. And/or add more, and specify travel distance between locations somewhere?
Could give everything x/y coords, then get the vector between them for approx travel time. If super far, 2 blocks of time, etc.

12:15
Have updated the weather to move +/- 1 from current weather.

3:01pm
If you sleep, skip 4-ish times.
Have updated the times list with more interstitial times, so the progression makes more sense.

9.51pm
Back at it.
Issue to fix:
"""It looks like you're already carrying too much. If you want to pick up paper scrap with number, you might need to drop something - or you can try to carry it all.
    (drop) or (ignore)
d
d: Describe location.
[A graveyard]  You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.

The entrace gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.

Chosen: (drop)"""

'd' gets the 'description' correctly, but then is maintained and also selects 'drop'. Need to 'reset' the input after 'description'.

Maybe turn
"""
    if text.lower() == "i":
        print()
        do_inventory()
        print()
"""
and its ilk into 'while', and set it to none at the end.
But none poses dfficulties, as 'none' is an outcome for many instances (eg 'hit enter to continue'.)

Well no, because this is within 'user_input', so it has a shell loop for None. Okay. Trying just making them all elifs instead of straight ifs, so any choice resets the loop instead of continuing.


---

I need to track 'discovered' for items. So if I 'describe' a graveyard again, it tells me which items I've already found here (but not picked up)

---

How about this:
Determined, you peer through the darkness.
Once your eyes adjust a bit, you manage to make out more shapes than you expected - you find a scrap of paper with a phone-number written on it.
[[ `paper scrap with number` added to inventory. ]]

Maybe a different description if it's found while dark. So if you look at it in the daytime/when light is present, then it 'updates' to 'with number'.


---

g
Chosen: (go)
Keeping in mind that it's late evening and raining, where do you want to go?
Please pick your destination:
    (a city hotel room, a graveyard, a forked tree branch)
2
Chosen: (a graveyard)
You decided to stay at thegraveyard a while longer.
With the weather a heatwave, you decide to look around the east of the graveyard.
Using the light from the sun, you're able to look around the graveyard without too much fear of a tragic demise.

Why is the time/weather not working?
It worked in isolation...

When arriving at a new place, should be facing opposite the exit wall.


11.32pm:
Okay so this:

  File "d:\Git_Repos\choose-your-own\choose_a_path.py", line 330, in get_loot
    if choices.loc_loot.pick_up_test(named): # should this be negative or positive? More things to look at but not pick up, or the inverse?
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^
  File "d:\Git_Repos\choose-your-own\choices.py", line 209, in pick_up_test
    if item["can_pick_up"]:
       ~~~~^^^^^^^^^^^^^^^
TypeError: 'NoneType' object is not subscriptable

is where it's failing  tonight. Going to bed now.


1.56pm 19/11/25
Worked on a few bits and pieces. Currently:

This:
What do you want to do? [Investigate] item, [take] item, [leave] it alone.
shouldn't give the option to 'take' something like a TV, right? But maybe it's better to let you try and keep it boilerplate, idk.

Also I need to fix this:
  File "d:\Git_Repos\choose-your-own\choose_a_path.py", line 111, in user_input
    text = input()
KeyboardInterrupt

New todos:
    - neaten the user_input section for lists, it seems redundant in parts and I want to make it clearer.
    - make sure everything works when looking for inputs, consistent use of lower() etc.
    - formalise exactly what's in choices.py vs env_data.py vs locations.py. Right now it's a higgledy ol' mess.
        - I'm not sure how I'd even want to separate them. Right now, 'choices' is some initial setup (carrier options etc), language variation (emphasis, choose variants (y, yes etc), lists like times of day, but then also all the loot tables + the loot class.) env_data is the weatherdict, detailed location data and weirdly the paintings list ( - have just moved paintings to choices.) locations.py is the place class, theoretically the nested locations (currently disabled) and the basic tree of locations. But there's no data there that isn't in the primary (detailed) location dict in env_data. I mean, I have class place_data in env_data and class places in locations.
        Going to smuch locations into env_data I think. For now I'll leave the nesting out and just implement it properly once I'm ready to actually use it. My main concern is that there's some interplay between places and place_data that I've forgotten about. (All I remember currently is that places_data gets the keys from places, but it can just get its own keys ffs.).
    - stop it displaying all items in a location without regard for cardinals. They can be described, but if I'm standing in the middle of a graveyard, I shouldn't have the option to examine a glass jar on the far wall. Currently cardinals aren't implemented in item locs at all.
    - let it find user_input with leading "a " removed. 'graveyard' should find 'a graveyard'. In fact why aren't we using the a-less version anyway? Maybe I only implemented that for items, not locations. Probably so.
    -- fix this issue in user_input:
     Updated values: [['north', 'east', 'west'], 'leave', ['carved stick']], type: <class 'list'>
        5
        5 is not a valid option, please try again.
    only works with a unified list of options. Will be fixed once I've cleaned the input options. Okay, will do that now.
    - set starting orientation to 'facing away from entrance wall' in relocate.


Things done:
    - Added an automatic space to switch_the.
    - hopefully allowed for non-case-sensitive item lookup
    - added some more attr for items, started item location tracking
    - worked on some copy
    - probably a bunch of other small things I've already forgotten.


2.55pm okay so fixed the digit input options, the values are a clean list after printing but before evaluation now.

3.16pm
Why does this fail sometimes.


You can look around more, leave, or try to interact with the environment:
    (north, south, west), (leave) or (TV set, window)
--------------------
 Original values: [['north', 'south', 'west'], 'leave', ['TV set', 'window']], type: <class 'list'>
tv set
Chosen: (TV set)
Unfortunately I haven't written anything here yet. Maybe just... go somewhere else?

 vs

  Original values: [['north', 'south', 'west'], 'leave', ['TV set', 'window']], type: <class 'list'>
TV set
Chosen: (TV set)
A decent looking TV set, probably a few years old but appears to be well kept. Currently turned off. This model has a built-in DVD.
What do you want to do - investigate it, take it, or leave it alone?
    (investigate), (take) or (leave)
--------------------
 Original values: ['investigate', 'take', 'leave'], type: <class 'list'>

 did I just fail to implement the lower()? Probably.

Okay that's fixed now, I'd missed swapping out a test for v.

Now back to this:

  File "d:\Git_Repos\choose-your-own\choose_a_path.py", line 360, in get_loot
    slowWriting(f"[[ `{item}` added to inventory. ]]")
                       ^^^^
in get_loot: value: None, random: True, named: TV set, message: None = fine.

Oh I didn't allow for it to fail the pick up test, that's why.

3:29pm
Okay that's fixed now.
Do I need to set 'inventory' as a location to simplify the item location tracking? Might be more straightforward tbh.



4.49pm
So now I can tell it an item is on my person and/or in another location. But currently I don't think it actually updates the location with that data. Also my location descriptions aren't modular enough for this really.

4:53
okay, so now it adds the child obj of an item. Currently it just does it without any additional checks, I need to check if the child is still in parent. But it's progress.

5.15pm
Okay so I broke the inventory, now I can't leave because it doesn't recognise plain enter. Will have to fix this, kinda major bug.

5.31 so I didn't just break it, the version I committed a couple of hours ago also had this issue, I just hadn't noticed yet. Damn.

5:41 okay, it was changing the ifs to elifs in user_input. Fixed now. Still means I might have the issue of bleedthrough, but at least it basically functions again. A better midpoint.

7.56pm I need a day counter. Certain plot events happen at certain points, maybe it runs over the course of a week? So to solve the mystery or w/e, you need to do everything in enough time. Which also means I need activities/etc that can kill time and make that harder, because right now all there is is looking at things.

Still kinda like the idea of giving the locations map coords and calculating distance for approximated travel times (per time_of_day segment).


1.03pm, 5/12/25 Short break to work on a birthday present, now back.

Going to implement colours to identify typeable words.

Also:
    - This:
        "You can drop the car keys or try to separate it into parts, or hit enter to continue. " Should only be shown if the item /can/ be split. Currently it happens after any inventory item inspection.


Could randomly assign colours to items as they're identified the first time, and then use those colours each time. Would be neat. And could have specific colours for types eventually if I wanted.


Also:

This:
    The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.
    Pick a direction to investigate, or go elsewhere?
        (north, south, east, west) or (go)
    i

    INVENTORY:
    To examine an item more closely, type it here, otherwise hit 'enter' to continue.
        (paperclip, fashion mag, batteries, unlabelled cream, regional map, fish food, anxiety meds)
    regional map
    Chosen: (regional map)
    Description: None yet

    You can drop the regional map or try to separate it into parts, or hit enter to continue.
        (drop) or (separate)

    Continuing.
    To examine an item more closely, type it here, otherwise hit 'enter' to continue.
        (paperclip, fashion mag, batteries, unlabelled cream, regional map, fish food, anxiety meds)


    You decide to leave the graveyard
    Please pick your destination:
        (a graveyard, a forked tree branch, a city hotel room)

    Should not happen. After finishing in the inventory, it should return to the question, not take the question as answered when it wasn't.


Also:

    You can look around more, leave, or try to interact with the environment:
        (north, south, west), (leave) or (glass jar, dried flowers, moss, headstone, north, west, south)

It's repeating the cardinals in the 'or' section. Need to exclude those if they appear again, or better yet stop them reappearing.

(They're nicely coloured, though. Can't tell here, but they are.)


Also:

    You decide to move on from the graveyard
    Please pick your destination:
        (a forked tree branch, a graveyard, a city hotel room)
    a city hotel room
    Chosen: (a city hotel room)
    You decided to stay at the graveyard a while longer.

I clearly didn't pick the graveyard...
Rigged is off, so it shouldn't be forcing the graveyard.

Hm. Well rigged was partly on, and I tried to fix it but this isn't quite right...:

    a city hotel room
    Chosen: (a city hotel room)
    You make your way to a city hotel room. It's 2am, the weather is raining, and you're feeling pretty okay overall.
    With the weather outside raining, you decide to look around the south of the city hotel room.

    There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.

    Directions to look: ['north', 'east', 'west']
    You can look around more, leave, or try to interact with the environment:
        (north, east, west) or (leave)

Oh nvm, I hadn't updated the description yet. It's not a coding issue, just a copywriting one.

I need a way to mark objects in the descriptions, so 'You see a TV set' has 'tv set' in the tv's predefined colour.


Also, this:

item start location: {'a forked tree branch': 'east'}
[Find the loot taking function that already exists, make sure the item is removed from the list here.]
Unfortunately I haven't written anything here yet. Maybe just... go somewhere else?
Keeping in mind that it's early morning and cloudy, where do you want to go?
Please pick your destination:
    (a forked tree branch, a city hotel room, a graveyard)
i

INVENTORY:
To examine an item more closely, type it here, otherwise hit 'enter' to continue.
    (severed tentacle, fashion mag, fish food, unlabelled cream, batteries, car keys, carved stick)
carved stick
Chosen: (carved stick)
Description: [DESCRIBE] No such item: carved stick

You can drop the carved stick or try to separate it into parts, or hit enter to continue.
    (drop) or (separate)

Continuing.
To examine an item more closely, type it here, otherwise hit 'enter' to continue.
    (severed tentacle, fashion mag, fish food, unlabelled cream, batteries, car keys, carved stick)


You make your way to None. It's mid-morning, the weather is perfect, and you're feeling doing quite well.
Traceback (most recent call last):
  File "d:\Git_Repos\choose-your-own\choose_a_path.py", line 766, in <module>

I went to inventory while it was asking me to choose a new destination, and it ended up with no destination (ie it lost where I just was). game.locatin should never be cleared...


ah, it's because I set the game.location directly from the return of option:

game.place = option(options, print_all=True, preamble="Please pick your destination:")

So if the input doesn't make sense, it just returns none.



Also this:

You can drop the regional map or try to separate it into parts, or hit enter to continue.
    (drop) or (separate)
separate
Chosen: (separate)
Dropped regional map. If you want to drop anything else, type 'drop', otherwise we'll carry on.


7/12/25 5.05pm
I think I need to update the inventory system entirely. I want to be able to treat item names as a specific type, and apply colours to that. Currently the colour application is context dependent.

But for now, I think I'm going to work on this:

    You could stay and sleep in the forked tree branch until morning, or go somewhere else to spend the wee hours. What do you do?
        (stay) or (go)
    i

    INVENTORY:
    To examine an item more closely, type it here, otherwise hit 'enter' to continue.
        (paperclip, puzzle mag, anxiety meds, regional map, unlabelled cream, fish food, car keys, paper scrap with number)
    paper scrap with number
    Chosen: (paper scrap with number)
    Description: A small scrap of torn, off-white paper with a hand-scrawled phone number written on it

    You can drop the paper scrap with number or try to separate it into parts, or hit enter to continue.
        (drop) or (separate)

    Continuing.
    To examine an item more closely, type it here, otherwise hit 'enter' to continue.
        (paperclip, puzzle mag, anxiety meds, regional map, unlabelled cream, fish food, car keys, paper scrap with number)


    Keeping in mind that it's pre-dawn and a heatwave, where do you want to go?
    Please pick your destination:
        (a graveyard, a city hotel room, a forked tree branch)

Where the 'i' takes you to inventory, but when you leave the inventory, it puts you back /after/ the input call, not before it. It should return you to the prior input call.

That particular example is this:

            if test in no:
                slowWriting("Thinking better of it, you decide to keep the advanced investigations until you have more light. What now, though?")
            test = option("stay", "go", preamble=f"You could stay and sleep in {switch_the(place, "the ")} until morning, or go somewhere else to spend the wee hours. What do you do?")
            if test in ("sleep", "stay"):
                if places[game.place].inside == False:
                    sleep_outside()
                else:
                    sleep_inside()
            else:
                slowWriting(f"Keeping in mind that it's {time} and {weather}, where do you want to go?")
                relocate()

So the input is either returning `i` (what was typed) or None (the last enter on leaving the inventory)

this:
        test=user_input()
        if test in ("inventory_done"):
            continue
doesn't work, as it just repeats the last line of the inventory management line itself, I need it to trigger only after the inventory management is done.

Okay, think I fixed it. Seemingly having only one entry in that list made it fail, probably checking against the letters instead of the full string. But now it seems to work; 'enter' just takes you to the single prior entry, so if in description it goes back to inventory, if in inventory it reprints the prior text:

    Pick a direction to investigate, or go elsewhere?
        (north, south, east, west) or (go)
    i

    INVENTORY:
    To examine an item more closely, type it here, otherwise hit 'enter' to continue.
        (severed tentacle, mail order catalogue, regional map, unlabelled cream, batteries, car keys, fish food)
    car keys
    Chosen: (car keys)
    Description: None yet

    You can drop the car keys or try to separate it into parts, or hit enter to continue.
        (drop) or (separate)

    Continuing.
    To examine an item more closely, type it here, otherwise hit 'enter' to continue.
        (severed tentacle, mail order catalogue, regional map, unlabelled cream, batteries, car keys, fish food)


    Pick a direction to investigate, or go elsewhere?
        (north, south, east, west) or (go)

Also:

q
No sufficient response to the text. Returning Null.

in response to:

Unfortunately, it's raining
You can weather it out (no pun intended) or try a last minute relocation - what do you do?
    (stay) or (move)
q
No sufficient response to the text. Returning Null.
Please pick your destination:
    (a city hotel room, a forked tree branch, a graveyard)

1, I thought 'q' should be 'quit'. Two, why isn't that picked up earlier? Glad I added that print line.

Also I need to inforce the 'none_allowed' flag or whatever it's called. None should not be allowed in 'do you want to stay or move', it shouldn't default to 'move'.

Well this is a bizarre bug I introduced:

    The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.
    Pick a direction to investigate, or go elsewhere?
        (west, west, west, west) or (go)

blue, cyan cyan cyan, and it changed the text. Whoops.

When it's not cardinals it doesn't change the text:
    Please pick your destination:
        (a graveyard, a forked tree branch, a graveyard)
but it's all cyan.

Think it's fixed now. Maybe.

Thing to note though:

    Once your eyes adjust a bit, you manage to make out more shapes than you expected - you find a scrap of paper with a phone-number written on it.
    colour: `None`. Type: <class 'NoneType'>
    [[ `paper scrap with number` added to inventory. [NAME SHOULD BE COLOURED]]]

"a scrap of paper" is coloured, as it should be, but 'paper scrap with number' has a differnt colour. I really want the inventory items to store and retrieve their colours, so they're persistent each time.

Okay so it's not fully fixed. The full colours do loop around properly for longer lists now, but for two items it's still looping the full four, instead of 1==1 and 2==2.

Oh, it's because those aren't a list, they're each processed separately.
Okay so... I need to make it so that if it's a list, we enumerate and get the number /there/. Otherwise only those with 'print_all' are getting the ordered list.

Think I've fixed that now.


Why does this:
    You can look around more, leave, or try to interact with the environment:
        (north, south, west), (leave) or (glass jar, dried flowers, moss, headstone, north, west, south)

add the cardinals to the inventory list?
It's getting it from here:

potential = choices.location_loot[game.place].get(game.facing_direction)

Okay have at least confirmed it's not an issue of the colour text somehow, it must predate it.

If  there is no inventory in that direction, it prints normally:

    You can look around more, leave, or try to interact with the environment:
        (north, south, east) or (leave)

OOOh. It's because I'd had 'north, west, south' as children of 'east', so looking 'east' gets you those as location loot. Oops.

Directions to look: ['north', 'south', 'west']
Interactable items: ['glass jar', 'dried flowers', 'moss', 'headstone']

  (north, south, west), (leave) or (glass jar, dried flowers, moss, headstone)

Okay, fixed it now.

7:13pm
Trying to fix the loot pickups a bit.

also this:
    Please pick your destination:
        (a graveyard, a city hotel room, a forked tree branch)
Having to type the 'a' is a pain.


Another variation of the 'why are you ending early':
Pick a direction to investigate, or go elsewhere?
    (north, south, east, west) or (go)
d
d: Describe location.
[A forked tree branch]  None yet....

The entrace gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.
  You're facing north. You think you could leave through the large wrought-iron gates to the north. They're imposing but run-down; this graveyard doesn't get as much love as it could.



You decide to leave the forked tree branch
Please pick your destination:
    (a city hotel room, a graveyard, a forked tree branch)

Ah. Because I never added the 'description' return from user_input.

8:33pm.
Next thing.

    INVENTORY:
    To examine an item more closely, type it here, otherwise hit 'enter' to continue.
        (severed tentacle, mail order catalogue, batteries, unlabelled cream, regional map, car keys, fish food, glass jar, dried flowers)
    Chosen: (glass jar)
    Description: [DESCRIBE] No such item: glass jar

11.45pm
TODO:
If drop item, need to add it to the description to the current location.

11.27am, 8.12.25
I'm thinking I might need a second Class for the loot. One for actual loot management, separate from the loot tables. idk.

Also need to make the descriptions modular.

This:
    You're facing east. You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, dried flowers left long ago.

stops working as soon as you pick up the glass jar. (Or anything else, that's just my default selection.)

1.11pm Succumbed to chatting to chat gpt to discuss refactoring the inventory/item system before it gets too much messier. Think I have a decent plan now.

Going to work on the JSON file for the item defs (which I needed to switch to anyway)

EDIT: Actually it's going to be a .py file, at least for now. No need to bring JSON into it at this scale.


10/12/25

    You make your way to a graveyard. It's middle of the night, the weather is cloudy, and you're feeling pretty okay overall.
    With the weather cloudy, you decide to look around the east of the graveyard.

    You're facing east. You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, dried flowers left long ago.

    You can look around more, leave, or try to interact with the environment:
        (north, south, west), (leave) or (glass jar, dried flowers, moss, headstone)

Need to add time-relevance to this section.

    You can look around more, leave, or try to interact with the environment:
        (north, south, west), (leave) or (glass jar, dried flowers, moss, headstone)

If it's too dark to see, the inventory shouldn't be provided without investigating.

ALSO:


        INVENTORY:
        To examine an item more closely, type it here, otherwise hit 'enter' to continue.
            (severed tentacle, gardening mag, fish food, unlabelled cream, car keys, regional map, batteries, glass jar)
        Chosen: (glass jar)
        Description: A glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers.

        You can drop the glass jar or try to separate it into parts, or hit enter to continue.
            (drop) or (separate)
        Chosen: (separate)
        dried flowers separated from glass jar

        Description: A glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers.

        You can drop the glass jar or try to separate it into parts, or hit enter to continue.
            (drop) or (separate)
        Chosen: (separate)

Once an item is separated, it should print both updated descriptions, and then return to the inventory 'screen'.

ALSO also:

Continuing.
To examine an item more closely, type it here, otherwise hit 'enter' to continue.
    (severed tentacle, gardening mag, fish food, unlabelled cream, car keys, regional map, batteries, glass jar, dried flowers, dried flowers, dried flowers, dried flowers)

Currently it just keeps making more dried flowers, as there's no tracking on whether the item's already separated from children yet. But the new inventory system should fix that at least once it's implemented.


5.50pm, 13/12/25
Worked on the TUI for a couple of days.
Back to trying to fix inventory item colour consistency.

Currently, when printing one-by-one, it properly applies the item.colour. But when printing a list, it still goes by item-index.

6.25 Okay, seem to have gotten the item.colour to work consistently now.

Not sure what else is still broken, probably quite a bit. Part of the game is still using loc_loot, so I need to fix that and switch over entirely before I do too much else.

7:32 I want to get multiples organised. Currently it just lists them as separate items, but then there's no way to differentiate, it just takes the first one each time. I need some way to differentiate between them.
Given that I'm storing the instance in the inventory directly now, shouldn't be too hard.
Really, if >1 of an item in the inventory, it should just print "paperclip x2". Then if I 'drop', it asks 'how many do you want to drop, you are carrying 2 <item>'. Similar for describing the item. 'You have two paperclips; they are virtually identical. Need a description for 'is_plural'. currently the descrip is 'A humble paperclip'. Could do it automatically, maybe. Depends on the descrip tho.

I need to fix the 'drop' function implementation.

I switched it up so you can 'drop' anywhere, instead of only inside the inventory after looking at the item (so you can just write 'drop paperclip', instead of 'paperclip', then 'drop'.)

But, it doesn't break the loop early enough:

        To examine an item more closely, type it here, otherwise hit 'enter' to continue.
            severed tentacle, paperclip, mail order catalogue, regional map, paperclip, anxiety meds, 5 pound note, paper scrap with number
        paperclip
        Chosen: (paperclip)ls and not an instance: Chosen: (paperclip)
        Description: A humble paperclip.

        You can drop the paperclip or try to separate it into parts, or hit enter to continue.
            drop or separate
        drop paperclip
        Text starts with drop: drop paperclip
        textparts: ['paperclip'], len: 1
        Item: [<ItemInstance paperclip (557bbf4c-39c1-4672-a792-e1b20db1af7e)>, <ItemInstance paperclip (dd6aadfd-ef4d-4826-9997-26e31cb5cb93)>], type: <class 'list'>
        Dropped paperclip. If you want to drop anything else, type 'drop', otherwise we'll carry on.

        Load lightened, you decide to carry on.
        [[ Psst. Hey. Type 'secret' for a secret hidden option, otherwise type literally anything else. ]]


        You can drop the paperclip or try to separate it into parts, or hit enter to continue.
            drop or separate

        Continuing.
            severed tentacle
            mail order catalogue
            regional map
            paperclip
            anxiety meds
            5 pound note
            paper scrap with number
        To examine an item more closely, type it here, otherwise hit 'enter' to continue.
            severed tentacle, mail order catalogue, regional map, paperclip, anxiety meds, 5 pound note, paper scrap with number


8:32 Seems to be fixed now.

Really want to get the main game 'playing' in the textblock of the tui. That's for another day though. Maybe tomorrow.


2.14pm, 15/12/25
Trying to figure out why the text block is wrong as smaller sizes.
At full size, the text block starts one line below ====..., and ends one line above, as it should.
But when smaller, all the info blocks and the text block are one line down.

Oh, it's because it was one column too thin, so there was overlap at the top line. So the movement didn't match what was expected.

idk why the centering is off. the spacing works properly, but fullscreen I have 0 spaces to the left and 2 spaces to the right. Should be centred...


2.51pm Working on implementing the main game with the tui. Just starting with the context boxes first, to get health/etc in.
Right now, going to work on inventory. Probably the trickiest one tbh.

Note: Going to have an issue later because datablocks runs game, set_up, which will clash later. Need to keep that in mind and just replace the game/setup elements of datablocks with placeholders once I get to that point.

9.44pm, 15/12/25
All three infoboxes working properly now. Code could use a cleanup but those elements are working.

Next up, need to get the actual 'gameplay' in the text box. Not sure how to do that yet given it likely means having to rejig every print section, but maybe I can route it via slowWriting and slowLines. idk.

2.53pm 16/12/25
 ## small words/long words dict
    #if i in [3, 4]: ## small words/long words dict ## with name, but wipes HP. Not sure why.
    ## This does work, ish. I'd rather have it all on one line until it was too long, though. But it does /function/ as is. Leaving it for now, later will combine the two sets based on how many free character spaces are left in the first line
I need to reinstate this at some point. Where it'll check the space and apply the new element on the first or second line based on that, instead of specific items per line (eg using the second line even if the first line is blank just because the item name is longer.)
That, /or/, have everything visible but not 'bold', and just bold it when selected.

Also I need to fix the name printing.


9.49am 18/12/25
Going to switch the print statements over to the new rich version. Using the ansi>rich converter for now, will make it native later.

Need to read back through this file to see what todos I've forgotten about.

1.48pm Maybe a database for text entries instead of having them in the script itself. Can reuse them for atmosphere maybe.


1.15pm 21/12/25
Haven't been so good with keeping notes here. Lots of git commits though so maybe that's some compensation. And lots of comments inline.

Currently working on the inventory w/ multiple duplicates. Going okay. Need to get myself a clearer outline of what needs doing though. Maybe one of those workboards with tasks so I don't just keep forgetting the things I realise need doing.


2.47pm:

# With the weather cloudy, you decide to look around the west of the forked tree branch.
# You're facing west. There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.
# You can look around more, leave, or try to interact with the environment:
# north, south, east, leave or


   The blank after 'or' is new. Means it's including a blank entry, assumedly for 'potential' (the items at that location) because there are no items there, but it never used to create a blank. I thought it already excluded blank entries. Not sure.

3.43 Okay, fixed that, am onto the next thing.

The 'cut to line length' is failing.
#
#     |##|         -|  You take a moment to take in your surroundings. You're in a 'budget' hotel room; small but pleasant enough, at least to sleep in. The sound of traffic tells you you're a couple of floors            |-          |##|
#     |##|         -|      up at least, and the carpet is well-trod.. There's a queen-size bed, simple but clean looking, to the north. To the east is a television and two decent sized windows overlooking the city, to the south is a door, likely to a bathroom,                                                                                                                                                                                            ty, to the south is a door, l
#  ikely to a bathroom,Pick a direction to investigate, or go elsewhere?                                                                                                                                           ty, to the south is a door, l
#  ikely to a bathroom,                                                                                                                                                                                            ty, to the south is a door, l
#  ikely to a bathroom,    north, south, east, west or go elsewhere                                                                                                                                                ty, to the south is a door, l
#  ikely to a bathroom,                                                                                                                                                                                            ty, to the south is a door, l
#  ikely to a bathroom, and to the west is the door out of the room, likely to the hallway.

Not exactly sure why it failed yet. Possibly a list within a list?

The call was slowWriting(f"You take a moment to take in your surroundings. {loc_data.overview}") from main.

3.51pm
hm.
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|    You're facing north. The bed looks nice enough - nothing fancy, but not a disaster either. Two pillows, a spare blanket at the foot of the bed. There's a small bedside drawer to each              |-          |##|
#   |##|         -|      side, and a painting above the bed.                                                                                                                                                               |-          |##|
#   |##|         -|

   Worked this time.

Ah.

#
#   |##|                    INPUT:  Line split: part a: `[A city hotel room]  You're in a 'budget' hotel room; small but pleasant enough, at least to sleep in. The sound of traffic tells you you're a couple of floors up at least, and the carpet`, partb: `    is well-trod.. There's a queen-size bed, simple but clean looking, to the north. To the east is a television and two decent sized windows overlooking the city, to the south is a door, likely to a bathroom, and to the west is the door out of the room, likely to the hallway.`
#

Because it's not recursive, if it's more than just one split then fails just slightly later. Okay. Shall make it recursively check B.

Okay, fixed now.

3:57pm

 CURRENT LOCATION: a forked tree branch
 Location does not update when moving.

Also:
For some reason it's still not printing the items at the hotel room. Thought it'd be fixed but no.
And to note: It's not the city that's broken. Graveyard also does not show items anymore. So yeah I just broke it today. Will fix it again.

4:13pm Okay fixed it now.

Back to the other thing.

  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1005, in test========================================================================================================================================================
    do_print()______________________________________________________________________________________________________________________________________________________________________________________________________________________________
    ~~~~~~~~^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 928, in inner_loop
    slowWriting("You decide to look around a while.")
    ^^^^^^^^^^^^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 887, in look_around
    else:
        ^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 823, in look_light
TypeError: 'NoneType' object is not subscriptable

Trying to select 'window' from
 You can look around more, leave, or try to interact with the environment:                                                                                                                             |-          |##|
   |##|         -|                                                                                                                                                                                                        |-          |##|
   |##|         -|      north, south, west, leave or TV set, window

If you type 'window' it just repeats it self like you entered an invalid value.
If you type a number, you get the above error.
#
#
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|  TV set                                                                                                                                                                                                |-          |##|
#   |##|         -|  window                                                                                                                                                                                                |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|  You can look around more, leave, or try to interact with the environment:                                                                                                                             |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|      north, south, west, leave or TV set, window                                                                                                                                                       |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|  Chosen: (tv set)                                                                                                                                                                                      |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|  You can look around more, leave, or try to interact with the environment:                                                                                                                             |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|      north, south, west, leave or TV set, window                                                                                                                                                       |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|  Chosen: (window)                                                                                                                                                                                      |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|  You can look around more, leave, or try to interact with the environment:                                                                                                                             |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|      north, south, west, leave or TV set, window                                                                                                                                                       |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|  Chosen: (5)                                                                                                                                                                                           |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|         -|                                                                                                                                                                                                        |-          |##|
#   |##|          :========================================================================================================================================================================================================:           |##|
#   |##|                                                                                                                                                                                                                               |##|
#   |##|                    INPUT:  Traceback (most recent call last):                                                                                                                                                                 |##|
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1009, in <module>                                                                                                                                               |##|
#    time.sleep(1)                                                                                                                                                                                                                    /|##|
#    ^^^^^^----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|##|
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1005, in test========================================================================================================================================================
#    do_print()______________________________________________________________________________________________________________________________________________________________________________________________________________________________
#    ~~~~~~~~^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 928, in inner_loop
#    slowWriting("You decide to look around a while.")
#    ^^^^^^^^^^^^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 887, in look_around
#    else:
#        ^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 823, in look_light
#  TypeError: 'NoneType' object is not subscriptable
#

4:30pm Okay.
Not being able to select the TV is because the actual line is this:

values: [['north', 'south', 'west'], 'leave', ['\x1b[1;31mwindow\x1b[0m', '\x1b[1;34mTV set\x1b[0m']], clean_values: ['north', 'south', 'west', 'leave', '\x1b[1;31mwindow\x1b[0m', '\x1b[1;34mTV set\x1b[0m']

The cardinals work because they only have their colour applied at print, while the other elements get it applied when the list is cleaned.


5.35pm:
Chosen: (a graveyard)

test: a graveyard
RETURNING: a graveyard
You make your way to None. It's midday, the weather is perfect, and you're feeling bit stressed.

Traceback (most recent call last):
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1047, in <module>
    test()
    ~~~~^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1043, in test
    inner_loop(speed_mode=test_mode)
    ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 966, in inner_loop
    relocate()
    ~~~~~~~~^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 675, in relocate
    if places[game.place].visited:
       ~~~~~~^^^^^^^^^^^^
KeyError: None

D:\Git_Repos\choose-your-own>


5.52pm:
INVENTORY:

Inv list: ['paperclip', 'paperclip', 'paperclip', 'gardening mag', 'batteries', 'unlabelled cream', 'regional map', 'fish food', 'paperclip', 'paperclip', 'glass jar']

inventory isn't printing properly. Need to fix this one.

5.52pm:


Chosen: (glass jar)

Description: It's a gardening mag

Inv list: ['paperclip', 'paperclip', 'paperclip', 'gardening mag', 'batteries', 'unlabelled cream', 'regional map', 'fish food', 'paperclip', 'paperclip', 'glass jar']


Ah. It's more broken I thought. Still using the index of named vs the index of not, I imagine. inv_list is the wrong list to be using.


5.56

INVENTORY:

True


Type the name of an object to examine it, or hit 'enter' to continue.


Hm. Not exactly what I was intending on getting back.


10.48 Just lost a chunk of time thinking I'd screwed something up, but turns out I hadn't. Damn.


11.11am, 22/12/25
Going to take a break for a couple of days to work on a birthday present. Will be back on this soon enough.

22.13pm 24.12.26

You can look around more, leave, or try to interact with the environment:
(north, south, west, leave) or TV set, window

Chosen: (window)

 facing out of the hotel room and down over the street below. Currently closed.
What do you want to do with the window - investigate it, take it, or leave it alone?
(investigate, take) or leave

I need to take these interactions from the object flags. Take appears if can_pickup, 'open' appears if 'can_open', etc.


25/12/25

Working on getting the 'visible objects' to update within the print function, and it's being a pain.

# You're facing east. Against the wall is a large television, sitting between two decent sized windows overlooking the city. The curtains are drawn.
#
# TV set
# window
#
# TV set
# window
#
# TV set
# window
#
# INPUT:  Values: [['north', 'south', 'west'], 'leave']
#
#
# formatted: ['\x1b[1;31mnorth\x1b[0m, \x1b[1;34msouth\x1b[0m, \x1b[1;35mwest\x1b[0m', '\x1b[1;34mleave\x1b[0m', '\x1b[1;31mT\x1b[0m, \x1b[1;34mV\x1b[0m, \x1b[1;36m \x1b[0m, \x1b[1;35ms\x1b[0m, \x1b[1;31me\x1b[0m, \x1b[1;34mt\x1b[0m', '\x1b[1;31mw\x1b[0m, \x1b[1;34mi\x1b[0m, \x1b[1;36mn\x1b[0m, \x1b[1;35md\x1b[0m, \x1b[1;31mo\x1b[0m, \x1b[1;34mw\x1b[0m']

It prints the list three times (regardless of the number of items), then the 'formatted' is the (singular) local items, broken into individual letters.

Originally it added each item three times. :/


3.25pm
okay, fixed that. Now a new weirdness.

Went and got the  carved stick from the forked tree. Picked it up. Went to graveyard and dropped it while looking around. All seemed good. Ignored the 'secret'. Then, when it reprints the 'or interact with the environment':


   You can look around more, leave, or try to interact with the environment:
   north, south, west, leave or glass jar, moss, dried flowers, headstone

   test from inventory name: <ItemInstance carved stick (a68327b5-c221-4b91-a84c-1c479e6b71de)>

   Dropped carved stick.

   Load lightened, you decide to carry on.

   [[ Psst. Hey. Type 'secret' for a secret hidden option, otherwise type literally anything else. ]]

   You can look around more, leave, or try to interact with the environment:

   paperclip, paperclip, paperclip, puzzle mag, car keys, paperclip, paperclip, batteries, unlabelled cream, anxiety meds, regional map, fish food, glass jar or moss, carved stick, headstone, glass jar, dried flowers


All of a sudden, it's included the inventory as 'values', when I wasn't printing the inventory.

3.36pm It's because I'd given it hardcoded inventory name values. fixed now.

5.02pm
Hm.

Actions: ['read', 'drop']
Values: [['read', 'drop']], type: <class 'list'>
Colour is None. Item: (read). Type: (<class 'str'>)
values: [['read', 'drop']], formatted: ['\x1b[31mread\x1b[0m']
    read

So, why is it not formatting the second word. That's unusual.

Trying to implement the 'item actions'. The actions are coming through correctly as values, but then discarded by the formatter?


5.21pm
Okay. Fixed now. The functions aren't perfect but basically it's implemented and more or less printing properly.

Actions available for glass jar:

    drop, remove dried flowers

both drop and remove dried flowers are generated dynamically based on the item flags. idk why it doesn't have the 'or', but I'll fix that part later. Basic idea works, which is nice.

Currently only when the item is named from the inventory after picking it up. Should probably do it before that, when the option to pick up is given at all.


11.38am 26/12/25


    north, south, west, leave or moss, glass jar, dried flowers, headstone

g


Chosen: (g)

Container in inst.flags: <ItemInstance glass jar (05b758d6-2c8a-4068-ae64-80790f6d38dc)>
children: [<ItemInstance dried flowers (4e29c044-cdad-416c-b765-8ec429abddeb)>]
Description: A glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers.

Values: ['take', 'leave'], type: <class 'list'>
What do you want to do with the glass jar - take it, or leave it alone?

    take or leave

t


Chosen: (t)

glass jar added to inventory.



no children present. name: a glass jar
Values: ['drop', 'ignore'], type: <class 'list'>
It looks like you're already carrying too much. If you want to pick up the glass jar, you might need to drop something - or you can try to carry it all.

    drop or ignore

ignore


Chosen: (ignore)

Well alright. You're the one in charge...

You feel a little lighter all of a sudden...


... [returned to graveyard]

Values: [['north', 'south', 'west'], 'leave'], type: <class 'list'>
You can look around more, leave, or try to interact with the environment:

    north, south, west, leave or moss, a glass jar, headstone

glass jar

Chosen: (glass jar)

No entry in loc_loot for None

So, when dropped it uses the name, not the item def key.

Well, when dropped it drops the instance. So it's getting the name when fetching the list.

But that failure is coming from an error, here:

                item_entry = registry.instances_by_name(text)
                if item_entry:


So it was picked up, correctly named in the inventory, force dropped and had the wrong name in the location items.

So when dropped, for some reason it's using inst.nicename instead of inst.name. And I don't know why.

Drop func in item_management just assigns inst, not .name or .nicename.


OOOOOh.

It's because of this:

"name_children_removed":"a glass jar"

So where it should give name (with or without children), it's giving the child-free version of nicename.


So yes. name_children_removed should never be called from the main script, only ever via the nicename func in item man, where it's done automatically after checking for children.
