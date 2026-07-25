import json
from google.cloud import bigquery

# Initialize BigQuery client (uses Application Default Credentials)
client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

DATASET = "project-743aab84-f9a5-4ec7-954.ai_sandbox"
SOURCE_TABLE = "hb_surface_flow"
DEST_FILE = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7\hb_surface_flow_wgs84.geojson"

# Query to transform geometry to WGS84 (SRID 4326) and output as GeoJSON string
query = f"""
SELECT
  * EXCEPT(geometry_json),
  ST_ASGEOJSON(
    ST_TRANSFORM(
      ST_GEOGFROMGEOJSON(geometry_json),
      4326
    )
  ) AS geometry_wgs84
FROM `{DATASET}.{SOURCE_TABLE}`
"""

print("[+] Running transformation query…")
job = client.query(query)
results = job.result()

features = []
for row in results:
    props = dict(row)
    # Remove the raw geometry columns we don't need in the output
    props.pop("geometry_json", None)
    geom = props.pop("geometry_wgs84", None)
    features.append({
        "type": "Feature",
        "properties": props,
        "geometry": json.loads(geom) if geom else None,
    })

feature_collection = {
    "type": "FeatureCollection",
    "features": features,
}

print(f"[+] Writing {len(features)} features to GeoJSON…")
with open(DEST_FILE, "w", encoding="utf-8") as f:
    json.dump(feature_collection, f, ensure_ascii=False, indent=2)

print(f"[+] Done – GeoJSON saved at {DEST_FILE}")
