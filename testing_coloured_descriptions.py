from itemRegistry import registry
from env_data import locRegistry, loc_dict
from initialise_all import initialise_all
from misc_utilities import assign_colour

initialise_all()


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

#"long_desc": "MMMThe shrine itself is fragile looking, with candles still not burnt down entirely. AAAEEE, and AAAtwo jars; one on the desk, and the other on the ground beside itEEE."

# going to test it with shrine north:
# The shrine itself is fragile looking, with candles still not burnt down entirely. There are scrolls on the main surface, and two jars; one on the desk, and the other on the ground beside it.

# current amended version:
#"MMMThe shrine itself is fragile looking, with candles still not burnt down entirely. AAAThere are scrolls on the main surfaceEEE, and AAAtwo jars; one on the desk, and the other on the ground beside itEEE."
# 'MMM' is just a notation to indicate it can be modified, if missing then we just use the base description.
# I'm not sure if I want 'AAA -- EEE, BBB -- EEE, or AAA -- EEE, AAA -- EEE. One indicates part, but I don't know if that's necessary. Going to go with just 'a=start, e=end' for now.
# No wait. I was going to write it in parts then join them, not split and rejoin the hardcopy. Beh.

loc = locRegistry.place_by_name("shrine")

loc.items = ["scroll", "metal jar"]
item_descrip = {
    "shrine": {"north": {"scroll": "a scroll on the main surface", "ivory jar": "an ivory jar on the desk", "metal jar": "a metal jar on the floor beside the desk",}}
}

long_desc = []
def format_descrip(d_type="area_descrip", description=""):

    if d_type == "area_descrip":
        print(f"AREA DESCRIPTION:\n{description}")
        if "PPP" in description:
            # replace from PPP to EEE with assign_colour version of the placename.
            first_part, second_part = description.split("PPP")
            #print(f"first_part: {first_part}, second_part: {second_part}")
            placename, last_part = second_part.split("EEE")
            print(f"placename: {placename}, type: {type(placename)}")
            new_descrip = first_part + assign_colour(locRegistry.place_by_name(placename)) + last_part
            #print(f"new_descrip: {new_descrip}")
            return new_descrip

    else:
        #print(f"       {description}")
        for item in loc.items:
            print(f"item in items: {item}")
            if item in item_descrip[loc.name]["north"]:
                print(f"item in loc north: {item}")
                long_desc.append(item_descrip[loc.name]["north"].get(item))

    #area_description = loc_dict[loc.name]["descrip"] # generic, unchangeable description of the area

    return long_desc

    #formatted = []
    #print(f"Long desc: {long_desc}, type: {type(long_desc)}")
    #for v in long_desc:
    #    print(f"v: {v}")
    #    formatted.append(f"{"".join(v)}")

"""
new_desc: The shrine itself is fragile looking, with candles still not burnt down entirely. There are scrolls on the main surface and an ivory jar on the desk."""
# Well I mean that basically works, right?
"""
added 'metal jar' -

new_desc: The shrine itself is fragile looking, with candles still not burnt down entirely. There are scrolls on the main surface, an ivory jar on the desk and a metal jar on the floor beside the desk.
"""

# yeah I think that works. Simplified to hell but it works. (No coloured noun_inst but that can come.)


area_descrip = format_descrip(d_type="area_descrip", description=loc_dict["shrine"]["descrip"])

long_desc = format_descrip(d_type="cardinal_descrip", description=loc.cardinals["north"].long_desc)
#for cardinal in ("north", "east", "south", "west"):
#    print(f"\nCardinal description for {loc.name} {cardinal}:")
#    if cardinal == "north":
#        format_descrip(d_type="cardinal_descrip", description=loc.cardinals[cardinal].long_desc)
#    else:
#        if loc_dict[loc.name].get(cardinal):
#            print(loc_dict[loc.name][cardinal]["long_desc"])

formatted = long_desc
print("formatted: ", formatted)
print(f"area_descrip: {area_descrip}")
#print(f"    {', '.join(formatted[:-1])} or {formatted[-1]}")
if formatted:
    items_descrip = (f"{', '.join(formatted[:-1])} and {formatted[-1]}")

    new_desc = area_descrip + "\n" + loc.cardinals["north"].long_desc +  " There are " + items_descrip + "."
    print(f"new_desc: {new_desc}")
#print(loc)
#print(dir(loc))
#print(loc.set_scene_descrip(loc.name, loc))

#unrelated test
#from testclass import testReg, init_testreg
#init_testreg()
#print(testReg.by_loc_cat["Graveyard"]["container"])#[flag]
