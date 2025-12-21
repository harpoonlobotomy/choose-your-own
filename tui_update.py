
from time import sleep

print("Importing tui_update.py")

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


def update_infobox(hp_value=None, name=None, carryweight_value=None, location=None, weather=None, time_of_day=None, day=None):

    from layout import state
    getattr(state, "playerdata_start")
    playerdata_base = getattr(state, "playerdata_start")
    worldstate_base = getattr(state, "worldstate_start")
    player_pos = getattr(state, "playerdata_positions")
    world_pos = getattr(state, "worldstate_positions")

    data_update_dict = {
        "hp_value": {
            "positions": player_pos[0],
            "value": hp_value,
            "base_pos": playerdata_base,
            "alt_colour": True,
            "min_length": 2},
        "name": {
            "positions": player_pos[1],
            "value": name,
            "base_pos": playerdata_base,
            "alt_colour": False,
            "min_length": 13},
        "carryweight_value": {
            "positions": player_pos[2],
            "value": carryweight_value,
            "base_pos": playerdata_base,
            "alt_colour": True,
            "min_length": 2},
        "location": {
            "positions": world_pos[0],
            "value": location,
            "base_pos": worldstate_base,
            "alt_colour": False,
            "min_length": 20},
        "weather": {
            "positions": world_pos[1],
            "value": weather,
            "base_pos": worldstate_base,
            "alt_colour": False,
            "min_length": 28},
        "time_of_day": {
            "positions": world_pos[2],
            "value": time_of_day,
            "base_pos": worldstate_base,
            "alt_colour": False,
            "min_length": 24},
        "day": {
            "positions": world_pos[3],
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

def update_text_box(to_print, end=False, edit_list=False, use_TUI=True):

    if not use_TUI:
        if to_print:
            if isinstance(to_print, list):
                for item in to_print:
                    print(item)
            if isinstance(to_print, str):
                print(to_print)
        return

## NOTE: The 'cut line to size' is faulty. See workdoc.

    import re
    ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

    from layout import state

    linelength = state.linelength
    blank_str = " " * linelength
    _, left_textblock_edge = state.text_block_start
    printable_lines = state.printable_lines

    def advance_list(print_list):
        cleaned_list = []
        for i, entry in enumerate(print_list):
            if i == 0:# or entry == "":
                continue
            cleaned_list.append(entry)
        return list(cleaned_list)


    def strip_ansi(text):
        return ANSI_RE.sub("", text)

    def split_coloured_line(text, max_len):

        visible = strip_ansi(text)

        if len(visible) <= max_len:
            return text, ""

        # find split position in visible text
        split_pos = visible.rfind(" ", 0, max_len)
        if split_pos == -1:
            split_pos = max_len

        # now walk original string until visible chars match split_pos
        vis_count = 0
        real_pos = 0

        while real_pos < len(text) and vis_count < split_pos:
            if text[real_pos] == "\x1b":
                # skip entire ANSI sequence
                m = ANSI_RE.match(text, real_pos)
                if m:
                    real_pos = m.end()
                    continue
            vis_count += 1
            real_pos += 1

        return text[:real_pos], f"    " + text[real_pos:].lstrip()


    def print_list_to_textbox(print_list):

        new_print_items = len(print_list)
        duration = .0001
        empty_list = [" "] * len(printable_lines)
        existing_list=None
        for item in print_list:
            if hasattr(state, "existing_list"):
                existing_list = state.existing_list
            if not existing_list:
                existing_list=empty_list
            existing_list.append(item)

            for i, row_no in enumerate(printable_lines):
                new_print_list = existing_list

                if len(new_print_list) > len(printable_lines):
                    while len(new_print_list) > len(printable_lines):
                        new_print_list.pop(0)

                #if i > (len(printable_lines) - new_print_items):
                #    duration = .02
                #else:
                #    duration = .0001

                line = new_print_list[i]

                ## What if I always print line pairs together. So, print i, i+1, skip one, repeat, ending with a single line as needed. Might make it less chopping feeling maybe?


                #duration=.005
                sleep(float(duration))
                print(f"\033[{int(row_no)};{left_textblock_edge}H{blank_str}") # blank the full line before printing
                print(f"\033[{int(row_no)};{left_textblock_edge}H{line}")
                #print(item)

                #  for line in print_list: # need to do it line by line.
                #print(HIDE, end='')
                #print_in_text_box(tui_placements, blank_lines, pauselines, text_list=print_list, slow_lines=True)
                new_print_list = advance_list(new_print_list)
                attr_name = "existing_list"
                setattr(state, attr_name, new_print_list)

    if end==True:
        print(HIDE, end='')
        print(to_print, end='')

    if edit_list: # to change the last line, eg changing the input text to 'chosen'
        if not to_print:
            print("Cannot edit without to_print text given.")

        existing_list = state.existing_list
        list_length = len(existing_list)

        if list_length < len(printable_lines):
            empty_list = [" "] * (len(printable_lines)- list_length)

        existing_list = empty_list + existing_list
        count = 1
        last_line = existing_list[list_length-count]
        if last_line.strip() == "":
            count += 1

        for _ in range(0,count):
            existing_list.pop()

        if count > 1:
            existing_list.append("  ")

        existing_list.append(to_print)

        for i, row_no in enumerate(printable_lines):
            line = existing_list[i]
            if len(line) < linelength:
                line = line + (" " * (linelength - len(line)))
            print(f"\033[{int(row_no)};{left_textblock_edge}H{line}", end='')

        state.existing_list = existing_list

    elif to_print:
        temp_list=list()
        print_list=list()
        if isinstance(to_print, str):
            if "\n" in to_print:
                temp_to_print = to_print.split("\n")
                temp_list = temp_list + temp_to_print
            else:
                temp_list.append("".join(to_print))

        if isinstance(to_print, list):
            for item in to_print:
                if isinstance(item, str):
                    if "\n" in item:
                        parts = item.split("\n")
                        for piece in parts:
                            temp_list.append(piece)
                    else:
                        temp_list.append(item)
                elif isinstance(item, list):
                    temp_list = temp_list+item
                else:
                    temp_list.append(item)


        for line in temp_list:
            if len(line) > linelength:
                linea, lineb = split_coloured_line(line, linelength)
                print_list.append(linea)
                while len(lineb) > linelength:
                    linea, lineb = split_coloured_line(lineb, linelength)
                    print_list.append(linea)
                print_list.append(lineb)
            else:
                print_list.append(line)


        print_list_to_textbox(print_list)
        #for i, item in enumerate(print_list):



    b_white_format=';'.join([str(1), str(37), str(40)])
    B_WHITE=f"\x1b[{b_white_format}m"
    col=B_WHITE
    input_str="INPUT:  "
    col_text = f"{col}{input_str}{END}"
    print(f"\033[{state.input_pos}H{col_text + blank_str[8:]}", end='')
    print(f"\033[{state.input_pos}H{col_text}", end='')
    sleep(.24)


