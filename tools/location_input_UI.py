# tested using python 3.14.1
# tkinter is included in python
# no need to install it 

# uncomment the following line to install geopy if you haven't already
### \/ \/ \/
# pip install geopy
### /\ /\ /\


# this modules ensures multiple Tk instaces are not created

import tkinter as tk

# this prevents multiple Tk instances from being created
class TkinterGuard:
    _active_root = None

    # this is a context manager to ensure the root window is properly destroyed
    @classmethod
    def create_root(cls):
        if cls._active_root is not None:
            raise RuntimeError(
                "A Tk() instance is already running. " \
                "Close the existing window before creating a new one."
            )
        # create the root window and store it in the class variable
        cls._active_root = tk.Tk()
        return cls._active_root

    # just a helper method to destroy the root window if it exists
    @classmethod
    def destroy_root(cls):
        if cls._active_root is not None:
            try:
                cls._active_root.destroy()
            finally:
                cls._active_root = None

from geopy.geocoders import Nominatim

# this is required to store the coordinates
class AppState:
    def __init__(self):
        self.latitude = None
        self.longitude = None

state = AppState()

# intialize geolocator
geolocator = Nominatim(user_agent="sun_sim_app")

# this is what takes the user input 
# and returns the coordinates, or None if not found
def get_coordinates(location_input):
    try:
        location = geolocator.geocode(location_input, timeout=5)
        if location:
            return location.latitude, location.longitude
    except Exception:
        pass
    return None, None

# this function shows the error message when the location is not found
def show_error(message):
    error_label.config(text=message, fg="red")
    result_label.config(text="") # use format (text="", fg="")
                                 # if you want to add additional error messages

# this function shows the successful retrieval of coordinates
def show_success(lat, lon):
    error_label.config(text="")
    result_label.config(
        text=f"✔ Location set:\nLatitude: {lat:.4f}\nLongitude: {lon:.4f}",
        fg="green"
    )

# this is the main function that gets called when the user submits the location
# it validates the input, gets the coordinates, and updates the state
def submit_location(event=None):
    user_input = location_entry.get().strip()

    if not user_input:
        show_error("Input required. Example: 'New York, NY' or '27858'")
        return

    lat, lon = get_coordinates(user_input)

    if lat is not None and lon is not None:
        state.latitude = lat
        state.longitude = lon
        show_success(lat, lon)

        # note: in a real application, you would likely trigger the 
        # sun simulation update here
        # for now, it just prints the stored coordinates
        print("Stored Coordinates:", state.latitude, state.longitude)
    else:
        show_error(
            "Location not found.\n"
            "Try formats like:\n"
            "- City, State (e.g., Dallas, TX)\n"
            "- ZIP code (e.g., 90210)"
        )

# CoPilot provided the following functions to manage the placeholder 
# text in the input field
# this function manages the placeholder text in the input field
def clear_placeholder(event):
    if location_entry.get() == "e.g., Greenville, NC or 27858":
        location_entry.delete(0, tk.END)
        location_entry.config(fg="black")

# this function restores the placeholder text if the field is left empty
def add_placeholder(event):
    if not location_entry.get():
        location_entry.insert(0, "e.g., Greenville, NC or 27858")
        location_entry.config(fg="gray")

# this is the main GUI setup
root = tk.Tk()
root.title("Sun Simulation Control Panel") # not actually setting the simulation location, just the window title
root.geometry("420x420") # width x height
root.resizable(False, False) # disable resizing to keep the layout consistent

# title
# note: this doesn't actually set the simulation location
# it just shows the title of the app
tk.Label(root, text="Set Simulation Location", font=("Arial", 14)).pack(pady=10)

# instructions, easy to understand, and shows the accepted formats for input
# note: this is just a label with instructions, it doesn't validate the input
instructions = (
    "Enter a valid location to calculate sun movement.\n\n"
    "Accepted formats:\n"
    "• City, State (e.g., Atlanta, GA)\n"
    "• ZIP Code (e.g., 12345)\n"
)
tk.Label(root, text=instructions, font=("Arial", 9), justify="center").pack(pady=5)

# Thanks CoPilot
# this is the input field for the location, 
# it has a placeholder text that guides the user on what to enter
location_entry = tk.Entry(root, width=35, fg="gray")
location_entry.insert(0, "e.g., Greenville, NC or 27858")
location_entry.pack(pady=8)

location_entry.bind("<FocusIn>", clear_placeholder)
location_entry.bind("<FocusOut>", add_placeholder)
location_entry.bind("<Return>", submit_location)

# submit Button
# pady is padding along y-axis, it adds space around the button
tk.Button(root, text="Set Location", command=submit_location).pack(pady=10)

# Result display
# just a baseline for now
result_label = tk.Label(root, text="", font=("Arial", 10))
result_label.pack(pady=5)

# error message
# note: this is required and if commented out/removed
# the app will give a traceback error when trying to show an error message
error_label = tk.Label(root, text="", font=("Arial", 9))
error_label.pack()

# Run App
root.mainloop()