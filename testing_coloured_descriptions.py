#from itemRegistry import registry
from env_data import locRegistry, loc_dict
from initialise_all import initialise_all
import itemRegistry
from misc_utilities import assign_colour
from printing import print_green, print_red, print_yellow

initialise_all()

# So. Order of operations here.
# Need to initialise everything. Can remove the existing code for location/cardinal descriptions.
# After env and item initialisation (which would be now, given initialise_all has already run (will add this to the end of that most likely)), then run this, using registry.by_location() to get current items.

# Don't spend too much time on the latter though as the existing tests all rely on the test class.


def format_descrip(d_type="area_descrip", description="", location = None, cardinal = None):
    long_desc = []

    if d_type == "area_descrip":
        #print(f"AREA DESCRIPTION:\n{description}")
        description = loc_dict[location]["descrip"]
        if "PPP" in description:
            first_part, second_part = description.split("PPP")
            placename, last_part = second_part.split("EEE")
            #print(f"placename: {placename}, type: {type(placename)}")
            new_descrip = first_part + assign_colour(locRegistry.place_by_name(placename)) + last_part
            if new_descrip[-1] != ".":
                new_descrip = new_descrip + "."
            return new_descrip
        else:
            return description

    elif d_type == "long_descrip":
        #print(f" loc_dict[location]: {loc_dict[location]}")
        if loc_dict[location].get(cardinal) and loc_dict[location][cardinal].get("long_desc_dict"):
            long_dict = loc_dict[location][cardinal]["long_desc_dict"]
            for item in long_dict:
                if item == "generic":
                    start = long_dict[item]
                    long_desc.append(start)
                    #print(f"LONG  DESC GENERIC : {long_desc}")
                else:
                    if itemRegistry.registry.instances_by_name(item):
                        if itemRegistry.registry.get_item_by_location(f"{location} {cardinal}"):
                            if itemRegistry.registry.instances_by_name(item)[0] in itemRegistry.registry.get_item_by_location(f"{location} {cardinal}"):
                                if "[[]]" in long_dict[item]:
                                    test = long_dict[item].replace("[[]]", assign_colour(item))
                                else:
                                    test = long_dict[item]
                                long_desc.append(test)
                    #print(f"APPENDING TEST: {long_desc}")
        else:
            if loc_dict[location].get(cardinal) and loc_dict[location][cardinal].get("long_desc"):
                long_desc.append(loc_dict[location][cardinal].get("long_desc"))

    return long_desc

##area_descrip = format_descrip(d_type="area_descrip", description=loc_dict[location]["descrip"])
#long_desc = format_descrip(d_type="cardinal_descrip")
#formatted = long_desc
#
#if formatted:
#    items_descrip = (f"{formatted[0]}{', '.join(formatted[1:-1])} and {formatted[-1]}")
#    new_desc = area_descrip + ".\n" + f"You're facing {assign_colour(cardinal)}. " + items_descrip + "."
#    print(f"new_desc: \n\n{new_desc}")



"""
    self.overview = f"{area_descrip}.{"\033[0m"} \n{self.cardinals["north"].short_desc} to the {assign_colour("north")}. To the {assign_colour("east")} is {self.cardinals["east"].short_desc}, and to the {assign_colour("south")} is {self.cardinals["south"].short_desc}."


    self.overview = f"{loc_dict[name]["descrip"]}.{"\033[0m"} \n{self.cardinals["north"].short_desc} to the {assign_colour("north")}. To the {assign_colour("east")} is {self.cardinals["east"].short_desc}, and to the {assign_colour("south")} is {self.cardinals["south"].short_desc}."
"""

def init_loc_descriptions():
    desc_dict = {} # if 4, use all of them. if len(3), skip #3. if len(2, skip #2 + #3)
    compiled_output = {}
    compiled_cardinals = {}

    for location in loc_dict:
        area_descrip = (format_descrip(d_type="area_descrip", description=loc_dict[location]["descrip"], location=location))
        output = []
        desc_dict[location] = {}
        compiled_cardinals[location] = {}
        active_cardinals = set()
        for cardinal in ("north", "east", "south", "west"):
            if loc_dict[location][cardinal] != None:
                active_cardinals.add(cardinal)

        for i, cardinal in enumerate(("north", "east", "south", "west")):
            if cardinal in active_cardinals:
                desc_dict[location][cardinal] = {}
                short_desc = (loc_dict[location][cardinal].get("short_desc") if loc_dict[location].get(cardinal) else None)

                desc_print_dict ={
                    "len_1": {
                        0: f"{short_desc} is to the {assign_colour(cardinal)}." # always north
                    },
                    "len_2": {
                        0: f"{short_desc} is to the {assign_colour(cardinal)},",
                        1: f"and to the {assign_colour(cardinal)} is {short_desc}."
                    },
                    "len_3": {
                        0: f"{short_desc} is to the {assign_colour(cardinal)}.",
                        1: f"To the {assign_colour(cardinal)} is {short_desc},",
                        2: f"and to the {assign_colour(cardinal)} is {short_desc}."
                    },
                    "len_4": {
                        0: f"{short_desc} is to the {assign_colour(cardinal)}.",
                        1: f"To the {assign_colour(cardinal)} is {short_desc},",
                        2: f"to the {assign_colour(cardinal)} is {short_desc},",
                        3: f"and to the {assign_colour(cardinal)} is {short_desc}."},
                    }

                if short_desc and short_desc != None:
                    cardinal_sort_desc = desc_print_dict["len_" + str(len(active_cardinals))][i]

                    desc_dict[location][cardinal]["short"] = cardinal_sort_desc
                    output.append(cardinal_sort_desc)

                long_desc = format_descrip(d_type="long_descrip", location=location, cardinal=cardinal)

                if long_desc:
                    if len(long_desc) == 1:
                        long_description = long_desc[0]
                    elif len(long_desc) == 2:
                        long_description = (f"{long_desc[0]}, and {long_desc[1]}")
                    else:
                        #print(f"LONG DESC len 3: {long_desc}")
                        long_description = (f"{long_desc[0]}{', '.join(long_desc[1:-1])}, and {long_desc[-1]}")
                        #print(f"Parts: long_desc[0]: {long_desc[0]} // long_desc[1:-1]: {long_desc[1:-1]} // long_desc[-1]: {long_desc[-1]}")
                    new_desc = area_descrip + "\n" + f"You're facing {assign_colour(cardinal)}. " + long_description
                    compiled_cardinals[location][cardinal] = new_desc

        #print(f"OUTPUT: {output}")
        output = " ".join(output)
        #print(f"OUTPUT after 'output = ' '.join(output)': {output}")
        output = str(area_descrip + "\n" + output)
        #print(f"OUTPUT after output = str(area_descrip + '\\n' + output): {output}")
        compiled_output[location] = output

    return desc_dict, compiled_output, compiled_cardinals

if __name__ == "__main__":
    desc_dict, compiled_output, compiled_cardinals = init_loc_descriptions()
    for k, v in compiled_output.items():
        print(f"\n")
        print_green(f"Location: {k}", invert=True)
        print(f"{v}")
        if compiled_cardinals.get(k):
            #print(f"Compiled_cardinals[k]: {compiled_cardinals[k]}")
            for key, val in compiled_cardinals[k].items():
                print()
                print_red(f"Cardinal: {key}")
                print(val)
