import requests
import json

# Check the TaxParcelQuery layer fields
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0'
r = requests.get(url + '?f=json', timeout=30)
if r.status_code == 200:
    data = r.json()
    print('Fields:')
    for field in data.get('fields', []):
        if 'tract' in field['name'].lower() or 'lot' in field['name'].lower() or 'block' in field['name'].lower():
            print(f'  {field["name"]}: {field["type"]} ({field["alias"]})')

# Try querying by legal description or other fields
url2 = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0/query'
params = {
    'where': "LEGALDESCRIPTION LIKE '%TR 405%' OR LEGALDESCRIPTION LIKE '%TRACT 405%' OR LEGALDESCRIPTION LIKE '%TRCT 405%'",
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326'
}
r2 = requests.get(url2, params=params, timeout=30)
print(f'\nLegal Description Query Status: {r2.status_code}')
if r2.status_code == 200:
    data = r2.json()
    print(f'Features found: {len(data.get("features", []))}')
    for f in data.get('features', [])[:5]:
        attrs = f.get('attributes', {})
        print(f'  APN: {attrs.get("PARCELID")}, Address: {attrs.get("SITEADDRESS")}, Legal: {attrs.get("LEGALDESCRIPTION", "")[:100]}')
        if 'geometry' in f:
            print(f'  Geometry: {json.dumps(f["geometry"])[:200]}...')

# Also try the OCPW_Parcels service
url3 = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/OCPW_Parcels/FeatureServer/0/query'
params3 = {
    'where': "TRACT = '405' OR TRACTNUMBER = '405' OR LEGALDESC LIKE '%405%'",
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326'
}
r3 = requests.get(url3, params=params3, timeout=30)
print(f'\nOCPW_Parcels Query Status: {r3.status_code}')
if r3.status_code == 200:
    data = r3.json()
    print(f'Features found: {len(data.get("features", []))}')
    for f in data.get('features', [])[:5]:
        attrs = f.get('attributes', {})
        print(f'  {attrs}')
        if 'geometry' in f:
            print(f'  Geometry: {json.dumps(f["geometry"])[:200]}...')