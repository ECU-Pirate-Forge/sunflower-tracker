# Light Sensor Setup (Pan/Tilt Mount)

## Goal
Add light sensors to the pan/tilt mount so the controller can detect **light intensity + direction**.

## Acceptance Criteria Checklist
1. ✅ At least one LightSensor attached to the top of the mount  
2. ✅ Sensor oriented upward & outward toward the sky  
3. ✅ Sensor returns varying values based on light source position  
4. ✅ Readings accessible by name from a Python controller  
5. ✅ Sensor behavior documented (value range)

---

## What we built (Webots)
### Sensor nodes
- `light_left` (LightSensor)
- `light_right` (LightSensor)

### Where they live in the Scene Tree
Robot `pan_tilt` → `PAN_JOINT` → `endPoint Solid` → `TILT_JOINT` → `endPoint Solid` (`TILT_HEAD`) → children  
- `LightSensor "light_left"`
- `LightSensor "light_right"`

### Orientation
Sensors are positioned symmetrically on the tilt head and rotated so they face upward/outward.

---

## How to read values (Python controller)
Controller file:
- `webots/SunflowerSIM/controllers/pan_test/pan_test.py`

Sensor access by name:
- `robot.getDevice("light_left")`
- `robot.getDevice("light_right")`

---

## Observed value range (Acceptance Criteria #5)
Controller files for light reading of the value range:

- `webots/SunflowerSIM/controllers/light_read/light_read.py`

Run the controller for ~30 seconds while pan/tilt moves.
 - Record the min/max seen during the run.
 - `light_left':  min = 0.050, max = 0.164`
 - `light_right': min = 0.050, max = 0.161`


**Notes**
- Values change based on sun direction and whether a sensor is facing the light.
- The LightSensor `lookupTable` affects scaling and min/max.

---

## Evidence (screenshots)
- Scene Tree showing sensors: `Images/scene-tree-sensors.png`
- Sensor placement/orientation: `Images/sensor-placement.png`
- Console output sample:
    - `Images/console-value-output.png`
    - `Images/console-range-output.png`
