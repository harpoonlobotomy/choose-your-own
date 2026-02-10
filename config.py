#config.py
#just here to hold this value for now. Maybe more later.

enable_tui: bool = False

run_tests = True

test_mode = True # True == skip player name, intro

white_bg = True
print_items_in_area = False#True
print_input_str = True

map_file = r"ref_files\map.png"


item_data = r"ref_files\items_main.json"
loc_data = r"ref_files\loc_data.json"
event_data = r"ref_files\event_defs.json"


starting_location_str = r"everything"
starting_facing_direction = "north"

# verbregistry/verb_membrane/parsing
show_reciever = True#False

add_new_words_if_missing = False

require_firesource = True
