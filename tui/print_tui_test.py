# print_tui

## $ == 5 spaces
## & == 5 underscores
## £ == 5 equals
## % == 5 dashes

## There are 8 'spacers' per line.

#   |##|  /                                                $INVENTORY $                                         $\   /              $PLAYER DATA              $\   /$              WORLD STATE              $$\  |##|

tui_lines = "screen_draft_expanding.txt"
#no_of_spacers = 10
global spacing
spacing = 0
get_longest=True # temporarily, later will be used to do auto spacing + centering.
longest_min = 0
tui_linelist = []
END="\x1b[0m"
RESET = "\033[0m"
HIDE = "\033[?25l"
SHOW = "\033[?25h"

title_str = "Choose a Path"

### UI blocking ###
global ui_blocking
ui_blocking = {"inv_start":None, "inv_end":None, "playerdata_start":None, "playerdata_end":None, "worldstate_start":None, "worldstate_end":None, "input_line":None, "text_block_start":None, "text_block_end":None, "commands_start":None, "commands_end":None}


def col_text(text:str="", colour:str=None):
    bg=40
    hash_bg=44
## def apply_col_to_text(item, colour="green"): # is just this, copied from Choices.

    baseline_format=';'.join([str(0), str(37), str(bg)]) ## Add more colours later
    #bold_white_format=';'.join([str(1), str(37), str("40")])
    red_format=';'.join([str(0), str(31), str(bg)])
    #bold_red_format=';'.join([str(1), str(31), str("40")])
    green_format=';'.join([str(0), str(32), str(bg)])
    b_green_format=';'.join([str(1), str(32), str(bg)])
    u_green_format=';'.join([str(4), str(32), str(hash_bg)])
    bg_green_format=';'.join([str(0), str(32), str(hash_bg)])
    cyan_format=';'.join([str(0), str(36), str(bg)])
    b_cyan_format=';'.join([str(1), str(36), str(bg)])
    blue_format=';'.join([str(0), str(34), str(bg)])
    b_blue_format=';'.join([str(1), str(34), str(bg)])
    u_blue_format=';'.join([str(4), str(32), str(hash_bg)])
    yellow_format=';'.join([str(0), str(33), str(bg)])
    bg_yellow_format=';'.join([str(0), str(33), str(hash_bg)])
    b_yellow_format=';'.join([str(1), str(33), str(bg)])
    magenta_format=';'.join([str(0), str(35), str(bg)])
    b_white_format=';'.join([str(1), str(37), str(bg)])

    BASELINE=f"\x1b[{baseline_format}m"
    B_WHITE=f"\x1b[{b_white_format}m"
    RED=f"\x1b[{red_format}m"

    #BOLD_RED=f"\x1b[{bold_red_format}m"
    GRN=f"\x1b[{green_format}m"
    B_GRN=f"\x1b[{b_green_format}m"
    U_GRN=f"\x1b[{u_green_format}m"
    BG_GRN=f"\x1b[{bg_green_format}m"
    CYAN=f"\x1b[{cyan_format}m"
    U_CYAN = f"\x1b[{b_cyan_format}m"
    BLUE=f"\x1b[{blue_format}m"
    B_BLUE=f"\x1b[{b_blue_format}m"
    U_BLUE=f"\x1b[{u_blue_format}m"
    YEL=f"\x1b[{yellow_format}m"
    B_YEL=f"\x1b[{b_yellow_format}m"
    BG_YEL=f"\x1b[{bg_yellow_format}m"
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
    "deco_1": B_GRN,
    "title": B_YEL,
    "pipe": GRN,
    "underscore": YEL,
    "equals": U_BLUE,
    "dash": GRN,
    "hash": BG_GRN,
    "slash": YEL,
    "up": GRN,
    "title_white": B_WHITE,
    "bg_yellow": BG_YEL
    }


    if col_dict.get(colour):
        col=col_dict.get(colour)
    else:
        col=BASELINE

    if text == None:
        col = BASELINE ## Hadded this here, stops it randomly colouring a couple of blocks off to the side with the previously used blue backgrounds.
        return f"{col}{text}{END}"
    if colour == None:
        return f"{col}{text}{END}"

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
            ui_blocking[f"{block_part}start"] = (col, area_start)
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
        text=text.replace("!", col_text(":", "yellow"))

    elif symbol == "titles":
        texts = ["INVENTORY", "PLAYER DATA", "WORLD STATE"]
        for item in texts:
            text=text.replace(item, col_text(item, col))
    else:
        #if symbol in "all" and (symbol * 10) in text: ## commented out because using it leaves some of the `all` symbols uncoloured.
        #    symbol_start = text.find(symbol)
        #    symbol_end = text.rfind(symbol)
        #    symbol_text = text[symbol_start+1:symbol_end]
        #    text=text.replace(symbol_text, col_text(symbol_text, col))
        #else:
#            if col == "dash":
#                col = "pipe"
            text=text.replace(symbol, col_text(symbol, col)) ## I want to reimplement the 'all' section, to avoid recolouring every character at once.
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
    ### If you change the size of the terminal after a run, the next run will have coloured bgs off to the right side. On the second run (without changing the terminal size again), it fixes. need to figure out how to fix this.
    from shutil import get_terminal_size
    import os
    os.system("cls") ##<-- seems to fix the above issue.
    cols, rows = get_terminal_size()
    return cols, rows

def make_centred_list(input_list:list, linelength, ui_blocking):
    cols, rows = get_terminal_cols_rows()
    spare_cols = cols-linelength
    global spacing

    spacing=int(spare_cols/no_of_spacers)
    if spacing <= 0:
        spacing = 0
    plain_list = []
    new_list=[]
    up_lines = []
    list_length = len(input_list)
    additional_rows = rows-list_length-2
    longer_list = []
        ## There has to be a much better way of doing this. but this does work... eh idk.

    for line in input_list:
        if '+' in line:
            #line_str = "  |##| $$  -| $$                                                                                                                                                                                    $$ |-   $$ |##|"
            for number in range(0, additional_rows+1):
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
            line = col_text_partial(line, symbol="titles", col="yellow")

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

    return new_list, plain_list, up_lines, text_box_count

with open(tui_lines) as f:
    counter=0
    for line in f:
        if counter==0:
            no_of_spacers = line.count("&")
        if counter == 19:
            line_str = line.rstrip('\n')
        tui_linelist.append(line.rstrip('\n'))
        if get_longest:
            if len(line) > longest_min:
                longest_min = len(line)-no_of_spacers
        counter += 1

import os
os.system("cls")

if get_longest:
    #print(f"ui blocking: {ui_blocking}, type: {type(ui_blocking)}")
    tui_linelist, plain_list, up_lines, text_box_count = make_centred_list(tui_linelist, longest_min, ui_blocking)

    ui_blocking["input_line"] = up_lines[1]+3

printable_lines = list(range((up_lines[0]+3), (up_lines[1])))
ui_blocking["printable_lines"]=printable_lines

## longest line: 206
def print_TUI():
    for line in tui_linelist:
        print(line)#, end='')


## |##|'                                                                                              -===|     Choose a Path     |===-                                                                                        '|##|
#print(f"Text area start: {text_area_start}")
#print(f"Text area end: {text_area_end}")

#print(tui_linelist)

import time
def print_in_text_box(up_lines, text:str="", reverse_txt:list=None, print_from_bottom=False, slow=False):
    first_row=None
    last_row=None
    text_block_start_col=(up_lines[0]+3)
    _, left_textblock_edge = ui_blocking["text_block_start"]
    _, right_textblock_edge = ui_blocking["text_block_end"]
    textblock_width = right_textblock_edge-left_textblock_edge+1
    printable_lines = list(range((up_lines[0]+3), (up_lines[1])))
    from rich.console import Console
    console = Console(record=True)

    if print_from_bottom:
        last_line = len(printable_lines)
        for i, row_no in enumerate(printable_lines):
            from rich.control import Control
            console.control(Control.move_to(x=left_textblock_edge, y=row_no-1))
            if i == last_line-1:
                test=text
            elif reverse_txt and i!=last_line-1:
                reverse_txt=reverse_txt
                test=reverse_txt[i]
            else:
                test = " "
            if isinstance(text, str):
                if len(text) < textblock_width:
                    text = text + (" " * (textblock_width-len(text)))
            console.print(test)
            if slow:
                time.sleep(.08)
        console_text = console.export_text()
        return console_text

    import random
    print_once = False
    for i, row in enumerate(printable_lines):
        print(f"\033[{row};{str(left_textblock_edge)}H")
        if print_once:
            text = " "
        if text == "":
            import string
            result = random.choices(string.ascii_uppercase, k=right_textblock_edge)
            printline = ''.join(result)
        else:
            if isinstance(text, str):
                if len(text) < right_textblock_edge:
                    text = text + (" " * (right_textblock_edge-len(text)))
                printline = text
                print_once = True

        line=(f"\033[{row};{str(left_textblock_edge)}H{printline}")
        if i==0:
            first_row=row
        print(line, end='')
        if slow:
            time.sleep(.08)
        last_row=row

    print("\033[u")
    return first_row, last_row, text_block_start_col


def prep_datablocks(text):
    new_text=[]
    for line in text:
        line=line.replace('$', (' ' * spacing))
        new_text.append(line)
    return new_text

def add_infobox_data(backgrounds = False):

#ui_blocking = {"inv_start":None, "inv_end":None, "playerdata_start":None, "playerdata_end":None, "worldstate_start":None, "worldstate_end":None, "input_line":None}
    #part = "inv_"
    #part = "worldstate_"
    #part = "playerdata_"
    bg_col = 40
    if backgrounds:
        bg_col = 44

    def overprint_part(part, text, inv):
        top_row, left_col, = ui_blocking[f"{part}start"]
        bottom_row, right_col, = ui_blocking[f"{part}end"]
        r_counter=0
        if inv == None:
            top_row = top_row-1
            bottom_row = bottom_row + 2
            left_col = left_col-3
            right_col = right_col+4
        else:
            bottom_row = bottom_row + 1
        for row in range(top_row, bottom_row):
            if inv != None:
                ## Need to print inventory items by the numbers.
                # Can remove the numbers and just add spacers between entries, but need to pay attention to r_col and "make newline" if itll hit.
                pass
            c_counter=0
            for col in range(left_col, right_col):
                bg_format=';'.join([str(1), str(33), str(bg_col)])
                if part == "commands_":
                    bg_format=';'.join([str(0), str(33), str(bg_col)])

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

        text=prep_datablocks(text) ## makes sure the inventory etc have the same internal spacing to match the rest of the UI

        overprint_part(part, text, inv)
    for part in ["text_block_"]:
        overprint_part(part, None, None)


def advance_list(console_text, not_reverse=False): ## turns out reversing it was the opposite thing I needed. Whoops. Will rename this later, seeing as the reversal is why it was behaving so strangely before. Now it advances properly.

    cleaned_list = []
    console_list = console_text.split("\n")
    for i, entry in enumerate(console_list):
        if i == 0:
            continue
        elif entry == "":
            continue
        else:
            cleaned_list.append(entry)
    return list(cleaned_list)



def clean_intro_block(intro_list=None):

    cleaned_list = []

    # logo == 15 lines
    # with text = 20 lines

    #if linecount < 20:
    #   stop adding lines after 15, so it's either all or no test lines.

    ## Will be adding the text to the side instead anyway, there's already a substantial minimum width.
    # maybe we check if there's more hor or vert space, and use a horizontal or vertical arrangement of logo + intro text.


## NOTE: Currently, min text block width is 162. If less than this, everything breaks. // Now 158. Going to add yet more spacers to try to get the functional size smaller.
    ## Downside of this is, currently the 'instructions' box is hardcoded. Need to make a flexible version. Or figure out how to make the terminal window be either a set smaller size or fullscreen. (that said, on a larger monitor than mine, full screen might still break.)

## if wide: widest line is 8 (counting from 1)

    linecount = ui_blocking["printable_lines"]
    _, start_offset = ui_blocking["text_block_start"]
    _, end_offset = ui_blocking["text_block_end"]
    text_block_width = end_offset-start_offset
    #print(f"Text block width: {text_block_width}")
    if intro_list:
        if len(linecount) < 20:
            #print("Intro list less than 20")
            counter = 0
            temp_list=[]
            while counter < 15:
                for line in intro_list:
                    temp_list.append(line)
                    counter += 1
            intro_list = temp_list

        if len(intro_list) < len(linecount):
            diff = len(linecount) - len(intro_list)
            add_to_start = int(diff/2)
            add_to_end = diff-add_to_start
        else:
            add_to_start=0
            add_to_end=0

        start_list = []
        end_list = []
        if add_to_start > 0:
            for _ in range(add_to_start):
                start_list.append("")
            for _ in range(add_to_end):
                end_list.append("")

        sample_length = intro_list[4]
        centring = " " * int((text_block_width-len(sample_length))/2)
        for text in intro_list:
            if isinstance(text, str):
                if len(text) < text_block_width:
                    text = centring + text + centring
                    cleaned_list.append(text)

        total_list = start_list + cleaned_list + end_list

    else: ## if no intro text, make a blank block.
        sample_length = text_block_width
        for _ in range(len(linecount)):
            text = (" " * sample_length)
            cleaned_list.append(text)
        total_list = cleaned_list

    return total_list
# you can print "\033[1;2H" to position the cursor. It will move the cursor and will not print anything on screen. The values 1 and 2 are the row and the column, so change them to use different positions.

def clear_print_area(intro):

    clean_intro_block(intro)


def print_text_from_bottom_up(input_list=None):
    text=None
    reversed_list=None
    slow_bool=False
    first_input_done=False

    def print_output(text="", reversed_list=None, slow=False):
        print(HIDE, end='')
        console_text = print_in_text_box(up_lines, text, reverse_txt=reversed_list, print_from_bottom=True, slow=slow) ## does not overwrite the rest of the line. // fixed, just adds spaces to the rest of the line.
        reversed_list = advance_list(console_text, not_reverse=True)
        return reversed_list

    if input_list:
        print_output(text="", reversed_list=input_list, slow=True)

    else:
        slow_bool=False
        while text not in ["done", "quit", "q", "exit", ""]:
            if not first_input_done:
                input_str = col_text("Please enter your name:  ", "title_white")
            else:
                input_str=col_text("INPUT:  ", "title_white")
            print(f"\033[{int(ui_blocking["input_line"])};{(up_lines[0]+3)+7}H{input_str}", end='')
            print("\033[s") ## instead of saving, maybe specifically save the cursor position for the input line. Not sure if that's beneficial or not. // Oh, I already did. 'input_line' in the dict. Duh.
            print(HIDE, end='')
            print(f"\033[u", SHOW, end='')
            text = input()
            if not first_input_done:
                while True:
                    first_input_done = True
                    player_name = text
                    print(f"\033[{int(ui_blocking["input_line"])};{(up_lines[0]+3)+7}H{'                                           '}", end='')
                    if isinstance(player_name, str) and len(player_name) > 1:
                        clean = clean_intro_block()
                        print_output(text="", reversed_list=clean, slow=True)
                        break
                    input_str = col_text("Please enter your name:  ", "title_white")
                    print(f"\033[{int(ui_blocking["input_line"])};{(up_lines[0]+3)+7}H{input_str}", end='')
                    text = input()

            else:
                reversed_list = print_output(text, reversed_list, slow=slow_bool)
            print(f"\033[u{'                                                                             '}", end='') # just here to wipe the previous input


def run_tui_intro():
    print_TUI()
    print("\033[s")
    add_infobox_data(backgrounds = False) ## will need to run again if numbers change. Currently the changes happen in 'datablocks.py', not locally.

    from datablocks import intro

    intro = clean_intro_block(intro)
    print_text_from_bottom_up(input_list=intro) # plays automatically to print intro text
    print_text_from_bottom_up()
    return ui_blocking

if "__main__" in __name__:
    run_tui_intro()

print(f"\033[5B", end='') ## return to end of screen when program ends to avoid overwriting, doesn't matter but is better aesthetically.


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#### https://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
