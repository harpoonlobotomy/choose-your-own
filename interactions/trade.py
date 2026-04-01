#trade.py

from itemRegistry import itemInstance
from misc_utilities import assign_colour
from npcRegistry import npcInstance

loot_table = {
    "minor_loot": 1,
    "medium_loot": 2,
    "great_loot": 3,
    "special_loot": 4}

def t_print(string, newline_before=False, newline_after=False, item_1=None, item_2=None):
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
    if "_" in string:
        import re
        matches = re.findall("_\w*_", string)
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
    trade_item.location = loc.no_place
    if loc.inv_place.items and trade_item in loc.inv_place.items:
        loc.inv_place.items.remove(trade_item)
    npc.inventory.add(trade_item)
    if not npc.will_not_sell or trade_item.name not in npc.will_not_sell:
        npc.trade_items.add(trade_item)

def take_item_from_npc(npc:npcInstance, purchase_item:itemInstance):
    if npc.inventory and purchase_item in npc.inventory:
        npc.inventory.remove(purchase_item)
    else:
        print(f"ITEM NOT IN NPC.INVENTORY. THIS IS AN UPSTREAM PROBLEM, ALL SELLABLE ITEMS MUST BE IN INVENTORY. {npc} / {purchase_item} \nvars: {vars(npc)}")
    npc.trade_items.remove(purchase_item)
    from env_data import locRegistry as loc
    purchase_item.location = loc.inv_place
    loc.inv_place.items.add(purchase_item)
    purchase_item.encountered = True
    from itemRegistry import registry
    registry.by_location[loc.inv_place].add(purchase_item)


def get_sellable(npc:npcInstance, loot_table, force_all=False):

    sellable_items = set()
    from itemRegistry import registry
    from env_data import locRegistry as loc
    if force_all or not hasattr(npc, "trade_intake"):
        items = set(i for i in registry.by_location.get(loc.inv_place) if registry.by_location.get(loc.inv_place) and "loot_type" in i.item_type)
        if items:
            children = set((child for child in i.children) for i in items if hasattr(i, "children") and i.children and i.is_open)
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

def buy_item(npc, purchase_item, trade_value=None, trade_item=None):

    if trade_value:
        from set_up_game import game
        if not game.gold:
            t_print("You don't have any gold to pay with.", newline_before = True, newline_after=True)
            return False
        elif game.gold < trade_value:
            t_print("You don't have enough gold to pay with.", newline_before = True, newline_after=True)
            return False
        else:
            t_print(f"You pay the {npc.name}.", newline_before = True, newline_after=True)
            game.gold -= trade_value
            npc.gold += trade_value
            return True

    elif trade_item:
        give_item_to_npc(npc, trade_item)
        take_item_from_npc(npc, purchase_item)
        from misc_utilities import is_plural_noun
        t_print(f"You exchanged the item_1 for the item_2. The item_2 {is_plural_noun(purchase_item)} now in your inventory.", newline_before=True, newline_after=False, item_1=trade_item, item_2=purchase_item)
        print()# extra newline to emphasise state change
        return True



def sell_item(sellable_items, npc, value = None, purchase_item = None):
    from misc_utilities import assign_colour
    test = True

    while test:
        t_print(f"item_1 is willing to trade for:", newline_after=True, item_1=npc)
        print_list = list(f"{assign_colour(item=f'  - {i.name}', noun=i)}\n" for i in sellable_items)
        print(''.join(print_list))
        t_print(f"Which item do you want to sell to item_1?   [Enter the name of the item you want to trade, or hit enter to return to menu]", newline_after=True, item_1=npc)
        #t_print("", newline_after=True)
        test = input("... ")
        if not test or test.lower() in ("none", "nothing"):
            return False
        sold_item = list(i for i in sellable_items if i.name.lower() in test.lower())
        if sold_item:
            sold_item = sold_item[0]
            if purchase_item:
                if buy_item(npc, purchase_item, None, sold_item):
                    #print(f"Trade successful: gave {npc.name} the {sold_item.name} in exchange for the {purchase_item.name}")
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
                test=input()
                if test in ("y", "yes"):
                    give_item_to_npc(npc, sold_item)
                    from set_up_game import game
                    game.gold += value
                    t_print(f"You recieve item_1 in exchange for the item_2.", item_1=assign_colour(f"{value} gold", colour="description"), item_2=sold_item, newline_after=True)
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
    end_text = f" -- Ending trade with item_1 --"
    while True:
        t_print("Do you want to buy or sell?", newline_before=True, newline_after=True)
        test = input("... ")
        if not test or test and test in ("no", "n"):
            if test and test in ("no", "n"):
                "Ending trade."
                break
            t_print("Do you want to leave? Enter nothing to end trade.", newline_before=True)#, newline_after=True)
            test = input("\n... ")
            if not test:
                print("Ending trade.")
                break

        if "buy" in test or test == "b":
            if not npc.trade_items:
                t_print(f"item_1 doesn't have items to trade. Do you want to sell anything?", item_1=npc, newline_before=True, newline_after=True)
                test = input("\n... ")
                if test in ("y", "yes"):
                    test = "sell"
            else:
                t_print("What do you want to look at?", newline_before = True, newline_after = True)
                printlist = list(f"{assign_colour(f'  - {i if isinstance(i, str) else i.name}')}\n" for i in npc.trade_items)
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
                                if hasattr(item, "loot_type"):
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
                                                t_print(f"Which item do you want to trade to item_1 for the item_2?", newline_before=True, newline_after=True, item_1 = npc, item_2 = item)
                                                while True:
                                                    if sell_item(sellable_items, npc, purchase_item=item):
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
                        if not sellable_items:
                            t_print(f"You don't have anything else item_1 wants.", item_1=npc, newline_after=True)
                            test = None
                            trade_done = True
                            break
                    else:
                        print()
                        break

        if test and test not in ("sell", "buy", "s", "b", "trade"):
            if test == "trade":
                t_print(end_text, item_1 = npc, newline_after=True)
                if npc.trade_end:
                    print("\n   ", affect(npc, npc.trade_end), "\n")
                return

            t_print(f"I'm not sure what you mean by `{test}`.")
            test = input("\n... ")

    t_print(end_text, item_1 = npc, newline_after=True)
    if npc.trade_end:
        print("\n   ", affect(npc, npc.trade_end), "\n")
