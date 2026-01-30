test results for the parser tests.

# input str: `go to shed`
# Nothing found here by the name `shed`.
# Sequence: ('verb', 'direction', 'location')
#
# [[ ROUTER INPUT LIST:  go to work shed  ]]

# result( You turn to face the west graveyard)
correct

{go north: works.}

#   input str: `go to work shed`
#   Perfect match: work shed
#   Perfect: idx: 2, word: work, canonical: work shed
#   Sequence: ('verb', 'direction', 'noun')
#
#   [[ ROUTER INPUT LIST:  go to work shed  ]]
correct

{go north: works.}

#   input str: `go to shed door`
#   Perfect match: shed door
#   Perfect: idx: 2, word: shed, canonical: shed door
#   Sequence: ('verb', 'direction', 'noun')
#
#   [[ ROUTER INPUT LIST:  go to shed door  ]]
correct

(still at work shed ext/west graveyard)

#   input str: `go to work shed door`
#   Perfect match: work shed
#   Perfect: idx: 2, word: work, canonical: work shed
#   No viable sequences found for go to work shed door.
#   verb direction noun noun
#   Raw tokens: [Token(idx=0, text='go', kind={'verb'}, canonical='go'), Token(idx=1, text='to', kind={'direction'}, canonical='to'), Token(idx=2, text='work', kind={'noun'}, canonical='work shed'), Token(idx=4, text='door', kind={'noun'}, canonical='shed door')]
# previously this would have exited as it has no sequence, currently it just ignores and lets you re-enter input.

input str: `open door`
Sequence: ('verb', 'noun')

[[ ROUTER INPUT LIST:  open shed door  ]]

noun_inst.is_open now: False
You open the shed door.
noun_inst.is_open now: True
#   correct

input str: `close door`
Sequence: ('verb', 'noun')

[[ ROUTER INPUT LIST:  close shed door  ]]

You close the shed door.
noun_inst.is_open now: True
noun_inst.is_open now: False
#   correct

input str: `go into shed`
More than one viable sequence. Help?
[('verb', 'direction', 'location'), ('verb', 'direction', 'noun')]
[This should be where it's culled down, right? Idk. Or maybe we just go with the first here and refine it later if it breaks. Idk yet. For now, just quit. Shouldn't be more than one I think.]
Sequence: ('verb', 'direction', 'location')
Sequence: ('verb', 'direction', 'noun')

[[ ROUTER INPUT LIST:  go into shed door  ]]

noun.enter_location: <placeInstance work shed (ee9858e2-99c5-4f41-ad04-9a2ad2df4d36)>
You can't enter through a closed door.
# correct technically, though it should probably assume I mean to open it (if it's not locked.)

(when in work shed already:)
#   [[ ROUTER INPUT LIST:  go into work shed  ]]
#
#   noun <ItemInstance work shed (baf03e5a-e8e0-477a-b195-fe6dbd20f7e8)> is loc #  ext has transition objects: <ItemInstance shed door (68b420ce-9830-4d78-abd3-d046098f24a3)>
noun.enter_location: <placeInstance work shed # (ee9858e2-99c5-4f41-ad04-9a2ad2df4d36)>
You head back out through the door.
#   You're now in the graveyard, facing north.
#
#   You're in a rather poorly kept graveyard - smaller than you might have #   expected given the scale of the gate and fences.
The entrance gates are to the north. To the east sit a variety of # headstones, to the south stands a mausoleum, and to the west is what looks like a work shed of some kind.
#
#   incorrect, should respond 'already at loc.current.place'.

While outside shed:
#   input str: `leave shed`
#   Nothing found here by the name `shed`.
#   Sequence: ('verb', 'location')
#
#   [[ ROUTER INPUT LIST:  leave work shed  ]]
#
#   <ItemInstance shed door (68b420ce-9830-4d78-abd3-d046098f24a3)>
#   input_dict: {0: {'verb': {'instance': <verbInstance leave (556bb11a-9145-46fc-9c50-01450994734d)>, 'str_name': 'leave'}}, 1: {'location': {'instance': <placeInstance work shed (ee9858e2-99c5-4f41-ad04-9a2ad2df4d36)>, 'str_name': 'work shed'}}, 2: {'noun': {'instance': <ItemInstance shed door (68b420ce-9830-4d78-abd3-d046098f24a3)>, 'str_name': 'shed door'}}}
#   enter location via go
#   noun.enter_location: <placeInstance work shed (ee9858e2-99c5-4f41-ad04-9a2ad2df4d36)>
#   The door creaks, but allows you to head inside.
#   You're now in the work shed, facing north.
#
#   Around you, you see the interior of a rather run-down looking work shed, previously boarded up but seemingly, not anymore.
#   There's a simple desk, hazily lit by the window over it to the north.
#
 Incorrect, should fail as we aren't /in/ the shed anymore.

Next test set:
drop/take magazine, works. Drop magazine at other-loc, fails correctly.


Failure:
#   #    input str: `go into work shed`
#   Perfect match: work shed
#   Perfect: idx: 2, word: work, canonical: work shed
#   Sequence: ('verb', 'direction', 'noun')
#
#   [[ ROUTER INPUT LIST:  go into work shed  ]]
#
#   noun <ItemInstance work shed (53838937-235d-4b5f-91e6-cb2ca8d27673)> is loc ext has transition objects: <ItemInstance shed door (bd542cdc-0a09-45c2-bc3b-675943aa9605)>
#   noun.enter_location: <placeInstance work shed (59cdd9cb-e7b9-4db0-9a4e-8bb189a71a2b)>
#   You turn to face the west graveyard
#   Standing in unkempt long grass, you see what looks like a work shed of some kind, with a wooden door that looks like it was barricaded until recently.
#
This should just fail, because we can't enter with the door closed. Go enter != go to in this case.

partial failure:
#   #    input str: `open work shed door`
#   Perfect match: work shed
#   Perfect: idx: 1, word: work, canonical: work shed
#   Sequence: ('verb', 'noun', 'noun')
#
#   [[ ROUTER INPUT LIST:  open work shed shed door  ]]
Accurately found 'shed door' to open, but the input 'open work shed shed door' is wrong. I think this is a specific issue I'll need to accomodate though, not a general failure. It's correctly identifing both nouns, I'm just using a colloquial name that includes a noun, and that's breaking it.

open shed door after this works correctly (fails because closed)


Major failure:

#   #    input str: `go into shed`
#   More than one viable sequence. Help?
#   [('verb', 'direction', 'noun'), ('verb', 'direction', 'location')]
#   [This should be where it's culled down, right? Idk. Or maybe we just go with the first here and refine it later if it breaks. Idk yet. For now, just quit. Shouldn't be more than one I think.]
#   Sequence: ('verb', 'direction', 'noun')
#   Sequence: ('verb', 'direction', 'location')
#   self.by_name: {'city hotel room': <placeInstance city hotel room (88937a03-3d16-4cca-a942-db118e33c062)>, 'forked tree branch': <placeInstance forked tree branch (5c96b487-2686-4768-a72b-ac67986e44a7)>, 'graveyard': <placeInstance graveyard (6bba6c7e-ea2f-4079-ab32-201373b26a28)>, 'pile of rocks': <placeInstance pile of rocks (f03cad5c-93d5-4ea8-8f6d-b3d92d5c2614)>, 'shrine': <placeInstance shrine (84f72473-2454-455b-ad6e-e22ca347112f)>, 'church': <placeInstance church (fd2c2a1e-b840-49e5-bcf6-51c57eaeeee4)>, 'work shed': <placeInstance work shed (59cdd9cb-e7b9-4db0-9a4e-8bb189a71a2b)>}
#   by_alt_name: {'hotel room': <placeInstance city hotel room (88937a03-3d16-4cca-a942-db118e33c062)>}
#   LOC INST: None, type: <class 'NoneType'>
#   Failed to get placeInstance for shed door. Please investigate. Exiting from env_data.

This is the one I gave up on last night. It has two options for the sequence, and it fails because it tries to get placeInstance for the door. I need to track down where this is happening because it just shouldn't. I couldn't see yesterday where it was failing exactly.


12.23
okay, running some more tests.

Why this:

#    input str: `go to shed`
PARTS: ['go', 'to', 'shed']
parts dict:: type: <class 'dict'>
Word: shed, idx: 2, kinds: set(), word_type: noun
Nothing found here by the name `shed`.

Okay, so it doesn't find the noun because it's not local, but finds the location. Okay, that's fine.

Next:
#    input str: `go to shed door`
PARTS: ['go', 'to', 'shed', 'door']
parts dict:: type: <class 'dict'>
Word: shed, idx: 2, kinds: set(), word_type: noun
Perfect match: shed door
Perfect: idx: 2, word: shed, canonical: shed door
Tokens in get_sequences_from_tokens: [Token(idx=0, text='go', kind={'verb'}, canonical='go'), Token(idx=1, text='to', kind={'direction'}, canonical='to'), Token(idx=2, text='shed', kind={'noun'}, canonical='shed door')]

SEQ in sequences: ['verb', 'direction', 'noun']
Sequence: ('verb', 'direction', 'noun')

[[ ROUTER INPUT LIST:  go to shed door  ]]

noun.enter_location: <placeInstance work shed (eb1c68a3-9fa2-432a-97f1-634f205f1c94)>
You turn to face the west graveyard

This should fail because it's an object, right?
But I can't exclude it just on that, can I?
