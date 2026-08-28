"""
borrow_and_scroll.py — Borrows the user's active Google Photos tab via Kimi WebBridge,
scrolls smoothly to trigger lazy-loading of all photos in the album,
and extracts every single photo URL and ID.
"""
import requests
import json
import time
import os
import sys

DAEMON_URL = "http://127.0.0.1:10086/command"
SESSION_NAME = "osint-user-session"

def call_bridge(action, args=None):
    if args is None:
        args = {}
    payload = {
        "action": action,
        "args": args,
        "session": SESSION_NAME
    }
    r = requests.post(DAEMON_URL, json=payload, timeout=20)
    return r.json()

def main():
    out_file = sys.argv[1] if len(sys.argv) > 1 else "data/google_photos_unlimited_live.json"
    
    print("[*] Finding and borrowing user's active Google Photos tab...", flush=True)
    tab_res = call_bridge("find_tab", {
        "url": "https://photos.google.com",
        "active": True
    })
    print(f"[+] Tab Borrow Result: {tab_res}", flush=True)

    # Check page state
    eval_res = call_bridge("evaluate", {
        "code": "(() => ({ url: window.location.href, title: document.title, photos: document.querySelectorAll('a[href*=\"/photo/\"]').length }))()"
    })
    print(f"[+] Current Page State: {eval_res.get('data') or eval_res.get('value')}", flush=True)

    print("\n[*] Starting deep scrolling loop to load 100% of album photos...", flush=True)
    last_cnt = 0
    stable_count = 0

    for step in range(1, 80):
        scroll_code = """
        (() => {
            window.scrollBy(0, 3500);
            const items = document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"]');
            return {
                photoCount: items.length,
                scrollHeight: document.body.scrollHeight,
                scrollY: window.scrollY || window.pageYOffset
            };
        })()
        """
        res = call_bridge("evaluate", {"code": scroll_code})
        data = res.get("data", {}) or res.get("value", {})
        count = data.get("photoCount", 0) if isinstance(data, dict) else 0
        height = data.get("scrollHeight", 0) if isinstance(data, dict) else 0

        print(f"  [Scroll Step #{step:02d}] Visible Photos Loaded: {count} (Height: {height}px)", flush=True)

        if count == last_cnt and count > 0:
            stable_count += 1
            if stable_count >= 6:
                print(f"[+] Photo count stabilized at {count} photos. Reached bottom of album!", flush=True)
                break
        else:
            stable_count = 0
            last_cnt = count

        time.sleep(1.5)

    print("\n[*] Harvesting all photo links from DOM...", flush=True)
    harvest_code = """
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
    final_res = call_bridge("evaluate", {"code": harvest_code})
    items = final_res.get("data", []) or final_res.get("value", []) or []
    print(f"[+] Total photos harvested: {len(items)}", flush=True)

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    print(f"[+] Saved {len(items)} photo records to {out_file}", flush=True)

if __name__ == "__main__":
    main()
