import requests
import json

# Query ArcGIS for Tract 405 parcel geometry
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/OCPW_Parcels/FeatureServer'
r = requests.get(url + '?f=json', timeout=30)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print('Layers:')
    for layer in data.get('layers', []):
        print(f'  {layer["id"]}: {layer["name"]}')

# Try the TaxParcelQuery service which has the parcel data
url2 = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0/query'
params = {
    'where': "TRACTNUMBER = '405'",
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326'
}
r2 = requests.get(url2, params=params, timeout=30)
print(f'\nTract 405 Query Status: {r2.status_code}')
if r2.status_code == 200:
    data = r2.json()
    print(f'Features found: {len(data.get("features", []))}')
    for f in data.get('features', [])[:5]:
        attrs = f.get('attributes', {})
        print(f'  APN: {attrs.get("PARCELID")}, Address: {attrs.get("SITEADDRESS")}, Tract: {attrs.get("TRACTNUMBER")}')
        if 'geometry' in f:
            print(f'  Geometry: {json.dumps(f["geometry"])[:200]}...')