
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
    from time import sleep
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
