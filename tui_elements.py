from layout import state
from tui.colours import Colours
from misc_utilities import assign_colour
from time import sleep
import os

linelength = 0
END="\x1b[0m"
RESET = "\033[0m"
HIDE = "\033[?25l"
SHOW = "\033[?25h"


title_str = "Choose a Path"

### UI blocking ###
#global ui_blocking
#ui_blocking = {"inv_start":None, "inv_end":None, "playerdata_start":None, "playerdata_end":None, "worldstate_start":None, "worldstate_end":None, "input_line":None, "text_block_start":None, "text_block_end":None, "commands_start":None, "commands_end":None}


os.system("cls")

def col_text_partial(text:str="", symbol:str="", col:str="", not_end=False): ## needs to use the misc_utility colours, but doesn't yet.

    if symbol == "|##|":
        text=text.replace("|", assign_colour("|", "b_yellow"))
        text=text.replace("##", assign_colour("##", "hash"))
    elif symbol == "^":
        text=text.replace(symbol, assign_colour("=", col))
    elif symbol == "!":
        text=text.replace("!", assign_colour(":", "yellow"))

    elif symbol == "titles":
        texts = ["INVENTORY", "PLAYER DATA", "WORLD STATE"]
        for item in texts:
            text=text.replace(item, assign_colour(item, col, no_reset = not_end))
    else:
        text=text.replace(symbol, assign_colour(symbol, col, no_reset = not_end)) ## I want to reimplement the 'all' section, to avoid recolouring every character at once.

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
    title = assign_colour(title, "b_title")

    pre_title_0 = line[title_start-5:title_start]
    post_title_0 = line[title_end+1:title_end+6]
    pre_title = assign_colour(pre_title_0, "blue")
    post_title = assign_colour(post_title_0, "blue")

    line = line[:title_start-len(pre_title_0)] + pre_title + " " + title + " " + post_title + line[title_end+len(post_title_0)+1:]#+ (" " * int(diff/4)) + title_str + (" " * int(diff/4)) + line[:title_end]

    return line


def make_coloured_list(input_list:list, title_block=False):

    if title_block:
        spacing=0
    else:
        spacing = state.spacing

    new_list=[]
    longer_list = []

    if not title_block:
        for line in input_list:
            longer_list.append("\n" + line)
    else:
        longer_list = input_list


    symbol_dict = {
        "|##|": {"to_print":"|##|", "col":"hash"},
        " | ": {"to_print":" | ", "col":"pipe"},
        "/": {"to_print": "/", "col":"slash"},
        "\\": {"to_print": "\\", "col":"slash"},
        "!": {"to_print": "!", "col":"yellow"},
        "_": {"to_print": "_", "col": "underscore"}
    }

    void_dict = { #"exclude": "|##|",
       "#": {"to_print":"#", "col":"title_bg"},
       "$": {"to_print":"$", "col":"b_yellow"},
       "|": {"to_print": "|", "col":"yellow"},
       "/": {"to_print": "/", "col":"yellow"},
       "\\": {"to_print": "\\", "col":"yellow"},
       "=": {"to_print": "=", "col":"yellow"},
       "_": {"to_print": "_", "col":"yellow"},

    }
    for line in longer_list:
        line = col_text_partial(line, line, "yellow")

        if title_block:
            for item in void_dict:
                if item in line:
                    line = col_text_partial(line, symbol=void_dict[item]["to_print"], col=void_dict[item]["col"])

        else:
            if "~" in line:
                line = title_text(line)

            excl="===-"
            exl_2="-==="
            if excl in line:
                line = col_text_partial(line, symbol=excl, col="deco")
                line = col_text_partial(line, symbol=exl_2, col="deco")

            elif "=" in line: ## make this a dict.
                line = col_text_partial(line, symbol="=", col="equals") ## These ones done separately to not mess with the title edges.
            elif "-" in line:
                line = col_text_partial(line, symbol="-", col="dash")

            for item in symbol_dict:
                if item in line:
                    line = col_text_partial(line, symbol=symbol_dict[item]["to_print"], col=symbol_dict[item]["col"])

            if not title_block:
                line = line.replace('$', (' ' * spacing))

            if "INVENTORY" in line:
                line = col_text_partial(line, symbol="titles", col="yellow")

            if not title_block:
                if "^" in line:
                    line = col_text_partial(line, symbol="^", col="up")

        #### INVENTORY BOX ####
            line = line.replace('\n', '')
        new_list.append(line)

    return new_list


def print_TUI(tui_linelist):

    for line in tui_linelist:
        print(line)
        sleep(.02)


def print_in_text_box(up_lines, text:str="", text_list:list=None, print_console=False, slow_lines=False, slow_char=False): ## Cannot use this with ansi codes as it breaks. Need to either go all in on 'rich' or not.

    ## I just gutted this a bit. Might regret that later.
    # Have now decided to make a new separate function, because this one's too damn fragile.
    first_row=None
    last_row=None
    text_block_start_col=(up_lines[0]+3)
    _, left_textblock_edge = state.text_block_start
    _, right_textblock_edge = state.text_block_end
    textblock_width = right_textblock_edge-left_textblock_edge+1
    printable_lines = state.printable_lines

    if print_console:
        from rich.console import Console, Control
        console = Console(record=True)
        last_line = len(printable_lines)
        for i, row_no in enumerate(printable_lines):
            console.control(Control.move_to(x=left_textblock_edge, y=row_no-1))
            if i == last_line-1:
                test=text
            elif text_list and i!=last_line-1:
                test=text_list[i]
            else:
                test = " "
            if isinstance(text, str):
                if len(text) < textblock_width:
                    text = text + (" " * (textblock_width-len(text)))
            #if slow_char:
            #    for char in test:
            #        console.print(char, end='')
            #        sleep(.08)
            #        print(f"\033[{row_no};{str(left_textblock_edge)}H{END}")
            #    print()
            #else:
            #    console.print(test)
            if slow_lines:
                sleep(.08)
                console.print(test)
                #print(f"\033[{row_no};{str(left_textblock_edge)}H{END}")
        console_text = console.export_text()
        return console_text

    if text_list:
        for i, row_no in enumerate(printable_lines):

            slow_char=False # v so turning it off for now
            if slow_char: ## doesn't work with the coloured text. Neec to colour it here if this is what I want.
                if len(text_list[i])> 1:
                    for v, char in enumerate(text_list[i]):
                        sleep(.0005)
                        print(f"\033[{int(row_no)};{left_textblock_edge+v}H{char}", end='')
                        print(f"\033[{row_no};{str(left_textblock_edge)}H{END}") ## having this on, it waits properly. Don't know why it needs it but apparently it does.
                else:
                    print(f"\033[{int(row_no)};{left_textblock_edge}H{text_list[i]}", end='')
            else:
                print(f"\033[{int(row_no)};{left_textblock_edge}H{text_list[i]}", end='')
                sleep(.05) ### Why is this never triggering. It pauses /before/ printing anything in this section, but not between lines. I don't understand why.
                print(f"\033[{row_no};{str(left_textblock_edge)}H{END}") ## having this on, it waits properly. Don't know why it needs it but apparently it does.
        sleep(.2)
        return text_list

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
        if slow_lines:
            sleep(.08)
        last_row=row

    print("\033[u")
    return first_row, last_row, text_block_start_col


def prep_datablocks(text):
    new_text=[]
    for line in text:
        if line == "":
            continue
        line=line.replace('$', (' ' * state.spacing))
        new_text.append(line)
    return new_text


def overprint_part(part:str="", datablock:list=None, inv:list=None, backgrounds:bool=False):

    from layout import get_positions

    bg_col = 40
    if backgrounds:
        bg_col = 44

    attr_name = f"{part}start"
    top_row, left_col, = getattr(state, attr_name)
    inv_format=';'.join([str(1), str(33), str(bg_col)])
    inv_col=f"\x1b[{inv_format}m"

    def print_playerdata(part, inv, datablock, speed=.05):

        item_list = []

        header_format=';'.join([str(0), str(33), str(bg_col)])
        header_col=f"\x1b[{header_format}m"
        item_list=inv
        datablock = prep_datablocks(datablock)
        item_pos = get_positions(part, datablock)

        if len(item_list) > len(item_pos):
            print(f"Too many items for {part}.")
        i=0
        item=None
        counter = 0
        while i < len(item_pos)-1:
            for i, item in enumerate(item_list):
                pos = item_pos[i]
                row_base, col_base = pos
                row = (row_base + top_row)
                row=row+1
                if part == "playerdata_":
                    if i in [3, 4]:
                        line = []
                        for stat, val in item.items():
                            if val and val is True:
                                line.append(f"{stat}   ")
                        item="".join(line)
                if part == "worldstate_":
                    counter = 1 ## Adding this here gets 'day' back. Maybe deleted it some time ago but didn't realise? Not sure. The line alignment is weird, plus/minus ones everywhere.
                print(f"\033[0;0H{END}", end='')
                title_str = datablock[i + counter]
                title_str = title_str.replace("*", " ") ## titles only, no real data.
                title = f'{header_col}{title_str}{END}' ## Will do the same with inventory later, printing it after the concept of 'carrying things in <carrier>' comes up.
                print(f"\033[{int(row)};{left_col}H{title}")#, end='')
                sleep(speed)
                print(f"\033[0;0H{END}", end='')

        return

    def print_inventory(part, inv, datablock, speed=.05):

        inv_list = []
        if part == "inv_":
            for item in inv:
                inv_list.append(item.name)

        datablock=prep_datablocks(datablock) ## Want a way to do this accounting for the items in the list. Don't know how to do that yet.
        inv_pos = get_positions(part, datablock)

        if len(inv_list) > len(inv_pos):
            print(f"Too many items for {part}.") # Need to actually act on this.
        i=0

        while i < len(inv_pos)-1 and i < len(inv_list)-2: # i don't understand why this has to be -2, but when it was -1 it was recursive. Will look into it more.
            for i, item in enumerate(inv_list):
                pos = inv_pos[i]
                row_base, col_base = pos
                row = row_base + top_row +2
                col = col_base + left_col
                coloured = f'{inv_col}{item}{END}'
                print(f"\033[{int(row)};{col}H{coloured}", end='')
                sleep(speed)
                print(f"\033[0;0H{END}")

        return

    def print_command(datablock, speed=.05):
        r_counter=0
        attr_name = f"{part}end"
        bottom_row, right_col, = getattr(state, attr_name)
        bottom_row = bottom_row + 1 # not sure why needed, but needed or it only prints the first line.
        for row in range(top_row, bottom_row):
            c_counter=0
            for col in range(left_col, right_col):
                bg_format=';'.join([str(0), str(33), str(bg_col)])
                bg=f"\x1b[{bg_format}m"
                char = datablock[r_counter][c_counter-1:c_counter]
                if char == "*":
                    coloured = f'{bg}{" "}{END}'
                else:
                    coloured = f'{bg}{char}{END}'
                print(f"\033[{row+1};{col}H{coloured}")
                c_counter+=1
            sleep(speed)
            print(f"\033[0;0H{END}")
            r_counter+=1

    if inv != None: ## This is only command_
        if part == "inv_":
            print_inventory(part, inv, datablock)
        else:
            print_playerdata(part, inv, datablock) # playerdata + worldstate both

    else:
        print_command(datablock)


def print_commands(backgrounds=False):
    from datablocks import commands_
    datablock=prep_datablocks(commands_)
    overprint_part("commands_", datablock, None, backgrounds)


def add_infobox_data(print_data:bool = False, backgrounds:bool = False, inventory:list=None, playerdata:tuple=None, worldstate:list=None, ):


    def clean_player_data(playerdata):
        game_player, carryweight, name = playerdata # still here, just not being used until I can fix it overwriting the HP
        health = game_player.get("hp")
        short_stats = {
            "tired": game_player.get("tired"),
            "full": game_player.get("full"),
            "bored": game_player.get("bored"),
            "sad": game_player.get("sad"),
            "blind": game_player.get("blind")}

        long_stats={
            "hungry": game_player.get("hungry"),
            "overwhelmed": game_player.get("overwhelmed"),
            "encumbered": game_player.get("encumbered")}

        pd=list((health, name, carryweight, short_stats, long_stats))
        return pd

    from datablocks import inv_, worldstate_, playerdata_
    player_inv = None
    if playerdata:
        player_inv = clean_player_data(playerdata)
    infobox_dict = {
        "inventory": {
                    "part":"inv_",
                    "datablock":inv_,
                    "inv":inventory},

        "playerdata": {
                    "part":"playerdata_",
                    "datablock":playerdata_,
                    "inv":player_inv},

         "worldstate": {
                    "part":"worldstate_",
                    "datablock":worldstate_,
                    "inv":worldstate}}

    for section in ["inventory", "playerdata", "worldstate"]:
        part = infobox_dict[section].get("part")
        datablock = infobox_dict[section].get("datablock")
        inv = infobox_dict[section].get("inv")
        if print_data and inv:
            overprint_part(part, datablock, inv, backgrounds)

    return

def advance_list(console_text):
    cleaned_list = []
    console_list = console_text.split("\n")
    for i, entry in enumerate(console_list):
        if i == 0 or entry == "":
            continue
        cleaned_list.append(entry)
    return list(cleaned_list)


def clean_print_block(state, intro_list=None):

    cleaned_list = []

    linecount = state.printable_lines
    _, start_offset = state.text_block_start
    _, end_offset = state.text_block_end
    text_block_width = end_offset-start_offset

    if intro_list:
        if len(linecount) < 20:
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

    else:
        sample_length = text_block_width
        for _ in range(len(linecount)):
            text = (" " * sample_length)
            cleaned_list.append(text)
        total_list = cleaned_list

    return total_list


def print_output(text="", print_list=None, slow=False, print_to_console=True, by_char=False):
    print(HIDE, end='')
    console_text = print_in_text_box(state.up_lines, text, text_list=print_list, print_console=print_to_console, slow_lines=slow, slow_char=by_char)
    if print_to_console:
        print_list = advance_list(console_text)
    else:
        print_list = console_text
    return print_list

def print_text_from_bottom_up(input_list:list=None, input_text:str="", get_name=True):
    text=None
    reversed_list=None
    slow_bool=False
    first_input_done=False

    if input_list:
        print_output(text="", print_list=input_list, slow=True, by_char=True)

    else:
        if not first_input_done and not input_text:
            input_str = Colours.c("Please enter your name:  ", "title_white")
        else:
            input_str=Colours.c("INPUT:  ", "title_white")

        print(f"\033[{state.input_pos}H{input_str}", end='')
        print("\033[s", end="")
        print(HIDE, end='')
        if input_text and input_text != " " and not input_list:
            print_output(text=input_text, print_list=None, slow=False)
            input_text=None
        print(f"\033[u", SHOW, end='')
        text = input()
        print(HIDE, end='')

        if get_name:
            while True:
                player_name = text
                print(HIDE, end='')
                print(f"\033[{state.input_pos}H{'                                           '}{END}", end='')
                if isinstance(player_name, str) and len(player_name) > 0:
                    clean = clean_print_block(state)
                    print_output(text="", print_list=clean, slow=True)
                    first_input_done = True
                    return player_name
                input_str = Colours.c("Please enter your name:  ", "title_white")
                print(f"\033[{state.input_pos}H{input_str}{END}", end='')
                print(SHOW, end='')
                text = input()
                print(f"\033[u{'                                                                             '}", end='')
                print(HIDE, end='')

        if input_text:
            print_output(text, print_list=None, slow=slow_bool)
            print(f"\033[u{'                                                                             '}", end='')
            print(f"\033[{state.input_pos}H{input_str}{END}", end='')
            while text != "":
                print(HIDE, end='')
                reversed_list = print_output(text, reversed_list, slow=slow_bool)
                print(f"\033[u", SHOW, end='')
                text = input()
                print(f"\033[u{'                                                                             '}", end='')
                print(HIDE, end='')
        print(f"\033[u{'                                                                             '}", end='')


def run_tui_intro():

    print(HIDE, end='')


    print("\033[s", end='')
    spaced_linelist = state.ui_layout
    #print_TUI(spaced_linelist)
    coloured_linelist = make_coloured_list(spaced_linelist)
    print_TUI(coloured_linelist)
    player_name=None
    print_intro=True
    if print_intro:
        from datablocks import intro
        intro = clean_print_block(state, intro)
        intro = make_coloured_list(intro, title_block=True)
        print_output(text="", print_list=intro, slow=True, print_to_console=False, by_char=True)
        player_name = print_text_from_bottom_up(get_name=True)
    return player_name


if "__main__" in __name__:
    run_tui_intro()
    print(f"\033[5B", end='') ## return to end of screen when program ends to avoid overwriting, doesn't matter but is better aesthetically.

#### https://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
