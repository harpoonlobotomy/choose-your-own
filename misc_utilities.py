from env_data import cardinalInstance, placeInstance
from itemRegistry import itemInstance
from logger import logging_fn

## utilities to be used by any script at any point

accessible_dict = {
    0: "accessible",
    1: "in a closed local/accessible container",
    2: "in a locked local/accessible container",
    3: "in an open container in your inventory",
    4: "in an open container accessible locally, can pick up but not drop",
    5: "in inventory",
    6: "not at current location",
    7: "other error, investigate",
    8: "is a transitional item (eg a door that can be seen from both sides)",
    9: "item is hidden"# (must be discovered somehow, not shown in general 'look around' views.)
}


cardinal_cols = {
    "north": "red",
    "south": "blue",
    "east": "cyan",
    "west": "magenta"
}

cardinals=list(cardinal_cols.keys())

MOVE_UP = "\033[A"

### STRING MANIPULATION

def smart_capitalise(s: str) -> str:
    """Capitalises the first character of the string and returns it."""
    return s[0].upper() + s[1:] if s else s

def is_plural_noun(noun_inst, singular = None, plural = None, bool_test=False):
    """Checks if the given noun_inst is a plural noun.name. If so, returns `'are'`, `1` if bool_test, or `plural` if given, and similarly for singular. `singular` and `plural` can be specified as anything and will be appled in the same fashion."""
    plural_nouns = set(("dried flowers", "bedsheets",))
    if noun_inst.name in plural_nouns:
        if bool_test:
            return 1
        if plural:
            return plural
        return "are"
    if bool_test:
        return 0
    if singular:
        return singular
    return "is"

def check_name(item_name):
    """Gets `plain_name` from `item_name`, as well as `plural_val` if the item ends in '` (x)`'. Removes various formatting options from `item_name`, with the intent of returning the searchable inst.name"""
    logging_fn()
    special_type = {
        "name": 0,
        "container": 1,
        "plural": 2
    }
    if "  - " in item_name:
        item_name = item_name.replace("  - ", "")
        plain_name = item_name
        name_type = 0

    if " x" in item_name:
        plain_name = item_name.split(" x")[0]
        plural_val = item_name.split(" x")[1]
        name_type = int(plural_val)

    elif "*" in item_name:
        plain_name = item_name.replace("*", "")
        name_type = special_type["container"]

    else:
        plain_name = item_name
        name_type = special_type["name"]

    return plain_name, name_type

def switch_the(text:str|itemInstance|list, replace_with:str="the")->str:
    """Replace `a/an ` with `the `, unless an alterative is given in replace_with."""
    if isinstance(text, list):
        if len(text) == 1:
            text=text[0]
            text=text.name
        else:
            print("Trying to `switch_the`, but text is a list with more than one item.")
            exit()

    if isinstance(text, itemInstance):
        text=text.name

    if replace_with == "a ":
        text = text.replace("the ", "a ")

    for article in ("a ", "an "):
        if text.startswith(article):# in text:
            if replace_with != "":
                if replace_with[-1] != " ":
                    replace_with = replace_with + " "
            text = text.replace(article, replace_with)

    if replace_with == "the":
        text = "the "+ text

    return text

def clean_separation_result(result:list, to_print=False):
    logging_fn()
    if not result:
        print("No result in clean_separation_result")
        return
    if not isinstance(result, list):
        print(f"Expecting a list of 'result'. Result is type {type(result)}. Contents: {result}")
        return


    for result_set in result:
        string = result_set[0]
        split_string = string.split("[")
        joint_split=[]
        for item in split_string:
            if item != "" and item != None:
                splits = item.split("]")
                for split_item in splits:
                    if split_item != "" and split_item != None:
                        joint_split.append(split_item)

        child = result_set[1]
        parent = result_set[2]

        coloured_list = []

        for item in joint_split:
            if item == "child":
                item = assign_colour(child)
            elif item == "parent" or item == "new_container":
                item = assign_colour(parent)
            else:
                item = assign_colour(item, colour="yellow")

            coloured_list.append(item)
        coloured_list = "".join(coloured_list)

        if to_print:
            print(coloured_list)

def underline_central(text_str):
    half = len(text_str) / 2
    quart = half / 2
    spacing = " " * int(quart) + "_" * int(half)
    print(spacing, "\n")

### END STRING MANIPULATION

def look_around():
    """Generates and prints `loc.currentPlace.overview` and `loc.current.description`."""
    from env_data import locRegistry as loc, get_loc_descriptions
    from itemRegistry import registry
    get_loc_descriptions(place=loc.currentPlace) # Is this still needed? Aren't we updating this on item change?

    print(f"{loc.currentPlace.overview}\n\nYou're facing {assign_colour(loc.current)}. {loc.current.description}")

    applicable_items = []
    import config
    if config.print_items_in_area: # will remove this later, it's taken care of nicely by the location descriptions now.
        is_items = registry.get_item_by_location() ## Need to merge this with the dict writing to account for missing items.
        if is_items:
            for item in is_items:
                _, reason_val, _ = registry.run_check(item)
                if reason_val == 0:
                    applicable_items.append(item)
            if applicable_items:
                print(assign_colour("\nYou see a few scattered objects in this area:", "b_white"))
                is_items = ", ".join(col_list(applicable_items))
                print(f"   {is_items}")


def print_failure_message(input_str=None, message=None, noun=None, verb=None, idx_kind=None, init_dict=None, format = None):
    """prints a failure message using `input_str`, `noun`, `verb`, `inx_kind`, `init_dict` and `format`, depending on which elements are given. If nothing else, just prints a generic message using `input_str`."""
    logging_fn()
    if input_str:
        print(f'{MOVE_UP}\033[1;32m[[  {input_str}  ]]\033[0m\n')

    from verb_actions import get_verb
    if not init_dict and not (noun and verb):
        print(f"Sorry, I don't know what to do with `{assign_colour(input_str, colour="green")}`.")
        return

    if not verb and init_dict:
        verb = get_verb(init_dict)

    if not verb:
        print(f"Sorry, I don't know what to do with `{assign_colour(input_str, colour="green")}`.")
        return

    from verb_actions import get_noun
    from verbRegistry import VerbInstance
    if isinstance(verb, VerbInstance):
        verb = verb.name
        if verb == "find":
            noun = get_noun(init_dict)
            if noun and isinstance(noun, str) and get_noun(init_dict, get_str=True) != noun: # == assumed noun
                from verb_actions import find
                if find(format_tuple=format, input_dict=init_dict):
                    return

    if not idx_kind and not (noun and verb):
        print(f"Sorry, I don't know what to do with `{assign_colour(input_str, colour="green")}`.")
        return

    noun_name = None
    if noun:
        if isinstance(noun, itemInstance):
            noun_name = noun.name
        elif isinstance(noun, str):
            noun_name = noun

    entry2 = noun2 = None
    if idx_kind:
        idx, kind = idx_kind
        entry = init_dict[idx][kind]
        if isinstance (entry["instance"], str):
            if entry["instance"] != "assumed_noun":
                noun_name = entry["instance"]
            else:
                noun_name = entry["text"]
        for i, kind in init_dict.items():
            kind = list(kind)[0]
            if "noun" in kind and init_dict[i][kind].get("text") != entry['text']:
                entry2 = init_dict[i][kind]
                if entry2.get("instance") and not isinstance(entry2["instance"], str):
                    if (not hasattr(entry2["instance"], "is_hidden") or entry2["instance"].is_hidden == False):
                        noun2 = entry2["instance"]
                        a_or_the = "the "
                    else:
                        noun2 = entry2["text"]
                        a_or_the = "a "

    if noun_name:# and entry["instance"] == 'assumed_noun':
        if verb == "drop":
            print(f"You can't drop a {assign_colour(noun_name, colour="yellow")}; you aren't holding one.")
            return
        if not entry2:
            if verb == "look":
                print(f"There's no {assign_colour(noun_name, colour="yellow")} around here to {assign_colour(verb, colour="green")} at.")
                return
            if verb in ("go", "move"):
                print(f"There's no {assign_colour(noun_name, colour="yellow")} around here to {assign_colour(verb, colour="green")} to.")
                return
            print(f"There's no {assign_colour(noun_name, colour="yellow")} around here to {assign_colour(verb, colour="green")}.")
            return
        if not noun2:
            print(f"There's no {assign_colour(noun_name, colour="yellow")} around here to {assign_colour(verb, colour="green")} {assign_colour(entry2['text'], colour="yellow")} with.")
            return
        #print(f"There's no {assign_colour(noun2)} around here to {assign_colour(verb, colour="green")} the {assign_colour(entry['text'], colour="yellow")} with.")
        from verb_actions import get_dir_or_sem
        dir_or_sem = get_dir_or_sem(init_dict)
        if dir_or_sem:
            if dir_or_sem == "with":
                temp = noun_name
                noun_name = noun2
                noun2 = temp

        print(f"There's no {assign_colour(noun_name, colour="yellow") if isinstance(noun_name, str) else assign_colour(noun_name)} around here to {assign_colour(verb, colour="green")} {a_or_the}{assign_colour(noun2) if isinstance(noun2, itemInstance) else assign_colour(noun2, colour="yellow")} with.")


### INVENTORY LIST MANAGEMENT (possible all should be in item_management instead, but keeping here for now.)

def get_inst_list_names(inventory_inst_list) -> list:
    """Returns a list of all inventory items' names using the inputted inventory list."""
    logging_fn()
    inventory_names_list=list()
    for item in inventory_inst_list:
        inventory_names_list.append(item.name)

    return inventory_names_list

def from_inventory_name(test:str) -> itemInstance:
    """Returns an itemInstance from the inventory based on a given `test` string. `test` is run through `check_name` first to remove common formatting before searching."""
    logging_fn()
    if isinstance(test, itemInstance):
        test = test.name

    from env_data import locRegistry
    inst_inventory = locRegistry.inv_place.items

    cleaned_name,_ = check_name(test)
    for inst in inst_inventory:
        if inst.name == cleaned_name:
            return inst

    logging_fn()
    print(f"Could not find inst `{test}` in inst_inventory.")
    input()

def is_item_in_container(item):
    """Just checks if the given `item` is in a container, and returns that `container` or None."""

    if hasattr(item, "contained_in") and item.contained_in != None:
        container = item.contained_in
        return container
    return None

def generate_clean_inventory(inventory_inst_list=None, will_print = False, coloured = False):
    """Generates a nice looking inventory list, applying '` (x)` for plural entries' and adds colour and formatting."""
    from env_data import locRegistry as loc

    if inventory_inst_list == None:
        inventory_inst_list = loc.inv_place.items

    no_xval_inventory_names = []

    inv_list = get_inst_list_names(inventory_inst_list)
    dupe_items = list()
    checked = set()

    inventory_names = []
    for i, item_name in enumerate(inv_list):
        if item_name in inventory_names:
            if item_name in checked:
                continue
            else:
                checked.add(item_name)
        else: # Removed all the notes about children, because children of inventory items are no longer stored directly in the inventory.
            inventory_names.append(item_name) ## add to inventory if item does not have a parent(container)
            no_xval_inventory_names.append(item_name)

    second_checked = set()
    for inst_name in checked:
        dupe_items = len(list(i for i in loc.inv_place.items if i.name == inst_name))#registry.get_duplicate_details(inst_name, inventory_inst_list))
        if inst_name in second_checked:
            continue
        name_index = inventory_names.index(inst_name)
        inventory_names[name_index] = f"{inst_name} x{str(dupe_items)}"
        second_checked.add(inst_name)

    if coloured:
        coloured_and_spaced = []
        for item_name in inventory_names:
            coloured_and_spaced.append(f"  - {item_name}")
            #coloured_list.append(f"{assign_colour(item_name)}")

        if coloured_and_spaced:
            if isinstance(coloured_and_spaced, list):
                for item in coloured_and_spaced:
                    if item != None:
                        print(assign_colour(item))
            elif isinstance(coloured_and_spaced, str):
                print(coloured_and_spaced)

    return inventory_names, no_xval_inventory_names

def separate_loot(child_input=None, parent_input=None, inventory=[]): ## should be inside registry, not here.
    from itemRegistry import registry
    child = None
    parent = None

    if child_input:
        if isinstance(child_input, itemInstance):
            child = child_input
        else:
            child = from_inventory_name(child_input)

    if parent_input:
        if isinstance(parent_input, itemInstance):
            parent = parent_input
        else:
            parent = from_inventory_name(parent_input)

    #print(f"parent: {parent}, child: {child}")
    if parent and not child:
        children = registry.instances_by_container(parent) ### Maybe this is the issue to the 'remove all children when you only picked one.

        if children:
            for item in children:
                result = registry.move_from_container_to_inv(item, parent)

    else:
        result = registry.move_from_container_to_inv(child, parent)

    clean_separation_result(result, to_print=True)

    #print(f"game.inventory: {game.inventory}")
    return inventory, result

### END INVENTORY LIST MANAGEMENT


### COLOUR ASSIGNMENT

def get_itemname_from_sqrbrkt(string, noun):
    """To replace [[item]] with <{noun} with noun.colour applied>."""

    parts = string.split("[[")
    other_parts = parts[1].split("]]")
    item_name_raw = other_parts[0].strip()
    if noun and noun != None and (noun.name == item_name_raw or item_name_raw in noun.print_name):
        item_name = assign_colour(item = noun)
    else:
        item_name = assign_colour(item_name_raw)
    joined = [parts[0], item_name]

    for part in other_parts:
        if part == item_name_raw:
            continue
        joined.append(part)

    compiled_str = "".join(joined)

    return compiled_str


def assign_colour(item, colour=None, *, nicename=None, switch=False, no_reset=False, not_bold=False, caps=False, card_type = None, noun=None):
    """Take an item and apply its colour. If the item has .colour, that will be applied (either 'colour' if colour provided, otherwise a selection from the colour list on a rotating basis). If item is an instance or instance.name without associated colour, will assign that colour to item.colour and apply the colour.\n\ncard_type specifies the variation of cardinalInstance name to print, the options are\n
        * "name"
        * "ern_name"
        * "place"
        * "place_name"
        * "in_loc_facing_card"\n\n

    By default 'switch' replaces 'a/an x' with 'the x', though this is not used often anymore. 'not_bold' removes any bolding applid by other attributes. caps uses smart_capitalise to capitalise the first character. If noun is provided, get_itemname_from_sqrbrkt can be used to add noun_name into strings with [[name]].\n\n
    If "  - " is in the item name, it will be removed and re-applied at the end of the function, so that inventory items can have the correct colouring applied while maintaining the spacing.
    """
    from tui.colours import Colours

    if hasattr(item, "colour") and not colour and not nicename and not caps and not card_type and not noun:
        simple = True
    else:
        simple = False

    if isinstance(item, itemInstance) and simple and item.colour:
        coloured_text=Colours.c(item.print_name, item.colour, bold=True)
        return coloured_text # shortcut for simple assign_colour(noun) calls.

    if isinstance(item, placeInstance) and simple:
        coloured_text=Colours.c(item.name, fg="green", bold=True)
        return coloured_text # shortcut for simple assign_colour(noun) calls.



    string = f"{(item if isinstance(item, str) else '')}"

    if colour == "event_msg":
        if "[[" in string and not "[[]]" in string:
            return get_itemname_from_sqrbrkt(string, noun)

    if isinstance(item, str) and "  - " in item:
        item = item.replace("  - ", "")

    bg = None
    bld = ita = u_line = invt = False

    specials = ("location", "loc", "description", "title_bg", "title", "deco", "hash", "title_white", "equals", "underscore", "event_msg")

    specials_dict = {
        "loc": {"colour":"green", "bld":True},
        "title_bg": {"colour": "black", "bg": "green"},
        "equals": {"u_line":True, "bg":"blue"},
        "hash": {"bg":"blue"},
        "title_white": {"colour":"white"},
        "title": {"bld":True},
        "event_msg": {"ita":True, "colour": "yellow"}
    }

    Colours.colour_counter = Colours.colour_counter%len(cardinals)

    if colour and isinstance(colour, str):
        if "b_" in colour:
            bld=True
            colour=colour.strip("b_")
        if "u_" in colour:
            u_line=True
            colour=colour.strip("u_")
        if "i_" in colour:
            ita=True
            colour=colour.strip("i_")

        bold_special = ["title", "deco", "description", "title_white"]

        if colour in specials:
            if "loc" in colour:
                colour = "loc"
            if specials_dict.get(colour):
                for attr, val in specials_dict[colour].items():
                    if attr == "u_line":
                        u_line = val
                    if attr == "bg":
                        bg = val
                    if attr == "bld":
                        bld = val
                    if attr == "ita":
                        ita = val
                if colour in bold_special:
                    bld=True
                if specials_dict[colour].get("colour"):
                    colour = specials_dict[colour]["colour"]

    elif isinstance(item, list):
        print(f"Item instance in assign_colour is a list: {item}")
        from time import sleep
        sleep(.5)
        item=item[0] #arbitrarily take the first one.

    def check_instance_col(item):
        """Checks for `item.colour`. If not found, assigns `item.colour` using `Colours.colour_counter`."""
        from itemRegistry import registry
        if isinstance(item, itemInstance|placeInstance|cardinalInstance):
            entry = item

            if entry and entry.colour != None:
                colour=entry.colour
                bld=True
                if isinstance(item, placeInstance):
                    item=item.name
                elif isinstance(item, itemInstance):
                    item = item.print_name
            else:
                colour=cardinals[Colours.colour_counter%len(cardinals)]
                colour=cardinal_cols[colour] # TODO: is there any reason fo this to be separate? Can't we just use the %len directly against cardinal_cols?
                Colours.colour_counter += 1

                if isinstance(item, itemInstance):
                    item=registry.register_name_colour(item, colour)
                    bld=True
                elif isinstance(item, placeInstance|cardinalInstance):
                    item.colour=colour
                    if not isinstance(item, cardinalInstance): # why is cardinalInstance treated so differently here?
                        item = item.name
                    bld=True

            return colour, item, bld

    if item in cardinals:
        colour=cardinal_cols[item]
        bld=True

    elif (isinstance(item, str) and not colour) or isinstance(item, itemInstance|placeInstance|cardinalInstance):
        from itemRegistry import registry

        if isinstance(item, str):

            plain_name, val = check_name(item)
            if val > 0:
                item_instance = from_inventory_name(plain_name)
                colour, _, bld = check_instance_col(item_instance)
            else:
                item_instances=registry.instances_by_name(item)
                if item_instances:
                    item=item_instances[0]
                    colour, item, bld = check_instance_col(item)
                    #colour = item.colour

        if isinstance(item, itemInstance|placeInstance|cardinalInstance):
            if nicename:
                held_name = item.nicename
            colour, item, bld = check_instance_col(item)
            if nicename and held_name: # Need to check here to make sure nicename exists and isn't None. Maybe the issue with the matchbox?
                item = held_name

            if isinstance(item, itemInstance):
                print(f"ITEM INSTANCE PRINT_NAME: {item.print_name}/name: {item.name}")
                item = item.print_name

        elif isinstance(colour, (int, float)):
            colour=int(colour)%len(cardinals)
            colour=cardinals[int(colour)]

            colour=cardinal_cols[colour]
            bld=True

    if switch:
        item=switch_the(item)
    if caps:
        item = smart_capitalise(item)

    if not_bold:
        bld=False

    if card_type:
        if card_type == "name":
            item = item.name
        elif card_type == "ern_name":
            item = item.ern_name
        elif card_type == "place":
            item = item.place.name
        elif card_type == "place_name":
            item = item.place_name
        elif card_type == "in_loc_facing_card":
            item = item.in_loc_facing_card

    elif isinstance(item, cardinalInstance):
        item = item.name
    elif isinstance(item, placeInstance):
        item=item.name

    if string and "  - " in string and isinstance(item, str):
        item = "  - " + item
    coloured_text=Colours.c(item, colour, bg, bold=bld, italics=ita, underline=u_line, invert=invt, no_reset=no_reset)
    return coloured_text

def col_list(print_list:list=[], colour:str=None, nicename=False)->list:
    """Takes a list and assigns colour to each list entry. If `colour` and/or `nicename` is supplied, those will be applied to each item."""
    coloured_list=[]

    for i, item in enumerate(print_list):
        if item == None:
            continue
        if not colour:
            if isinstance(item, itemInstance):
                coloured_text = assign_colour(item, nicename=nicename)
            else:
                coloured_text = assign_colour(item, i, nicename=nicename)
        else:
            coloured_text = assign_colour(item, colour, nicename=nicename)
        coloured_list.append(coloured_text)
    return coloured_list


def in_loc_facing_card(cardinal:cardinalInstance):
    """Returns `the {assign_colour(cardinal.place,)}, facing {assign_colour(cardinal)}` using the provided `cardinalInstance`."""
    text = f"the {assign_colour(cardinal.place,)}, facing {assign_colour(cardinal)}."
    return text

### END COLOUR ASSIGNMENT

### SHORTHAND FNs

def has_and_true(item, attr):
    """Returns True or False based on the results of `if hasattr(item, attr) and getattr(item, attr)` for the provided `item` and `attr`."""

    if hasattr(item, attr) and getattr(item, attr):
        return True
    return False

### SIMPLE UTILITIES

def print_type(item, exit=False, disabled=False):
    """Returns `Item: {item}, type: {type(item)}`. I'm pretty sure I already wrote this, so this function may exist elsewhere too."""
    if disabled:
        return

    print(f"Item: {item}, type: {type(item)}")
    if exit:
        exit()

