# uncomment the following line to install geopy if not installed already
###
# pip install geopy
###

import tkinter as tk
from geopy.geocoders import Nominatim
import os


class TkinterGuard:
    _active_root = None

    @classmethod
    def create_root(cls):
        if cls._active_root is not None:
            raise RuntimeError(
                "A Tk() instance is already running. Close it before creating another."
            )
        cls._active_root = tk.Tk()
        return cls._active_root

    @classmethod
    def destroy_root(cls):
        if cls._active_root is not None:
            try:
                cls._active_root.destroy()
            finally:
                cls._active_root = None


class AppState:
    def __init__(self):
        self.latitude = None
        self.longitude = None


class LocationApp:
    PLACEHOLDER_TEXT = "e.g., Greenville, NC or 27858"

    def __init__(self):
        self.state = AppState()
        self.geolocator = Nominatim(user_agent="sun_sim_app") # this is the geopy geolocator for converting location input to coordinates
        self.file_path = os.path.join(os.path.dirname(__file__), "location.txt") # this is the path to the file where the coordinates will be stored

        self.root = TkinterGuard.create_root()
        self.root.title("Sun Simulation Control Panel")
        self.root.geometry("420x420")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_ui()

    def _build_ui(self):
        tk.Label(self.root, text="Set Simulation Location", font=("Arial", 14)).pack(pady=10)

        instructions = (
            "Enter a valid location to calculate sun movement.\n\n"
            "Accepted formats:\n"
            "• City, State (Atlanta, GA)\n"
            "• ZIP Code (12345)\n"
        )
        tk.Label(self.root, text=instructions, font=("Arial", 9), justify="center").pack(pady=5)

        self.location_entry = tk.Entry(self.root, width=35, fg="gray")
        self.location_entry.insert(0, self.PLACEHOLDER_TEXT)
        self.location_entry._placeholder_active = True
        self.location_entry.pack(pady=8)

        # these bindings handle the placeholder text behaviour and submission when the user presses Enter
        self.location_entry.bind("<FocusIn>", self.clear_placeholder)
        self.location_entry.bind("<FocusOut>", self.add_placeholder)
        self.location_entry.bind("<Return>", self.submit_location)

        tk.Button(self.root, text="Set Location", command=self.submit_location).pack(pady=10)

        self.result_label = tk.Label(self.root, text="", font=("Arial", 10))
        self.result_label.pack(pady=5)

        self.error_label = tk.Label(self.root, text="", font=("Arial", 9))
        self.error_label.pack()

    def get_coordinates(self, location_input):
        try:
            location = self.geolocator.geocode(location_input, timeout=5)
            if location:
                return location.latitude, location.longitude
        except Exception as e:
            print("Geocoding error:", e)
        return None, None

    # this is for writing the coordinates to a file called location.txt in the same directory as this script, 
    # so that the sun simulation can read it and use the coordinates for its calculations
    def write_coordinates_to_file(self, lat, lon):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(f"{lat},{lon}")
        except Exception as e:
            print("File write error:", e)

    # validates the user input, gets the coordinates using geopy, 
    # updates the state, shows success or error messages, 
    # and writes the coordinates to a file for the sun simulation to use
    def submit_location(self, event=None):
        user_input = self.location_entry.get().strip()

        if (
            self.location_entry._placeholder_active
            or not user_input
            or user_input.isspace()
        ):
            self.show_error("Please enter a valid location (e.g., Atlanta, GA or 30301)")
            return

        lat, lon = self.get_coordinates(user_input)

        if lat is not None and lon is not None:
            self.state.latitude = lat
            self.state.longitude = lon
            self.show_success(lat, lon)
            self.write_coordinates_to_file(lat, lon)
            print("Stored Coordinates:", lat, lon)
        else:
            self.show_error(
                "Location not found.\n"
                "Try formats like:\n"
                "- City, State (Dallas, TX)\n"
                "- ZIP code (90210)"
            )

    def show_error(self, message):
        self.error_label.config(text=message, fg="red")
        self.result_label.config(text="")

    def show_success(self, lat, lon):
        self.error_label.config(text="")
        self.result_label.config(
            text=f"✔ Location set:\nLatitude: {lat:.4f}\nLongitude: {lon:.4f}",
            fg="green"
        )

    def clear_placeholder(self, event):
        if self.location_entry._placeholder_active:
            self.location_entry.delete(0, tk.END)
            self.location_entry.config(fg="black")
            self.location_entry._placeholder_active = False

    def add_placeholder(self, event):
        if not self.location_entry.get():
            self.location_entry.insert(0, self.PLACEHOLDER_TEXT)
            self.location_entry.config(fg="gray")
            self.location_entry._placeholder_active = True

    def on_close(self):
        TkinterGuard.destroy_root()

    def run(self):
        self.root.mainloop()

# fixes the issue of multiple Tk() instances by using a guard class to manage the root window,
# and ensures that the geolocator and file path are initialised properly in the constructor
if __name__ == "__main__":
    app = LocationApp()
    app.run()
