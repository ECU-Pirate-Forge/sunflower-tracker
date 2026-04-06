# tilt_closed_loop.py
from . import config

_last_avg = None
_direction = 1  # +1 = tilt up, -1 = tilt down

def update_tilt_closed_loop(tilt_motor, left_val: float, right_val: float):
    """
    Acceptance criteria:
      - Tilt moves up/down to maximize average brightness
      - Stops when centered (no improvement within TILT_DEADBAND)
      - Independent of pan (uses average only, not diff)
    """
    global _last_avg, _direction

    avg = (left_val + right_val) / 2.0

    if _last_avg is None:
        _last_avg = avg
        return

    improvement = avg - _last_avg
    _last_avg = avg

    if abs(improvement) <= config.TILT_DEADBAND:
        return

    if improvement < 0:
        _direction *= -1

    current = tilt_motor.getTargetPosition()
    if current != current:  # NaN safety
        current = 0.0

    target = current + _direction * config.TILT_STEP

    if target > config.TILT_MAX:
        target = config.TILT_MAX
    if target < config.TILT_MIN:
        target = config.TILT_MIN

    tilt_motor.setPosition(target)

