import requests
import json
import os
from datetime import datetime

BASE_URL = "https://www.ocgis.com/survey/rest/services"
OUTPUT_DIR = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\oc_land_insights"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_service_info(base_url, service_path):
    url = f"{base_url}/{service_path}?f=json"
    resp = requests.get(url, timeout=30)
    return resp.json()

def get_layers(base_url, service_path):
    info = get_service_info(base_url, service_path)
    layers = info.get('layers', [])
    return layers

def query_feature_layer(base_url, service_path, layer_id, where="1=1", out_fields="*", result_offset=0, result_count=1000):
    url = f"{base_url}/{service_path}/{layer_id}/query"
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

def download_feature_layer(base_url, service_path, layer_id, layer_name, max_records=10000):
    print(f"\nDownloading: {layer_name} (Layer {layer_id})")
    
    all_features = []
    offset = 0
    batch_size = 1000
    
    while offset < max_records:
        try:
            data = query_feature_layer(base_url, service_path, layer_id, 
                                       result_offset=offset, 
                                       result_count=batch_size)
            
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
    
    output_file = os.path.join(OUTPUT_DIR, f"{layer_name.replace('/', '_')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'service': service_path,
            'layer_id': layer_id,
            'layer_name': layer_name,
            'record_count': len(all_features),
            'downloaded_at': datetime.now().isoformat(),
            'features': all_features
        }, f, indent=2)
    
    print(f"  Saved {len(all_features)} records to {output_file}")
    return all_features

def main():
    print("=" * 80)
    print("OC LAND INSIGHTS DATA SCRAPER")
    print("=" * 80)
    
    services_to_scrape = [
        ("OCLandInsights", "Geodetic"),
        ("OCLandInsights", "UsageTracking_Table"),
        ("Landbase", "Landbase_Lines"),
        ("Landbase", "RoWService"),
        ("Landbase", "TentativeMaps"),
    ]
    
    results = {}
    
    for folder, service_name in services_to_scrape:
        service_path = f"{folder}/{service_name}"
        print(f"\n{'=' * 60}")
        print(f"Processing: {service_path}")
        print(f"{'=' * 60}")
        
        try:
            layers = get_layers(BASE_URL, service_path)
            print(f"Found {len(layers)} layers")
            
            for layer in layers:
                layer_id = layer['id']
                layer_name = layer['name']
                
                features = download_feature_layer(BASE_URL, service_path, layer_id, layer_name)
                
                if service_path not in results:
                    results[service_path] = []
                results[service_path].append({
                    'layer_id': layer_id,
                    'layer_name': layer_name,
                    'record_count': len(features)
                })
                
        except Exception as e:
            print(f"Error processing {service_path}: {e}")
    
    summary_file = os.path.join(OUTPUT_DIR, "download_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'scraped_at': datetime.now().isoformat(),
            'base_url': BASE_URL,
            'services': results
        }, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print("SCRAPING COMPLETE")
    print(f"{'=' * 80}")
    print(f"Summary saved to: {summary_file}")
    
    total_records = sum(
        sum(layer['record_count'] for layer in layers)
        for layers in results.values()
    )
    print(f"Total records downloaded: {total_records}")

if __name__ == "__main__":
    main()
