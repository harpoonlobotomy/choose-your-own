#meta_commands.py Place to centralise all meta commands except the baseline logger/args. Item data visibility, editing item/env data, etc, all comes through here.

from itemRegistry import ItemInstance, cardinalInstance
from item_dict_gen import CARDINALS
from printing import print_green, print_blue, print_yellow, print_col

nulls = ("", None)
def yes_test(string=""):
    test = input(string)
    if test in ("y", "yes"):
        return 1

def select_noun(noun_name=None):

    noun_instance = None
    from itemRegistry import registry

    if not noun_name:
        while not noun_name:
            noun_name = input("Please enter a noun name:  ")
            if not noun_name:
                print(f"Available nouns: {list(registry.by_name)}")

    print(f"Finding instance for `{noun_name}`...")


    while True:
        noun_instances = registry.instances_by_name(noun_name)
        if not noun_instances:
            print(f"No nouns by the name `{noun_name}` could be found.\nDo you want to try again? Enter a noun name, or 'cancel' to exit meta control.")
            noun_name = input()
            if noun_name == 'cancel':
                break
        else:
            break

    if isinstance(noun_instances, list) and len(noun_instances)>1:
        print(f"There are {len(noun_instances)} instances with this name.\n")
        print(noun_instances)
        print("Do you want a specific instance, or will any do?")
        test = input("Press enter to default to the first option, or enter 'loc' to choose by item location, or 'inv' to choose from inventory items.\n")
        if "loc" in test:
            location = input("Please enter the location:\n")
            from env_data import locRegistry
            if locRegistry.place_by_name(location):
                for noun in noun_instances:
                    if noun.location.place == locRegistry.place_by_name(location):
                        print(f"{noun} is in {noun.location}")
                        noun_instance = noun
                # for card in CARDINALS:
                #     cardinal_inst = locRegistry.by_cardinal_str(card, location)
                #     if cardinal_inst:
                #             if noun.location ==
                # noun in
        if "inv" in test:
            from misc_utilities import from_inventory_name
            inv_instance = from_inventory_name(noun_name)
            if inv_instance and inv_instance in noun_instances:
                noun_instance = inv_instance
            else:
                print(f"Could not find {noun_name} in the inventory.")

    elif isinstance(noun_instances, list):
        noun_instance = noun_instances[0]

    else:
        noun_instance = noun_instances

    print_blue(f"Instance found for {noun_name}: {noun_instance}", invert=True)

    return noun_instance

def edit_noun(noun):

    if not noun:
        return

    if not isinstance(noun, ItemInstance):
        if isinstance(noun, str):
            noun = select_noun(noun)

    fields_to_pop = set()
    new_vars = {}
    print_blue(" :: noun attributes :: ")
    from pprint import pprint
    pprint(vars(noun))
    if yes_test("\n Do you want to edit these attributes?\n"):
        test = input("\nType an attribute name here, or 'cancel' to cancel, or nothing to edit one by one.\n")
        if test in vars(noun):

            def edit_single_field(noun, field, new_vars, fields_to_pop):
                if hasattr(noun, field):
                    print(f"Editing `{field}`:")
                    test = input(f"Please enter the new value for {noun.name}//{field}, type 'delete' to remove this field, or nothing to cancel.\n")
                    if test in ("del", "delete"):
                        fields_to_pop.add(field)
                    elif test != "" and test != None:
                        new_vars[field] = test
                else:
                    print(f"{field} is not a valid field. \n{vars(noun)}\n")

                return new_vars, fields_to_pop

            while True:
                new_vars, fields_to_pop = edit_single_field(noun, test, new_vars, fields_to_pop)
                test = input("Do you want to edit another field? If yes, enter it here.\n")
                if test in ("", None, "no", "n"):
                    print("Editing complete.")
                    print(f"New vars: {new_vars}, fields_to_pop: {fields_to_pop}")
                    break

        elif test == "cancel":
            return

        else:
            for item in vars(noun):
                #print()
                test = input(f"Field: `{item}`. Type the new value, 'delete' to remove it, or enter to continue.\n")
                if test in ("del", "delete"):
                    fields_to_pop.add(item)
                elif test != "" and test != None:
                    new_vars[item] = test

        if new_vars or fields_to_pop:
            print("The following change(s) will be applied if you type 'yes': ")
            if new_vars:
                pprint(new_vars)
            if fields_to_pop:
                print("These fields will be deleted:")
                print(fields_to_pop)
            if yes_test():
                for item in new_vars:
                    setattr(noun, item, new_vars[item])
                for item in fields_to_pop:
                    delattr(noun, item)

                print(f"The updated attributes for {noun.name}: ")
                pprint(vars(noun))

            main_json = r"dynamic_data\items_main.json"
            generated_json = r"dynamic_data\generated_items.json"

            test=input("Do you want update this item in generated_items or items_main?\n")
            if "main" in test:
                print(f"Updating {noun}'s attributes in {main_json}")
                json_file = main_json
            elif "gen" in test:
                print(f"Updating {noun}'s attributes in {generated_json}")
                json_file = generated_json
            else:
                return

            if json_file:
                import json
                with open(json_file, 'r') as file:
                    existing_data = json.load(file)
                if existing_data.get(noun.name):
                    print(f"{noun.name} already has an entry in {json_file}. Do you want to overwrite")
                    print(existing_data[noun.name])
                    print(f"with {vars(noun)}\n?")
                    if not yes_test():
                        print(f"Ending without updating {json_file}")
                        return

                for item in list(vars(noun)):
                #for item, value in vars(noun).items():
                    if item in ("location", "starting_location", "id"):
                        delattr(noun, item)
                    else:
                        if not isinstance(vars(noun).get(item), str|list|dict|bool):
                            setattr(noun, item, str(vars(noun).get(item)))
                        if isinstance(vars(noun).get(item), dict):
                            for val, child in vars(noun).get(item).items():
                                if not isinstance(child, str|list|dict|bool):
                                    setattr(noun, val, str(child))

                print(f"Final check before writing to {json_file}:\n")
                pprint(vars(noun))
                if yes_test(f"\nType 'yes' to update {json_file}\n"):
                    existing_data[noun.name] = vars(noun)
                    with open(json_file, 'w') as file:
                        json.dump(existing_data, file, indent=2)
                    print(f"{json_file} has been updated.")

def select_location():

    from env_data import locRegistry

    location = input("Enter the name of the location you wish to edit:  ")
    place = None

    while not place:

        if location == "":
            location = input(f"Please enter a location name. Options: {locRegistry.by_name}. Enter nothing again to exit location editing.")
            if location == "":
                return

        place = locRegistry.place_by_name(location)
        if place:
            #print(f"\n{place} found.")
            return place
        print(f"Could not find location entry for {location}.")
        location = ""

def dump_data(new_data, json_file):
    import json
    with open(json_file, 'w') as file:
        json.dump(new_data, file, indent=2)
    print(f"{json_file} has been updated.")

def update_json(loc_dict):

    print("Changes made to loc_data")
    if yes_test("Do you want to show the loc_data now?\n"):
        from pprint import pprint
        pprint(loc_dict)
    test = input("Do you want to save these changes to loc_data, a temp file or none?\n")
    if test in nulls:
        print("Ending without editing JSON file(s).")
        return

    loc_data = "loc_data.json"
    temp_loc = r"dynamic_data\temp_loc.json"
    if test in ("loc", "main", loc_data):
        print(f"Applying these changes to {loc_data}")
        dump_data(loc_dict, loc_data)
    elif test in ("temp", "gen"):
        print(f"Applying these changes to {temp_loc}")
        dump_data(loc_dict, temp_loc)



def loc_dict_edits(loc_dict, edit_dict):

    if not edit_dict or edit_dict == {}:
        print("No edits to make to loc_data.json.")
        #update_json(loc_dict)
        return

    for place in edit_dict:
        for cardinal in edit_dict[place]:
            if cardinal not in CARDINALS:
                print("Will be a location description, process separately.")

            if "item_desc" in edit_dict[place][cardinal]:
                for item in edit_dict[place][cardinal]["item_desc"]:
                    if item == "delete":
                        loc_dict[place][cardinal]["item_desc"].pop(item)

                    elif item == "add":
                        for entry in edit_dict[place][cardinal]["item_desc"]["add"]:
                            loc_dict[place][cardinal]["item_desc"][entry] = edit_dict[place][cardinal]["item_desc"]["add"][entry]
                    else:
                        if loc_dict[place][cardinal]["item_desc"].get(item):
                            loc_dict[place][cardinal]["item_desc"][item] = edit_dict[place][cardinal]["item_desc"][item]

            if "items" in edit_dict[place][cardinal]:
                for item in edit_dict[place][cardinal]["items"]:
                    print(f"item: {item}")
                    if item == "delete":
                        for itemname in edit_dict[place][cardinal]["items"][item]:
                            if loc_dict[place][cardinal]["items"].get(itemname):
                                loc_dict[place][cardinal]["items"].pop(itemname)
                    else:
                        for section in edit_dict[place][cardinal]["items"][item]:
                            print(f"section: {section}")
                            if section == "delete_field":
                                for element in edit_dict[place][cardinal]["items"][item]["delete_field"]:
                                    if loc_dict[place][cardinal]["items"].get(item) and loc_dict[place][cardinal]["items"][item].get(element):
                                        loc_dict[place][cardinal]["items"][item].pop(element)
                                        print(f"`{element}` removed from items>{item}")

                            else:
                                if loc_dict[place][cardinal]["items"][item].get(section):
                                    loc_dict[place][cardinal]["items"][item][section] = edit_dict[place][cardinal]["items"][item]


    update_json(loc_dict)

def edit_item_text(item, local_edits, long_dict, category):

    edit = 0

    print(f"`{item}`: `{long_dict[item]}`")
    if category == "item_desc":
        new_desc = input("If you want to edit this item description, enter it here. If you want to edit the item name, enter the item name. Otherwise, enter nothing.")
    else:
        new_desc = input("If you want to edit this item, enter it here. If you want to edit the item name, enter the item name. Type 'delete' to remove it. Otherwise, enter nothing.\n")

    if new_desc in nulls:
        return
    if new_desc == "delete":
        local_edits.setdefault(category, {}).setdefault("delete", list()).append(item)
        edit += 1
    elif new_desc == item:
        new_name = input(f"Editing item name `{item}`. Please enter new item name:")
        if new_name in nulls:
            print("No new name entered, continuing with no change.")
            return
        if yes_test(f"New name for {item} will be {new_name}. Enter 'yes' to confirm"):
            #edit_dict.setdefault(cardinal.place, {}).setdefault(cardinal, {}).setdefault("item_desc", {}).setdefault("delete", list())
            #edit_dict[cardinal.place][cardinal]["item_desc"]["delete"].append(item)
            #edit_dict[cardinal.place][cardinal]["item_desc"].setdefault("add", {}).update({new_name: long_dict[item]})
            #print("Item name edited.")
            local_edits.setdefault(category, {}).setdefault("delete", list())
            local_edits[category]["delete"].append(item)
            local_edits[category].setdefault("add", {}).update({new_name: long_dict[item]})
            print("Item name edited.")
            return 1

    else:
        if category == "item_desc":
            new_desc = input(f"Editing item description for `{item}`. Please enter new description:")
            if new_desc in nulls:
                print("No new description entered, continuing with no change.")
                return
            if yes_test(f"New description for {item} will be {new_desc}. Enter 'yes' to confirm"):
                local_edits.setdefault("item_desc", {})[item] = new_desc
                print("Item description edited.")
                return 1
        else:
            edit = 0
            for field in long_dict:
                if yes_test(f"{item} field: `{field}`. Edit this field?"):
                    new_input = input("Enter 'delete' to remove the field, a new value to replace the value, or nothing to continue without changes.")
                    if new_input in nulls:
                        continue
                    if new_input == "delete":
                        local_edits[category].setdefault(item, {}).setdefault("delete_field", list).append(item)
                        edit += 1
                    else:
                        local_edits[category].setdefault(item, {})[field] = new_input
                        edit += 1

    if edit:
        return edit


def edit_description_text(existing_text):

    print(f"Existing text: {existing_text}")
    new_text = input("Please enter the new description.\n\n")
    if new_text in nulls:
        print("No description entered, returning.")
        return
    if yes_test("Is this correct? \n\n"):
        return new_text


def edit_card_desc(cardinal:cardinalInstance):

    place = cardinal.place.name
    cardinal = cardinal.name
    edit_dict = {}
    edits = 0
    import json
    loc_items_json = "loc_data.json"
    with open(loc_items_json, 'r') as loc_items_file:
        loc_dict = json.load(loc_items_file)

    print(f"\n Editing descriptions for {cardinal} {place} ::\n")

    if loc_dict.get(place):
        #print(loc_dict.get(place))
        if loc_dict[place].get("descrip"):
            print(f"General area description:\n")
            print(f"'{loc_dict[place].get('descrip')}`")
            test = yes_test("Do you want to edit this description?\n")
            if test:
                new_text = edit_description_text(loc_dict[place].get("descrip"))
                if new_text:
                    edits += 1
                    edit_dict.setdefault(place, {})["descrip"] = new_text

            if loc_dict[place].get(cardinal):
                local_edits = edit_dict.setdefault(place, {}).setdefault(cardinal, {})

                if loc_dict[place][cardinal].get("item_desc"):
                    print(f"Item descriptions:\n")
                    long_dict = loc_dict[place][cardinal]["item_desc"]

                    if long_dict:
                        for item in long_dict:
                            edited = edit_item_text(item, local_edits, long_dict, category="item_desc")
                            if edited:
                                edits += 1
                        print("\nFinished location-description items.\n")

                if loc_dict[place][cardinal].get("items"):
                    print(f"Location item data:\n")
                    simple_items = loc_dict[place][cardinal]["items"]
                    if simple_items:
                        for item in simple_items:
                            print(f"Editing {item}")
                            edited = edit_item_text(item, local_edits, simple_items, category="items")
                            if edited:
                                edits += 1
                        print("\nFinished item-data location items.\n")
    else:
        print(f"No location data for {cardinal.place}")

    #if edit_dict:
    if edits:
        loc_dict_edits(loc_dict, edit_dict)
    else:
        print("\nNo edits made.\n")

def edit_card_items(cardinal:cardinalInstance):

    import json
    loc_items_json = "loc_data.json"
    with open(loc_items_json, 'r') as loc_items_file:
        loc_dict = json.load(loc_items_file)

    print(f"\n Editing items in {cardinal.place_name}")


def edit_cardinal(cardinal:cardinalInstance):

    print(f"\nEditing {cardinal.place_name}.\n")
    edit_card_desc(cardinal)

    #task = input("Do you want to: \n1: Edit cardinal descriptions/items\n2: Cancel\n")
    #if task in ("1", "2"):
    #    if task == "1":
    #        print(f"\nEditing descriptions for {cardinal.place_name}.")
    #        return 1
#
    #    else:
    #        print("\nReturning to previous menu.")
    #        return 0


def edit_location(location):
    if location == "":
        return

    print(f"Editing location {location.name} / {location}\n")
    cardinals = location.cardinals
    card = None

    while not card:

        card = input(f"Enter the cardinal direction you want to edit. Cardinals for {location.name}:\n{list(cardinals)}\n")
        if card == "":
            card = input(f"Enter nothing again to exit editing. Otherwise, please enter a cardinal name.\n")
            if card == "":
                print(f"Ending editing of {location.name}.")
                return
        if card in list(cardinals):
            cardinal:cardinalInstance = cardinals.get(card)
            card = edit_cardinal(cardinal) # card == 0 if failed/return to choose cardinal again.
            if card:
                return
def do_other():

    print("Do you want to print all cardinals?")
    if yes_test():

        card_dict = {}

        from env_data import all_cardinals
        print(f"All cardinals: {all_cardinals}")
        for item in all_cardinals:
            card_dict.setdefault(item.place, list()).append(item)
            print(f"{item.id}: {item.place_name}")

        for place in card_dict:
            print(f"Place: {place}")
            for card in card_dict[place]:
                print(f"{card.id}, {card.name}")

    print("Do you want to print all items?")
    if yes_test():

        item_dict = {}
        from itemRegistry import all_items_generated, all_item_names_generated
        #print(f"All items: {all_items_generated}")
        for item in all_items_generated:
            item_dict.setdefault(item.name, set()).add(item)

        for item in item_dict:
            print(f"ITEM NAME: {item}")
            for inst in item_dict[item]:
                print(f"INSTANCE: {inst}")

        for item in all_item_names_generated:
            print(f"ITEM: {item}")

    print("Do you want to print all events?")
    if yes_test():
        from eventRegistry import events
        for state in events.by_state:
            print(f"State: {state}")
            for event in events.by_state[state]:
                print(f"EVENT: {event}")


def add_temp_to_loc_data():

    temp_file = r"dynamic_data\temp_loc.json"
    import json
    with open(temp_file, 'r') as file:
        temp_file_data = json.load(file)
    loc_data = "loc_data.json"
    dump_data(temp_file_data, loc_data)

def meta_control(input_format, noun=None, location=None, cardinal=None):
    print()
    print_green(" :::META CONTROL::: ", invert=True)

    if noun:
        edit_noun(noun)
    if location:
        edit_location(location)
    if cardinal:
        edit_cardinal(cardinal)

    print("\n")
    while True:
        print("\nWhat do you want to do?\n")
        test = input("\n1: See/edit an item\n2: See/edit a location\n3: See/edit an event\n4: Add temp location data to main loc_data file\n5: Other\nAnything else: Leave meta control\n\n")
        if test in ("1", "2", "3", "5"):
            if test == "1":
                edit_noun(select_noun())
            elif test == "2":
                edit_location(select_location())
            elif test == "3":
                print("Not implemented yet.")
                add_temp_to_loc_data()
            elif test == "5":
                print("Going to do_other")
                do_other()
            else:
                print("I haven't added anything here yet.")
                break
        else:
            break

    print_green("\n :: END META CONTROL :: \n")
    print()
    from misc_utilities import look_around
    look_around()


## "attributes noun" is something I was looking for previously. That's basically something I want for meta command. Instead of 'attributes noun', do 'meta noun', then 'attributes', or 'edit attr', or whatever.
