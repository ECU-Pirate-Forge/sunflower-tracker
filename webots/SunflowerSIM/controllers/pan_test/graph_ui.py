import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sensor_history import SensorHistory


class SensorGraphUI:
    """
    Tkinter-based UI for visualizing light sensor data over time.

    Displays:
    - Left sensor values
    - Right sensor values
    - Difference (left - right)

    Data is pulled from a shared SensorHistory buffer.
    """

    def __init__(self, root, history):
        self.root = root
        self.history = history

        self.root.title("Sunflower Tracker Sensor Graph")
        self.root.geometry("900x500")

        # Create matplotlib figure
        self.figure = Figure(figsize=(9, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        # Embed figure into Tkinter window
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Update interval (milliseconds)
        self.update_interval_ms = 200

        # Start updating graph
        self.update_graph()

    def update_graph(self):
        data = self.history.get_plot_data()

        timestamps = data["timestamps"]
        left = data["light_left"]
        right = data["light_right"]
        diff = data["diff"]

        self.ax.clear()

        if len(timestamps) > 0:
            self.ax.plot(timestamps, left, label="Left Sensor")
            self.ax.plot(timestamps, right, label="Right Sensor")
            self.ax.plot(timestamps, diff, label="Diff")

        self.ax.set_title("Historical Sensor Data")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Sensor Value")
        self.ax.legend()
        self.ax.grid(True)

        # More efficient redraw
        self.canvas.draw_idle()

        # Schedule next update
        self.root.after(self.update_interval_ms, self.update_graph)


def launch_graph_ui(history):
    root = tk.Tk()
    SensorGraphUI(root, history)
    root.mainloop()


if __name__ == "__main__":
    # Standalone test mode (no live data source)
    history = SensorHistory(max_points=100)
    launch_graph_ui(history)