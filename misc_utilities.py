## utilities to be used by any script at any point


""" Want to do some colour coding.


Need a colour for locations, separate from the cardinals. I'll need to use something other than what I am now as the straight 16 is too limiting.

Maybe make all locations green, and not use green for anything else?

Yellow for 'interactable' in description text, maybe?


"""
from item_management_2 import ItemInstance, registry





def switch_the(text, replace_with=""): # remember: if specifying the replace_with string, it must end with a space. Might just add that here actually...
    if isinstance(text, list):
        if len(text) == 1:
            text=text[0]
            text=text.name
        else:
            print("Trying to `switch_the`, but text is a list with more than one item.")
            exit()
    if isinstance(text, ItemInstance):
        text=text.name
    for article in ("a ", "an "):
        if text.startswith(article):# in text:
            if replace_with != "":
                #print(f"replace with isn't blank: `{replace_with}`")
                if replace_with[-1] != " ":
                    #print(f"replace with doesn't end with a space: `{replace_with}`")
                    replace_with = replace_with + " "
                    #print(f"replace with should now have a space: `{replace_with}`")
            text = text.replace(article, replace_with) # added 'replace with' so I can specify 'the' if needed. Testing.


    if replace_with == "" or replace_with == None: # should only trigger if neither article is in the text. This might need testing.
        text = "the "+ text # so I can add 'the' in front of a string, even if it doesn't start w 'a' or 'an'.
    return text


cardinal_cols = {
    "north": "red",
    "south": "blue",
    "east": "cyan",
    "west": "magenta"
}

def assign_colour(item, colour=None, *, nicename=None, switch=False, no_reset=False, not_bold=False):

    from tui.colours import Colours

    bg = None
    bld = ita = u_line = invt = False

    specials = ("location", "loc", "description", "title_bg", "title", "deco", "hash", "title_white", "equals", "underscore")
    cardinals=["north", "south", "east", "west"]
    Colours.colour_counter = Colours.colour_counter%len(cardinals)

    if colour and isinstance(colour, str):
        if "b_" in colour:
            bld=True
            colour=colour.strip("b_")
        if "u_" in colour:
            u_line=True
            colour=colour.strip("u_")
        if "i_" in colour:
            ita=True
            colour=colour.strip("i_")

        bold_special = ["title", "deco", "description", "title_white"]

        if colour in specials:
            if "loc" in colour:
                colour="green" # set 'loc' in colours.C instead of hardcoding the actual colours here. Only code here for bold, or if the colour named is inaccurate.
            if colour == "title_bg":
                colour="black"
                bg="green"
            if colour == "equals":
                u_line=True
                bg="blue"
            if colour == "hash":
                bg="blue"
            if colour == "title_white":
                colour="white"
            if colour in bold_special:
                bld=True
            if colour == "title":
                bld=True

    elif isinstance(item, list):
        item=item[0] #arbitrarily take the first one.
        #print(f"Item was a list. Now: {item}, type: {type(item)}")

    def check_instance_col(item):
        if isinstance(item, ItemInstance):
            #print(f"Item is an instance: {item}")
            entry:ItemInstance = item

            if entry and entry.colour != None:
                #print("Item found.")
                #print(f"Tex col is not none. {entry.get(colour)}")
                colour=entry.colour
                item=item.name
                bld=True
            #if game.inv_colours.get(item):
            #    text_colour = game.inv_colours.get(item)
            else:
                #print("Text colour is none, assigning based on counter")
                colour=cardinals[Colours.colour_counter%len(cardinals)]
                colour=cardinal_cols[colour]
                Colours.colour_counter += 1

                item_name = registry.name_col(item, colour)
                item=item_name # can do this inline, just here for now while testing.
                bld=True
            return colour, item, bld

    if item in cardinals:
        #print(f"Item is a cardinal: {item}")
        colour=cardinal_cols[item]
        bld=True



    elif isinstance(item, str) or isinstance(item, ItemInstance):
        if isinstance(item, str):
            if "(x2)" in item:
                item_temp = item.replace(" (x2)", "")
                item_instance=registry.instances_by_name(item_temp)
                if item_instance:
                    item_temp=item_instance[0]
                    colour, _, bld = check_instance_col(item_temp)

            else:
                item_instance=registry.instances_by_name(item)
                if item_instance:
                    item=item_instance[0] ## breaks as soon as there's more then one item in inventory.


        if isinstance(item, ItemInstance):
            colour, item, bld = check_instance_col(item)


        elif isinstance(colour, (int, float)):
            colour=int(colour)%len(cardinals)
            colour=cardinals[int(colour)]

            colour=cardinal_cols[colour]
            bld=True
        #else:
        #    print(f"Item not in cardinals and not an instance: {item}") #### ## triggers on locations, possible other things too.
        # This whole thing needs redoing so I'm not going to focus on it too much for now.

    if nicename:
        item=nicename
    if switch:
        item=switch_the(item)

    if colour == None:
        print(f"Colour is None. Item: ({item})")

    if not_bold:
        bld=False

    coloured_text=Colours.c(item, colour, bg, bold=bld, italics=ita, underline=u_line, invert=invt, no_reset=no_reset)
    return coloured_text

def col_list(list:list=[], colour:str=None):
    coloured_list=[]

    for i, item in enumerate(list):
        if not colour:
            coloured_text = assign_colour(item, i)
        else:
            coloured_text = assign_colour(item, colour)
        coloured_list.append(coloured_text)
    return coloured_list
