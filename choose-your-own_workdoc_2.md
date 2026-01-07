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
