import requests
import json
import os
from datetime import datetime

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\oc_land_insights"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_layer(name, base_url, max_records=10000):
    print(f"\n=== {name} ===")
    all_features = []
    offset = 0
    batch = 1000
    
    while offset < max_records:
        params = {
            "where": "1=1",
            "outFields": "*",
            "resultOffset": offset,
            "resultRecordCount": batch,
            "f": "json",
            "returnGeometry": "true"
        }
        resp = requests.get(base_url, params=params, timeout=60)
        data = resp.json()
        features = data.get("features", [])
        if not features:
            break
        all_features.extend(features)
        offset += len(features)
        print(f"  {len(all_features)} records...")
        if not data.get("exceededTransferLimit", False):
            break
    
    outfile = os.path.join(OUTPUT_DIR, f"{name}.json")
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump({"name": name, "count": len(all_features), "time": datetime.now().isoformat(), "features": all_features}, f, indent=2)
    print(f"  SAVED: {len(all_features)} records")
    return len(all_features)

layers = [
    ("Tentative_Maps", "https://www.ocgis.com/survey/rest/services/Landbase/TentativeMaps/FeatureServer/10/query"),
    ("Landbase_Lines", "https://www.ocgis.com/survey/rest/services/Landbase/Landbase_Lines/FeatureServer/0/query"),
    ("RoW_Service", "https://www.ocgis.com/survey/rest/services/Landbase/RoWService/FeatureServer/0/query"),
]

total = 0
for name, url in layers:
    total += download_layer(name, url)

print(f"\nDONE - Total: {total} records")
