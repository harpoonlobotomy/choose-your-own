#trade.py

from itemRegistry import itemInstance
import itemRegistry
from misc_utilities import assign_colour
from npcRegistry import npcInstance

loot_table = {
    "minor_loot": 1,
    "medium_loot": 2,
    "great_loot": 3,
    "special_loot": 4}

def t_print(string, newline_before=False, newline_after=False, item_1=None, item_2=None, item_3=None, item_list=None, add_count=False, list_is_precoloured=False):
    """for formatting"""
    bg = "44"
    colourcode = "\033[0;32m"
    boldcode = "\033[1;32m"
    endcode = "\033[0m"
    start = end = ""
    if not string:
        print(f"[t_print(): Nothing to print: `{string}`]")
        return
    if newline_before:
        start = "\n"
    if newline_after:
        end = "\n"
    if item_1:
        item_1 = endcode + assign_colour(item_1, no_reset=True) + colourcode
        string = string.replace("item_1", item_1)
    if item_2:
        item_2 = endcode + assign_colour(item_2, no_reset=True) + colourcode
        string = string.replace("item_2", item_2)
    if item_3:
        item_3 = endcode + assign_colour(item_3, no_reset=True) + colourcode
        string = string.replace("item_3", item_3)
    if item_list:
        list_string = ""
        for item in item_list:
            if list_is_precoloured:
                item_entry = endcode + item + colourcode
            else:
                item_entry = endcode + assign_colour(item, no_reset=True) + colourcode
            list_string = list_string + (f"{colourcode}, " if list_string else "") + ("1x " if add_count else "") + item_entry
        string = string.replace("item_list", list_string)
    if "_" in string:
        import re
        matches = re.findall(r"_\w*_", string)
        #print(f"regex matches: {matches}")
        for item in matches:
            string = string.replace(item, f"{boldcode}{item.replace("_", '')}{colourcode}")


    string = f"{start} {colourcode}##  " + string + f"  ##\033[0m{end}"
    print(string)

def give_item_to_npc(npc:npcInstance, trade_item:itemInstance):
    from env_data import locRegistry as loc
    from itemRegistry import registry

    #print(f"give_item_to_npc: `{trade_item}`")
    registry.by_location[loc.inv_place].remove(trade_item)
    trade_item.location = loc.npc_inv_place
    if loc.inv_place.items and trade_item in loc.inv_place.items:
        loc.inv_place.items.remove(trade_item)
    npc.inventory.add(trade_item)
    registry.move_item(trade_item, location=loc.npc_inv_place)
    trade_item.held_by = npc
    if not npc.will_not_sell or trade_item.name not in npc.will_not_sell:
        npc.trade_items.add(trade_item)

def take_item_from_npc(npc:npcInstance, purchase_item:itemInstance):
    if npc.inventory and purchase_item in npc.inventory:
        npc.inventory.remove(purchase_item)
    else:
        print(f"ITEM NOT IN NPC.INVENTORY. THIS IS AN UPSTREAM PROBLEM, ALL SELLABLE ITEMS MUST BE IN INVENTORY. {npc} / {purchase_item} \nvars: {vars(npc)}")
    if purchase_item in npc.trade_items:
        npc.trade_items.remove(purchase_item)
    from itemRegistry import registry
    from env_data import locRegistry as loc
    registry.move_item(purchase_item, location=loc.inv_place)
    loc.inv_place.items.add(purchase_item)
    purchase_item.held_by = None
    purchase_item.encountered = True
    #TODO: I need to get rid of the 'by_location' set adding. IT's just messy.
    registry.by_location[loc.inv_place].add(purchase_item)


def get_sellable(npc:npcInstance, loot_table, force_all=False):

    sellable_items = set()
    from itemRegistry import registry
    from env_data import locRegistry as loc
    if force_all or not hasattr(npc, "trade_intake"):
        items = set(i for i in registry.by_location.get(loc.inv_place) if registry.by_location.get(loc.inv_place) and "loot_type" in i.item_type)
        if items:
            children = set((child for child in i.children if not child.is_hidden) for i in items if hasattr(i, "children") and i.children and i.is_open)
            sellable_items = items|children
        return sellable_items
    for category, items in npc.trade_intake.items():
        # note: can be multiple categories. 'named and min cat, etc'
        #print(f"CATEGORY: {category} // items: {items}")
        if category == "named_only":
            items = set(i for i in registry.by_location[loc.inv_place] if registry.by_location.get(loc.inv_place) and i.name in items)
            if items:
                children = set((child for child in i.children) for i in items if hasattr(i, "children") and i.children and i.is_open)
                sellable_items = items|children

        if category == "loot_value":
            inv_items = [] # just placeholder
            for loot_val in items:
                for inst in inv_items:
                    if hasattr(inst, "loot_type") and inst.loot_type == loot_val and loot_table.get(inst.loot_type):
                        sellable_items.add(inst)

    #print(f"Returning sellable_items: {sellable_items}")
    return sellable_items

def make_print_list(trade_item):
    """returns a precoloured list of items with counts."""
    if not isinstance(trade_item, list):
        print(f"trade_item {trade_item} isn't a list, it shouldn't be in make_print_list.")
        return
    if len(trade_item) == 1:
        return f"a {assign_colour(trade_item[0])}"
    named = set()
    item_count = []
    for item in trade_item:
        if item.name in named:
            continue
        named.add(item.name)
        count = len(list(i for i in trade_item if i.name == item.name))
        item_count.append(assign_colour(f"x{count} {item.name}", noun=item))
    #print(f"ITEM COUNT: {item_count}")
    return item_count


def buy_item(npc, purchase_item, trade_value=None, trade_item=None):

    from misc_utilities import is_plural_noun
    if trade_value:
        from set_up_game import game
        if not game.gold:
            t_print("You don't have any gold to pay with.", newline_before = True, newline_after=True)
            return False
        elif game.gold < trade_value:
            t_print("You don't have enough gold to pay with.", newline_before = True, newline_after=True)
            return False
        else:
            t_print(f"You pay the item_1 item_2. The item_3 {is_plural_noun(purchase_item)} now in your inventory.", newline_before = True, newline_after=False, item_1=npc, item_2 = assign_colour(f"{trade_value} gold", colour="description"), item_3=purchase_item)
            game.gold -= trade_value
            npc.gold += trade_value
            return True

    elif trade_item:
        if isinstance(trade_item, list|set):
            held_print = ""
            for item in trade_item:
                give_item_to_npc(npc, item)
                #held_print = held_print + (", " if held_print else "") + assign_colour(f"1x {item.name}", noun=item)
            print_list = make_print_list(trade_item)
            t_print(f"You exchanged item_list for the item_2. The item_2 {is_plural_noun(purchase_item)} now in your inventory.", newline_before=True, newline_after=False, item_2=purchase_item, item_list=print_list, list_is_precoloured = True)
        else:
            give_item_to_npc(npc, trade_item)
            t_print(f"You exchanged the item_1 for the item_2. The item_2 {is_plural_noun(purchase_item)} now in your inventory.", newline_before=True, newline_after=False, item_1=trade_item, item_2=purchase_item, add_count=True)
        take_item_from_npc(npc, purchase_item)
        print()# extra newline to emphasise state change
        return True


def get_item_from_list(test, npc, printed_list, source):

    int_test = None
    try:
        int_test = int(test)
        print(f"INT_TEST: {int_test}")
    except:
        t_print(f"Which item do you want to sell to item_1?   [Enter the name of the item you want to trade, or hit enter to return to menu]", newline_after=True, item_1=npc)
        test = input("... ")
        if not test or test.lower() in ("none", "nothing"):
            return test
    if int_test and isinstance(int_test, int):
        if int_test <= len(source):
            print("About to fetch from list by index, may break because I'm exhausted")
            item = printed_list[int_test-1]
            if item:
                print(f"ITEM: {item}")
                print(f"source before: {source}")
                if isinstance(source, set):
                    source = list(source)
                    print(f"source_after: {source}")
                if len(source) == len(printed_list):
                    print("len source == len printed_list")
                    inst = source[int_test-1]
                    print(f"inst from source[int_test-10]: {inst}")
                    if inst.name in item: # because `item` has the assign_colour formatting, so direct matches don't work unless I stripped it first. NOTE: If I always alphabetise the sellable_items before printing, the order will always match. Maybe do that? Not sure.
                        print(f"Inst.name == item: item: {item} // inst: {inst}")
                        return inst
                for i in source: # loop to get one by the right name in case the above fails. Though if the above fails, it will kill the route so it probably wouldn't continue to try this loop anyway. Will see.
                    if i.name == item:
                        return i
            #test = input("... ")
            #if not test or test.lower() in ("none", "nothing"):
            #    return test

def get_item_to_sell(npc:npcInstance, sellable_items:list[itemInstance], held_items:list[itemInstance], value:int=None):
    selected_item = None
    if held_items:
        held_print = []
        for item in held_items:
            held_print.append(assign_colour(f"1x {item.name} (value: {item.trade_value})", noun=item))
            if item in sellable_items:
                sellable_items.remove(item)
        t_print(f"You are already trading item_list", item_list=held_print, list_is_precoloured=True, newline_after=True)

    #print(f"Value: {value}")
    if held_items:
        t_print(f"Which item do you want to add to the trade with item_1?", newline_after=True, item_1=npc)
    else:
        t_print(f"item_1 is willing to trade for these items: [Enter the name of the item you want to trade, or hit enter to return to menu]", newline_before=True, newline_after=True, item_1=npc)
    print_list = list(f"{assign_colour(item=f'  - {i.name}, value: {i.trade_value}', noun=i)}\n" for i in sellable_items)
    print(''.join(print_list))
    #else:
        #t_print(f"Which item do you want to sell to item_1?   ", newline_after=True, item_1=npc)
    #t_print("", newline_after=True)
    test = input("... ")
    if not test or test.lower() in ("none", "nothing"):
        return False
    if len(test) == 1:
        selected_item = get_item_from_list(test, npc, printed_list = print_list, source = sellable_items)
        if not selected_item or (selected_item and isinstance(selected_item, str) and selected_item in ("none", "nothing")):
            print(f"[No sold item or is str: `{selected_item}`]")
            return False
        print(f"sold_item by index: {selected_item}")

    #t_print("", newline_after=True)
    if not selected_item: # to allow for the idx without having to repeat this section
        selected_item = list(i for i in sellable_items if i.name.lower() in test.lower())
    if selected_item:
        if isinstance(selected_item, list):
            selected_item = selected_item[0]
    #print(f"SELECTED ITEM TO SELL: {selected_item}")
    return selected_item

def get_total_value(held_items, sold_item):
    total_val = 0
    if held_items:
        for item in held_items:
            total_val += item.trade_value

    total_val += sold_item.trade_value
    return total_val


def sell_item(sellable_items, npc:npcInstance, value = None, purchase_item = None):
    from misc_utilities import assign_colour
    test = True

    while test:
        held_items = []
        sold_item = None
        sold_item = get_item_to_sell(npc, sellable_items, held_items, value)

        if sold_item:
            if purchase_item:
                if sold_item.trade_value < purchase_item.trade_value:
                    trade_value = sold_item.trade_value
                    while trade_value < purchase_item.trade_value:
                        t_print(f"The item you want to trade for is worth {purchase_item.trade_value}, but the item you're offering is worth {sold_item.trade_value}. You can add another item to the trade if you still want to purchase the item_1.", item_1 = purchase_item)
                        held_items.append(sold_item)
                        sold_item = get_item_to_sell(npc, sellable_items, held_items, value)
                        if not sold_item:
                            return False
                        total_trade_value = get_total_value(held_items, sold_item)
                        if total_trade_value > purchase_item.trade_value:
                            t_print("What you're offering is worth more than what item_1 is selling. Do you want to continue with the trade?", item_1=npc)
                            test = input()
                            if test.lower() not in ("y", "yes", "continue"):
                                return False
                        trade_value = total_trade_value
                        held_items.append(sold_item)
                    if held_items:
                        sold_item = held_items

                from interactions.conversations import npc_colour
                if isinstance(sold_item, itemInstance):
                    sold_item = list((sold_item))
                responded = False
                if npc.special_responses:
                    #print("npc has special responses")
                    for entry, data in npc.special_responses.items():
                        #print(f"entry: {entry} / data: {data} / old_item: {sold_item}")
                        match = list(i for i in sold_item if i.name in entry)
                        if match:
                            import random
                            print("   ", npc_colour(npc, random.choice(npc.special_responses[entry])))
                            responded = True
                            break

                if not responded:
                    print("   ", npc_colour(npc, npc.approval))

                if buy_item(npc, purchase_item, None, sold_item):
                    #print("after if buy_item ln 286")
                    #print(f"Trade successful: gave {npc.name} the {sold_item.name} in exchange for the {purchase_item.name}")
                    if isinstance(sold_item, list):
                        for item in sold_item:
                            if item in sellable_items:
                                sellable_items.remove(item)
                    else:
                        sellable_items.remove(sold_item)
                    return True
                else:
                    return False
            else:
                if not value:
                    if hasattr(purchase_item, "loot_type"):
                        value = loot_table.get(purchase_item.loot_type, 1)
                    elif hasattr(npc, "default_trade_value"):
                        value = npc.default_trade_value
                    else:
                        value = 1
                t_print(f"item_1 will give you item_2 for this item. Do you want to make this trade?", newline_before=True, newline_after=True, item_1=npc, item_2=assign_colour(f"{value} gold", colour="description"))
                test=input("... ")
                if test in ("y", "yes"):
                    give_item_to_npc(npc, sold_item)
                    from set_up_game import game
                    game.gold += value
                    t_print(f"You recieve item_1 in exchange for the item_2.", item_1=assign_colour(f"{value} gold", colour="description"), item_2=sold_item, newline_before=True, newline_after=False)
                    print() # like selling items, add an extra newline to make it clearer something has changed.
                    return True
                t_print("You decide to keep the item_1 for now.", item_1 = sold_item, newline_before=True)
                return False
        else:
            t_print("Sorry, try again?", newline_after=True)
    else:
        return False


def trade_with(npc:npcInstance):

    from misc_utilities import assign_colour
    from itemRegistry import registry
    from interactions.conversations import affect

    if npc.trade_start:
        print("\n   ", affect(npc, npc.trade_start))
    t_print(f" --- Entering trade with {npc.name} ---", newline_before=True)
    npc.encounter("Encountered in trade_with")
    end_text = f" -- Ending trade with item_1 --"
    while True:
        t_print("Do you want to _buy_ or _sell_?", newline_before=True, newline_after=True)
        test = input("... ")
        if not test or (test and test in ("no", "n")) or (test and test in ("y", "yes")):
            if test and test in ("no", "n"):
                print()
                "Ending trade."
                break
            if test and test in ("y", "yes"):
                t_print("Do you want to _buy_ or _sell_?", newline_before=True, newline_after=True)
                test = input("... ")

            else:
                t_print("Do you want to leave? Enter nothing to end trade.", newline_before=True)#, newline_after=True)
                test = input("\n... ")
                if not test or test in ("y", "yes"):
                    print("Ending trade.")
                    break
                if test and test in ("n", "no"):
                    t_print("Do you want to _buy_ or _sell_?", newline_before=True, newline_after=True)
                    test = input("... ")

        if "buy" in test or test == "b":
            if not npc.trade_items:
                t_print(f"item_1 doesn't have items to trade. Do you want to sell anything?", item_1=npc, newline_before=True, newline_after=True)
                test = input("... ")
                if test in ("y", "yes"):
                    test = "sell"
            else:
                t_print("What do you want to look at?", newline_before = True, newline_after = True)
                printlist = list(f"{assign_colour(f'  - {i if isinstance(i, str) else i.name}')}\n" for i in npc.trade_items)
                for item in npc.trade_items:
                    item.encounter("Encountered as npc.trade_items")
                print(''.join(printlist))

                while test:
                    test = input("... ")
                    if test and npc.trade_items:
                        item = list(i for i in npc.trade_items if i.name.lower() in test.lower())
                        if item:
                            item = item[0]
                            print(f"\n   {assign_colour(registry.describe(item, caps=True), colour="description")}\n")
                            t_print("Do you want to buy the item_1?", item_1=item, newline_after=True)
                            test = input("...")
                            if test in ["y", "yes", "buy", "b"]:
                                if item.trade_value and item.trade_value != 1:
                                    value = item.trade_value
                                elif hasattr(item, "loot_type"):
                                    value = loot_table.get(item.loot_type, 1)
                                elif hasattr(npc, "default_trade_value"):
                                    value = npc.default_trade_value
                                else:
                                    value = 1
                                trade_done = False
                                while not trade_done:
                                    sellable_items = get_sellable(npc, loot_table)
                                    from set_up_game import game
                                    if not game.gold and not sellable_items:
                                        extra = ", but you don't have anything they want.\n"
                                        test = None
                                    else:
                                        extra = ". Do you want to pay in _gold_, or _trade_?"
                                    t_print(f"item_1 will sell this for item_2{extra}", item_1=npc, item_2 = assign_colour(f"{value} gold", colour="description"), newline_before=True)
                                    if not test:
                                        trade_done = True
                                        break
                                    while True:
                                        test = input("\n... ")
                                        if test and "gold" in test.lower():
                                            if buy_item(npc, item, value):
                                                print() # I thought I already added an extra line after purchases but I guess not?
                                                test = None
                                                trade_done = True
                                                break
                                            test = None
                                            break

                                        elif test and "trade" in test.lower():
                                            # currently all items are of equal value when selling. will work on it later.
                                            if not sellable_items:
                                                t_print(f"You don't have anything item_1 wants.", newline_after=True, item_1=npc)
                                                test = None
                                                break
                                            else:
                                                t_print(f"Which item do you want to trade to item_1 for the item_2?", newline_before=True, item_1 = npc, item_2 = item)
                                                while True:
                                                    if sell_item(sellable_items, npc, purchase_item=item):
                                                        #print("after if sell_item at 420")
                                                        sellable_items = get_sellable(npc, loot_table)
                                                        if not sellable_items:
                                                            t_print(f"You don't have anything else item_1 wants.", newline_after=True, item_1=npc)
                                                            test = None
                                                            trade_done = True
                                                        else:
                                                            test = "buy"
                                                        break
                                                    else:
                                                        break
                                                break
                                        else:
                                            if test:
                                                t_print("Sorry, what do you mean? Press enter to return to menu or enter your selection again.")
                                            else:
                                                break
                                    break
                                break
                            else:
                                if test and test not in ("n", "no", "nope"):
                                    t_print("Sorry, what?", newline_after=True)
                                    test = "buy"
                                    break
                    if test and test not in ("y", "n", "yes", "no"):
                        t_print("Sorry, what?", newline_before=True, newline_after=True)

        if test and ("sell" in test or test == "s"):
            sellable_items = get_sellable(npc, loot_table)
            if not sellable_items:
                t_print(f"It seems you don't have anything item_1 wants.", newline_before=True, newline_after=True, item_1=npc)
            else:
                #printlist = list(f"  - {i.name}\n" for i in sellable_items)
                while True:
                    if sell_item(sellable_items, npc):
                        sellable_items = get_sellable(npc, loot_table)
                        trade_done = True
                        if not sellable_items:
                            t_print(f"You don't have anything else item_1 wants.", item_1=npc, newline_after=True)
                            test = None
                            break
                        test = "buy"
                    else:
                        break

        if test and test not in ("sell", "buy", "s", "b", "trade"):
            if test == "trade":
                t_print(end_text, item_1 = npc, newline_after=True)
                if npc.trade_end:
                    print("\n   ", affect(npc, npc.trade_end), "\n")
                return

            t_print(f"I'm not sure what you mean by `{test}`.", newline_before=True)
            test = input("\n... ")

    t_print(end_text, item_1 = npc, newline_after=True)
    if npc.trade_end:
        print("\n   ", affect(npc, npc.trade_end), "\n")
