# tools/set_location.py
import json
import re
import time
from pathlib import Path

import requests

UNIT_PATTERNS = [
    r"\bapt\b\s*\w+",
    r"\bapartment\b\s*\w+",
    r"\bunit\b\s*\w+",
    r"\bsuite\b\s*\w+",
    r"\bste\b\.?\s*\w+",
    r"\b#\s*\w+",
]

def strip_unit(text: str) -> str:
    s = text
    for pat in UNIT_PATTERNS:
        s = re.sub(pat, "", s, flags=re.IGNORECASE)
    # clean leftover double spaces/commas
    s = re.sub(r"\s{2,}", " ", s).strip()
    s = re.sub(r"\s*,\s*,", ",", s).strip(", ").strip()
    return s

def build_fallback_queries(address: str) -> list[str]:
    addr = address.strip()
    no_unit = strip_unit(addr)

    # Try a few increasingly “less specific” variants
    queries = []
    if addr:
        queries.append(addr)
    if no_unit and no_unit != addr:
        queries.append(no_unit)

    # If user typed something like "lat,lon" we’ll handle elsewhere; keep these for nominatim
    return list(dict.fromkeys(queries))  # dedupe, preserve order

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    # Use a real identifier per Nominatim etiquette.
    "User-Agent": "sunflower-tracker/1.0"
}

# Where we store the location for Webots controllers to read
REPO_ROOT = Path(__file__).resolve().parents[1]  # sunflower-tracker/
OUT_PATH = REPO_ROOT / "webots" / "SunflowerSIM" / "controllers" / "tracker_main" / "tracker" / "location.json"


def candidate_queries(address: str) -> list[str]:
    """Generate a few progressively-simplified queries."""
    addr = address.strip()

    # Remove apartment/unit/suite fragments but keep the street/city/state/zip
    # Examples removed: "apt 703", "unit B", "#12", "ste 200"
    simplified = re.sub(
        r"\s*(,?\s*)\b(apt|apartment|unit|ste|suite|#)\s*[\w\-]+\b",
        "",
        addr,
        flags=re.IGNORECASE
    ).strip()

    # Remove double spaces and trailing commas
    simplified = re.sub(r"\s{2,}", " ", simplified).strip(" ,")

    queries = []
    for q in [addr, simplified]:
        if q and q not in queries:
            queries.append(q)

    # Also try without ZIP (sometimes helps)
    no_zip = re.sub(r"\b\d{5}(-\d{4})?\b", "", simplified).strip(" ,")
    if no_zip and no_zip not in queries:
        queries.append(no_zip)

    return queries


def geocode_nominatim(address: str) -> tuple[float, float]:
    # If user enters "lat,lon" directly, accept it
    m = re.match(r"^\s*(-?\d+(\.\d+)?)\s*,\s*(-?\d+(\.\d+)?)\s*$", address)
    if m:
        return float(m.group(1)), float(m.group(3))

    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        # Nominatim expects a real user-agent; include your project + contact
        "User-Agent": "sunflower-tracker/1.0"
    }

    queries = build_fallback_queries(address)

    last_error = None
    for q in queries:
        params = {
            "q": q,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
            "countrycodes": "us",
        }

        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return lat, lon

        except Exception as e:
            last_error = e

        # polite pause (also helps if you get rate-limited)
        time.sleep(1.0)

    if last_error:
        raise RuntimeError(f"No results found for '{address}' (tried fallbacks). Last error: {last_error}")
    raise RuntimeError(f"No results found for '{address}' (tried fallbacks).")


def main():
    address = input("Enter address or city/state: ").strip()
    if not address:
        raise RuntimeError("No input provided.")

    lat, lon = geocode_nominatim(address)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    payload = {"address": address, "lat": lat, "lon": lon}
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Saved: {OUT_PATH}")
    print(f"lat={lat}, lon={lon}")


if __name__ == "__main__":
    main()