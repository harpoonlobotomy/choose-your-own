
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

    def advance_list(print_list):
        cleaned_list = []
        for i, entry in enumerate(print_list):
            if i == 0:# or entry == "":
                continue
            cleaned_list.append(entry)
        return list(cleaned_list)

    if to_print:
        print_list=list()
        if isinstance(to_print, str):
            if "\n" in to_print:
                to_print = to_print.split("\n")
                print_list=to_print
            else:
                print_list.append("".join(to_print))

        if isinstance(to_print, list):
            temp_list = []
            for item in to_print:
                if isinstance(item, str):
                    if "\n" in item:
                        parts = item.split("\n")
                        for piece in parts:
                            temp_list.append(piece)
                    else:
                        temp_list.append(item)
                else:
                    temp_list.append(item)
            print_list = temp_list
            #print_list=to_print ## for line in to_print - print line by line even if a given input has multiple lines. Otherwise it breaks and looks bad.

        printable_lines = tui_placements["printable_lines"]
        empty_list = [" "] * len(printable_lines)

        #for i, item in enumerate(print_list):
        for item in print_list:
            existing_list = tui_placements.get("existing_list")
            if not existing_list:
                existing_list=empty_list
            existing_list.append(item)

            for i, row_no in enumerate(printable_lines):
                #print(f"i, row_no: {i}, {row_no}")
                #existing_list = existing_list
                #existing_list.append(item)
                #print(f"existing list: {existing_list}")
                new_print_list = existing_list
                #print(f"item: {item}, print_list: {print_list}")

                if len(new_print_list) > len(printable_lines):
                    #print(f"print list longer than printable lines: {new_print_list}, type: {type(new_print_list)}, len: {len(new_print_list)}, len printable_lines: {len(printable_lines)}")
                    while len(new_print_list) > len(printable_lines):
                        #print(f"print_list: {print_list}")
                        new_print_list.pop(0)

                line = new_print_list[i]
                #print(f"new_print_list: {new_print_list}, len: {len(new_print_list)}")
                #for i, line in enumerate(print_list):
                blankline = False
                pauseline = False
                if line == "[PAUSE]":
                    pauseline = True
                    #pauselines.add(i)
                if line.strip() == "":
                    blankline = True
                    #blank_lines.add(i)
                #if "\n" in line:
                #    line = line.replace("\n","")

                _, left_textblock_edge = tui_placements["text_block_start"]
                linelength = tui_placements["linelength"]
                blank_str = " " * linelength

                if blankline:
                    test=" "
                    #test="BLANK"
                    duration=0.001
                elif pauseline:
                    test=" "
                    duration=.001
                else:
                    duration=.003
                    test=line

                sleep(float(duration))
                print(f"\033[{int(row_no)};{left_textblock_edge}H{blank_str}") # blank the full line before printing
                print(f"\033[{int(row_no)};{left_textblock_edge}H{test}", end='')
                #print(item)

                #  for line in print_list: # need to do it line by line.
                #print(HIDE, end='')
                #print_in_text_box(tui_placements, blank_lines, pauselines, text_list=print_list, slow_lines=True)

                new_print_list = advance_list(new_print_list)
                tui_placements["existing_list"] = new_print_list

    sleep(.5)
    sleep(.5)

    b_white_format=';'.join([str(1), str(37), str(40)])
    B_WHITE=f"\x1b[{b_white_format}m"
    col=B_WHITE
    input_str="INPUT:  "
    col_text = f"{col}{input_str}{END}"
    print(f"\033[{tui_placements["input_pos"]}H{col_text}", end='')
    sleep(.24)
    return tui_placements

