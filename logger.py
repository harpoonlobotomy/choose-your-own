import inspect
import logging

logging_config = {
    "function_logging": True,
    "details": True,
    "traceback": False,
    "ignore": []
    }

  ## SCRIPT IDENTIFICATION ##
 ## this whole thing is stupid.
#I'm so tired. So fucking tired.

item_man = "item_management_2.py",
item_defs = "item_definitions.py",
places = "env_data.py",
utilities = "misc_utilities.py",
set_up_game = "set_up_game.py",
colour_class = "colours.py",
choices = "choices.py",
main_script = "choose_a_path_tui_vers.py"

layout = "layout.py",
tui_elements = "tui_elements.py",
tui_update = "tui_update.py",

scripts_list = [item_man, item_defs, layout, places, utilities, set_up_game, tui_elements, tui_update, colour_class, choices, main_script]

 #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#

logger = logging.getLogger("main.FuncTracer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

#class FuncTracer:
#    def __init__(self):
#        self.logger = logging.getLogger("FuncTracer")
#        #self.logger.info('creating an instance of Auxiliary')

categories = ["colour", "instance_data", ""]



def logging_fn(traceback=False, category=None):

    frame = inspect.currentframe().f_back
    #data == frame obj

#        Frame objects provide these attributes:
#        f_back          next outer frame object (this frame's caller)
#        f_builtins      built-in namespace seen by this frame
#        f_code          code object being executed in this frame
#        f_globals       global namespace seen by this frame
#        f_lasti         index of last attempted instruction in bytecode
#        f_lineno        current line number in Python source code
#        f_locals        local namespace seen by this frame
#        f_trace         tracing function for this frame, or None"""

        #data: <frame at 0x00000193B9B1A560, file 'D:\\Git_Repos\\choose-your-own\\choose_a_path_tui_vers.py', line 949, code look_light>


    if logging_config["function_logging"]:
        functionname = frame.f_code.co_name
        filename = frame.f_code.co_filename
        #if logging_config["ignore_item_man"] and filename == "item_management_2.py":

        lineno = frame.f_lineno

        filename = filename.split("\\")[-1]
        text=f"((FILE: {filename}. FN: {functionname}. LINE: {lineno}))"
        code = "\033[4;41m"
        ending= f"{text}\033[0m"
        print(f"{code}{ending}")
        args = inspect.getargvalues(frame)
        #print(f"Args: {args}")
        #
        # Args: ArgInfo(args=['self'], varargs=None, keywords=None, locals={'self': <item_management_2.LootRegistry object at 0x000002493DAD9E80>})
        arg = args.args
        var = args.varargs
        kw = args.keywords
        loc = args.locals

        args_list = []
        for item in (arg, var, kw):
            if item != None:
                if isinstance(item, (set|list|tuple)):
                    for subitem in item:
                        args_list.append(subitem)
                else:
                    args_list.append(item)

        for item in args_list:
            args_val = loc.get(item)
            if args_val and item != "self":

                print(f"\033[0;44m{item}: {args_val}\033[0m")

        if traceback or logging_config["traceback"]:
            from traceback import print_stack
            print(print_stack(f=frame))
        ##  Args: ArgInfo(args=['no_lookup', 'print_all', 'none_possible', 'preamble', 'inventory', 'look_around', 'return_any'], varargs='values', keywords=None, locals={'no_lookup': None, 'print_all': True, 'none_possible': True, 'preamble': 'Please pick your destination:', 'inventory': False, 'look_around': False, 'return_any': False, 'values': (['a graveyard', 'a forked tree branch', 'a city hotel room', 'a pile of rocks'],)})

