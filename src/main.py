from datetime import datetime
from get_weather import retrieve_all_weather
from draw_display import draw_and_update_display
import traceback

def try_run_print_log(state, function, function_description=None):
    if function_description is None:
        function_description = function.__name__

    try:
        print("-------------------")
        print("%s Started on %s" % (function_description, datetime.now().strftime('%Y-%m-%d (%a) %H:%M:%S'),))
        print("-------------------")
        function(state)
        print("%s Finished on %s" % (function_description, datetime.now().strftime('%Y-%m-%d (%a) %H:%M:%S'),))
    except Exception as exception:
        # Output unexpected Exceptions.
        print(exception)
        print(exception.__class__.__name__)
        traceback.print_exc()
        print("%s Failed on %s" % (function_description, datetime.now().strftime('%Y-%m-%d (%a) %H:%M:%S'),))


if __name__ == "__main__":
    state = {}
    current_hour = datetime.now().hour
    # Opeartion time by hours of day
    if current_hour > 0 and current_hour < 6:
        print("-------------------")
        print(" Current time is outside operaation time: %s" % datetime.now().strftime('%Y-%m-%d (%a) %H:%M:%S'))
        print("Good night.")
        print("-------------------")
    else:
        try_run_print_log(state, retrieve_all_weather, "Retrieve Weather")
        try_run_print_log(state, draw_and_update_display, "Display Update")

    print(" - - - - - - - - - - - -")
