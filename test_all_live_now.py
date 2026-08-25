import urllib.request
import time

endpoints = [
    ("Local 3D Master Map", "http://127.0.0.1:10000/map/master"),
    ("Local 3D Tilt View", "http://127.0.0.1:10000/map/3d"),
    ("Local Swipe Mode", "http://127.0.0.1:10000/map/swipe"),
    ("Local Google Earth KML", "http://127.0.0.1:10000/map/kml"),
    ("Local HBNC Parcel Map", "http://127.0.0.1:10000/map/hbnc"),
    ("Local Chain of Custody", "http://127.0.0.1:10000/map/coc"),
    ("Local Money Pipeline", "http://127.0.0.1:10000/map/pipeline"),
    ("Local Health Check", "http://127.0.0.1:10000/health"),
    ("Azure Public Cloud (Port 10000)", "http://57.152.82.43:10000/"),
    ("Hercules Cloud Hub", "https://osintneoai.onhercules.app/"),
    ("Global Domain Map", "http://osintneoai.me/")
]

print("=" * 80)
print("🧪 REAL-TIME COMPREHENSIVE ENDPOINT AUDIT & VERIFICATION")
print("=" * 80)

for name, url in endpoints:
    try:
        t0 = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=5)
        dur = round((time.time() - t0) * 1000)
        data = resp.read()
        size = len(data)
        status = resp.status
        print(f"🟢 {name:<32} | HTTP {status} | {dur:>4}ms | {size:>7} bytes | URL: {url}")
    except Exception as e:
        print(f"🔴 {name:<32} | ERROR: {str(e)[:40]} | URL: {url}")

print("=" * 80)
