import requests
import json

# Check all the ArcGIS map services from the endpoint document
services = [
    'https://ocpw.maps.arcgis.com/sharing/rest/content/items/5bbd1fa12e7a43fa8d27a55afa83afa8/data?f=json',
    'https://ocpw.maps.arcgis.com/sharing/rest/content/items/cec066dcef964bdd8636ec05f9408a7a/data?f=json',
    'https://ocpw.maps.arcgis.com/sharing/rest/content/items/cc8ebdb51c36432aa421bd4ccfc0e7fd/data?f=json',
    'https://ocpw.maps.arcgis.com/sharing/rest/content/items/323e1b6ae02746bca659ca98ebc2435a/data?f=json',
]

for i, url in enumerate(services):
    try:
        r = requests.get(url, timeout=30)
        print(f'\n=== Service {i+1} ===')
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            if 'operationalLayers' in data:
                print(f'Operational Layers:')
                for layer in data['operationalLayers']:
                    print(f'  Title: {layer.get("title")}, ID: {layer.get("id")}, URL: {layer.get("url")}')
            if 'layers' in data:
                print(f'Layers:')
                for layer in data.get('layers', []):
                    print(f'  {layer.get("id")}: {layer.get("name")}')
    except Exception as e:
        print(f'Error: {e}')

# Also try the FeatureServer endpoints directly
feature_services = [
    'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/OCPW_Parcels/FeatureServer?f=json',
    'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/TaxParcelQuery/FeatureServer?f=json',
    'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/AssessmentNeighborhoods/FeatureServer?f=json',
    'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/AssessmentAppeals/FeatureServer?f=json',
]

for i, url in enumerate(feature_services):
    try:
        r = requests.get(url, timeout=30)
        print(f'\n=== FeatureService {i+1} ===')
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            if 'services' in data:
                for svc in data['services']:
                    print(f'  {svc["name"]} ({svc["type"]})')
            if 'layers' in data:
                for layer in data.get('layers', []):
                    print(f'  Layer {layer["id"]}: {layer["name"]}')
    except Exception as e:
        print(f'Error: {e}')