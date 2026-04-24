import tkinter as tk
import csv
import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class SensorGraphUI:
    def __init__(self, root):
        self.root = root

        self.root.title("Sunflower Tracker Live Sensor Dashboard")
        self.root.geometry("950x600")

        self.figure = Figure(figsize=(9.5, 5.5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Show only the most recent points so the graph stays readable
        self.max_points_to_show = 300

        # Refresh rate in milliseconds
        self.update_interval_ms = 300

        self.update_graph()

    def load_sensor_data(self):
        timestamps = []
        left = []
        right = []
        diff = []

        file_path = os.path.join(os.path.dirname(__file__), "sensor_data.csv")

        try:
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                next(reader, None)

                for row in reader:
                    if len(row) < 4:
                        continue

                    timestamps.append(float(row[0]))
                    left.append(float(row[1]))
                    right.append(float(row[2]))
                    diff.append(float(row[3]))

        except FileNotFoundError:
            pass
        except ValueError:
            pass

        return timestamps, left, right, diff

    def update_graph(self):
        timestamps, left, right, diff = self.load_sensor_data()

        # Keep the graph focused on recent activity
        timestamps = timestamps[-self.max_points_to_show:]
        left = left[-self.max_points_to_show:]
        right = right[-self.max_points_to_show:]
        diff = diff[-self.max_points_to_show:]

        self.ax.clear()

        if len(timestamps) > 0:
            latest_left = left[-1]
            latest_right = right[-1]
            latest_diff = diff[-1]

            if latest_diff > 0.02:
                status = "Turning Left: left sensor is receiving more light"
            elif latest_diff < -0.02:
                status = "Turning Right: right sensor is receiving more light"
            else:
                status = "Centered: left and right sensors are balanced"

            self.ax.plot(
                timestamps,
                left,
                label="Left light sensor reading",
                linewidth=2
            )

            self.ax.plot(
                timestamps,
                right,
                label="Right light sensor reading",
                linewidth=2
            )

            self.ax.plot(
                timestamps,
                diff,
                label="Direction signal: left - right",
                linewidth=2.5,
                linestyle="--"
            )

            # Reference line: diff = 0 means centered
            self.ax.axhline(
                0,
                linestyle=":",
                linewidth=1.5,
                label="Centered line (diff = 0)"
            )

            self.ax.set_title(
                f"Live Sunflower Tracker Sensor Data\n{status}",
                fontsize=14
            )

            self.ax.text(
                0.02,
                0.95,
                f"Latest values\n"
                f"Left: {latest_left:.3f}\n"
                f"Right: {latest_right:.3f}\n"
                f"Diff: {latest_diff:.3f}",
                transform=self.ax.transAxes,
                verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
            )

            # Dynamic y-axis padding
            all_values = left + right + diff
            min_y = min(all_values)
            max_y = max(all_values)
            padding = max((max_y - min_y) * 0.15, 0.01)
            self.ax.set_ylim(min_y - padding, max_y + padding)

        else:
            self.ax.set_title("Waiting for sensor data...")
            self.ax.text(
                0.5,
                0.5,
                "Start the Webots simulation to generate sensor data.",
                ha="center",
                va="center",
                transform=self.ax.transAxes
            )

        self.ax.set_xlabel("Simulation Time (seconds)")
        self.ax.set_ylabel("Sensor Reading / Direction Difference")
        self.ax.grid(True, alpha=0.4)
        self.ax.legend(loc="upper right")

        self.figure.tight_layout()
        self.canvas.draw_idle()

        self.root.after(self.update_interval_ms, self.update_graph)


def main():
    root = tk.Tk()
    SensorGraphUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()