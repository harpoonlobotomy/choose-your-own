# print_tui

## $ == 5 spaces
## & == 5 underscores
## £ == 5 equals
## % == 5 dashes

## There are 8 'spacers' per line.

#   |##|  /                                                $INVENTORY $                                         $\   /              $PLAYER DATA              $\   /$              WORLD STATE              $$\  |##|

tui_lines = "screen_draft_expanding.txt"
no_of_spacers = 8
global spacing
spacing = 0
get_longest=True # temporarily, later will be used to do auto spacing + centering.
longest_min = 0
tui_linelist = []
END="\x1b[0m"
title_str = "Choose a Path"

### UI blocking ###
global ui_blocking
ui_blocking = {"inv_start":None, "inv_end":None, "playerdata_start":None, "playerdata_end":None, "worldstate_start":None, "worldstate_end":None, "input_line":None, "text_block_start":None, "text_block_end":None, "commands_start":None, "commands_end":None}


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

def col_text_partial(text:str="", plain_line="", ui_blocking:dict=(), symbol:str="", col:str=""):

    #print(f"Col text partial: text: {text}, symbol: {symbol}, col: {col}")
    individual = [" | ", "\\", "//", "|"]
    complex_individual = ["##", "|##|", "|##|/", "|##|\\", "/|##|", "\\|##|"]
    all = ["=", "-", "_"]
    excl = ["-===", "===-"]

 ## UI blocking
    ui_blocks = ["i", "w", "p", "c"]

    if symbol in ui_blocks:

        if symbol == 'i':
            block_part="inv_"
        elif symbol == "w":
            block_part = "worldstate_"
        elif symbol == "p":
            block_part = "playerdata_"
        elif symbol == "c":
            block_part = "commands_"

        if ui_blocking[f"{block_part}start"]==None:
            area_start = plain_line.find(symbol)
            # line number in `col`.
            ui_blocking[f"{block_part}start"] = (col, area_start+1)
            #print(f'ui_blocking["inv_start"]: {ui_blocking["inv_start"]}')
        else:
            area_end = plain_line.rfind(symbol)
            ui_blocking[f"{block_part}end"] = (col, area_end-1)
        text=text.replace(symbol, col_text(" ", None))
        return text

    if symbol == "|##|":
        text=text.replace("|", col_text("|", "b_yellow"))
        text=text.replace("##", col_text("##", "hash"))
    elif symbol == "^":
        text=text.replace(symbol, col_text("=", col))

    elif symbol == "!":
        text=text.replace("!", col_text(":", col))

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
    diff = title_length - len(title_str)
    title= (" " * int(diff/2)) + title_str + (" " * int(diff/2))
    if len(title) < title_length:
        title = title + " "
    title = col_text(title, colour="title")

    pre_title_0 = line[title_start-5:title_start]
    post_title_0 = line[title_end+1:title_end+6]
    pre_title = col_text(pre_title_0, colour=None)
    post_title = col_text(post_title_0, colour=None)

    line = line[:title_start-len(pre_title_0)] + pre_title + " " + title + " " + post_title + line[title_end+len(post_title_0)+1:]#+ (" " * int(diff/4)) + title_str + (" " * int(diff/4)) + line[:title_end]

    return line


def get_terminal_cols_rows():

    from shutil import get_terminal_size
    cols, rows = get_terminal_size()
    return cols, rows

def make_centred_list(input_list:list, linelength, ui_blocking):
    cols, rows = get_terminal_cols_rows()
    spare_cols = cols-linelength
    global spacing

    spacing=int(spare_cols/no_of_spacers)
    plain_list = []
    new_list=[]
    up_lines = []
    list_length = len(input_list)
    additional_rows = rows-list_length-2
    longer_list = []
    for line in input_list:
        if '+' in line:
            line_str = "  |##| $$  -| $$                                                                                                                                                                                    $$ |-   $$ |##|"
            for number in range(0, additional_rows):
                longer_list.append(line_str)
        else:
            longer_list.append("\n" + line)
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
        if "!" in line:
            line = col_text_partial(line, symbol="!", col="yellow")

        line = line.replace('$', (' ' * spacing))
        plain_line=plain_line.replace('$', (' ' * spacing))

        if "INVENTORY" in line:
            line = col_text_partial(line, symbol="titles", col="title_white")

        if "^" in line:
            line = line.replace('@', '^' * spacing)
            plain_line=plain_line.replace('@', '^' * spacing)
            up_lines.append(i)


        if longest_min + (no_of_spacers * spacing) < cols-1:
            extra_spaces = cols - (longest_min + (no_of_spacers * spacing) -1)
            line = (' ' * int(extra_spaces/2)) + line + (' ' * int(extra_spaces/2))
            plain_line = (' ' * int(extra_spaces/2)) + plain_line + (' ' * int(extra_spaces/2))

        if "^" in line:
            if ui_blocking["text_block_start"] == None:
                ui_blocking["text_block_start"] = (i+3, plain_line.find('^')+3)
            else:
                ui_blocking["text_block_end"] = (i-1, plain_line.rfind('^')-3)
            text_area_start = plain_line.find('^')
            text_area_end = plain_line.rfind('^')
            text_box_count=plain_line.count("^")
            line = col_text_partial(line, symbol="^", col="up")

    #### INVENTORY BOX ####
        ui_blocks = ["i", "w", "p", "c"]
        for block in ui_blocks:
            if block in line:
                line = col_text_partial(line, plain_line, ui_blocking, symbol=block, col=i+1)
        line = line.replace('\n', '')
        plain_line = plain_line.replace('\n', '')
        new_list.append(line)
        plain_list.append(plain_line)

    return new_list, plain_list, text_area_start, text_area_end, up_lines, text_box_count

with open(tui_lines) as f:
    for line in f:
        tui_linelist.append(line.rstrip('\n'))
        if get_longest:
            if len(line) > longest_min:
                longest_min = len(line)-no_of_spacers

import os
os.system("cls")

if get_longest:
    #print(f"ui blocking: {ui_blocking}, type: {type(ui_blocking)}")
    tui_linelist, plain_list, text_area_start, text_area_end, up_lines, text_box_count = make_centred_list(tui_linelist, longest_min, ui_blocking)

    ui_blocking["input_line"] = up_lines[1]+3

## longest line: 206
def print_TUI():
    for line in tui_linelist:
        print(line)#, end='')


## |##|'                                                                                              -===|     Choose a Path     |===-                                                                                        '|##|
#print(f"Text area start: {text_area_start}")
#print(f"Text area end: {text_area_end}")

#print(tui_linelist)

def print_at_start_of_line(text_area_start, text_area_end, up_lines):

    first_row=None
    last_row=None
    text_block_start_col=(up_lines[0]+3)
    inset = int(text_area_start+8)
    end_offset = int(text_box_count-11)
    #if end_offset > inset:
    #    inset += 1
    #    end_offset -= 1
    printable_lines = list(range((up_lines[0]+3), (up_lines[1])))
    #print(f"Printable lines: {printable_lines}")
    import random
    #print(f"Text area end: {text_area_end}, text_area_start: {text_area_start}")
    letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    for i, row in enumerate(printable_lines):
        #print("len of letters: ", len(letters))
        #print(f"text_area_end: {text_area_end}, text area start: {text_area_start}")
        printline = random.sample(letters, end_offset)#int(text_area_end)-(text_area_start+7))
        printline=''.join(printline)

        line=(f"\033[{row};{str(inset)}H {printline}")
        #line=(f"\033[{row};{str(int(text_area_start+7))}H {printline}")
        if i==0:
            first_row=row
        print(line, end='')
        last_row=row

    print("\033[u")
    return first_row, last_row, text_block_start_col


def prep_datablocks(text):
    new_text=[]
    for line in text:
        line=line.replace('$', (' ' * spacing))
        new_text.append(line)
    return new_text

def overwrite_infoboxes():

#ui_blocking = {"inv_start":None, "inv_end":None, "playerdata_start":None, "playerdata_end":None, "worldstate_start":None, "worldstate_end":None, "input_line":None}
    #part = "inv_"
    #part = "worldstate_"
    #part = "playerdata_"

    def overprint_part(part, text, inv):
        top_row, left_col, = ui_blocking[f"{part}start"]
        bottom_row, right_col, = ui_blocking[f"{part}end"]
        r_counter=0

        for row in range(top_row, bottom_row+1):
            if inv != None:
                ## Need to print inventory items by the numbers.
                # Can remove the numbers and just add spacers between entries, but need to pay attention to r_col and "make newline" if itll hit.
                pass
            c_counter=0
            for col in range(left_col, right_col+1):

                bg_format=';'.join([str(0), str(37), str("44")])
                bg=f"\x1b[{bg_format}m"
                if text != None:
                    char = text[r_counter][c_counter-1:c_counter]
                    if char == "*":
                        coloured = f'{bg}{" "}{END}'
                        #### future marking for stat data
                    else:
                        coloured = f'{bg}{char}{END}'
                else:
                    coloured = f'{bg}{" "}{END}'
                print(f"\033[{row};{col}H{coloured}") ### this works now
                c_counter+=1
            r_counter+=1

    from datablocks import inv_, worldstate_, playerdata_, inventory_items, commands_
    inv=None
    for part in ["inv_", "worldstate_", "playerdata_", "commands_"]:
        if part == "inv_":
            text=inv_
            inv = inventory_items
        elif part == "worldstate_":
            text=worldstate_
        elif part == "playerdata_":
            text=playerdata_
        elif part == "commands_":
            text=commands_
        #text=db[part]
        text=prep_datablocks(text)
        #print(f"Text: ")
        #for line in text:
        #    print(line)
        #exit()
        overprint_part(part, text, inv)
    for part in ["text_block_"]:
        overprint_part(part, None, None)


## print TUI
print_TUI()
print("\033[s")
overwrite_infoboxes()


#first_row, last_row, text_block_start_col = print_at_start_of_line(text_area_start, text_area_end, up_lines)

#print(f"First row: {first_row}, last row: {last_row}, start_block_start: {text_block_start}")

## go to inventory block and mark it out:

#row, column = ui_blocking["inv_start"] ## top left corner of inventory box
#print(f"\033[{row};{column}HI") ### this works now
#
#row, column = ui_blocking["inv_end"] ## bottom right corner of inventory box
#print(f"\033[{row};{column}HI")





#print(f"\033[6A", end='')
input_str=col_text("INPUT:  ", "title_white")
print(f"\033[{int(ui_blocking["input_line"])};{(up_lines[0]+3)+7}H{input_str}", end='')


# you can print "\033[1;2H" to position the cursor. It will move the cursor and will not print anything on screen. The values 1 and 2 are the row and the column, so change them to use different positions.
input()
print(f"\033[5B", end='')




#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#### https://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
