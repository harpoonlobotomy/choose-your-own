## choose-your-own

A little text-based adventure. Still in its infancy, no idea where it's going yet.

Started 1/11/2025.


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

