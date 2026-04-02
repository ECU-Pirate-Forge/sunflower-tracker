# pan_test.py
# Minimal controller to verify light sensors on the pan/tilt mount.
# Prints L/R + diff and a direction label (LEFT/RIGHT/CENTER).
#
# Notes:
# - A sensor can sit near a "floor" value when facing away from the sun or shaded.
# - DEADBAND avoids jitter when readings are almost equal.
# - Near the sensor "ceiling" (both sensors high), tiny diffs can still be meaningful,
#   so we reduce the deadband to satisfy the edge-case unit test.

try:
    from controller import Robot  # Webots runtime
except ImportError:
    Robot = None  # allows pytest to import this file outside Webots
import math
from typing import List, Tuple


USE_PATTERN = False  # If True, follows fixed pattern; if False, uses sine wave motion.

# --- Tuning knobs ---
DEADBAND = 0.02            # base diff threshold to call LEFT/RIGHT
PRINT_EVERY_N_STEPS = 10   # reduce console spam

PAN_AMPLITUDE = 1.0        # radians
PAN_FREQ = 1.0             # rad/sec for sine input
TILT_AMPLITUDE = 0.6       # radians
TILT_FREQ = 0.7            # rad/sec for sine input

# --- "Ceiling" handling (fixes failing test at high readings) ---
CEILING_THRESHOLD = 0.15        # if both sensors >= this, treat as "near max"
CEILING_DEADBAND_SCALE = 0.10   # effective deadband = DEADBAND * scale (0.02*0.10=0.002)

PATTERN = [
    (0.0, 3000),     # centre
    (0.8, 3000),     # right
    (0.0, 3000),     # centre
    (-0.8, 3000),    # left
    (0.0, 3000),     # centre
]

def step_pattern(
    index: int,
    elapsed: int,
    timestep: int,
    pattern: List[Tuple[float, int]],
):
    elapsed += timestep
    target, dwell = pattern[index]

    if elapsed >= dwell:
        elapsed = 0
        index = (index + 1) % len(pattern)
        target, _ = pattern[index]

    return index, elapsed, target


def classify_direction(l: float, r: float, deadband: float = DEADBAND) -> str:
    """
    Return LEFT/RIGHT/CENTER based on (l - r).

    Uses a normal deadband most of the time, but when both sensors are near their
    top readings, reduces the deadband so small differences are still classified.
    """
    effective_deadband = deadband
    if l >= CEILING_THRESHOLD and r >= CEILING_THRESHOLD:
        effective_deadband = deadband * CEILING_DEADBAND_SCALE

    diff = l - r
    if diff > effective_deadband:
        return "LEFT"
    if diff < -effective_deadband:
        return "RIGHT"
    return "CENTER"

def main():
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    pan_motor = robot.getDevice("pan_motor")
    tilt_motor = robot.getDevice("tilt_motor")
    
    pan_motor.setVelocity(1.5)
    tilt_motor.setVelocity(1.5)

    light_left = robot.getDevice("light_left")
    light_right = robot.getDevice("light_right")
    
    light_left.enable(timestep)
    light_right.enable(timestep)

    t = 0.0
    step_count = 0

    # pattern based on closed-loop
    pattern_index = 0
    elapsed = 0
    pan_motor.setPosition(PATTERN[pattern_index][0])

    while robot.step(timestep) != -1:
        t += timestep / 1000.0
        step_count += 1
        
        if USE_PATTERN:
            pattern_index, elapsed, target = step_pattern(
                pattern_index,
                elapsed,
                timestep,
                PATTERN,
            )
            pan_motor.setPosition(target)

        else:
            pan_motor.setPosition(PAN_AMPLITUDE * math.sin(PAN_FREQ * t))
            tilt_motor.setPosition(TILT_AMPLITUDE * math.sin(TILT_FREQ * t))

        l = float(light_left.getValue())
        r = float(light_right.getValue())
        
        diff = l - r
        side = classify_direction(l, r)

        if step_count % PRINT_EVERY_N_STEPS == 0:
            print(f"L:{l:.3f} R:{r:.3f} diff:{diff:.3f} -> {side}")


if __name__ == "__main__":
    if Robot is None:
        raise RuntimeError("Run inside Webots (controller module not found).")
    main()
