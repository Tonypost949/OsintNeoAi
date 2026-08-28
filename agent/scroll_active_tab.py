"""
scroll_active_tab.py — Connects to the active browser tab via Kimi WebBridge,
scrolls down repeatedly to trigger dynamic loading of ALL photos,
and extracts all photo links and images into JSON.
"""
import requests
import json
import time
import os
import sys

DAEMON_URL = "http://127.0.0.1:10086/command"
SESSION_NAME = "active-tab-scroll"

def cmd(action, args=None):
    if args is None:
        args = {}
    payload = {"action": action, "args": args, "session": SESSION_NAME}
    try:
        r = requests.post(DAEMON_URL, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    out_file = sys.argv[1] if len(sys.argv) > 1 else "data/active_tab_photos.json"

    print("[*] Connecting to current active tab in Chrome via WebBridge...", flush=True)
    tab_info = cmd("find_tab", {"active": True})
    print(f"[+] Active Tab: {tab_info}", flush=True)

    print("[*] Reading page URL and initial state...", flush=True)
    state = cmd("evaluate", {"code": "(() => ({ url: window.location.href, title: document.title, photos: document.querySelectorAll('a[href*=\"/photo/\"]').length }))()"})
    print(f"[+] Page State: {state.get('value')}", flush=True)

    print("[*] Starting scroll loop (scrolling 40 times)...", flush=True)
    last_count = 0
    stable_rounds = 0

    for i in range(1, 60):
        res = cmd("evaluate", {
            "code": """
            (() => {
                window.scrollBy(0, 4000);
                const items = document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"]');
                return {
                    count: items.length,
                    scrollHeight: document.body.scrollHeight,
                    scrollY: window.scrollY || window.pageYOffset
                };
            })()
            """
        })
        val = res.get("value", {}) if isinstance(res.get("value"), dict) else {}
        cnt = val.get("count", 0)
        print(f"  [Step #{i}] Rendered Photos in DOM: {cnt} (ScrollY: {val.get('scrollY')})", flush=True)

        if cnt == last_count and cnt > 0:
            stable_rounds += 1
            if stable_rounds >= 5:
                print(f"[+] No more new photos loading (Count: {cnt}). Reached bottom.", flush=True)
                break
        else:
            stable_rounds = 0
            last_count = cnt

        time.sleep(1.5)

    print("\n[*] Extracting all photo links and image sources from DOM...", flush=True)
    extract_code = """
    (() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"]'));
        const seen = new Set();
        const results = [];
        for (let a of anchors) {
            const href = a.href;
            if (!seen.has(href)) {
                seen.add(href);
                const img = a.querySelector('img');
                const src = img ? (img.src || img.getAttribute('src')) : null;
                const aria = a.getAttribute('aria-label') || '';
                results.push({
                    href: href,
                    image_url: src,
                    aria_label: aria
                });
            }
        }
        return results;
    })()
    """
    final_res = cmd("evaluate", {"code": extract_code})
    items = final_res.get("value", []) if isinstance(final_res.get("value"), list) else []
    print(f"[+] Extracted {len(items)} total unique photos from active tab!", flush=True)

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    print(f"[+] Saved {len(items)} photo records to {out_file}", flush=True)

if __name__ == "__main__":
    main()
