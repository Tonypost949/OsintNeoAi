import requests
import json

# Try querying the FeatureServer layers directly without geometry
# Get the TaxParcelQuery layer definition
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0'
r = requests.get(url + '?f=json', timeout=30)
if r.status_code == 200:
    data = r.json()
    print('TaxParcelPublishing Layer Info:')
    print(f'  Name: {data.get("name")}')
    print(f'  Type: {data.get("type")}')
    print(f'  Description: {data.get("description")}')
    print(f'  Default Visibility: {data.get("defaultVisibility")}')
    print(f'  Max Record Count: {data.get("maxRecordCount")}')
    print(f'  Supported Query Formats: {data.get("supportedQueryFormats")}')
    print(f'  Capabilities: {data.get("capabilities")}')
    print(f'  Has Geometry: {data.get("geometryType")}')
    print(f'  Spatial Reference: {data.get("spatialReference")}')
    print(f'  Fields Count: {len(data.get("fields", []))}')

# Try to query using the ArcGIS REST API with a token-less approach
# Try using the public query endpoint
print('\n=== Trying broad query on TaxParcelPublishing ===')
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0/query'
params = {
    'where': 'OBJECTID > 0',
    'outFields': 'PARCELID,SITEADDRESS,LEGALDESCRIPTION,OWNERNME1,TRACTNUMBER',
    'f': 'json',
    'returnGeometry': 'false',
    'resultRecordCount': 10
}
r = requests.get(url, params=params, timeout=30)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Features: {len(data.get("features", []))}')
    for f in data.get('features', [])[:5]:
        print(f'  {f.get("attributes", {})}')

# If that fails, try the item data endpoint for the OC Public Works maps
print('\n=== Checking OC Public Works map items ===')
map_items = [
    '5bbd1fa12e7a43fa8d27a55afa83afa8',  # OC Construction Projects
    'cec066dcef964bdd8636ec05f9408a7a',  # Map 2
    'cc8ebdb51c36432aa421bd4ccfc0e7fd',  # Map 3
    '323e1b6ae02746bca659ca98ebc2435a',  # Map 4
]

for item_id in map_items:
    url = f'https://ocpw.maps.arcgis.com/sharing/rest/content/items/{item_id}/data?f=json'
    try:
        r = requests.get(url, timeout=30)
        print(f'\nItem {item_id}: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            if 'operationalLayers' in data:
                for layer in data['operationalLayers']:
                    print(f'  Layer: {layer.get("title")} - {layer.get("url")}')
    except Exception as e:
        print(f'Error: {e}')