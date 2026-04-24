from collections import deque
from threading import Lock


class SensorHistory:
    """
    Thread-safe fixed-size buffer for storing light sensor data.

    Stores:
    - timestamps
    - left sensor values
    - right sensor values
    - diff (left - right)

    Designed for real-time visualization with Tkinter + matplotlib.
    """

    def __init__(self, max_points=500):
        """
        Initialize buffer with a maximum number of stored points.

        Args:
            max_points (int): Maximum number of data points to keep.
        """
        self.max_points = max_points
        self.lock = Lock()

        # Fixed-size buffers (oldest data is automatically discarded)
        self.timestamps = deque(maxlen=max_points)
        self.light_left = deque(maxlen=max_points)
        self.light_right = deque(maxlen=max_points)
        self.diff = deque(maxlen=max_points)

    def append(self, timestamp, left, right):
        """
        Add a new sensor reading.

        Args:
            timestamp (float): Simulation time
            left (float): Left sensor value
            right (float): Right sensor value
        """
        difference = left - right

        # Lock ensures thread-safe writes (Webots thread + UI thread)
        with self.lock:
            self.timestamps.append(timestamp)
            self.light_left.append(left)
            self.light_right.append(right)
            self.diff.append(difference)

    def get_plot_data(self):
        """
        Retrieve a snapshot of current data for plotting.

        Returns:
            dict: Contains lists of timestamps, left, right, and diff values
        """
        # Return copies to avoid threading issues during plotting
        with self.lock:
            return {
                "timestamps": list(self.timestamps),
                "light_left": list(self.light_left),
                "light_right": list(self.light_right),
                "diff": list(self.diff),
            }

    def __len__(self):
        """
        Returns:
            int: Number of stored data points
        """
        with self.lock:
            return len(self.timestamps)


# --- Standalone test block ---
if __name__ == "__main__":
    print("Running SensorHistory test...")

    history = SensorHistory(max_points=3)

    history.append(0.1, 1.0, 0.5)
    history.append(0.2, 1.1, 0.4)
    history.append(0.3, 1.2, 0.3)
    history.append(0.4, 1.3, 0.2)  # Oldest value should be dropped

    data = history.get_plot_data()

    print("Stored timestamps:", data["timestamps"])
    print("Stored left values:", data["light_left"])
    print("Stored right values:", data["light_right"])
    print("Stored diff values:", data["diff"])
    print("Buffer length:", len(history))