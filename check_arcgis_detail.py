import requests
import json

# Check the first map item in detail
url = 'https://ocpw.maps.arcgis.com/sharing/rest/content/items/5bbd1fa12e7a43fa8d27a55afa83afa8/data?f=json'
r = requests.get(url, timeout=30)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:5000])