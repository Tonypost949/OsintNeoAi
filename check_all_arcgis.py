import requests
import json

urls = [
    'https://ocpw.maps.arcgis.com/sharing/rest/content/items/5bbd1fa12e7a43fa8d27a55afa83afa8/data?f=json',
    'https://ocpw.maps.arcgis.com/sharing/rest/content/items/cec066dcef964bdd8636ec05f9408a7a/data?f=json',
    'https://ocpw.maps.arcgis.com/sharing/rest/content/items/cc8ebdb51c36432aa421bd4ccfc0e7fd/data?f=json',
    'https://ocpw.maps.arcgis.com/sharing/rest/content/items/323e1b6ae02746bca659ca98ebc2435a/data?f=json',
    'https://www.ocgis.com/ocpw/pavementcondition/?f=json',
]

for url in urls:
    try:
        r = requests.get(url + '?f=json', timeout=30)
        print(f'{url}: {r.status_code}')
        if r.status_code == 200:
            try:
                data = r.json()
                if 'layers' in data:
                    for layer in data.get('layers', []):
                        print(f'  Layer: {layer.get("name", "N/A")}')
                elif 'operationalLayers' in data:
                    for layer in data.get('operationalLayers', []):
                        print(f'  OpLayer: {layer.get("title", layer.get("id", "N/A"))}')
            except:
                pass
    except Exception as e:
        print(f'Error: {e}')