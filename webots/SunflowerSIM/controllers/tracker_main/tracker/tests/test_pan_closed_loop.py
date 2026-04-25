# tracker/tests/test_pan_closed_loop.py
from tracker import config
from tracker.pan_closed_loop import update_pan_closed_loop


class FakeMotor:
    """Minimal stub motor for unit testing update_pan_closed_loop()."""
    def __init__(self, target_position=0.0):
        self._target_position = target_position
        self.last_set_position = None

    def getTargetPosition(self):
        return self._target_position

    def setPosition(self, target):
        self.last_set_position = target
        # mimic Webots behavior: after setting, target position becomes new target
        self._target_position = target


def test_stops_within_deadband_no_move():
    m = FakeMotor(target_position=0.0)

    # diff = 0 -> inside deadband
    update_pan_closed_loop(m, left_val=1.0, right_val=1.0)

    assert m.last_set_position is None


def test_stops_exactly_at_deadband_no_move():
    m = FakeMotor(target_position=0.0)

    # diff exactly == DEADBAND should also stop (<=)
    update_pan_closed_loop(m, left_val=1.0 + config.DEADBAND, right_val=1.0)

    assert m.last_set_position is None


def test_rotates_left_when_left_greater():
    m = FakeMotor(target_position=0.0)

    update_pan_closed_loop(m, left_val=1.0, right_val=0.0)

    assert m.last_set_position == 0.0 + config.STEP


def test_rotates_right_when_right_greater():
    m = FakeMotor(target_position=0.0)

    update_pan_closed_loop(m, left_val=0.0, right_val=1.0)

    assert m.last_set_position == 0.0 - config.STEP


def test_nan_target_position_defaults_to_zero():
    m = FakeMotor(target_position=float("nan"))

    update_pan_closed_loop(m, left_val=1.0, right_val=0.0)

    # should treat NaN as 0.0 then move left by STEP
    assert m.last_set_position == 0.0 + config.STEP


def test_clamps_at_pan_max():
    m = FakeMotor(target_position=config.PAN_MAX)

    update_pan_closed_loop(m, left_val=1.0, right_val=0.0)

    assert m.last_set_position == config.PAN_MAX


def test_clamps_at_pan_min():
    m = FakeMotor(target_position=config.PAN_MIN)

    update_pan_closed_loop(m, left_val=0.0, right_val=1.0)

    assert m.last_set_position == config.PAN_MIN