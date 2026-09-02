#!/usr/bin/env python3
"""
scripts/calculate_cctv_proximity.py
===================================
Calculates spatial proximity between high-priority OSINT target hubs and
the 288 Orange County Caltrans District 12 CCTV live cameras.
Generates evidence/target_cctv_proximity.json for God's Eye View HUD radar.
Supports dynamic relative pathing and callable nearest camera lookup.
"""

import json
import math
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Dynamic Repo Root resolution
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1] if THIS_FILE.parents[1].name != "scripts" else THIS_FILE.parents[1]
if not (REPO_ROOT / "evidence").exists():
    for cand in [Path("/home/site/wwwroot"), Path("C:/OsintNeoAi"), Path.cwd()]:
        if (cand / "evidence").exists():
            REPO_ROOT = cand
            break

CCTV_GEOJSON = REPO_ROOT / "evidence" / "caltrans_d12_cctv.geojson"
PROXIMITY_OUTPUT = REPO_ROOT / "evidence" / "target_cctv_proximity.json"

TARGETS = [
    {"id": "DOVE_ST", "name": "1601 Dove Street", "lat": 33.6558, "lon": -117.8682, "city": "Newport Beach", "type": "Corporate Nexus"},
    {"id": "CAMERON_LN", "name": "17631 Cameron Lane", "lat": 33.7028, "lon": -117.9944, "city": "Huntington Beach", "type": "Residential Proxy"},
    {"id": "CENTER_AVE", "name": "7561 Center Ave", "lat": 33.7389, "lon": -118.0016, "city": "Huntington Beach", "type": "Commercial Hub"},
    {"id": "BEACH_BLVD", "name": "17642 Beach Blvd", "lat": 33.7029, "lon": -117.9892, "city": "Huntington Beach", "type": "Contamination Zone"}
]


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate Great-Circle geodesic distance between two points in statute miles.
    """
    R = 3958.8  # Earth mean radius in statute miles
    try:
        phi1 = math.radians(float(lat1))
        phi2 = math.radians(float(lat2))
        dphi = math.radians(float(lat2) - float(lat1))
        dlambda = math.radians(float(lon2) - float(lon1))
        
        a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
        a = min(1.0, max(0.0, a))
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c
    except Exception:
        return 9999.0


def load_cctv_cameras() -> List[Dict[str, Any]]:
    """
    Load and parse all 288 Caltrans CCTV cameras from GeoJSON.
    """
    if not CCTV_GEOJSON.exists():
        # Search alternative locations
        for cand in [REPO_ROOT / "public" / "caltrans_d12_cctv.geojson", REPO_ROOT / "opencode_work" / "caltrans_d12_cctv.geojson"]:
            if cand.exists():
                return _parse_geojson(cand)
        return []
    return _parse_geojson(CCTV_GEOJSON)


def _parse_geojson(geojson_path: Path) -> List[Dict[str, Any]]:
    cameras = []
    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            cctv_data = json.load(f)
        for feat in cctv_data.get("features", []):
            props = feat.get("properties", {})
            coords = feat.get("geometry", {}).get("coordinates", [0.0, 0.0])
            cam_id = str(props.get("object_id") or props.get("id") or props.get("cctv_id") or "")
            location = str(props.get("entity_name") or props.get("locationName") or props.get("name") or "Caltrans CCTV")
            cameras.append({
                "id": cam_id,
                "location": location,
                "route": str(props.get("route") or ""),
                "direction": str(props.get("direction") or ""),
                "postmile": props.get("postmile"),
                "stream_url": props.get("stream_url") or props.get("streamingVideoURL"),
                "image_url": props.get("image_url") or props.get("currentImageURL"),
                "lon": float(coords[0]),
                "lat": float(coords[1])
            })
    except Exception as e:
        print(f"❌ Error loading CCTV GeoJSON ({geojson_path}): {e}")
    return cameras


def get_nearest_cctv(lat: float, lon: float, k: int = 4, cameras: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Return top-k nearest Caltrans CCTV cameras to given coordinates.
    """
    if cameras is None:
        cameras = load_cctv_cameras()
    if not cameras or lat is None or lon is None:
        return []
        
    distances = []
    for cam in cameras:
        d = haversine_miles(lat, lon, cam["lat"], cam["lon"])
        distances.append({
            "id": cam["id"],
            "location": cam["location"],
            "route": cam["route"],
            "direction": cam["direction"],
            "postmile": cam["postmile"],
            "stream_url": cam["stream_url"],
            "image_url": cam["image_url"],
            "lat": cam["lat"],
            "lon": cam["lon"],
            "distance_miles": round(d, 2)
        })
        
    distances.sort(key=lambda x: x["distance_miles"])
    return distances[:k]


def compute_proximity() -> Dict[str, Any]:
    cameras = load_cctv_cameras()
    if not cameras:
        print(f"❌ CCTV GeoJSON not found at {CCTV_GEOJSON}")
        return {"targets_coverage": [], "generated_at": datetime.now(timezone.utc).isoformat()}

    print(f"[*] Analyzing {len(cameras)} Caltrans CCTV cameras against {len(TARGETS)} operational target nodes...")

    results = []
    for tgt in TARGETS:
        t_lat, t_lon = tgt["lat"], tgt["lon"]
        nearest = get_nearest_cctv(t_lat, t_lon, k=4, cameras=cameras)

        coverage_radius = nearest[0]["distance_miles"] if nearest else None
        results.append({
            "target": tgt,
            "nearest_cameras": nearest,
            "coverage_radius_miles": coverage_radius
        })
        if nearest:
            print(f"  🎯 {tgt['name']} -> Nearest Camera: {nearest[0]['location']} ({nearest[0]['distance_miles']} mi)")

    payload = {
        "targets_coverage": results,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    try:
        PROXIMITY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with open(PROXIMITY_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"[+] Proximity Matrix saved: {PROXIMITY_OUTPUT}")
    except Exception as e:
        print(f"❌ Error saving proximity output: {e}")

    return payload


if __name__ == "__main__":
    compute_proximity()
