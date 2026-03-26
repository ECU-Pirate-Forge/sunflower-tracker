from controller import Robot
import math

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Motors still run so sensors see changing angles
pan_motor = robot.getDevice("pan_motor")
tilt_motor = robot.getDevice("tilt_motor")
pan_motor.setVelocity(1.5)
tilt_motor.setVelocity(1.5)

PAN_AMPLITUDE = 1.0
PAN_FREQ = 1.0
TILT_AMPLITUDE = 0.6
TILT_FREQ = 0.7

light_left = robot.getDevice("light_left")
light_right = robot.getDevice("light_right")
light_left.enable(timestep)
light_right.enable(timestep)

l_min, l_max = float("inf"), float("-inf")
r_min, r_max = float("inf"), float("-inf")

t = 0.0
step_count = 0
PRINT_EVERY_N_STEPS = 10

while robot.step(timestep) != -1:
    t += timestep / 1000.0
    step_count += 1

    pan_motor.setPosition(PAN_AMPLITUDE * math.sin(PAN_FREQ * t))
    tilt_motor.setPosition(TILT_AMPLITUDE * math.sin(TILT_FREQ * t))

    l = float(light_left.getValue())
    r = float(light_right.getValue())

    l_min = min(l_min, l); l_max = max(l_max, l)
    r_min = min(r_min, r); r_max = max(r_max, r)

    if step_count % PRINT_EVERY_N_STEPS == 0:
        print(
            f"L:{l:.3f} (min {l_min:.3f}, max {l_max:.3f}) | "
            f"R:{r:.3f} (min {r_min:.3f}, max {r_max:.3f})"
        )