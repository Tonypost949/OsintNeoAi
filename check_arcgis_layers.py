import requests
url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/OCPW_Parcels/FeatureServer'
r = requests.get(url + '?f=json', timeout=30)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print('Layers:')
    for layer in data.get('layers', []):
        print(f'  {layer["id"]}: {layer["name"]}')