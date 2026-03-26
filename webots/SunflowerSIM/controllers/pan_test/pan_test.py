from controller import Supervisor
import math

robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

# grabbing the sun object from the scene so we can move it
# this is the light source that will move across the sky
sun_node = robot.getFromDef("SUN")

# change this number to control how fast the sun moves
# 60.0 means the sun completes a full arc in 60 seconds (sped up)
# if you want real time you'd set this to 86400.0 (seconds in a day)
SUN_CYCLE_SECONDS = 60.0

# this function figures out where the sun should be at any given time
# it traces an arc from one side of the sky to the other like a real sunrise/sunset
# speed depends on SUN_CYCLE_SECONDS above
def get_sun_direction(t):
    angle = (t / SUN_CYCLE_SECONDS) * math.pi
    x = math.cos(angle)
    y = -abs(math.sin(angle))  # keeps the sun above the horizon
    z = math.sin(angle) * 0.3  # slight drift so it doesnt just go straight across
    return [x, y, z]

# main loop - runs every timestep and updates the sun position
t = 0.0
while robot.step(timestep) != -1:
    t += timestep / 1000.0

    # move the sun to its new position each step
    sun_dir = get_sun_direction(t)
    if sun_node:
        sun_node.getField("direction").setSFVec3f(sun_dir)

if __name__ == "__main__":
    if Robot is None:
        raise RuntimeError("This controller must be run inside Webots (controller module not found).")
    main()