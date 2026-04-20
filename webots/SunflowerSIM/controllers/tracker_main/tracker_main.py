import math
from typing import List, Tuple
from controller import Robot
from tracker import config
from tracker.sensors import init_light_sensors, read_light_sensors
from tracker.pan_closed_loop import update_pan_closed_loop
from tracker.tilt_open_loop import update_open_loop_tilt
from tracker.tilt_closed_loop import update_tilt_closed_loop

"""
---------------------------------GLOBAL VARIABLES---------------------------------
"""

USE_PATTERN = False

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

"""
---------------------------------HELPER FUNCTIONS---------------------------------
"""

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

"""
The code in this function was used multiple times due to the implementation of both open and hybrid logic. To prevent
reusing the same blocks of code in multiple places, this code was placed into a function so only that function call
needs to be used in multiple places, and not the entire code block.

The code's purpose is to determine if the open loop's logic should run on a specifically defined pattern (located in
the step_pattern function), or use sine wave motion to control the motors in open loop logic.
"""
def open_loop_logic(
        pattern_index: int,
        elapsed: int,
        timestep: int,
        pan_motor,
        tilt_motor,
        t: float
):
    if USE_PATTERN:
        pattern_index, elapsed, target = step_pattern(
            pattern_index,
            elapsed,
            timestep,
            PATTERN,
        )
        pan_motor.setPosition(target)
        update_open_loop_tilt(tilt_motor)
    else:
        pan_motor.setPosition(PAN_AMPLITUDE * math.sin(PAN_FREQ * t))
        tilt_motor.setPosition(TILT_AMPLITUDE * math.sin(TILT_FREQ * t))


def classify_direction(l: float, r: float, deadband: float = DEADBAND) -> str:
    effective_deadband = deadband
    if l >= CEILING_THRESHOLD and r >= CEILING_THRESHOLD:
        effective_deadband = deadband * CEILING_DEADBAND_SCALE
    diff = l - r
    if diff > effective_deadband:
        return "LEFT"
    if diff < -effective_deadband:
        return "RIGHT"
    return "CENTER"

"""
---------------------------------CREATION OF MAIN FUNCTION---------------------------------
"""

def main():
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    # --- START SWITCH HARDWARE ---
    selector_motor = robot.getDevice('selector_motor')
    selector_sensor = robot.getDevice('switch_sensor')
    selector_sensor.enable(timestep)
    keyboard = robot.getKeyboard()
    keyboard.enable(timestep)

    MODE_POSITIONS = [0.7, 0.6, 0.5]
    # --- END SWITCH HARDWARE ---

    # Devices that are used within Webots
    pan_motor = robot.getDevice(config.PAN_MOTOR_NAME)
    pan_motor.setVelocity(config.PAN_MOTOR_VELOCITY)
    tilt_motor = robot.getDevice(config.TILT_MOTOR_NAME)
    tilt_motor.setVelocity(config.TILT_MOTOR_VELOCITY)

    light_left = robot.getDevice("light_left")
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

        # --- START SWITCH LOGIC ---
        key = keyboard.getKey()
        current_sw_x = selector_sensor.getValue()

        if key == ord('1'):
            target_x = MODE_POSITIONS[0]
            print('Current mode: Open')
        elif key == ord('2'):
            target_x = MODE_POSITIONS[1]
            print('Current mode: Hybrid')
        elif key == ord('3'):
            target_x = MODE_POSITIONS[2]
            print('Current mode: Closed')
        else:
            target_x = min(MODE_POSITIONS, key=lambda x: abs(x - current_sw_x))

        # This prevents the "falling" by actively holding the motor at the target
        selector_motor.setPosition(target_x)
        # --- END SWITCH LOGIC ---

        ll = float(light_left.getValue())
        lr = float(light_right.getValue())

        diff = ll - lr
        side = classify_direction(ll, lr)

        """
        ------------------------------------------SWITCH LOGIC------------------------------------------
        Movement type that is executed is determined by mode value, contained in the target_x variable
        ------------------------------------------------------------------------------------------------
        """

        if (target_x == MODE_POSITIONS[0]):
            open_loop_logic(pattern_index, elapsed, timestep, pan_motor, tilt_motor, t)
        elif (target_x == MODE_POSITIONS[1]):
            if (ll <= float(0.050) and lr <= float(0.050)):
                open_loop_logic(pattern_index, elapsed, timestep, pan_motor, tilt_motor, t)
            else:
                update_pan_closed_loop(pan_motor, ll, lr)
                update_tilt_closed_loop(tilt_motor, ll, lr)
        elif (target_x == MODE_POSITIONS[2]):
            update_pan_closed_loop(pan_motor, ll, lr)
            update_tilt_closed_loop(tilt_motor, ll, lr)
        else:
            target_x = MODE_POSITIONS[0]

        """
        ------------------------------------------SANITY CHECKING-----------------------------------
        """

        if step_count % PRINT_EVERY_N_STEPS == 0:
            print(f"L:{ll:.3f} R:{lr:.3f} diff:{diff:.3f} -> {side} | Mode X: {target_x}")

"""
---------------------------------RUNNING THE MAIN FUNCTION---------------------------------
"""

if __name__ == "__main__":
    main()
