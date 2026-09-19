import urllib.request

routes = [
    "/map/master",
    "/map/3d",
    "/map/swipe",
    "/map/kml",
    "/map/badass",
    "/map/hbnc",
    "/map/coc",
    "/map/pipeline",
    "/health"
]

print("=" * 60)
print("🗺️ VERIFYING ALL LIVE MAP ROUTES ON PORT 10000")
print("=" * 60)

for r in routes:
    url = f"http://127.0.0.1:10000{r}"
    try:
        resp = urllib.request.urlopen(url, timeout=2)
        print(f"🟢 {r:<18} -> HTTP {resp.status} ({len(resp.read())} bytes)")
    except Exception as e:
        print(f"🔴 {r:<18} -> ERROR: {e}")

print("=" * 60)
