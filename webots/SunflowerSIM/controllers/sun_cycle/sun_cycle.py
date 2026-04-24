# sun_cycle.py
from controller import Supervisor
import sys
from pathlib import Path
from datetime import datetime, timezone

from solar_math import solar_direction_from_latlon, elevation_deg_from_direction

# --- Make tracker package importable (controllers/tracker_main/tracker/...) ---
HERE = Path(__file__).resolve()
CONTROLLERS_DIR = HERE.parents[1]            # .../controllers
TRACKER_MAIN_DIR = CONTROLLERS_DIR / "tracker_main"

if str(TRACKER_MAIN_DIR) not in sys.path:
    sys.path.insert(0, str(TRACKER_MAIN_DIR))

# Now this works because tracker_main is on sys.path
from tracker.location_store import LocationStore  # noqa: E402

TRACKER_DIR = TRACKER_MAIN_DIR / "tracker"
store = LocationStore(path=str(TRACKER_DIR / "location.json"))

# --- Webots setup ---
robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

sun_node = robot.getFromDef("SUN")  # DirectionalLight must be DEF SUN
if not sun_node:
    print("WARNING: Could not find DEF SUN in the world.")

# Speed: how long for a full sunrise->sunset arc (seconds)
SUN_CYCLE_SECONDS = 10.0

# Use today's day-of-year for declination
DAY_OF_YEAR = datetime.now(timezone.utc).timetuple().tm_yday

# Location store reads tracker/location.json
store = LocationStore(path=str(TRACKER_DIR / "location.json"))


t = 0.0
last_loc = None
step_count = 0
max_elev = -999.0

while robot.step(timestep) != -1:
    t += timestep / 1000.0

    # Read location each step (LocationStore caches unless file changed)
    loc = store.load()
    if last_loc != loc:
        print(f"[sun_cycle] Using location lat={loc.lat:.6f}, lon={loc.lon:.6f} (reset max elevation)")
        last_loc = loc
        t = 0.0
        step_count = 0
        max_elev = -999.0

    frac = (t % SUN_CYCLE_SECONDS) / SUN_CYCLE_SECONDS

    if sun_node:
        direction = solar_direction_from_latlon(loc.lat, loc.lon, frac, DAY_OF_YEAR)

        if direction is None:
            sun_node.getField("on").setSFBool(False)
        else:
            sun_node.getField("on").setSFBool(True)
            sun_node.getField("direction").setSFVec3f(direction)

            # Track elevation only when sun is up
            step_count += 1
            elev = elevation_deg_from_direction(direction)
            max_elev = max(max_elev, elev)

            if step_count % 20 == 0:
                print(f"[sun_cycle] lat={loc.lat:.4f} lon={loc.lon:.4f} elev={elev:.1f}° max={max_elev:.1f}°")