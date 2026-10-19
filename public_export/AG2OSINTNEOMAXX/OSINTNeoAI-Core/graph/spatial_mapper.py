import json

class SpatialMapper:
    """Consolidated GIS and spatial mapping tool producing GeoJSON footprints."""
    
    def __init__(self):
        self.features = []

    def add_point(self, name, lat, lon, properties=None):
        """Add a geographic point (such as an address or office) with optional metadata properties."""
        try:
            latitude = float(lat)
            longitude = float(lon)
        except (ValueError, TypeError):
            print(f"[GIS] Invalid coordinates skipped for point {name}: ({lat}, {lon})")
            return
            
        props = properties or {}
        props["name"] = name
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [longitude, latitude] # GeoJSON uses [lon, lat] order
            },
            "properties": props
        }
        self.features.append(feature)

    def export_to_geojson(self, output_path):
        """Compiles registered features and writes a standard GeoJSON file."""
        geojson = {
            "type": "FeatureCollection",
            "features": self.features
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, indent=2)
            print(f"[GIS] Exported {len(self.features)} features to GIS Layer {output_path}")
        except Exception as e:
            print(f"[GIS] Error writing GeoJSON file: {e}")
            raise
            
        return geojson
