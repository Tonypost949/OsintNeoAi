import os
import json
import re
import datetime

BASE_DIR = r"C:\OsintNeoAi\data\takeouts\etp949609_takeout_20260913\sept_11_phone_theft_investigation"

def build_full_sept_11_dossier():
    print(f"[DOSSIER COMPILER] Parsing all September 11 records in {BASE_DIR}...")
    
    events = []
    
    # 1. Location & Place Visits
    for f in os.listdir(BASE_DIR):
        if f.endswith(".json") and "SEPTEMBER" in f:
            p = os.path.join(BASE_DIR, f)
            year = f.split("_")[0]
            try:
                with open(p, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    objs = data.get("timelineObjects", [])
                    for obj in objs:
                        if "placeVisit" in obj:
                            pv = obj["placeVisit"]
                            s = pv.get("duration", {}).get("startTimestamp", "")
                            e = pv.get("duration", {}).get("endTimestamp", "")
                            if "09-11" in s or "09-11" in e:
                                loc = pv.get("location", {})
                                name = loc.get("name", "Unknown Place")
                                addr = loc.get("address", "")
                                lat = loc.get("latitudeE7", 0) / 1e7
                                lng = loc.get("longitudeE7", 0) / 1e7
                                events.append({
                                    "year": year,
                                    "start": s,
                                    "end": e,
                                    "type": "PLACE_VISIT",
                                    "location": name,
                                    "address": addr,
                                    "lat": lat,
                                    "lng": lng
                                })
                        elif "activitySegment" in obj:
                            act = obj["activitySegment"]
                            s = act.get("duration", {}).get("startTimestamp", "")
                            e = act.get("duration", {}).get("endTimestamp", "")
                            if "09-11" in s or "09-11" in e:
                                atype = act.get("activityType", "TRANSIT")
                                dist = act.get("distance", 0)
                                events.append({
                                    "year": year,
                                    "start": s,
                                    "end": e,
                                    "type": f"TRANSIT_{atype}",
                                    "distance_meters": dist
                                })
            except Exception as e:
                print(f"Error parsing {f}: {e}")

    # 2. Play Store Installs & Purchases on Sept 11
    for f in ["Installs.json", "Order History.json", "Purchase History.json"]:
        p = os.path.join(BASE_DIR, f)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as fp:
                    pdata = json.load(fp)
                    if isinstance(pdata, list):
                        for item in pdata:
                            txt = json.dumps(item)
                            if "09-11" in txt:
                                events.append({
                                    "source": f,
                                    "type": "PLAY_STORE_ACTIVITY",
                                    "data": item
                                })
            except Exception:
                pass

    # Sort events by timestamp
    events.sort(key=lambda x: str(x.get("start", x.get("data", ""))))

    # Write out comprehensive JSON dossier
    dossier_data = {
        "target": "etp949609@gmail.com",
        "investigation_focus": "September 11 Phone Theft & Movement Analysis",
        "total_events_logged": len(events),
        "events": events
    }
    
    with open(os.path.join(BASE_DIR, "SEPT_11_INVESTIGATION_DOSSIER.json"), "w", encoding="utf-8") as fp:
        json.dump(dossier_data, fp, indent=2)

    # Write out comprehensive Markdown report
    with open(os.path.join(BASE_DIR, "SEPT_11_INVESTIGATION_REPORT.md"), "w", encoding="utf-8") as fp:
        fp.write("# SEPTEMBER 11 FORENSIC DOSSIER & PHONE THEFT TRACE\n\n")
        fp.write(f"**Target Account**: `etp949609@gmail.com`\n")
        fp.write(f"**Total Chronological Events**: `{len(events)}`\n\n")
        fp.write("## Chronological Timeline of Events & Geolocation Breadcrumbs\n\n")
        fp.write("| Timestamp / Duration | Event Type | Location / Details | Coordinates |\n")
        fp.write("| :--- | :--- | :--- | :--- |\n")
        for ev in events:
            t = f"{ev.get('start', '')} to {ev.get('end', '')}"
            etype = ev.get('type', 'EVENT')
            loc_info = f"{ev.get('location', '')} ({ev.get('address', '')})" if 'location' in ev else str(ev.get('distance_meters', '')) + "m transit"
            coords = f"`{ev.get('lat')}, {ev.get('lng')}`" if 'lat' in ev else "—"
            fp.write(f"| `{t}` | `{etype}` | {loc_info} | {coords} |\n")

    print(f"[✓] Successfully compiled September 11 Dossier with {len(events)} timestamped events!")

if __name__ == "__main__":
    build_full_sept_11_dossier()
