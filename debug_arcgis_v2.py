import requests
import json

# Check the OC Public Works map items in detail to find parcel layers
map_items = [
    ('5bbd1fa12e7a43fa8d27a55afa83afa8', 'OC Construction Projects'),
    ('cec066dcef964bdd8636ec05f9408a7a', 'Map 2'),
    ('cc8ebdb51c36432aa421bd4ccfc0e7fd', 'Map 3'),
    ('323e1b6ae02746bca659ca98ebc2435a', 'Map 4'),
]

for item_id, name in map_items:
    url = f'https://ocpw.maps.arcgis.com/sharing/rest/content/items/{item_id}/data?f=json'
    try:
        r = requests.get(url, timeout=30)
        print(f'\n=== {name} ({item_id}) ===')
        if r.status_code == 200:
            data = r.json()
            if 'operationalLayers' in data:
                print(f'Operational Layers ({len(data["operationalLayers"])}):')
                for layer in data['operationalLayers']:
                    print(f'  Title: {layer.get("title")}')
                    print(f'  ID: {layer.get("id")}')
                    print(f'  URL: {layer.get("url")}')
                    print(f'  Visibility: {layer.get("visibility")}')
                    if 'layerType' in layer:
                        print(f'  Type: {layer["layerType"]}')
    except Exception as e:
        print(f'Error: {e}')

# Also try to query the ArcGIS Online item for the TaxParcelQuery service directly
print('\n=== Trying TaxParcelQuery service item ===')
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer?f=json'
r = requests.get(url, timeout=30)
if r.status_code == 200:
    data = r.json()
    if 'services' in data:
        for svc in data['services']:
            print(f'Service: {svc["name"]} - {svc["type"]}')

# Try to access the actual data through the ArcGIS REST API with a different approach
print('\n=== Trying to export TaxParcelPublishing data ===')
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0'
params = {
    'where': '1=1',
    'outFields': 'PARCELID,SITEADDRESS,LEGALDESCRIPTION,OWNERNME1,TRACTNUMBER,MAPBOOK,MAPPAGE',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326',
    'resultRecordCount': 5
}
r = requests.get(url + '/query', params=params, timeout=30)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Features: {len(data.get("features", []))}')
    for f in data.get('features', [])[:3]:
        print(f'  {f.get("attributes", {})}')
        if 'geometry' in f:
            print(f'  Geometry: {json.dumps(f["geometry"])[:200]}...')