# title_open_loop.py
# Allows for the sunflower tracker to tilt in a direction over a set interval,
# independent from the light sensors.

from . import config

tilt_dir = 0 # 0 tilts right, 1 tilts left

def update_open_loop_tilt(tilt_motor):
    global tilt_dir # Global delcaration ensures value is accessible and isn't reset on function call 

    # Get the target position and handle any possible errors of NaN being returned
    current_pos = tilt_motor.getTargetPosition()
    if current_pos != current_pos:
        current_pos = 0.0

    # Clamps to prevent the motor from going past the maximum amount, then change directions
    if current_pos >= config.TILT_MAX:
        tilt_dir = 1
    elif current_pos <= config.TILT_MIN:
        tilt_dir = 0
    
    # Handles performing object movement, in the direct indicated by tilt_dir       
    if tilt_dir == 0:
        target_pos = (current_pos + config.STEP)
    else:
        target_pos = (current_pos - config.STEP)
    
    # Clamp the position at the motor's limits to prevent going over them     
    target_pos = max(config.TILT_MIN, min(config.TILT_MAX, target_pos))

    # Set the motor's position to the calculated carget position
    tilt_motor.setPosition(target_pos)
    