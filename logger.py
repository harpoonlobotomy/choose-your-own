import inspect
import logging

logging_config = {
    "function_logging": False,
    "args": False,
    "details": True,
    "traceback": False,
    "ignore": []
    }

logger = logging.getLogger("main.FuncTracer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def traceback_fn():
    # to run at expected error points to trace why it failed.
    frame = inspect.currentframe().f_back
    args = inspect.getargvalues(frame)
    functionname = frame.f_code.co_name
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

    print(f"Traceback point encountered in {functionname}:  ")
    for item in args_list:
        args_val = loc.get(item)
        if args_val and item != "self":
            print(f"\033[0;44m{item}: {args_val}\033[0m")
    from traceback import print_stack
    print(print_stack(f=frame))
    ##  Args: ArgInfo(args=['no_lookup', 'print_all', 'none_possible', 'preamble', 'inventory', 'look_around', 'return_any'], varargs='values', keywords=None, locals={'no_lookup': None, 'print_all': True, 'none_possible': True, 'preamble': 'Please pick your destination:', 'inventory': False, 'look_around': False, 'return_any': False, 'values': (['a graveyard', 'a forked tree branch', 'a city hotel room', 'a pile of rocks'],)})

def logging_fn(note:str=""):

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
        #if logging_config["ignore_item_man"] and filename == "itemRegistry.py":

        plain_formatting = "\033[3;34m"
        fancy_formatting = "\033[4;1;35m"
        note_formatting = "\033[0;42m"
        clear_formatting = "\033[0m"

        start = f"{plain_formatting}(  Func: {clear_formatting}"
        middle = f"{fancy_formatting}{functionname}{clear_formatting}"
        if note:
            note = f"{note_formatting}{note}{clear_formatting}"
        end = f"{plain_formatting}  ){clear_formatting}"

        print(start, middle, note, end)
        if logging_config["args"]:
            args = inspect.getargvalues(frame)
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


