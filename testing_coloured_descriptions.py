from itemRegistry import registry
from env_data import locRegistry, loc_dict
from initialise_all import initialise_all
from misc_utilities import assign_colour

initialise_all()

loc = locRegistry.place_by_name("graveyard")
card = "east"

long_desc = []
def format_descrip(d_type="area_descrip", description=""):

    if d_type == "area_descrip":
        print(f"AREA DESCRIPTION:\n{description}")

        description = loc_dict[loc.name]["descrip"]
        if "PPP" in description:
            first_part, second_part = description.split("PPP")
            placename, last_part = second_part.split("EEE")
            print(f"placename: {placename}, type: {type(placename)}")
            new_descrip = first_part + assign_colour(locRegistry.place_by_name(placename)) + last_part
            return new_descrip

    else:
        if loc_dict[loc.name][card].get("long_desc_dict"):
            long_dict = loc_dict[loc.name][card]["long_desc_dict"]
            for item in long_dict:
                if item == "generic":
                    start = long_dict[item]
                    long_desc.append(start)
                else:
                    if "[[]]" in long_dict[item]:
                        test = long_dict[item].replace("[[]]", assign_colour(item))
                    else:
                        test = long_dict[item]
                    long_desc.append(test)
    return long_desc

area_descrip = format_descrip(d_type="area_descrip", description=loc_dict["graveyard"]["descrip"])
long_desc = format_descrip(d_type="cardinal_descrip")
formatted = long_desc

if formatted:
    items_descrip = (f"{formatted[0]}{', '.join(formatted[1:-1])} and {formatted[-1]}")

    new_desc = area_descrip + ".\n" + f"You're facing {assign_colour(card)}. " + items_descrip + "."
    print(f"new_desc: \n\n{new_desc}")
