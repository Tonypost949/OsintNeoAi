import urllib.request
import json

api_key = "AIzaSyBc2q4I5fbjLFCM8q-lR-H_-lrJwbxGh9Q"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

print("Calling ListModels to inspect key capabilities...")
try:
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req) as response:
        res_data = response.read().decode('utf-8')
        res_json = json.loads(res_data)
        print("\n--- VISIBLE MODELS ---")
        models = [m['name'] for m in res_json.get('models', [])]
        print(models if models else "No models listed.")
        print("----------------------")
except Exception as e:
    print(f"\n--- ERROR DETAILS ---")
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8').strip())
    else:
        print(type(e).__name__, ":", e)
    print("----------------------")
