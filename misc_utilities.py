from env_data import cardinalInstance, placeInstance
from itemRegistry import ItemInstance
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

### STRING MANIPULATION

def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s

def is_plural_noun(noun_inst):
    #from itemRegistry import registry
    #registry.item_defs
    plural_nouns = set(("dried flowers", "bedsheets",))
    if noun_inst.name in plural_nouns:
        return "are"
    return "is"

def check_name(item_name):
    logging_fn()
    special_type = {
        "name": 0,
        "container": 1,
        "plural": 2
    }

    if "*" in item_name:
        plain_name = item_name.replace("*", "")
        name_type = special_type["container"]

    elif " x" in item_name:
        plain_name = item_name.split(" x")[0]
        plural_val = item_name.split(" x")[1]
        name_type = int(plural_val)

    else:
        plain_name = item_name
        name_type = special_type["name"]

    return plain_name, name_type

def switch_the(text:str|ItemInstance|list, replace_with:str="the")->str:

    if isinstance(text, list):
        if len(text) == 1:
            text=text[0]
            text=text.name
        else:
            print("Trying to `switch_the`, but text is a list with more than one item.")
            exit()

    if isinstance(text, ItemInstance):
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
            do_print(coloured_list)

### END STRING MANIPULATION

def look_around():
    from env_data import locRegistry as loc, get_loc_descriptions
    #from choose_a_path_tui_vers import get_items_at_here
    from itemRegistry import registry
    get_loc_descriptions(place=loc.currentPlace)
    print("\033[37m \033[0m")

    print(loc.currentPlace.overview, "\n")
    #print("^ loc overview ^")
    #print(f"loc.current: {loc.current}")
    #print(f"loc.current vars: \n{vars(loc.current)}")

    print(f"You're facing {assign_colour(loc.current)}. {loc.current.description}")
    #print("^ loc current.description ^")
    #print(f"You're facing {assign_colour(loc.current, card_type="name")}. {loc.current.description}")

    is_items = registry.get_item_by_location() ## Need to merge this with the dict writing to account for missing items.

    #is_items = get_items_at_here(print_list=False, place=loc.current)

    applicable_items = []
    import config
    if config.print_items_in_area:
        if is_items:
            for item in is_items:
                #print(f"ITEM: {item}, type: {type(item)}")
                _, _, reason_val, _ = registry.check_item_is_accessible(item)
                #print(f"REASON VAL FOR `{item}`: {reason_val}")
                if reason_val == 0:
                    applicable_items.append(item)
            if applicable_items:
                print(assign_colour("\nYou see a few scattered objects in this area:", "b_white"))
                is_items = ", ".join(col_list(applicable_items))
                print(f"   {is_items}")



### INVENTORY LIST MANAGEMENT (possible all should be in item_management instead, but keeping here for now.)

def get_inst_list_names(inventory_inst_list) -> list:
    logging_fn()
    inventory_names_list=list()
    for item in inventory_inst_list:
        inventory_names_list.append(item.name)

    return inventory_names_list

def from_inventory_name(test:str, inst_inventory:list=None) -> ItemInstance:
    logging_fn()
    if isinstance(test, ItemInstance):
        test = test.name

    if inst_inventory == None:
        from set_up_game import game ## might break
        inst_inventory = game.inventory

    cleaned_name,_ = check_name(test)
    #print(f"Test: {test}, cleaned_name: {cleaned_name}")
    for inst in inst_inventory:
        if inst.name == cleaned_name: # always returns the first, even if there are multiples. This is fine though I think.
            return inst

    #print(f"Inst inventory: {inst_inventory}")
    logging_fn()
    print(f"Could not find inst `{test}` in inst_inventory.")
    input()


def is_item_in_container(item, inventory_list=None):

    inst = None
    if isinstance(item, ItemInstance) and item != None:
        inst = item
    elif isinstance(item, str) and item != None:
        inst = from_inventory_name(item, inventory_list)

    if inst == None:
        print(f"Failed to get instance for {item}, type: {type(item)}")
        exit()
    if hasattr(inst, "contained_in"):
        #print(f"Hasattr contained_in: {inst}:inst.contained_in {inst.contained_in}")
        if inst.contained_in != None:
            #print("Not necessary but I want to see:")
            #print("inst.contained_in's vars:")
            #print(f"{vars(inst.contained_in)}")
            container = inst.contained_in
            return container, inst
    return None, inst

def generate_clean_inventory(inventory_inst_list=None, will_print = False, coloured = False):

    from itemRegistry import registry
    from tui.tui_update import update_text_box
    from config import enable_tui
    tui_enabled = enable_tui

    if inventory_inst_list == None:
        from set_up_game import game
        inventory_inst_list = game.inventory

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
        else:
            """
        else:#
            # check if it's a child:
            has_parent, child_inst = is_item_in_container(inventory_inst_list, item_name)
            #print(f"In generate clean inventory: has_parent: {has_parent}, child_inst: {child_inst}")
            if not has_parent:
                # check if it's a parent:
                inst = from_inventory_name(item_name, inventory_inst_list)
                children = registry.instances_by_container(inst)
                if children:
                    inventory_names.append(item_name+"*") ## add to inventory with asterisk if has children inside.
                else:
                    inventory_names.append(item_name) ## add to inventory if item does not have a parent(container)
                no_xval_inventory_names.append(item_name)
            """
            children=None
            has_parent, child_inst = is_item_in_container(item_name, inventory_inst_list) # is it a child
            if not has_parent:
                inst = from_inventory_name(item_name, inventory_inst_list)
                if registry.by_container.get(inst):
                    children = registry.instances_by_container(inst)
                if children:
                    inventory_names.append(item_name+"*") ## add to inventory with asterisk if has children inside.
                else:
                    inventory_names.append(item_name) ## add to inventory if item does not have a parent(container)
                no_xval_inventory_names.append(item_name)

    second_checked = set()
    for inst_name in checked: # because it's a set, should only be one per item
        dupe_items = (registry.get_duplicate_details(inst_name, inventory_inst_list))
        if inst_name in second_checked:
            continue
        name_index = inventory_names.index(inst_name)
        inventory_names[name_index] = f"{inst_name} x{len(dupe_items)}"
        second_checked.add(inst_name)

    if coloured:
        coloured_list = []
        coloured_and_spaced = []
        for item_name in inventory_names:
            coloured_and_spaced.append(f"    {assign_colour(item_name)}")
            coloured_list.append(f"{assign_colour(item_name)}")
        if will_print and tui_enabled:
            update_text_box(coloured_and_spaced)
        elif will_print:
            update_text_box(inventory_names)

    return inventory_names, no_xval_inventory_names

def separate_loot(child_input=None, parent_input=None, inventory=[]): ## should be inside registry, not here.
    from itemRegistry import registry
    child = None
    parent = None

    if child_input:
        if isinstance(child_input, ItemInstance):
            child = child_input
        else:
            child = from_inventory_name(child_input)

    if parent_input:
        if isinstance(parent_input, ItemInstance):
            parent = parent_input
        else:
            parent = from_inventory_name(parent_input)

    #print(f"parent: {parent}, child: {child}")
    if parent and not child:
        children = registry.instances_by_container(parent) ### Maybe this is the issue to the 'remove all children when you only picked one.

        if children:
            for item in children:
                inventory, result = registry.move_from_container_to_inv(item, inventory, parent)

    else:
        inventory, result = registry.move_from_container_to_inv(child, inventory, parent)

    clean_separation_result(result, to_print=True)

    #print(f"game.inventory: {game.inventory}")
    return inventory, result

### END INVENTORY LIST MANAGEMENT


### COLOUR ASSIGNMENT

def get_itemname_from_sqrbrkt(string):

    parts = string.split("[[")
    other_parts = parts[1].split("]]")
    #print(f"Parts[0]: {parts[0]}, other_parts: {other_parts}")
    item_name_raw = other_parts[0].strip()
    item_name = assign_colour(item_name_raw)
    #print(f"item_name: {item_name}")
    joined = [parts[0], item_name]
    for part in other_parts:
        if part == item_name_raw:
            continue
        joined.append(part.strip())
    compiled_str = "".join(joined)
    #print(f"joined: {compiled_str}")
    return compiled_str


def assign_colour(item, colour=None, *, nicename=None, switch=False, no_reset=False, not_bold=False, caps=False, card_type = None):
    #logging_fn()
    from tui.colours import Colours
    string = item
    if colour == "event_msg":
        if "[[" in item:
            return get_itemname_from_sqrbrkt(string)

    bg = None
    bld = ita = u_line = invt = False

    specials = ("location", "loc", "description", "title_bg", "title", "deco", "hash", "title_white", "equals", "underscore", "event_msg")

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
                colour="green" # set 'loc' in colours.C instead of hardcoding the actual colours here. Only code here for bold, or if the colour named is inaccurate.
                bld=True
            if colour == "title_bg":
                colour="black"
                bg="green"
            if colour == "equals":
                u_line=True
                bg="blue"
            if colour == "hash":
                bg="blue"
            if colour == "title_white":
                colour="white"
            if colour in bold_special:
                bld=True
            if colour == "title":
                bld=True
            if colour == "event_msg":
                ita=True
                colour = "yellow"

    elif isinstance(item, list):
        print(f"Item instance in assign_colour is a list: {item}")
        from time import sleep
        sleep(.5)
        item=item[0] #arbitrarily take the first one.

    def check_instance_col(item):

        from itemRegistry import registry
        if isinstance(item, ItemInstance|placeInstance|cardinalInstance):
            entry = item

            if entry and entry.colour != None:
                colour=entry.colour
                bld=True
                if not isinstance(item, cardinalInstance):
                    item=item.name
            else:
                colour=cardinals[Colours.colour_counter%len(cardinals)]
                colour=cardinal_cols[colour] # TODO: is there any reason fo this to be separate? Can't we just use the %len directly against cardinal_cols?
                Colours.colour_counter += 1

                if isinstance(item, ItemInstance):
                    item=registry.register_name_colour(item, colour)
                    bld=True
                elif isinstance(item, placeInstance|cardinalInstance):
                    item.colour=colour
                    if not isinstance(item, cardinalInstance):
                        item = item.name
                    bld=True

            return colour, item, bld

    if item in cardinals:
        colour=cardinal_cols[item]
        bld=True


    elif isinstance(item, str) or isinstance(item, ItemInstance|placeInstance|cardinalInstance):
        from itemRegistry import registry

        if isinstance(item, str):

            plain_name, val = check_name(item)
            if val > 0:
                item_instance = from_inventory_name(plain_name, None)
                colour, _, bld = check_instance_col(item_instance)

            else:
                item_instances=registry.instances_by_name(item)
                if item_instances:
                    item=item_instances[0]
                    colour, item, bld = check_instance_col(item)
                    #colour = item.colour

        if isinstance(item, ItemInstance|placeInstance|cardinalInstance): # changing to elif breaks non-instance colours entirely.
            if nicename:
                held_name = item.nicename
            colour, item, bld = check_instance_col(item)
            if nicename:
                item = held_name


        elif isinstance(colour, (int, float)):
            colour=int(colour)%len(cardinals)
            colour=cardinals[int(colour)]

            colour=cardinal_cols[colour]
            bld=True

    #if nicename:
    #    item=nicename # can't remember what this was used for
    if switch:
        item=switch_the(item)
    if caps:
        item = smart_capitalise(item)

    #if colour == None:
    #    colour=cardinals[Colours.colour_counter%len(cardinals)]
    #    colour=cardinal_cols[colour]
    #    Colours.colour_counter += 1
    #    bld=True

    #if colour == None:
        #print(f"Colour is None. Item: ({item}). Type: ({type(item)})")

    if not_bold:
        bld=False

    if card_type:
        if card_type == "name":
            item = item.name
        elif card_type == "ern_name":
            item = item.ern_name
        elif card_type == "place_name":
            item = item.place_name
        elif card_type == "in_loc_facing_card":
            item = item.in_loc_facing_card

    elif isinstance(item, cardinalInstance):
        item = item.name

    coloured_text=Colours.c(item, colour, bg, bold=bld, italics=ita, underline=u_line, invert=invt, no_reset=no_reset)
    return coloured_text

def col_list(print_list:list=[], colour:str=None)->list: ## merge this to the above, to it just deals with lists automatically instead of being a separate call.
    coloured_list=[]

    for i, item in enumerate(print_list):
        if item == None:
            continue
        if not colour:
            coloured_text = assign_colour(item, i)
        else:
            coloured_text = assign_colour(item, colour)
        coloured_list.append(coloured_text)
    return coloured_list


def in_loc_facing_card(cardinal:cardinalInstance):
    # just putting this here because the things that will need it probably import locRegistry anyway.
    text = f"the {assign_colour(cardinal.place,)}, facing {assign_colour(cardinal)}."
    return text

### END COLOUR ASSIGNMENT

### SHORTHAND FNs

def has_and_true(item, attr):
    #print(f"HAS AND TRUE: item: {item}, attr: {attr}")
    if hasattr(item, attr) and getattr(item, attr) == True:
        return True
    return False

### SIMPLE UTILITIES

def print_type(item, exit=False, disabled=False):

    if disabled:
        return

    print(f"Item: {item}, type: {type(item)}")
    if exit:
        exit()

def do_print(text=None, end=None, do_edit_list=False, print_func=None):

    from tui.tui_update import update_text_box

    if text==None:
        text=" "
    if print_func:
        text = text + "[" + print_func + "]"
    #if isinstance(text, str) and text.strip=="":
    #    do_edit_list=True

    update_text_box(to_print=text, edit_list=do_edit_list) ## enable_tui removed from here, instead tui_update pulls it itself.
#    if end != "no": # bit weak but it'll do, lets me force no extra newlines even with the messy af print sequence I hae for now.
#        update_text_box(to_print="  ")

def do_input():

    #from choose_a_path_tui_vers import enable_tui
    SHOW = "\033[?25h"
    MOVE_UP = "\033[A"
    HIDE = "\033[?25l"

    move_up = MOVE_UP
    import config
    enable_tui=config.enable_tui
    if enable_tui:
        print(SHOW, end='') ## is this right? Not sure...
        move_up = ""
    text=input()

    #if text == "" or text == None:
    #    do_print(assign_colour(f"{move_up}{HIDE}(Chosen: <NONE>)", "yellow"))
    #else:
    #    do_print(assign_colour(f'{move_up}{HIDE}Chosen: ({text.strip()})', 'yellow'))
    return text

