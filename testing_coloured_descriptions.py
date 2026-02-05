
from env_data import placeInstance
import itemRegistry
from misc_utilities import assign_colour
from printing import print_green, print_red, print_yellow

print_test_descriptions = False

def format_descrip(d_type="area_descrip", description="", location = None, cardinal = None):
    long_desc = []

    import json

    loc_items_json = "loc_data.json"
    with open(loc_items_json, 'r') as loc_items_file:
        loc_dict = json.load(loc_items_file)

    if d_type == "area_descrip":
        if not loc_dict.get(location):
            for loc in loc_dict:
                if loc_dict[loc].get("alt_names"):
                    for name in loc_dict[loc]["alt_names"]:
                        if name == location:
                            location = name
        #if location == "hotel room":
        #    location = "city hotel room" ## just for the moment, working on other things.
        description = loc_dict[location]["descrip"]
        if "PPP" in description:
            first_part, second_part = description.split("PPP")
            placename, last_part = second_part.split("EEE")
            if placename == "hotel room":
                placename = "city hotel room"
            from env_data import locRegistry
            new_descrip = first_part + assign_colour(locRegistry.place_by_name(placename)) + last_part
            if new_descrip[-1] != ".":
                new_descrip = new_descrip + "."
            return new_descrip
        else:
            return description

    elif d_type == "item_desc":
        no_items_text = None
        if location == "hotel room":
            location = "city hotel room"
        if loc_dict[location].get(cardinal) and loc_dict[location][cardinal].get("item_desc"):
            long_dict = loc_dict[location][cardinal]["item_desc"]
            no_starting_items = long_dict.get("no_starting_items")
            local_items = itemRegistry.registry.get_item_by_location(f"{location} {cardinal}")
            if local_items:
                local_items = list(i for i in local_items if not (hasattr(i, "is_hidden") and getattr(i, "is_hidden")))
                #for thing in local_items:
                #    print(f"{thing}: {(thing.is_hidden if hasattr(thing, "is_hidden") else "No is_hidden attr.")} ")
            for item in long_dict:
                inst_children = None
                #print(f"ITEM IN LONG_DICT: {item}\n{long_dict[item]}")
                if item == "generic":
                    start = long_dict[item]
                    long_desc.append(start)
                elif item == "no_items":
                    no_items_text = long_dict[item]
                elif item == "no_starting_items":
                     no_starting_items = long_dict["no_starting_items"]
                else:
                    if item:
                        if itemRegistry.registry.instances_by_name(item) and local_items:
                            print(f"Item {item} in registry and local_items")
                            for inst in itemRegistry.registry.instances_by_name(item):
                                if inst in local_items:
                                    if "[[]]" in long_dict[item]:
                                        long_parts = long_dict[item].split("[[]]")
                                        test = long_parts[0] + assign_colour(inst) + long_parts[1]
                                        long_desc.append(test)
                                    else:
                                        print(f"No [[]] in this description so it's excluded: {long_dict[item]}.")
            #                        if hasattr(inst, "children"):
            #                            inst_children = inst.children # no children here, only for item descriptions.
#
            #if inst_children:
            #    for child in inst_children:
            #        if not (hasattr(child, "is_hidden") and child.is_hidden):
            #            print(f"CHILD: {child}")
            #            long_desc.append(assign_colour(child, nicename=True))
            #        else:
            #            print(f"HIDDEN CHILD: {child}")



            if len(long_desc) == 1 and no_items_text:
                if local_items:
                    if no_starting_items:
                        long_desc.append(no_starting_items)
                    for loc_item in local_items:
                        print(f"loc_item: {loc_item}")
                        long_desc.append(assign_colour(loc_item, nicename=True))

                else:
                    long_desc.append(no_items_text)
        else:
            if loc_dict[location].get(cardinal) and loc_dict[location][cardinal].get("long_desc"):
                long_desc.append(loc_dict[location][cardinal].get("long_desc"))

    return long_desc

def generate_overview(location):

    format_descrip(d_type="area_descrip", description="", location = location, cardinal = None)

def compile_long_desc(long_desc):
    if len(long_desc) == 1:
        item_description = long_desc[0]
    elif len(long_desc) == 2:
        item_description = (f"{long_desc[0]}{long_desc[1]}")
    else:
        item_description = (f"{long_desc[0]}{', '.join(long_desc[1:-1])}, and {long_desc[-1]}")

    #new_desc = f"You're facing {assign_colour(cardinal)}. " + item_description
    new_desc = item_description
    if not new_desc.endswith("."):
        new_desc = new_desc + "."

    return new_desc

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
                    new_desc = compile_long_desc(long_desc)
                    compiled_cardinals[location][cardinal] = new_desc

        output = " ".join(output)
        output = str(area_descrip + "\n" + output)
        location_description[location] = output

    return location_description, compiled_cardinals

def loc_descriptions(place=None):

    location_description, cardinal_descriptions = init_loc_descriptions(place)
    #print(f"LOCATION DESCRIPTION: {location_description}")
    #print(f"CARDINAL DESCRIPTIONS: {cardinal_descriptions}")

    combined_dict = {}

    for location, overview in location_description.items():
        combined_dict[location] = ({"overview": {overview}})
        if print_test_descriptions:
            print_green(f"Location: {location}", invert=True)
            print(f"{overview}")
        if cardinal_descriptions.get(location):
            for cardinal, card_description in cardinal_descriptions[location].items():
                combined_dict[location][cardinal] = card_description
                if print_test_descriptions:
                    print_red(f"Cardinal: {cardinal}")
                    print(card_description)

    return combined_dict

if __name__ == "__main__":
    loc_descriptions()
