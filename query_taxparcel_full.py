import requests
import json

# Get all records from TaxParcelPublishing (first 100)
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0/query'
params = {
    'where': '1=1',
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326',
    'resultRecordCount': 100
}
r = requests.get(url, params=params, timeout=60)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Features found: {len(data.get("features", []))}')
    for f in data.get('features', [])[:20]:
        attrs = f.get('attributes', {})
        # Check for any tract/lot info in any field
        tract_info = {k: v for k, v in attrs.items() if 'tract' in k.lower() or 'lot' in k.lower() or 'block' in k.lower() or 'legal' in k.lower() or 'map' in k.lower() or 'book' in k.lower() or 'page' in k.lower()}
        if tract_info:
            print(f'  APN: {attrs.get("PARCELID")}, Address: {attrs.get("SITEADDRESS")}, TractInfo: {tract_info}')
        if 'geometry' in f:
            geom = f['geometry']
            if 'rings' in geom:
                print(f'  Geometry rings: {len(geom["rings"])} ring(s)')

# Also try to query the OCPW_Parcels service with a broader search
print('\n=== Trying OCPW_Parcels with spatial query ===')
url2 = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/OCPW_Parcels/FeatureServer/0/query'
params2 = {
    'geometry': '-117.9881801,33.7064036',
    'geometryType': 'esriGeometryPoint',
    'inSR': '4326',
    'spatialRel': 'esriSpatialRelIntersects',
    'distance': 1000,
    'units': 'esriSRUnit_Foot',
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326',
    'resultRecordCount': 50
}
r2 = requests.get('https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/OCPW_Parcels/FeatureServer/0/query', params=params2, timeout=60)
print(f'Status: {r2.status_code}')
if r2.status_code == 200:
    data = r2.json()
    print(f'Features found: {len(data.get("features", []))}')
    for f in data.get('features', [])[:10]:
        attrs = f.get('attributes', {})
        print(f'  APN: {attrs.get("PARCELID")}, Address: {attrs.get("SITEADDRESS")}, Owner: {attrs.get("OWNERNME1")}')

# Also try the AssessmentNeighborhoods layer properly
print('\n=== AssessmentNeighborhoods - full query ===')
url3 = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/AssessmentNeighborhoods/FeatureServer/0/query'
params3 = {
    'where': '1=1',
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'true',
    'outSR': '4326',
    'resultRecordCount': 50
}
r3 = requests.get(url3, params=params3, timeout=60)
print(f'Status: {r3.status_code}')
if r3.status_code == 200:
    data = r3.json()
    print(f'Features: {len(data.get("features", []))}')
    for f in data.get('features', [])[:5]:
        attrs = f.get('attributes', {})
        print(f'  {attrs}')
        if 'geometry' in f:
            print(f'  Geometry: {json.dumps(f["geometry"])[:200]}...')