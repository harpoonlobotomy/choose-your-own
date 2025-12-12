# print_tui

## $ == 5 spaces
## & == 5 underscores
## £ == 5 equals
## % == 5 dashes

## There are 8 'spacers' per line.

#   |##|  /                                                $INVENTORY $                                         $\   /              $PLAYER DATA              $\   /$              WORLD STATE              $$\  |##|

tui_lines = "screen_draft_expanding.txt"
no_of_spacers = 8
spacing = 0
get_longest=True # temporarily, later will be used to do auto spacing + centering.
longest_min = 0
tui_linelist = []

title_str = "Choose a Path"


def col_text(text:str="", colour:str=None):

## def apply_col_to_text(item, colour="green"): # is just this, copied from Choices.

    baseline_format=';'.join([str(0), str(37), str("40")]) ## Add more colours later
    #bold_white_format=';'.join([str(1), str(37), str("40")])
    red_format=';'.join([str(0), str(31), str("40")])
    #bold_red_format=';'.join([str(1), str(31), str("40")])
    green_format=';'.join([str(0), str(32), str("40")])
    b_green_format=';'.join([str(1), str(32), str("40")])
    u_green_format=';'.join([str(4), str(32), str("40")])
    cyan_format=';'.join([str(0), str(36), str("40")])
    u_cyan_format=';'.join([str(1), str(36), str("40")])
    blue_format=';'.join([str(0), str(34), str("40")])
    b_blue_format=';'.join([str(1), str(34), str("40")])
    u_blue_format=';'.join([str(4), str(34), str("40")])
    yellow_format=';'.join([str(0), str(33), str("40")])
    b_yellow_format=';'.join([str(1), str(33), str("40")])
    magenta_format=';'.join([str(0), str(35), str("40")])
    b_white_format=';'.join([str(1), str(37), str("40")])

    BASELINE=f"\x1b[{baseline_format}m"
    B_WHITE=f"\x1b[{b_white_format}m"
    RED=f"\x1b[{red_format}m"
    END="\x1b[0m"
    #BOLD_RED=f"\x1b[{bold_red_format}m"
    GRN=f"\x1b[{green_format}m"
    B_GRN=f"\x1b[{b_green_format}m"
    U_GRN=f"\x1b[{u_green_format}m"
    CYAN=f"\x1b[{cyan_format}m"
    U_CYAN = f"\x1b[{u_cyan_format}m"
    BLUE=f"\x1b[{blue_format}m"
    B_BLUE=f"\x1b[{b_blue_format}m"
    U_BLUE=f"\x1b[{u_blue_format}m"
    YEL=f"\x1b[{yellow_format}m"
    B_YEL=f"\x1b[{b_yellow_format}m"
    MAG=f"\x1b[{magenta_format}m"
    #BOLD_GRN=f"\x1b[{bold_green_format}m"
    #REAL_WHT=f"\x1b[{white_format}m"

    col_dict={
    "blue": BLUE,
    "b_blue": B_BLUE,
    "cyan": CYAN,
    "u_cyan": U_CYAN,
    "green": GRN,
    "red": RED,
    "yellow": YEL,
    "b_yellow": B_YEL,
    "magenta":MAG,
    "description": B_YEL,
    "deco_1": B_GRN,#YEL,
    "title": B_YEL,
    "pipe": GRN,
    "underscore": YEL,
    "equals": U_BLUE,
    "dash": U_GRN,
    "hash": GRN,
    "slash": YEL,
    "up": GRN,
    "title_white": B_WHITE
    }

    if colour == None:
        return text

    if col_dict.get(colour):
        col=col_dict.get(colour)

    else:
        col=BASELINE

    col_text = f'{col}{text}{END}'

    return col_text

def col_text_partial(text:str="", symbol:str="", col:str=""):

    #print(f"Col text partial: text: {text}, symbol: {symbol}, col: {col}")
    individual = [" | ", "\\", "//", "|"]
    complex_individual = ["##", "|##|", "|##|/", "|##|\\", "/|##|", "\\|##|"]
    all = ["=", "-", "_"]
    excl = ["-===", "===-"]

    if symbol == "|##|":
        text=text.replace("|", col_text("|", "b_yellow"))
        text=text.replace("##", col_text("##", "hash"))
    elif symbol == "^":
        text=text.replace(symbol, col_text("=", col))

    elif symbol == "titles":
        texts = ["INVENTORY", "PLAYER DATA", "WORLD STATE"]
        for item in texts:
            text=text.replace(item, col_text(item, col))
    else:
        if symbol in "all" and (symbol * 10) in text:
            symbol_start = text.find(symbol)
            symbol_end = text.rfind(symbol)
            symbol_text = text[symbol_start+1:symbol_end]
            text=text.replace(symbol_text, col_text(symbol_text, col))
        else:
            if col == "dash":
                col = "pipe"
            text=text.replace(symbol, col_text(symbol, col)) ## I want to reimplement the 'all' section, to avoid recolouring every character at once.
        #if symb in complex_individual:
        #    text=text.replace(symb, col_text(symb, colour=col[i]))
#
        #if symb in individual:
        #    #symb = symb.strip()
        #    #symb = symb.rstrip()
        #    text=text.replace(symb, col_text(symb, colour="magenta"))
#
        #if symb in all:
        #    text=text.replace(symb, col_text(symb, colour=col[i]))
        #    #text=col_text(text, colour=col[i])
        #if symb in excl:
        #    text=text.replace(symb, col_text(symb, colour=col[i]))


    return text

def title_text(line):

## title can be adjusted, but currenlty the length is `                     `. Shorter or longer will break spacing. Will adapt for this later.
    title_start = line.find('~')
    title_end = line.rfind('~')
    title_text = line[title_start+1:title_end]
    title_length = len(title_text)
    if len(title_str) > title_length:
        diff = len(title_str) - title_length
        print(f"Title is too long by {diff} characters. Adjust hardcoded title line.")
    #if len(title_str) < title_length:
    diff = title_length - len(title_str)
    title= (" " * int(diff/2)) + title_str + (" " * int(diff/2))
    if len(title) < title_length:
        title = title + " "
    title = col_text(title, colour="title")

    pre_title_0 = line[title_start-5:title_start]
    post_title_0 = line[title_end+1:title_end+6]
    pre_title = col_text(pre_title_0, colour=None)
    post_title = col_text(post_title_0, colour=None)

    #print(f"Pre title_start_2: {pre_title}")
    #print(f"Pre title_end: {post_title}")
    line = line[:title_start-len(pre_title_0)] + pre_title + " " + title + " " + post_title + line[title_end+len(post_title_0)+1:]#+ (" " * int(diff/4)) + title_str + (" " * int(diff/4)) + line[:title_end]

    return line



def get_terminal_cols_rows():

    from shutil import get_terminal_size
    cols, rows = get_terminal_size()
    #print(f"cols: {cols}, rows: {rows}")
    return cols, rows

def make_centred_list(input_list:list, linelength):
    cols, rows = get_terminal_cols_rows()
    spare_cols = cols-linelength
    spacing=int(spare_cols/no_of_spacers)
    plain_list = []
    new_list=[]
    up_lines = []
    list_length = len(input_list)
    additional_rows = rows-list_length-2
    #print(f"Additional rows: {additional_rows}")
    #print(f"Length of list: {len(input_list)}")
    longer_list = []
    for line in input_list:
        #print(f"Line: {line}")
        if '+' in line:
            line_str = "  |##| $$  -| $$                                                                                                                                                                                    $$ |-   $$ |##|"
            for number in range(0, additional_rows):
                longer_list.append(line_str)
        else:
            longer_list.append("\n" + line)
#    for line in new_list:
#        print(line)
#    exit()
    #print(f"Length of list: {len(longer_list)}")
    for i, line in enumerate(longer_list):
        if "&" in line:
            line = line.replace('&', ('_' * spacing))
        if '*' in line:
            line = line.replace('*', ('=' * spacing))
        if '%' in line:
            line = line.replace('%', ('-' * spacing))
        plain_line=line
        if "~" in line:
            line = title_text(line)
        if "_" in line:
            line = col_text_partial(line, symbol="_", col="underscore")
        excl="===-"
        exl_2="-==="
        if excl in line or exl_2 in line:
            line = col_text_partial(line, symbol=excl, col="deco_1")
            line = col_text_partial(line, symbol=exl_2, col="deco_1")

        elif "=" in line:
                line = col_text_partial(line, symbol="=", col="equals")
        elif "-" in line:
            line = col_text_partial(line, symbol="-", col="dash")
        if "|##|" in line:
            line = col_text_partial(line, symbol="|##|", col="hash")
        if " | " in line:
            line = col_text_partial(line, symbol=" | ", col="pipe")
        if "/" in line:
            line = col_text_partial(line, symbol="/", col="slash")
        if "\\" in line:
            line = col_text_partial(line, symbol="\\", col="slash")
        line = line.replace('$', (' ' * spacing))
        plain_line=plain_line.replace('$', (' ' * spacing))
        if "^" in line:
            line = line.replace('@', '^' * spacing)
            plain_line=plain_line.replace('@', '^' * spacing)
            up_lines.append(i)
            text_area_start = plain_line.find('^')
            text_area_end = plain_line.rfind('^')
            #print(f"Text area start: {text_area_start}")
            #print(f"Text area end: {text_area_end}")
            line = col_text_partial(line, symbol="^", col="up")

        if "INVENTORY" in line:
            line = col_text_partial(line, symbol="titles", col="title_white")
        if longest_min + (no_of_spacers * spacing) < cols-1:
            extra_spaces = cols - (longest_min + (no_of_spacers * spacing) -1)
            line = (' ' * int(extra_spaces/2)) + line + (' ' * int(extra_spaces/2))
        line = line.replace('\n', '')
        plain_line = plain_line.replace('\n', '')
        new_list.append(line)
        plain_list.append(plain_line)
        #print(line)

    return new_list, plain_list, text_area_start, text_area_end, up_lines

with open(tui_lines) as f:
    for line in f:
        tui_linelist.append(line.rstrip('\n'))
        if get_longest:
            if len(line) > longest_min:
                longest_min = len(line)-no_of_spacers

import os
os.system("cls")

if get_longest:
    #print(f"Longest line without adding spacers: {longest_min}")
    tui_linelist, plain_list, text_area_start, text_area_end, up_lines = make_centred_list(tui_linelist, longest_min)

## longest line: 206
def print_screen():
    for line in tui_linelist:
        print(line)#, end='')


## |##|'                                                                                              -===|     Choose a Path     |===-                                                                                        '|##|
#print(f"Text area start: {text_area_start}")
#print(f"Text area end: {text_area_end}")

#print(tui_linelist)

def print_at_start_of_line(text_area_start, text_area_end, up_lines):

    print_screen()
    print("\033[s")

    first_row=None
    last_row=None
    text_block_start=text_area_start+7

    printable_lines = list(range((up_lines[0]+3), (up_lines[1])))
    #print(f"Printable lines: {printable_lines}")
    import random
    #print(f"Text area end: {text_area_end}, text_area_start: {text_area_start}")
    letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    for i, row in enumerate(printable_lines):
        #print("len of letters: ", len(letters))
        #print(f"text_area_end: {text_area_end}, text area start: {text_area_start}")
        printline = random.sample(letters, int(text_area_end)-(text_area_start+7))
        printline=''.join(printline)
        line=(f"\033[{row};{str(int(text_area_start+7))}H {printline}")
        if i==0:
            first_row=row
        print(line, end='')
        last_row=row

    print("\033[u")
    return first_row, last_row, text_block_start

first_row, last_row, text_block_start = print_at_start_of_line(text_area_start, text_area_end, up_lines)

#print(f"First row: {first_row}, last row: {last_row}, start_block_start: {text_block_start}")
print(f"\033[6A", end='')
input_str=col_text("INPUT:  ", "title_white")
print(f"\033[{int(text_block_start-7)}C{input_str}", end='')
# you can print "\033[1;2H" to position the cursor. It will move the cursor and will not print anything on screen. The values 1 and 2 are the row and the column, so change them to use different positions.
input()
