
from csv import excel


def log_objects(objects, input_str, run_tag):
    from datetime import datetime

    date = datetime.now()
    date = date.strftime("%d_%m_%Y")#_%H_%M_%S")
    log_file = f"logs/mem_checker_{date}.csv"

    with open(log_file, "a+") as log:
        import csv
        csv_writer = csv.writer(log, dialect=excel)
        csv_writer.writerow([str(objects), f"`[{run_tag}:] {input_str}`"])


def report_memory_usage_for_fn(fn):
    from memory_profiler import memory_usage

    mem_usage = memory_usage(proc=(fn, (), {}))
    #print(f"Memory usage: {mem_usage}")
    #print(f"Peak increase: {max(mem_usage) - min(mem_usage)} MB")
    return f"Peak increase: {max(mem_usage) - min(mem_usage)} MB"


if  __name__ == "__main__":

    from test_runme import test_main
    #from initialise_all import initialise_all
    usage = report_memory_usage_for_fn(fn=test_main)
    print(usage)


"""
Notes 18/2/26 objs, 37 command run:
Single run:
Start 15447
End 16095

Repeat loops:
Start 15453
End 16104

Start 16104
End: 16179

Start: 16179
End: 16245
"""
