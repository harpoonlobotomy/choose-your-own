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


12.46pm
okay, progress.

paperclip x4
fashion mag
anxiety meds
regional map
fish food
batteries
dried flowers
glass jar*

the car keys are now in the glass jar, as indicated by the asterisk. Will fail if you try to access it because I haven't done anything on the next state to deal with said asterisk, but progress. Car keys no longer in inventory, glass jar notes children. It's a start.

2.03pm
Slowly progressing.
Trying to get the children to work properly with action_items, to give a list of children to be removed.
The list is working, but now it fails to find the child in the parent, after finding the child in the parent...

# items by name: [<ItemInstance dried flowers (6db6e4a4-f2f2-41a7-8c9c-791e2ed08c2f)>]
# parent: <ItemInstance glass jar (605e2705-508a-4281-ae63-3c734b82eb48)>, child: None
# children: [<ItemInstance dried flowers (6db6e4a4-f2f2-41a7-8c9c-791e2ed08c2f)>]
# Parent_manual (inst.contained_in): <ItemInstance glass jar (605e2705-508a-4281-ae63-3c734b82eb48)>
# Parent from external: <ItemInstance glass jar (605e2705-508a-4281-ae63-3c734b82eb48)>
# Traceback (most recent call last):
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1104, in <module>
#    test()
#    ~~~~^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1100, in test
#    inner_loop(speed_mode=test_mode)
#    ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1011, in inner_loop
#    look_around()
#    ~~~~~~~~~~~^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 970, in look_around
#    look_light("skip_intro")
#    ~~~~~~~~~~^^^^^^^^^^^^^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 952, in look_light
#    relocate()
#    ~~~~~~~~^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 749, in relocate
#    new_location = option(options, print_all=True, preamble="Please pick your destination:")
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 470, in option
#    test=user_input()
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 364, in user_input
#    do_inventory()
#    ~~~~~~~~~~~~^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 271, in do_inventory
#    item_interaction(test, inventory_names, no_xval_names)
#    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 244, in item_interaction
#    do_action(trial, inst)
#    ~~~~~~~~~^^^^^^^^^^^^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 177, in do_action
#    separate_loot(child_input=child, parent_input=parent)
#    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 97, in separate_loot
#    game.inventory = registry.move_from_container_to_inv(item, game.inventory, parent)
#                     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#  File "D:\Git_Repos\choose-your-own\item_management_2.py", line 330, in move_from_container_to_inv
#    self.move_item(inst)
#    ~~~~~~~~~~~~~~^^^^^^
#  File "D:\Git_Repos\choose-your-own\item_management_2.py", line 307, in move_item
#    self.by_container[parent].remove(inst)
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
#KeyError: <ItemInstance dried flowers (6db6e4a4-f2f2-41a7-8c9c-791e2ed08c2f)>


2.13pm Think I fixed that one, it was removing from parent in the 'move_from_container_to_inv' func then trying to do it again in the move_item func. Moved it to only the move_item func, which is called by move_from_container_to_inv anyway.

Now:
i


Chosen: (i)



INVENTORY:

Traceback (most recent call last):
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1111, in <module>
    test()
    ~~~~^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1107, in test
    inner_loop(speed_mode=test_mode)
    ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1018, in inner_loop
    look_around()
    ~~~~~~~~~~~^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 977, in look_around
    look_light("skip_intro")
    ~~~~~~~~~~^^^^^^^^^^^^^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 948, in look_light
    look_light("turning") # run it again, just printing the description of where you turned to.
    ~~~~~~~~~~^^^^^^^^^^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 959, in look_light
    relocate()
    ~~~~~~~~^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 756, in relocate
    new_location = option(options, print_all=True, preamble="Please pick your destination:")
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 477, in option
    test=user_input()
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 371, in user_input
    do_inventory()
    ~~~~~~~~~~~~^^
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 264, in do_inventory
    inventory_names, no_xval_names = generate_clean_inventory(game.inventory, will_print=True, coloured=True, tui_enabled=enable_tui)
                                     ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Git_Repos\choose-your-own\misc_utilities.py", line 77, in generate_clean_inventory
    has_parent, child_inst = is_item_in_container(inventory_inst_list, item_name)
    ^^^^^^^^^^^^^^^^^^^^^^
TypeError: cannot unpack non-iterable NoneType object

Not have that one before. Not sure how/why it failed. I can see why it returned what it did, if it didn't find a container item


2.50pm That issue is solved, but it's still not updating the inventory properly after separating an item. It claims to... but doesn't.


Also I just got this error:
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 937, in look_light
#    relocate()
#    ~~~~~~~~^^
#  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 767, in relocate
#    do_print(places[game.place].same_weather)
#             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# AttributeError: 'Place' object has no attribute 'same_weather'

which is new...


3.03pm
Okay so back to the item issue.

# Game.inventory after item_interaction: [<ItemInstance severed tentacle (2115f579-33c8-4ecd-b095-05e3f4b99c19)>, <ItemInstance paperclip (15023f68-1856-493d-9ed6-ea1b21618dd6)>, <ItemInstance paperclip (90c17bd7-ae6f-4dae-98a8-e5a2a7186c69)>, <ItemInstance paperclip (5a34c84f-41e2-4eda-a475-019036637731)>, <ItemInstance paperclip (69b75cbe-1889-498d-92c7-5a311be7f253)>, <ItemInstance unlabelled cream (712ac3fe-686f-4d8c-b7f7-74ba3b2f2bf0)>, <ItemInstance car keys (5a5cc69a-b213-421b-972a-c8e9c7e145fb)>, <ItemInstance regional map (fd0dbf0b-1bba-4d50-bbc8-0c353fa19986)>, <ItemInstance paperclip (92e62a35-2992-4a70-9de8-ecd7e2e02311)>, <ItemInstance batteries (566dfbd8-e0b1-4e0e-8e2e-ce48a0afde13)>, <ItemInstance paperclip (b9261437-4671-4187-a83a-053d09c11750)>, <ItemInstance glass jar (2e6a640a-83dd-4871-bdf3-1db3bd7729df)>, <ItemInstance dried flowers (08a80e24-bf1c-4fec-a66c-a007ec20044f)>]
# severed tentacle
# paperclip x6
# unlabelled cream
# car keys
# regional map
# batteries
# glass jar
# inventory names: ['severed tentacle', 'paperclip x6', 'unlabelled cream', 'car keys', 'regional map', 'batteries', 'glass jar']

The dried flowers are being added to the inventory as they should. But, they're not being printed in inventory names.

Potential reasons why:
phantom 'in_container' flag on dried flowers
old inv list data

# In generate clean inventory: has_parent: <ItemInstance glass jar (cff9d972-f6d2-4b6f-90e2-63e996e93f02)>, child_inst: <ItemInstance dried flowers (70dd1a3f-58a8-4648-a3a8-b1055e249af6)>

Okay, was the first one.

3.09 okay, fixed.

3.41
So the inventory works nicely now. Automatically updates the status of container objects with ...* if it's holding something, does not add the child to inventory unless separated from parent, dynamically adds <remove <item>> and <add to> options for container objects.


4.03pm
# Item `dried flowers` removed from old container `glass jar`
#
# Actions available for glass jar:

TODO: I want to set a colour for item interactions like this. Currently I'm using yellow as I do for descriptions (but currently not bolded) but idk if i like it. The colours are generally pretty bad tbh, I need to set some defaults outside the starting 16 options. Need a proper palette.

But the inventory thing I've been working on today does seem to work properly now.


So, next issue:

#  Description: A humble paperclip.
#
#  You currently have 5 paperclips
#
#  Actions available for paperclip:
#
#      drop
#
#  drop
#
#
#  Chosen: (drop)
#
#  Traceback (most recent call last):
#    File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1170, in <module>
#      test()
#      ~~~~^^
#    File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1166, in test
#      inner_loop(speed_mode=test_mode)
#      ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
#    File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1069, in inner_loop
#      test=option("stay here", "go elsewhere", preamble="What do you want to do? Stay here and look around, or go elsewhere?")
#    File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 531, in option
#      test=user_input()
#    File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 425, in user_input
#      do_inventory()
#      ~~~~~~~~~~~~^^
#    File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 331, in do_inventory
#      trial = item_interaction(test, inventory_names, no_xval_names)
#    File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 300, in item_interaction
#      actions = registry.get_actions_for_item(inst, game.inventory)
#    File "D:\Git_Repos\choose-your-own\item_management_2.py", line 610, in get_actions_for_item
#      if inst in inventory_list:
#         ^^^^^^^^^^^^^^^^^^^^^^
#  TypeError: argument of type 'NoneType' is not iterable
#


Oh wait, I know why. I wiped game.inventory accidentally by not finishing the next section. Fixed now.


2.09pm 27.12.25
#    Chosen: (add to)
#
#    Choose an object to put inside the glass jar or hit enter when done:
#
#        paperclip x5, anxiety meds, batteries, fish food
#
#    paperclip
#
#
#    Chosen: (paperclip)
#
#    Choose an object to put inside the glass jar or hit enter when done:
#
#        paperclip x5, anxiety meds, batteries, fish food
#
#    anxiety meds
#
#
#    Chosen: (anxiety meds)
#
#    Added anxiety meds to glass jar
#
#    Choose an object to put inside the glass jar or hit enter when done:
#
#        paperclip x5, batteries, fish food
#

The 'add to' selection doesn't account for multiples correctly. I need to shift the 'check for multiples' to something more reusable and central.


3.26pm Have set up 'compare_input_to_options in misc_utilities, which should help with above and some other usecases too. Intent is to set it up any time user input needs to be checked against option lists, with output tailored to minimum noise but with the required usability. Having a check after the compare func is an additional step, but being able to check 'if this null/instance/(float|int)/str' to get what 'kind' of metadata is involved with clear steps therafter feels nicer than returning 6 different pieces of information and checking against them all, with the endless item_name, _, _, _, _, etc.


In practice:

    outcome, alignment = compare_input_to_options(game.inventory, game.player, input="paperclip")
    outcome_ref = alignment.get(outcome)
    print(f"outcome: {outcome}, alignment: {outcome_ref}")

# [<ItemInstance severed tentacle (9429d103-3e5a-4a3e-9f1a-18edb8529dba)>, <ItemInstance paperclip (0bf9f141-9d84-4f9e-8ea1-ef52560cf53b)>, <ItemInstance paperclip (cba0ebbb-dd0b-447b-a81c-133e10aa8eb5)>, <ItemInstance paperclip (cc6d5a2c-2738-40f3-895d-3a1014d7a815)>, <ItemInstance fashion mag (e5718a73-063f-4286-8513-3b345f37594a)>, <ItemInstance fish food (6c3f6283-9ee4-4f10-ab8c-a27129b6e6b6)>, <ItemInstance paperclip (69f0c8ee-6862-4853-986d-8556b5f12031)>, <ItemInstance regional map (c1aeeec5-cc29-45bd-95bc-ec5c56f33454)>, <ItemInstance paperclip (7c530b89-d3dc-4c97-9762-403f73a067e8)>, <ItemInstance paperclip (01f4d086-acfd-4370-9e67-f4aa7ac9766a)>]
# outcome: paperclip, alignment: {<ItemInstance paperclip (0bf9f141-9d84-4f9e-8ea1-ef52560cf53b)>}

Returns the first paperclip, provided with just 'paperclip' input.


With 'use last' on:

[<ItemInstance paperclip (5e77a4e6-81c0-4c9b-8fb4-71d3a0fb5dfc)>, <ItemInstance paperclip (70782774-62b9-4ce6-bb6a-29fd2193a983)>, <ItemInstance paperclip (be761953-3186-49fd-acb4-83ab946012b1)>, <ItemInstance fashion mag (e6d4c204-10b6-4cdc-b9f1-cff04a1e615c)>, <ItemInstance car keys (bed5ea45-2256-406b-85b2-4f9882c566b0)>, <ItemInstance anxiety meds (772f0f04-8f41-4ef1-b52a-d97066625f36)>, <ItemInstance paperclip (48abc0ba-c645-4369-9f6c-b500ea636245)>, <ItemInstance unlabelled cream (328c7002-8f59-47a8-93ce-72b5e1bcd7d6)>, <ItemInstance fish food (73e7f5fd-6aec-4dee-94f0-58b3f8e18e68)>, <ItemInstance paperclip (c78af0e0-654c-4d41-9c46-2649621743bf)>, <ItemInstance batteries (71a0c01f-6ced-4305-bc0d-6e2ef6f51b26)>]
outcome: paperclip, alignment: {<ItemInstance paperclip (c78af0e0-654c-4d41-9c46-2649621743bf)>}

Returns last as expected.

Hmmmm.
But using the cleaned list (with x5 etc), it ruturns

outcome: paperclip, alignment: {6}

where the plural val has superceded the instance val.

So yes. It's one or the other - if I feed it the actual inventory, it returns instance correctly. If i feed it the cleaned inventory (which is just strings), it returns plural/etc. Which is to be expected, it's not doing the interal checks against the inventory databank.


3.48pm:

[<ItemInstance paperclip (e85b3c2c-bc47-4e56-92dd-8de0d047839a)>, <ItemInstance paperclip (3d87fa86-6ed3-4b95-8365-d8f7159f7b44)>, <ItemInstance paperclip (c3cc3b7f-a762-48e1-ac7c-3bbe3576ce2e)>, <ItemInstance gardening mag (705f455f-3736-478f-ba0b-ef7e80968fd4)>, <ItemInstance anxiety meds (03b36466-adbd-4483-8ebb-a50379af67c0)>, <ItemInstance car keys (8c1972db-3f3b-45fb-a627-2c12e080d274)>, <ItemInstance paperclip (928a7501-58dc-4e16-a6b5-4157ae63b3a2)>, <ItemInstance paperclip (0952747d-876b-4136-a566-a8cb9bbdf6fe)>, <ItemInstance fish food (c55223b4-76e1-48f3-9ee4-f7de8e722085)>]
outcome: paperclip, alignment: {'name_type': 5, 'instance': <ItemInstance paperclip (0952747d-876b-4136-a566-a8cb9bbdf6fe)>}

Okay. One mor step, but now it carries both the name_type data if reevant and instance data if relevant.


So, this:

    from misc_utilities import compare_input_to_options
    clean_list, _ = generate_clean_inventory(game.inventory, tui_enabled=enable_tui)
    outcome, alignment = compare_input_to_options(clean_list, game.player, input="fashion mag", inventory=game.inventory, use_last=True)
    outcome_ref = alignment.get(outcome)
    print(f"outcome: {outcome}, alignment: {outcome_ref}")

gets you this:

outcome: fashion mag, alignment: {'name_type': 0, 'instance': <ItemInstance fashion mag (54e7ba14-8aaf-4e53-bf76-4f48c94d1d34)>}

Yeah I'm happy with that. Whther you get name_type, instance or both depending it on what  you feed into it, but I think that's a pretty solid setup. The interface from str input > instances is significant, and I feel better about having this as a main component of the 'option selected' engine. (Not really an engine, but it sounded good.)


5:42pm
Okay, updated the item identification: 'drop' now uses the new system, taking the inputted instance (as chosen by 'paperclip>drop'), but grabs the last instance and drops that. This means the inventory colours are consistent, as it drops the 'hidden' paperclip, not the first in the list. Subtle but nice.


Hm. Issue though: After they're dropped, the items lose their colour. When 'dropped x', they had their own colours. But once they're on the ground in the inventory list, they have the default colour (red), matching the first one found. So the ones on the ground default to red. Not sure if that's a matter of the inv print or if the items have lost the colour attr.

5:47pm
Okay, so have tested:

north, east, west, leave or paperclip, paperclip, paperclip, paperclip <- all paperclips are red

What do you want to do with the paperclip - take it, or leave it alone? <-- paperclip is red

Chosen: (take)

paperclip added to inventory. <- paperclip is cyan, as it was originally.

So the instance retains its colour, but it's not utilised when the obj is on the ground.

5.54pm
Fixed. Now it retains the instance color regardless of whether it's in the inventory or not.
Only exception is:


You can look around more, leave, or try to interact with the environment:

    north, south, east, leave or paperclip, paperclip  <- purple, red

paperclip


Chosen: (paperclip)

Description: A humble paperclip.

What do you want to do with the paperclip - take it, or leave it alone?  <-- red

    take or leave

take


Chosen: (take)

paperclip added to inventory.  <-- purple

You can look around more, leave, or try to interact with the environment:

    north, south, east, leave or paperclip   <-- red


So it shows purple, red. The 'chosen' is the last one. But the one it chooses is the first. I would expect it to always be taking the first one's colour, given that's the one it defaults to - typing the name it picks the first. But for some reason,
What do you want to do with the paperclip <-- this one is taking red. I assume it's the colour of hte first paperclip in the inventory, so it's the first that it comes across when searching by name, but it can correctly identify the colour in the next step. So I just need to specify slightly sooner.


6.03pm Okay, seems to be fixed now. It still picks items from the local items at a seemingly random order, but the colours are consistent


5.03pm 28/12/25

Working on null-entry user input and print spacing. There are weird bunches of spacing that I need to identify, so I'm going to add markers to print lines.

#  You can look around more, leave, or try to interact with the environment:
#
#      south, east, west or leave
#
#
#
#
#  (Chosen: <NONE> [do_input])
#
#  (Chosen: <NONE>) [look_light]
#
#  You can look around more, leave, or try to interact with the environment:
#
#      south, east, west or leave

Notes

5.54pm
okay have fixed some of it. Added the 'none' print in user_input, and whether it adds a line or not is dependent on whether the TUI is in use or not, because when not TUI it needs a line added.

    -|  Chosen: (i)
   |-          |##|
   |-          |##|
   |-          |##|
   INVENTORY:
   |-          |##|

Still three lines beween choosing 'i' and the inventory being printed. Need to check why.

6.09pm
Added a basic CLI arg to the main script so I can turn the tui on/off between runs without editing the script. Should have done that ages ago.

Chosen: (i)



INVENTORY:

non-tui has 3 blank lines between 'i' and INVENTORY too. Looking into that now.


Fixed it. Had to remove a single do_print. It always adds 3 for some reason.

Am moving do_print to a different

New bug: if in settings you type a not-number, you get:

# To change text speed, enter a number (0.1 to 2), or hit enter to continue with current speed (1.2). Default is (1)
# [Default test printing speed is 1. 0.1 is very slow, 2 is very fast.]
# d
# Please enter a number between 0.1 and 2, or hit 'enter' to keep default.
# Traceback (most recent call last):
# ...
#     if new_text_speed:
#        ^^^^^^^^^^^^^^
# UnboundLocalError: cannot access local variable 'new_text_speed' where it is not associated with a value

So I need to fix that.

7.37pm
Tangent: Think I just removed the last remaining parts of 'location.py' from the main script, have put them into env_data instead. visited etc is all in env_data now.
env_data no longer requires location.py for its base resource


7.40pm
#   File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 542, in get_formatted
#     temp_values = registry.instances_by_location(game.place, game.facing_direction)
#   File "D:\Git_Repos\choose-your-own\item_management_2.py", line 266, in instances_by_location
#     if self.by_location[place].get(direction): # check if the direction has been established yet.
#        ~~~~~~~~~~~~~~~~^^^^^^^
# KeyError: 'a forked tree branch'
Dammit. Still this.
> fixed now.


Also this:

# It looks like you're already carrying too much. If you want to pick up the glass jar with flowers, you might need to drop something - or you can try to carry it all.
#
#     drop or ignore
#
# Chosen: (drop)
#
# You decide to look in your inventory and figure out what you don't need.
#
# [Type the name of the object you want to leave behind]
#
#     severed tentacle, paperclip, paperclip, gardening mag, batteries, paperclip, regional map, car keys, anxiety meds, unlabelled cream, fish food, paperclip, carved stick, glass jar
#
# Chosen: (glass jar)
#
> # Error: This item (`glass jar`) was not found in the inventory. #<<--- why not though?? Look into it tomorrow.
#
# Load lightened, you decide to carry on.
#
# [[ Psst. Hey. Type 'secret' for a secret hidden option, otherwise type literally anything else. ]]

--------

Ugh the spacing is so inconsistent:

# Chosen: (east)
# <## one line gap here.>
# You're already facing east
#
# Do you want to stay here or move on?
#
#     stay here, move on
#
# Chosen: (stay)
#
# < two line gap here>
#   You're facing east. You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, dried flowers left long ago.
#
#
# You can look around more, leave, or try to interact with the environment:
#

Just noting this here so I don't forget:

# ------
#
#   File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 485, in user_input
#     do_print(f"{places[game.place].description}")#{descriptions[game.place].get('description')}")
#                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# AttributeError: 'place_data' object has no attribute 'description'
>    Fixed this now. 8:25pm.


--------------

# Chosen: (n)

# Traceback (most recent call last):
...
#   File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1081, in look_light
#     checked_str, _ = compare_input_to_options(options, input=text)
#                      ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
#   File "D:\Git_Repos\choose-your-own\misc_utilities.py", line 471, in compare_input_to_options
#     elif input.lower() in lower_cleaned:
#          ^^^^^^^^^^^
# AttributeError: 'list' object has no attribute 'lower'


8.40pm

You can look around more, leave, or try to interact with the environment:

    south, east, west or leave

Chosen: (n)

Do you want to stay here or move on?

    stay here, move on

Chosen: (n)

Text from stay here or move on: ['n', 'no', 'nope']. type: <class 'list'>
No match found for n.
Unfortunately I haven't written anything here yet so this'll just repeat for now.

You're facing north. You think you could leave through the large wrought-iron gates to the north. They're imposing but run-down; this graveyard doesn't get as much love as it could.



Because 'n' defaults to 'no', you can't try to look north if you're already looking north by typing 'n', but you can with all other letters. I need to add a 'prefer cardinals' option, so if there's a n/s/e/w optionset, it chooses from those first instead of defaulting to 'no' (even if technically north isn't currently an option.)
Or I guess I could just always make all four cardinals an option, but that feels worse. Idk.

Need to test today's changes with the TUI tomorrow. See how much I broke in the migraine.


1.36pm 29/12/15

So. Just moved a bunch of things to misc_utilities and rearranged things. Just testing, and for some reason now I have this:

#   You can look around more, leave, or try to interact with the environment:
#
#       north, south, west, leave or glass jar, headstone, headstone, moss, moss, glass jar

added a print line:
# Instance objs at: [<ItemInstance glass jar (d5911675-3d14-4a0c-9de4-9a18c999160c)>, <ItemInstance moss (6d9c11a1-9190-4ccd-a790-2fc62cbeb870)>, <ItemInstance headstone (6f1d510c-548a-45f0-a669-73b972bae407)>, <ItemInstance moss (860dbac2-3707-4dda-bf81-c880309c6383)>, <ItemInstance headstone (5c67a7b3-b7d3-4371-a4f9-162b7de8caf0)>, <ItemInstance glass jar (0f75c659-0a37-44c2-b07a-b32c1a7ffc51)>]
# Local items: ['glass jar', 'moss', 'headstone', 'moss', 'headstone', 'glass jar']

Okay so it's not a print issue, it's actually duplicating the instances.


1.51pm okay, have looked into it.

Importing choose_a_path_tui_vers.py
Init in item instance is running now. glass jar

importing choose_a_path is what triggers it to run again. It doesn't trigger

1.55pm
okay so it was specifically

def update_text_box(to_print, edit_list=False, use_TUI=True):

    #from choose_a_path_tui_vers import enable_tui

in tui_update, it seems.


Okay so I fixed that, it was because run() was out in the open. Have moved a few things around and added a config file to store tui enablement in. Seems to be doing the job.

2.54pm
New issue:

cleaned_options: []
No match found for stay here in options (['stay here', 'move on'],). lower_cleaned: [].

For some reason this is not adding those options to the list when it really should be. Just need to fix the options section but I've no idea why it broke when it was working before.

Okay I wasn't including tuples, that's why. Okay.

3.46pm
    Player data: {'hp': 4, 'tired': 1, 'full': False, 'hungry': True, 'sad': False, 'overwhelmed': 0, 'encumbered': 1, 'blind': False, 'in love': False, 'inventory_management': True, 'inventory_asked': False, 'hunger': 1, 'sadness': -1}

So hungry and hunger are different things - hunger is in emotion_table in choices.py, hunger in in game.player.


-----------


4:14pm

#
# Actions available for glass jar:
#
#     drop, remove dried flowers, add to or continue
#
# Chosen: (drop)
#
# Dropped glass jar.
#
# Load lightened, you decide to carry on.
#
# [[ Psst. Hey. Type 'secret' for a secret hidden option, otherwise type literally anything else. ]]
#
# (Chosen: <NONE>)
#
# INVENTORY:
#
# severed tentacle
# paperclip x2
# mail order catalogue
# car keys
# anxiety meds
# fish food
# regional map
# batteries
#
#
# Type the name of an object to examine it, or hit 'enter' to continue.
#
# (Chosen: <NONE>)
#
# Continuing.
#
# You can look around more, leave, or try to interact with the environment:
#
#     north, south, west, leave or moss, headstone, glass jar
#
# Chosen: (glass jar)
#
# Do you want to stay here or move on?
#
#     stay here or move on




Hm.
So  what it's meant to do is


# You can look around more, leave, or try to interact with the environment:
#
#     north, south, west, leave or moss, headstone, glass jar
#
# Chosen: (glass jar)
#
# Description: A glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers.
#
# What do you want to do with the glass jar - take it, or leave it alone?
#
#     take or leave
#
# Chosen: (take)
#
# glass jar added to inventory.
#
# You can look around more, leave, or try to interact with the environment:
#
#     north, south, west, leave or moss, headstone
#
# (Chosen: <NONE>)


Which it did earlier in this exact session, directly before. So why is the input not being routed correctly?

4.18pm Okay, fixed it. It was getting local_items too early, so didn't register it as a match when it was just recently dropped.

Going to add some logging I think. Full routing logging, so I can trace the process per-function.


5:26pm
INVENTORY:

paperclip x2
fashion mag
regional map
car keys
anxiety meds
batteries
unlabelled cream
fish food
carved stick
glass jar*
moss


Type the name of an object to examine it, or hit 'enter' to continue.

Chosen: (glass jar)

Description: A glass jar, looks like it had jam in it once by the label. Holds a small bunch of dried flowers.


Actions available for glass jar:

    drop, remove dried flowers, add to or continue

Chosen: (r)

Item `dried flowers` removed from old container `glass jar`


Actions available for glass jar:

    pick up, add to or continue

Chosen: (p)


Actions available for glass jar:

    drop, add to or continue

(Chosen: <NONE>)

INVENTORY:

dried flowers
glass jar


Type the name of an object to examine it, or hit 'enter' to continue.

(Chosen: <NONE>)

Continuing.

You can look around more, leave, or try to interact with the environment:

    north, south, west, leave or headstone

Chosen: (stats)

    weird: [True]. location: [a graveyard]. time: [midday]. weather: [perfect]. checks: {'inventory_asked': False, 'inventory_on': False, 'play_again': False}

    inventory: ['dried flowers', 'glass jar'], inventory weight: [2], carryweight: [12]

    Player data: {'hp': 4, 'blind': False, 'in love': False, 'inventory_management': True, 'inventory_asked': False, 'tiredness': 0, 'hunger': -1, 'sadness': 0, 'overwhelmed': 0, 'encumbered': 0}



apparently reintroduced an inventory-wipe in some of my changes today. Will sort it out shortly.

More testing:

So it's the removal for some reason, I think.  After removing the flowers from the glass jar, I have dropped everything except the dried flowers.

Will fix.

6.48 seems to be fixed now. Was not providing the inventory list after moving the separate function to utility script, so it was rewriting with an empty list.


6.55pm
Hm. Odd.
((FILE: item_management_2.py. FN: instances_by_location. LINE: 253))
place: a graveyard
direction: east
You can look around more, leave, or try to interact with the environment:

    north, south, west, leave or moss, glass jar, headstone

So it says local items isn't 'None', because it if was it wouldn't have hit this else.
<deleted a bunch of logs. Can't remember what the problem was now.>


7.16pm
Next thing:
values: (['paperclip x2', 'anxiety meds', 'car keys', 'fish food', 'batteries'],)
Choose an object to put inside the glass jar or hit enter when done:

    paperclip x2, anxiety meds, car keys, fish food or batteries

Chosen: (car keys)

((FILE: misc_utilities.py. FN: compare_input_to_options. LINE: 72))
input: car keys

  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 121, in add_item_to_container
    instance = outcome_ref["instance"]
               ~~~~~~~~~~~^^^^^^^^^^^^
KeyError: 'instance'

D:\Git_Repos\choose-your-own>python choose_a_path_tui_vers.py anything



Okay so I fixed that, but:

Actions available for glass jar:
values: (['drop', 'remove batteries', 'remove dried flowers', 'remove car keys', 'add to', 'continue'],)

Actions available for glass jar:

    drop, remove batteries, remove dried flowers, remove car keys, add to or continue

Chosen: (remove dried flowers)

Item `car keys` removed from old container `glass jar`

Actions available for glass jar:

    drop, add to or continue

Removed dried flowers, and yet, everything is removed.

<fixed that, and then:>
severed tentacle
paperclip x2
mail order catalogue
anxiety meds
unlabelled cream
car keys x2
regional map
batteries x2
glass jar
dried flowers

batteries, glass jar and dried flowers.
Somehow we ended up with 2x batteries and 2x car keys in the inv, not sure how that happened.

Probably too tired for this today. I did get some problems solved but it's slow going.


7.35pm Okay so I fixed the last one, but now:

<deleted a huge swath of logging. tl;dr the inventory was broken when you dropped things.>

It's a mismatch between the inv being renewed and not.

Thought I fixed it but it's doing this now... Somewhere, it's mixing up what it should be doing .Because yeah, it's in there, promise.


The traceback:

test: car keys
inst_inventory: [<ItemInstance paperclip (c83a9b22-786e-4210-8c1e-cdc664473938)>, <ItemInstance mail order catalogue (e7279221-0186-47c4-86a3-8c87dcea2425)>, <ItemInstance regional map (7763fbd7-93d8-4e34-b91f-7a58bb6263d2)>, <ItemInstance anxiety meds (46334570-ed55-40b9-baa9-cd57a83b2877)>, <ItemInstance paperclip (22b2069b-27fc-443d-bd1f-1725fdd95846)>, <ItemInstance unlabelled cream (fa1cebe9-d0ba-4530-9165-c1b30320a0a4)>, <ItemInstance fish food (72827239-f90f-4c6c-b0ed-920d4e92fb7d)>, <ItemInstance glass jar (9489cf96-783b-49e5-92f5-dba9a060ac38)>]
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1204, in <module>
    run()
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1188, in run
    inner_loop(speed_mode=test_mode)
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1100, in inner_loop
    look_around()
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1056, in look_around
    look_light("skip_intro")
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 1003, in look_light
    text=option(remainders, "leave", no_lookup=None, print_all=True, preamble="You can look around more, leave, or try to interact with the environment:", look_around=local_items, return_any=True)
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 508, in option
    test=user_input()
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 391, in user_input
    do_inventory()
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 298, in do_inventory
    trial = item_interaction(test, inventory_names, no_xval_names)
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 269, in item_interaction
    test_inventory = do_action(match, inst) ## added so I don't accidentally wipe game.inventory if something fails.
  File "D:\Git_Repos\choose-your-own\choose_a_path_tui_vers.py", line 158, in do_action
    child = from_inventory_name(child)
  File "D:\Git_Repos\choose-your-own\misc_utilities.py", line 238, in from_inventory_name
    logging_fn(inspect.currentframe(), traceback=True)
None
Could not find inst `<ItemInstance glass jar (9489cf96-783b-49e5-92f5-dba9a060ac38)>` in inst_inventory.


So... inst_inventory is right there. Idk why it can't find it...

Ahhh, okay. So, it's failing now beause I told it to remove items from the inventoy when they were added to a container, but it's still checking against the inventory to get the item instance. Okay. that's fixable. Just need to get the instance obj from the children of parent, instead of inv list, because we're already accessing the parent obj. So should be simple enough.

8.27pm okay I think that's fixed.

Next:

# Dropped batteries.
#
# Load lightened, you decide to carry on.

batteries are dropped but not found at the location.

Okay, fixed that now too.

Briefly tried to get logging set up again and I'm so goddamn tired I can't think. It's not that it's hard, I just can't deal today. Support was a mess and I got no sleep and I'm wrecked, really wrecked.

10.04am, 30/12/25

Spent a few hours last night reading https://intfiction.org/t/rez-v1-7-0-open-source-tool-for-creating-non-linear-games-if/. Far more complex than what I'm capable of but interesting nonetheless.

I'm curious about using an existing interacting-fiction engine but can't find many comparisons between them that tell me anything useful. I downloaded Inform 7, and while it has obvious potential the structure of it is maddening to me. Didn't help that I couldn't make any progress at all on the most basic example 'game' they have, I have to assume there are genre conventions I needed to know but it wasn't a great start. (You start in a garden, looking at a hut. I couldn't look at/enter/examine/open/anything else the hut, either by using its full name or just 'hut' or 'the hut'. Literally googled how to progress. In the end i had to type 'in' or 'inside', with nothing else added, and that put me in the hut.) I just don't think that game works how I think about things.

But yes. While I'm not really considering using Rez (though it is more in line with what I'm doing personally, the point is that I'm enjoying making it myself), it has given me the idea of verb-objects. So, instead of giving the options (["stay", "go"]), the options would be '[stay_obj, go_obj]', and those objects would contain themselves the allowable variations, instead of them being processed by the input fn. So if an instance can be dropped, it would trigger the 'drop_obj', etc.

So, using 'drop' as the example -

Currently, 'drop' is just a string, and added to the actions by 'can_pick_up' and 'in_inventory' being true.

If it was an obj, it would contain information, such as:
    the instance that triggered it
    which strings are acceptable as input (less viable for 'drop' but for eg: 'hit', 'punch', 'assault' for "attack")

8.29pm Spent a couple of hours today figuring out a UI in godot. Don't think I'm going to do the game in it, but was interesting nonetheless. Also my 'd' key is dying. Damnit.

9.59pm
Have written up a very basic verb registry. Not close to usable yet, but it's something. Works in basic testing, will identify the verb object and the location name from "go to the graveyard".


Not done here, but instead of testing the words themselves first, maybe we identify the format first - based on length, then null words, we figure out which verbs it /could/ be, and check those, instead of checking every single verb every time. Might be a false benefit though if it means we end up checking repeatedly. Idk. Just a thought. Too tired. Have a cold or something it turns out so I'm braindead.

9.07pm 1/1/26

working on the verbRegistry some more.

Briefly had this issue:

TOKENS: [Token(text='go', kind={'noun', 'verb'}), Token(text='to', kind={'null', 'direction'}), Token(text='the', kind={'null'}), Token(text='graveyard', kind={'location'})]
verb, format keys: Token(text='go', kind={'noun', 'verb'}), set()
confirmed verb: None

TOKENS: [Token(text='go', kind={'verb', 'noun'}), Token(text='to', kind={'null', 'direction'}), Token(text='the', kind={'null'}), Token(text='graveyard', kind={'location'})]
verb, format keys: Token(text='go', kind={'verb', 'noun'}), {('verb', 'direction', 'location')}
confirmed verb: <__main__.VerbInstance object at 0x000001F9790F1FD0>

Where it would only recognise the first 'kind', and if the first 'kind' wasn't the verb, it'd fail. I need to implement format_options, where it generates potential format keys for each variation (so "noun (null) location" and "verb (null) location", then check if any/all of the options are viable formats. Then it takes any viable candidates forward to the next stage, instead of arbitrarily deciding which of the potential kinds are canonical.)

Tomorrow, though. Nearly no sleep last night so I need rest. But, it does work -

#    verbs.input_str_parser("go to the graveyard")
#    from set_up_game import game, set_up ## might break
#    set_up(weirdness=True, bad_language=True, player_name="Testing")
#    verbs.input_str_parser("pick up the paperclip", inventory=game.inventory)
#

Both of those successfully find the verb-instance-obj they should, including the conversion of 'pick up' to 'take'. (That conversion is done very roughly at present but I have a thought in mind to do it in a much better way, tomorrow.)
