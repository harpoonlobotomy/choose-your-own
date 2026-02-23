#printing.py

import config
white_bg = config.white_bg

def print_col(text, col, bg, invert=False):
    """Simple function to return a coloured text string. col and bg must be given as ints (30-39 and 40-49 respectively). Always outputs underlined text.\n'invert=True' will swap the bg and colour options."""
    if bg == False or white_bg == False:
        bg = 40
    else:
        bg = 47

    if invert:
        bg_tmp = col + 10
        col = bg - 10
        bg = bg_tmp

    print(f"\033[4;{col};{bg}m{text}\033[0m")

def print_red(text, bg=True, invert=False):
    colour = 31
    print_col(text, colour, bg, invert)

def print_green(text, bg=True, invert=False):

    colour = 32
    print_col(text, colour, bg, invert)

def print_blue(text, bg=True, invert=False):

    colour = 34
    print_col(text, colour, bg, invert)

def print_yellow(text, bg=False, invert=False):

    colour = 33
    print_col(text, colour, bg, invert)

def printkind(text):
    """Prints `Text: {text}, type: {type(text)}` in yellow text."""
    text = f"Text: {text}, type: {type(text)}"
    print_yellow(text, invert=True)
