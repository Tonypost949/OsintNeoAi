"""test_maps_open_live.py — Automated Verification of Open Map Services
"""
import requests
import time

TARGETS = [
    {"name": "Global Domain Map", "url": "http://osintneoai.me/"},
    {"name": "Hercules Cloud Hub", "url": "https://osintneoai.onhercules.app/"},
    {"name": "Azure Public Cloud", "url": "http://57.152.82.43:10000/"},
    {"name": "Local High-Speed Port 9999", "url": "http://localhost:9999/index.html"}
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("=" * 70)
print("🗺️ TESTING ALL OPEN LIVE MAP SERVICES & SCRIPT INTEGRITY")
print("=" * 70)

for t in TARGETS:
    name = t["name"]
    url = t["url"]
    try:
        t0 = time.time()
        resp = requests.get(url, headers=headers, timeout=8)
        dur = round((time.time() - t0) * 1000)
        status = resp.status_code
        size = len(resp.content)
        
        # Check key components
        has_leaflet = "leaflet" in resp.text.lower() or "map" in resp.text.lower()
        has_drone = "autopilot" in resp.text.lower() or "flight" in resp.text.lower()
        
        icon = "🟢" if status == 200 else "🔴"
        print(f"{icon} {name:<26} | HTTP {status} | {dur:>4}ms | {size:>6} bytes | Map Engine: {'✅' if has_leaflet else '⚠️'}")
    except Exception as e:
        print(f"🔴 {name:<26} | ERROR: {str(e)[:45]}")

print("=" * 70)
