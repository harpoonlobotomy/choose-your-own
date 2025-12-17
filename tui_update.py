#  tui_update
END="\x1b[0m"

def update_playerdata(tui_placements, hp_value=None, carryweight_value=None):
#    print(END, end='')

    #for field in [hp_value, carryweight]: ## will do this in a bit.
    base_start = tui_placements["playerdata_start"]

    if hp_value:
        hp_pos = tui_placements["playerdata_positions"][0]
        hp_row, hp_col = hp_pos
        base_row, base_col = base_start
        hp_row = hp_row + base_row+1
        hp_col = hp_col + base_col

        if hp_value < 2:
            colour = 31
        else:
            colour = 33
        b_yellow_format=';'.join([str(1), str(colour), str(40)])
        B_YEL=f"\x1b[{b_yellow_format}m"

        val = f"{B_YEL}{hp_value}"
        print(f"\033[{hp_row};{hp_col}H{val}{END}", end='')

    if carryweight_value:
        carryweight_pos = tui_placements["playerdata_positions"][1] ## will be 2 when name is added layer.

        carryweight_row, carryweight_col = carryweight_pos
        base_row, base_col = base_start
        carryweight_row = carryweight_row + base_row+1
        carryweight_col = carryweight_col + base_col

        if carryweight_value < 2:
            colour = 31
        else:
            colour = 33
        b_yellow_format=';'.join([str(1), str(colour), str(40)])
        B_YEL=f"\x1b[{b_yellow_format}m"

        width = 2
        carryweight_value = str(carryweight_value).ljust(width)

        val = f"{B_YEL}{carryweight_value}"
        print(f"\033[{carryweight_row};{carryweight_col}H{val}{END}", end='')


def update_worlddata(tui_placements, weather=None, time_of_day=None, location=None):
#    print(END, end='')

#   'worldstate_start': (7, 182),
#   'worldstate_end': (12, 226),
#   'worldstate_positions': [(1, 24), (2, 15), (3, 19), (4, 36)]}

    base_start = tui_placements["worldstate_start"]
    location_pos = tui_placements["worldstate_positions"][0]
    location_row, location_col = location_pos
    weather_pos = tui_placements["worldstate_positions"][0]
    weather_row, weather_col = weather_pos
    base_row, base_col = base_start


