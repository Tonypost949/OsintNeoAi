import os
import json
import datetime

base = r"C:\OsintNeoAi\data\takeouts\etp949609_takeout_20260913\Takeout"

def parse_recent():
    print("=== CHECKING SEMANTIC LOCATION TIMELINE ===")
    for loc_dir in ["Location History (Timeline)", "Location History"]:
        sem_root = os.path.join(base, loc_dir, "Semantic Location History")
        if os.path.exists(sem_root):
            for year in sorted(os.listdir(sem_root), reverse=True):
                year_path = os.path.join(sem_root, year)
                if os.path.isdir(year_path):
                    for month_file in sorted(os.listdir(year_path), reverse=True):
                        print(f"Found Semantic File: {year}/{month_file}")
                        full_f = os.path.join(year_path, month_file)
                        try:
                            with open(full_f, "r", encoding="utf-8") as fp:
                                sdata = json.load(fp)
                                timeline_objs = sdata.get("timelineObjects", [])
                                print(f"  -> {len(timeline_objs)} timeline objects in {month_file}")
                                # Look at last 5 objects
                                for obj in timeline_objs[-5:]:
                                    if "activitySegment" in obj:
                                        act = obj["activitySegment"]
                                        start = act.get("duration", {}).get("startTimestamp")
                                        end = act.get("duration", {}).get("endTimestamp")
                                        act_type = act.get("activityType")
                                        dist = act.get("distance")
                                        print(f"  [ACTIVITY] {start} to {end} | Type: {act_type} | Dist: {dist}m")
                                    elif "placeVisit" in obj:
                                        pv = obj["placeVisit"]
                                        start = pv.get("duration", {}).get("startTimestamp")
                                        end = pv.get("duration", {}).get("endTimestamp")
                                        loc = pv.get("location", {})
                                        name = loc.get("name", "Unknown Place")
                                        addr = loc.get("address", "")
                                        lat = loc.get("latitudeE7", 0) / 1e7
                                        lng = loc.get("longitudeE7", 0) / 1e7
                                        print(f"  [PLACE VISIT] {start} to {end} | {name} ({addr}) | Lat: {lat}, Lng: {lng}")
                        except Exception as e:
                            print(f"  Error reading {full_f}: {e}")

    print("\n=== CHECKING RECORDS.JSON LATEST POINTS ===")
    records_file = os.path.join(base, "Location History", "Records.json")
    if os.path.exists(records_file):
        with open(records_file, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            locs = data.get("locations", [])
            print(f"Total raw GPS records: {len(locs)}")
            for l in locs[-15:]:
                t = l.get("timestamp") or l.get("timestampMs")
                lat = l.get("latitudeE7", 0) / 1e7
                lng = l.get("longitudeE7", 0) / 1e7
                acc = l.get("accuracy", "N/A")
                print(f"Raw GPS: {t} | Lat: {lat}, Lng: {lng} | Accuracy: {acc}m")

    print("\n=== CHECKING MY ACTIVITY (ANDROID & DEVICE ACTIVITY) ===")
    act_dir = os.path.join(base, "My Activity")
    if os.path.exists(act_dir):
        for root, dirs, files in os.walk(act_dir):
            for f in files:
                if f.endswith(".html") or f.endswith(".json"):
                    full_p = os.path.join(root, f)
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                            txt = fp.read()
                            # Check recent date mentions (September 2026 or Sep 10-13)
                            for d in ["Sep 10, 2026", "Sep 11, 2026", "Sep 12, 2026", "Sep 13, 2026", "2026-09-10", "2026-09-11", "2026-09-12", "2026-09-13"]:
                                if d in txt:
                                    print(f"Recent Activity found for {d} in: {f}")
                    except Exception:
                        pass

if __name__ == "__main__":
    parse_recent()
