#meta_commands.py Place to centralise all meta commands except the baseline logger/args. Item data visibility, editing item/env data, etc, all comes through here.

main_json = r"dynamic_data\items_main.json"
generated_json = r"dynamic_data\generated_items.json"

from itemRegistry import ItemInstance
from item_dict_gen import CARDINALS
from printing import print_green, print_blue, print_yellow, print_col

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

def meta_control(input_format, noun=None, location=None, cardinal=None):
    print_green(" :::META CONTROL::: ", invert=True)

    if noun:
        edit_noun(noun)

    while True:
        print("\nWhat do you want to do?\n")
        test = input("\n1: See/edit an item\n2: See/edit a location\n3: See/edit an event\n4: Leave meta control\n\n")
        if test in ("1", "2", "3"):
            if test == "1":
                edit_noun(select_noun())
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
