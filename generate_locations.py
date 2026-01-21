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

if __name__ == "__main__":

    edit_location_json()
