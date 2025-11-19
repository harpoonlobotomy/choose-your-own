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
