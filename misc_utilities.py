## utilities to be used by any script at any point

## colour selected string

""" Want to do some colour coding.


Need a colour for locations, separate from the cardinals. I'll need to use something other than what I am now as the straight 16 is too limiting.

Maybe make all locations green, and not use green for anything else?

Yellow for 'interactable' in description text, maybe?


"""
from choices import loot, loc_loot
from set_up_game import game

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
    magenta_format=';'.join([str(0), str(35), str("40")])


    BASELINE=f"\x1b[{baseline_format}m"
    RED=f"\x1b[{red_format}m"
    END="\x1b[0m"
    #BOLD_RED=f"\x1b[{bold_red_format}m"
    GRN=f"\x1b[{green_format}m"
    CYAN=f"\x1b[{cyan_format}m"
    BLUE=f"\x1b[{blue_format}m"
    YEL=f"\x1b[{yellow_format}m"
    MAG=f"\x1b[{magenta_format}m"
    #BOLD_GRN=f"\x1b[{bold_green_format}m"
    #REAL_WHT=f"\x1b[{white_format}m"

    col_dict={
    "blue": BLUE,
    "cyan": CYAN,
    "green": GRN,
    "red": RED,
    "yellow": YEL,
    "magenta":MAG
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

def assign_colour(item, colour=None):

    specials = ("location", "loc")
    cardinals=["north", "south", "east", "west"]
    game.colour_counter = game.colour_counter%len(cardinals)
    text_colour = None

    if isinstance(colour, (int, float)) and colour != None: # and colour <= len(cardinals)-1: cut the length part as it makes the entries of list len>4 colourless.
        colour=int(colour)%len(cardinals)
        colour=cardinals[int(colour)] # get the value from the list by index, so lists always have the same order (separate from the game.colour_counter, which loops but not per text line. This way the first through fourth option always have the same order unless they've another priority.)
        # This should stop the current issue where 'yes, no' are green and blue, then red and cyan next time, because the loop is 4 colours long. Would prefer it to be consistent.
        colour=cardinal_cols[colour]

    if colour in specials:
        if "loc" in colour:
            colour="green" # change it here to change all location text. Maybe a decent way to do it.

    if not colour:
        if item in cardinals:
            colour=cardinal_cols[item]
        elif loot.get_item(item):
            entry = loot.get_item(item)

            if entry and entry.get('text_col'):
                print("Item found.")
                if entry.get('text_col') != None:
                    colour=text_colour
            #if game.inv_colours.get(item):
            #    text_colour = game.inv_colours.get(item)
            if text_colour != None:
                colour=text_colour
            else:
                colour=cardinals[game.colour_counter]
                colour=cardinal_cols[colour]
                game.colour_counter += 1
                game.inv_colours[item]=colour # souldn't need this at all, only made it because name_col didn't work.
                loot.name_col(item, colour)
        else:
            colour=cardinals[game.colour_counter]
            colour=cardinal_cols[colour]
            game.colour_counter += 1

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
