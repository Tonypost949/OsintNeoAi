#!/usr/bin/env python3
"""
scripts/calculate_cctv_proximity.py
===================================
Calculates spatial proximity between high-priority OSINT target hubs and
the 288 Orange County Caltrans District 12 CCTV live cameras.
Generates evidence/target_cctv_proximity.json for God's Eye View HUD radar.
"""

import json
import math
import os

REPO_ROOT = r"C:\OsintNeoAi"
CCTV_GEOJSON = os.path.join(REPO_ROOT, "evidence", "caltrans_d12_cctv.geojson")
PROXIMITY_OUTPUT = os.path.join(REPO_ROOT, "evidence", "target_cctv_proximity.json")

TARGETS = [
    {"id": "DOVE_ST", "name": "1601 Dove Street", "lat": 33.6558, "lon": -117.8682, "city": "Newport Beach", "type": "Corporate Nexus"},
    {"id": "CAMERON_LN", "name": "17631 Cameron Lane", "lat": 33.7028, "lon": -117.9944, "city": "Huntington Beach", "type": "Residential Proxy"},
    {"id": "CENTER_AVE", "name": "7561 Center Ave", "lat": 33.7389, "lon": -118.0016, "city": "Huntington Beach", "type": "Commercial Hub"},
    {"id": "BEACH_BLVD", "name": "17642 Beach Blvd", "lat": 33.7029, "lon": -117.9892, "city": "Huntington Beach", "type": "Contamination Zone"}
]

def haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def compute_proximity():
    if not os.path.exists(CCTV_GEOJSON):
        print(f"❌ CCTV GeoJSON not found: {CCTV_GEOJSON}")
        return

    with open(CCTV_GEOJSON, "r", encoding="utf-8") as f:
        cctv_data = json.load(f)

    cameras = []
    for feat in cctv_data.get("features", []):
        props = feat.get("properties", {})
        coords = feat.get("geometry", {}).get("coordinates", [0, 0])
        cameras.append({
            "id": props.get("id"),
            "location": props.get("locationName"),
            "route": props.get("route"),
            "direction": props.get("direction"),
            "postmile": props.get("postmile"),
            "stream_url": props.get("streamingVideoURL"),
            "image_url": props.get("currentImageURL"),
            "lon": coords[0],
            "lat": coords[1]
        })

    print(f"[*] Analyzing {len(cameras)} Caltrans CCTV cameras against {len(TARGETS)} operational target nodes...")

    results = []
    for tgt in TARGETS:
        t_lat, t_lon = tgt["lat"], tgt["lon"]
        cam_distances = []
        for cam in cameras:
            dist = haversine_miles(t_lat, t_lon, cam["lat"], cam["lon"])
            cam_distances.append({**cam, "distance_miles": round(dist, 2)})
        
        cam_distances.sort(key=lambda x: x["distance_miles"])
        nearest = cam_distances[:4]

        results.append({
            "target": tgt,
            "nearest_cameras": nearest,
            "coverage_radius_miles": nearest[0]["distance_miles"] if nearest else None
        })
        print(f"  🎯 {tgt['name']} -> Nearest Camera: {nearest[0]['location']} ({nearest[0]['distance_miles']} mi)")

    with open(PROXIMITY_OUTPUT, "w", encoding="utf-8") as f:
        json.dump({"targets_coverage": results, "generated_at": "2026-09-01T12:15:00Z"}, f, indent=2)

    print(f"[+] Proximity Matrix saved: {PROXIMITY_OUTPUT}")

if __name__ == "__main__":
    compute_proximity()
