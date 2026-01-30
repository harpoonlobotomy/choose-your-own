temp_notes_while_Im_back_on_this_branch.md


go to shed
Failed: list index out of range
[[  go to work shed  ]]he name `shed`.


go into shed
Failed: list index out of range
More than one viable sequence. Help?
[('verb', 'direction', 'location'), ('verb', 'direction', 'noun')]
[[  go into shed door  ]]


This always fails with list index out of range errors. I'm pretty sure that's what I tried to fix yesterday...


open shed door
Before parts[idx+matches_count]: 0
Before parts[idx+matches_count]: 0
Before parts[idx+matches_count]: 0
Before parts[idx+matches_count]: 0
Nothing found here by the name `shed`.
Before parts[idx+matches_count]: 0
Before parts[idx+matches_count]: 0
Before parts[idx+matches_count]: 1
After parts[idx+matches_count]: 1
Before parts[idx+matches_count]: 2
After parts[idx+matches_count]: 2
Perfect match: shed door
No viable sequences found for open shed door.
verb location noun

Yeah so without hte changes I made it fails even harder. I don't think this version had location items properly implemented.

Okay. Going to try to just mush the current edit of verbRegistry with the later version of everything else.

---------

Maybe if I add 'door' as a special thing, then if it finds 'open {location} door' it'll find the loc_item instance?
Because right now (post smushing) it takes 'open work shed door' and outputs 'open work shed work shed'.
And it really shouldn't, because 'shed door' is... not 'work shed'.
I'm way too tired to fix this today tho.


--------------
2.52pm
Okay now it's literally saying

open shed door
Word: shed, bit: work, idx: 1, compound_word: work shed, i: 0
Before parts[idx+matches_count]: 0
Word: shed, bit: shed, idx: 1, compound_word: work shed, i: 1
Before parts[idx+matches_count]: 1
Perfect match: work shed

'work shed' is a perfect match for 'shed door'.

I'm going insane...
