from typing import Literal

from itemRegistry import itemInstance
from misc_utilities import npc_colour
from npcRegistry import npcInstance, npc_Registry, conversationInstance, conversing

from config import print_conversation_lines
from printing import print_green, print_blue, print_red

def convo_print(*input_str):

    if input_str == '' or not input_str:
        return

    if print_conversation_lines:
        for part in input_str:
            if "PRINTGREEN " in part and isinstance(part, str):
                part = part.replace("PRINTGREEN ", '')
                print_green(part, invert=True)
            elif "PRINTBLUE " in part and isinstance(part, str):
                part = part.replace("PRINTBLUE ", '')
                print_blue(part, invert=True)
            elif "PRINTRED " in part and isinstance(part, str):
                part = part.replace("PRINTRED ", '')
                print_red(part, invert=True)
            else:
                print(part)

affect = npc_Registry.alter_speech

leave_convo = ["leave conversation", "end conversation", "end convo", "leave convo", "leave", "end", "nothing"]

def manage_events(npc, event_data):

    from eventRegistry import events
    if event_data.get("starts_event"):
        event_name = event_data["starts_event"]
        event = events.event_by_name(event_name)
        if event:
            events.start_event(event.name, event, noun=npc)
            events.set_state(event, 1)
            print()
            #print(f"Event found from conversation trigger: {event}")

def check_requirements(data, keyword, conversation):
    """True or "no_check" if the requirements were not met ("no check" means there were no requirements), False means requirements existed but were not met."""
    requirement_not_met = True

    if data["has_requirements"]:
        for kind, name in data["has_requirements"].items():
            requirement_not_met = tuple((kind, name))
            if kind == "item":
                from itemRegistry import registry
                from env_data import locRegistry
                named_in_inv = list(i for i in registry.by_location.get(locRegistry.inv_place) if i.name == name)
                if named_in_inv:
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
            if requirement_not_met:
                return requirement_not_met # return per-item if it fails. So if any of the required items fail, they all fail.  I think that's the simplest way to deal with the comment below.

        return requirement_not_met # currently can only deal with one at a time. If you need to check both a current event + an item, this won't cut it.
    else:
        if not data["autoplay"]:
            print(f"KEYWORD: {keyword}")
            print(f"data.get(keywords): {data.get('keywords')}\n")
            print(f"conversation.reverse_keywords.get(keyword): {conversation.reverse_keywords.get(keyword)}")
            if data.get("keywords") and keyword:
                print(f"data.get('keywords'): {data.get('keywords')}")
                if keyword and keyword in data["keywords"]:
                    print(f"keyword in check: {keyword} / type: {keyword} // data.get('keywords'): {data.get('keywords')}\n")
                    return False # return False so requirement is met for keywords.
                elif keyword and conversation.reverse_keywords.get(keyword) in data["keywords"]:
                    print(f"keyword in check: {keyword} / type: {keyword} // data.get('keywords'): {data.get('keywords')}\n")
                    return False # return False so requirement is met for keywords.
            return "keyword_only"

        return "no_check"

def confirm_use_of_data(npc, data):
    convo_print(f"[in confirm_use_of_data for {npc.name}]")
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

def check_data(npc:npcInstance, idx:str, conversation:conversationInstance, data:dict, parts_said=None, is_keyword=False, failed_checks:set=set()):

    convo_print(f"[in check_data] checking data for {idx}, failed_checks: {failed_checks}, is_keyword: {is_keyword}\n")
    not_requirements = check_requirements(data, is_keyword, conversation)
    if not_requirements:
        if not_requirements == "no_check":
            if not data.get("autoplay") and is_keyword:
                if isinstance(is_keyword, set) and len(is_keyword) == 1:
                    is_keyword = next(iter(is_keyword), None)
                convo_print(f"No check required, not autoplay, is_keyword: {is_keyword}, is_keyword type: {type(is_keyword)}")
                if not ((conversation.reverse_keywords.get(is_keyword) and data.get("keywords")) and conversation.reverse_keywords[is_keyword] in data["keywords"]):
                    convo_print(f"[in check_data {not_requirements}] not conversation.reverse_keywords.get(is_keyword): {conversation.reverse_keywords.get(is_keyword)} // \nor not data.get('{'keyword'}'): {data.get("keywords")} or not data keyword == reverse_keywords[is_keyword]: {conversation.reverse_keywords.get(is_keyword) in data.get('keywords')}")
                    return None, failed_checks, parts_said
        elif not_requirements == "keyword_only":
            convo_print(f"Idx {idx} is keyword only and either no keyword was provided or the keyword did not match this idx: {is_keyword}\nReturning None from check_data.")
            return None, failed_checks, parts_said
        else:
            print(f"NOT REQUIREMENTS: {not_requirements}")
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

    parts_said.add(idx)

    if is_keyword:
        print("\n   ", affect(npc, data["speech"]), "\n")
    else:
        print("\n   ", affect(npc, data["speech"]), "\n")
    #print(f"parts_said: {parts_said}")

    confirm_use_of_data(npc, data)

    test = input("...")
    if test:
        skip = False
        if data.get("can_be_answered"):
            if data["can_be_answered"].get("if_yes"):
                if test.lower() in ("y", "yes"):
                    requirement_met, failure = if_can_be_answered(data["can_be_answered"]["if_yes"])
                    if requirement_met:
                        convo_print("requirements_met if_can_be_answered")
                        confirm_use_of_data(npc, data)
                        test = data["can_be_answered"]["if_yes"].get("send_keyword")
                    elif failure:
                        print("\n   ", affect(npc, failure), "\n")
                        return None, failed_checks, parts_said

                import random
                print("\n   ", affect(npc,random.choice(npc.acceptance)), "\n")
                return None, failed_checks, parts_said
        else:
            convo_print("cannot be answered, confirming use of data")
            confirm_use_of_data(npc, data)

        if test.lower() in ("y", "yes"):
            print("What do you want to say?")
            test = input("\n... ")
    else:
        convo_print("no test, confirming use of data")
        confirm_use_of_data(npc, data)
        skip = True


    if test:
        is_keyword = False
        print(f"about npc.keywords.get({test}): ")
        if npc.keywords.get(test):# = {convo:convo.keywords[kw]}
            print("npc.keywords.get(test): ", npc.keywords.get(test))
            if parts_said:
                convo_print(f"parts_said: {parts_said} // npc.conversations[conversation]['parts_said'] :", npc.conversations[conversation]['parts_said'])
                npc.conversations[conversation]["parts_said"] = parts_said
            else:
                convo_print(f"No parts_said for test {test}")
            if failed_checks:
                npc.conversations[conversation]["autoplay_failed"] = failed_checks

            for convo, entry in npc.keywords[test].items():
                convo_print(f"[sending convo and entry `{entry}` / type: {type(entry)} to discuss_topic from if test in check_data]")
                outcome = discuss_topic(npc, convo, entry, skip=skip)
                skip = True
                convo_print(f"discuss_topic outcome for {test}: {outcome}")
                if outcome == "end_topic":
                    convo_print(f"[outcome for discuss_topic inside check_data: {outcome} for keyword_test {test}], returning end_topic\n--------------\n\n")
                    return "end_topic", failed_checks, parts_said
                if outcome == "inner_loop":
                    convo_print(f"[outcome for discuss_topic inside check_data: {outcome} for keyword_test {test}], returning end_topic\n--------------\n\n")
                    return "end_topic", failed_checks, parts_said
                    return "inner_loop"
                print(f"outcome is not end_topic or inner_loop: {outcome}")

        if not is_keyword:
            import random
            print(f"    {npc_colour(npc, f'`{test}`?')}", affect(npc, f"{random.choice(npc.unsure)}"), "\n")
            return None, failed_checks, parts_said

    npc.conversations[conversation]["parts_said"] = parts_said
    return None, failed_checks, parts_said

def check_for_keywords(keyword_part, conversation, npc, failed_checks) -> None | Literal['failed']:
    print(f"CHeck for keywords: {keyword_part}")
    if conversation.by_part.get(keyword_part):
        data = conversation.by_part[keyword_part]
        test, failed_checks, parts_said = check_data(npc, keyword_part, conversation, data, parts_said=None, is_keyword=True, failed_checks=failed_checks)
        return test, failed_checks, parts_said
    return None, failed_checks, parts_said

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

    import random
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
            failed_requirements = check_requirements(data, keyword_part, conversation)
            if failed_requirements and failed_requirements != "no_check":
                print(f"--------------\nFailed requirements for idx {idx}: {failed_requirements}\n--------------")
                failed_checks.add(idx)

        else:
            convo_print(f"No autoplay for idx: {idx}.\nData: {data}\n--------------")

    if autoplay_failed and not failed_checks:
        failed_checks = autoplay_failed # why is this necessary. I don't get it.
    convo_print(f"failed checks in advance: {failed_checks}\nautoplay_failed: {autoplay_failed}\nlen(conversation.autoplay_parts): {len(conversation.autoplay_parts)}\n--------------")
    if autoplay_in_said and len(autoplay_in_said) + (len(failed_checks) if failed_checks else 0) >= len(conversation.autoplay_parts) and (keyword_part if keyword_part in autoplay_in_said and len(autoplay_in_said) == 1 else not keyword_part): # < so it doesn't succeed if we said a bunch of keyword lines but not the autoplay ones as happened in testing.
    #if parts_said and len(parts_said) >= len(conversation.autoplay_parts):
        print("\n   ", affect(npc, "We've discussed this topic before. Do you want to discuss it again?"), "\n")
        test = input("... ")
        if test and test.lower() in ("y", "yes"):
            print("\n   ", affect(npc, f"{random.choice(npc.approval)}"), "\n")
            parts_said = set()
            npc.conversations[conversation]["parts_said"] = parts_said # wipe convo history if you say you want to discuss it again. Not the ideal way of doing it perhaps but what I'm going with for now.
            test = None
        else:
            print("\n   ", affect(npc, f"{random.choice(npc.acceptance)}"), "\n")
            #print()
            return "end_topic"
    convo_print("about to run main bit of discuss_topic")
    failed_checks = set() # retry the checks each time in case conditions have changed

    if play_again or keyword_part:
        #if not keyword_part:
        if keyword_part:
            convo_print(f"Keyword part: {keyword_part}")
            if conversation.by_part.get(keyword_part):
                data = conversation.by_part[keyword_part]
                idx = keyword_part if len(keyword_part) == 1 else conversation.keywords[keyword_part]
                convo_print(f"idx == keyword part if keyword_part len 1: {idx}\nData: {data}\nFailed checks before check_data if keyword_part: ``{failed_checks}``")
                test, failed_checks, parts_said = check_data(npc, idx, conversation, data, parts_said, keyword_part, failed_checks)
            #test, failed_checks, parts_said = check_for_keywords(keyword_part, conversation, npc,failed_checks)
                if test == "end_topic":
                    convo_print(f"[with keyword] [keyword_part: {keyword_part}] test is end_topic, returning inner_loop")
                    return "inner_loop"
                if test == "failed":
                    convo_print(f"[with keyword] [keyword_part: {keyword_part}] test is failed, returning failed")
                    return "failed"
                if test == "inner_loop":
                    convo_print(f"[with keyword] [keyword_part: {keyword_part}] returning inner loop")
                    return "inner_loop"

        else:
            for idx, data in conversation.by_part.items():
                convo_print(f"[conversation.by_part] [no keyword]: idx: {idx}, data: {data}\nFailed checks before check_data not keyword: ``{failed_checks}``")
                test, failed_checks, parts_said = check_data(npc, idx, conversation, data, parts_said, is_keyword = None, failed_checks = failed_checks)
                if test == "end_topic":
                    convo_print(f"[no keyword] [idx {idx}] test is end_topic, returning end_topic")
                    return "end_topic" # changed from returning None
                if test == "inner_loop":
                    convo_print(f"[no keyword] [idx {idx}] test is inner_loop, returning inner loop")
                    return "inner_loop"
                convo_print(f"[no keyword] [idx {idx}]  Test after check_data for {idx}: {test}")
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
        print()
    return "end_topic"

def conversation_loop(npc:npcInstance):
    """Conversation loop calls the parser directly, and doesn't go through router. When conversation ends (by 'leave conversation' type input or end_of_conversation marker), return to main loop."""
    user_input = None
    new_conversations = get_new_conversations(npc) # possibly don't need this at all
    if not new_conversations:
        print("   ", affect(npc), "I'm not sure we have much else to talk about.")
        return
    print("   ", npc_colour(npc, "What do you want to talk about?\n"))
    convo_dict = {}
    for convo in new_conversations:
        print("   ", npc_colour(npc, f"  - {convo.topic_label}"))
        convo_dict[convo.topic_label] = convo

    test = input("\n... ")
    if test and test != "":
        found = False
        if test in leave_convo:
            return test

        for convo in new_conversations:
            if convo.keywords.get(test):
                found=True
                user_input = discuss_topic(npc, convo, convo.keywords[test])
                convo_print(f"PRINTBLUE AFTER THE FIRST DISCUSS_TOPIC IN CONVERSATION_LOOP: {user_input}")
                if user_input == "failed":
                    found = False
                if user_input == "inner_loop":
                    return "inner_loop"

        if not found:
            convo_print(f"`not_found` after first discuss_topic loop for test [ `{test}` ]")
            for label in convo_dict:
                if test.lower() in label.lower():
                    found=True
                    user_input = discuss_topic(npc, convo_dict[label])
                    convo_print(f"PRINTGREEN AFTER THE second DISCUSS_TOPIC IN CONVERSATION_LOOP: {user_input} / label: {label}")
                    if user_input == "failed":
                        found = False
                    if user_input == "inner_loop":
                        convo_print(f"[returning from not_found after discuss_topic for {label}]")
                        return "inner_loop"

        if not found:
            import random
            print(f"    {npc_colour(npc, f'`{test}`?')}", affect(npc, f"{random.choice(npc.unsure)}"), "\n")
            return "end_topic" # get it to relist the conversation options. Might not work.

    else:
        convo_print(f"[Returning [{test}] from 'else' in conversation_loop]")
        return test

    if user_input:
        while user_input:
            if user_input == "end_topic":
                return user_input

            if npc.keywords: # [kw] = {convo:convo.keywords[kw]}
                for kw in npc.keywords:
                    if user_input in kw:
                        for convo, idx in npc.keywords[kw].items():
                            user_input = discuss_topic(npc, convo, convo.by_part[idx])
                            convo_print(f"PRINTRED AFTER THE THIRD DISCUSS_TOPIC IN CONVERSATION_LOOP: {user_input}\nreturning 'end_topic' from conversation_loop")
                            return "end_topic"


def start_conversation(npc:npcInstance):

    print(f"You approach the {npc_colour(npc)} to start a conversation.\n")
    if not npc.encountered:
        print(npc.introduction, "\n")
    if npc.convo_start:
        print("  ", affect(npc, npc.convo_start), "\n")

    output = conversation_loop(npc)
    while output in ("end_topic", "inner_loop"):
        convo_print(f"[while_loop in start_conversation] while output in (end_topic, inner_loop): {output}")
        output = conversation_loop(npc)
        convo_print(f"[while_loop in start_conversation] output: {output}")
        if output == "inner_loop":
            convo_print(f"[while_loop in start_conversation] {output}")
            output = conversation_loop(npc)
            convo_print(f"[while_loop in start_conversation] after conversation_loop after 'inner_loop': {output}")

    print(f"[Output not in end_topic or inner_loop, end of `start_conversation` loop: `{output}`]")

    if not output:
        print(f"\n   {affect(npc, f'Nothing else you want to discuss? {npc.convo_end}')}\n")
    else:
        print(f"\n   {affect(npc, npc.convo_end)}\n")

    print(f"You step aside, leaving the conversation with {npc_colour(npc)}.\n\n")
