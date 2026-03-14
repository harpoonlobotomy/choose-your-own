from itemRegistry import itemInstance
from misc_utilities import npc_colour
from npcRegistry import npcInstance, npc_Registry, conversationInstance, conversing

affect = npc_Registry.alter_speech

leave_convo = ["leave conversation", "end conversation", "end convo", "leave convo", "leave", "end"]
def get_new_conversations(npc:npcInstance, topic=None) -> None | dict[conversationInstance, set]:
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
                if part not in parts_said:
                    fresh_conversation[convo].append(part)

    return fresh_conversation

def discuss_topic(npc:npcInstance, conversation:conversationInstance, keyword_part=None, skip=False):

    import random
    if not keyword_part:
        print("\n  ", affect(npc, f"{random.choice(npc.approval)} Let's discuss {conversation.topic_label}."), "\n")
    else:
        print()
    play_again = False
    parts_said = npc.conversations[conversation].get("parts_said")
    if len(parts_said) == len(conversation.by_part):
        print("   ", affect(npc, "We've discussed this topic before. Do you want to discuss it again?"))
        test = input()
        if test.lower() in ("y", "yes"):
            print("   ", affect(npc, f"{random.choice(npc.approval)}", "\n"))
            play_again = True

    for idx, data in conversation.by_part.items():
        if not data["speech"]:
            continue
        if not keyword_part and not data.get("autoplay"): # so I can have lines only available if a keyword is used.
            continue
        if keyword_part and idx != keyword_part:
            continue
        if parts_said and idx in parts_said and not play_again and not keyword_part:
            continue

        if data["has_requirements"]:
            requirement_met = False
            for kind, name in data["has_requirements"].items():
                if kind == "item":
                    from misc_utilities import from_inventory_name
                    item = from_inventory_name(name)
                    if item and isinstance(item, itemInstance):
                        requirement_met = True
                if kind == "location":
                    from env_data import locRegistry
                    if name.lower() in locRegistry.current.place_name.lower():
                        requirement_met = True
                if kind == "event":
                    from eventRegistry import events
                    event = events.by_name.get(name)
                    if event and event.state == 1:
                        requirement_met = True
            if not requirement_met:
                continue
        parts_said.add(idx)
        print("   ", affect(npc, data["speech"]), "\n")

        test = input("...")
        if test:
            if test.lower() in ("y", "yes"):
                print("What do you want to say?")
                test = input("\n...")
        else:
            skip = True

        print()
        for convo in npc.conversations:
            if convo.keywords.get(test):
                discuss_topic(npc, convo, convo.keywords[test], skip=skip)
                skip = True
    if len(parts_said) == len(conversation.by_part):
    #if not skip:
        print("   ", affect(npc, "There's nothing else to say about this."))
        print()
    return "end_topic"

def conversation_loop(npc:npcInstance):
    """Conversation loop calls the parser directly, and doesn't go through router. When conversation ends (by 'leave conversation' type input or end_of_conversation marker), return to main loop."""

    new_conversations = get_new_conversations(npc) # possibly don't need this at all
    if not new_conversations:
        print("   ", affect(npc), "I'm not sure we have much else to talk about.")
        return
    print("   ", npc_colour(npc, "What do you want to talk about?\n"))
    convo_dict = {}
    for convo in new_conversations:
        print("   ", npc_colour(npc, f"  - {convo.topic_label}"))
        convo_dict[convo.topic_label] = convo

    test = input("\n")
    if test and test != "":
        found = False
        if test in leave_convo:
            return

        for convo in new_conversations:
            if convo.keywords.get(test):
                found=True
                user_input = discuss_topic(npc, convo, convo.keywords[test])

        if not found:
            for label in convo_dict:
                if test.lower() in label.lower():
                    found=True
                    user_input = discuss_topic(npc, convo_dict[label])
        if not found:
            return test

    else:
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


        print(f"User input: {user_input} \nI need to do something with this. For now, nothing happens.")


def start_conversation(npc:npcInstance):

    print(f"You approach the {npc_colour(npc)} to start a conversation.\n")
    if npc.convo_start:
        print("  ", affect(npc, npc.convo_start), "\n")

    output = conversation_loop(npc)
    while output == "end_topic":
        output = conversation_loop(npc)

    if output:
        output = output + "? "
    if npc.convo_end:
        if output:
            print(f"\n   {npc_colour(npc, output)}{affect(npc, npc.convo_end)}\n")
        else:
            print(f"\n   {affect(npc, npc.convo_end)}\n")

    print(f"You step aside, leaving the conversation with {npc_colour(npc)}.\n\n")
