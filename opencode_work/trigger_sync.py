"""
Trigger sync to local Flask webhook
Usage: python trigger_sync.py
"""
import urllib.request, json

url = "http://127.0.0.1:5000/api/sync"
data = json.dumps({}).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"Sync triggered! Response: {resp.status}")
        print(resp.read().decode())
except Exception as e:
    print(f"Error: {e}")
    print("Is the Flask server running? Try: python app.py")
