## utilities to be used by any script at any point


""" Want to do some colour coding.


Need a colour for locations, separate from the cardinals. I'll need to use something other than what I am now as the straight 16 is too limiting.

Maybe make all locations green, and not use green for anything else?

Yellow for 'interactable' in description text, maybe?


"""
from item_management_2 import ItemInstance, registry


def smart_capitalise(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def get_inventory_names(inventory_inst_list) -> list:

    inventory_names_list=list()
    for item in inventory_inst_list:
        inventory_names_list.append(item.name)

    return inventory_names_list

def from_inventory_name(test:str, inst_inventory:list=None) -> ItemInstance: # works now with no_xval_names to reference beforehand.
    if inst_inventory == None:
        from set_up_game import game ## might break
        inst_inventory = game.inventory

    if " x"  in test or "*" in test:
        cleaned_name = test.split(" x")[0]
        cleaned_name = test.replace("*", "")
    else:
        cleaned_name = test

    for inst in inst_inventory:
        if inst.name == cleaned_name:
            return inst

    print(f"Could not find inst `{inst}` in inst_inventory.")
    input()

def is_item_in_container(inventory_list, item):

    inst = None
    if isinstance(item, ItemInstance) and item != None:
        inst = item
    elif isinstance(item, str) and item != None:
        inst = from_inventory_name(item, inventory_list)

    if inst == None:
        print(f"Failed to get instance for {item}, type: {type(item)}")
        exit()
    if hasattr(inst, "contained_in"):
        container = inst.contained_in
        return container, inst
    return None, None

def generate_clean_inventory(inventory_inst_list, will_print = False, coloured = False, tui_enabled=True):

    from tui_update import update_text_box

    no_xval_inventory_names = []
    inv_list = get_inventory_names(inventory_inst_list)
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
            # check if it's a child:
            has_parent, child_inst = is_item_in_container(inventory_inst_list, item_name)
            #print(f"In generate clean inventory: has_parent: {has_parent}, child_inst: {child_inst}")
            if not has_parent:
                # check if it's a parent:
                inst = from_inventory_name(item_name, inventory_inst_list)
                children = registry.instances_by_container(inst)
                if children:
                    inventory_names.append(item_name+"*") ## add to inventory with asterisk if has children inside.
                    no_xval_inventory_names.append(item_name) ## this one stays clean for input reference
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
            update_text_box(inventory_names, use_TUI=False)


#    registry.inst_to_names_dict There's no point in this, because we can just do inst.name. Bleh.

    return inventory_names, no_xval_inventory_names



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

    for article in ("a ", "an "):
        if text.startswith(article):# in text:
            if replace_with != "":
                if replace_with[-1] != " ":
                    replace_with = replace_with + " "
            text = text.replace(article, replace_with)

    if replace_with == "the":
        text = "the "+ text
    return text


cardinal_cols = {
    "north": "red",
    "south": "blue",
    "east": "cyan",
    "west": "magenta"
}

def assign_colour(item, colour=None, *, nicename=None, switch=False, no_reset=False, not_bold=False, caps=False):

    from tui.colours import Colours

    bg = None
    bld = ita = u_line = invt = False

    specials = ("location", "loc", "description", "title_bg", "title", "deco", "hash", "title_white", "equals", "underscore")
    cardinals=["north", "south", "east", "west"]
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

    elif isinstance(item, list):
        item=item[0] #arbitrarily take the first one.

    def check_instance_col(item):
        if isinstance(item, ItemInstance):
            entry:ItemInstance = item

            if entry and entry.colour != None:
                colour=entry.colour
                item=item.name
                bld=True
            else:
                colour=cardinals[Colours.colour_counter%len(cardinals)]
                colour=cardinal_cols[colour]
                Colours.colour_counter += 1

                item=registry.register_name_colour(item, colour) ## applies the colour the inst, so we later have item.colour.
                bld=True
            return colour, item, bld

    if item in cardinals:
        colour=cardinal_cols[item]
        bld=True


    elif isinstance(item, str) or isinstance(item, ItemInstance):
        if isinstance(item, str):
            if " x" in item:
                item_temp = item.split(" x")[0]
                item_instances=registry.instances_by_name(item_temp)
                if item_instances:
                    item_reduced=item_instances[0]
                    colour, _, bld = check_instance_col(item_reduced)

            elif "*" in item:
                item_temp = item.replace("*", "")
                item_instance = from_inventory_name(item_temp, None)
                if item_instance:
                    colour, _, bld = check_instance_col(item_instance)
            else:
                item_instances=registry.instances_by_name(item)
                if item_instances:
                    item=item_instances[0]
                    colour, item, bld = check_instance_col(item)
                    #colour = item.colour

        if isinstance(item, ItemInstance):
            colour, item, bld = check_instance_col(item)

        elif isinstance(colour, (int, float)):
            colour=int(colour)%len(cardinals)
            colour=cardinals[int(colour)]

            colour=cardinal_cols[colour]
            bld=True
        #else:
        #    print(f"Item not in cardinals and not an instance: {item}") #### ## triggers on locations, possible other things too.
        # This whole thing needs redoing so I'm not going to focus on it too much for now.

    if nicename:
        item=nicename
    if switch:
        item=switch_the(item)
    if caps:
        item = smart_capitalise(item)

    #if colour == None:
        #print(f"Colour is None. Item: ({item}). Type: ({type(item)})")
        # This is printing every time an inventory item is found the first time. I've no idea why though. This:
        #   Colour is None. Item: (moss). Type: (<class 'str'>)
        #   moss
        #   Colour is None. Item: (glass jar). Type: (<class 'str'>)
        #   glass jar
        #   Colour is None. Item: (headstone). Type: (<class 'str'>)
        #   headstone
        #   Colour is None. Item: (dried flowers). Type: (<class 'str'>)
        #   dried flowers
        # prints with full colour.

    if not_bold:
        bld=False

    coloured_text=Colours.c(item, colour, bg, bold=bld, italics=ita, underline=u_line, invert=invt, no_reset=no_reset)
    return coloured_text

def assign_colour2(item:ItemInstance|str, colour:str=None, *, nicename:str=None, switch=False, no_reset=False, not_bold=False, caps=False)->str: ## tried to change some things, broke it. Stored here for later investigation.

    from tui.colours import Colours

    bg = None
    bld = ita = u_line = invt = False

    specials = ("location", "loc", "description", "title_bg", "title", "deco", "hash", "title_white", "equals", "underscore")
    cardinals=["north", "south", "east", "west"]
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

    elif isinstance(item, list):
        item=item[0] #arbitrarily take the first one.

    def check_instance_col(item:ItemInstance|str)->tuple:

        if isinstance(item, ItemInstance):
            entry:ItemInstance = item
            if entry and entry.colour != None:
                colour=entry.colour
                item=item.name
                bld=True
            else:
                colour=cardinals[Colours.colour_counter%len(cardinals)]
                colour=cardinal_cols[colour]
                Colours.colour_counter += 1

                item=registry.register_name_colour(item, colour) ## applies the colour the inst, so we later have item.colour.
                bld=True
            return colour, item, bld

    if item in cardinals:
        colour=cardinal_cols[item]
        bld=True


    elif isinstance(item, str) or isinstance(item, ItemInstance):
        item_temp = None
        if isinstance(item, str):
            if " x" in item:
                item_temp = item.split(" x")[0]

            elif "*" in item:
                item_temp = item.replace("*", "")

            if item_temp != None:
                item_instance = from_inventory_name(item_temp, None)
                colour, _, bld = check_instance_col(item_instance)

            else:
                item_instance = from_inventory_name(item, None)
                if item_instance == None:
                    item_instances=registry.instances_by_name(item)
                    if item_instances:
                        item=item_instances[0]
                else:
                    if item != None and isinstance(item, ItemInstance):
                        print(f"Item instance: {item_instance}")
                        colour, item, bld = check_instance_col(item_instance)

        elif isinstance(item, ItemInstance):
            colour, item, bld = check_instance_col(item)

        if isinstance(colour, (int, float)):
            colour=int(colour)%len(cardinals)
            colour=cardinals[int(colour)]

            colour=cardinal_cols[colour]
            bld=True

    if nicename:
        item=nicename
    if switch:
        item=switch_the(item)
    if caps:
        item = smart_capitalise(item)

    if colour == None:
        print(f"Colour is None. Item: ({item}). Type: ({type(item)})")

    if not_bold:
        bld=False

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
