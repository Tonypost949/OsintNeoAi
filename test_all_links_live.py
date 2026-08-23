"""test_all_links_live.py — Comprehensive Live HTTP Health Audit (Cleaned Regex)
Extracts every URL across repository markdown docs and verifies live HTTP status.
"""

import re
import time
import requests
from pathlib import Path

FILES_TO_CHECK = [
    Path("README.md"),
    Path("reports/EDR_LIGHTBOX_MASTER_ASSET_INDEX.md")
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_urls(file_path):
    if not file_path.exists():
        return []
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    # Match clean http/https URLs
    raw_urls = re.findall(r'https?://[^\s\)\"\]\`\<\>]+', content)
    clean_urls = []
    for u in set(raw_urls):
        u = u.rstrip(".,;:)'\"`]>")
        if u and not u.endswith("/v1/parcels/us`"):
            clean_urls.append(u)
    return clean_urls

def test_url(url):
    try:
        start = time.time()
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        dur = round(time.time() - start, 2)
        # HTTP 200, 301, 302, 401 (active endpoint requiring auth), 403 (Cloudflare/WAF block but live)
        is_live = resp.status_code in [200, 301, 302, 307, 308, 401, 403]
        return {"status": resp.status_code, "ok": is_live, "duration": dur, "error": None}
    except Exception as e:
        return {"status": "ERR", "ok": False, "duration": 0, "error": str(e)[:80]}

def main():
    print("=" * 75)
    print("🌐 EXECUTING LIVE HTTP LINK AUDIT ACROSS ALL REPOSITORY ASSETS")
    print("=" * 75)

    all_urls = set()
    for f in FILES_TO_CHECK:
        found = extract_urls(f)
        all_urls.update(found)

    sorted_urls = sorted(list(all_urls))
    print(f"[*] Total Clean Unique URLs to Live Test: {len(sorted_urls)}\n")

    results = []
    for i, url in enumerate(sorted_urls, 1):
        res = test_url(url)
        status_sym = "🟢 LIVE" if res["ok"] else "🔴 DOWN"
        print(f"[{i:02d}/{len(sorted_urls)}] {status_sym} (HTTP {res['status']}, {res['duration']}s) -> {url[:60]}")
        results.append({
            "url": url,
            "status": res["status"],
            "ok": res["ok"],
            "duration": res["duration"],
            "error": res["error"]
        })
        time.sleep(0.15)

    # Generate Report
    report_lines = [
        "# 🌐 Comprehensive Live Link Health & Verification Audit",
        f"**Audit Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Total Tested Endpoints:** {len(results)}",
        f"**Live & Reachable:** {sum(1 for r in results if r['ok'])}",
        f"**Failed / Unreachable:** {sum(1 for r in results if not r['ok'])}",
        "",
        "## I. Live Verified Endpoints Matrix",
        "",
        "| Status | HTTP Code | Response Time | URL / Target Link |",
        "| :--- | :--- | :--- | :--- |"
    ]

    for r in results:
        sym = "🟢 LIVE" if r["ok"] else "🔴 CHECK"
        report_lines.append(f"| {sym} | **HTTP {r['status']}** | {r['duration']}s | [{r['url']}]({r['url']}) |")

    report_path = Path("reports/LIVE_LINK_HEALTH_AUDIT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"\n[+] Master Live Audit Report written: {report_path}")
    print("=" * 75)

if __name__ == "__main__":
    main()
