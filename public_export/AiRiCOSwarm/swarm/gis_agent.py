"""SpatialGISAgent: Correlates APN parcels, addresses, and municipal contracts."""

import json
import os
from typing import Dict, Any, List

class SpatialGISAgent:
    def __init__(self, storage_dir: str = "AiRiCOSwarm/storage"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.geojson_path = os.path.join(storage_dir, "spatial_features.geojson")

    def build_feature(self, lat: float, lon: float, title: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "title": title,
                **details
            }
        }

    def save_features(self, features: List[Dict[str, Any]]):
        feature_collection = {
            "type": "FeatureCollection",
            "features": features
        }
        with open(self.geojson_path, "w", encoding="utf-8") as f:
            json.dump(feature_collection, f, indent=2)
