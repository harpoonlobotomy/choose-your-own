## utilities to be used by any script at any point

## colour selected string

from choices import loot
from set_up_game import game

def col_text(text:str="", colour:str=None):

## def apply_col_to_text(item, colour="green"): # is just this, copied from Choices.

    baseline_format=';'.join([str(0), str(37), str("40")]) ## Add more colours later
    #bold_white_format=';'.join([str(1), str(37), str("40")])
    red_format=';'.join([str(0), str(31), str("40")])
    #bold_red_format=';'.join([str(1), str(31), str("40")])
    green_format=';'.join([str(0), str(32), str("40")])
    #bold_green_format=';'.join([str(1), str(32), str("40")])
    cyan_format=';'.join([str(0), str(34), str("40")])
    blue_format=';'.join([str(0), str(36), str("40")])


    BASELINE=f"\x1b[{baseline_format}m"
    RED=f"\x1b[{red_format}m"
    END="\x1b[0m"
    #BOLD_RED=f"\x1b[{bold_red_format}m"
    GRN=f"\x1b[{green_format}m"
    CYAN=f"\x1b[{cyan_format}m"
    BLUE=f"\x1b[{blue_format}m"
    #BOLD_GRN=f"\x1b[{bold_green_format}m"
    #REAL_WHT=f"\x1b[{white_format}m"

    col_dict={
    "blue": BLUE,
    "cyan": CYAN,
    "green": GRN,
    "red": RED
    }

    if col_dict.get(colour):
        col=col_dict.get(colour)
    else:
        col=BASELINE

    col_text = f'{col}{text}{END}'

    return col_text


cardinal_cols = {
    "north":"red",
    "south":"blue",
    "east": "green",
    "west": "cyan"
}

def assign_colour(item, colour=None):

    cardinals=["north", "south", "east", "west"]
    game.colour_counter = game.colour_counter%len(cardinals)
    text_colour = None

    if not colour:
        if item in cardinals:
            colour=cardinal_cols[item]
        elif loot.get_item(item):
            if game.inv_colours.get(item):
                text_colour = game.inv_colours.get(item)
            if text_colour != None:
                colour=text_colour
            else:
                colour=cardinals[game.colour_counter]
                colour=cardinal_cols[colour]
                game.colour_counter += 1
                game.inv_colours[item]=colour
        else:
            colour=cardinals[game.colour_counter]
            colour=cardinal_cols[colour]
            game.colour_counter += 1

    coloured_text=col_text(item, colour)
    return coloured_text

def col_list(list:list=[], colour:str=None):
    coloured_list=[]

    for item in list:
        coloured_text= assign_colour(item, colour)

        #coloured_text=col_text(item, colour)
        coloured_list.append(coloured_text)
    return coloured_list
