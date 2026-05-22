import random

from interactions.meta_commands import yes_test
from misc_utilities import npc_colour
from npcRegistry import npcInstance, npc_Registry, conversationInstance, conversing

from config import print_conversation_lines
from printing import print_green, print_blue, print_red

print_nothingelse_after_keyword = True

def convo_print(*input_str):

    print_colours_only = True
    if input_str == '' or not input_str:
        return

    def print_colours(part):
        if "PRINTGREEN " in part and isinstance(part, str):
            part = part.replace("PRINTGREEN ", '')
            print_green(part, invert=True)
        elif "PRINTBLUE " in part and isinstance(part, str):
            part = part.replace("PRINTBLUE ", '')
            print_blue(part, invert=True)
        elif "PRINTRED " in part and isinstance(part, str):
            part = part.replace("PRINTRED ", '')
            print_red(part, invert=True)

    if print_colours_only:
        for part in input_str:
            if "PRINT" in part:
                print_colours(part)

    elif print_conversation_lines:
        for part in input_str:
            if "PRINT" in part:
                print_colours(part)
            else:
                print(part)

affect = npc_Registry.alter_speech

leave_convo = ["leave conversation", "end conversation", "end convo", "leave convo", "leave", "end", "nothing", "goodbye", "bye"]


def manage_events(npc, event_data):

    from eventRegistry import events # will need updating to allow for generated/repeating events.
    if event_data.get("starts_event"):
        event_name = event_data["starts_event"]
        event = events.event_by_name(event_name)
        if event:
            events.start_event(event.name, event, noun=npc)
            events.set_state(event, 1)
            #print(f"Event found from conversation trigger: {event}")


def check_requirements(data, keyword, conversation, npc):
    """True or "no_check" if the requirements were not met ("no check" means there were no requirements), False means requirements existed but were not met."""
    requirement_not_met = True

    if data.get("has_requirements") and data["has_requirements"]:
        for kind, name in data["has_requirements"].items():
            requirement_not_met = tuple((kind, name))
            if kind == "item":
                specification = "in_inv"
                if isinstance(name, dict):
                    name, specification = next(iter(name.items()), None)
                from itemRegistry import registry
                if specification == "in_inv":
                    from env_data import locRegistry
                    named_in_inv = list(i for i in registry.by_location[locRegistry.inv_place] if registry.by_location.get(locRegistry.inv_place) and i.name == name)
                    if named_in_inv:
                        requirement_not_met = False
                elif specification == "encountered":
                    if registry.instances_by_name(name):
                        named = set(i for i in registry.instances_by_name(name) if i.encountered)
                        if named:
                            requirement_not_met = False

                #from misc_utilities import from_inventory_name
                #item = from_inventory_name(name)
                #if item and isinstance(item, itemInstance):
                    #requirement_met = True
            if kind == "location":
                from env_data import locRegistry
                if name.lower() in locRegistry.current.place_name.lower():
                    requirement_not_met = False
            if kind == "event":
                from eventRegistry import events
                event = events.by_name.get(name)
                if isinstance(event, set):
                    event = list(i for i in event if i.state in (0, 1))
                    event = event[0] if event else None
                #print(f"Event: {event}")
                if event and event.state in (0, 1): # past + present, not future. May set this to just future or specify required state at some point.
                    requirement_not_met = False
            if kind == "keyword":
                convo_print(f"kind == keyword, is_keyword = {keyword}, keyword required = {name}")
                if keyword and keyword == name or (conversation.reverse_keywords.get(keyword) and conversation.reverse_keywords[keyword] == name):
                    convo_print("keyword matches")
                    requirement_not_met=False

            if requirement_not_met:
                if data.get("if_not_requirements"):
                    print("\n   ", affect(npc, data["if_not_requirements"]["speech"]), "\n")
                return requirement_not_met # return per-item if it fails. So if any of the required items fail, they all fail.  I think that's the simplest way to deal with the comment below.

        return requirement_not_met # currently can only deal with one at a time. If you need to check both a current event + an item, this won't cut it.
    else:
        if not data["autoplay"]:
            convo_print(f"KEYWORD: {keyword} // data.get(keywords): {data.get('keywords')}\n")
            convo_print(f"conversation.reverse_keywords.get(keyword): {conversation.reverse_keywords.get(keyword)}")
            if data.get("keywords") and keyword:
                convo_print(f"data.get('keywords'): {data.get('keywords')}")
                if keyword and keyword in data["keywords"]:
                    convo_print(f"keyword in check: {keyword} / type: {keyword} // data.get('keywords'): {data.get('keywords')}\n")
                    return False # return False so requirement is met for keywords.
                elif keyword and conversation.reverse_keywords.get(keyword) in data["keywords"]:
                    convo_print(f"keyword in check: {keyword} / type: {keyword} // data.get('keywords'): {data.get('keywords')}\n")
                    return False # return False so requirement is met for keywords.
            return "keyword_only"

        return "no_check"

def confirm_use_of_data(npc, data):
    convo_print(f"[in confirm_use_of_data for {npc.name}]")
    if not data:
        return
    if data.get("event"):
        manage_events(npc, data["event"])

    if data.get("add_conversation"):
        from npcRegistry import npc_Registry
        npc_Registry.add_conversation_to_npc(npc, topic=data["add_conversation"])

def if_can_be_answered(data):
    requirement_met = True
    failure = None

    if data.get("requirements"):
        requirement_met = False
        for key, value in data["requirements"].items():
            if key == "datapoint":
                from set_up_game import game
                if game.datapoints:
                    for k, v in game.datapoints.items():
                        if v == value:
                            requirement_met = True
            # if key == othe things that aren't set up yet
        if not requirement_met:
            failure = data["requirements"].get("if_requirement_not_met")
    else:
        requirement_met = True

    return requirement_met, failure

def test_response(test:str, data:dict, npc:npcInstance, conversation:conversationInstance, failed_checks:set=set(), parts_said=set(), keyword_part:str=None, answering_question:bool=False):

    if (test and test != "failed") or answering_question:
        if data.get("can_be_answered") or answering_question:
            print("About to ask question, ln161")
            next_keyword = ask_question(npc, data)
            if next_keyword == "trade":
                print("going to trade (from keyword)")
                from interactions.trade import trade_with
                trade_with(npc)
                next_keyword = "end_topic"
            print("next_keyword line 151 after ask_questions")
            if next_keyword and next_keyword != "end_topic":
                next_keyword = "KEYWORD" + next_keyword
            return next_keyword, failed_checks, parts_said
        else:
            convo_print(f"cannot be answered, confirming use of data. test is : `{test}`")
            confirm_use_of_data(npc, data)

    if test:
        is_keyword = False
        convo_print(f"test_response going to run_keyword: ({test})")
        outcome, is_keyword = run_keyword(npc, conversation, idx=None, test=test)

        if is_keyword and not is_keyword == "skip_printing":
            convo_print(f"is_keyword after run_keyword, about to return outcome ({outcome}), failed_checks ({failed_checks}) and parts_said ({parts_said}) from ln 216")
            outcome = "KEYWORD" + outcome
            return outcome, failed_checks, parts_said

        if outcome == "end_topic":
            if print_nothingelse_after_keyword and not (is_keyword and is_keyword == "skip_printing"):
                from time import sleep
                sleep(.2)
                print("   ", affect(npc, "That's all for that for now."), "\n")
                #print("   ", affect(npc, f"{random.choice(npc.nothing_else)}" if npc.nothing_else else "It seems like there's nothing else to say about this."))
            return outcome, failed_checks, parts_said # if I change the first part to 'inner_loop' here, it resumes the prior conversation where it diverged.

        if not is_keyword or is_keyword == "skip_printing":
            print(f"    {npc_colour(npc, f'`{test}`?')}", affect(npc, f"{random.choice(npc.unsure)}"), "\n")
            return "was_input", failed_checks, parts_said

    elif test and test == "failed":# and keyword_part:
        if len(keyword_part) == 1 and conversation.reverse_keywords.get(keyword_part):
            keyword_part = conversation.reverse_keywords.get(keyword_part)
        print(f"    {npc_colour(npc, f'`{keyword_part}`?')}", affect(npc, f"{random.choice(npc.unsure)}"), "\n")
        return "was_input", failed_checks, parts_said

    else:
        convo_print("no test, confirming use of data")
        confirm_use_of_data(npc, data)

    if parts_said:
        npc.conversations[conversation]["parts_said"] = parts_said

    return None, failed_checks, parts_said

def check_data(npc:npcInstance, idx:str, conversation:conversationInstance, data:dict, parts_said=set(), is_keyword=False, failed_checks:set=set()):

    keyword_met = False
    convo_print(f"[in check_data] checking data for {idx}, failed_checks: {failed_checks}, is_keyword: {is_keyword}\n")
    not_requirements = check_requirements(data, is_keyword, conversation, npc)
    if not_requirements:
        if not_requirements == "no_check":
            if not data.get("autoplay") and is_keyword:
                if isinstance(is_keyword, set) and len(is_keyword) == 1:
                    is_keyword = next(iter(is_keyword), None)
                convo_print(f"No check required, not autoplay, is_keyword: {is_keyword}, is_keyword type: {type(is_keyword)}")
                if not ((conversation.reverse_keywords.get(is_keyword) and data.get("keywords")) and conversation.reverse_keywords[is_keyword] in data["keywords"]):
                    convo_print(f"[in check_data {not_requirements}] not conversation.reverse_keywords.get(is_keyword): {conversation.reverse_keywords.get(is_keyword)} // \nor not data.get('{'keyword'}'): {data.get("keywords")} or not data keyword == reverse_keywords[is_keyword]: {conversation.reverse_keywords.get(is_keyword) in data.get('keywords')}")
                    return "failed", failed_checks, parts_said
        elif not_requirements == "keyword_only":
            convo_print(f"Idx {idx} is keyword only and either no keyword was provided or the keyword did not match this idx: {is_keyword}\nReturning None from check_data.")
            return "failed", failed_checks, parts_said
        else:
            convo_print(f"NOT REQUIREMENTS: {not_requirements}")
            if not failed_checks:
                failed_checks = set()
            failed_checks.add(idx)
            return "failed", failed_checks, parts_said
            """if not data.get("autoplay") and not is_keyword:
                convo_print(f"[in check_data] failed check: autoplay and not is_keyword. Data:\n{data}\n[adding [{idx}] to failed_checks\n")
            elif not data.get("autoplay"):
                convo_print(f"[in check_data] failed check: not get_autoplay. Data:\n{data}\nReturning None\n")
                return None, failed_checks, parts_said
            if is_keyword:
                convo_print(f"[in check_data] failed check: is_keyword. Data:\n{data}\nReturning 'failed'\n")
                return "failed", failed_checks, parts_said"""
    else:
        convo_print(f"[in check_data] `{idx}` meets the requirements:")
        if data["has_requirements"]:
            for kind, name in data["has_requirements"].items():
                convo_print(f"kind: {kind} / name: {name}")
            convo_print("end requirements print\n---------------\n")
        else:
            #if not id)
            print(f"keyword_requirement_met: {is_keyword}")
            keyword_met = True

    if not data["speech"]:
        convo_print(f"[in check_data] no speech for {idx}, returning None.\n")
        return None, failed_checks, parts_said

    if not data.get("autoplay") and not is_keyword:
        convo_print(f"[in check_data] not autoplay and not is_keyword for {idx}, returning None.\n")
        return None, failed_checks, parts_said

    if parts_said and idx in parts_said and not is_keyword:
        convo_print(f"[in check_data] parts said and idx `{idx}`in parts_said\n")
        return None, failed_checks, parts_said

    if not parts_said and parts_said == None:
        convo_print(f"[in check_data] no parts_said, getting from npc.conversations")
        parts_said = npc.conversations[conversation].get("parts_said") if npc.conversations[conversation].get("parts_said") else set()
        convo_print(f"[in check_data] parts_said from npc.conversations: {parts_said}")

    convo_print(f"[in check_data] Adding {idx} to parts_said. parts_said before adding: {parts_said} / type: {type(parts_said)}")
    convo_print(f"parts said: {parts_said} ////")
    parts_said.add(idx)
    convo_print(f"parts_said after idx added: {parts_said}")
    if is_keyword:
        convo_print(f"is_keyword: `{is_keyword}`")
        if data.get("keywords"):
            convo_print(f"data.get(keywords): {data.get("keywords")}")
            if ((conversation.reverse_keywords.get(is_keyword) and data.get("keywords")) and conversation.reverse_keywords[is_keyword] in data["keywords"]):#
                convo_print("conversation match in reverse_keywords")
                keyword_met = True

    if is_keyword:
        print("\n   ", affect(npc, data["speech"]), "\n")
    else:
        print("\n   ", affect(npc, data["speech"]), "\n")
    #print(f"parts_said: {parts_said}")

    returning = None
    confirm_use_of_data(npc, data)
    if keyword_met == True:
        returning = "keyword_met"
    if data.get("can_be_answered"):
        print("Answering question from idx loop, ln 295")
        ask_question(npc, data)
        returning = "end_topic"

    return returning, failed_checks, parts_said


def get_new_conversations(npc:npcInstance, topic:str=None) -> None | dict[conversationInstance, set]:
    if not npc.conversations:
        print(f"{npc_colour(npc)} has nothing to say.")
        return None
    convo = None
    fresh_conversation = {}

    if topic:
        by_topic = conversing.by_topic.get(topic)
        if by_topic and by_topic in npc.conversations:
            fresh_conversation[by_topic] = list()
            for part in by_topic.by_part:
                if part not in npc.conversations[by_topic]:
                    fresh_conversation[by_topic].append(part)
    else:
        for convo, parts_said in npc.conversations.items():
            fresh_conversation[convo] = list()
            convo:conversationInstance = convo
            for part in convo.by_part:
                if not parts_said or part not in parts_said:
                    fresh_conversation[convo].append(part)

    return fresh_conversation

def discuss_topic(npc:npcInstance, conversation:conversationInstance, keyword_part=None, skip=False):


    """    outcome, is_keyword = run_keyword(npc, conv, convo.keywords[test], test)
        if is_keyword:
            test = outcome"""

    if not keyword_part:
        print("\n  ", affect(npc, f"{random.choice(npc.approval)} Let's discuss {conversation.topic_label}."))#, "\n")

    play_again = True
    parts_said = npc.conversations[conversation].get("parts_said")
    autoplay_failed = npc.conversations[conversation].get("autoplay_failed") #possibly don't need this at all, I'm doing the checks in advance anyway so keywords work properly.

    #print(f"parts said: {parts_said}, type: {type(parts_said)} // conversation.autoplay_parts: {conversation.autoplay_parts}")
    convo_print(f"[getting autoplay in said] existing parts_said for npc: `{parts_said}`\nexisting autoplay_failed for npc: `{autoplay_failed}`\n")
    autoplay_in_said = list(i for i in conversation.autoplay_parts if parts_said and i in parts_said)
    convo_print(f"autoplay_in_said at start: {autoplay_in_said}")
    failed_checks = set()
    for idx, data in conversation.by_part.items():
        if data.get("autoplay"):
            convo_print(f"Getting the precheck for failed requirements for {idx}. Data:\n{data}\n")
            failed_requirements = check_requirements(data, keyword_part, conversation, npc)
            print(f"Faield reqwuirements after check_requirements: {failed_requirements}")
            if failed_requirements and failed_requirements != "no_check":
                convo_print(f"--------------\nFailed requirements for idx {idx}: {failed_requirements}\n--------------")
                failed_checks.add(idx)

        else:
            convo_print(f"No autoplay for idx: {idx}.\nData: {data}\n--------------")

    if autoplay_failed and not failed_checks:
        failed_checks = autoplay_failed # why is this necessary. I don't get it.
    convo_print(f"failed checks in advance: {failed_checks}\nautoplay_failed: {autoplay_failed}\nlen(conversation.autoplay_parts): {len(conversation.autoplay_parts)}\n--------------")
    if autoplay_in_said and len(autoplay_in_said) + (len(failed_checks) if failed_checks else 0) >= len(conversation.autoplay_parts) and (keyword_part if keyword_part and keyword_part in autoplay_in_said and len(autoplay_in_said) == 1 else not keyword_part): # < so it doesn't succeed if we said a bunch of keyword lines but not the autoplay ones as happened in testing.
    #if parts_said and len(parts_said) >= len(conversation.autoplay_parts):
        print("\n   ", affect(npc, "We've discussed this topic before. Do you want to discuss it again?"), "\n")
        test = input("... ")
        if test and test.lower() in ("y", "yes"):
            print("\n   ", affect(npc, f"{random.choice(npc.approval)}"), "\n")
            parts_said = set()
            autoplay_in_said = parts_said
            npc.conversations[conversation]["parts_said"] = parts_said # wipe convo history if you say you want to discuss it again. Not the ideal way of doing it perhaps but what I'm going with for now.
            test = None
        else:
            print("\n   ", affect(npc, f"{random.choice(npc.acceptance)} Let us move on."), "\n")
            #print()
            return "end_topic"
    convo_print("about to run main bit of discuss_topic")
    failed_checks = set() # retry the checks each time in case conditions have changed
    if keyword_part:
        print("\n   ", affect(npc, f'Anyway, as I was saying...'), "\n")

    for idx, data in conversation.by_part.items():
        resumed = False
        if idx in autoplay_in_said:
            convo_print(f"idx in autoplay: {idx}")
            if not resumed:
                print("\n   ", affect(npc, f'As I was saying...'), "\n")
                resumed=True
            parts_said.add(idx)
            continue
        convo_print(f"[conversation.by_part] [no keyword]: idx: {idx}, data: {data}\nFailed checks before check_data not keyword: ``{failed_checks}``")
        print(f"Going to check_data ln 386 {data}")
        test_initial, failed_checks, parts_said = check_data(npc, idx, conversation, data, parts_said, is_keyword = None, failed_checks = failed_checks)
        convo_print(f"Test initial after check_data: `{test_initial}`\n")
        if test_initial and test_initial == "was_input":
            convo_print("was_input returned")
        if not test_initial:
            convo_print(f"NOT TEST INITIAL, getting new test input")
        #if test_initial and not test_initial == "was_input":
            test = input("(ln 394) ... ")
            test, failed_checks, parts_said = test_response(test, data, npc, conversation, failed_checks, parts_said)
            if test and "trade" in test:
                convo_print("going to trade (from keyword)")
                from interactions.trade import trade_with
                trade_with(npc)
                return "end_topic"
            convo_print(f"end of test_response lm 395: {test} / DATA: {data}")
            if data.get("can_be_answered"):
                convo_print(f"[[can_be_answered]]")
                outcome = ask_question(npc, data) # all the print lines contained in the question data are printed internally
                convo_print(f"next_keyword line 537 after ask_questions. Outcome: `{outcome}`")
                if outcome:
                    if outcome != "end_topic":
                        if outcome == "trade":
                            from interactions.trade import trade_with
                            trade_with(npc)
                            return "end_topic"
                        run_keyword(npc, conversation, idx, outcome) # for running keywords from inside the idx loop
                        return "end_topic"
            if test and test == "end_topic":
                convo_print(f"[no keyword] [idx {idx}] test is end_topic, returning end_topic")
                return "end_topic" # changed from returning None
            elif test and test == "inner_loop":
                convo_print(f"[no keyword] [idx {idx}] test is inner_loop, returning inner loop")
                return "inner_loop"
            else:
                convo_print(f"TEST AFTER TEST_RESPONSE: {test}")

        convo_print(f"[no keyword] [idx {idx}]  Test after check_data for {idx}: {test_initial}")
    convo_print(f"[after if/else loop in discuss_topic] failed checks: {failed_checks}\n")
    convo_print(f"[npc.conversations[conversation]['autoplay_failed]: {npc.conversations[conversation]['autoplay_failed']}\nParts said: {parts_said}")

    npc.conversations[conversation]["autoplay_failed"] = failed_checks
    npc.conversations[conversation]["parts_said"] = parts_said

    convo_print(f"[conversation.autoplay_parts and end of `discuss_topic`: {conversation.autoplay_parts}]")
    autoplay_in_said = list(i for i in conversation.autoplay_parts if (parts_said and (i in parts_said) or (failed_checks and i in failed_checks)))
    convo_print(f"[autoplay_in_said at end of `discuss_topic`: {autoplay_in_said}]")
    if autoplay_in_said and (len(autoplay_in_said) == len(conversation.autoplay_parts)) or (keyword_part and len(autoplay_in_said) == 1) or (autoplay_in_said == [] and keyword_part):
    #if parts_said and len(parts_said) >= len(conversation.autoplay_parts):
    #if not skip:
        if keyword_part:
            print("   ", affect(npc, f"{random.choice(npc.nothing_else)}" if npc.nothing_else else "It seems like there's nothing else to say about this."))
        else:
            print("\n   ", affect(npc, f"{random.choice(npc.nothing_else)}" if npc.nothing_else else "It seems like there's nothing else to say about this."))
            from time import sleep
            sleep(.2)
        print()
    return "end_topic"

def ask_question(npc, data):

    test = input("(ask_questions) ... ")
    convo_print("[Conversation part is a question, waiting for answer]")
    responses = {
        "if_yes": ["y", "yes"],
        "if_no": ["n", "no"]
    }

    def check_response(test) ->None|str:

        next_keyword = None
        #for criteria in responses:
        criteria = list(i for i in responses if test.lower() in responses.get(i))
        if criteria:
            criteria = criteria[0]
            convo_print(f"criteria in check_response: {criteria}")
            if (test and test.lower() in responses[criteria]) and data["can_be_answered"].get(criteria):
                requirement_met, failure = if_can_be_answered(data["can_be_answered"][criteria])
                if requirement_met:
                    convo_print("requirements_met if_can_be_answered")
                    confirm_use_of_data(npc, data)
                    if data["can_be_answered"][criteria].get("send_keyword"):
                        next_keyword = data["can_be_answered"][criteria]["send_keyword"]
                    if data["can_be_answered"][criteria].get("response"): # check this last to get keyword first is present.
                        print("\n   ", affect(npc, data["can_be_answered"][criteria]["response"]), "\n")
                    if next_keyword: # moved in a tab so it sends with or without a response, it shouldn't be dependent on that.
                        if next_keyword == "trade":
                            from interactions.trade import trade_with
                            trade_with(npc)
                            return "end_topic"
                        return next_keyword # sending 'outcome' here in case it had a keyword to send /and/ a response to print.
                    else:
                        return "end_topic"
                elif failure:
                    print("\n   ", affect(npc, failure), "\n")
                    return "end_topic"
                else:
                    print(f"Requirements not met and also not 'failure'. What? requirement_met: `{requirement_met}` // failure: `{failure}`")
        if not criteria:
            print(f"No criteria found for `{test}`")
        if not next_keyword or not criteria or not test:
            if test:
                print("\n   ", npc_colour(npc, f'`{test}`?'), affect(npc, speech_str=f"{random.choice(npc.unsure)} We'll carry on."), "\n")
            else:
                print("\n   ", affect(npc,random.choice(npc.acceptance)), "\n")
            return "end_topic"

        convo_print(f"End of check_response - should not get to here. next_keyword: `{next_keyword}`, test: `{test}`.")

    next_keyword = check_response(test)
    convo_print(f"After check_response, returning next_keyword string: {next_keyword}")
    return next_keyword


def run_keyword(npc:npcInstance, conversation:conversationInstance, idx:str, test:str) -> tuple[str|None,str]:
    """For keyword sections, instead of reusing discuss_topic"""
    convo_print(f"[run_keyword for conversation {conversation.topic_label} // {idx}]")
    outcome = "unknown"

    if test == "trade":
        print("TEST == TRADE. Sending to trade.")
        from interactions.trade import trade_with
        trade_with(npc)
        return "end_topic", "skip_printing"

    if not idx and conversation.keywords.get(test):
        idx = conversation.keywords[test]
        if not idx:
            idx = conversation.reverse_keywords.get(test)

    if not idx:
        print(f"IDX not found and no keyword to match. Test: `{test}`\n")
        return "failed", None # assume a typo and treat as such?

    if not conversation.keywords.get(test):
        convo_print(f"in run_keyword: {test} // not in conversation.keywords")
        return "unknown", None
    keyword = None
    if conversation.by_part.get(idx):
        convo_print(f"in run_keyword: {test} // not in conversation.by_part")
        data = conversation.by_part[idx]
        #idx = idx if len(idx) == 1 else conversation.keywords[idx]
        #convo_print(f"idx == keyword part if keyword_part len 1: {idx}\nData: {data}")
        failed_requirements = check_requirements(data, test, conversation, npc)
        if (failed_requirements and not failed_requirements == "no_check") or not data["speech"]:
            convo_print("[[failed requirements (except no_check) and/or no 'speech'.]]")
            return "unknown", None
            """if not_requirements == "no_check":
            elif not_requirements == "keyword_only":"""

        print("\n   ", affect(npc, data["speech"]), "\n")

        if data.get("can_be_answered"):
            print("About to ask question, ln 534")
            outcome = ask_question(npc, data) # all the print lines contained in the question data are printed internally
            convo_print(f"next_keyword line 537 after ask_questions. Outcome: `{outcome}`")
            if outcome:
                if outcome != "end_topic":
                    return outcome, "is_keyword"
                #return outcome, None

        else:
            test = input("(ln541)... ")
            if test:
                test, _, _ = test_response(test, data, npc, conversation)
                convo_print(f"Test after keyword inner test: {test}")
                keyword = "skip_printing"
            #convo_print("cannot be answered, confirming use of data")
            convo_print("cannot be answered, confirming use of data")
            confirm_use_of_data(npc, data)
            #print("   ", affect(npc, f"{random.choice(npc.nothing_else)}" if npc.nothing_else else "It seems like there's nothing else to say about this."))
            convo_print("[[[returining 'end_topic' after completing keyword entry]]]")
            outcome = "end_topic" # assuming we immediately end topic after a keyword word, which isn't always true...

        """test, _, _ = check_data(npc, idx, conversation, data, parts_said=None, is_keyword=idx, failed_checks=None)
        print(f"if keyword_part, after check test = {test}")

        if test and not test == "was_input":
            convo_print(f"test and not test == was_input: {test}")
            if test == "keyword_met":
                test = None
            if test == "can_be_answered":
                test = input("...")
            test, _, _ = test_response(test, data, npc, conversation, keyword_part=idx, answering_question=True if test == "can_be_answered" else False)
            test = input("...")

        #test, failed_checks, parts_said = check_for_keywords(keyword_part, conversation, npc,failed_checks)
            if test == "end_topic":
                convo_print(f"[with keyword] [keyword_part: {idx}] test is end_topic, returning inner_loop")
                return "inner_loop"
            if test == "failed":
                convo_print(f"[with keyword] [keyword_part: {idx}] test is failed, returning failed")
                return "failed"
            if test == "inner_loop":
                convo_print(f"[with keyword] [keyword_part: {idx}] returning inner loop")
                return "inner_loop"
        print(f"Keyword part over: {test}")
        if test and (yes_test(test) or no_test(test)):
        return "keyword_done"
            return test"""
    #else:
    return outcome, keyword

def conversation_loop(npc:npcInstance):
    """Conversation loop calls the parser directly, and doesn't go through router. When conversation ends (by 'leave conversation' type input or end_of_conversation marker), return to main loop."""
    user_input = None
    new_conversations = get_new_conversations(npc) # possibly don't need this at all
    convo_print(f"top of conversation_loop. Has new_conversations: {"True" if new_conversations else "False"}")
    if not new_conversations:
        print("   ", affect(npc), "I'm not sure we have much else to talk about, I think we've covered anything. Do you want to go over it again?")
        if not yes_test():
            print("   ", affect(npc, speech_str=f"No? {random.choice(npc.acceptance)}"))
            return

    print("   ", npc_colour(npc, "What do you want to talk about?\n"))
    convo_dict = {}
    alt_dict = {}
    for convo in new_conversations:
        print("   ", npc_colour(npc, f"  - {convo.topic_label}"))
        convo_dict[convo.topic_label] = convo
        if convo.alt_labels:
            for label in convo.alt_labels:
                alt_dict[label] = convo.topic_label

    test = input("\n(ln603)... ")
    if test and test != "":
        found = False
        if test in leave_convo:
            return test
        if "trade" in test:
            print("going to trade (from keyword)")
            from interactions.trade import trade_with
            trade_with(npc)
            return "end_topic"

        for convo in new_conversations:
            if convo.keywords.get(test):
                found=True
                outcome, is_keyword = run_keyword(npc, convo, convo.keywords[test], test)
                convo_print(f"PRINTRED AFTER RUN_KEYWORD IN CONVERSATION_LOOP: test: `{test}` / is_keyword: `{is_keyword}`, outcome: `{outcome}`")
                convo_print(f"\nOutcome after run_keyword: `{outcome}`\n")
                if is_keyword and is_keyword != "skip_printing":
                    convo_print(f"is_keyword, about to return outcome ({outcome}) from ln 615")
                    test = outcome
                    found = True # found True should let it loop again, I think.
                    convo_print(f"is_keyword {test}; breaking for loop.")
                    break
                if outcome == "unknown" or outcome == "failed": # might merge later
                    found = False
                if outcome == "end_topic":
                    if not (is_keyword and is_keyword == "skip_printing"):
                        if print_nothingelse_after_keyword:
                            from time import sleep
                            sleep(.2)
                            print("   ", affect(npc, "That's all for that for now.\n"))
                            #print("   ", affect(npc, f"{random.choice(npc.nothing_else)}" if npc.nothing_else else "It seems like there's nothing else to say about this."))
                    return outcome

                """user_input = discuss_topic(npc, convo, convo.keywords[test])
                convo_print(f"PRINTBLUE AFTER THE FIRST DISCUSS_TOPIC IN CONVERSATION_LOOP: {user_input}")
                if user_input == "failed" or user_input == "keyword_done":
                    found = False
                if user_input == "inner_loop":
                    return "inner_loop"
"""
        if not found:
            convo_print(f"`not_found` after first discuss_topic loop for test [ `{test}` ]")
            for label in convo_dict:
                if test and (test.lower() in label.lower() or (convo.alt_labels and test.lower() in convo.alt_labels)):
                    if (convo.alt_labels and test in convo.alt_labels):
                        label = alt_dict[test]
                    found=True
                    user_input = discuss_topic(npc, convo_dict[label])
                    convo_print(f"PRINTGREEN AFTER DISCUSS_TOPIC IN CONVERSATION_LOOP: {user_input} / label: {label}")
                    if user_input == "failed":
                        found = False
                    if user_input == "inner_loop":
                        convo_print(f"[returning from not_found after discuss_topic for {label}]")
                        return "inner_loop"
                    if user_input == "end_topic":
                        return "end_topic"

        if not found:
            print("Not found in conversation_loop")
            if user_input == "keyword_done":
                return "inner_loop"
            print(f"    {npc_colour(npc, f'`{test}`?')}", affect(npc, f"{random.choice(npc.unsure)}"), "\n")
            return "end_topic" # get it to relist the conversation options. Might not work.

    else:
        convo_print(f"[Returning [{test}] from 'else' in conversation_loop]")
        return test

    """if user_input:
        while user_input:
            if user_input == "end_topic":
                return user_input

            if npc.keywords: # [kw] = {convo:convo.keywords[kw]}
                for kw in npc.keywords:
                    if user_input in kw:
                        for convo, idx in npc.keywords[kw].items():
                            user_input = discuss_topic(npc, convo, convo.by_part[idx])
                            convo_print(f"PRINTRED AFTER THE THIRD DISCUSS_TOPIC IN CONVERSATION_LOOP: {user_input}\nreturning 'end_topic' from conversation_loop")
                            return "end_topic"""


def start_conversation(npc:npcInstance):

    print(f"You approach the {npc_colour(npc)} to start a conversation.\n")
    if not npc.encountered:
        print(npc.introduction, "\n")
        npc.encounter("Encountered in start_conversation in conversations.py")
    if npc.convo_start:
        print("  ", affect(npc, npc.convo_start), "\n")

    output = "end_topic" # setting this as a string so the loop starts immediately, instead of starting outside the loop
    while output in ("end_topic", "inner_loop"):
        convo_print(f"[while_loop in start_conversation] while output in (end_topic, inner_loop):` {output}`")
        output = conversation_loop(npc)
        convo_print(f"[while_loop in start_conversation] output: {output}")
        """if output == "inner_loop": # I don't think this is needed at all. Might predate the while loop?
            convo_print(f"[while_loop in start_conversation] {output}")
            output = conversation_loop(npc)
            convo_print(f"[while_loop in start_conversation] after conversation_loop after 'inner_loop': {output}")"""

    convo_print(f"[Output not in end_topic or inner_loop, end of `start_conversation` loop: `{output}`]")

    #if not output:
    #    print(f"\n   {affect(npc, f'Nothing else you want to discuss? {npc.convo_end}')}\n")
    #else:
    print(f"\n   {affect(npc, npc.convo_end)}\n")

    print(f"You step aside, leaving the conversation with {npc_colour(npc)}.\n\n")
