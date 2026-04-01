from controller import Robot

def main() -> None:
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    # Motor control horizontal movement
    # No sensors being used
    pan_motor = robot.getDevice("pan_motor")
    pan_motor.setVelocity(2.0)

    # (target position, time in ms to hold that position)
    # does not depend on sensors -> fixed pattern
    # this can be esaily changed if needed
    pattern = [
        (0.0, 3000),     # centre
        (0.8, 3000),     # right
        (0.0, 3000),     # centre
        (-0.8, 3000),    # left
        (0.0, 3000),     # centre
    ]

    index = 0      # tracks current position
    elapsed = 0    # tracks elapsed time at current position (ms)

    pan_motor.setPosition(pattern[index][0])

    while robot.step(timestep) != -1:
        elapsed += timestep

        target, dwell = pattern[index]

        if elapsed >= dwell:
            elapsed = 0
            index = (index + 1) % len(pattern)
            # movement is based on timme rather than sensors
            pan_motor.setPosition(pattern[index][0])


if __name__ == "__main__":
    main()