#from itemRegistry import registry

#from initialise_all import initialise_all
from env_data import placeInstance
import itemRegistry
from misc_utilities import assign_colour
from printing import print_green, print_red, print_yellow

#initialise_all()

# So. Order of operations here.
# Need to initialise everything. Can remove the existing code for location/cardinal descriptions.
# After env and item initialisation (which would be now, given initialise_all has already run (will add this to the end of that most likely)), then run this, using registry.by_location() to get current items.

# Don't spend too much time on the latter though as the existing tests all rely on the test class.

def format_descrip(d_type="area_descrip", description="", location = None, cardinal = None):
    long_desc = []

    import json

    #item_dict_json = "dynamic_data/items_main.json"
    #with open(item_dict_json, 'r') as items_main:
    #    items_dict = json.load(items_main)

    loc_items_json = "loc_data.json"
    with open(loc_items_json, 'r') as loc_items_file:
        loc_dict = json.load(loc_items_file)

    if d_type == "area_descrip":
        #print(f"AREA DESCRIPTION:\n{description}")
        if location == "hotel room":
            location = "city hotel room" ## just for the moment, working on other things.
        description = loc_dict[location]["descrip"]
        if "PPP" in description:
            first_part, second_part = description.split("PPP")
            placename, last_part = second_part.split("EEE")
            if placename == "hotel room":
                placename = "city hotel room"
            #print(f"placename: {placename}, type: {type(placename)}")
            from env_data import locRegistry
            new_descrip = first_part + assign_colour(locRegistry.place_by_name(placename)) + last_part
            if new_descrip[-1] != ".":
                new_descrip = new_descrip + "."
            #print(f"new_descrip/area_descrip: {new_descrip}")
            return new_descrip
        else:
            return description

    elif d_type == "item_desc":
        no_items_text = None
        if location == "hotel room":
            location = "city hotel room"
        #print(f" loc_dict[location]: {loc_dict[location]}")
        if loc_dict[location].get(cardinal) and loc_dict[location][cardinal].get("item_desc"):
            long_dict = loc_dict[location][cardinal]["item_desc"]
            for item in long_dict:
                if item == "generic":
                    start = long_dict[item]
                    long_desc.append(start)
                    #print(f"LONG  DESC GENERIC : {long_desc}")
                elif item == "no_items":
                    no_items_text = long_dict[item]
                else:
                    if item:
                        if itemRegistry.registry.instances_by_name(item):
                            #print(f"Item in item registry: {item}")
                            local_items = itemRegistry.registry.get_item_by_location(f"{location} {cardinal}")
                            #print(f"local_items: {local_items}")
                            #print(f"itemRegistry.registry.instances_by_name(item)[0] : {itemRegistry.registry.instances_by_name(item)[0]}")
                            if local_items and itemRegistry.registry.instances_by_name(item)[0] in local_items:
                                item_inst = itemRegistry.registry.instances_by_name(item)[0]
                            #if itemRegistry.registry.instances_by_name(item)[0] in itemRegistry.registry.get_item_by_location(f"{location} {cardinal}"):

                                if "[[]]" in long_dict[item]:
                                    long_parts = long_dict[item].split("[[]]")
                                    #print(f"long_parts[0] + assign_colour(item_inst) + long_parts[1]:\n\n{long_parts[0] + assign_colour(item_inst) + long_parts[1]}\n\n")
                                    test = long_parts[0] + assign_colour(item_inst) + long_parts[1]
                                    #test = long_dict[item].replace("[[]]", assign_colour(item_inst))
                                    #print(f'"[[]]" in long_dict[item] and local: {long_dict[item]}')
                                    #print(f"---------- assign_colour(item_inst): {assign_colour(item_inst)}")
                                    #print(f"test: {test}")
                                else:
                                    test = long_dict[item]
                                long_desc.append(test)
                                #print(f"long_desc: {long_desc}")
                                #print(f"LOCAL ITEMS TEST: {test}")
                           # else:
                            #    if "[[]]" in long_dict[item]:
                                #print(f'"[[]]" in long_dict[item] but not local: {long_dict[item]}')
                            #        test = long_dict[item].replace("[[]]", assign_colour(item))
                            #        long_dict[item]
                            #        #long_desc.append(test)
                            #    else:
                            #        test = long_dict[item]
                            #    long_desc.append(test)
                                #print(f"NOT LOCAL TEST: {test}")

                        #else:
                        #    if "[[]]" in long_dict[item]:
                        #        #print(f"item in long_dict[item]: {long_dict[item]}")
                        #        test = long_dict[item].replace("[[]]", item) ## for now just do the text, later get the colours back once instances are done.
                        #    else:
                        #        #print(f"[[]] not in long_dict[item]: {long_dict[item]}")
                        #        test = long_dict[item]
                        #    long_desc.append(test)
                            #print("NOT INSTANCE BY NAME TEST:")
                            #from testclass import testReg
                            #testReg.create_item_by_name(item)

                    #else:
                    #    print("No entries other than 'generic'.")
                    #print(f"APPENDING TEST: {long_desc}")
            if len(long_desc) == 1 and no_items_text:
                long_desc.append(no_items_text)
        else:
            if loc_dict[location].get(cardinal) and loc_dict[location][cardinal].get("long_desc"):
                long_desc.append(loc_dict[location][cardinal].get("long_desc"))
    #print(f"long_desc: {long_desc}")
    return long_desc

def generate_overview(location):

    format_descrip(d_type="area_descrip", description="", location = location, cardinal = None)


"""
    self.overview = f"{area_descrip}.{"\033[0m"} \n{self.cardinals["north"].short_desc} to the {assign_colour("north")}. To the {assign_colour("east")} is {self.cardinals["east"].short_desc}, and to the {assign_colour("south")} is {self.cardinals["south"].short_desc}."


    self.overview = f"{loc_dict[name]["descrip"]}.{"\033[0m"} \n{self.cardinals["north"].short_desc} to the {assign_colour("north")}. To the {assign_colour("east")} is {self.cardinals["east"].short_desc}, and to the {assign_colour("south")} is {self.cardinals["south"].short_desc}."
"""

def init_loc_descriptions(place=None):

    desc_dict = {}
    location_description = {}
    compiled_cardinals = {}

    import json
    loc_items_json = "loc_data.json"
    with open(loc_items_json, 'r') as loc_items_file:
        loc_dict = json.load(loc_items_file)


    for location in loc_dict:
        if place != None:
            if isinstance(place, placeInstance):
                place = place.name
            if location != place:
                continue

        #print(f"LOCATION IN LOC_DICT: {location}")
        area_descrip = (format_descrip(d_type="area_descrip", description=loc_dict[location]["descrip"], location=location))
        output = []
        desc_dict[location] = {}
        compiled_cardinals[location] = {}
        active_cardinals = set()
        for cardinal in ("north", "east", "south", "west"):
            if loc_dict[location].get(cardinal) != None:
                active_cardinals.add(cardinal)

        for i, cardinal in enumerate(("north", "east", "south", "west")):
            if cardinal in active_cardinals:
                desc_dict[location][cardinal] = {}
                short_desc = (loc_dict[location][cardinal].get("short_desc") if loc_dict[location].get(cardinal) else None)

                desc_print_dict ={
                    "len_1": {
                        0: f"{short_desc} to the {assign_colour(cardinal)}."
                    },
                    "len_2": {
                        0: f"{short_desc} to the {assign_colour(cardinal)},",
                        1: f"and to the {assign_colour(cardinal)} {short_desc}."
                    },
                    "len_3": {
                        0: f"{short_desc} to the {assign_colour(cardinal)}.",
                        1: f"To the {assign_colour(cardinal)} {short_desc},",
                        2: f"and to the {assign_colour(cardinal)} {short_desc}."
                    },
                    "len_4": {
                        0: f"{short_desc} to the {assign_colour(cardinal)}.",
                        1: f"To the {assign_colour(cardinal)} {short_desc},",
                        2: f"to the {assign_colour(cardinal)} {short_desc},",
                        3: f"and to the {assign_colour(cardinal)} {short_desc}."},
                    }

                if short_desc and short_desc != None:
                    cardinal_sort_desc = desc_print_dict["len_" + str(len(active_cardinals))][i]

                    desc_dict[location][cardinal]["short"] = cardinal_sort_desc
                    output.append(cardinal_sort_desc)

                long_desc = format_descrip(d_type="item_desc", location=location, cardinal=cardinal)

                if long_desc:
                    #print(f"LONG_DESC: {long_desc}, len: {len(long_desc)}")
                    if len(long_desc) == 1:
                        item_description = long_desc[0]# testing out for when there are no items, need to finish the sentence somehow. Do this better. TODO: Alternate long_desc for 'all items are gone'. This does work for now, though.
                    elif len(long_desc) == 2:
                        #item_description = (f"{long_desc[0]}, and {long_desc[1]}")
                        item_description = (f"{long_desc[0]}{long_desc[1]}")
                    else:
                        #print(f"LONG DESC len 3: {long_desc}")
                        item_description = (f"{long_desc[0]}{', '.join(long_desc[1:-1])}, and {long_desc[-1]}")
                        #print(f"Parts: long_desc[0]: {long_desc[0]} // long_desc[1:-1]: {long_desc[1:-1]} // long_desc[-1]: {long_desc[-1]}")

                        #print(f"item_description: {item_description}")
                    new_desc = f"You're facing {assign_colour(cardinal)}. " + item_description
                    #print(f"new_desc: {new_desc}")
                    if not new_desc.endswith("."):
                        new_desc = new_desc + "."
                    #print(f"new_desc: {new_desc}")
                    compiled_cardinals[location][cardinal] = new_desc
                    #print(f":compiled_cardinals[location][cardinal]: {compiled_cardinals[location][cardinal]}")
                else:
                    compiled_cardinals[location][cardinal] = f"You're facing {assign_colour(cardinal)}. " + loc_dict[location][cardinal].get("long_desc")



        #print(f"OUTPUT: {output}")
        output = " ".join(output)
        #print(f"OUTPUT after 'output = ' '.join(output)': {output}")
        output = str(area_descrip + "\n" + output)
        #print(f"OUTPUT after output = str(area_descrip + '\\n' + output): {output}")
        location_description[location] = output

    return location_description, compiled_cardinals

def loc_descriptions(place=None):

    location_description, cardinal_descriptions = init_loc_descriptions(place)
    #print(f"LOCATION DESCRIPTION: {location_description}")
    #print(f"CARDINAL DESCRIPTIONS: {cardinal_descriptions}")

    combined_dict = {}

    for location, overview in location_description.items():
        combined_dict[location] = ({"overview": {overview}})
        #print(f"\n")
        #print_green(f"Location: {location}", invert=True)
        #print(f"{overview}")
        if cardinal_descriptions.get(location):
            for cardinal, card_description in cardinal_descriptions[location].items():
                combined_dict[location][cardinal] = card_description
                #print()
                #print_red(f"Cardinal: {cardinal}")
                #print(card_description)

    #print("\n\n\n")
    #for entry in combined_dict:
        #print(f"{entry}: {combined_dict[entry]}")

    return combined_dict

if __name__ == "__main__":
    loc_descriptions()



    #print(f"desc dict: {desc_dict}")
