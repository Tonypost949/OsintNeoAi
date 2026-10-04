import requests
import json

# Check the layer fields
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0'
r = requests.get(url + '?f=json', timeout=30)
if r.status_code == 200:
    data = r.json()
    print('Fields:')
    for field in data.get('fields', []):
        print(f'  {field["name"]}: {field["type"]} ({field["alias"]})')

# Try a broader search - get some records to see the field values
params = {
    'where': '1=1',
    'outFields': '*',
    'f': 'json',
    'returnGeometry': 'false',
    'resultRecordCount': 5
}
r = requests.get('https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer/0/query', params=params, timeout=30)
if r.status_code == 200:
    data = r.json()
    print(f'\nSample records: {len(data.get("features", []))}')
    for f in data.get('features', []):
        print(json.dumps(f.get('attributes', {}), indent=2))