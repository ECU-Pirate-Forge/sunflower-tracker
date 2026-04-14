# solar_math.py
import math
from typing import Optional, List

def solar_direction_from_latlon(
    lat_deg: float,
    lon_deg: float,
    frac_day: float,
    day_of_year: int,
) -> Optional[List[float]]:
    """
    Returns DirectionalLight.direction vector (light ray direction) or None if below horizon.
    frac_day: 0..1 representing time through the day.
    day_of_year: 1..365 for declination stability in tests.
    """
    lat = math.radians(lat_deg)

    # Solar declination (approx)
    decl = math.radians(23.44) * math.sin(2.0 * math.pi * (284 + day_of_year) / 365.0)

    # Time of day in hours mapped to [0, 24), shift by longitude
    time_hours = (frac_day * 24.0 + (lon_deg / 15.0)) % 24.0

    # Hour angle H (0 at solar noon)
    H = math.radians(15.0 * (time_hours - 12.0))

    # Altitude
    sin_alt = math.sin(lat) * math.sin(decl) + math.cos(lat) * math.cos(decl) * math.cos(H)
    alt = math.asin(max(-1.0, min(1.0, sin_alt)))

    if alt <= 0.0:
        return None

    # Azimuth
    az = math.atan2(math.sin(H), (math.cos(H) * math.sin(lat) - math.tan(decl) * math.cos(lat)))
    az_from_north = (az + math.pi) % (2.0 * math.pi)

    # ENU unit vector (x=east, y=up, z=north)
    x = math.cos(alt) * math.sin(az_from_north)
    y = math.sin(alt)
    z = math.cos(alt) * math.cos(az_from_north)

    # DirectionalLight direction = -sun_vector
    return [-x, -y, -z]

def elevation_deg_from_direction(d):
    x, y, z = d
    horiz = math.sqrt(x * x + z * z)
    return math.degrees(math.atan2(-y, horiz))