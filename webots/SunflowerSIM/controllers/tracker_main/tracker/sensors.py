# sensors.py
from . import config


def init_light_sensors(robot, timestep):
    left = robot.getDevice(config.LIGHT_LEFT_NAME)
    right = robot.getDevice(config.LIGHT_RIGHT_NAME)
    left.enable(timestep)
    right.enable(timestep)
    return left, right


def read_light_sensors(left, right):
    return float(left.getValue()), float(right.getValue())