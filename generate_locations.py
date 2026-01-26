CARDINALS = ["north", "east", "south", "west"]

def edit_location_json():

    import json
    loc_items_json = "loc_data.json" ## Add these to a base class to stop having to reopen the json all the time. Any time the JSON is to be edited, edit the class-stored dict, and at end of runtime, then update the JSON.

    with open(loc_items_json, 'r') as loc_items_file:
        loc_items = json.load(loc_items_file)
        # combine the entries if they already exist. Don't know if I need this at all, I'm probably just doing it initially here.
        # OR, automatically grab items from env_data's loc items in item_desc, and add them here. That's probably a good one.

    edited_dict = {}
    if loc_items:
        for place in loc_items:
            edited_dict[place] = {}
            print(f"place: {place}")
            for cardinal in loc_items[place]:
                if cardinal in CARDINALS and loc_items[place][cardinal] != None:
                    #print(f"cardinal: {cardinal}")
                #loc_base[place][cardinal] = loc_dict[place][cardinal]
                    for flag in loc_items[place][cardinal]:
                        if flag == "alt_names":
                            edited_dict[place]["alt_names"] = loc_items[place][cardinal][flag]

                    edited_dict[place][cardinal] = loc_items[place][cardinal]
                    print(f"loc_items[place][cardinal]:: {loc_items[place][cardinal]}")
                    if not loc_items[place][cardinal].get("items"):
                        edited_dict[place][cardinal]["items"] = {"": {"description": None, "is_hidden": False}} # empty template. Adding is_hidden here so I have a straightforward location-specific hidden flag, makes sense. Everything else can be from item gen or item_defs.
                elif cardinal == "alt_names":
                    edited_dict[place]["alt_names"] = loc_items[place][cardinal]
            #if not loc_items[place].get("alt_names"):
            print(f"loc_items[place].get('descrip'): {loc_items[place].get('descrip')}")
            edited_dict[place]["descrip"] = loc_items[place].get("descrip")

            edited_dict[place]["alt_names"] = (loc_items[place].get("alt_names") if loc_items[place].get("alt_names") != None else [])

            #if not loc_items[place].get("descrip"):
            #edited_dict[place]["descrip"] = (loc_items[place].get("descrip") if loc_items[place].get("descrip") != None else "")

        with open(loc_items_json, 'w') as loc_items_file:
            json.dump(edited_dict, loc_items_file, indent=2)
        print(f"Written to {loc_items_json}")


def edit_descriptions_in_cardinal(card, loc_dict_entry, name):
    print(f"The format for cardinal descriptions is : ['generic'] + [item(s)], or ['generic'] + ['no_items']")

    items = {}

    generic = input("Enter 'generic: \n")
    if generic:
        items["generic"] = generic
    while True:
        item_name = input("Enter 'item name', or nothing to continue: \n")
        if item_name:
            item_desc = input(f"Enter the scene descriptor for {item_name}.\n")
            items[item_name] = item_desc
        else:
            break
    no_items = input("Enter the text for no_items: \n")
    items["no_items"] = no_items

    from pprint import pprint
    pprint(f"New cardinal entry for {name}: {items}")
    loc_dict_entry[card]["item_desc"] = items
    return loc_dict_entry


def edit_all_lines_in_cardinal(card, loc_dict_entry, name):
    print()


def edit_items_in_cardinal(cardinal, loc_dict_entry, name):

    card = loc_dict_entry.get(cardinal)
    if not card.get("items"):
        card["items"] = {}
    while True:
        print(f"Enter item name to add to {name} {cardinal}")
        print("Or add multiple names at once, with spaces between.")
        test = input()
        if " " in test:
            test = test.replace(",", "")
            parts = test.split(" ")
            print("Do you want to add descriptions to any of these items?")
            trial = input()
            if trial in ("y", "yes"):
                for part in parts:
                    print(f"Enter a description for {part}")
                    trial = input()
                    print(f"Description stored for {part}")
                    card["items"].update({part:{"description": trial, "is_hidden": False}})

            else:
                for part in parts:
                    card["items"].update({part:{"description": "", "is_hidden": False}})
        if test in ("", None):
            break
        print(f"Enter to add without description, or 'desc'/'description' to add a description.")
        trial = input()
        if trial in ("desc", "description"):
            print(f"Please enter the description you want to add for {test}:")
            trial = input()
            print(f"Description stored for {test}")
            card["items"].update({test:{"description": trial, "is_hidden": False}})
        else:
            card["items"].update({test:{"": trial, "is_hidden": False}})

        print(f"loc_dict_entry: {loc_dict_entry}")



def change_loc_data(loc_dict_entry, name, cardinal_no):
    cardinal = None
    #new_loc_dict[loc_name]
    print("Do you want to add [items], edit cardinal [descriptions], or peruse [all] fields?")
    test = input()

    if cardinal_no != 1:
        print("Do you want to edit one cardinal, or all? If one, enter that cardinal.")
        trial = input()

    else:
        trial = "north"

    if trial in CARDINALS or trial == "all":
        cardinal = trial
    else:
        print("I needed a cardinal direction or 'all'. Enter a cardinal or 'all', or enter to cancel editing.")
        trial = input()
        if trial in CARDINALS or trial == "all":
            cardinal = trial

    if cardinal:
        if test == "items":
            if cardinal == "all":
                for card in CARDINALS:
                    loc_dict_entry = edit_items_in_cardinal(card, loc_dict_entry, name)
            else:
                loc_dict_entry = edit_items_in_cardinal(cardinal, loc_dict_entry, name)

        if test == "descriptions":
            if cardinal == "all":
                for card in CARDINALS:
                    loc_dict_entry = edit_descriptions_in_cardinal(card, loc_dict_entry, name)
            else:
                loc_dict_entry = edit_descriptions_in_cardinal(cardinal, loc_dict_entry, name)

        if test == "all":
            if cardinal == "all":
                for card in CARDINALS:
                    loc_dict_entry = edit_all_lines_in_cardinal(card, loc_dict_entry, name)
            else:
                loc_dict_entry = edit_all_lines_in_cardinal(cardinal, loc_dict_entry, name)



def generate_new_location(loc_name):

    cardinal_format = {
            "item_desc": {},
            "short_desc": "",
            "long_desc": "",
            "items": {
                "": {
                "description": "",
                "is_hidden": False
                }
            }
        }

    format = {
      "Test": {
        "alt_names": [],
        "north": {
            "item_desc": {},
            "short_desc": "",
            "long_desc": "",
            "items": {
                "": {
                "description": "",
                "is_hidden": False
                }
            }
        },
        "east": {
            "item_desc": {},
            "short_desc": "",
            "long_desc": "",
            "items": {
                "": {
                "description": "",
                "is_hidden": False
                }
            }
        },
        "south": {
            "item_desc": {},
            "short_desc": "",
            "long_desc": "",
            "items": {
                "": {
                "description": "",
                "is_hidden": False
                }
            }
        },
        "west": {
            "item_desc": {},
            "short_desc": "",
            "long_desc": "",
            "items": {
                "": {
                "description": "",
                "is_hidden": False
                }
            }
        },
        "descrip": ""
        }
    }

    new_loc_dict = {}
    new_loc_dict.setdefault(loc_name, {})
    cardinal_no = input(f"How many cardinals should {loc_name} have?  >>  ")
    if int(cardinal_no) < 4:
        cardinal_number = int(cardinal_no)
        for card in CARDINALS:
            if cardinal_number == 0:
                break
            new_loc_dict[loc_name][card] = cardinal_format
            cardinal_number -= 1
    else:
        new_loc_dict = {}
        new_loc_dict[loc_name] = format["Test"]

    descr = input(f"Enter a description for {loc_name}. If nothing is entered, will default to `f'It's a PPP{loc_name}EEE.`")
    if descr:
        new_loc_dict[loc_name]["descrip"] = descr
    else:
        new_loc_dict[loc_name]["descrip"] = f"It's a PPP{loc_name}EEE."

    change_loc_data(new_loc_dict[loc_name], loc_name, int(cardinal_no))

    print(f"new_loc_dict: {new_loc_dict[loc_name]}")
    import json
    loc_data_json = "loc_data.json"
    with open(loc_data_json, 'r') as loc_data_file:
        loc_dict = json.load(loc_data_file)

    if loc_dict.get(loc_name):
        print(f"Location {loc_name} already exists. Press y to replace, otherwise skip and leave JSON unchanged.")
        test = input()
        if test in ("y", "yes"):
            loc_dict[loc_name] = new_loc_dict[loc_name]
    else:
        loc_dict[loc_name] = new_loc_dict[loc_name]

    with open(loc_data_json, 'w') as file:
        json.dump(loc_dict, file, indent=2)


    from env_data import add_new_loc
    add_new_loc(loc_name, reset_current=True)
    return new_loc_dict

if __name__ == "__main__":

    #edit_location_json()
    new_loc = input(f"Please enter desired location name: ")
    generate_new_location(new_loc)
