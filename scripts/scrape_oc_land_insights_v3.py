import requests
import json
import os
from datetime import datetime

OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\oc_land_insights"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LAYERS = [
    {
        "name": "Tentative_Maps",
        "url": "https://www.ocgis.com/survey/rest/services/Landbase/TentativeMaps/FeatureServer/10/query",
        "fields": "*"
    },
    {
        "name": "Landbase_Lines",
        "url": "https://www.ocgis.com/survey/rest/services/Landbase/Landbase_Lines/FeatureServer/0/query",
        "fields": "*"
    },
    {
        "name": "RoW_Service",
        "url": "https://www.ocgis.com/survey/rest/services/Landbase/RoWService/FeatureServer/0/query",
        "fields": "*"
    },
    {
        "name": "Geodetic_Levels",
        "url": "https://www.ocgis.com/survey/rest/services/OCLandInsights/Geodetic/MapServer/0/query",
        "fields": "*"
    },
]

def download_layer(layer_config):
    name = layer_config["name"]
    base_url = layer_config["url"]
    fields = layer_config["fields"]
    
    print(f"\nDownloading: {name}")
    
    all_features = []
    offset = 0
    batch_size = 1000
    max_records = 50000
    
    while offset < max_records:
        params = {
            'where': '1=1',
            'outFields': fields,
            'resultOffset': offset,
            'resultRecordCount': batch_size,
            'f': 'json',
            'returnGeometry': 'true'
        }
        
        try:
            resp = requests.get(base_url, params=params, timeout=60)
            data = resp.json()
            
            features = data.get('features', [])
            if not features:
                break
            
            all_features.extend(features)
            offset += len(features)
            
            print(f"  Fetched {len(all_features)} records...")
            
            if not data.get('exceededTransferLimit', False):
                break
                
        except Exception as e:
            print(f"  Error at offset {offset}: {e}")
            break
    
    output_file = os.path.join(OUTPUT_DIR, f"{name}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'layer_url': base_url,
            'layer_name': name,
            'record_count': len(all_features),
            'downloaded_at': datetime.now().isoformat(),
            'features': all_features
        }, f, indent=2)
    
    print(f"  Saved {len(all_features)} records")
    return len(all_features)

def main():
    print("=" * 80)
    print("OC LAND INSIGHTS DATA SCRAPER v3")
    print("=" * 80)
    
    total = 0
    for layer in LAYERS:
        count = download_layer(layer)
        total += count
    
    print(f"\n{'=' * 80}")
    print(f"COMPLETE - Total records: {total}")

if __name__ == "__main__":
    main()
