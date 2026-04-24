# pan_test.py
# Controller for testing light sensors on the pan/tilt mount.
# Also integrates real-time visualization via Tkinter + matplotlib.

try:
    from controller import Robot  # Webots runtime
except ImportError:
    Robot = None  # Allows import during testing outside Webots

import math
import threading

from sensor_history import SensorHistory
from graph_ui import launch_graph_ui

# --- Tuning knobs ---
DEADBAND = 0.02                 # Threshold for determining LEFT/RIGHT vs CENTER
PRINT_EVERY_N_STEPS = 10        # Reduce console spam

# Sine wave motion (used to simulate movement for testing sensors)
PAN_AMPLITUDE = 1.0
PAN_FREQ = 1.0
TILT_AMPLITUDE = 0.6
TILT_FREQ = 0.7

# --- "Ceiling" handling ---
# When both sensors are near max values, reduce deadband for better sensitivity
CEILING_THRESHOLD = 0.15
CEILING_DEADBAND_SCALE = 0.10

# --- Shared sensor buffer ---
# Stores recent sensor values for graph visualization
MAX_HISTORY_POINTS = 500
sensor_history = SensorHistory(max_points=MAX_HISTORY_POINTS)


def classify_direction(l: float, r: float, deadband: float = DEADBAND) -> str:
    """
    Determine direction of light based on difference between sensors.

    Returns:
        "LEFT"   -> more light on left
        "RIGHT"  -> more light on right
        "CENTER" -> roughly equal (within deadband)
    """

    # Adjust sensitivity if both sensors are near maximum
    effective_deadband = deadband
    if l >= CEILING_THRESHOLD and r >= CEILING_THRESHOLD:
        effective_deadband = deadband * CEILING_DEADBAND_SCALE

    diff = l - r

    if diff > effective_deadband:
        return "LEFT"
    if diff < -effective_deadband:
        return "RIGHT"
    return "CENTER"


def run_webots_loop(history: SensorHistory):
    """
    Runs the Webots simulation loop in a background thread.

    Responsibilities:
    - Move pan/tilt motors (sine wave for testing)
    - Read light sensor values
    - Compute diff and direction
    - Append data to shared history buffer for graphing
    """

    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    # Get motors
    pan_motor = robot.getDevice("pan_motor")
    tilt_motor = robot.getDevice("tilt_motor")
    pan_motor.setVelocity(1.5)
    tilt_motor.setVelocity(1.5)

    # Get sensors
    light_left = robot.getDevice("light_left")
    light_right = robot.getDevice("light_right")
    light_left.enable(timestep)
    light_right.enable(timestep)

    t = 0.0
    step_count = 0

    while robot.step(timestep) != -1:
        # Track simulation time
        t += timestep / 1000.0
        step_count += 1

        # Move robot in sine wave pattern (for testing sensor response)
        pan_motor.setPosition(PAN_AMPLITUDE * math.sin(PAN_FREQ * t))
        tilt_motor.setPosition(TILT_AMPLITUDE * math.sin(TILT_FREQ * t))

        # Read sensor values
        l = float(light_left.getValue())
        r = float(light_right.getValue())

        # Compute difference and direction
        diff = l - r
        side = classify_direction(l, r)

        # Append data to shared history buffer
        # This feeds the Tkinter graph UI
        history.append(t, l, r)

        # Print debug info occasionally
        if step_count % PRINT_EVERY_N_STEPS == 0:
            print(f"L:{l:.3f} R:{r:.3f} diff:{diff:.3f} -> {side}")


if __name__ == "__main__":
    # Ensure this is only run inside Webots
    if Robot is None:
        raise RuntimeError(
            "This controller must be run inside Webots (controller module not found)."
        )

    # Start Webots simulation loop in a background thread
    # This allows the Tkinter UI to run in the main thread (required on macOS)
    webots_thread = threading.Thread(
        target=run_webots_loop,
        args=(sensor_history,),
        daemon=True
    )
    webots_thread.start()

    # Launch Tkinter graph UI in the main thread
    # This displays real-time sensor data
    launch_graph_ui(sensor_history)