import requests
import json

url = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services'
r = requests.get(url + '?f=json', timeout=30)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print('Services:')
    for service in data.get('services', []):
        print(f'  {service["name"]} ({service["type"]})')