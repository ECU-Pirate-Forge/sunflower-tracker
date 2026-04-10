from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Optional


@dataclass(frozen=True)
class Location:
    lat: float
    lon: float


class LocationStore:
    """
    Reads/writes a JSON file containing {"lat": <float>, "lon": <float>}.
    Designed so Webots can re-read this during simulation.
    """

    def __init__(
        self,
        path: Optional[str] = None,
        default: Location = Location(35.78, -78.64),
    ):
        if path is None:
            # file lives beside this module: tracker/location.json
            path = str(Path(__file__).with_name("location.json"))
        self.path = Path(path)
        self.default = default
        self._last_mtime: Optional[float] = None
        self._cached: Location = default

    def load(self) -> Location:
        if not self.path.exists():
            return self.default

        try:
            mtime = self.path.stat().st_mtime
            if self._last_mtime is not None and mtime == self._last_mtime:
                return self._cached

            data = json.loads(self.path.read_text(encoding="utf-8"))
            loc = Location(lat=float(data["lat"]), lon=float(data["lon"]))
            self._last_mtime = mtime
            self._cached = loc
            return loc
        except Exception:
            # If file is malformed mid-edit, keep last known good value
            return self._cached

    def save(self, loc: Location) -> None:
        self.path.write_text(
            json.dumps({"lat": loc.lat, "lon": loc.lon}, indent=2),
            encoding="utf-8",
        )
        self._last_mtime = self.path.stat().st_mtime
        self._cached = loc