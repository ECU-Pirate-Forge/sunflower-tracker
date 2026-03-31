# sun_cycle.py
from controller import Supervisor
import math

robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

sun_node = robot.getFromDef("SUN")  # your DirectionalLight must be DEF SUN
SUN_CYCLE_SECONDS = 10.0

def get_sun_direction(t: float):
    angle = (t / SUN_CYCLE_SECONDS) * math.pi
    x = math.cos(angle)
    y = -abs(math.sin(angle))      # keeps sun above “horizon”
    z = math.sin(angle) * 0.3
    return [x, y, z]

t = 0.0
warned = False

while robot.step(timestep) != -1:
    t += timestep / 1000.0
    if sun_node:
        sun_node.getField("direction").setSFVec3f(get_sun_direction(t))
    elif not warned:
        print("WARNING: Could not find DEF SUN in the world.")
        warned = True