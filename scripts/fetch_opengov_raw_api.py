import urllib.request
import json
import ssl
import os
import time

out_dir = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
os.makedirs(out_dir, exist_ok=True)

out_file1 = r"C:\OsintNeoAi\data\oc_procurement_raw_api_mapped.json"
out_file2 = os.path.join(out_dir, "oc_procurement_raw_api_mapped.json")

print("Starting high-speed direct JSON API mapping script...")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9"
}

# Base OpenGov API endpoints to map
api_endpoints = [
    "https://procurement.opengov.com/api/v2/projects",
    "https://procurement.opengov.com/api/v1/portals/211273c0-1753-47bb-a90d-025e86f9aec2/projects",
    "https://procurement.opengov.com/api/atlas/v1/county-of-orange-ca/projects"
]

mapped_results = []
for endpoint in api_endpoints:
    for page in range(1, 6): # Probe first 5 pages per endpoint
        url = f"{endpoint}?limit=50&page={page}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    mapped_results.append({
                        "endpoint": url,
                        "page": page,
                        "status": 200,
                        "data_type": type(data).__name__,
                        "count": len(data) if isinstance(data, list) else data.get("totalCount", 0)
                    })
                    print(f"[API HTTP 200 OK] {url}")
        except Exception as e:
            mapped_results.append({
                "endpoint": url,
                "page": page,
                "status": "Fallback / Blocked",
                "error": str(e)
            })

# Save clean structured API map
payload = {
    "script_name": "Direct JSON API Mapper (No-Browser High Speed)",
    "execution_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    "target_portal": "County of Orange Procurement Portal (OpenGov)",
    "mapped_endpoints_count": len(mapped_results),
    "mapped_results": mapped_results
}

with open(out_file1, "w", encoding="utf-8") as fp:
    json.dump(payload, fp, indent=2)

with open(out_file2, "w", encoding="utf-8") as fp:
    json.dump(payload, fp, indent=2)

print(f"Saved direct raw JSON API mapping dataset to {out_file1} and {out_file2}")
