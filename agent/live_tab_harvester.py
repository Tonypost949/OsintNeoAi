"""
live_tab_harvester.py — Controls the active borrowed Google Photos browser tab,
scrolls to load all photos into DOM, and extracts every single link & image.
"""
import requests
import json
import time
import os
import sys

SESSION = "test-session"
DAEMON = "http://127.0.0.1:10086/command"

def send(action, args=None):
    if args is None:
        args = {}
    r = requests.post(DAEMON, json={"action": action, "args": args, "session": SESSION}, timeout=20)
    return r.json()

def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "data/google_photos_live_scraped.json"

    print("[*] Checking connection to borrowed active tab...", flush=True)
    # Ensure tab is borrowed
    tab_res = send("find_tab", {"url": "https://photos.google.com", "active": True})
    print(f"[+] Tab borrow status: {tab_res}", flush=True)

    # Initial check
    status_js = '(() => ({ url: window.location.href, title: document.title, photos: document.querySelectorAll("a[href*=\\"/photo/\\"], a[href*=\\"./photo/\\"]").length }))()'
    initial_state = send("evaluate", {"code": status_js})
    print(f"[+] Active Page: {initial_state.get('data') or initial_state.get('value')}", flush=True)

    print("\n[*] Commencing automated scrolling loop across the entire album...", flush=True)
    last_cnt = 0
    stable_rounds = 0

    scroll_js = '''
    (() => {
        window.scrollBy(0, 4500);
        const links = document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"]');
        return {
            count: links.length,
            scrollHeight: document.body.scrollHeight,
            scrollY: window.scrollY || window.pageYOffset
        };
    })()
    '''

    for step in range(1, 80):
        res = send("evaluate", {"code": scroll_js})
        val = res.get("data", {}) or res.get("value", {})
        cnt = val.get("count", 0) if isinstance(val, dict) else 0
        height = val.get("scrollHeight", 0) if isinstance(val, dict) else 0

        print(f"  [Scroll Step #{step:02d}] Loaded {cnt} photo elements in DOM (Height: {height}px)", flush=True)

        if cnt == last_cnt and cnt > 0:
            stable_rounds += 1
            if stable_rounds >= 6:
                print(f"[+] Count stabilized at {cnt}. Album fully unrolled!", flush=True)
                break
        else:
            stable_rounds = 0
            last_cnt = cnt

        time.sleep(1.5)

    print("\n[*] Harvesting all unrolled photo objects from DOM...", flush=True)
    harvest_js = '''
    (() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"]'));
        const items = [];
        const seen = new Set();
        for (let a of anchors) {
            const href = a.href;
            if (!seen.has(href)) {
                seen.add(href);
                const img = a.querySelector('img');
                items.push({
                    href: href,
                    image_url: img ? (img.src || img.getAttribute('src')) : null,
                    aria_label: a.getAttribute('aria-label') || ''
                });
            }
        }
        return items;
    })()
    '''
    harvest_res = send("evaluate", {"code": harvest_js})
    items = harvest_res.get("data") or harvest_res.get("value") or []

    print(f"[+] Total photos extracted from live browser session: {len(items)}", flush=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    print(f"[+] Saved complete un-capped dataset to {out_path}", flush=True)

if __name__ == "__main__":
    main()
