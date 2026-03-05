# pan_test.py
# Minimal controller to verify pan/tilt motors + light sensors.
# Prints L/R + diff and a direction label (LEFT/RIGHT/CENTER).
# Note: A sensor may sit near a "floor" value when facing away from the sun or shaded.

from controller import Robot
import math

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# --- Motors ---
pan_motor = robot.getDevice("pan_motor")
tilt_motor = robot.getDevice("tilt_motor")

# Set visible speeds
pan_motor.setVelocity(1.5)
tilt_motor.setVelocity(1.5)

# --- Joint sensors (still enabled, but not printed) ---
pan_sensor = robot.getDevice("pan_sensor")
tilt_sensor = robot.getDevice("tilt_sensor")
pan_sensor.enable(timestep)
tilt_sensor.enable(timestep)

# --- Light sensors ---
light_left = robot.getDevice("light_left")
light_right = robot.getDevice("light_right")
light_left.enable(timestep)
light_right.enable(timestep)

# --- Tuning knobs ---
PAN_AMPLITUDE = 1.0        # radians
PAN_FREQ = 1.0             # rad/sec for sine input
TILT_AMPLITUDE = 0.6       # radians
TILT_FREQ = 0.7            # rad/sec for sine input

DEADBAND = 0.02            # diff threshold to call LEFT/RIGHT
PRINT_EVERY_N_STEPS = 10   # reduce console spam

t = 0.0
step_count = 0

while robot.step(timestep) != -1:
    # time in seconds
    t += timestep / 1000.0
    step_count += 1

    # Drive motors with smooth motion (so sensors see changing angles)
    pan_target = PAN_AMPLITUDE * math.sin(PAN_FREQ * t)
    tilt_target = TILT_AMPLITUDE * math.sin(TILT_FREQ * t)
    pan_motor.setPosition(pan_target)
    tilt_motor.setPosition(tilt_target)

    # Read light sensors
    l = float(light_left.getValue())
    r = float(light_right.getValue())
    diff = l - r

    # Direction classification
    if diff > DEADBAND:
        side = "LEFT"
    elif diff < -DEADBAND:
        side = "RIGHT"
    else:
        side = "CENTER"

    # Print occasionally (NO pan/tilt printed)
    if step_count % PRINT_EVERY_N_STEPS == 0:
        print(f"L:{l:.3f} R:{r:.3f} diff:{diff:.3f} -> {side}")