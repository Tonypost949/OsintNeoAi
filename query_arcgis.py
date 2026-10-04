import requests
import json

# Try the feature layer directly
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/OCPW_Parcels/FeatureServer/0/query'
params = {
    'where': "SITEADDRESS LIKE '%17631%CAMERON%' OR SITEADDRESS LIKE '%17642%BEACH%'",
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true'
}
r = requests.get(url, params=params, timeout=30)
print(f'ArcGIS Query: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Features: {len(data.get("features", []))}')
    for f in data.get('features', [])[:5]:
        print(json.dumps(f.get('attributes', {}), indent=2))

# Also try searching by APN
params2 = {
    'where': "APN IN ('167-472-08', '167-472-09')",
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true'
}
r2 = requests.get(url, params=params2, timeout=30)
print(f'ArcGIS Query by APN: {r2.status_code}')
if r2.status_code == 200:
    data = r2.json()
    print(f'Features: {len(data.get("features", []))}')
    for f in data.get('features', []):
        print(json.dumps(f.get('attributes', {}), indent=2))