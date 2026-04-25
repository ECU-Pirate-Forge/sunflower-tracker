import math
from pathlib import Path
from solar_math import solar_direction_from_latlon, elevation_deg_from_direction  # noqa: E402

# Make solar_math importable when running pytest from anywhere
SUN_CYCLE_DIR = Path(__file__).resolve().parents[1]


DAY = 172  # fixed day-of-year for stable tests (approx June)

def test_returns_none_below_horizon_midnight():
    # frac_day=0 -> around midnight solar time (depending on lon shift)
    d = solar_direction_from_latlon(lat_deg=35.0, lon_deg=0.0, frac_day=0.0, day_of_year=DAY)
    assert d is None

def test_direction_is_unit_vector_when_present():
    d = solar_direction_from_latlon(lat_deg=35.0, lon_deg=0.0, frac_day=0.5, day_of_year=DAY)  # near noon
    assert d is not None
    mag = math.sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2])
    assert abs(mag - 1.0) < 1e-6

def test_lower_latitude_has_higher_noon_elevation():
    # Compare Miami vs Anchorage at solar noon (frac_day=0.5, lon=0 for clean comparison)
    miami = solar_direction_from_latlon(lat_deg=25.7742, lon_deg=0.0, frac_day=0.5, day_of_year=DAY)
    anch  = solar_direction_from_latlon(lat_deg=61.2163, lon_deg=0.0, frac_day=0.5, day_of_year=DAY)

    assert miami is not None
    assert anch is not None

    elev_miami = elevation_deg_from_direction(miami)
    elev_anch  = elevation_deg_from_direction(anch)

    assert elev_miami > elev_anch