import requests
import json

# Check TaxParcelPublishing layer (FeatureServer 2, Layer 0)
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0'
r = requests.get(url + '?f=json', timeout=30)
if r.status_code == 200:
    data = r.json()
    print('TaxParcelPublishing Fields:')
    for field in data.get('fields', []):
        if any(kw in field['name'].upper() for kw in ['TRACT', 'LOT', 'BLOCK', 'LEGAL', 'MAP', 'BOOK', 'PAGE']):
            print(f'  {field["name"]}: {field["type"]} ({field["alias"]})')

# Query for parcels with TRACT = 405 in any field
url2 = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0/query'
params = {
    'where': "TRACTNUMBER = '405' OR LEGALDESCRIPTION LIKE '%TRACT 405%' OR LEGALDESCRIPTION LIKE '%TR 405%' OR LEGALDESCRIPTION LIKE '%TRCT 405%'",
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326',
    'resultRecordCount': 20
}
r2 = requests.get(url2, params=params, timeout=30)
print(f'\nTract 405 Query Status: {r2.status_code}')
if r2.status_code == 200:
    data = r2.json()
    print(f'Features found: {len(data.get("features", []))}')
    for f in data.get('features', [])[:10]:
        attrs = f.get('attributes', {})
        print(f'  APN: {attrs.get("PARCELID")}, Address: {attrs.get("SITEADDRESS")}, Legal: {attrs.get("LEGALDESCRIPTION", "")[:120]}')
        if 'geometry' in f:
            print(f'  Geometry: {json.dumps(f["geometry"])[:200]}...')

# Also query by the known APNs for HBNC
print('\n=== Query by HBNC APNs ===')
params2 = {
    'where': "PARCELID IN ('167-472-08', '167-472-09')",
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326'
}
r3 = requests.get(url2, params=params2, timeout=30)
print(f'Status: {r3.status_code}')
if r3.status_code == 200:
    data = r3.json()
    print(f'Features found: {len(data.get("features", []))}')
    for f in data.get('features', []):
        attrs = f.get('attributes', {})
        print(f'  APN: {attrs.get("PARCELID")}, Address: {attrs.get("SITEADDRESS")}, Owner: {attrs.get("OWNERNME1")}, Legal: {attrs.get("LEGALDESCRIPTION", "")[:120]}')
        if 'geometry' in f:
            print(f'  Geometry: {json.dumps(f["geometry"])[:300]}...')

# Also try the AssessmentNeighborhoods layer
print('\n=== AssessmentNeighborhoods ===')
url3 = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/AssessmentNeighborhoods/FeatureServer/0/query'
params3 = {
    'where': "1=1",
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326',
    'resultRecordCount': 5
}
r4 = requests.get(url3, params=params3, timeout=30)
print(f'Status: {r4.status_code}')
if r4.status_code == 200:
    data = r4.json()
    print(f'Features: {len(data.get("features", []))}')
    for f in data.get('features', [])[:3]:
        print(f'  {f.get("attributes", {})}')
        if 'geometry' in f:
            print(f'  Geometry: {json.dumps(f["geometry"])[:200]}...')