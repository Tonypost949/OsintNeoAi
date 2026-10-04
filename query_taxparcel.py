import requests
import json

# Query the TaxParcelPublishing layer
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0/query'
params = {
    'where': "APN IN ('167-472-08', '167-472-09')",
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true'
}
r = requests.get(url, params=params, timeout=30)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Features: {len(data.get("features", []))}')
    for f in data.get('features', []):
        print(json.dumps(f.get('attributes', {}), indent=2))
        if 'geometry' in f:
            print(f'Geometry: {json.dumps(f["geometry"])}')

# Also try searching by address
params2 = {
    'where': "SITEADDRESS LIKE '%17631%CAMERON%' OR SITEADDRESS LIKE '%17642%BEACH%'",
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true'
}
r2 = requests.get('https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0/query', params=params2, timeout=30)
print(f'\nSearch by address - Status: {r2.status_code}')
if r2.status_code == 200:
    data = r2.json()
    print(f'Features: {len(r2.json().get("features", []))}')
    for f in r2.json().get('features', [])[:5]:
        print(json.dumps(f.get('attributes', {}), indent=2))