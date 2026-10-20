#!/usr/bin/env python3
"""GeoJSON Spatial Telemetry Transformer for OsintNeoAi 3D Maps.

Converts GPS coordinates, municipal entities, and target account locations
into standardized GeoJSON FeatureCollections for MapLibre / ArcGIS / God's Eye.
"""

import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
OUTPUT_GEOJSON = os.path.join(PUBLIC_DIR, "live_telemetry.geojson")

def create_feature(
    lat: float,
    lng: float,
    title: str,
    category: str = "General",
    description: str = "",
    properties: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized GeoJSON Feature object."""
    props = {
        "title": title,
        "category": category,
        "description": description,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "marker-color": get_marker_color(category)
    }
    if properties:
        props.update(properties)

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lng, lat]
        },
        "properties": props
    }

def get_marker_color(category: str) -> str:
    category_lower = category.lower()
    if "surveillance" in category_lower or "target" in category_lower:
        return "#e74c3c"  # Red
    elif "municipal" in category_lower or "court" in category_lower:
        return "#3498db"  # Blue
    elif "commercial" in category_lower or "corporate" in category_lower:
        return "#2ecc71"  # Green
    elif "medical" in category_lower:
        return "#e67e22"  # Orange
    return "#9b59b6"      # Purple

def compile_feature_collection(features: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Wrap features in a GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "metadata": {
            "generator": "OsintNeoAi GeoJSON Telemetry Engine",
            "count": len(features),
            "generated_at": datetime.now(timezone.utc).isoformat()
        },
        "features": features
    }

def generate_telemetry_feed(output_path: str = OUTPUT_GEOJSON) -> str:
    """Generate default live telemetry feed from repository locations."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    sample_nodes = [
        (33.7455, -117.8677, "Santa Ana Municipal Center", "Municipal", "Orange County Administration"),
        (33.6595, -117.9988, "Huntington Beach Police Dept", "Surveillance", "Public Safety & Records Hub"),
        (33.8366, -117.9143, "Anaheim Corporate Complex", "Corporate", "Corporate Registry Ingestion"),
        (42.3601, -71.0589, "Massachusetts Federal Court", "Court", "First Circuit District Court"),
        (32.7157, -117.1611, "San Diego Cross-Border Node", "Target", "Cross-border surveillance node")
    ]
    
    features = [
        create_feature(lat, lng, title, cat, desc)
        for lat, lng, title, cat, desc in sample_nodes
    ]
    
    collection = compile_feature_collection(features)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2)
        
    print(f"[+] Exported {len(features)} GeoJSON features to {output_path}")
    return output_path

if __name__ == "__main__":
    generate_telemetry_feed()
