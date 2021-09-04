from datetime import datetime
from get_weather import retrieve_all_weather
from draw_display import draw_and_update_display


def try_run_print_log(function, function_description=None):
    if function_description is None:
        function_description = function.__name__

    try:
        print("-------------------")
        print("%s Started on %s" % (function_description,datetime.now().strftime('%Y-%m-%d (%a) %H:%M:%S'),))
        print("-------------------")
        function()
        print("%s Finished on %s" % (function_description,datetime.now().strftime('%Y-%m-%d (%a) %H:%M:%S'),))
    except Exception as exception:
        # Output unexpected Exceptions.
        print(exception, False)
        print(exception.__class__.__name__ + ": " + exception.message)
        print("%s Failed on %s" % (function_description,datetime.now().strftime('%Y-%m-%d (%a) %H:%M:%S'),))


if __name__ == "__main__":
    try_run_print_log(retrieve_all_weather, "Retrieve Weather")
    try_run_print_log(draw_and_update_display, "Display Update")

    print(" - - - - - - - - - - - -")
