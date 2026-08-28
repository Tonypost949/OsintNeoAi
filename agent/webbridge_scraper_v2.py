"""
webbridge_scraper_v2.py — Uses Kimi WebBridge with resolved URLs and active tab borrowing
to scroll and extract 100% of photos from Google Photos albums.
"""
import requests
import json
import time
import sys
import os

DAEMON_URL = "http://127.0.0.1:10086/command"
SESSION_NAME = "osint-photos-live"

def send_webbridge_cmd(action, args=None):
    if args is None:
        args = {}
    payload = {
        "action": action,
        "args": args,
        "session": SESSION_NAME
    }
    resp = requests.post(DAEMON_URL, json=payload, timeout=45)
    return resp.json()

def main():
    album_url = sys.argv[1] if len(sys.argv) > 1 else "https://photos.google.com/share/AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew?key=d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "data/google_photos_album1_browser_extracted.json"

    print(f"[*] Connecting to Kimi WebBridge daemon at {DAEMON_URL}...", flush=True)
    
    # Try borrowing active tab or navigating
    tab_res = send_webbridge_cmd("find_tab", {"active": True})
    print(f"[+] Active tab lookup: {tab_res}", flush=True)

    print(f"[*] Navigating to resolved Google Photos album: {album_url}", flush=True)
    nav_res = send_webbridge_cmd("navigate", {"url": album_url})
    print(f"[+] Nav response: {nav_res}", flush=True)

    print("[*] Waiting 5 seconds for Google Photos UI initialization...", flush=True)
    time.sleep(5)

    print("[*] Commencing deep scrolling loop across page...", flush=True)
    last_photo_count = 0
    stable_cycles = 0

    for i in range(1, 100):
        scroll_js = """
        (() => {
            window.scrollBy(0, 3000);
            const anchors = Array.from(document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"]'));
            return {
                photoCount: anchors.length,
                scrollHeight: document.body.scrollHeight,
                scrollTop: window.scrollY || document.documentElement.scrollTop
            };
        })()
        """
        res = send_webbridge_cmd("evaluate", {"code": scroll_js})
        val = res.get("value", {}) if isinstance(res.get("value"), dict) else {}
        count = val.get("photoCount", 0)
        print(f"  [Scroll #{i}] Photos currently visible/rendered in DOM: {count} (Height: {val.get('scrollHeight')})", flush=True)

        if count == last_photo_count and count > 0:
            stable_cycles += 1
            if stable_cycles >= 6:
                print(f"[+] Photo count stabilized at {count}. Reached bottom of album!", flush=True)
                break
        else:
            stable_cycles = 0
            last_photo_count = count

        time.sleep(2)

    # Extract all elements
    extract_js = """
    (() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"]'));
        const items = [];
        const seen = new Set();
        for (let a of anchors) {
            const href = a.href;
            if (!seen.has(href)) {
                seen.add(href);
                const img = a.querySelector('img');
                const src = img ? (img.src || img.getAttribute('src')) : null;
                const aria = a.getAttribute('aria-label') || '';
                items.push({
                    href: href,
                    image_url: src,
                    aria_label: aria
                });
            }
        }
        return items;
    })()
    """
    final_res = send_webbridge_cmd("evaluate", {"code": extract_js})
    items = final_res.get("value", []) if isinstance(final_res.get("value"), list) else []
    print(f"\n[+] Total photos harvested via browser automation: {len(items)}", flush=True)

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    print(f"[+] Saved complete un-capped dataset to {out_file}", flush=True)

if __name__ == "__main__":
    main()
