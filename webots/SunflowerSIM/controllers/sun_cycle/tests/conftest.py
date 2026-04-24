import sys
from pathlib import Path

# Add the sun_cycle controller folder to sys.path so tests can import solar_math.py
SUN_CYCLE_DIR = Path(__file__).resolve().parents[1]  # .../controllers/sun_cycle
sys.path.insert(0, str(SUN_CYCLE_DIR))