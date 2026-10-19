import json
import os
import time
import urllib.request
import concurrent.futures
from datetime import datetime

def fetch_url(url):
    start = time.time()
    try:
        req = urllib.request.urlopen(url, timeout=5)
        content = req.read()
        latency = round((time.time() - start) * 1000, 2)
        return {"status": req.status, "bytes": len(content), "latency_ms": latency, "success": True}
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        return {"status": "ERROR", "error": str(e), "latency_ms": latency, "success": False}

def run_stress_test():
    urls = [
        ("User Landing & Chat", "http://localhost:8095/"),
        ("Admin Backend", "http://localhost:8095/admin"),
        ("Full Developer Environment", "http://localhost:8095/dev")
    ]

    total_requests_per_endpoint = 50
    results = {}

    for name, url in urls:
        print(f"[*] Stress testing {name} ({url}) with {total_requests_per_endpoint} concurrent requests...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_url, url) for _ in range(total_requests_per_endpoint)]
            res_list = [f.result() for f in concurrent.futures.as_completed(futures)]

        successes = [r for r in res_list if r["success"]]
        latencies = [r["latency_ms"] for r in successes]

        avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else 0
        min_lat = min(latencies) if latencies else 0
        max_lat = max(latencies) if latencies else 0

        results[name] = {
            "target_url": url,
            "total_sent": total_requests_per_endpoint,
            "total_successful": len(successes),
            "success_rate": f"{round((len(successes)/total_requests_per_endpoint)*100, 2)}%",
            "latency_avg_ms": avg_lat,
            "latency_min_ms": min_lat,
            "latency_max_ms": max_lat
        }

    report_payload = {
        "status": "COMPLETED",
        "tested_at": datetime.now().isoformat(),
        "total_requests_executed": len(urls) * total_requests_per_endpoint,
        "results": results
    }

    out_v1 = r"C:\Amd949609_Antigravity_v1\docs\STRESS_TEST_REPORT.json"
    out_repo = r"C:\OsintNeoAi\reports\STRESS_TEST_REPORT.json"

    os.makedirs(os.path.dirname(out_v1), exist_ok=True)
    os.makedirs(os.path.dirname(out_repo), exist_ok=True)

    with open(out_v1, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)

    with open(out_repo, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)

    print(f"Stress test complete. Saved report to:\n- {out_v1}\n- {out_repo}")

if __name__ == "__main__":
    run_stress_test()
