# config.py
# Central place for device names and tunables

# Device names (must match Webots node names)
PAN_MOTOR_NAME = "pan_motor"
LIGHT_LEFT_NAME = "light_left"
LIGHT_RIGHT_NAME = "light_right"

# Control tuning
PAN_MOTOR_VELOCITY = 1.5

# Closed-loop behavior
DEADBAND = 0.02          # within this diff -> stop
STEP = 0.02              # radians per step (position increment)
PAN_MIN = -3.14
PAN_MAX = 3.14
