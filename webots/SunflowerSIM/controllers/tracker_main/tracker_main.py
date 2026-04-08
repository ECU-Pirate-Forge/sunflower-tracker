# tracker_main.py
# Main robot controller that wires modules together (closed-loop pan, etc.)
# Prints L/R + diff and a direction label so you can verify behavior.

from controller import Robot
from tracker import config
from tracker.sensors import init_light_sensors, read_light_sensors
from tracker.pan_closed_loop import update_pan_closed_loop
from tracker.title_open_loop import update_open_loop_tilt
from tracker.tilt_closed_loop import update_tilt_closed_loop


def direction_label(diff: float) -> str:
    # Mirrors acceptance criteria meaning
    if abs(diff) <= config.DEADBAND:
        return "CENTER"
    return "LEFT" if diff > 0 else "RIGHT"


def main():
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    # Devices
    pan_motor = robot.getDevice(config.PAN_MOTOR_NAME)
    pan_motor.setVelocity(config.PAN_MOTOR_VELOCITY)
    tilt_motor = robot.getDevice(config.TILT_MOTOR_NAME)
    tilt_motor.setVelocity(config.TILT_MOTOR_VELOCITY)

    tilt_motor = robot.getDevice(config.TILT_MOTOR_NAME)
    tilt_motor.setVelocity(config.TILT_MOTOR_VELOCITY)

    # Light sensors
    light_left, light_right = init_light_sensors(robot, timestep)

    # Print throttle
    step_count = 0
    PRINT_EVERY_N_STEPS = 10  # adjust if you want more/less output

    while robot.step(timestep) != -1:
        step_count += 1

        l, r = read_light_sensors(light_left, light_right)
        diff = l - r

        # Closed-loop pan update
        update_pan_closed_loop(pan_motor, l, r)
        update_tilt_closed_loop(tilt_motor, l, r)

        # Open-loop tilt update
        """
        To prevent any clashing with closed loop tilt, I am commenting out open-loop tilt until the functionality
        for switching between modes is added.
        update_open_loop_tilt(tilt_motor)
        """

        # Debug print (throttled)
        if step_count % PRINT_EVERY_N_STEPS == 0:
            side = direction_label(diff)
            print(f"L:{l:.3f} R:{r:.3f} diff:{diff:.3f} -> {side}")


if __name__ == "__main__":
    main()
