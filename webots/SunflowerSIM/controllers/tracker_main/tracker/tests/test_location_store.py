import json
from pathlib import Path
from tracker.location_store import LocationStore, Location

def test_load_returns_default_when_missing(tmp_path: Path):
    p = tmp_path / "location.json"
    store = LocationStore(path=str(p), default=Location(1.0, 2.0))
    loc = store.load()
    assert loc.lat == 1.0 and loc.lon == 2.0

def test_save_then_load(tmp_path: Path):
    p = tmp_path / "location.json"
    store = LocationStore(path=str(p), default=Location(0.0, 0.0))
    store.save(Location(35.0, -78.0))
    loc = store.load()
    assert loc.lat == 35.0 and loc.lon == -78.0

def test_load_ignores_bad_json_keeps_last_good(tmp_path: Path):
    p = tmp_path / "location.json"
    store = LocationStore(path=str(p), default=Location(0.0, 0.0))

    store.save(Location(10.0, 20.0))
    assert store.load() == Location(10.0, 20.0)

    # corrupt file
    p.write_text("{not json", encoding="utf-8")
    # should return cached last good
    assert store.load() == Location(10.0, 20.0)