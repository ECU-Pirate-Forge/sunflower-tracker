from controller import Robot
import math

robot = Robot()
timestep = int(robot.getBasicTimeStep())

pan = robot.getDevice("pan_motor")
tilt = robot.getDevice("tilt_motor")

pan_sensor = robot.getDevice("pan_sensor")
tilt_sensor = robot.getDevice("tilt_sensor")
pan_sensor.enable(timestep)
tilt_sensor.enable(timestep)
light_left = robot.getDevice("light_left")
light_right = robot.getDevice("light_right")
light_left.enable(timestep)
light_right.enable(timestep)


# Make sure motors are allowed to move at a visible speed
pan.setVelocity(1.5)
tilt.setVelocity(1.5)

t = 0.0
while robot.step(timestep) != -1:
    t += timestep / 1000.0

    # Pan: +/- 1 rad, Tilt: +/- 0.6 rad
    pan.setPosition(1.0 * math.sin(t))
    tilt.setPosition(0.6 * math.sin(0.7 * t))
    print("L:", light_left.getValue(), "R:", light_right.getValue())
    

