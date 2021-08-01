from datetime import datetime
try:
    print("Display update Started on " + datetime.now().strftime('%Y-%m-%d (%a) %H:%M:%S'))
    import display_date
    print("Display update Success on " + datetime.now().strftime('%Y-%m-%d (%a) %H:%M:%S'))
except Exception as exception:
    # Output unexpected Exceptions.
    print(exception, False)
    print(exception.__class__.__name__ + ": " + exception.message)
    print("Display update Failed on " + datetime.now().strftime('%Y-%m-%d (%a) %H:%M:%S'))
print(" - - -")
