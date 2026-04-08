import unittest
from unittest.mock import MagicMock
import title_open_loop
from title_open_loop import update_open_loop_tilt

# Configurations for testing
TEST_MIN = -1.2
TEST_MAX = 1.2
TEST_STEP = 0.02

class TestUpdateOpenLoopTilt(unittest.TestCase):

# ----------------------------------------------------------------SETUP FUNCTIONS----------------------------------------------------------------
    def setUpTilt(self): # Set the tilt direction to normal at the beginning each test
        title_open_loop.tilt_dir = 0

    def setUpMotor(self, position):
        mock_motor = MagicMock()
        mock_motor.getTargetPosition.return_value = position
        return mock_motor

# ----------------------------------------------------------------UNIT TEST FUNCTIONS----------------------------------------------------------------
    def test_handlingNAN(self):
        motor = self.setUpMotor(float("nan"))
        title_open_loop.tilt_dir = 0
        update_open_loop_tilt(motor)

        # Expected = 0 + STEP, 
        expected = max(TEST_MIN, min(TEST_MAX, 0.0 + TEST_STEP))
        motor.setPosition.assert_called_once_with(expected)
    
    def test_centerToRight(self):
        center = float(0)
        motor = self.setUpMotor(center)
        title_open_loop.tilt_dir = 0
        update_open_loop_tilt(motor)
        motor.setPosition.assert_called_once_with(center + TEST_STEP)
    
    def test_centertitle_open_loopeft(self):
        center = float(0)
        motor = self.setUpMotor(center)
        title_open_loop.tilt_dir = 1
        update_open_loop_tilt(motor)
        motor.setPosition.assert_called_once_with(center - TEST_STEP)
    
    def test_righttitle_open_loopeft(self):
        motor = self.setUpMotor(TEST_MAX)
        title_open_loop.tilt_dir = 0 # Start right
        update_open_loop_tilt(motor)
        self.assertEqual(title_open_loop.tilt_dir, 1) # End left

    def test_leftToRight(self):
        motor = self.setUpMotor(TEST_MIN)
        title_open_loop.tilt_dir = 1 # Start left
        update_open_loop_tilt(motor)
        self.assertEqual(title_open_loop.tilt_dir, 0) # End right
    
    def test_maxClamp(self):
        motor = self.setUpMotor(TEST_MAX)
        title_open_loop.tilt_dir = 0
        update_open_loop_tilt(motor)
        called_pos = motor.setPosition.call_args[0][0]
        self.assertLessEqual(called_pos, TEST_MAX)

    def test_minClamp(self):
        motor = self.setUpMotor(TEST_MIN)
        title_open_loop.tilt_dir = 1
        update_open_loop_tilt(motor)
        called_pos = motor.setPosition.call_args[0][0]
        self.assertGreaterEqual(called_pos, TEST_MIN)
    
    def test_fullCycle(self):
        position = [TEST_MIN]  # Used for assertations
 
        def get():
            return position[0]
 
        def set(pos):
            position[0] = pos
 
        # Set up Motor
        motor = MagicMock()
        motor.getTargetPosition.side_effect = get
        motor.setPosition.side_effect = set
        title_open_loop.tilt_dir = 0
        steps = int((TEST_MAX - TEST_MIN) / TEST_STEP) * 4   # 2 cycles
        for _ in range(steps):
            update_open_loop_tilt(motor)
            self.assertGreaterEqual(position[0], TEST_MIN)
            self.assertLessEqual(position[0], TEST_MAX)
    
    def test_returnToStart(self): # Direction variable will be 0 again after a full cycle
        position = [TEST_MIN]
 
        def get():
            return position[0]
 
        def set(pos):
            position[0] = pos
 
        motor = MagicMock()
        motor.getTargetPosition.side_effect = get
        motor.setPosition.side_effect = set
        title_open_loop.tilt_dir = 0
        steps = int((TEST_MAX - TEST_MIN) / TEST_STEP) * 2 + 2
        for _ in range(steps):
            update_open_loop_tilt(motor)
 
        self.assertEqual(title_open_loop.tilt_dir, 0)


if __name__ == "__main__":
    unittest.main()