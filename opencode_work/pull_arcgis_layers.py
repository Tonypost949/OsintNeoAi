import urllib.request, json, os, csv

out_dir = r'C:\Users\HP\OneDrive\Documents\opencode_work\arcgis_exports'
os.makedirs(out_dir, exist_ok=True)

layers = [
    ('Property', 0, 'HB_Properties'),
    ('Parcels', 0, 'HB_Parcels'),
    ('SurfaceFlow', 0, 'HB_SurfaceFlow'),
    ('Business', 0, 'HB_Business'),
    ('Planning', 0, 'HB_Planning'),
    ('CityFacilities', 0, 'HB_CityFacilities'),
    ('SewerLayers', 0, 'HB_Sewer'),
    ('StormLayers', 0, 'HB_Storm'),
    ('WaterBroadcast', 0, 'HB_Water'),
    ('WebAddresses', 0, 'HB_Addresses'),
]

base_url = 'https://gis.huntingtonbeachca.gov/arcgis/rest/services'

for service, layer_id, name in layers:
    try:
        url = f'{base_url}/{service}/MapServer/{layer_id}/query'
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'json',
            'resultRecordCount': 100,
            'resultOffset': 0,
            'returnGeometry': 'false'
        }
        
        all_features = []
        offset = 0
        
        while True:
            params['resultOffset'] = offset
            query = '&'.join([f'{k}={v}' for k, v in params.items()])
            full_url = f'{url}?{query}'
            
            req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            
            features = data.get('features', [])
            if not features:
                break
            
            all_features.extend(features)
            offset += 100
            print(f'{name}: pulled {len(all_features)} records (offset {offset})')
            
            if len(all_features) > 5000:
                break
        
        if all_features:
            # Save as JSON
            json_path = os.path.join(out_dir, f'{name}.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(all_features, f, indent=2)
            
            # Also save as CSV
            attrs = [feat.get('attributes', {}) for feat in all_features]
            if attrs:
                csv_path = os.path.join(out_dir, f'{name}.csv')
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=attrs[0].keys())
                    writer.writeheader()
                    writer.writerows(attrs)
            
            print(f'  Saved {name}.json ({len(all_features)} records)')
            print(f'  Saved {name}.csv')
        else:
            print(f'  {name}: no data')
    
    except Exception as e:
        print(f'  {name}: ERROR - {e}')

print('Done pulling ArcGIS layers')
