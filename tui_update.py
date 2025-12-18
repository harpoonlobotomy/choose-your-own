
from time import sleep

END="\x1b[0m"

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

def update_text_box(tui_placements, existing_list, to_print):

    def print_to_console(printable_lines, pauselines, left_margin, textblock_width, print_list, slow=False, clear=True):

        from rich.console import Console, Control
        console = Console(record=True)
        for i, row_no in enumerate(printable_lines):
            if i in pauselines:
                text=None
                sleep(.8)
                continue
            console.control(Control.move_to(x=left_margin, y=row_no-1))
            text = print_list[i]
            if clear:
                if len(text) < textblock_width:
                    text = text + (" " * (textblock_width-len(text)))
            if slow:
                console.print(text)
                print(f"\033[{END}", end="")
            else:
                console.print(text)
            sleep(.08)
        console_text = console.export_text()
        return console_text

    if to_print:
        if isinstance(to_print, str):
            print_list = list((to_print))
        if isinstance(to_print, list):
            print_list=to_print

    if existing_list:
        if print_list and print_list != None:
            existing_list = existing_list + print_list
        print_list = existing_list

    printable_lines = tui_placements["printable_lines"]
    _, left_margin = tui_placements["text_block_start"]
    textblock_width = tui_placements["linelength"]

    if len(print_list) < len(printable_lines):
        empty_list = list()
        counter=1
        while counter <= (len(printable_lines) - len(print_list)):
            empty_list.append("") ## there is a better way of doing this. Too tired. Don't know it. Should.
            counter += 1
        print_list = empty_list + print_list

    elif len(print_list) > len(printable_lines):
        while len(print_list) > len(printable_lines):
            print_list = print_list.pop[0]

    pauselines = []
    for i, line in enumerate(print_list):
        if line == "[PAUSE]":
            pauselines.append(i)

    print_to_console(printable_lines, pauselines, left_margin, textblock_width, print_list, slow=True, clear=False)

    sleep(.1)
# putting this here temporarily. Will bring the text-colouring to unification later.
    b_white_format=';'.join([str(1), str(37), str(40)])
    B_WHITE=f"\x1b[{b_white_format}m"
    col=B_WHITE
    input_str="INPUT:  "
    col_text = f"{col}{input_str}{END}"
    print(f"\033[{tui_placements["input_pos"]}H{col_text}", end='')
    text = input()
    return text
