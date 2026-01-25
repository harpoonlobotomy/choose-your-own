## Workdoc 2 ##

2.01pm 5/1/26

So. Need to make some actual notes because I've made changes to things and have gotten very bad at keeping notes, apparently.

So, I've set up a verbRegistry, that works much like the itemRegistry. Got that to the point where it can parse a sentence like 'pick up the paperclip' correctly.

But then once I started trying to think about the next step, which is /using/ the verbs, I realised I want a second type of verb-object, because the initial one isn't really about verbs, it's about parsing. All it cares about is that it is /a/ verb, not which one or what it does.

So I've made verb_actions, which takes the output from verbRegistry (which is actually the parser) and contains the verb-specific actions (def drop() etc). But this also meant I created the verbActions registry, which creates action-instances (so, 'drop' is a verbinstance in terms of parsing, but doesn't contain any information on what 'drop' does or requires. So 'drop' as a verbaction contains what other things it needs to know, etc. Figure I'll also assign the word-instance to the action-instance, so once a command has been given once, the verb can immediately go 'oh, I'm this action'.)

So... it's messy, and it really feels like too many layers. It used to just be string parsing, and if the user input was 'drop paperclip', it found 'drop ' and went to the drop function.

Maybe in resolve_verb() in verbRegistry it checks for action-instances of that name? Might be good. Having the two sets of instances makes sense I think...? idk. Not sure if I want that or to just add the verb-action information to the word-instance. I think the difference makes sense, but it just feels so... bulky now. And my head spins when I think about it, though I put that down partly to not being well.

Going to outline the current process.

*********************************

(verbRegistry currently contains a test setup, so will go with that. Not yet implemented into the main script at all.)

Test string == "go to the graveyard"

Test str, inventory and items list is sent to Parser.input_parser. (in verbRegistry.)

String is run through tokenise(), which
#   gets information on current location to check for local objects, gets their names if any.
#   gets the list of inventory names

#   breaks the string into word tokens, identifies their kind (verb, noun, location, sem, dir, null, adjective)
#   manages compound words ('glass jar') (at a basic level at least)
#   returns tokens, one per word (one per compound word where appropriate)

The tokens are sent to get_sequences_from_tokens(), which generates all potential sequences of the tokens provided, then culls those sequences to only those which are viable formats. It also produces verb_options, which is simply a set of verb names found in those tokens.

The tokens are sent to get_non_null_tokens(), which produces a token count. If the sequences is not a matching token count (eg there are 4 tokens but a 'viable' sequences of len(2)), the sequence is discarded. (NOTE: Perhaps should clear the tokens first. Or do it inside the sequence culler. Feels weird to do it in two steps like this.)

For each verb is verb_options (usually just one, currently the system can't deal with multiple verbs - may make it explicit that only one verb is allowed), it resolves the verb to a verb object and returns the winning format key. (NOTE: Should check for existing verb keys early on. Though I guess the verbs are all pre-init'd anyway, so what am I skipping? Idk. The system jsut feels very bloated for what it is atm.)

Originally here it would return just a list of the refined token data, with the canonical name and only the valuable sentence-parts. Now, it returns a dict,
reformed_dict[token_count] = {list(token.kind)[0]: token.canonical} for all parts in get_non_null_tokens, and
reformed_dict[idx][k]=confirmed_verb
for verbs in reform_str.
(This separation is because (apparently) the 'confirmed_verb' may be a verb_obj or not - this really should be clearly resolved earlier.)

***And so ends verbRegistry's initial step***

The dict is then sent to verb_membrane, which holds the VerbActionsRegistry class. The class is initialised, then the dict is sent to route_verbs().

route_verbs() gets the noun instances from the ItemRegistry, and action_instances from verb_membrane. (Reminder: these are not the same instances as the verbInstances in VerbRegistry.)

Once it has the verb and noun instances, it sends noun_inst, verb_inst and reformed_dict to router(), which is in the verb_actions script.

***Here is where it stops doing much of anything***

Router goes through the reformed_dict and gets the verb_inst and noun instances, again. (I think this was from a time where I thought I'd get the dictionary only? And/or, because previously only one noun was sent, and there may be more than one. So maybe we just stop sending the instances beforehand and get them from Router directly? Or we get them all and add them to the dict. Either way, silly to get them twice.)

Then it iterates through noun instances, once again getting the instances in case they're strings (really, really should be sure by this point...) and for each inst, checks the noun_actions.
Each noun instance carries '.verb_actions', which are the actions it's allowed to perform (eg if 'can_pick_up', then it gets 'drop', 'throw' and 'put', etc). If the noun has the verb-name as an allowed action, then it passes.

***This is where it ends***

Actually going from this point to 'go to drop function' is a stop-check for me. Other than just a list of all the verbs + 'if drop, drop()' for each, idk how to dynamically send it to the verb-named function, if there even is a way.
I mean I guess I could just do this:
function_dict = {
            "drop": drop,
}
?
Or at least play with that idea.

4.43pm
Oh, that does work. Okay, so I can just do

    function_dict = {
        "drop": drop,
    }

    if noun_name:
        func = function_dict[verb_inst.name]

        func(noun_name)

and it runs the drop func. Okay, so that's nice. I feel better all of a sudden.

Now I did temporarily try to move the 'parser' class to its own script, but it's massively reliant on the verbRegistry class, and really struggles outside of that. So I think I'm quitting that idea. Wish I'd not named it 'verbRegistry, because that really should be verb_actions name. Eh.


So: questions/choices.

> Should I get the noun instances early, like I get the verbs?
#   I feel like no? But couldn't tell you why.

> At what point should I get the noun_instances? I feel like that's what verb_membrane should be for. It makes sure the dict has all the right parts, the verb_action + noun instances etc. Then the router just sends it to the right function, but doesn't need to get external information.

> Are the two verb + verb_action classes really necessary?
Probably not technically.
VerbInstance holds:                     VerbActions holds:
    id
    name                                    name
    kind **never used**
    alt_words
    null_words
    format **never used, uses wrong name**  formats (all viable formats for that verb)
    distinction                             format_parts (dict, idx=format_element for each format)                                 other (for any other attr (eg distinction etc)
    colour

VerbRegistry holds:                     VerbActionsRegistry holds:
    all verb instnaces                      all verb actions
    by_name                                 by name
    by_format                               by format
    by_alt_words
    null words set
    all verbs set (includes alts)           all verb names (only key verb-names, not alts)
    adjectives set
    semantics set
    formats set                             all_formats set
                                            all_item_action_options (for noun_instance actions)


So... it really looks like it hsould just be the one. No wonder it feels bulky. I can just ignore the alt_words etc one we're out of the registry section. Okay.

Alright. So then I really do just need to use the Registry for both of these. It did feel silly.

In that case, 'verb_membrane' can just be a function within verbRegistry, that routes to verb_actions directly.
Or maybe not, because it still needs to get the noun instances. I don't really want that done inside the verb registry. Though it is just poorly named tbh.

So, on the assumption that 'verbRegistry.py' will be renamed to 'parser.py' or something in the future, will add the noun-instance-getter to verbRegistry.py, and add the specific parts currently only in the verbAction instances to the regular verb instances. Then reroute to verb_actions from there.


So. If we're using the same verb instance, then it makes sense to simply add that to the resulting dict once it's been found.

------

3:25pm
So... what is 'resolve_verb' even doing here? We literally get the verb during 'sequences', discard it, then check to see if it's viable again?
We send the format key to resolve_verb, then just send it out again, it doesn't check against anything.

Oh--- it checks to see that the verb found has the currently-testing format key as an acceptable format. That's what it's doing, it's not testing the /verb/. Rightright.

We already test that the sequences are viable globally in get_sequences_from_tokens.  Any by that point we've found the verb. So instead, I'll just get the already-found verb instance's accepted formats and use that directly.

(Will enforce the 'only one verb found' later, too. Having two verbs of the same name makes no point. Any potential conflict (like 'set on fire' and 'set on floor'), we deal with inside that verb, or in the router fn.)

4.11pm

Ohh, now I remember. Getting the noun instances is tricky because they're item-specific, whereas verbs are the same regardless. So for the nouns I need to check if they're in inventory and so on.
Sooooo....

First thought - remove the inventory checks etc from the Parser. Just give it the static wordlists (inc item defs) to confirm it's a noun, but then once the parsing is done, check the context.

Maybe 'verb_membrane' needs to be 'context_membrane', and there it figures out if it's inventory instance or whatever else.

but that's tricky, because what if I say 'get paperclip'? I might already have one in the inventory, so it can't just search there first and assume that's what I meant, if there's also one on the table.

Maybe the verbs themselves need to direct it. So, 'get' would search the location + containers, but /not/ inventory. That makes more sense.

So we don't check for noun instances in router, either. Just forward it on to the verb. Router is just an entry-point to verb_actions, it doesn't nee to do more than direct its input onward.

Well it can check some default instance for matching noun_actions, but that's not 'the' instance. That works.

So, parsing happens, verb-object (which is the same obj in parsing and in actions) is decided, applicable formats are found. All that is forward as a dict (token/inst data) and a set (suitable/potential formats, which may be more than one (viably)) to router.
Router goes through the noun(s) and for each unique noun, checks if it's applicable for the verb. If not, then return 'You can't {verb} the {noun}'.

Else, forwards on to the verb fn.


5.36pm
Okay, another weird one. Clearly my code has a failure somewhere.

TEST STRING: `pick up the fashion magazine`
MATCH IN PLURAL WORDS: `fashion` FOR COMPOUND WORD: fashion mag
RESULT: [[ 'pick' 'fashion mag' ]]
Viable formats: [('verb', 'noun')]
Kind: noun, entry: pick
Kind: noun, entry: fashion mag
Nouns: {'pick', 'fashion mag'}
Noun: pick
No found ItemInstance for pick
Noun: fashion mag


The format is clearly 'verb, noun'. 'pick' is not a viable noun to choose, but is a verb.

And yet. Why is it coming up as 'kind, pick'?

And strangely only sometimes.

If I run it again, changing nothing:

TEST STRING: `pick up the fashion magazine`
MATCH IN PLURAL WORDS: `fashion` FOR COMPOUND WORD: fashion mag
RESULT: [[ 'pick' 'fashion mag' ]]
Viable formats: [('verb', 'noun')]
Kind: verb, entry: <verbRegistry.VerbInstance object at 0x0000022A1748A680>
Kind: noun, entry: fashion mag
Nouns: {'fashion mag'}
Noun: fashion mag
No found ItemInstance for fashion mag


Dict from registry: {0: {'noun': 'pick'}, 1: {'noun': 'fashion mag'}}
Dict from registry: {0: {'verb': <verbRegistry.VerbInstance object at 0x0000024E49DBA680>}, 1: {'noun': 'fashion mag'}}
Kind: verb, entry: <verbRegistry.VerbInstance object at 0x0000024E49DBA680>

Same script(s), run seconds apart. Seems random.

Didn't use to do this, I've clearly introduced something in this changeover to membrane.

Okay fixed it. Somehow I'd been feeding it the verbs list instead of the nouns. No wonder it broke.
Not sure why it was successful in identifying the format though, when it hadn't recognised the verb as a verb.

Oh, because it adds both verb and noun, because all_verbs is generated separately. So when it finds 'pick' in items because of the list generation error of mine, it adds noun. That does make sense.


7.19pm
Okay, getting there now. Drop function works with 'drop x in y' and 'drop x at y' depending on whether y == item + container or y == location.

7.47pm
tbh it feels like I should make the locations instances, too. I thought I had but I guess I never made use of it.



7.89pm 6/1/26
Still working on the verbs.

TEST STRING: `watch the watch`
idx 0, word: watch
idx 1, word: the
Word in initial: the
null word: the
idx 2, word: watch
Tokens: [Token(idx=0, text='watch', kind={'verb', 'noun'}, canonical='watch'), Token(idx=1, text='the', kind={'null'}, canonical='the'), Token(idx=2, text='watch', kind={'verb', 'noun'}, canonical='watch')]
Sequences: [['verb', 'verb'], ['verb', 'noun'], ['noun', 'verb'], ['noun', 'noun']]
This sequence is compatible with verb_instance look: ['verb', 'noun']
length checked sequences: [('verb', 'noun')]
Build dict: {0: {'verb': 'watch'}, 1: {'verb': 'watch'}}
Token index: 0, data: {'verb': 'watch'}
kind: verb, entry: watch
entry 0 is confirmed verb look
Token index: 1, data: {'verb': 'watch'}
kind: verb, entry: watch
entry 1 is confirmed verb look
RESULT: [[ 'watch' 'watch' ]]
Verb: `look`
Verb: `look`
Kind: verb, entry: <verbRegistry.VerbInstance object at 0x000001B03CBDA200>
Kind: verb, entry: <verbRegistry.VerbInstance object at 0x000001B03CBDA200>
All nouns (0) are suitable for this verb (look). Sending onward.
Format:  ('verb', 'noun')
NOUN INDEX: 1
dict_values([<verbRegistry.VerbInstance object at 0x000001B03CBDA200>])
For simple verb-noun dispersal

That was number 41

Works fine. But:

TEST STRING: `watch the watch`
idx 0, word: watch
idx 1, word: the
Word in initial: the
null word: the
idx 2, word: watch
Tokens: [Token(idx=0, text='watch', kind={'noun', 'verb'}, canonical='watch'), Token(idx=1, text='the', kind={'null'}, canonical='the'), Token(idx=2, text='watch', kind={'noun', 'verb'}, canonical='watch')]
Sequences: [['noun', 'noun'], ['noun', 'verb'], ['verb', 'noun'], ['verb', 'verb']]
This sequence is compatible with verb_instance look: ['verb', 'noun']
length checked sequences: [('verb', 'noun')]
Build dict: {0: {'noun': 'watch'}, 1: {'noun': 'watch'}}
Token index: 0, data: {'noun': 'watch'}
kind: noun, entry: watch
Token index: 1, data: {'noun': 'watch'}
kind: noun, entry: watch
RESULT: [[ 'watch' 'watch' ]]
Kind: noun, entry: watch
Noun inst: [<ItemInstance watch (2c1e876b-077d-4eb4-8310-23999319dddf)>]
Traceback (most recent call last):
  File "d:\Git_Repos\choose-your-own\verb_membrane.py", line 152, in <module>
    run_membrane(input_str)
    ~~~~~~~~~~~~^^^^^^^^^^^
  File "d:\Git_Repos\choose-your-own\verb_membrane.py", line 134, in run_membrane
    inst_dict = get_noun_instances(dict_from_registry)
  File "d:\Git_Repos\choose-your-own\verb_membrane.py", line 76, in get_noun_instances
    noun_name = check_noun_actions(noun_inst[0], verb)
  File "d:\Git_Repos\choose-your-own\verb_membrane.py", line 51, in check_noun_actions
    if verb_inst.name in flag_actions[action]:
       ^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'name'

So I need to look into why.


So they're both actually wrong, because they both take either watch == verb or watch == noun.
So I need to... realign them to the format. Because the format key is still there and knows which is which.

Need a specific 'they do match but for some reason are fucky' function. Or just to figure out why it breaks like this and fix it. Should probaly od that one.


Okay, fixed it. Now it checks if the token.kind matches its position in the sequence, and if so, adds the applicable type as the reformed_dict entry.


11.27pm
Fixed, broke and re-fixed the verb setup.
The previous fix worked /sometimes/ but failed under specific criteria, but it's better now.

It's getting a bit less fragile I think. Messed up the verb allocation in the middle so will need to go over that again tomorrow, my brain's just scrambled today.
But it does now correctly allocate multiple noun objects along with the correct verb, so 'get apple from tree' would work now. Still not tied into the game yet, but it's messy enough that I'm happy keeping it in isolation for the time being.

9.37am 7/1/26
Just realised I haven't accounted for interacting with scenery at all yet. Might need another class or smth for that.

10.00am
Working on the outline for how the format + verb functions will actually work beyond just parsing. Realised I'm going to need context beyond game + instance data, eg

'# verb_noun = move item (to where? maybe context.)' -- if the scene is 'there is a box in front of the door', then contextually it's pretty clear the intent is to get the box out of the way.
So I need to think about how to work that.

I'm thinking maybe the membrane take in scene-specific data, and after sending off to the parser and running through the router, it can add data from the scene more generally with the results of the router.

11.19am
goddamn I think I need a membrane class too.

This is so dumb. Surely I just need to put it all in one place, no...?

1.22pm
Changed the parser's output dict so it retains original inputted text instead of relying on the instance name. For both the verbs and nouns, so while it'll act on the fully-named noun, it'll return whatever you gave it. (At least for the moment. Might not always be applicable.)

Oh damn I just realised I could have assigned it to the verb object itself. Although maybe not because then it'd change each time... that could get funky. Idk. TODO: Potentially save the current-name for the verb on the verb object.

3.18pm
Added the location instances to the dict in membrane.

3.27
realised I'm not using location instances basically anywhere. Need to. Would solve the damn 'a graveyard/graveyard' issue somewhat. Hell I can just have a place.a_name variant (and place.the_name if I'm feeling ostentatious) and do away with it hardcoded entirely. How nice would that be.

I'm really sad. Probably not going to get muich else done today.


10.10am 8/1/26

Have the location instances plugged in. They work nicely now. And I was right yesterday, the a_name/the_name variants are lovely. Will still need  the 'switch_the' fn for some other things, but removing the 'a ' from the literal names and adding
        self.a_name = "a " + name
        self.the_name = "the " + name
to the class means I can just set this:
        slowWriting(f"You wake up in {assign_colour(loc.current.a_name, 'loc')}, right around {game.time}. You find have a bizarrely good sense of cardinal directions; how odd.")
        slowWriting(f"`{game.playername}`, you think to yourself, `is it weird to be in {assign_colour(loc.current.the_name, 'loc')} at {game.time}, while it's {game.weather}?`")
and have it work.

I've basically replaced all instances of game.place with loc.current. 'loc.current' is self.current of placeRegistry, which holds all placeInstances keyed by name. So loc.current == the current place instance

11.13am
So I'm going to have to redo the main structure of the game, because it's so definitively geared around 'here are your discrete possible answers, here's the selection you made from those'.

So I think I just need to rejig it, take old parts from the existing (all the copy text etc can be reused) and go with that.


11.32am

Input dict: {0: {'verb': {'instance': <verbRegistry.VerbInstance object at 0x000001CFF9B96900>, 'str_name': 'go'}}, 1: {'direction': {'instance': None, 'str_name': 'east'}}}

I really need to make the location:cardinals instances too, nested under those locations.

Not exactly sure how it'd work, and I need to be careful not to rule out cardinal travel (if at some point I want them to be alble to travel 'east', generally, instead of 'east {place}'). But generally it will work - you start by default in the graveyard, not facing any direction. So 'go east' should take you to the east-graveyard instance. And that can hold the location-items, instead of the primary location instance. Mm. Okay. Will think about it.

Maybe 'if you're in a location, 'go east' == 'go east within this space if there is one'. Then at some other point if there's like, map-based travel, we just use alt contextual east. I think that works.

3.27pm
Have set up the location instances with cardinals. Happy with it for the moment.

"locRegistry.by_cardinal("north").place_name" uses current location if no loc is given, and returns the location's cardinal instance's place_name.

So when we're at the east graveyard, I can just use locRegistry.by_cardinal("east").place_name to have it print such, instead of manually having to fetch the cardinal data via dict. Also makes local items much easier. Wil need to update the itemRegistry accordingly, but that already needed a major overhaul so I'm okay with it.

Still need to move cardinal_actions to the cardinals themselves and have to make sure I use the cardinals directly instead of locations, but I think it'll work. Have added self.place to cardinals, so the cardinal instance holds its association.  If the place we'r at is locRegistry.by_cardinal("east"), we can get the overall place inst back with locRegistry.by_cardinal("east").place

locRegistry.set_current("graveyard")
print(place_cardinals["east"].place_name)
place = place_cardinals["east"].place
print(place.name)

==

Set loc.current to graveyard
east graveyard
graveyard


4.07pm
decided to add 'cardinals' as a new kind-type, but just realised it means adding cardinals to each format. But that's probably not a bad idea really, a bit of a pain to do now but it makes sense.

Maybe not 'cardinals' exclusively. Maybe something that encompasses 'left/right' etc instead. Something that differentiates from 'to/from/at' etc.

Going to call it cardinals for now anyway. Can change it later.

5.58pm
[[  go east  ]]
go east
Tokens: [Token(idx=0, text='go', kind={'verb'}, canonical='go'), Token(idx=1, text='east', kind={'cardinal'}, canonical='east')]
verb instance: <verbRegistry.VerbInstance object at 0x00000246DB106BA0>
Name: go
Sequences: [['verb', 'cardinal']]
This sequence is compatible with verb_instance go: ['verb', 'cardinal']
Winning format: ('verb', 'cardinal')
dict_from_parser: {0: {'verb': {'instance': <verbRegistry.VerbInstance object at 0x00000246DB106BA0>, 'str_name': 'go'}}, 1: {'cardinal': {'instance': None, 'str_name': 'east'}}}
kind: verb, entry: {'instance': <verbRegistry.VerbInstance object at 0x00000246DB106BA0>, 'str_name': 'go'}
kind: cardinal, entry: {'instance': None, 'str_name': 'east'}
Kind is cardinal: {'instance': None, 'str_name': 'east'}
card_inst: <env_data.cardinalInstance object at 0x00000246DB093B60>
kind: verb, entry: {'instance': <verbRegistry.VerbInstance object at 0x00000246DB106BA0>, 'str_name': 'go'}
kind: cardinal, entry: {'instance': <env_data.cardinalInstance object at 0x00000246DB093B60>, 'str_name': 'east'}
Input dict: {0: {'verb': {'instance': <verbRegistry.VerbInstance object at 0x00000246DB106BA0>, 'str_name': 'go'}}, 1: {'cardinal': {'instance': <env_data.cardinalInstance object at 0x00000246DB093B60>, 'str_name': 'east'}}}
input_dict[1]: {'cardinal': {'instance': <env_data.cardinalInstance object at 0x00000246DB093B60>, 'str_name': 'east'}}
Going to east graveyard
kind: verb, entry: {'instance': <verbRegistry.VerbInstance object at 0x00000246DB106BA0>, 'str_name': 'go'}
kind: cardinal, entry: {'instance': <env_data.cardinalInstance object at 0x00000246DB093B60>, 'str_name': 'east'}
Input dict: {0: {'verb': {'instance': <verbRegistry.VerbInstance object at 0x00000246DB106BA0>, 'str_name': 'go'}}, 1: {'cardinal': {'instance': <env_data.cardinalInstance object at 0x00000246DB093B60>, 'str_name': 'east'}}}
input_dict[1]: {'cardinal': {'instance': <env_data.cardinalInstance object at 0x00000246DB093B60>, 'str_name': 'east'}}
Going to east graveyard


Proud of this mess.


6.56pm
 Changed 'north' to 'north_desc' to make it clearer once it's added to the cardinals, but realised that's not actually that helpful either.
 So maybe just change it when I'm adding it to the class? Idk.
Or maybe I need to break up the dataset more, just make 'city hotel room' > north > short_desc/desc/actions.
Would make more sense now I'm doing it the way I am. Might do that.

9.06am
didn't sleep again. Have updated the location dict (prev 'dataset') and updated cardinal instances to include the cardinal descriptions, which are now accessable from the place>instance.

11.02am
Yeah so membrane really shouldn't return anything unless it needs to be acted on in the 'story'. Actions should send their own calls, I don't need to add a network of other calls to it.

I think I am going to do the player_movement and item_interactions scripts though, because a lot of those actions are currently done in the main script. I don't have a clear vision for this yet tbh, but I'm trying.

main script holds the 'shape' of the thing, it's what actually 'plays'.
membrane takes input and figures out what's what, and sends out the relevant calls to do whatever the text said.

Originally it was all a pretty linear loop, and I'm just not sure what to replace that with, if that makes sense.

11.50am
Ah, now I see a reason why to separate the action-command from the action happening - I can't print the input the way I want to before the action happening at present, because the action-results are printing inside the functions. So there /is/ a reason to send the calls and /then/ respond. Okay.

Will work on that later, though. Far too tired today to make sense of anything.

But, it is working, to a degree:

# Chosen: (look east)
#
# LOOK FUNCTION
# You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, dried  left long ago.
#
# [[  look east  ]]
#
# What do you want to do? Stay here and look around, or go elsewhere?
# Chosen: (go to city hotel room)
#
# You're now facing north city hotel room
# You're in a 'budget' hotel room; small but pleasant enough, at least to sleep in. The sound of traffic tells you you're a couple of floors up at least, and the carpet is well-trod
#
# [[  go to city hotel room  ]]
#
# What do you want to do? Stay here and look around, or go elsewhere?
#
The commands are being followed, even if there's not much actually happening. Proof of concept stage, at least.
So the to-be new way -

main game gives you things to respond to.
You input, it sends it to membrane for parsing. Membane sends back 'here's what you need to do/say'. then... I guess the main game sends it out again? Idk. This is where I get lost. Maybe just too tired.

This:
instances_by_location(self, place:str, direction:str)->list:
needs an upate; it should just use the loc_cardinal instance, not two strings. Oh jeez. Okay, going to do the smart thing and branch it before I start all that.


2.21pm 10/1/26

Changing itemRegistry to use the cardinalInstances.

Going to add 'inventory' as an actual inventory item maybe. But then would have to exclude it from everything, so maybe not... Yeah actually it'll cause more problems than it solves, I think. Just going to add an 'in_container' flag to items and check against that + an equivalent 'in_inventory' flag.


For some reason, changing this part:
        if loc and not cardinal and self.current == None:
            self.current = loc

in env_data triggers this:
  File "d:\Git_Repos\choose-your-own\itemRegistry.py", line 427, in pick_up
    if not hasattr(inst.flags, "can_pick_up"):
                   ^^^^^^^^^^
AttributeError: 'str' object has no attribute 'flags'
Fixed it. It was failing because it couldn't give/find a location for the startup items, so they weren't proper items. Previously they'd just been assigned the string location name, which had accidentally solved itself later on lookup.

5.10pm
Just realised I was re-running game.set_up() each time I wrote something because the while loop included the full intro. Now the 'while loop' is literally just the inner_loop() itself, until you type 'quit' at which points the whole process ends.

5.31pm
Made a note in membrane re adding a traceback flag in the fn sig of the main memrane parser. But it might be a good idea to add a global logging flag that I can trigger via that input_str. Being able to be mid-run, get a weird result then run the same command again with 'go east traceback' instead of 'go east' and have it log live for that command, instead of having a run with/without logging entirely, would be excellent given the kind of thing this is. Will do that.


6.55pm
[[  take glass jar  ]]

take FUNCTION
Inst list: <ItemInstance headstone (e0d7df0b-1f6f-457c-a64e-44d2730020ec)>
Noun inst glass jar can be accessed.

Hm. This is... odd.
Why is the headstone the only thing that prints, even though the glass jar is outputted correctly?


8.43 just realised I've spent most of the afternoon/evening trying to add 'meta' as a verb and it's not working. Should have just added it as a damn category. No idea why I didn't. Or I did, but tried to make it a verb as well...? Absolutely no clue.

10.06am 11/1/26
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "d:\Git_Repos\choose-your-own\itemRegistry.py", line 480, in pick_up
    self.move_item(inst)
    ~~~~~~~~~~~~~~^^^^^^
  File "d:\Git_Repos\choose-your-own\itemRegistry.py", line 272, in move_item
    if self.by_location_inst.get(old_loc):
       ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
TypeError: unhashable type: 'set'

Tried to pick up the fish food I just dropped, and this. So old_loc is being stored as a set, when it should be a cardinalInstance. Need to work on that.

5.09pm 12/1/26

    self.by_location.setdefault(cardinal_inst, set()).add(inst)
    self.by_cardinal_placename.setdefault(cardinal_inst.place_name, set()).add(inst)
setting up two parallel dicts for item location. It's messy at the moment.


6.56pm
Have fixed the item locations, I think. Not using the placename version at all so will remove it again later.
Cardinals are no longer sub-parts of locations, but instead are just their place_name versions directly. Will cause problems for locations without four cardinal locations potentially, but will come to that later.
Maybe should add a tiny location like a shrine or something that only has one cardinal direction, either you're at the shrine or you're not. Will need to customise loc.current.overview and add additional checks for whether location has x cardinal or not. But for now, you can go to any location, go from any location to any other location (generally or by cardinal location), picking up and dropping items seems to work (though the descriptions don't update; wasn't too much of an issue before because if the item list, but now there's no item list printed by default there's no way to know the active items available at all unless you try to pick things up, which isn't acceptable.)

The user_input options still work, which is nice. So `show visited`, `d`, `i`, etc. Though `i` and `inventory` currently show different things, as the latter is done via membrane. Need to remove one of those. Not sure which.

Current problem to fix:
#   File "d:\Git_Repos\choose-your-own\itemRegistry.py", line 282, in run_check
#     if confirmed_container.is_locked or confirmed_container.is_closed:
#        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# AttributeError: 'ItemInstance' object has no attribute 'is_locked'


Okay that one's done, I think.

Next:


[[  get glass jar  ]]

take FUNCTION
Noun inst glass jar can be accessed.
[[move item glass jar]]

(inventory at this time:
severed tentacle
paperclip x2
gardening mag
fish food
regional map
car keys
anxiety meds
batteries
glass jar*
)

[[  get dried flowers  ]]

take FUNCTION
Item dried flowers is in an container, but you can take it.
[[move item dried flowers]]


[[  drop dried flowers  ]]

drop FUNCTION


i
INVENTORY:

paperclip x2
puzzle mag
unlabelled cream
regional map
batteries
car keys
glass jar
dried flowers

> Issue:
Dried flowers were picked up inside the jar, but not removed from location as I was then able to pick them up. And, after dropping, they're still in the inventory.
So I need to rework the inventory child setup a bit to work with the new system.


Going to make a new scene just for testing.
Needs:
#   a locked box that can be picked up
#   a key for that box
#   an item in that box that can only be seen/interacted w/ after the box is unlocked + opened.
#   an open container with an item in, both of which can be picked up (the container + child if present, or just the child)

I need to use setattr far more. Been sleeping on that one.


1.02pm
Added it so you can just write 'tree' and it'll assume the verb 'go'. So:
#   go to the forked tree branch
 ==
# tree



1.42
Added logging. And the ability to toggle it off/on mid run, which is nice. Not the single-run traceback I had originally, but logging_fn() at the header of each fn to trace the data route, as well as traceback_fn() at expected failure points. Hopefully it helps.

Just encountered a weird one, though:
tree
(  Func:  run_membrane   )
(  Func:  get_current_loc   )
[[  forked tree branch  ]]

(  Func:  go   )
(  Func:  get_current_loc   )
(  Func:  get_entries_from_dict   )
(  Func:  new_relocate   )
You're now facing north
You've climbed up a gnarled old tree, and found a relatively safe place to sit, in the fork of its broad branches. This needs more description but that's all that's written for now..
The entrace gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.
(  Func:  option   )


go to east graveyard
(  Func:  run_membrane   )
(  Func:  get_current_loc   )
[[  go to east graveyard  ]]

(  Func:  go   )
(  Func:  get_current_loc   )
(  Func:  get_entries_from_dict   )
(  Func:  new_relocate   )
You're now facing east
You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.
(  Func:  option   )


look around
(  Func:  run_membrane   )
(  Func:  get_current_loc   )
[[  look around  ]])

(  Func:  look   )
(  Func:  get_entries_from_dict   )
You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.
You're facing east. You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, with dried flowers left long ago.
(  Func:  get_item_by_location   )
(  Func:  check_name   )
(  Func:  register_name_colour   )
(  Func:  check_name   )

You see a few scattered objects in this area:
(  Func:  check_name   )
   carved stick
(  Func:  option   )


Now the carved stick is at east tree. So something is broken.

2.11pm
... Okay so it's even weirder, because looking around in the tree gives you the graveyard's items. What the hell's going on here....

You wake up in a graveyard, right around midnight. You find have a bizarrely good sense of cardinal directions; how odd.
`test`, you think to yourself, `is it weird to be in the graveyard at midnight, while it's perfect?`

You take a moment to take in your surroundings. You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.


[[  look around  ]]

You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.
You're facing north. You think you could leave through the large wrought-iron gates to the north. They're imposing but run-down; this graveyard doesn't get as much love as it could.
LOC CARDINAL PLACE_NAME: north graveyard


[[  look east  ]]

prospective cardinal going to loc test: <env_data.cardinalInstance object at 0x000001AB919EA5F0>
loc.current_cardinal after turn_around: <env_data.cardinalInstance object at 0x000001AB919EA5F0>, type: <class 'env_data.cardinalInstance'>
You turn to face the eastern graveyard
You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, dried flowers left long ago.


[[  look around  ]]

You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.
You're facing east. You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, dried flowers left long ago.
LOC CARDINAL PLACE_NAME: east graveyard

You see a few scattered objects in this area:
   glass jar, moss, headstone


[[  go to forked tree branch  ]]

You're now facing east
You've climbed up a gnarled old tree, and found a relatively safe place to sit, in the fork of its broad branches. This needs more description but that's all that's written for now..
The northern tree parts are  to the north. To the east is an eastern tree part, to the south is a southern tree part, and to the west is what looks like a a western tree part.


[[  look around  ]]

You've climbed up a gnarled old tree, and found a relatively safe place to sit, in the fork of its broad branches. This needs more description but that's all that's written for now..
The northern tree parts are  to the north. To the east is an eastern tree part, to the south is a southern tree part, and to the west is what looks like a a western tree part.
You're facing east. This is the east of a forked tree. Not sure what's here. Maybe a bird's nest..
LOC CARDINAL PLACE_NAME: east forked tree branch

You see a few scattered objects in this area:
   carved stick


[[  go to east graveyard  ]]

You're now facing east
You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.


[[  look around  ]]

You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.
You're facing east. This is the east of a forked tree. Not sure what's here. Maybe a bird's nest..
LOC CARDINAL PLACE_NAME: east forked tree branch

You see a few scattered objects in this area:
   carved stick


[[  go to graveyard  ]]

You're now facing east
You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.


[[  look around  ]]

You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east is a variety of headstones, to the south is a mausoleum, and to the west is what looks like a work shed of some kind.
You're facing east. You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, dried flowers left long ago.
LOC CARDINAL PLACE_NAME: east graveyard

You see a few scattered objects in this area:
   glass jar, moss, headstone



Okay. So it's the turning around. For some reason when we turn, we're not updating the location properly, but it seems like only in the place where the location is checked for items, because the description updates properly.




new_cardinal: <env_data.cardinalInstance object at 0x0000023CD9588050> >- east tree

'go to graveyard' > new_location: <env_data.placeInstance object at 0x0000023CD94E6AD0>
## but i don't know if cardinal is updated here. it should be.

'look east'
cardinal: <env_data.cardinalInstance object at 0x0000023CD952A5F0>

Okay.
So if I change location with specific cardinal, it doesn't update the current_cardinal somewhere. Or maybe it doesn't update current_loc? I need to check. Clearly the description and the items are checking different places, and they shouldn't be.

(This new toggleable args + fn logger is really useful btw.)


2.25pm
Ohh. I think it's because of this:

    if new_location and isinstance(new_location, placeInstance):
        loc.set_current(loc=new_location)

where set_current is a placeInstance, not a cardinal. That should never happen... If we give it a placeInstance, it needs to take the str of currentCardinal and go to that cardinal of the new location. Okay.


No, I'm wrong, that was intentional; 'loc' has always been the general location, while current_cardinal is the cardinal. But... why. Maybe we get rid of loc.current as a placeInstance entirely and just have player movement + items be cardinal-specific. That makes far more sense, right? Why have 'location = graveyard' if everything about my location that matters is relevant only to the cardinal?

I can still have graveyard-wide things apply, cardinal.place still gives us the graveyard instance for travel-tracking, weather etc.

Okay. Going to commit what I have for now and do that. Change it so all player + item-relevant things are to the cardinal-instance, so 'loc.current' is the cardinal, not the general location.

Then I really need to do that test location I had the idea for last night, a proper setup just with things that will probably break and less noise.

3.00 pm

from env_data:
cardinal = self.cardinals[self.current][cardinal]
self.current_cardinal = cardinal

Ah.
So if you update by cardinal, it doesn't update the location at all, /only/ the cardinal. So then, when it later checks 'location' by cardinal.name, the location is still 'tree' or w/e. Which is why the issue doesn't happen if you
go to graveyard
turn east

but does if you
go to east graveyard

Because :
self.cardinals = {} # locRegistry.place_cardinals[place_instance_obj][cardinal_direction_str] <- because we look by cardinal_str here, even if 'current_cardinal' is accurate, the location won't have been updated in this context.

Still kinda want to change it all to cardinalInstances though.

3.08pm
I was missing one really obvious thing in set_current:

        if loc and cardinal:
            if isinstance(loc, placeInstance) and isinstance(cardinal, cardinalInstance):
                self.currentPlace = loc
                self.currentCardinal = cardinal
                return

and def new_relocate() never actually sent the new location, only the cardinal. that's why.

3.55pm
got distracted. Haven't fixed it yet.
"go to east graveyard"

Inst dict: {0: {'verb': {'instance': <verbRegistry.VerbInstance object at 0x00000233A6AFABA0>, 'str_name': 'go'}}, 1: {'direction': {'instance': None, 'str_name': 'to'}}, 2: {'cardinal': {'instance': <env_data.cardinalInstance object at 0x00000233A6A87D40>, 'str_name': 'east'}}, 3: {'location': {'instance': <env_data.placeInstance object at 0x00000233A6AC6710>, 'str_name': 'graveyard'}}}

then in 'look':
loc_cardinal: <env_data.cardinalInstance object at 0x00000233A6A87D40>

Okay so the cardinalInstance applied at 'east graveyard' is not 'east graveyard's', but current_location before the change. Okay.

4.00pm

Ahhh.
check_cardinals is /trying/, but it's checking against 'data'. Which is the value of 'idx, data' in dict_from_parser. So it's only looking at its own entry, which obviously doesn't contain a location.

So I need to expand so it can check the rest of the dict too, then it should be okay. Or I can hard-fix it elsewhere, but that feels messier. Though idk. I mean if it's not at least probably-correct, then there's no point adding the cardinalInst here at all.

Okay so it /might/ be fixed. I say this tentatively.

I haven't shifted everything to a cardinal-only basis yet. Playing on a stripped-down version of the main script, seeing as most of it wasn't being used anyway.


4.41pm

There were notes here, they made no sense and are gone now.



8.10pm:

take ivory jar
ivory jar is now in your inventory.


open jar
No canonical for idx `1`, word `jar`
No viable sequences found for open jar.
verb

So, this fails here. Not sure why. 'jar' worked before, perhaps it's because now there's more than one in the noun dict, even if they're not all viable options. I never did make that as robust as I'd thought about doing.

8.12pm
Yes, that's the issue. If I rename the new jars to pots, then I can use 'take jar' again, though obviously both pots fail.


"instance_name_in_inventory" and "from_inventory_name" can absolutely be collapsed into one. Man so much of this is overlapping for no benefit. Beh.

9.44pm

[[  look at scroll  ]]

You look at the scroll in your inventory.
An old parchment scroll, seemingly abandoned at a hidden shrine.

I need a way to trigger the key falling out from the scroll at this point.

9.53
Well I have it set to just reveal the contents after it's open, but it only shows  it when you first open it, then the contents are seemingly hidden. You could still take key from scroll, but you'd have to know about it. Opening doesn't move the item out of the container.

Maybe I need to add container contents to container, so if not hidden and container is open, 'look at' also lists contents?

10.04pm
Have added that for now.

'use key on metal pot' doesn't work, and it should. Need to fix that tomorrow.

use key on metal pot
No canonical for idx `0`, word `use`
No verb_instance or meta_instance found in get_sequences_from_tokens. Returning None.
TOKENS: [Token(idx=1, text='key', kind={'noun'}, canonical='old gold key'), Token(idx=2, text='on', kind={'direction'}, canonical='on'), Token(idx=3, text='metal', kind={'noun'}, canonical='metal pot')]
No viable sequences found for use key on metal pot.
noun direction noun

(open metal pot with key) does work, though.


10.19pm
Also this:
[[  take old gold key from scroll  ]]

Confirmed container locally, not in inventory: <ItemInstance scroll (8d385860-d1b5-4244-a3d6-8079ededaa75)>
old gold key is now in your inventory.

should not work, as the scroll is closed.


10.24pm
Also this:

[[  open ivory pot  ]]

noun entry: {'instance': <ItemInstance ivory pot (3ee3e8cd-aa34-4689-a98c-b9cd33a9fa56)>, 'str_name': 'ivory pot'}
noun_inst: <ItemInstance ivory pot (3ee3e8cd-aa34-4689-a98c-b9cd33a9fa56)>
reason val: 0
IS_LOCKED: `True`
key: `wire cutters`
CONTAINER: <ItemInstance wire cutters (648853ad-d8be-458e-96ae-906550e6c4ba)>
You need to unlock it before you can open it. You do have the key, though... (wire cutters)


[[  open ivory pot with wire cutters  ]]

list(input_dict[2].values())[0]: with
ivory pot is already open.

10.48pm
also this:

ivory pot


[[  open ivory pot  ]]

noun entry: {'instance': <ItemInstance ivory pot (2e127fec-2b32-491d-b99a-490158f0f312)>, 'str_name': 'ivory pot'}
noun_inst: <ItemInstance ivory pot (2e127fec-2b32-491d-b99a-490158f0f312)>
reason val: 2
IS_LOCKED: `True`
key: `wire cutters`
Confirmed container locally, not in inventory: <ItemInstance metal pot (120ed582-2120-49cb-b81c-eb2c631efa93)>
Container <ItemInstance metal pot (120ed582-2120-49cb-b81c-eb2c631efa93)> is locked.
Container.name metal pot
Could not find confirmed instance for wire cutters
CONTAINER: wire cutters
It seems like you need a way to open it first...


[[  open ivory pot with wire cutters  ]]

list(input_dict[2].values())[0]: with
ivory pot is already open.

I hadn't discovered the wire cutters yet.

And this:
#   ivory pot is already open.
is from the format_tuple 'verb, noun'. But the command was 'open x with y', so it shouldn't have been triggered...

Okay so I fixed part of it, but it's still:

[[  open ivory pot with wire cutters  ]]

list(input_dict[2].values())[0]: with
You open the ivory pot


and i didn't have (or even find) the wire cutters yet.
Oh right. The long form version doesn't check if you have the key, just checks that it's correctly identified.

Not going to fix it further here, going to just make a proper lock/unlock x with key' fn. Actually I'm quite sure I made one already, just not using it. Tomorrow.

Progress is being made, slowly.

4.04am 13/1/26

def check_lock_open_state
# func to determine is a container is locked, unlocked but closed, or open.


8.08am


[[  open scroll  ]]

MEANING (initial): accessible
reason val: 0
scroll is not open.
You need to unlock it before you can open it. What you need should be around somewhere...

Hm.

8.21am
next:

[[  take old gold key from scroll  ]]

old gold key is now in your inventory.

This shouldn't work, the scroll wasn't opened.

##
REASON: in a container but accessible locally, can pick up but not drop

So it's not recognising that the scroll is closed. Around line 288 in itemRegistry.


accessible_dict = {
    0: "accessible",
    1: "in a closed local/accessible container",
    2: "in a locked local/accessible container",
    3: "in an open container in your inventory",
    4: "in an open container accessible locally, can pick up but not drop",
    5: "in inventory",
    6: "not at current location",
    7: "other error, investigate",
}

4.37pm 13/1/26

Okay. This is an improvement:

# [[  get old gold key from scroll  ]]

# Container scroll is closed by is_open flag.
# Sorry, you can't take the old gold key right now.


5.36pm:
weirdness:

[[  open scroll  ]]

You open the scroll

The scroll contains:
  old gold key


[[  open scroll  ]]

You need to unlock it before you can open it. What you need should be around somewhere...


Suddenly now it's locked...?

And I wrote a standalone 'open' function, and it apparently doesn't update the is_open status correctly, so we get


[[  open scroll  ]]

You open the scroll.


[[  open scroll  ]]



[[  open scroll  ]]

You open the scroll.


[[  open scroll  ]]

You open the scroll.

It just keeps opening, and all the while:
 'is_open': False,


think I fixed the open scroll thing. No idea why it broke how it did earlier.


6.22
New oddity:

[[  take anxiety meds  ]]

anxiety meds is already in your inventory.
anxiety meds is now in your inventory.

6.24
Okay, that was simple enough.

Thoughts currently:

Need to add an alternate route for 'take' for things like meds. Need 'take anxiety pills' to route to 'consume'
# Have just added a check, if only 'take x' and 'x' is in inventory and can_consume, then it prompots:

[[  take anxiety meds  ]]
anxiety meds is already in your inventory.
Did you mean to consume the anxiety meds?

It'll do for now. (Added a placeholder for eating, there's a short text print and it removes the item from inventory + registry.)


6.46pm
Hm.

        print(f"Look at item MEANING: {meaning}")
        if reason_val not in (0, 5):
            print(f"Cannot look at {item_inst.name}.")

Should you be able to look at an item in an open container? surely yes, right? But you have to know it's there first...

I think I need to add a 'discovered' tag or something to items. So when you look at the room, you can't just go 'look at thing in jar' (unless it's described in the copy), but once you've looked at the jar and seen what's in it, then you can do 'look at thing in jar'.


11.40am 14/1/16
"You see nothing special." - description of container with contents removed.
Need to set to None and use the default for some objects, not all containers will have different descriptions. And/or the description should dynamically include discovered contents.

1.39pm
Just had a thought. I need to implement item-types, instead of individual flags.
So, instead of

"ivory pot": {"name": "an ivory-coloured jar", "description": f"A tall scratched ivory pot; no label, and a cork stopper held in place with a fine but strong-looking wire tied around the neck.", "description_no_children": f"A tall scratched ivory pot; no label, and a cork stopper held in place with a fine but strong-looking wire tied around the neck.", "flags": [CONTAINER, CAN_PICKUP, CAN_OPEN, CAN_LOCK, LOCKED, CLOSED], KEY:"wire cutters", "container_limits": SMALLER_THAN_APPLE, "item_size": SMALLER_THAN_BASKETBALL, "starting_location": {"test shrine": "north"}},

we have:

"ivory pot": "name": an ivory coloured jar", "description": f"A tall scratched ivory pot; no label, and a cork stopper held in place with a fine but strong-looking wire tied around the neck.", "item_type": typename

where typename contains the typical attributes of that type.

Just need to figure out what the types are.

'active' vs 'static' where 'static' is functionally scenery?

All active can be picked up by default, unless there's some reason why not.

So type category 1 is active/static.
Do I just have that one category, or subcategories? Note that the subcategories have to be mutually exclusive (probably). Or maybe not I suppose, if the item instance is created independently (so 'book' is 'standard', but a particular book might be added to category 'container' and gain those attributes? idk.)

Active:
    defaults: can be picked up
Active>standard:
    defaults: no special flags
Active>container
    defaults: can open, starts closed, may have children
Active>key
    defaults: can be used to open something
    ## Maybe not 'key'. Maybe 'trigger'? Then it might be 'a key that opens a thing', or 'a button that opens a door', etc. 'Thing that causes thing to happen. So yes. Trigger might be better.

Or maybe these aren't 'categories', but sets of flags? I'm not sure. Categories would just be handy I think. When looking for a key for a locked container, checking 'registry.keys' for the instance just makes sense. Or I guess 'registry.keys_by_name()'
And would save having to check all items for a 'container' flag, and just check 'registry.containers'. I think I already do that, but I also add all the extra flags to containers manually.

Maybe instead of active/static as base categories with standard/container/key as secondary, standard/container/key is primary and 'active/static' is an item flag. Otherwise I'd need to check 'is there any active.containers or static.containers'. Better to check 'if there are containers: are any of them active', I think, because the 'container' part is what's relevant.

So, current idea is:

class itemRegistry has

        self.standard = set()
        self.containers = set()
        self.triggers =  set() (prev 'keys')

and every item is in one of those. Mostly mutually exclusive but I guess there's no reason for that to be exclusive (other than 'standard', because that's the catchall for 'not a trigger and not a container' items.)

So 'triggers' might be 'button on the wall' or 'old gold key'. I think that works.

all items in all categories have default flags:

item_size: 0

Items in self.triggers can have specific flags:
    acts_on: item (if 'key opens gold lock on metal jar') or plot event (if 'button means villian appears when you leave the room').
    trigger_exhausted: False (if trigger was one-time or limited and has been used (so pushing a button may not do anything the second time, instead of having to check remotely if an event has run).)
# (( speaking of - a plotInstances might not be a bad idea. Marking which story beats have been met, manage plot trigger states, etc.))

Items in containers have flags with defaults:

    can_be_closed: True
    if so:
        is_closed: True

    can_be_locked: True
    if so:
        is_locked: True

    children: None

    can_add_children:True (False for times when something may have had default contents but cannot hold anything thereafter)

    children_size: self.item_size-1 (default can hold things one size smaller than itself)

    # need something here to limit number of items. Like, a wallet could hold 5-10 small bits of paper, but a basketball sized thing can't hold 5-10 'smaller than basketball' sized  things. Not sure how to manage that yet. Want to avoid having to use cubic volume but maybe I'll end up doing that, hm. Or just arbitrary per item, but that's tricky. If a vase can hold 20 'marble sized' things but 2 palm-sized things, what if there's one palm-sized and 10 marbles? Hm.
    # Maybe a default of like, 3 items per container and figure it out later.

perhaps a
    self.special = set()
for items with some other characteristic. Not sure about that though. For things like the moss that dries out after three days. Though maybe that's managed by the plotInstance? 'moss_drying' could be a plot event. It's not really 'plot events' specifically, but 'events' in general. Maybe eventInstances is better phrasing. Mm.

so maybe self.event_items, as a holding-pen for items that are involved in events. So in the moss example, moss is in self.standard, and temporarily in self.event_items also.
self.event_items[moss_obj][moss_drying]
Then once the event is concluded, it's removed with whatever state is set by the event.

--------
3.03pm

[[  get scroll  ]]

scroll is now in your inventory.

(A.N.: key is in the scroll, currently you don't have to be told that to be able to pick it up.)

[[  take old gold key  ]]

old gold key is now in your inventory.


[[  inventory  ]]

severed tentacle
paperclip x2
mail order catalogue
car keys
anxiety meds
regional map
fish food
batteries
scroll
old gold key


[[  put old gold key in scroll  ]]

Put varies depending on the format.
Format list: ('verb', 'noun', 'direction', 'noun')
Input dict: {0: {'verb': {'instance': <verbInstance put (0c4b08f7-ad83-4af2-9327-ba5b007d2d1e)>, 'str_name': 'put'}}, 1: {'noun': {'instance': <ItemInstance old gold key (5afd0d8f-1f3f-4b30-ae60-4bf7c395d99e)>, 'str_name': 'old gold key'}}, 2: {'direction': {'instance': None, 'str_name': 'in'}}, 3: {'noun': {'instance': <ItemInstance scroll (0f95d375-0203-4665-bcd8-913237fa3d66)>, 'str_name': 'scroll'}}}
list(input_dict[2].values())[0]: in
direction in kind: {'instance': None, 'str_name': 'in'}
You put old gold key in scroll


[[  inventory  ]]

severed tentacle
paperclip x2
mail order catalogue
car keys
anxiety meds
regional map
fish food
batteries
scroll*


Oh shit, it works.


## NOTE:
go east graveyard
No viable sequences found for go east graveyard.
verb cardinal location

This should work. Add the format.

Also

east graveyard
No verb_instance or meta_instance found in get_sequences_from_tokens. Returning None.
TOKENS: [Token(idx=0, text='east', kind={'cardinal'}, canonical='east'), Token(idx=1, text='graveyard', kind={'location'}, canonical='graveyard')]
No viable sequences found for east graveyard.
cardinal location


11.00pm

Well shit.

take watch
No viable sequences found for take watch.
verb verb

Apparently at some point I broke the whole 'watch the watch with a watch' thing that I had previously. Shiiiit.

11:20pm okay, re-fixed it again. At one point I'd told it basically to only check sequences if there's only one verb match, but the potential verbs of each 'watch' meant it failed immediately despite having viable sequence options. So it's back to 'for v in verb_instances' and it works again.

11.51am 15/1/26
Sick as hell today.

Have added car_loc as well as loc_car, so now 'east graveyard' and 'graveyard east' both work.

Also added 'go graveyard east/go east graveyard', as neither of those worked either.

3.46pm
Got distracted with the idea of dynamic location descriptions. Maybe have an idea, it's going to be a bit of a pain (breaking scene descriptions down into parts that can be removed at will depending on item presence or lack thereof) but it'll be nice to now have it say 'there's a glass jar' when the glass jar's been removed. And I do want item-inclusive descriptions, because then I can drop the 'items in this area' line. I might add a 'look for items' func so you can explicitly look for actively interactable items, but I don't like it by default, it's too hand-holdy, 'I'll play for you' vibes.

Also this could be reused elsewhere if it's flexible enough. Description of the shrine might change if the scroll's removed, not just the location descrip. Will have to think on that one. Would be far better to do that, just have to figure out how. First thought is an indicator in the string; if the graveuard description is currently
"You see a variety of headstones, most quite worn and decorated by clumps of moss."
then maybe it's
"CCCYou see a variety of headstones, most quite worn and decorated by clumps of moss.EEE" to indicate the text is changeable, and then it is adapted internally to

"CCCYou see a variety of headstones, most quite wornAAA and decorated by clumps of mossEEE.EEE"

to mark a part that can be removed.
(That's a location description, but there's no actual 'shrine' object to use yet for an example. Scenery doesn't exist yet.)

Also I've spent a couple of days working on the test class. I do think it's going to work. Need to rewrite so much but it's worth it. So I tell myself.

4.06pm Added failure prints to the functions that don't have all-inclusive if/else statements, so if they come to the end of the function unresolved it prints the dict and fn name. Should make it easier to track down random failures that I'm not expecting.


11.45am 16/1/26

{'breakable': False,
 'can_examine': False,
 'current_loc': None,
 'description': "It's a stone ground",
 'exceptions': {'starting_location': 'west Graveyard'},
 'id': 'c6a7ba6f-1e29-42a1-9115-f2daf097dab6',
 'is_horizontal_surface': False,
 'is_vertical_surface': False,
 'item_type': {'static', 'all_items'},
 'name': 'stone ground',
 'starting_location': 'east Graveyard'}

 Hm. Just noticed it's added 'exceptions: the exception' instead up updating the actual exceptioned field.


Hm.

ITEM: stone ground
{'description': "It's a stone ground",
 'exceptions': {},
 'id': '428f46ca-eb9f-4860-a8ac-7205838754eb',
 'item_type': {'static', 'all_items'},
 'name': 'stone ground',
 'starting_location': 'north Graveyard'}
ITEM: headstones
ITEM: box
ITEM: stone ground
{'description': "It's a stone ground",
 'id': '62600240-c50d-4223-8b52-d4a54e2ad831',
 'item_type': {'static', 'all_items'},
 'name': 'stone ground'}
ITEM: stone ground
{'breakable': False,
 'can_examine': False,
 'current_loc': None,
 'description': "It's a stone ground",
 'exceptions': {},
 'id': 'bb718a6c-3587-467e-9e37-e56accc9fc2b',
 'is_horizontal_surface': False,
 'is_vertical_surface': False,
 'item_type': {'static', 'all_items'},
 'name': 'stone ground',
 'starting_location': 'west Graveyard'}

 So I can fix that, but, all the earlier ones are missing the item_type attributes.


from midway, before sending it on to testReg.init_items(loc_items, descriptions)
loc_items[item]: {'id': 'ad3c364b-182d-4c7e-a925-0bb51b0b7e37', 'name': 'stone ground', 'item_type': {'all_items', 'static'}, 'starting_location': 'north Graveyard', 'current_loc': None, 'is_horizontal_surface': False, 'is_vertical_surface': False, 'can_examine': False, 'breakable': False, 'description': "It's a stone ground", 'exceptions': {}}


[NOT IN by_name: loc_items[item]: {'item_type': ['static'], 'exceptions': {'starting_location': 'east Graveyard'}}
FLAG IN GET(EXCEPTIONS) not dict: starting_location
east Graveyard
item: starting_location: v: east Graveyard
item in self already: starting_location, v: east Graveyard
Found in by_name: loc_items[item]: {'id': '3e32c20d-014c-469f-83a8-2fe82802ab5e', 'name': 'stone ground', 'item_type': {'static', 'all_items'}, 'is_horizontal_surface': False, 'is_vertical_surface': False, 'can_examine': False, 'breakable': False, 'starting_location': 'east Graveyard', 'current_loc': None, 'description': "It's a stone ground", 'exceptions': {'starting_location': 'west Graveyard'}}

1.24pm

--------
--------
--------

Deleted a whole swath of logs over the previous couple of hours, I just removed the part where it tried to get the attributes from existing instances entirely. I'm not exactly sure why it broke, but it did, and this fixes it. I'll look into it again later with fresh eyes.


5.55pm

{'id': '9901ea49-34b1-439b-b8a4-178ae5ec676f',
 'name': 'gold key',
 'description': "It's a gold key",
 'current_loc': 'graveyard north',
 'contained_in': None,
 'item_size': 0,
 'item_type': {'all_items', 'key', 'can_pick_up'},
 'starting_location': 'graveyard north',
 'started_contained_in': None}

 Working on dynamic simple item generation. Not working properly yet, it's not applying all the tags like it should, but getting there.

 At item-gen, the new key item is:

 SELF: {'id': '9901ea49-34b1-439b-b8a4-178ae5ec676f', 'name': 'gold key', 'item_type': {'all_items', 'key', 'can_pick_up'}, 'starting_location': 'graveyard north', 'current_loc': 'graveyard north', 'is_key': True, 'can_pick_up': True, 'item_size': 0, 'started_contained_in': None, 'contained_in': None}

So the data is added, but for some reason not preserved. Will have to check my dict-formatting func, it's likely an issue there.
Tis cool. though. It stops, asks for item_type(s), then generates the new item accordingly.


9.46pm

And now it checks if you like it or not, then adds it to the JSON if so.

The following item(s) have been confirmed for future use:
Text: earring, type: <class 'str'>
Text: {'id': 'a13fb652-6ba8-46a6-acec-c8ec8b1d8bde', 'name': 'earring', 'item_type': {'all_items', 'can_pick_up'}, 'starting_location': None, 'current_loc': None, 'can_pick_up': True, 'item_size': 0, 'started_contained_in': <ItemInstance
box (ea05874a-e72d-485a-bb60-ec398ca091d7)>, 'contained_in': <ItemInstance box (ea05874a-e72d-485a-bb60-ec398ca091d7)>, 'description': 'a single silver earring with a small blue stone dangling from a short chain'}, type: <class 'dict'>
Popped dict: {'name': 'earring', 'item_type': "{'all_items', 'can_pick_up'}", 'can_pick_up': True, 'item_size': 0, 'description': 'a single silver earring with a small blue stone dangling from a short chain'}
KEY: earring

It'll prompt for you to add a description to any location-based item that doesn't already have one, and the once it's saved it'll check the JSON for that description and use it again in the future.

Later I'll add the regular items to the same file and compile them somehow so it's just one main file, but for now while I'm playing this is good.


1.47pm 17/1/26
Have added alt_name support for items, so if someone times 'tv' or 'television' it'll find item.name "TV set".

Note: Need to add an arg in assign_colour to let it use the instance to get the colour data, but still use the input str for printing. Won't be hard, just have to remember to. Really need to start using that todo list again.

Also, have neatened up the dynamic description printing quite a bit, very pleased with it now. Still only running in isolation, but for the moment I'm going to hook it up to the existing item class and let it go from there.

Ooooor I hook it up to the new item class, and give that the item defs dict. Should probably do that one tbh. Will just copy over the parts that definitely work from itemRegistry.
Oh god I'm going to have to rename it again.  Neh this time I'm just going to overwrite it with the new version once it's slightly functional and go from there.

4:33pm

ITEM ENTRY: {'exceptions': {'flammable': None, 'item_size': 'small_flat_things'}, 'name': 'a 5 pound note', 'description': 'A small amount of legal tender. Could be useful if you find a shop.', 'dupe': None, 'loot_type': 'medium_loot', 'item_type': {'fragile', 'can_pick_up'}}
inst description: A small amount of legal tender. Could be useful if you find a shop.
ITEM ENTRY: {'exceptions': {'can_read': None, 'flammable': None, 'item_size': 'small_flat_things', 'print_on_investigate': True}, 'name': 'a scrap of paper with a number written on it', 'description': 'A small scrap of torn, off-white paper with a hand-scrawled
phone number written on it.', 'loot_type': 'medium_loot', 'item_type': {'fragile', 'books_paper', 'can_pick_up'}}
inst description: A small scrap of torn, off-white paper with a hand-scrawled phone number written on it.
ITEM ENTRY: {'exceptions': {'is_locked': None, 'is_charged': None, 'item_size': 'palm_sized'}, 'name': 'a mobile phone', 'description': "A mobile phone. You don't think it's yours. Doesn't seem to have a charge.", 'fragile': None, 'can_lock': None, 'key': 'mobile_passcode', 'loot_type': 'great_loot', 'item_type': {'container', 'can_pick_up', 'electronics'}}
inst description: A mobile phone. You don't think it's yours. Doesn't seem to have a charge.

{'id': '736ca1ba-d140-4ea9-9a23-0d925269a81d', 'name': 'mobile phone', 'description': "A mobile phone. You don't think it's yours. Doesn't seem to have a charge.", 'item_type': {'container', 'can_pick_up', 'electronics', 'all_items'}, 'starting_location': None,
'current_loc': None, 'alt_names': {}, 'is_hidden': False, 'is_open': False, 'can_be_opened': True, 'can_be_closed': True, 'can_be_locked': True, 'is_locked': None, 'requires_key': False, 'starting_children': None, 'container_limits': None, 'name_no_children': None, 'description_no_children': None, 'can_pick_up': True, 'item_size': 'palm_sized', 'started_contained_in': None, 'contained_in': None, 'can_be_charged': True, 'is_charged': None, 'takes_batteries': False, 'has_batteries': False, 'fragile': None, 'can_lock': None, 'key': 'mobile_passcode', 'loot_type': 'great_loot'}


Result: Messy and it repeats more than I think it out to, but it works. Successfully takes me existing item_defs and converts them into this new format.


5.07pm

Hm.
{'id': '3ace1f57-33a4-48b7-9c3c-53168b9fcf77', 'name': 'paper scrap with number', 'description': 'A small scrap of torn, off-white paper with a hand-scrawled phone number written on it.', 'item_type': {'all_items', 'books_paper', 'fragile', 'can_pick_up'}, 'starting_location': None, 'current_loc': None, 'alt_names': {}, 'is_hidden': False, 'can_pick_up': True, 'item_size': 'small_flat_things', 'started_contained_in': None, 'contained_in': None, 'broken_name': None, 'flammable': True, 'can_break': True, 'print_on_investigate': True, 'can_read': True, 'loot_type': 'medium_loot'}

This paper scrap is accurately marked as flammable.

Okay so this tells me it's just taking the original starting location from the inst in by_name and copying that. Doesn't explain why removing the 'exceptions' gets rid of all the other attr but w/e. Will figure it out.


5.14pm, 18/1/16
Have been working on it. Also added a 'add the new items to the real dict' function, and cleaned up a little, separated the dict-editing from the generation. Can now run edit_dict on existing dicts, specify fields to edit, etc.

I had descriptions etc written for headstones, grave etc. I have no idea where those descriptions are gone, I can't find record of them.

9.49pm

Note: For actual game - graveyard starts locked, need to find the key to move on.
Related note: Need to check against events to see if things can be acted on. eg can't move from graveyard until an event is met. So not just that you need to key for the padlock, but that you can't fast-travel away until travel is unrestricted.

Descriptions for items:
When needed:
default == based on the default state (eg padlock == child of gate)
if_no_parent == based on missing expected parent (parent-specific, not just 'is child')
if_no_child == based on missing expected child (child-specific as above)


3.55pm
Okay so it's not working properly. I changed a few things today and one of them's gone wrong -


GENERATED: <TestInstances mummified mouse (1dce50f0-c994-4e31-bbd4-d820e9be5925)>

target object after create_item_by_name from list: <TestInstances mummified mouse (1dce50f0-c994-4e31-bbd4-d820e9be5925)>
All children found/created as instances: [<TestInstances mummified mouse (1dce50f0-c994-4e31-bbd4-d820e9be5925)>]
generated_entry:
 {'grandfather clock': {'name': 'grandfather clock', 'nicename': 'a grandfather clock', 'description': "An antique-looking grandfather clock, silent. Maybe it's in need of a wind. ", 'item_type': "{'container', 'all_items', 'static'}", 'alt_names': {}, 'is_hidden': False, 'can_examine': False, 'breakable': False, 'is_open': False, 'can_be_opened': True, 'can_be_closed': True, 'can_be_locked': True, 'is_locked': True, 'requires_key': True, 'starting_children': ['mummified
mouse'], 'container_limits': 4, 'name_no_children': None, 'description_no_children': None}, 'mummified mouse': {'name': 'mummified mouse', 'nicename': 'a mummified mouse', 'description': "The tiny, dried body of a long-dead mouse, curled
up. You could think it was sleeping if it wasn't so frail and stiff.", 'item_type': "{'fragile', 'can_pick_up', 'all_items', 'food_drink'}", 'broken_name': None, 'flammable': True, 'can_break': True, 'can_pick_up': True, 'item_size': 0, 'alt_names': {}, 'is_hidden': False, 'can_consume': True, 'can_spoil': True, 'is_safe': True, 'effect': None}}, name: True


Failed to generate instance from {'grandfather clock': {'name': 'grandfather clock', 'nicename': 'a grandfather clock', 'description': "An antique-looking grandfather clock, silent. Maybe it's in need of a wind. ", 'item_type': "{'container', 'all_items', 'static'}", 'alt_names': {}, 'is_hidden': False, 'can_examine': False, 'breakable': False, 'is_open': False, 'can_be_opened': True, 'can_be_closed': True, 'can_be_locked': True, 'is_locked': True, 'requires_key': True, 'starting_children': ['mummified mouse'], 'container_limits': 4, 'name_no_children': None, 'description_no_children': None}, 'mummified mouse': {'name': 'mummified mouse', 'nicename': 'a mummified mouse', 'description': "The tiny, dried body of a long-dead mouse, curled up. You could think it was sleeping if it wasn't so frail and stiff.", 'item_type': "{'fragile', 'can_pick_up', 'all_items', 'food_drink'}", 'broken_name': None, 'flammable': True, 'can_break': True, 'can_pick_up': True, 'item_size': 0, 'alt_names': {}, 'is_hidden': False, 'can_consume': True, 'can_spoil': True, 'is_safe': True, 'effect': None}}
No generated entry for True; continuing.

Nothing found for item name `True` in def item_by_name.
Do you want to create a new instance with this name?
please enter -type_default key(s)- to create a new instance of that type now.
Options: ['standard', 'static', 'all_items', 'container', 'key', 'can_pick_up', 'event', 'trigger', 'flooring', 'wall', 'food_drink', 'fragile', 'electronics', 'books_paper']
Entering nothing will skip this process.



It's adding the dict entry of mummified mouse, not the child obj. Hm.
Just prior to this I was having this issue:

  Item `mummified mouse` does not have a description, do you want to write one?. Enter it here, or hit enter to cancel.
The tiny, dried body of a long-dead mouse, curled up. You could think it was sleeping if it wasn't so frail and stiff.
Is this correct? 'y' to accept this description, 'n' to try again or anything else to cancel.
y
Inst after self.init_items(): <TestInstances mummified mouse (2f67f6ff-9556-4a87-a55a-5d4a76c2ce9c)>, type: <class '__main__.testInstances'>
{'id': '2f67f6ff-9556-4a87-a55a-5d4a76c2ce9c', 'name': 'mummified mouse', 'nicename': 'a mummified mouse', 'description': "The tiny, dried body of a long-dead mouse, curled up. You could think it was sleeping if it wasn't so frail and stiff.", 'item_type': {'fragile', 'can_pick_up', 'all_items', 'food_drink'}, 'starting_location': 'graveyard north', 'current_loc': 'graveyard north', 'broken_name': None, 'flammable': False, 'can_break': True, 'can_pick_up': True, 'item_size': 0, 'started_contained_in': None, 'contained_in': None, 'alt_names': {}, 'is_hidden': False, 'can_consume': True, 'can_spoil': True, 'is_safe': True, 'effect': None}
Add to gen_items: <TestInstances mummified mouse (2f67f6ff-9556-4a87-a55a-5d4a76c2ce9c)>
Text: mummified mouse, type: <class 'str'>
Text: {'id': '2f67f6ff-9556-4a87-a55a-5d4a76c2ce9c', 'name': 'mummified mouse', 'nicename': 'a mummified mouse', 'description': "The tiny, dried body of a long-dead mouse, curled up. You could think it was sleeping if it wasn't so frail and stiff.", 'item_type': {'fragile', 'can_pick_up', 'all_items', 'food_drink'}, 'starting_location': 'graveyard north', 'current_loc': 'graveyard north', 'broken_name': None, 'flammable': False, 'can_break': True, 'can_pick_up': True, 'item_size': 0, 'started_contained_in': None, 'contained_in': None, 'alt_names': {}, 'is_hidden': False, 'can_consume': True, 'can_spoil': True, 'is_safe': True, 'effect': None}, type: <class 'dict'>
Exception: 'testInstances' object has no attribute 'id'

and so in trying to fix that may have broken this a little.


Okay tracing it back.

So it started off generating correctly:

`grandfather clock` found in generated_items.
GEN ITEMS grandfather clock: {'name': 'grandfather clock', 'nicename': 'a grandfather clock', 'description': "An antique-looking grandfather clock, silent. Maybe it's in need of a wind. ", 'item_type': "{'container', 'all_items', 'static'}", 'alt_names': {}, 'is_hidden': False, 'can_examine': False, 'breakable': False, 'is_open': False, 'can_be_opened': True, 'can_be_closed': True, 'can_be_locked': True, 'is_locked': True, 'requires_key': True, 'starting_children': ['mummified mouse'], 'container_limits': 4, 'name_no_children': None, 'description_no_children': None}
About to go to init_single:

INST GENERATED: {'id': 'ec3e6339-9c23-42ef-bb2e-a85efc12e8c7', 'name': 'grandfather clock', 'nicename': 'a grandfather clock', 'description': "An antique-looking grandfather clock, silent. Maybe it's in need of a wind. ", 'item_type': {'static', 'container', 'all_items'}, 'starting_location': 'east OtherPlace', 'current_loc': 'east OtherPlace', 'alt_names': {}, 'is_hidden': False, 'can_examine': False, 'breakable': False, 'is_open': False, 'can_be_opened': True, 'can_be_closed': True, 'can_be_locked': True, 'is_locked': True, 'requires_key': True, 'starting_children': ['mummified mouse'], 'container_limits': 4, 'name_no_children': None, 'description_no_children': None}

Then at this point when it gets to clean_children:
Item.starting_children: None
generated_entry:
 {'grandfather clock': {'name': 'grandfather clock', 'nicename': 'a grandfather clock', 'description': "An antique-looking grandfather clock, silent. Maybe it's in need of a wind. ", 'item_type': "{'container', 'all_items', 'static'}", 'alt_names': {}, 'is_hidden': False, 'can_examine': False, 'breakable': False, 'is_open': False, 'can_be_opened': True, 'can_be_closed': True, 'can_be_locked': True, 'is_locked': True, 'requires_key': True, 'starting_children': ['mummified
mouse'], 'container_limits': 4, 'name_no_children': None, 'description_no_children': None}, 'mummified mouse': {'name': 'mummified mouse', 'nicename': 'a mummified mouse', 'description': "The tiny, dried body of a long-dead mouse, curled
up. You could think it was sleeping if it wasn't so frail and stiff.", 'item_type': "{'fragile', 'can_pick_up', 'all_items', 'food_drink'}", 'broken_name': None, 'flammable': True, 'can_break': True, 'can_pick_up': True, 'item_size': 0, 'alt_names': {}, 'is_hidden': False, 'can_consume': True, 'can_spoil': True, 'is_safe': True, 'effect': None}}, name: False


5.30pm
okay next:
Adding `ornate silver key` to generated_items.json
Add to gen_items: <TestInstances ornate silver key (07a61206-d9e4-4f52-ba1a-15711a867137)>
Text: ornate silver key, type: <class 'str'>
Text: {'id': '07a61206-d9e4-4f52-ba1a-15711a867137', 'name': 'ornate silver key', 'nicename': 'a ornate silver key', 'description': 'an ornate silver key with `VI` pressed into the head.', 'item_type': {'key', 'all_items', 'can_pick_up'}, 'starting_location': 'graveyard north', 'current_loc': 'graveyard north', 'is_key': True, 'alt_names': {}, 'is_hidden': False, 'can_pick_up': True, 'item_size': 0, 'started_contained_in': None, 'contained_in': None}, type: <class 'dict'>Exception: 'testInstances' object has no attribute 'id'

this issue only happens when adding a new entry to generated_items.json.
the item gets added correctly, but then this error.


Data written to dynamic_data/generated_items.json.
#  ^-- added this print at the very end of add_to_gen_items() so it's happening after that.
Exception: 'testInstances' object has no attribute 'id



New side issue:

key
NEW_ITEM_FROM_STR -------------==============------------
new_item_from_str:
 {'ornate silver key': {'item_type': {'e', 'k', 'y'}, 'exceptions': {'starting_location': 'graveyard north'}}}, ornate silver key

If only one defautl type is entered, it thinks its a set again and breaks the string. Goddamn I hate this. Why can't just stay a fucking set?

Okay, fixed now. I just manually create the set and then .add the inst to it. Stupid workaround but needs must. Can't figure out how to make it be a set containing one word otherwise. Too tired. Bleh.


7.03am
Starting on working on converting the itemRegistry to the new system. Am basically going to retrofit it - the verbRegistry has very specific expectations, so I need to make sure I don't break it too hard or I'll be fixing it all week.

Thing one:
Removing the 'self.flags' reference, because the new format doesn't have that at all.

Also, the itemReg doesn't have the new item generation. Might rejig the testclass to make it a generated-item setup, sending the completed dict to itemRegistry instead of generating the item instance. Or make an item instance that is added immediately to itemReg in the format it expects, either way.

But for now - making the exact calls match as closely as I can (eg instead of if "can_pick_up" in self.flags:", apply all attr to self then check if hasattr(self, can_pick_up)).


# NOTE: "can_open" from old version. New version uses "can_be_opened". Need to update either the item defs or the verbReg/parser.
# "can_lock" is now "can_be_locked".

old self.needs_key_to_lock == new "requires_key"


9.00am

long_desc_dict == item_desc

10.58am
Need to update this:
local_items = itemRegistry.registry.get_item_by_location(f"{location} {cardinal}")

Currently it fails to check local_items, need to update locations in itemRegistry for it to work. Just noting it here so I hopefully don't forget. The basic scene descriptions are working again.

1.59pm
## print(f"items_at_cardinal: {items_at_cardinal}, type: {type(items_at_cardinal)}")
Still no items. Items aren't being added to self.by_location (because I haven't set it up yet), that's the next major thing.

The input parsing is working though. So that's very very nice.

3.55pm

items_at_cardinal: {<ItemInstance padlock (13d4420a-7609-4b36-9192-e2bf56d26bd0)>, <ItemInstance padlock (3a3f69e0-495d-45da-b208-0cb67e749c68)>}, type: <class 'set'>
self.by_name.get(definition_key): [<ItemInstance gate (f5d36449-aa7a-4b72-9a63-dfe7be1e3ae5)>]
itemRegistry.registry.instances_by_name(item)[0] : <ItemInstance gate (f5d36449-aa7a-4b72-9a63-dfe7be1e3ae5)>
self.by_name.get(definition_key): [<ItemInstance gate (f5d36449-aa7a-4b72-9a63-dfe7be1e3ae5)>]
"[[]]" in long_dict[item] but not local: a heavy wrought-iron [[]] - imposing but run-down
self.by_name.get(definition_key): [<ItemInstance gate (f5d36449-aa7a-4b72-9a63-dfe7be1e3ae5)>]
NOT LOCAL TEST: a heavy wrought-iron gate - imposing but run-down
self.by_name.get(definition_key): [<ItemInstance padlock (3a3f69e0-495d-45da-b208-0cb67e749c68)>]
Item in item registry: padlock
Loc name in place_by_name: graveyard
items_at_cardinal: {<ItemInstance padlock (13d4420a-7609-4b36-9192-e2bf56d26bd0)>, <ItemInstance padlock (3a3f69e0-495d-45da-b208-0cb67e749c68)>}, type: <class 'set'>
self.by_name.get(definition_key): [<ItemInstance padlock (3a3f69e0-495d-45da-b208-0cb67e749c68)>]
itemRegistry.registry.instances_by_name(item)[0] : <ItemInstance padlock (3a3f69e0-495d-45da-b208-0cb67e749c68)>
self.by_name.get(definition_key): [<ItemInstance padlock (3a3f69e0-495d-45da-b208-0cb67e749c68)>]
self.by_name.get(definition_key): [<ItemInstance padlock (3a3f69e0-495d-45da-b208-0cb67e749c68)>]
"[[]]" in long_dict[item] and local: an old dark-metal [[]] on a chain holding the gate closed
LOCAL ITEMS TEST: an old dark-metal padlock on a chain holding the gate closed
self.by_name.get(definition_key): [<ItemInstance moss (aefeb5d8-3d0d-4bb2-a916-7edcb7f1144a)>]
Item in item registry: moss
Loc name in place_by_name: graveyard
items_at_cardinal: None, type: <class 'NoneType'>
self.by_name.get(definition_key): [<ItemInstance moss (aefeb5d8-3d0d-4bb2-a916-7edcb7f1144a)>]
itemRegistry.registry.instances_by_name(item)[0] : <ItemInstance moss (aefeb5d8-3d0d-4bb2-a916-7edcb7f1144a)>
"[[]]" in long_dict[item] but not local: clumps of [[]]
self.by_name.get(definition_key): [<ItemInstance moss (aefeb5d8-3d0d-4bb2-a916-7edcb7f1144a)>]
NOT LOCAL TEST: clumps of moss
self.by_name.get(definition_key): [<ItemInstance glass jar (ad4bb5a4-031e-4782-91bf-69ae48f7bb93)>]
Item in item registry: glass jar

So this is /messy/.

Trying to move the testclass functions over to itemReg


5:32pm
Have got rid of some of those issues. Now just having to fix container parenting again.

INVENTORY LIST IN RUN_CHECK: [<ItemInstance severed tentacle (31b3ea7f-930c-48f2-96ac-98c6b95d0c09)>, <ItemInstance paperclip (fdd1b6cf-b49e-4113-ab90-d80c7e955e03)>, <ItemInstance gardening mag (30306431-b476-437d-8c4c-ad68c84a1b18)>, <ItemInstance paperclip (564bf72c-41ab-4262-8e05-f199152ece89)>, <ItemInstance glass jar (d75e4652-4cc4-4d57-9b20-223d0e1517af)>]
items_at_cardinal: {<ItemInstance moss (3c27dea9-f1af-46ef-9df3-892afc286c77)>, <ItemInstance dried flowers (c0414aef-7daa-4c7e-a3ac-19e6f73cefaf)>}, type: <class 'set'>
Hasattr contained_in: <ItemInstance glass jar (d75e4652-4cc4-4d57-9b20-223d0e1517af)>
You open the glass jar
Cannot process {0: {'verb': {'instance': <verbInstance open (88b277b6-2530-4cf8-9423-c0249b46a1a4)>, 'str_name': 'open'}}, 1: {'noun': {'instance': <ItemInstance glass jar (d75e4652-4cc4-4d57-9b20-223d0e1517af)>, 'str_name': 'glass jar'}}} in def open_close() End of function, unresolved.

[[  take dried flowers from glass jar  ]]

items_at_cardinal: {<ItemInstance moss (3c27dea9-f1af-46ef-9df3-892afc286c77)>, <ItemInstance dried flowers (c0414aef-7daa-4c7e-a3ac-19e6f73cefaf)>}, type: <class 'set'>
Hasattr contained_in: <ItemInstance dried flowers (c0414aef-7daa-4c7e-a3ac-19e6f73cefaf)>
REASON: 0 / accessible
The dried flowers doesn't seem to be in glass jar.


5.55pm
create_item_by_name: dried flowers
Exception: 'itemRegistry' object has no attribute 'create_item_by_name'

Ah, finally saw it. That's why it keeps failing.


6.29 Fiiiiiinally. Got the flowers out of the jar. Added a straight 'children' set for containers to use, separate from starting_children.


8.37
look at jar
INVENTORY LIST IN RUN_CHECK: [<ItemInstance severed tentacle (b65bbc12-a5c5-47b7-93ae-4d11a8a87d6b)>, <ItemInstance paperclip (8fa97de2-798a-4ae9-89d3-4dccdbc8f4c2)>, <ItemInstance mail order catalogue (3f4f9448-80f1-4978-8f20-c9aba14c8927)>, <ItemInstance paperclip (ac6f78c0-11ea-4176-9415-2b62f3c111b1)>, <ItemInstance glass jar (54c3855c-c8e2-4e6a-a272-26f38500958f)>]
items_at_cardinal: {<ItemInstance moss (ad23872e-6971-455c-9e27-b1304517689a)>}, type: <class 'set'>
Look at item MEANING: in inventory
You look at the glass jar.
A glass jar, now empty aside from some bits of debris.

Hm. So - apparently it's not generating the flowers early enough. I'm not sure why.

If I 'take flowers from jar' it invents the flowers, but they need to be present as soon as the parent is activated.
Thought I'd done that but clearly not.

6.51pm
Okay, fixed it. Now the description is accurate, and the parenting holds up. I probably repeat the parenting checks too often now, but it was being tricksy so I'll just skim it off later.

At least for the moment, have switched the parenting check from

children = self.instances_by_container(inst)

to

for child in inst.starting_children:
    if child in inst.children:
        print(f"Child {child.name} is present in parent {inst.name}.")
    else:
        all_children = False

so it checks not just 'is it empty' but 'are its starting children gone'.
Currently is still binary, but it'll do for now. I'll do a version like I did with the dynamic scene descriptions later.


7.32 wrote myself a little function for adding locations on the fly. No descriptions etc, but I can name a location then choose to make it. It's cool.

Also, just saw another issue with why the parent children aren't working:

[init_single] ITEM ENTRY: {'name': 'some dried flowers', 'description': 'a bunch of old flowers, brittle and pale; certainly not as vibrant as you imagine they once were.', 'item_type': "{'can_pick_up', 'fragile', 'all_items'}", 'alt_names': {}, 'is_hidden': False, 'can_pick_up': True, 'item_size': 'smaller_than_apple', 'broken_name': None, 'flammable': True, 'can_break': True, 'can_remove_from': 'glass jar'}
Create_item_by_name for starting_children: <ItemInstance glass jar (41061f91-f985-485e-ab99-6a6be90db639)>
Exception: 'dict' object has no attribute 'starting_children'
:: Clean children:: parent: None
Create_item_by_name for starting_children: <ItemInstance glass jar (41061f91-f985-485e-ab99-6a6be90db639)>
Exception: 'dict' object has no attribute 'starting_children'

At some point it's sending a dict instead of an instance.


5.14am
Going to figure out the parenting I think.

Currrently, it is called:

If found from item_defs and parent inst created

if found in gen_items or made from str and parent, but like this:
        if registry.new_parents:
            registry.clean_children(inst)

and then again at the end of get_loc_items_dict.  So all three calls are there, one with the 'if registry.new_parents' limiter.


registry.new_parents is added to:
    after inst init, if container in item_types
    if hasattr(inst, starting_children) inside the item generation

registry.new_parents is removed from:
    if all children are found as instances (in two different ways within get_children)
    after initialising a new child instance


So I /think/, keeping if hasattr starting_children is the best version.
And we shouldn't be initialising a new child during the parenting check /unless/ it's in the preload local items stage.


Also need to make sure  this is fine:

# Create_item_by_name for starting_children: <ItemInstance glass jar (52e38d3a-bb85-4dee-91ed-6b53a6ff068f)>
# All children found or already parented to this parent.
# Exception: '52e38d3a-bb85-4dee-91ed-6b53a6ff068f'

I'm guessing that's trying to remove the parent.id from new_parents
registry.new_parents.remove(parent.id)


5.28am
Well just ran it again and so far that issue hasn't shown up.

But, at the end of item defs, the glass jar doesn't have child instances, only the str name. Going to add some prints to see if it adds them in the child check.

I don't mind if it adds them at the child check separately in this case because it's a location object, but really it should be internal; when you init an item, when it's done you check for children immediately. Not something located in the loc_items setup.


... huh.
                   print(f"\nINST GENERATED (item_dict by_cardinal): {vars(inst)}\n")
                    if hasattr(inst, "starting_children"):# and inst.starting_children != None:
                        print(f"Sending {item}/{inst} to clean_children from item_defs")
That print still isn't printing. So inst just doesn't get starting_children for some reason??

I mean, we do this:

        for attribute in attr:
            setattr(self, attribute, attr[attribute])

inside instance init.
And it has this:
starting_children': ['dried flowers'] in the vars after init.

###

Oh /now/ it does it.
Sending glass jar/<ItemInstance glass jar (e2a725c6-2160-4548-aabc-fd43810b0bc2)> to clean_children from item_defs

I just have to /print all the attributes as they come/, and suddenly it sends the glass jar to clean_children

I had issues with this earlier, where attr would sometimes fail to load defs but would work again if I printed it first.

And if I add the exit here:
        print(f"target child after create_item_by_name from list: {target_child}")
        exit()
suddenly it prints the child. Bleeeeeeh.

And proof that it ends up in parent.children like it should.

Okay so it's working both ways:

#  target_child.contained_in = parent: <ItemInstance glass jar (3333739c-e98f-46ea-98aa-1ec214cbdcac)>
#  parent.children: {<ItemInstance dried flowers (7609a4c7-8661-4eb1-8220-a2c14af212e1)>}


###
Wait, if a thing has a parent, we just make the parent automatically:

    if hasattr(item, "contained_in") and getattr(item, "contained_in") not in (False, None):
        print(f"Create_item_by_name for contained_in: {item}")
        target_obj = self.init_single(getattr(item, "contained_in"), self.item_defs.get(getattr(item, "contained_in")))

This is after loc_items is built.

Ah, it's never come up because I've only stated containers with contents, never actually manually set the 'contained_in' field. That probably works best...

So maybe the item_defs just always supplies parent>child, not the other way around.

5.56am Yeah commented the whole 'contained_in' section and it still works as expected. So I'll just cut that entirely.

I'm going to move child_parent to the registry, so I have a clean account of the relationships. It's another thing to update when something's removed/added to/from a container, but ... I thought of a benefit a second ago, now it's gone. Maybe I won't. hm.

6.03am
Okay so now I have this again:

Create_item_by_name for starting_children: <ItemInstance glass jar (8074cba6-bfbf-4a58-8054-e0f874bf562e)>
All children found or already parented to this parent.
Exception: '8074cba6-bfbf-4a58-8054-e0f874bf562e'
No settings in this version.

To note: glass jar was added to new_parents in this run:
# Added glass jar to new_parents: {'8074cba6-bfbf-4a58-8054-e0f874bf562e'}


So here it's sending the glass jar to get made again?
# Create_item_by_name for starting_children:

"print(f"\nINST GENERATED (item_dict by_cardinal): {vars(inst)}\n")" happens after init_single has run.

Ah, right - it's not using new_parent as a guide, it's checking all inst ids and seeing if they have starting_children.

Okay so the error is here:
        print("All children found or already parented to this parent.")
        print(f"REGISTRY.new_parents before remove attempt: {registry.new_parents}")
        registry.new_parents.remove(parent.id)
At that point, new_parents is empty. Need to track when it was emptied.


8.25am
Okay parenting is much, much neater now.

Next:
        "gate": "a heavy wrought-iron [[]] - imposing but run-down",
        "padlock": "an old dark-metal [[]] on a chain holding the gate closed"

I needa way to have these both exposed for descriptions, but to still have padlock be inside gate and now shown in location. It'll just be a flag, I just need to think more about it and how is best to do it. Not the generic 'hidden' flag, tht's a more specific thing. 'exposed_container', maybe? see_in_container? That might work. Allow descriptions and interactions but still maintain ownership. ownership_container, maybe, to differentiate from typical containers.

Current idea:

    "item_state": {"padlock": {"contained_in": "gate"}, "gate": "ownership_container"},

""can_remove_from": "glass jar"" is just silly. Need to remove that entirely.  If anything that should be 'contained_in', but it's easier just to list them in only one part. (this is from item_defs)

(Most of the container relationships will be defined in loc_datam not item_defs, so item_state above will be primary in most cases.)

((Great to realise that just now after I finally fixed parenting via item_defs))


11.10am

CHILD PARENT DICT: {<ItemInstance padlock (b005fbb2-24fc-4fb0-b0b2-2fcecd81b41d)>: <ItemInstance padlock (b005fbb2-24fc-4fb0-b0b2-2fcecd81b41d)>}

Hm. Not exactly right....
It's close though.


11.58 okay properly fixed now.

Now, I need to fix:

Look at item MEANING: accessible
You look at the gate.
Heavy wrought iron bars with little decoration, held closed with a padlock on a heavy chain.


I need it to show the padlock as an accessible item, but currently 'inside a closed container' is a hard no.

I added the 'ownership_container' flag for this; with this, it is a child for all internal things, but is displayed + interacted with mostly as a unique thing. So it should be



Hm.

# look around (east)
#
# You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
# The entrance gates are to the north. To the east sit a variety of headstones, to the south stands a mausoleum, and to the west is what looks like a work shed of some kind.
# You're facing east. You see a variety of headstones, most quite worn and decorated by clumps of moss. There's a glass jar being used as a vase in front of one of the headstones, with dried flowers left long ago.

# look around (north)
#
# You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
# The entrance gates are to the north. To the east sit a variety of headstones, to the south stands a mausoleum, and to the west is what looks like a work shed of some kind.
# You're facing north. You think you could leave through the large wrought-iron gates to the north. They're imposing but run-down; this graveyard doesn't get as much love as it could.


East gives the overview, but north just gives long_desc.

Oh, no. East just has a virtually identical east-overview to long_desc so it wasn't apparent it was the same. They're both long_desc.

How did I get it to print the overview again...? Maybe I didn't set that up and jsut saw it during test prints. That feels likely.


12.40pm
Having a weird issue where the long_desc with [[]] prints the colour correctly in test, but not in real.

"[[]]" in long_dict[item] and local: clumps of [[]]
---------- assign_colour(item_inst): moss
Loc name in place_by_name: graveyard
long_parts[0] + assign_colour(item_inst) + long_parts[1]:

a glass jar being used as a vase in front of one of the headstones, with some dried flowers left long ago
Here, 'glass jar' is cyan.


5.32pm needs resolution:
open gate
gate cannot be opened; this is odd. Potentially. Or maybe a totally normal thing.
Cannot process {0: {'verb': {'instance': <verbInstance open (43d759a0-fc05-45c9-b275-3c1ba0a7fa95)>, 'str_name': 'open'}}, 1: {'noun': {'instance': <ItemInstance gate (622fbf84-474e-433a-abe0-82a019bd53a6)>, 'str_name': 'gate'}}} in def simple_open_close() End of function, unresolved.

I was meant to be fixing things.

Also I need to implement "items" so I can start set designing.

also look at gate
You look at the gate.
Heavy wrought iron bars with little decoration, held closed with a padlock on a heavy chain.


open gate
gate cannot be opened; this is odd. Potentially. Or maybe a totally normal thing.
Cannot process {0: {'verb': {'instance': <verbInstance open (43d759a0-fc05-45c9-b275-3c1ba0a7fa95)>, 'str_name': 'open'}}, 1: {'noun': {'instance': <ItemInstance gate (622fbf84-474e-433a-abe0-82a019bd53a6)>, 'str_name': 'gate'}}} in def simple_open_close() End of function, unresolved.


look at padlock
Cannot look at padlock.

Also: TODO: "ownership_container": true
Need to set that up and fix the padlock + gate.

12.46pm 23/1/26

## The above issue with gate not opening:
     if hasattr(noun_inst, "is_open"): <- is not triggering

When what was written, is_open was true/false for any container.
Issue:
When items are generated, all the type_default tags are not added to the main dict, so is_open was not applied.


check_all_flags_present() in edit_items_defs is a workaround, those tags should be added when they're added to generated so will need to check why that's not happening but for now, all the items have all the tags they should.

look at gate
You look at the gate.
Child padlock is present in parent gate.
Heavy wrought iron bars with little decoration, held closed with a padlock on a heavy chain.


Hm. How to remove the padlock...

if the padlock is unlocked, it can be picked up or dropped, at which point the gate is unlocked? Kinda feels like the padlock shouldn't be its own item and should just be part of the description of the gate, but I like the idea of the padlock being its own thing. Maybe you can lock something else with it later if you didn't break it.

fundamentally:
    gate is locked. If padlock is removed, gate is unlocked.

Maybe the padlock should be the ownership_container. Then at least the padlock has the key, makes more sense. Currently the gate is locked, but doesn't have a key and doesn't need one...

Kinda makes sense for the padlock to the be ownership_container and have the gate 'in' it.


1.03pm
Okay. so I've added event_item to loc_data, so that items can be event keys/event-relevant items from there too. (item defs already had event keys.)
Adding padlock as 'event key' and gate as 'event item' - the padlock can affect the event, the gate is affected by it.

Now itemReg will be init before event_reg. So what I want to do is have itemReg made a dict of items with trigger/event attr, that it can send to eventReg, so eventReg doesn't need to go through the dict. (Then, later items that aren't in the original init can send their data directly from itemReg to eventReg in the same way, so it should work out for both.)

so currently,
self.event_items = {}
will just collect all the event items in item_reg. I don't really /need/ it maintained though, so I might x it out once it's been collected so it can just hold new items that are added without adding bulk. (That's just an easy way to collect the data without having to send it through each init func and send it back each time.)

    "event": null,
    "event_type": "item_triggered",
    "event_key": null
    "event_item": null
^ default event-related keys in item defs (whether from items main or loc_data.)

1.27pm
# {'gate': {'event_name': 'graveyard_gate_opens', 'event_key': None, 'event_item': True}, 'padlock': {'event_name': 'graveyard_gate_opens', 'event_key': True, 'event_item': None}}

# okay, working...


6.18pm
Note: This:
attr.get('description'): None
  Item `iron key` does not have a description, do you want to write one?. Enter it here, or hit enter to cancel.
is not picking up descriptions given in
    "south": {
      "item_desc": {},
      "short_desc": "stands a mausoleum",
      "long_desc": "There's a locked mausoleum here; graffiti that looks years-old and weeds sprouting at every crevice of the marble.",
      "items": {
        "iron key": {
          "description": "An iron key, handy for a quest or something, probably.",
          "is_hidden": false
        }
      }
loc_data, and it should be. that'll kinda be the primary place for them to be given descriptions for a lot of items now.

NOTE: If I name a key as a key for an item in loc_data, and also name that key as existing somewhere else, it add two keys.  Need to check if named children are found as items in other locations or smth.

For now, going to add "is_placed_elsewhere": true" flag, which will... hm.
Not create the child instance, I suppose? But then how do I align....
Okay. So, we check, if 'is_placed_elsewhere', if yes, then we find the location-specified other item_name, and set that location as this key-item with that as its starting location. And we add that key + loc/card to an exclusion dict, so when it's found, it doesn't make a second one (at least just one time, so it doesn't cancel all future items of that name). OR, if the key-item is already created, then we find the instance in that loc and assign it as key item to the lock.

Either way it needs to work either way because key or lock may be first/second, and I'm not interested in having to organise my item ref file to make it work.
Really I just need to make sure that the 'iron key' padlock is looking for is the same 'iron key' you can find in the mausoleum, so the interaction works. That's the goal here.


8.43pm
Oh, this is interesting -

attr.get('description'): None
  Item `iron key` does not have a description, do you want to write one?. Enter it here, or hit enter to cancel.
its a key for a quest
Is this correct? 'y' to accept this description, 'n' to try again or anything else to cancel.
y
Inst after self.init_items(): <TestInstances iron key (5ff33a32-15f7-49b1-b789-28abc44d7189)>, type: <class 'testclass.testInstances'>

Added a print and apparently it's still trying to add items to testinstances. Everything was meant to be diverted to itemReg now... oops.


10.40pm
Flagging.

Need to figure out why items from items aren't appearing in locations, but items from item_desc do. I don't /want/ all items to be in the description. I'd thought I corrected the omission but apparently not. Too tired now.

11.10am 24/1/26
finally got the items from items to be added to the locations, not just item_desc.

Next step: making them interactable. Currently they aren't, because they aren't in the nouns_list used by membrane and the verb registry. so I need to update the nouns list.

Nouns_list comes from

self.nouns_list = list(registry.item_defs.keys())

So I guess when I make an item I just have to make sure it's added to item_defs in itemReg. At least if it's in one of the categories that doesn't draw from that already.

Okay. So that's done now. Iron key now gets added to both item defs and plural words. But, 'pick up key' fails. I assume because there are multiple nouns in plural word dict with 'key', so it fails to pick one.

Okay, that's done. Now it gets local items, asks you to specify if there are multiple possible matches, or chooses the only local one if not. Need to add inventory items to this list, though. That depends on the verb tbh.

well have added the inventory. Still works the same way. It doesn't take the verb into account. Will adapt it later so it does, but for now it still only checks noun viability later.


12.21pm
wait what?

take key
There are multiple items here you could be talking about. Please enter which one you mean:
paperclip, gardening mag, severed tentacle, iron key


how are paperclip, gardening mag and tentacle == key???

12.25
Okay fixed it again.

Now I need to look into this mess and see why it fails:
#   take key
#   Verb inst name: <verbInstance take (30f6f874-4189-4eb7-a951-07de203ad839)>
#   noun inst actions: set()
#   Noun fails: <ItemInstance iron key (1fcb6740-f13c-4d61-9450-33830ef1f023)>, verbname: take
#   IS NOUN: <ItemInstance iron key (1fcb6740-f13c-4d61-9450-33830ef1f023)>
#   TAKE: 0 Meaning: accessible
#   Verb inst name: take
#   noun inst actions: set()
#   Noun fails: <ItemInstance iron key (1fcb6740-f13c-4d61-9450-33830ef1f023)>, verbname: take
#   You can't pick up the iron key.

I did make some changes to the take thing the other day so probably broke something there. Though tbh I did realise it was an absolute disaster at that point.

Hm. Okay so it's an attribute issue. Key isn't having the type keys assigned.

12.33pm
Ah, it was assigning the flags much later, outside of init. Trying again.

12.37pm
oh goddamn. Now it's not in local items anymore. wtf......

12.42pm
Okay so now it's there twice.

It's generating the key twice, immediately once after the other.


Item iron key not found in item_defs, generating from blank.


Options: ['standard', 'static', 'all_items', 'container', 'key', 'can_pick_up', 'event', 'trigger', 'flooring', 'wall', 'food_drink', 'fragile', 'electronics', 'books_paper', 'can_speak']
Please enter the default_types you want to assign to `iron key` (eg ' key, can_pick_up, fragile ' )
key can_pick_up
PARTS: {'key', 'can_pick_up'}, type: <class 'set'>
Parts len >1 : {'key', 'can_pick_up'}, type: <class 'set'>
[init_single] ITEM NAME: iron key
[init_single] ITEM ENTRY: {'description': 'An iron key, handy for a quest or something, probably.', 'is_key_to': 'padlock', 'is_hidden': False, 'item_type': {'key', 'can_pick_up'}, 'exceptions': {'starting_location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>}}


@@@@@@@@@@@@@@@@@ITEM iron key in INIT ITEMINSTANCE@@@@@@@@@@@@@@@


definition_key: iron key, attr: {'description': 'An iron key, handy for a quest or something, probably.', 'is_key_to': 'padlock', 'is_hidden': False, 'item_type': {'key', 'can_pick_up'}, 'exceptions': {'starting_location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>}}
after setting: self.item_type: {'key', 'can_pick_up'}
VARS before attributes are assigned: {'id': 'dafe8c35-1c64-4303-91fc-b67d6dabb9ff', 'description': 'An iron key, handy for a quest or something, probably.', 'is_key_to': 'padlock', 'is_hidden': False, 'item_type': {'key', 'can_pick_up'}, 'exceptions': {'starting_location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>}, 'name': 'iron key', 'nicename': None, 'colour': None, 'starting_location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>, 'verb_actions': set(), 'location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>, 'alt_names': None}
self.verb_actions: set()

end of new_item_from_str for <ItemInstance iron key (dafe8c35-1c64-4303-91fc-b67d6dabb9ff)>
{'id': 'dafe8c35-1c64-4303-91fc-b67d6dabb9ff', 'description': 'An iron key, handy for a quest or something, probably.', 'is_key_to': 'padlock', 'is_hidden': False, 'item_type': {'key', 'can_pick_up'}, 'exceptions': {'starting_location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>}, 'name': 'iron key', 'nicename': None, 'colour': None, 'starting_location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>, 'verb_actions': set(), 'location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>, 'alt_names': None, 'key': True}



<ItemInstance iron key (dafe8c35-1c64-4303-91fc-b67d6dabb9ff)>
<cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>



[init_single] ITEM NAME: iron key
[init_single] ITEM ENTRY: {'description': 'An iron key, handy for a quest or something, probably.', 'is_key_to': 'padlock', 'is_hidden': False, 'item_type': {'key', 'can_pick_up'}, 'exceptions': {'starting_location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>}}


@@@@@@@@@@@@@@@@@ITEM iron key in INIT ITEMINSTANCE@@@@@@@@@@@@@@@


definition_key: iron key, attr: {'description': 'An iron key, handy for a quest or something, probably.', 'is_key_to': 'padlock', 'is_hidden': False, 'item_type': {'key', 'can_pick_up'}, 'exceptions': {'starting_location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>}}
after setting: self.item_type: {'key', 'can_pick_up'}
VARS before attributes are assigned: {'id': 'f5b51530-6e6e-43cc-a6af-f1dd4e983327', 'description': 'An iron key, handy for a quest or something, probably.', 'is_key_to': 'padlock', 'is_hidden': False, 'item_type': {'key', 'can_pick_up'}, 'exceptions': {'starting_location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>}, 'name': 'iron key', 'nicename': None, 'colour': None, 'starting_location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>, 'verb_actions': set(), 'location': <cardinalInstance south graveyard (17fb3d61-144a-4065-bd47-cb06aa2cc14e)>, 'alt_names': None}
self.verb_actions: set()
No target_obj from item defs for <ItemInstance padlock (68781a21-87d8-495b-93a1-34b7e18b8bab)>, looking for iron key


Okay, so - in the first round of initial generations:

[('gate', 'item_defs'),
('gate', 'generate_child from item_defs'),
('padlock', 'item_defs'),
('moss', 'item_defs'),
('dried flowers', 'generate_child from item_defs'),
('glass jar', 'item_defs'),
('desiccated skeleton', 'item_defs'),
('iron key', 'item_from_str'),
(<ItemInstance padlock (12b6a0fd-56fb-4b84-95ff-0d593ccddefe)>, 'generate key from item_defs')]


So I need to formalise the parentage. Unsurprisingly.

How to determine if an item is a child or not.

If we have
location:
    north:
        item_desc:
            iron key
        items:
            irom key

surely, we assume they're the same thing. If there are 2x iron keys in items, then only the first. But if there's one match, we assume they're a match.

Now, if we have

location:
    north:
        item_desc:
            iron key
        items:
            irom key (is_key_to: padlock)

    south:
        items:
            padlock (requires key: iron_key)


Surely we match them by type.

I already make all top-level items first before looking for children. I think I just need to really clean up the child searching. There are far, far too many places I add new items from tbh.

8 different places I call init_single from.
5 places I call new_item_from_str.

Also that second key doesn't have the attributes properly added. It doesn't get its verb_actions set. No idea why not, that's meant to happen in init now.

Okay. So.
instead of making them immediately.

We go to each loc/cardinal. Make a dict of the items (top level only). We merge i for i in items_desc and items.

Make all those, with a dict of which ones note being keys_to and keys in general.

Then, children. Now the issue in at least one case is the gate. I think the whole parenting with the gate is broken, I'm going to use the event to maintain its relationship to the padlock, using adjusted parenting is just going to break more things. The event is a fine way of doing it.

1.09pm
Going to redo how parenting is done, and clean up item generation. Make dicts first, collect everything, then process top level. Then collect children, allocate parentage, create children when necessary.

Sounds so simple....



3.38 remember to do something with this later.
"event_ended_desc":

(items_main.json, now that gate isn't a container it can't have a no-children message so it needs to be here instead. When the event ends, change the item's description accordingly in itemReg.)

Am working on item_dict_gen, a separate script to get the data from items_main, generated + input_str type_defaults, and outputs a dict per item-name. then, itemreg can use this, just having a basic draw of all available information, and it can then apply that to whatever instances it needs to.

Also, need to be able to set keys to work for certain types of lock. So 'small gold key' can work for any lock in category x. would be useful going forward. Really need to refine the key/lock setup tbh.


5.29
Not sure where
#   Applying loc data to item: iron key, item data: ``{'name': 'iron key', 'item_type': "{'can_pick_up', 'key'}", 'can_pick_up': True, 'item_size': 0, 'is_key': True, 'description': 'An iron key, handy for a quest or something, probably.', 'is_key_to': 'padlock', 'is_hidden': False}``, loc data: ``{'iron key': {'description': 'An iron key, handy for a quest or something, probably.', 'is_key_to': 'padlock', 'is_hidden': False}}``
#   FIELD: iron key
#   [init_single] ITEM NAME: iron key
#   [init_single] ITEM ENTRY: {'name': 'iron key', 'item_type': "{'can_pick_up', 'key'}", 'can_pick_up': True, 'item_size': 0, 'is_key': True, 'description': 'An iron key, handy for a quest or something, probably.', 'is_key_to': 'padlock', 'is_hidden': False, 'iron key': False}

"iron key": False is coming from.

5.48pm
Okay, think I've fixed it, at least that part. Now, can look at and even pick up the iron key correctly.

Now:
Noun fails: <ItemInstance padlock (02745d80-2d52-4183-a28e-3e075fb70a75)>, verbname: use
Cannot 'use' the key on the padlock, because both key and padlock fail with verbname 'use'. Need to add the verbaction. Once I can remember how.

Though technically it failed this time because:
  File "d:\Git_Repos\choose-your-own\verb_actions.py", line 1181, in use_item_w_item
    verb_entry, noun_entry, direction_entry, cardinal_entry, location_entry, semantic_entry = get_entries_from_dict()
                                                                                              ~~~~~~~~~~~~~~~~~~~~~^^
TypeError: get_entries_from_dict() missing 1 required positional argument: 'input_dict'


Okay fixed a little bit more so I can have a more useful print:

Length format list: 4
More than one `noun`: {'instance': <ItemInstance iron key (f3d454c6-09ee-4c35-9661-1ca2ad2ceefb)>, 'str_name': 'iron key'} already exists, {'instance': <ItemInstance padlock (24de1864-7868-43cb-9f46-c1b397739184)>, 'str_name': 'padlock'} will be ignored.
MEANING for <ItemInstance iron key (f3d454c6-09ee-4c35-9661-1ca2ad2ceefb)> (5): in inventory
Cannot process {0: {'verb': {'instance': <verbInstance use (7be1ace6-6b4f-470b-aa9e-6ebeacdc93af)>, 'str_name': 'use'}}, 1: {'noun': {'instance': <ItemInstance iron key (f3d454c6-09ee-4c35-9661-1ca2ad2ceefb)>, 'str_name': 'iron
key'}}, 2: {'direction': {'instance': None, 'str_name': 'on'}}, 3: {'noun': {'instance': <ItemInstance padlock (24de1864-7868-43cb-9f46-c1b397739184)>, 'str_name': 'padlock'}}} in def use_item_w_item() End of function, unresolved. (Function partially written but doesn't do anything.)

6.04pm

Okay -- so it's been a straight 7 hrs, but - you can now pick up a key, go to a padlock, and use the key to open the padlock. Still needs help but, it's something.

Now currently, you can just... take the padlock, because it's not parented to anything, and parenting is the only thing that restricts access. Need to actually implement the events. Events hold data re: intances now, but the verb_actions don't do anything about it or feed data back. So will do that next. Need to add a check, in router(), that checks if an affected item is in events.
That feels wasteful though, each function already checks the noun etc. idk, will think about that. But either way, a check early on. Oh, maybe I can put the noun-is-event-relevant check in the /noun instance getter/. Might be good? Or would repeat too many times. Though that's my problem regardless just because it's so poorly laid out. Anyway. Will think on it.

7.53pm
Got the event working, ish.
There's nothing actually testing the padlock/key outside of this final check yet though. I've got a fn to set noun attr through which will check if it's event-relevant, but I need to employ that far more broadly (ie virtually all verbs...? )


10.14am 25/1/26
Events are minimally implemented; unlocking the padlock now enables travel outside the graveyard.


11.56am
NOTE: local descriptions do not update with item removal like they should. I imagine it's because they're only generated once, not repeatedly.

When should they regenerate? Each time they're called? Probably I guess.

also need to exclude hidden items from "You see a few scattered objects in this area:", otherwise they show up when they shouldn't.

Also if there's item_desc, 'long_desc' should never be used. Eventually I should just replace long_desc entirely and use item_desc exclusively, even if there are no items, and just have 'generic' hold the long_desc text. Might do that this afternoon.



2.25pm
Working on the location descriptions updating.

Currently:

[[  look east  ]]

You turn to face the eastern graveyard
local_items: {<ItemInstance gate (db301f06-fe0e-4040-a22f-febe95bcd38f)>, <ItemInstance padlock (0569b409-d1c1-4363-8636-f4cfceb930e0)>}
itemRegistry.registry.instances_by_name(item)[0] : <ItemInstance gate (db301f06-fe0e-4040-a22f-febe95bcd38f)>
local_items: {<ItemInstance gate (db301f06-fe0e-4040-a22f-febe95bcd38f)>, <ItemInstance padlock (0569b409-d1c1-4363-8636-f4cfceb930e0)>}
itemRegistry.registry.instances_by_name(item)[0] : <ItemInstance padlock (0569b409-d1c1-4363-8636-f4cfceb930e0)>
local_items: {<ItemInstance moss (f8c859ab-95a7-4c22-b6c8-7d0a3210624b)>, <ItemInstance desiccated skeleton (4015fb32-fb2f-4847-ac80-3b7b5617c5ce)>}
itemRegistry.registry.instances_by_name(item)[0] : <ItemInstance moss (f8c859ab-95a7-4c22-b6c8-7d0a3210624b)>
local_items: {<ItemInstance moss (f8c859ab-95a7-4c22-b6c8-7d0a3210624b)>, <ItemInstance desiccated skeleton (4015fb32-fb2f-4847-ac80-3b7b5617c5ce)>}
itemRegistry.registry.instances_by_name(item)[0] : <ItemInstance glass jar (88a3ab4a-07d2-4d67-b265-9a67b7b1c8f1)>
You're facing east. You see a variety of headstones, most quite worn and decorated by , and clumps of moss.

vs

[[  look around  ]]


You see a rather poorly kept graveyard - smaller than you might have expected given the scale of the gate and fences.
The entrance gates are to the north. To the east sit a variety of headstones, to the south stands a mausoleum, and to the west is what looks like a work shed of some kind.

You're facing east. You see a variety of headstones, most quite worn and decorated by clumps of moss, and a glass jar being used as a vase in front of one of the headstones, with some dried flowers left long ago.

You see a few scattered objects in this area:
   moss

So, two issues:

1: in 'look around', the glass jar is still present.
2: in 'look east', the glass jar is removed, but the output formatting is acting as if the glass jar was still present.


Issue 1:
    'look_around' == misc_utilities > def look_around.
    look_around doesn't call get_loc_descriptions, so no update happens.
    Fixed now, but it still prints "You see a few scattered objects in this area:" even if there are no items to print, it's checking the wrong thing. Or not checking anything, I don't remember.


Issue 2:
    Formatting should be set by the length of items in long_desc. But long_desc counts the generic description statement as 1, so it's always accounting for one more.
    Fixed now. It wasn't a counting issue, I just had a mistake in how it formatted base+1.

Issue 3:
    If facing east and take item, then 'look east', does not update.

2.48pm All issues seem to be fixed. Hopefully have set the descriptions to update everywhere.
Really should just replace the print(loc.current.long_desc) calls with a function rather than having to repeat
#        get_loc_descriptions(place=loc.currentPlace)
#        print(loc.current.long_desc)
each time, but it works.

4.54 setting up the item attr editing more formally. meta_commands is going to be useful. Currently it only edits the live data but will give it the option to add the edits to generated or proper dict.

NOTE: I need to find where it's adding 'key' as an attr. I already have 'is_key', I don't need 'key' too. Also the annoying thing where it adds the item's name as a field, so iron key has 'iron key': True. So silly and serves no purpose, need to figure out where that's coming from.

6.22pm
 'name': 'gate',
 'nicename': 'gate',
 'padlock': {'event': 'graveyard_gate_opens',
             'event_key': True,
             'is_locked': True,
             'key_is_placed_elsewhere': True,
             'requires_key': 'iron key'},
 'requires_key': False,
 'starting_location': <cardinalInstance north graveyard (d9b99560-f884-4d7f-ab1e-29bcc63edd34)>,
 'verb_actions': {'can_be_opened', 'can_be_locked'}}

 Huh. Somewhere (assumedly the parenting), it's adding the parent data to the key? Maybe what's happening with the iron key, too. Weeeierd. Need to look into this tomorrow.
