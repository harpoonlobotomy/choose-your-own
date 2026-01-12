#item_interactions.py

#Instinctively I want a new script for item interactions, that I can send to from membrane. But isn't that what the itemRegistry is for?
#It kinda is...
from itemRegistry import ItemInstance, registry
from env_data import cardinalInstance, locRegistry as loc
from misc_utilities import assign_colour

def look_at(response):
    print("[LOOK_AT] in item interactions.")
    print(f"Response: {response}")


def look_at_item(item_inst): ## this is just using everything from registry. Should really just be in registry....

    if isinstance(item_inst, ItemInstance):
        #print(f"item_inst.location: {item_inst.location}")
        confirmed, reason_val = registry.check_item_is_accessible(item_inst)
        if reason_val not in (0, 2):
            print(f"Cannot look at {item_inst.name}.")
        #if reason_val == 0:
        #    print("REASON VAL:: Accessible item. continue with action.")
        #elif reason_val == 1:
        #    print("REASON VAL:: Item is in a container that is closed and/or locked.")
        #elif reason_val == 2:
        #    print("REASON VAL:: ITEM IS IN INVENTORY ALREADY.")
        #elif reason_val == 3:
        #    print("REASON VAL:: Item is not at the current location or on your person.")

        else:
            if reason_val == 2:
                extra = " in your inventory."
            else:
                extra = "."
            print(f"You look at the {item_inst.name}{extra}")
            print(assign_colour(registry.describe(item_inst, caps=True), colour="description"))


def add_item_to_loc(item_instance, location=None):

    if location == None:
        location = loc.current_cardinal
    if location != None and location != loc.current_cardinal:
        print(f"You're currently at {loc.current_cardinal.place_name}. You can't leave {item_instance.name} at {location.name} unless you move there first.")

    if isinstance(location, cardinalInstance):
        registry.move_item(inst=item_instance, location=location)
    else:
        print("add_item_to_location needs a cardinalInstance.")
        exit

"""
def add_item_to_container(container:ItemInstance):
    from item_definitions import container_limit_sizes
    from set_up_game import game
    if "container" in container.flags:
        container_size = container.container_limits
        container_size = container_limit_sizes[container_size]
        from misc_utilities import generate_clean_inventory, compare_input_to_options, from_inventory_name

        def get_suitable_items():
            add_x_to = []
            inv_list = []
            for item in game.inventory:
                item_size = item.item_size
                item_size = container_limit_sizes[item_size]
                if item_size < container_size:
                    #print(f"Item size {item}, {item_size}, < container size {container.name}, container_size: {container_size}")
                    add_x_to.append(item)

                    inv_list, _ = generate_clean_inventory(add_x_to)
            return inv_list, add_x_to

        done=False
        while not done:
            inv_list, add_x_to = get_suitable_items()
            test = option(inv_list, preamble=f"Choose an object to put inside {assign_colour(container, switch=True)} or hit enter when done:", print_all=True)
            if test == "" or test == None:
                do_print(assign_colour(f"(Chosen: <NONE>) [add_item_to_container]", "yellow"))
                done=True
                break
            cleaned, alignment = compare_input_to_options(inv_list, input=test, inventory=game.inventory, use_last=False)

            if cleaned:
                outcome_ref = alignment.get(cleaned)
                #print(f"Cleaned: {cleaned}, alignment: {alignment}")
                if outcome_ref:
                    #print(f"outcome ref: {outcome_ref}")
                    instance = outcome_ref.get("instance")
                    if not instance:
                        print("no instance ")
                        instance = from_inventory_name(cleaned, add_x_to)
                else:
                    instance = from_inventory_name(test, add_x_to)
                    #print(f"instance from alignment: {instance}")
                #print(f"outcome: {outcome}, alignment: {outcome_ref}")
                #instance = from_inventory_name(test, add_x_to)
                #print(f"Instance from from_inventory_name: {instance}")
                #exit()
                result = [(f"Added [child] to [new_container]", assign_colour(instance), assign_colour(container))]
                from misc_utilities import clean_separation_result
                clean_separation_result(result, to_print=True)
                registry.move_item(instance, new_container=container)
                game.inventory.remove(instance)
"""
