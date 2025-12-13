## utilities to be used by any script at any point

## colour selected string

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

def col_text(text:str="", colour:str=None):

## def apply_col_to_text(item, colour="green"): # is just this, copied from Choices.

    baseline_format=';'.join([str(0), str(37), str("40")]) ## Add more colours later
    #bold_white_format=';'.join([str(1), str(37), str("40")])
    red_format=';'.join([str(0), str(31), str("40")])
    #bold_red_format=';'.join([str(1), str(31), str("40")])
    green_format=';'.join([str(0), str(32), str("40")])
    #bold_green_format=';'.join([str(1), str(32), str("40")])
    cyan_format=';'.join([str(0), str(36), str("40")])
    blue_format=';'.join([str(0), str(34), str("40")])
    yellow_format=';'.join([str(0), str(33), str("40")])
    b_yellow_format=';'.join([str(1), str(33), str("40")])
    magenta_format=';'.join([str(0), str(35), str("40")])


    BASELINE=f"\x1b[{baseline_format}m"
    RED=f"\x1b[{red_format}m"
    END="\x1b[0m"
    #BOLD_RED=f"\x1b[{bold_red_format}m"
    GRN=f"\x1b[{green_format}m"
    CYAN=f"\x1b[{cyan_format}m"
    BLUE=f"\x1b[{blue_format}m"
    YEL=f"\x1b[{yellow_format}m"
    B_YEL=f"\x1b[{b_yellow_format}m"
    MAG=f"\x1b[{magenta_format}m"
    #BOLD_GRN=f"\x1b[{bold_green_format}m"
    #REAL_WHT=f"\x1b[{white_format}m"

    col_dict={
    "blue": BLUE,
    "cyan": CYAN,
    "green": GRN,
    "red": RED,
    "yellow": YEL,
    "magenta":MAG,
    "description": B_YEL
    }


    if col_dict.get(colour):
        col=col_dict.get(colour)

    else:
        col=BASELINE

    col_text = f'{col}{text}{END}'

    return col_text


cardinal_cols = {
    "north": "red",
    "south": "blue",
    "east": "cyan",
    "west": "magenta"
}

def assign_colour(item, colour=None, nicename=None, switch=False):
    from set_up_game import game
    specials = ("location", "loc")
    cardinals=["north", "south", "east", "west"]
    game.colour_counter = game.colour_counter%len(cardinals)

    if colour in specials:
        if "loc" in colour:
            colour="green" # change it here to change all location text. Maybe a decent way to do it.

    if isinstance(item, list):
        item=item[0] #arbitrarily take the first one.
        #print(f"Item was a list. Now: {item}, type: {type(item)}")

    if item in cardinals:
        #print(f"Item is a cardinal: {item}")
        colour=cardinal_cols[item]

    elif isinstance(item, str) or isinstance(item, ItemInstance):
        if isinstance(item, str):
            item_instance=registry.instances_by_name(item)
            if item_instance:
                item=item_instance[0] ## breaks as soon as there's more then one item in inventory.

        if isinstance(item, ItemInstance):
            #print(f"Item is an instance: {item}")
            entry:ItemInstance = item

            if entry and entry.colour != None:
                #print("Item found.")
                #print(f"Tex col is not none. {entry.get(colour)}")
                colour=entry.colour
                item=item.name
            #if game.inv_colours.get(item):
            #    text_colour = game.inv_colours.get(item)
            else:
                #print("Text colour is none, assigning based on counter")
                colour=cardinals[game.colour_counter%len(cardinals)]
                colour=cardinal_cols[colour]
                game.colour_counter += 1
                #colour=cardinals[game.colour_counter]
                #colour=cardinal_cols[colour]
                ##print(f"Colour from counter: {colour}")
                #game.colour_counter += 1
                #game.inv_colours[item]=colour # souldn't need this at all, only made it because name_col didn't work.
                item_name = registry.name_col(item, colour) ## set colour to inst object. Returns the item.name.
                #print(f"Colour: {item.colour}")
                item=item_name # can do this inline, just here for now while testing.
        elif isinstance(colour, (int, float)):# and colour != None: # and colour <= len(cardinals)-1: cut the length part as it makes the entries of list len>4 colourless.
            colour=int(colour)%len(cardinals)
            colour=cardinals[int(colour)] # get the value from the list by index, so lists always have the same order (separate from the game.colour_counter, which loops but not per text line. This way the first through fourth option always have the same order unless they've another priority.)
            # This should stop the current issue where 'yes, no' are green and blue, then red and cyan next time, because the loop is 4 colours long. Would prefer it to be consistent.
            colour=cardinal_cols[colour]
        else:
            print(f"Item not in cardinals and not an instance: {item}") ####

# WHY IS THIS TRIGGERING
# WHEN THIS IS WHAT IT'S PRINTING:
#  "" Item not in cardinals and not an instance: <ItemInstance moss (9aae9489-13ee-40a3-af9b-2cdf8c63ef66)> ""

    if nicename:
        item=nicename
    if switch:
        item=switch_the(item)
    coloured_text=col_text(item, colour)
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
