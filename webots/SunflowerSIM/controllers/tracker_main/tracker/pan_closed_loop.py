# pan_closed_loop.py
from . import config


def update_pan_closed_loop(pan_motor, left_val: float, right_val: float):
    """
    Acceptance criteria:
      - Pan rotates left when left > right
      - Pan rotates right when right > left
      - Stops when within threshold (deadband)
      - No excessive jitter (deadband helps)
    """

    diff = left_val - right_val

    # Stop zone (no jitter)
    if abs(diff) <= config.DEADBAND:
        # Hold current position (no change)
        return

    # Determine direction and step
    current = pan_motor.getTargetPosition()
    if current != current:  # NaN safety (sometimes Webots returns NaN initially)
        current = 0.0

    if diff > 0:
        # left brighter -> rotate left (positive direction)
        target = current + config.STEP
    else:
        # right brighter -> rotate right (negative direction)
        target = current - config.STEP

    # Clamp
    if target > config.PAN_MAX:
        target = config.PAN_MAX
    if target < config.PAN_MIN:
        target = config.PAN_MIN

    pan_motor.setPosition(target)