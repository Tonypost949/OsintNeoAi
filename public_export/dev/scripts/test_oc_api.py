import requests
import json

url = "https://www.ocgis.com/survey/rest/services/Landbase/TentativeMaps/FeatureServer/10/query"
params = {"where": "1=1", "outFields": "*", "resultRecordCount": 10, "f": "json"}
resp = requests.get(url, params=params, timeout=30)
data = resp.json()
features = data.get("features", [])
print("Features:", len(features))
print("Exceeded limit:", data.get("exceededTransferLimit", False))
if features:
    print("First record attributes:")
    print(json.dumps(features[0]["attributes"], indent=2)[:500])
