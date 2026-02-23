
enable_tui: bool = False

run_tests = True
test_location = False#True
parse_test = False#True #turns off events + location item generation, generates every item placed at Everywhere North instead.
parser_tests_output_to_json = False#True

test_mode = True # True == skip player name, intro

white_bg = True
print_items_in_area = False#True
print_input_str = True

show_map = False
map_file = r"archived\map.png" # it keeps getting corrupted, and I wonder if it's because it's not part of a commit yet. Putting it here for now.

item_data = r"ref_files\items_main.json"
loc_data = r"ref_files\loc_data.json"
event_data = r"ref_files\event_defs.json"

usual_start = "graveyard"
test_start = "testing grounds"

starting_location_str = (test_start if test_location else usual_start)
starting_facing_direction = "north"

# verbregistry/verb_membrane/parsing
show_reciever = True#False

add_new_words_if_missing = False

require_firesource = True

key_dir = "north"
no_place_str = f"{key_dir} no_place"
inv_loc_str = f"{key_dir} inventory_place"

godmode = False

coloured_repr = True

record_event_starts_ends = True
