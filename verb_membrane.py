
### So the idea for this is, the verbRegistry identifies parts and figures out what the active verb is. Then it sends the command here, where it's processed according to that parsed data.

## I kinda want to have this in a separate script from the pure 'def move():' type functions.

#Maybe I should move this section into the verbRegistry, and then direct it to this script which just holds the verb actions themselves, not the registry.
# idk I like the idea of the verb-word-objects being different from the verb-action-objects. One's grammatical, one's an action-driver. With the third that is actually a list of functions for specific verbs.
from itemRegistry import registry

class VerbActions:

    def __init__(self, verb_name, attr, formats):
        self.name = verb_name
        self.formats = formats
        self.format_parts = {}
        self.other = {}# is attr with 'format' and 'alt_names' removed. Only the bits needed here.attr

        #print("formats: ", formats)
        for i, format_set in enumerate(formats):
            f_parts_dict = self.format_parts.setdefault(i, {})
            for idx, format_element in enumerate(format_set):
                #print(f"Part: {format_element}")
                f_parts_dict[idx]=format_element
            #print(f_parts_dict)
        self.format_parts = f_parts_dict
        print(list(self.format_parts))
        #print(f"Attr: {attr}")
        for subject, content in attr.items():
            if subject not in ("alt_words", "formats"):
                self.other[subject] = content
        #print(f"self other: {self.other}")


class VerbActionsRegistry:

    def __init__(self):

        self.verb_actions = {}
        self.by_name = {}
        self.by_format = {} # probably not going to be used but will put it here for now anyway.
        ## do I even need this? Probably yes.
        self.all_verb_names = set() # is not the same as all_verbs in VerbRegistry, as it only involves the key verb-names, not the alts.
        self.all_formats = set()
        self.item_action_options = list()

    def create_verb_action(self, verb_key:str, attr:dict, formats:set)->VerbActions:

        self.name = verb_key
        action = VerbActions(verb_key, attr, formats)
        self.verb_actions = action
        #print(f"Action: {dir(action)}")
        #'format_parts', 'formats', 'name', 'other'

        self.by_name[verb_key] = action # not sure if this is the best way.
        self.formats = formats
        self.by_item = set() ## assign verbs to items, eg 'pick up' etc.

        for item in formats:
            self.by_format.setdefault(item, list()).append(action) ## might be better to use name here? Not sure.
        #print(f"Action: {self.__dict__}") ## This is the one I need. Gives me the data inside the object.
        return action

    def get_action_from_name(self, verb_key):

        action_inst = self.by_name[verb_key]
        return action_inst


    def route_verbs(self, reformed_dict):

        noun_inst=None
        for entry in reformed_dict.values():
            for name, content in entry.items():
                if name == "verb":
                    verb_name = content
                if name == "noun":
                    noun_inst=registry.instances_by_name(content)


        #"format", "Reformed list", "Tokens"
        print(f"Verb name: {verb_name}")
        verb_inst = self.get_action_from_name(verb_name)
        #print(f"Verb inst: {verb_inst}")
        from verb_actions import router
        if noun_inst:
            for noun in noun_inst:
                router(noun, verb_inst, reformed_dict)
        else:
            router(noun_inst, verb_inst, reformed_dict)
        return

v_actions = VerbActionsRegistry()

def initialise_registry():

    from verb_definitions import get_verb_defs
    from item_definitions import item_actions

    verb_defs_dict, _ = get_verb_defs()
    #v_actions.all_formats = set(formats.values()) ## Probably don't need this. It's all possible formats but I don't imagine it's useful at all...
    v_actions.all_verb_names = set(verb_defs_dict.keys())
    v_actions.item_action_options = item_actions
    print("v_actions.all_verbs: ", v_actions.all_verb_names)
    print("v_actions.item_action_options: ", v_actions.item_action_options)

    for key, value in verb_defs_dict.items():
        needed_parts = {}
        format_items = list()
        for section, data in value.items():
            if section not in ("alt_names", "allowed_null"):
                needed_parts[section]=data
            if section == "formats":
                for format_inst in data:
                    #print(f"Format inst: {format_inst}, type: {type(format_inst)}, length: {len(format_inst)}")
                    if format_inst not in format_items:
                        format_items.append(format_inst) ## produces a string for single-part entires (only "verb" at this point.)
        v_actions.create_verb_action(key, needed_parts, format_items)
    #print(list(format_items))

if __name__ == "__main__":
    from itemRegistry import initialise_registry as item_reg
    from itemRegistry import registry
    item_reg()
    initialise_registry()

    str_dict = {0: {'verb': 'put'}, 1: {'noun': 'batteries'}, 2: {'null': 'on'}, 3: {'noun': 'glass jar'}}
    verb_name = "put"
    ## Current list of item action flags.
    from verb_actions import router
    verb_instance = v_actions.get_action_from_name(verb_name)
    #print(f"verb_inst: {verb_instance}")
    router(noun_inst=registry.instances_by_name("glass jar")[0], verb_inst = verb_instance, reformed_dict=str_dict)
    ['can_pick_up', 'container', 'flammable', 'dirty', 'locked', 'can_lock', 'fragile', 'can_open', 'can_read', 'can_combine', 'weird', 'dupe', 'is_child', 'combine_with', 'can_remove_from']
