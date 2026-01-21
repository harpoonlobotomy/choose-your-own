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


def generate_new_location(loc_name):

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
    new_loc_dict[loc_name] = format["Test"]
    new_loc_dict[loc_name]["descrip"] = f"It's a PPP{loc_name}EEE."
    print(f"new_loc_dict: {new_loc_dict[loc_name]}")
    import json
    loc_data_json = "loc_data.json"
    with open(loc_data_json, 'r') as loc_data_file:
        loc_dict = json.load(loc_data_file)
    if loc_dict.get(loc_name):
        print("Location already exists. Press y to replace, otherwise skip and leave JSON unchanged.")
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
    generate_new_location("church")
