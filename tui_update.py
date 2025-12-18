
from time import sleep
from rich.console import Console, Control
from rich.text import Text
console = Console(record=True)

END="\x1b[0m"
RESET = "\033[0m"
HIDE = "\033[?25l"
SHOW = "\033[?25h"

def print_update(value, pos, base_start, alt_colour=False, min_length=2):

    row, col = pos
    base_row, base_col = base_start
    row = row + base_row+1
    col = col + base_col

    colour = 33
    if alt_colour:
        if value < 2:
            colour = 31

    value = str(value).ljust(min_length)

    b_yellow_format=';'.join([str(1), str(colour), str(40)])
    B_YEL=f"\x1b[{b_yellow_format}m"
    val = f"{B_YEL}{value}"
    print(f"\033[{row};{col}H{val}{END}", end='')

    sleep(.05)
    print(f"\033{END}")


def update_infobox(tui_placements, hp_value=None, name=None, carryweight_value=None, location=None, weather=None, time_of_day=None, day=None):

    playerdata_base = tui_placements["playerdata_start"]
    worldstate_base = tui_placements["worldstate_start"]

    data_update_dict = {
        "hp_value": {
            "positions": tui_placements["playerdata_positions"][0],
            "value": hp_value,
            "base_pos": playerdata_base,
            "alt_colour": True,
            "min_length": 2},
        "name": {
            "positions": tui_placements["playerdata_positions"][1],
            "value": name,
            "base_pos": playerdata_base,
            "alt_colour": False,
            "min_length": 13},
        "carryweight_value": {
            "positions": tui_placements["playerdata_positions"][2],
            "value": carryweight_value,
            "base_pos": playerdata_base,
            "alt_colour": True,
            "min_length": 2},
        "location": {
            "positions": tui_placements["worldstate_positions"][0],
            "value": location,
            "base_pos": worldstate_base,
            "alt_colour": False,
            "min_length": 20},
        "weather": {
            "positions": tui_placements["worldstate_positions"][1],
            "value": weather,
            "base_pos": worldstate_base,
            "alt_colour": False,
            "min_length": 28},
        "time_of_day": {
            "positions": tui_placements["worldstate_positions"][2],
            "value": time_of_day,
            "base_pos": worldstate_base,
            "alt_colour": False,
            "min_length": 24},
        "day": {
            "positions": tui_placements["worldstate_positions"][3],
            "value": day,
            "base_pos": worldstate_base,
            "alt_colour": False,
            "min_length": 2}
        }

    for field in data_update_dict: ## will do this in a bit.
        entry = data_update_dict[field]
        value = entry["value"]
        pos = entry["positions"]
        is_alt = entry["alt_colour"]
        base_data = entry["base_pos"]
        min_length = entry["min_length"]
        if value != None:
            print_update(value, pos, base_data, alt_colour=is_alt, min_length=min_length)

def update_text_box(tui_placements, to_print):

    existing_list = tui_placements.get("existing_list")
    if not existing_list:
        existing_list=list()

    def advance_list(print_list):
        cleaned_list = []
        for i, entry in enumerate(print_list):
            if i == 0:# or entry == "":
                continue
            cleaned_list.append(entry)
        return list(cleaned_list)

    def print_in_text_box(tui_placements, blank_lines, pauselines, text_list:list=None, slow_lines=True):

        _, left_textblock_edge = tui_placements["text_block_start"]
        linelength = tui_placements["linelength"]
        blankline = " " * linelength
        for i, row_no in enumerate(printable_lines):
            test = text_list[i]
            print(f"\033[{int(row_no)};{left_textblock_edge}H{blankline}")
            if i in blank_lines:
                test=" "
                #test="BLANK"
                duration=0.0
            elif i in pauselines:
                test=" "
                duration=.5
            else:
                duration=.3
#                sleep(.08)
            sleep(float(duration))
            print(f"\033[{int(row_no)};{left_textblock_edge}H{test}{END}", end='')
                #print(f"\033[{row_no};{str(left_textblock_edge)}H{END}")
        return

    if to_print:
        print_list=list()
        if isinstance(to_print, str):
            print_list.append("".join(to_print))
        if isinstance(to_print, list):
            print_list=to_print

    if print_list and print_list != None:
        existing_list = existing_list + print_list
    print_list = existing_list

    printable_lines = tui_placements["printable_lines"]

    if len(print_list) < len(printable_lines):
        empty_list = list()
        counter=1
        while counter <= (len(printable_lines) - len(print_list)):
            empty_list.append("") ## there is a better way of doing this. Too tired. Don't know it. Should.
            counter += 1
        print_list = empty_list + print_list

    elif len(print_list) > len(printable_lines):
        while len(print_list) > len(printable_lines):
            print_list = print_list.pop(0)

    blank_lines = set()
    pauselines = set()
    for i, line in enumerate(print_list):
        if line == "[PAUSE]":
            pauselines.add(i)
        if line.strip() == "":
            blank_lines.add(i)

    if print_list:
        print(HIDE, end='')
        print_in_text_box(tui_placements, blank_lines, pauselines, text_list=print_list, slow_lines=True)
        if print_list:
            print_list = advance_list(print_list)

    sleep(.1)

    b_white_format=';'.join([str(1), str(37), str(40)])
    B_WHITE=f"\x1b[{b_white_format}m"
    col=B_WHITE
    input_str="INPUT:  "
    col_text = f"{col}{input_str}{END}"
    print(f"\033[{tui_placements["input_pos"]}H{col_text}{SHOW}", end='')
    text = input()
    print("print list after advance_list type::", type(print_list))
    print(print_list)
    print_list.append(text)
    exit()

    tui_placements["existing_list"] = print_list
    return text, tui_placements

