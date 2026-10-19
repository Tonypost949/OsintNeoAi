#!/usr/bin/env python3
"""GPS Trajectory Stream Extractor for God's Eye 3D Tactical Maps.

Extracts chronological waypoint tracks, vehicle surveillance trajectories,
and municipal incident points into GeoJSON LineString and Point milestones.
"""

import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "public", "gps_trajectory_stream.geojson")

def generate_trajectory_stream(output_path: str = OUTPUT_FILE) -> str:
    print("[+] Compiling tactical trajectory stream...")
    
    # Base timestamp for synthetic timeline simulation
    base_time = datetime.now(timezone.utc) - timedelta(hours=6)
    
    # Core surveillance waypoints along Orange County corridor
    waypoints = [
        {"lat": 33.7455, "lng": -117.8677, "label": "Santa Ana Civic Center", "speed_mph": 0, "event": "Depart Admin Hub"},
        {"lat": 33.7580, "lng": -117.8920, "label": "Garden Grove Blvd Node", "speed_mph": 35, "event": "Transit Point A"},
        {"lat": 33.7320, "lng": -117.9350, "label": "Westminster Blvd Intercept", "speed_mph": 42, "event": "Transit Point B"},
        {"lat": 33.7050, "lng": -117.9620, "label": "Fountain Valley Station", "speed_mph": 28, "event": "Checkpoint"},
        {"lat": 33.6840, "lng": -117.9890, "label": "Huntington Beach Civic Corridor", "speed_mph": 30, "event": "Surveillance Node"},
        {"lat": 33.6595, "lng": -117.9988, "label": "HBPD Public Safety Center", "speed_mph": 0, "event": "Stationary Inspection"},
        {"lat": 33.6320, "lng": -117.9280, "label": "Newport Beach Coastal Node", "speed_mph": 45, "event": "Transit Point C"},
        {"lat": 33.6180, "lng": -117.8850, "label": "Corona Del Mar Checkpoint", "speed_mph": 38, "event": "Transit Point D"},
        {"lat": 33.5420, "lng": -117.7830, "label": "Laguna Beach Terminal Node", "speed_mph": 0, "event": "End of Patrol"}
    ]
    
    features = []
    line_coordinates = []
    
    for idx, pt in enumerate(waypoints):
        ts = (base_time + timedelta(minutes=idx * 20)).isoformat()
        line_coordinates.append([pt["lng"], pt["lat"]])
        
        point_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [pt["lng"], pt["lat"]]
            },
            "properties": {
                "sequence_index": idx,
                "label": pt["label"],
                "speed_mph": pt["speed_mph"],
                "event": pt["event"],
                "timestamp": ts,
                "marker-color": "#06b6d4" if idx not in [0, len(waypoints)-1] else "#10b981"
            }
        }
        features.append(point_feature)
        
    # Trajectory Line Feature
    line_feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": line_coordinates
        },
        "properties": {
            "title": "Tactical Patrol & Surveillance Trajectory",
            "stroke": "#06b6d4",
            "stroke-width": 4,
            "stroke-opacity": 0.85,
            "total_waypoints": len(waypoints),
            "start_time": (base_time).isoformat(),
            "end_time": (base_time + timedelta(minutes=(len(waypoints)-1)*20)).isoformat()
        }
    }
    features.append(line_feature)
    
    feature_collection = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "OsintNeoAi Tactical GPS Trajectory Stream",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_features": len(features)
        },
        "features": features
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feature_collection, f, indent=2)
        
    print(f"[+] Exported {len(features)} trajectory features to {output_path}")
    return output_path

if __name__ == "__main__":
    generate_trajectory_stream()
