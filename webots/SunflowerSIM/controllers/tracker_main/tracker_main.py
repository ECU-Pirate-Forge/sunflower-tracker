# Minimal controller to verify light sensors on the pan/tilt mount.
# Prints L/R + diff and a direction label (LEFT/RIGHT/CENTER).
#
# Notes:
# - A sensor can sit near a "floor" value when facing away from the sun or shaded.
# - DEADBAND avoids jitter when readings are almost equal.
# - Near the sensor "ceiling" (both sensors high), tiny diffs can still be meaningful,
#   so we reduce the deadband to satisfy the edge-case unit test.

import math
import threading
import tkinter as tk
from queue import Queue, Empty
from typing import List, Tuple
from controller import Robot
from tracker import config
from tracker.sensors import init_light_sensors, read_light_sensors
from tracker.pan_closed_loop import update_pan_closed_loop
from tracker.tilt_open_loop import update_open_loop_tilt
from tracker.tilt_closed_loop import update_tilt_closed_loop


# --- Mode constants ---
MODE_OPEN_LOOP   = 1
MODE_HYBRID      = 2
MODE_CLOSED_LOOP = 3

MODE_LABELS = {
    MODE_OPEN_LOOP:   "Open-Loop",
    MODE_HYBRID:      "Hybrid",
    MODE_CLOSED_LOOP: "Closed-Loop",
}

# --- Tuning knobs ---
DEADBAND            = 0.02
PRINT_EVERY_N_STEPS = 10

PAN_AMPLITUDE  = 1.0   # radians
PAN_FREQ       = 1.0   # rad/sec
TILT_AMPLITUDE = 0.6   # radians
TILT_FREQ      = 0.7   # rad/sec

# --- Ceiling handling ---
CEILING_THRESHOLD      = 0.15
CEILING_DEADBAND_SCALE = 0.10

PATTERN = [
    (0.0,  3000),
    (0.8,  3000),
    (0.0,  3000),
    (-0.8, 3000),
    (0.0,  3000),
]

# --- Shared state (UI thread <-> simulation loop) ---
current_mode = MODE_OPEN_LOOP
mode_lock    = threading.Lock()
log_queue: Queue = Queue()


class ModeControlUI:
    """Floating window showing active mode and live sensor log."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sunflower Tracker – Mode Control")
        self.root.geometry("420x300")
        self.root.resizable(False, False)

        # Current mode display
        tk.Label(root, text="Current Mode:", font=("Arial", 11)).pack(pady=(14, 0))
        self.mode_value = tk.Label(
            root,
            text=MODE_LABELS[MODE_OPEN_LOOP],
            font=("Arial", 20, "bold"),
            fg="#4CAF50",
        )
        self.mode_value.pack(pady=(2, 4))

        tk.Label(
            root,
            text="[1] Open-Loop     [2] Hybrid     [3] Closed-Loop",
            font=("Arial", 9),
            fg="gray",
        ).pack()

        # Live log output
        log_frame = tk.Frame(root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_box = tk.Text(
            log_frame,
            height=8,
            state=tk.DISABLED,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),
            bg="#1e1e1e",
            fg="#d4d4d4",
        )
        self.log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_box.yview)

        # Keyboard bindings
        self.root.bind("1", lambda _: self._set_mode(MODE_OPEN_LOOP))
        self.root.bind("2", lambda _: self._set_mode(MODE_HYBRID))
        self.root.bind("3", lambda _: self._set_mode(MODE_CLOSED_LOOP))

        self._poll_log()

    def _set_mode(self, mode: int) -> None:
        global current_mode
        with mode_lock:
            current_mode = mode
        self.mode_value.config(text=MODE_LABELS[mode])

    def _poll_log(self) -> None:
        """Drain the log queue and append to the text widget (100 ms interval)."""
        try:
            while True:
                msg = log_queue.get_nowait()
                self.log_box.config(state=tk.NORMAL)
                self.log_box.insert(tk.END, msg + "\n")
                self.log_box.see(tk.END)
                self.log_box.config(state=tk.DISABLED)
        except Empty:
            pass
        self.root.after(100, self._poll_log)


def run_ui() -> None:
    """Entry point for the UI thread."""
    root = tk.Tk()
    ModeControlUI(root)
    root.mainloop()


def step_pattern(
    index: int,
    elapsed: int,
    timestep: int,
    pattern: List[Tuple[float, int]],
) -> Tuple[int, int, float]:
    elapsed += timestep
    target, dwell = pattern[index]
    if elapsed >= dwell:
        elapsed = 0
        index = (index + 1) % len(pattern)
        target, _ = pattern[index]
    return index, elapsed, target


def classify_direction(l: float, r: float, deadband: float = DEADBAND) -> str:
    """Return LEFT / RIGHT / CENTER based on sensor difference."""
    effective_deadband = deadband
    if l >= CEILING_THRESHOLD and r >= CEILING_THRESHOLD:
        effective_deadband = deadband * CEILING_DEADBAND_SCALE
    diff = l - r
    if diff > effective_deadband:
        return "LEFT"
    if diff < -effective_deadband:
        return "RIGHT"
    return "CENTER"


def main() -> None:
    # Launch UI in a daemon thread so it exits with the simulation
    ui_thread = threading.Thread(target=run_ui, daemon=True)
    ui_thread.start()

    robot   = Robot()
    timestep = int(robot.getBasicTimeStep())

    pan_motor  = robot.getDevice(config.PAN_MOTOR_NAME)
    pan_motor.setVelocity(config.PAN_MOTOR_VELOCITY)
    tilt_motor = robot.getDevice(config.TILT_MOTOR_NAME)
    tilt_motor.setVelocity(config.TILT_MOTOR_VELOCITY)

    light_left  = robot.getDevice("light_left")
    light_right = robot.getDevice("light_right")
    light_left.enable(timestep)
    light_right.enable(timestep)

    t             = 0.0
    step_count    = 0
    pattern_index = 0
    elapsed       = 0
    pan_motor.setPosition(PATTERN[pattern_index][0])

    while robot.step(timestep) != -1:
        t          += timestep / 1000.0
        step_count += 1

        # Read sensors (fixes ll/lr -> l/r variable mismatch from previous version)
        l    = float(light_left.getValue())
        r    = float(light_right.getValue())
        diff = l - r
        side = classify_direction(l, r)

        # Snapshot mode once per step to keep behavior consistent within a step
        with mode_lock:
            mode = current_mode

        # --- Mode dispatch ---
        if mode == MODE_OPEN_LOOP:
            # Pure sine-wave drive on both axes; no sensor feedback
            pan_motor.setPosition(PAN_AMPLITUDE * math.sin(PAN_FREQ * t))
            update_open_loop_tilt(tilt_motor)

        elif mode == MODE_HYBRID:
            # Open-loop pan, closed-loop tilt
            pan_motor.setPosition(PAN_AMPLITUDE * math.sin(PAN_FREQ * t))
            update_tilt_closed_loop(tilt_motor, l, r)

        elif mode == MODE_CLOSED_LOOP:
            # Full sensor-feedback control on both axes
            update_pan_closed_loop(pan_motor, l, r)
            update_tilt_closed_loop(tilt_motor, l, r)

        # Log to console and UI every N steps
        if step_count % PRINT_EVERY_N_STEPS == 0:
            msg = (
                f"[{MODE_LABELS[mode]:<12}]  "
                f"L:{l:.3f}  R:{r:.3f}  diff:{diff:+.3f}  -> {side}"
            )
            print(msg)
            log_queue.put(msg)


if __name__ == "__main__":
    main()
