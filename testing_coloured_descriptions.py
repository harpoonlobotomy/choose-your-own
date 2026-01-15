from itemRegistry import registry
from env_data import locRegistry, loc_dict
from initialise_all import initialise_all
from misc_utilities import assign_colour

initialise_all()

def format_descrip(type="area_descrip", description=""):
    if type == "area_descrip":
        print(f"AREA DESCRIPTION:\n{description}")
        if "PPP" in description:
            # replace from PPP to EEE with assign_colour version of the placename.
            first_part, second_part = description.split("PPP")
            print(f"first_part: {first_part}, second_part: {second_part}")
            placename, last_part = second_part.split("EEE")
            new_descrip = first_part + assign_colour(locRegistry.place_by_name(placename)) + last_part
            print(f"new_descrip: {new_descrip}")
    else:
        print(f"Cardinal description: {description}")

## For this to work, i need to store the descrips in the class, not get them from the dict each time. Or I guess just run this all each time but that seems wasteful.

# Although, this could evolve into something dynamic, in which case running it each time is good. As in, mark out 'sections', and if an item is removed, remove that section and adjust capitalisation etc accordingly. And/or add the 'dropped items' to the end of the description in-line, intead of the print line of local items I have now.

# So now the thought is, instead of having hard-written descriptions for each part, it's a sequence of parts which can be checked for. So instead of
#       loc.cardinals[cardinal].long_desc
# being a direct take from the dict, long_desc would be made of

#############
# long_desc = []

# area_description = loc_dict[loc.current.name]["description"] # generic, unchangeable description of the area

# long_desc.append(area_description)

# for item in loc.current.items:
#   if item.name in item_descrip[loc.current.name]:
#       long_desc.append(item_descrip[loc.current.name]) # Here the items have descriptions per location, not per item. This is probably better in this case, even if usually I'm trying to delineate items + environment more sharply. These are item-based location descriptions after all.

#formatted = []
#for v in long_desc:
#    formatted.append(f"{', '.join(v)}")
##print(f"    {', '.join(formatted[:-1])} or {formatted[-1]}")
#items_descrip = (f"{', '.join(formatted[:-1])} and {formatted[-1]}")
#
#new_desc = area_description + items_descrip

#############
# the above might work? Idk. Need to write some test copy to try it out.

loc = locRegistry.place_by_name("graveyard")
area_descrip = loc_dict["graveyard"]["descrip"]
format_descrip(type="area_descrip", description=area_descrip)

for cardinal in ("north", "east", "south", "west"):
    format_descrip(type="cardinal_descrip", description=loc.cardinals[cardinal].short_desc)

#print(loc)
#print(dir(loc))
#print(loc.set_scene_descrip(loc.name, loc))
