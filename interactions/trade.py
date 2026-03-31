#trade.py

from npcRegistry import npcInstance

loot_table = {
    "minor_loot": 1,
    "medium_loot": 2,
    "great_loot": 3,
    "special_loot": 4}


def get_sellable(npc, loot_table, force_all=False):

    sellable_items = set()
    if force_all or not hasattr(npc, "trade_intake"):
        print("Here just select all items in inv + containers with a loot value other than 'starting'")
        return sellable_items
    for category, items in npc.trade_intake.items():
        # note: can be multiple categories. 'named and min cat, etc'
        if category == "named_items":
            print("here get items from inv and accessible containers in inv to check if any named items")
            for itemname in items:
                sellable_items.add("named_item_instance")

        if category == "loot_value":
            print("here get items in inv and inv cont as above to check to loot val")
            inv_items = [] # just placeholder
            for loot_val in items:
                for inst in inv_items:
                    if hasattr(inst, "loot_type") and loot_table.get(inst.loot_type):
                        sellable_items.add(inst)

    return sellable_items

def buy_item(npc, purchase_item, trade_value=None, trade_item=None):

    if trade_value:
        from set_up_game import game
        if not game.gold:
            print("You don't have any gold to pay with.")
            return True
        elif game.gold < trade_value:
            print("You don't have enough gold to pay with.")
            return True
        else:
            print(f"You pay the {npc.name}.")
            game.gold -= trade_value
            return True

    elif trade_item:
        print("remove trade item from player, add it to npc. Remove purchase item from npc, add to player inv.")
        return True



def sell_item(sellable_items, npc, value = None, purchase_item = None):

    test = input("\n")
    if test:
        sold_item = (i for i in sellable_items if i.name.lower() in test.lower())
        if sold_item:
            if purchase_item:
                print("Here you need to remove the item from inv/container and add to npc's inv and add the recieving item to inv.")
                if buy_item(npc, purchase_item, None, sold_item):
                    print(f"Trade successful: gave {npc.name} the {list(sold_item)[0].name} in exchange for the {purchase_item}")
                    return True
                print("Here we apply the given value to the player's game.gold. and remove the item from inv")
            else:
                if not value:
                    if hasattr(purchase_item, "loot_type"):
                        value = loot_table.get(purchase_item.loot_type, 1)
                    elif hasattr(npc, "default_trade_value"):
                        value = npc.default_trade_value
                    else:
                        value = 1
                print(f"here we add the value {value} to the player's gold")
        else:
            print("Sorry, try again?")
    else:
        return True


def trade_with(npc:npcInstance):

    from misc_utilities import assign_colour
    from itemRegistry import registry
    print(f"Entering trade with {npc}")
    items_to_trade = npc.trade_items if npc.trade_items else None

    while True:
        if not items_to_trade:
            print(f"{npc.name} doesn't have items to trade. Do you want to sell anything?\n")

        else:
            print("What do you want to look at?.\n")
            printlist = list(f"  - {i if isinstance(i, str) else i.name}\n" for i in items_to_trade)
            print(''.join(printlist), "\n")

        test = input("\n")
        if test and items_to_trade:
            item = list(i for i in items_to_trade if i.name.lower() in test.lower())
            if item:
                print("item found.")
                item = item[0]
                print(f"\n   {assign_colour(registry.describe(item, caps=True), colour="description")}")
                test = input("Do you want to buy?\n")
                if test in ["y", "yes"]:
                    if hasattr(item, "loot_type"):
                        value = loot_table.get(item.loot_type, 1)
                    elif hasattr(npc, "default_trade_value"):
                        value = npc.default_trade_value
                    else:
                        value = 1
                    while True:
                        print(f"{npc.name} will sell this for... around {value}. Do you want pay in gold, or trade?")
                        test = input("\n")
                        if test and "gold" in test.lower():
                            if buy_item(npc, item, value):
                                break

                        elif test and "trade" in test.lower():
                            if npc.trade_intake:
                                sellable_items = get_sellable(npc, loot_table)
                                # currently all items are of equal value when selling. will work on it later.
                                if not sellable_items:
                                    print(f"You don't have anything {npc.name} wants.")
                                    break
                                else:
                                    print(f"Which item do you want to trade to {npc.name} for the {item}?")
                                    while True:
                                        if sell_item(sellable_items, npc, purchase_item=item):
                                            break
                        else:
                            print("Press enter to exit while loop, anything else to continue.")
                            test = input()
                            if not test:
                                break


        elif test:
            if npc.trade_intake:
                sellable_items = get_sellable(npc, loot_table)
                if not sellable_items:
                    print(f"It seems you don't have anything the {npc.name} wants.")
                else:
                    printlist = list(f"  - {i.name}\n" for i in sellable_items)
                    print(printlist, "\n")
                    print(f"Which item do you want to sell to {npc.name}?")
                    while True:
                        if sell_item(sellable_items, npc):
                            break


        else:
            print("Do you want to leave? Enter nothing or `yes` to end trade.")
            test = input()
            if not test or test in ("y", "yes"):
                break

    print(f"leaving trade with {npc}")
