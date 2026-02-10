7.39am 10/2/26
Going to just run it over and over until all the errors are cleared.
Had to turn off events otherwise everything breaks as I've moved all items to Everything location.

Errors in the test block:
(  Func:  move_item    )
inst: <ItemInstance paperclip (a9377328-60af-4ced-9709-524ade2af83c)>
new_container: <ItemInstance wallet (665256cf-8d4c-4cd7-a01b-cf80b6b39330)>
Failed parser: 'NoneType' object has no attribute 'add'

 # Hopefully fixed at 736 itemReg.
##########################################

 [[  place dried on headstone  ]] (means 'dried flowers', will set it back to printing instance names for the next run.)

Cannot process {0: {'verb': {'instance': <verbInstance put (43967a2f-20e2-4d82-9657-d2ba5ed667d7)>, 'str_name': 'place', 'text': 'place'}}, 1: {'noun': {'instance': <ItemInstance dried flowers (7cf6d1bf-f88d-4076-bda5-36ecb7c029e9)>, 'str_name': 'dried flowers', 'text': 'dried'}}, 2: {'direction': {'instance': None, 'str_name': 'on', 'text': 'on'}}, 3: {'noun': {'instance': <ItemInstance headstone (d517bcf8-e8e6-4dfb-9d0b-b35a88f50b72)>, 'str_name': 'headstone', 'text': 'headstone'}}} in def put() End of function, unresolved.

# Added 'on' to down_words in verb_actions, may be fixed. But there's no text for 'putting a thing on a thing', nor will it recognise in descriptions etc that a thing is on something else. Exceptions are tables etc where they can basicalyl be containers.
Ugh no. I need /surfaces/. I kinda got halfway there with the walls/floors. Idk. Will think on that part. But it should at least not error next time, or at least not in the same way..

##########################################

You're in a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east sit a variety of headstones, to the south stands a mausoleum, and to the west is what looks like a work shed of some kind.

There's a dark fence blocking the horizon, prominently featuring .

No item descriptions for north graveyard. Should have the gate and padlock, it used to. I did change a heap of descriptions though so maybe that broke it... Have added some more prints to figure out where it's failing.

###############

(  Func:  verbReg_Reciever    )
[ Couldn't find anything to do with the input `approach the forked tree branch`, sorry. <after get_sequences_from_tokens>]
Failed parser: too many values to unpack (expected 2)
Press any key to continue to next.

'approach the x' is not language I expect anyone to use, but -
if x is location, 'go to x'.
If x is noun, look at/investigate noun.

#####################

Hm.
(  Func:  get_item_by_location    )
loc_cardinal: <cardinalInstance north graveyard (6f5a22b7-211c-4e07-a79f-d7c0e7a2fb03)>
It's still looking at north graveyard. I really thought I'd set it to...

OOOOh. One of the commands was to go to graveyard. Right.

######################

Same error as the 'approach forked tree branch'.

[ Couldn't find anything to do with the input `read the fashion mag in the city hotel room`, sorry. <after get_sequences_from_tokens>]
Failed parser: too many values to unpack (expected 2)

I believe the error is happening here:

return [tuple(seq) for seq in viable_sequences if seq], verb_instances

Have added a print to see what 'verb_instances' is here so I can figure out why this return is bad.
Or it is just
[tuple(seq) for seq in viable_sequences if seq]
?
Does that not return /anything/ if there are no viable sequences? Surely it should at least return None, right?

Also, this one for some reason has counted 'city hotel room' as two tokens:

#   values: ("token_role_options: Token(idx=6, text='city', kind={'location'}, canonical='city hotel room') // kinds: {'location'}",)
#
#   values: ("token_role_options: Token(idx=7, text='hotel', kind={'location'}, canonical='city hotel room') // kinds: {'location'}",)

So that needs working on too.

###########
* 'What do you want to break the TV set with?' doesn't return, so it prints the end of fn error msg.

* 'break jar' just errors immediately. It should be breakable, maybe I didn't add  the tag. Yeah, I didn't add the fragile tag. Fair.

* `clean watch` just ends. Have added a fix at 726ish.
> clean severed tentacle should be fixed the same way.

* combine unlabelled cream with anxiety meds > fails because I've not written 'combine' yet. Have written something basic, a placeholder unless 'with y' happens to be a container in which case it reroutes to def put.
> Then the same for combine fish food and moss

########
Actual issue, not just undone functions:

You decide to consume the fish food.
something something consequences
Failed parser: set.pop() takes no arguments (2 given)

Ignoring the 'something something consequences', that pop is bad. (Am actually doing at least one stage of bugfixing as they come along, rather than running it 1000 times on just one issue. Thus the detailed notes so I can check if I actually improved things.) (Anything not mentioned, it went well. (I should be using the notes in the json file it's writing to but I forget.))
Oh, the issue with 'pop' was... a remnant from the script gippity wrote months ago when I didn't know how classes worked yet. I never used it beore.
 inst = self.instances.pop(inst_id, None)
 It shouldn't be 'pop' anyway, instances is a set... Maybe it was a dict once? I don't remember. Fixed now I think.

 ###############

Old issue again:
[ Couldn't find anything to do with the input `burn the fashion mag in a pile of rocks`, sorry. <after get_sequences_from_tokens>]
Failed parser: too many values to unpack (expected 2)

Is that just when it can't find a single sequence? I think it might be. Because this would be verb_noun_dir_loc, which does exist but not with 'burn'.
Maybe I need an output message for 'all the parts of this make sense but it's not a sentence'.

Although looking at the token role optins print...

# values: ("token_role_options: Token(idx=0, text='burn', kind={'verb'}, canonical='burn') // kinds: {'verb'}",)
#
# values: ("token_role_options: Token(idx=1, text='the', kind={'null'}, canonical='the') // kinds: {'null'}",)
#
# values: ("token_role_options: Token(idx=2, text='fashion', kind=('noun',), canonical='fashion mag') // kinds: {'noun'}",)
#
# values: ("token_role_options: Token(idx=4, text='in', kind={'direction'}, canonical='in') // kinds: {'direction'}",)
#
# values: ("token_role_options: Token(idx=5, text='a', kind={'null'}, canonical='a') // kinds: {'null'}",)
#
# values: ("token_role_options: Token(idx=7, text='of', kind={'null'}, canonical='of') // kinds: {'null'}",)
#
# values: ('return for sequences: viable sequences: []',)

I think I removed 'pile of rocks' a while back, so it found 'pile' (and ignored because not anything' and then 'of' then 'rocks'. So it failed because verb_noun_dir is also not viable for 'burn' verb.)
Removing that entry from previous test.

Maybe... I should track consecutive failed words. Though it wouldn't have helped with that 'of' in the middle. Hm.
Maybe I should just do something using the verb if it finds one. So, 'You want to burn something, but I can't figure out what'. Maybe. Not sure.
Have changed it to 'in the graveyard'. Basically I /do/ want a standard default, where if you say 'do this thing' and the verb + noun are viable, and the last bit is just 'dir loc', if 'loc' is loc.current, just accept it. If it's not loc.current, 'if you want to verb the noun in loc, you have to go to loc first'. (I kinda prefer that to 'you go to loc' in case that's not what they meant, but I might change my mind later. This is a larger parser change for when my brain is better than it is going to be this week.)

###########

Cannot process {0: {'verb': {'instance': <verbInstance throw (68dd8e49-520b-414b-9a7b-cfc2f9941da0)>, 'str_name': 'lob', 'text': 'lob'}}, 1: {'noun': {'instance': <ItemInstance pretty rock (9a873c23-ce2b-4300-99fc-1741e67bc69f)>, 'str_name': 'pretty rock', 'text': 'pretty'}}, 2: {'direction': {'instance': None, 'str_name': 'at', 'text': 'at'}}, 3: {'noun': {'instance': <ItemInstance window (4a4630be-cdfc-498b-b9cf-5ff46c90173f)>, 'str_name': 'window', 'text': 'window'}}} in def throw() End of function, unresolved. (Function not yet written)

throw rock at window, failed because I've not written anything for it yet.
Did I ever decide if slice_threshold was defence only or if I was using the same for both? I can't use the same for both, surely.
Have added 'slash_strength/smash_strength' for now. Will probably change it to 'slice_defence' and 'slice_attack' though. Have done that now. Currently it's added on all four as 5, perfectly average. Considering adding it as 'strength: {slice_defence' etc}' but don't see much practical benefit at this point. Will be worth it if I add more things.
Have written some simple checks, all of which will do nothing as I've not set those values, but will be okay for now, it'll still show it if worked or not.

#######################

swapped `chuck the glass jar into a pile of rocks` for `chuck the glass jar into the glass jar`, because 'a pile of rocks' we covered earlier and I want to see how it deals throwing a thing into itself (though it has two glass jars currently, because one was created as loc data. Hm. For the test I really should have turned all other item gen off, like I turned off events. Going to add parse_test to config so I can turn those things off universally.)

###########

"set the watch".
Now this fails because that's really specific. I only even have the watch so I could test the parser with 'watch the watch with a watch'. But, I might use it some day, so it's worth adding to def set anyway.
This should always be a 'place thing somewhere' type command. If not, fix me.
Cannot process {0: {'verb': {'instance': <verbInstance set (f9065242-5597-41df-b25f-db5228472f75)>, 'str_name': 'set', 'text': 'set'}}, 1: {'noun': {'instance': <ItemInstance watch (8e322d2b-378e-4fbd-ba04-3b996d7bf4ec)>, 'str_name': 'watch', 'text': 'watch'}}} in def set() End of function, unresolved. (Function not yet written)

Wrote something simple as a placeholder to test routing.

##############

lock/unlock window failed because it didn't have another noun and didn't return after '{item} requires a key, no?'. Now it returns.

############

similarly:

Cannot process {0: {'verb': {'instance': <verbInstance move (49953c52-b7b9-4e93-8208-2229f8d8cc27)>, 'str_name': 'move', 'text': 'move'}}, 1: {'noun': {'instance': <ItemInstance headstone (d517bcf8-e8e6-4dfb-9d0b-b35a88f50b72)>, 'str_name': 'headstone', 'text': 'headstone'}}} in def move() End of function, unresolved.

Wrote a placeholder in def move.
Even wrote a less placeholder bit that checks if noun is static, and refuses to move it if so.

#############

barricade the window with the TV set

'verb', 'noun', 'sem', 'noun'
It did correctly identify the parts, but it went to simple_open_close??
Oh, because 'barricade' is an alt_word of 'close'. Huh.
I think 'barricade' has to be its own thing, surely. That's a pretty specific noun.

Have added the fn and verb definitionm the fn checks if one of the nouns is a door/window, etc. There's no actual barricading yet, though.

#######

Fixed 'observe graveyard' failing because it didn't include loc.current.place as a valid option for len2 look.

####

[ Couldn't find anything to do with the input `go to a city hotel room`, sorry. <after get_sequences_from_tokens>]
This one failed again for the same reason as earlier. And again, it counts 'city' and 'hotel' as different instances, so 'verb dir loc' ends up as 'verb dir loc loc'. But I do need to run this again with the changes made to the parser to see exactly why it's failing, but I do know the cause.

####
'depart' doesn't print anything. It directs to 'go', gets entries, then just stops.
Fixed, just added a check for 1len def go.

######################

Oh, pure 'go' fails too, though I'm less sure why:

(  Func:  loop    )
input_str: go
(  Func:  input_parser    )
input_str: go
(  Func:  get_item_by_location    )
loc_cardinal: <cardinalInstance north graveyard (6f5a22b7-211c-4e07-a79f-d7c0e7a2fb03)>
(  Func:  get_current_loc    )
(  Func:  verbReg_Reciever    )
values: ('Tokenise: idx: 0, word: go',)
Failed parser: list index out of range

Will check.
Could be here:
parts[1]
in
if word in verbs.split_verbs and verbs.split_verbs.get(word) and parts[1] in verbs.split_verbs[word]:
(ln 326, verbReg)

Have added logging to check_compound_words, that should help.

##############

This one's weird.

(  Func:  loop    )
input_str: go to the pile of rocks
(  Func:  input_parser    )
input_str: go to the pile of rocks
(  Func:  get_item_by_location    )
loc_cardinal: <cardinalInstance north graveyard (6f5a22b7-211c-4e07-a79f-d7c0e7a2fb03)>
(  Func:  get_current_loc    )
(  Func:  verbReg_Reciever    )
values: ('Tokenise: idx: 0, word: go',)
(  Func:  verbReg_Reciever    )
values: ('Tokenise: idx: 1, word: to',)
(  Func:  verbReg_Reciever    )
values: ('Tokenise: idx: 2, word: the',)
(  Func:  verbReg_Reciever    )
values: ('Tokenise: idx: 3, word: pile',)
(  Func:  verbReg_Reciever    )
[ Couldn't find anything to do with the input `go to the pile of rocks`, sorry. ]
(  Func:  verbReg_Reciever    )
values: ('Tokenise: idx: 4, word: of',)
(  Func:  verbReg_Reciever    )
values: ('Tokenise: idx: 5, word: rocks',)
(  Func:  verbReg_Reciever    )
[ Couldn't find anything to do with the input `go to the pile of rocks`, sorry. ]
(  Func:  verbReg_Reciever    )
values: ("Tokens after tokenise: [Token(idx=0, text='go', kind={'verb'}, canonical='go'), Token(idx=1, text='to', kind={'direction'}, canonical='to'), Token(idx=2, text='the', kind={'null'}, canonical='the'), Token(idx=4, text='of', kind={'null'}, canonical='of')]",)
(  Func:  verbReg_Reciever    )
values: ("tokens before sequencer: [Token(idx=0, text='go', kind={'verb'}, canonical='go'), Token(idx=1, text='to', kind={'direction'}, canonical='to'), Token(idx=2, text='the', kind={'null'}, canonical='the'), Token(idx=4, text='of', kind={'null'}, canonical='of')]",)
(  Func:  verbReg_Reciever    )
values: ("top of token_role_options: Token(idx=0, text='go', kind={'verb'}, canonical='go')",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=0, text='go', kind={'verb'}, canonical='go') // kinds: {'verb'}",)
(  Func:  verbReg_Reciever    )
values: ("top of token_role_options: Token(idx=1, text='to', kind={'direction'}, canonical='to')",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=1, text='to', kind={'direction'}, canonical='to') // kinds: {'direction'}",)
(  Func:  verbReg_Reciever    )
values: ("top of token_role_options: Token(idx=2, text='the', kind={'null'}, canonical='the')",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=2, text='the', kind={'null'}, canonical='the') // kinds: {'null'}",)
(  Func:  verbReg_Reciever    )
values: ("top of token_role_options: Token(idx=4, text='of', kind={'null'}, canonical='of')",)
(  Func:  verbReg_Reciever    )
values: ("token_role_options: Token(idx=4, text='of', kind={'null'}, canonical='of') // kinds: {'null'}",)
(  Func:  verbReg_Reciever    )
values: ("return for sequences: viable sequences: [['verb', 'direction']]",)
(  Func:  verbReg_Reciever    )
values: ("sequences after sequencer: [('verb', 'direction')]",)
More than one fully viable sequence:
{0: {'verb': {'canonical': 'go', 'text': 'go'}}, 1: {'direction': {'canonical': 'to', 'text': 'to'}}}

1: More than one viable sequence?  How many options are there for 'go to'? I mean sequences after sequencer is literally ('verb', 'direction').
But the important note here is:
# The 'Couldn't find anything to do with the input {}' message may play multiple times within a single string tokenisation. This is bad.

###########

[ Couldn't find anything to do with the input `read the mail order catalogue at the forked tree branch`, sorry. <after get_sequences_from_tokens>]
Failed parser: too many values to unpack (expected 2)

Same error again, and have finally realised 'forked tree branch' also uses two tokens.
I think I need to either make sure omit_next is working properly (which I'll do anyway) or add a function before the sequencer that checks if two sequential tokens of compound_ type are the same kind and have the same canonical name, and if so, combine them. That's surely more likely than someone writing 'go to forked tree branch forked tree branch' with nothing in between.

###
Failed parser: 'ItemInstance' object has no attribute 'children'
Ah. This one's interesting. Because we want to treat 'put batteries into watch' as a container, but watch is not a container (and I don't want to make it one just for this to work like containers do). Think I need to just add 'if noun2 == electronics and noun2.takes_batteries', and noun.is_battery (currently that doesn't exist, need to add it as a type_default maybe.) Have added 'battery' as type_default, will need to update items_main for it to take effect.

