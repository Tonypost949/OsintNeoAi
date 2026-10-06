import requests
import json

# Check OCPW_Parcels service fields
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/OCPW_Parcels/FeatureServer/0'
r = requests.get(url + '?f=json', timeout=30)
if r.status_code == 200:
    data = r.json()
    print('OCPW_Parcels Fields:')
    for field in data.get('fields', []):
        print(f'  {field["name"]}: {field["type"]} ({field["alias"]})')

# Get some sample records to understand the data structure
url2 = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/OCPW_Parcels/FeatureServer/0/query'
params2 = {
    'where': '1=1',
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'false',
    'resultRecordCount': 5
}
r2 = requests.get(url2, params=params2, timeout=30)
if r2.status_code == 200:
    data = r2.json()
    print(f'\nSample records: {len(data.get("features", []))}')
    for f in data.get('features', []):
        attrs = f.get('attributes', {})
        print(f'  {attrs}')

# Also try to find parcels near 17631 Cameron / 17642 Beach Blvd
url3 = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/OCPW_Parcels/FeatureServer/0/query'
params3 = {
    'geometry': '-117.9881801,33.7064036',
    'geometryType': 'esriGeometryPoint',
    'inSR': '4326',
    'spatialRel': 'esriSpatialRelIntersects',
    'distance': 500,
    'units': 'esriSRUnit_Foot',
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326'
}
r3 = requests.get(url3, params=params3, timeout=30)
print(f'\nSpatial Query Status: {r3.status_code}')
if r3.status_code == 200:
    data = r3.json()
    print(f'Features found: {len(data.get("features", []))}')
    for f in data.get('features', [])[:10]:
        attrs = f.get('attributes', {})
        print(f'  APN: {attrs.get("PARCELID")}, Address: {attrs.get("SITEADDRESS")}, Owner: {attrs.get("OWNERNME1")}')
        if 'geometry' in f:
            print(f'  Geometry: {json.dumps(f["geometry"])[:200]}...')