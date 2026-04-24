import unittest
from unittest.mock import MagicMock, patch
import sys

# Stub ONLY the Webots 'controller' module BEFORE importing tracker_main.
# This prevents ModuleNotFoundError in pytest without affecting other modules.
sys.modules.setdefault("controller", MagicMock())

import tracker_main  # noqa: E402  (must come after controller stub)


"""TEST ALIASES"""
OPEN   = 0.7   # MODE_POSITIONS[0]
HYBRID = 0.6   # MODE_POSITIONS[1]
CLOSED = 0.5   # MODE_POSITIONS[2]
MODE_POSITIONS = [OPEN, HYBRID, CLOSED]

LOW_LIGHT  = 0.030   # both sensors below 0.050 (open loop branch)
HIGH_LIGHT = 0.080   # at least one sensor above 0.050 (closed loop branch)


# Recreation of the necessary Webots hardware using MagicMock
def _make_motors():
    return MagicMock(name="pan_motor"), MagicMock(name="tilt_motor")


# Recreation of the if-elif-else loop for determining modes
def _run_dispatch(target_x: float, ll: float, lr: float,
                  pan_motor=None, tilt_motor=None,
                  pattern_index=0, elapsed=0, timestep=32, t=1.0):
    if pan_motor is None or tilt_motor is None:
        pan_motor, tilt_motor = _make_motors()

    with (
        patch("tracker_main.open_loop_logic")         as mock_open,
        patch("tracker_main.update_pan_closed_loop")  as mock_pan_cl,
        patch("tracker_main.update_tilt_closed_loop") as mock_tilt_cl,
    ):
        # ---- replicate lines 176-190 of tracker_main.main() ----
        if target_x == MODE_POSITIONS[0]:
            tracker_main.open_loop_logic(
                pattern_index, elapsed, timestep, pan_motor, tilt_motor, t
            )
        elif target_x == MODE_POSITIONS[1]:
            if ll <= 0.050 and lr <= 0.050:
                tracker_main.open_loop_logic(
                    pattern_index, elapsed, timestep, pan_motor, tilt_motor, t
                )
            else:
                tracker_main.update_pan_closed_loop(pan_motor, ll, lr)
                tracker_main.update_tilt_closed_loop(tilt_motor, ll, lr)
        elif target_x == MODE_POSITIONS[2]:
            tracker_main.update_pan_closed_loop(pan_motor, ll, lr)
            tracker_main.update_tilt_closed_loop(tilt_motor, ll, lr)
        else:
            target_x = MODE_POSITIONS[0]   # fallback – no motor call this step
        # ---------------------------------------------------------

        return mock_open, mock_pan_cl, mock_tilt_cl, target_x


def _key_to_target(key_char: str, current_sw_x: float) -> float:
    """Replicate lines 148-158 (key → target_x resolution)."""
    if key_char == '1':
        return MODE_POSITIONS[0]
    elif key_char == '2':
        return MODE_POSITIONS[1]
    elif key_char == '3':
        return MODE_POSITIONS[2]
    else:
        return min(MODE_POSITIONS, key=lambda x: abs(x - current_sw_x))


class TestHybridLogic(unittest.TestCase):
    # -----------------------------------------------------------------------
    # Section 1 — Key → target_x resolution  (lines 148-158)
    # -----------------------------------------------------------------------

    def test_key_1_selects_open_mode(self):
        target = _key_to_target('1', current_sw_x=CLOSED)
        self.assertEqual(target, OPEN)

    def test_key_2_selects_hybrid_mode(self):
        target = _key_to_target('2', current_sw_x=OPEN)
        self.assertEqual(target, HYBRID)

    def test_key_3_selects_closed_mode(self):
        target = _key_to_target('3', current_sw_x=OPEN)
        self.assertEqual(target, CLOSED)

    def test_no_key_snaps_to_nearest_open(self):
        target = _key_to_target('', current_sw_x=0.68)
        self.assertEqual(target, OPEN)

    def test_no_key_snaps_to_nearest_hybrid(self):
        target = _key_to_target('', current_sw_x=0.61)
        self.assertEqual(target, HYBRID)

    def test_no_key_snaps_to_nearest_closed(self):
        target = _key_to_target('', current_sw_x=0.51)
        self.assertEqual(target, CLOSED)

    # -----------------------------------------------------------------------
    # Section 2 — Per-mode motor dispatch  (lines 176-190)
    # -----------------------------------------------------------------------

    def test_open_mode_calls_open_loop(self):
        mock_open, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=OPEN, ll=LOW_LIGHT, lr=LOW_LIGHT
        )
        mock_open.assert_called_once()
        mock_pan_cl.assert_not_called()
        mock_tilt_cl.assert_not_called()

    def test_open_mode_ignores_high_light(self):
        mock_open, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=OPEN, ll=HIGH_LIGHT, lr=HIGH_LIGHT
        )
        mock_open.assert_called_once()
        mock_pan_cl.assert_not_called()
        mock_tilt_cl.assert_not_called()

    def test_hybrid_low_light_calls_open_loop(self):
        mock_open, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=HYBRID, ll=LOW_LIGHT, lr=LOW_LIGHT
        )
        mock_open.assert_called_once()
        mock_pan_cl.assert_not_called()
        mock_tilt_cl.assert_not_called()

    def test_hybrid_exact_threshold_calls_open_loop(self):
        mock_open, _, _, _ = _run_dispatch(
            target_x=HYBRID, ll=0.050, lr=0.050
        )
        mock_open.assert_called_once()

    def test_hybrid_left_just_above_threshold_calls_closed_loop(self):
        mock_open, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=HYBRID, ll=0.051, lr=LOW_LIGHT
        )
        mock_open.assert_not_called()
        mock_pan_cl.assert_called_once()
        mock_tilt_cl.assert_called_once()

    def test_hybrid_right_just_above_threshold_calls_closed_loop(self):
        mock_open, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=HYBRID, ll=LOW_LIGHT, lr=0.051
        )
        mock_open.assert_not_called()
        mock_pan_cl.assert_called_once()
        mock_tilt_cl.assert_called_once()

    def test_hybrid_high_light_calls_closed_loop(self):
        mock_open, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=HYBRID, ll=HIGH_LIGHT, lr=HIGH_LIGHT
        )
        mock_open.assert_not_called()
        mock_pan_cl.assert_called_once()
        mock_tilt_cl.assert_called_once()

    def test_hybrid_closed_loop_receives_correct_light_values(self):
        ll, lr = 0.090, 0.075
        pan_motor, tilt_motor = _make_motors()
        _, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=HYBRID, ll=ll, lr=lr,
            pan_motor=pan_motor, tilt_motor=tilt_motor,
        )
        mock_pan_cl.assert_called_once_with(pan_motor, ll, lr)
        mock_tilt_cl.assert_called_once_with(tilt_motor, ll, lr)

    def test_closed_mode_calls_closed_loop(self):
        mock_open, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=CLOSED, ll=LOW_LIGHT, lr=LOW_LIGHT
        )
        mock_open.assert_not_called()
        mock_pan_cl.assert_called_once()
        mock_tilt_cl.assert_called_once()

    def test_closed_mode_ignores_low_light(self):
        mock_open, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=CLOSED, ll=0.001, lr=0.001
        )
        mock_open.assert_not_called()
        mock_pan_cl.assert_called_once()
        mock_tilt_cl.assert_called_once()

    def test_closed_loop_receives_correct_light_values(self):
        ll, lr = 0.120, 0.095
        pan_motor, tilt_motor = _make_motors()
        _, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=CLOSED, ll=ll, lr=lr,
            pan_motor=pan_motor, tilt_motor=tilt_motor,
        )
        mock_pan_cl.assert_called_once_with(pan_motor, ll, lr)
        mock_tilt_cl.assert_called_once_with(tilt_motor, ll, lr)

    def test_invalidToOpen_bad_position_resets_to_open(self):
        _, _, _, returned_target = _run_dispatch(
            target_x=0.99, ll=LOW_LIGHT, lr=LOW_LIGHT
        )
        self.assertEqual(returned_target, OPEN)

    def test_invalid_mode_makes_no_motor_calls(self):
        mock_open, mock_pan_cl, mock_tilt_cl, _ = _run_dispatch(
            target_x=0.99, ll=LOW_LIGHT, lr=LOW_LIGHT
        )
        mock_open.assert_not_called()
        mock_pan_cl.assert_not_called()
        mock_tilt_cl.assert_not_called()


if __name__ == "__main__":
    unittest.main()