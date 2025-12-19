#layout.py

tui_lines = "screen_draft_expanding.txt"

def calculate_layout(state):
    import shutil
    size = shutil.get_terminal_size()
    state.cols = size.columns
    state.rows = size.lines


def space_and_get_cursor_pos(state, input_list, space=True):
    ## UI blocking
    spaced_list = []
    up_lines = []

    ui_blocks = {
        'i': {"block_part": "inv_"},
        "w": {"block_part": "worldstate_"},
        "p": {"block_part": "playerdata_"},
        "c": {"block_part": "commands_"}
        }

    replace_dict = {
        "&": {"to_print":"_"},
        "*": {"to_print":"="},
        "%": {"to_print":"-"}
    }

    linelength=state.linelength
    spacing=state.spacing #  == 3

    cols = state.cols
    rows = state.rows
    line_str = state.line_str

    rows = state.rows
    additional_rows = rows-len(input_list)-2
    longer_list = []
    for line in input_list:
        if '+' in line:
            for _ in range(0, additional_rows+1):
                longer_list.append(line_str)
        else:
            longer_list.append(line)

    input_list = longer_list

    for row, text_line in enumerate(input_list):
        if len(text_line) < linelength:
            diff = linelength - len(text_line)
            text_line = text_line + (" " * diff)

        if space:
            text_line = text_line.replace("$", " " * spacing)
            text_line = text_line.replace('@', '^' * spacing)
            for item in replace_dict:
                text_line = text_line.replace(item, (replace_dict[item]["to_print"] * spacing))

        if len(text_line) < cols:
            extra_spaces = cols - len(text_line)
            text_line = (' ' * int(extra_spaces/2)) + text_line + (' ' * int(extra_spaces/2))

        for symbol in ui_blocks:
            if symbol in text_line:
                attr_name = f"{ui_blocks[symbol]['block_part']}start"
                if not hasattr(state, attr_name) or getattr(state, attr_name) is None:
                    column = text_line.find(symbol)
                    setattr(state, attr_name, (row, column))
                else:
                    column = text_line.rfind(symbol)
                    attr_name = f"{ui_blocks[symbol]["block_part"]}end"
                    setattr(state, attr_name, (row, column-1))

                text_line = text_line.replace(symbol, " ")

        if "^" in text_line:
            if not hasattr(state, "text_block_start") or state.text_block_start == None:
                state.text_block_start = (row+3, text_line.find('^')+3)
            else:
                state.text_block_end = (row-1, text_line.rfind('^')-3)
            up_lines.append(row) ## and this works. So why do the end lines not work properly?
        if text_line != "":
            spaced_list.append(text_line)

    state.ui_layout = spaced_list
    state.up_lines = up_lines
    state.input_line = up_lines[1]+3
    state.input_pos = f"{up_lines[1]+3};{(up_lines[0]+3)+7}"

    printable_lines = list(range((up_lines[0]+3), (up_lines[1])))
    state.printable_lines = printable_lines


def get_TUI_list(state, tui_lines):
    linelength=0
    tui_linelist = []
    with open(tui_lines) as f:
        counter=0
        for line in f:
            if counter==0:
                no_of_spacers = line.count("&")
            if counter == 19:
                line_str = line.rstrip('\n')
            tui_linelist.append(line.rstrip('\n'))
            if len(line) > linelength:
                linelength = len(line)-no_of_spacers
            counter += 1

    cols = state.cols
    spare_cols = cols-linelength
    spacing=int(spare_cols/no_of_spacers)

    if spacing <= 0:
        spacing = 0

    state.spacing = spacing
    state.line_str = line_str
    state.linelength = linelength

    space_and_get_cursor_pos(state, tui_linelist, space=True)


class TState:

    def __init__(self):
        # terminal / TUI
        calculate_layout(self)
        get_TUI_list(self, tui_lines)



state = TState()

def get_positions(part, text):
    positions_set = set()
    attr_name = f"{part}positions"
    for i, item in enumerate(text):
        pos = item.find("*")
        if pos >= 0:
            positions_set.add((i, pos))
        pos = item.rfind("*")
        if pos >= 0:
            positions_set.add((i, pos))
        pos_2 = item.rfind("*", 0, (pos-1))
        if pos_2 != pos and pos_2 >= 0:
            positions_set.add((i, pos_2))
    positions_set = list(sorted(positions_set))
    setattr(state, attr_name, positions_set)
    #ui_blocking[f"{part}positions"] = positions_set

    return positions_set


