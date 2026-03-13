
import re
from env_data import placeInstance
import itemRegistry
from logger import logging_fn
from misc_utilities import assign_colour
from printing import print_green, print_red, print_yellow

print_test_descriptions = False

def format_descrip(d_type="area_descrip", description="", location = None, cardinal = None):

    long_desc = []
    from env_data import locRegistry as loc
    if d_type == "area_descrip":
        logging_fn("area_descrip")
        if not loc.loc_data.get(location):
            for place in loc.loc_data:
                if loc.loc_data[place].get("alt_names"):
                    for name in loc.loc_data[place]["alt_names"]:
                        if name == location:
                            location = name
        #if location == "hotel room":
        #    location = "city hotel room" ## just for the moment, working on other things.
        description = loc.loc_data[location]["descrip"]
        if "PPP" in description:
            first_part, second_part = description.split("PPP")
            placename, last_part = second_part.split("EEE")
            if placename == "hotel room":
                placename = "city hotel room"
            new_descrip = first_part + assign_colour(loc.place_by_name(placename)) + last_part
            if new_descrip[-1] != ".":
                new_descrip = new_descrip + "."
            return new_descrip
        else:
            return description

    elif d_type == "item_desc":
        logging_fn("item_desc")
        no_items_text = None
        if location == "hotel room":
            location = "city hotel room"
        if loc.loc_data[location].get(cardinal) and loc.loc_data[location][cardinal].get("item_desc"):
            long_dict = loc.loc_data[location][cardinal]["item_desc"]
            no_starting_items = long_dict.get("no_starting_items")
            local_items = itemRegistry.registry.get_item_by_location(f"{location} {cardinal}")
            if local_items:
                local_items = list(i for i in local_items if not (hasattr(i, "is_hidden") and getattr(i, "is_hidden")))
                local_items = list(i for i in local_items if not (hasattr(i, "not_in_loc_desc") and getattr(i, "not_in_loc_desc")))
                #for thing in local_items:
                #    print(f"{thing}: {(thing.is_hidden if hasattr(thing, "is_hidden") else "No is_hidden attr.")} ")
            multiples = None
            for item in long_dict:
                if item == "generic":
                    start = long_dict[item]
                    long_desc.append(start)
                elif item == "no_items":
                    no_items_text = long_dict[item]
                elif item == "no_starting_items":
                     no_starting_items = long_dict[item]
                else:
                    if item and local_items:
                        multiples = {}
                        count = 0
                        for inst in local_items:
                            if inst.name == item:
                                if "[[]]" in long_dict[item]:
                                    long_parts = long_dict[item].split("[[]]")
                                    if "fff" in long_parts[1]:
                                        if hasattr(inst, "event") and inst.event.state in (0, 1):
                                            long_parts[1] = long_parts[1].replace("fff", "")
                                        else:
                                            split_parts = re.split("fff.+fff", long_parts[1])
                                            long_parts[1] = split_parts[1]

                                    if "<<" in long_parts[1]:
                                        if hasattr(inst, "event") and inst.event.state == 2:
                                            long_parts[1] = long_parts[1].replace("<<", "")
                                            long_parts[1] = long_parts[1].replace(">>", "")
                                        else:
                                            split_parts = re.split("<<.+>>", long_parts[1])
                                            long_parts[1] = split_parts[0]
                                            if "fff" in long_parts[0]:
                                                long_parts[0] = long_parts[0].replace("fff","")

                                    if "<" in long_parts[1]:
                                        passed = False
                                        if hasattr(inst, "children") and inst.starting_children:
                                            if len(inst.children) == len(inst.starting_children):
                                                passed=True
                                            for item in inst.children:
                                                if item not in inst.starting_children:
                                                    passed=False
                                        if passed:
                                            long_parts[1] = long_parts[1].replace("<", "")
                                        else:
                                            long_parts[1] = long_parts[1].split("<")[0]
                                    #print(f"Long parts: {long_parts}")
                                    test = long_parts[0] + assign_colour(inst) + long_parts[1]
                                    if not multiples:
                                        multiples[inst.name] = {}
                                    count += 1
                                    multiples[inst.name].update({count: test})
                                    long_desc.append(test)
                                else:
                                    print(f"No [[]] in this description so it's excluded: {long_dict[item]}.")

                    if multiples and multiples.get(item) and len(multiples.get(item)) > 1:
                        for key, val in multiples[item].items():
                            long_desc.remove(val)
                            if key == count:
                                val = val.strip("\x1b[0m")
                                val = val.strip("a ")
                                long_desc.append(val + f" x{count}\x1b[0m")

            if local_items:
                local_items = list(i for i in local_items if not long_dict.get(i.name))

            if long_desc and len(long_desc) == 1 and no_items_text and not local_items:
                #if local_items:
                #    for loc_item in local_items:
                #        if not long_dict.get(loc_item):
                #        #    print("pass, assume already included.")
                #        #else:
                #        #    print(f"loc_item: {loc_item}")
                #            long_desc.append(assign_colour(loc_item, nicename=True))
                #else:
                    long_desc.append(no_items_text)

            else:
                if local_items:
                    added = set()
                    for loc_item in local_items:
                        if loc_item.name in added:
                            continue
                        named = list(i for i in local_items if i.name == loc_item.name)
                        if len(named) > 1 and not loc_item.name in added:
                            val = f"{assign_colour(loc_item)}"
                            #val = val.strip("\x1b[0m")
                            if val.startswith("a "):
                                val = val.replace("a ", count=1)
                            if hasattr(loc_item, "nicenames") and loc_item.nicenames.get("is_plural"):
                                val = val.replace(loc_item.name, loc_item.nicenames["is_plural"])
                            elif loc_item.name[-1] != "s":
                                val = val.replace(loc_item.name, loc_item.name + "s")

                            long_desc.append(f"{len(named)} {val}\x1b[0m")
                            #long_desc.append(f"\033[0m{val} x{len(named)}\x1b[0m")
                            added.add(loc_item.name)

                        else:#if not long_dict.get(loc_item.name):
                            long_desc.append(assign_colour(loc_item, nicename=True))

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
        if new_desc == "":
            new_desc = "There's not much to see here" # So it's not just a full stop if no desc was given in loc_data.
        new_desc = new_desc + "."

    return new_desc

def init_loc_descriptions(place=None, card=None):
    """Generates or updates the location description for the given place and/or cardinal instances.\n\nUses current item presence and state to ensure the description matches the world-state."""

    desc_dict = {}
    location_description = {}
    compiled_cardinals = {}
    from env_data import locRegistry as loc
    for location in loc.loc_data:
        if place != None:
            if isinstance(place, placeInstance):
                place = place.name
            if location != place:
                continue

        area_descrip = (format_descrip(d_type="area_descrip", description=loc.loc_data[location]["descrip"], location=location))
        output = []
        desc_dict[location] = {}
        compiled_cardinals[location] = {}
        active_cardinals = set()
        for cardinal in ("north", "east", "south", "west"):
            if loc.loc_data[location].get(cardinal) != None:
                active_cardinals.add(cardinal)

        for i, cardinal in enumerate(("north", "east", "south", "west")):
            if cardinal in active_cardinals:
                desc_dict[location][cardinal] = {}
                short_desc = (loc.loc_data[location][cardinal].get("short_desc") if loc.loc_data[location].get(cardinal) else None)

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

                if card:
                    if cardinal == card.name:
                        long_desc = format_descrip(d_type="item_desc", location=location, cardinal=cardinal)
                    else:
                        long_desc = None

                else:
                    long_desc = format_descrip(d_type="item_desc", location=location, cardinal=cardinal)

                if long_desc:
                    new_desc = compile_long_desc(long_desc)
                    compiled_cardinals[location][cardinal] = new_desc

        output = " ".join(output)
        output = str(area_descrip + "\n" + output)
        location_description[location] = output

    return location_description, compiled_cardinals

def loc_descriptions(place=None, card_inst=None):
    from env_data import locRegistry as loc
    if place and place == loc.current.place:
        card_inst = loc.current
    location_description, cardinal_descriptions = init_loc_descriptions(place, card=card_inst)
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
