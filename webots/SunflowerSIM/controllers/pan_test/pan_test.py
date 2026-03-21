# Fares logging update
from controller import Robot
import math
import csv
import os
from datetime import datetime

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

# ---------------- LOGGING SETUP ----------------

# Configurable log folder and file name
LOG_FOLDER = "logs"
LOG_FILE_NAME = f"sunflower_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Build full log path inside this controller folder
controller_directory = os.path.dirname(os.path.abspath(__file__))
log_directory = os.path.join(controller_directory, LOG_FOLDER)
os.makedirs(log_directory, exist_ok=True)

log_file_path = os.path.join(log_directory, LOG_FILE_NAME)

# Open CSV file and write header row
log_file = open(log_file_path, mode="w", newline="")
csv_writer = csv.writer(log_file)

csv_writer.writerow([
    "timestamp_seconds",
    "pan_angle",
    "tilt_angle",
    "left_sensor",
    "right_sensor"
])

print(f"[LOGGING] Writing to: {log_file_path}")

t = 0.0

while robot.step(timestep) != -1:
    t += timestep / 1000.0

    # Pan: +/- 1 rad, Tilt: +/- 0.6 rad
    pan.setPosition(1.0 * math.sin(t))
    tilt.setPosition(0.6 * math.sin(0.7 * t))

    left_value = light_left.getValue()
    right_value = light_right.getValue()
    pan_angle = pan_sensor.getValue()
    tilt_angle = tilt_sensor.getValue()

    print("L:", left_value, "R:", right_value)

    csv_writer.writerow([
        round(t, 3),
        round(pan_angle, 4),
        round(tilt_angle, 4),
        round(left_value, 4),
        round(right_value, 4)
    ])

log_file.close()