import requests
import json
import os
from datetime import datetime

BASE_URL = "https://www.ocgis.com/survey/rest/services"
OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\oc_land_insights"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def query_feature_layer(url, where="1=1", out_fields="*", result_offset=0, result_count=1000):
    params = {
        'where': where,
        'outFields': out_fields,
        'resultOffset': result_offset,
        'resultRecordCount': result_count,
        'f': 'json',
        'returnGeometry': 'true'
    }
    resp = requests.get(url, params=params, timeout=60)
    return resp.json()

def download_layer(base_url, layer_url, layer_name, max_records=50000):
    print(f"\nDownloading: {layer_name}")
    
    all_features = []
    offset = 0
    batch_size = 1000
    
    while offset < max_records:
        try:
            url = f"{base_url}/{layer_url}/query"
            data = query_feature_layer(url, result_offset=offset, result_count=batch_size)
            
            features = data.get('features', [])
            if not features:
                break
            
            all_features.extend(features)
            offset += len(features)
            
            print(f"  Fetched {len(all_features)} records...")
            
            if len(features) < batch_size:
                break
                
        except Exception as e:
            print(f"  Error at offset {offset}: {e}")
            break
    
    safe_name = layer_name.replace('/', '_').replace(' ', '_')
    output_file = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'layer_url': layer_url,
            'layer_name': layer_name,
            'record_count': len(all_features),
            'downloaded_at': datetime.now().isoformat(),
            'features': all_features
        }, f, indent=2)
    
    print(f"  Saved {len(all_features)} records to {output_file}")
    return len(all_features)

def main():
    print("=" * 80)
    print("OC LAND INSIGHTS DATA SCRAPER v2")
    print("=" * 80)
    
    layers_to_download = [
        # OC Land Insights - Geodetic Control Points
        ("OCLandInsights/Geodetic/999018", "Horizontal_Control_Points"),
        ("OCLandInsights/Geodetic/999020", "Vertical_Control_Points"),
        ("OCLandInsights/Geodetic/0", "Geodetic_Levels_Table"),
        
        # Landbase Services
        ("Landbase/Landbase_Lines/0", "Landbase_Lines"),
        ("Landbase/RoWService/0", "RoW_Service"),
        ("Landbase/TentativeMaps/10", "Tentative_Maps"),
        
        # Additional Landbase layers (check if they exist)
        ("Landbase/MapLayers/0", "Map_Layers"),
    ]
    
    total_records = 0
    results = []
    
    for layer_path, layer_name in layers_to_download:
        count = download_layer(BASE_URL, layer_path, layer_name)
        total_records += count
        results.append({
            'layer': layer_path,
            'name': layer_name,
            'records': count
        })
    
    summary = {
        'scraped_at': datetime.now().isoformat(),
        'base_url': BASE_URL,
        'total_records': total_records,
        'layers': results
    }
    
    summary_file = os.path.join(OUTPUT_DIR, "download_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print("SCRAPING COMPLETE")
    print(f"{'=' * 80}")
    print(f"Total records: {total_records}")
    print(f"Summary: {summary_file}")

if __name__ == "__main__":
    main()
