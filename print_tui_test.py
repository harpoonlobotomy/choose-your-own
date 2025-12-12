# print_tui

## $ == 5 spaces
## & == 5 underscores
## £ == 5 equals
## % == 5 dashes

## There are 8 'spacers' per line.

tui_lines = "screen_draft_expanding.txt"

spacing = 0
get_longest=True # temporarily, later will be used to do auto spacing + centering.

def get_terminal_cols_rows():

    from shutil import get_terminal_size
    cols, rows = get_terminal_size()
    return cols, rows

def make_centred_list(input_list:list, linelength):
    cols = get_terminal_cols_rows()
    half=((cols-linelength)/2)
    new_list=[]
    for line in input_list:
        line=(" "*int(half)) + line + (" "*int(half))
        if linelength == 126:
            if len(line) > (half+linelength+5):
                line=line[:int(len(line)-(half/2))]
        new_list.append(line)

    linelength = len(new_list[0])
    return new_list, linelength

longest_min = 0
tui_linelist = []
with open(tui_lines) as f:
    for line in f:
        tui_linelist.append(line.rstrip('\n'))
        if get_longest:
            if len(line) > longest_min:
                longest_min = len(line)

if get_longest:
    print(f"Longest line without adding spacers: {longest_min}")

## longest line: 206
for line in tui_linelist:
    line = line.replace('$', (' ' * spacing))
    line = line.replace('&', ('_' * spacing))
    line = line.replace('*', ('=' * spacing))
    line = line.replace('%', ('-' * spacing))
    print(line)
