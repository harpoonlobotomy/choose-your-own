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


