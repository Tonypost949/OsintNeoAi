"""
GeoJSON export for mapping entities with geolocation data.
"""

import json
import os
from typing import Any


class GeoJSONExporter:
    """Export entities with coordinates to GeoJSON for mapping tools."""

    def __init__(self):
        self.features = []

    def add_point(self, lon: float, lat: float, properties: dict = None):
        self.features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": properties or {},
        })

    def add_entity_with_address(self, entity_value: str, entity_type: str, address: str = None,
                                 lat: float = None, lon: float = None, metadata: dict = None):
        props = {"name": entity_value, "type": entity_type}
        if address:
            props["address"] = address
        if metadata:
            props.update(metadata)
        if lat is not None and lon is not None:
            self.add_point(lon, lat, props)

    def add_line(self, coordinates: list[list[float]], properties: dict = None):
        self.features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coordinates},
            "properties": properties or {},
        })

    def add_polygon(self, coordinates: list[list[list[float]]], properties: dict = None):
        self.features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": coordinates},
            "properties": properties or {},
        })

    def to_geojson(self) -> dict:
        return {
            "type": "FeatureCollection",
            "features": self.features,
        }

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.to_geojson(), f, indent=2)
        return filepath

    def from_entities(self, entities: list[dict], lat_key: str = "lat", lon_key: str = "lon"):
        for e in entities:
            meta = e.get("metadata", {})
            lat = meta.get(lat_key) or e.get(lat_key)
            lon = meta.get(lon_key) or e.get(lon_key)
            if lat is not None and lon is not None:
                try:
                    self.add_point(float(lon), float(lat), {
                        "name": e.get("value", ""),
                        "type": e.get("type", ""),
                        "source": e.get("source", ""),
                        "confidence": e.get("confidence", 0),
                    })
                except (ValueError, TypeError):
                    pass
