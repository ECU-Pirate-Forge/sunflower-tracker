# pan_test.py
# Webots controller for tracking light and writing sensor data to CSV

try:
    from controller import Robot
except ImportError:
    Robot = None

import csv

# --- Tuning ---
DEADBAND = 0.02
STEP = 0.05
PRINT_EVERY_N_STEPS = 10


def run_webots_loop():
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    # Motors
    pan_motor = robot.getDevice("pan_motor")
    tilt_motor = robot.getDevice("tilt_motor")
    pan_motor.setVelocity(1.5)
    tilt_motor.setVelocity(1.5)

    # Sensors
    light_left = robot.getDevice("light_left")
    light_right = robot.getDevice("light_right")
    light_left.enable(timestep)
    light_right.enable(timestep)

    # Tracking state
    t = 0.0
    step_count = 0
    current_pan = 0.0

    # CSV file setup
    file = open("sensor_data.csv", "w", newline="")
    writer = csv.writer(file)
    writer.writerow(["time", "left", "right", "diff"])

    while robot.step(timestep) != -1:
        t += timestep / 1000.0
        step_count += 1

        # Read sensors
        l = float(light_left.getValue())
        r = float(light_right.getValue())
        diff = l - r

        # Tracking logic
        if diff > DEADBAND:
            current_pan += STEP
        elif diff < -DEADBAND:
            current_pan -= STEP

        pan_motor.setPosition(current_pan)
        tilt_motor.setPosition(0.0)

        # Write to CSV
        writer.writerow([t, l, r, diff])
        file.flush()

        # Debug print
        if step_count % PRINT_EVERY_N_STEPS == 0:
            print(f"L:{l:.3f} R:{r:.3f} diff:{diff:.3f}")


if __name__ == "__main__":
    if Robot is None:
        raise RuntimeError("Run inside Webots")

    run_webots_loop()