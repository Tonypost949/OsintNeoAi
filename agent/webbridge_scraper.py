"""
webbridge_scraper.py — Interacts with Kimi WebBridge daemon at http://127.0.0.1:10086
to control the live browser, scroll all the way through Google Photos albums,
and extract EVERY photo link and ID without any 300-item cutoff.
"""
import requests
import json
import time
import sys
import os

DAEMON_URL = "http://127.0.0.1:10086/command"
SESSION_NAME = "osint-google-photos-unlimited"

def send_webbridge_cmd(action, args=None):
    if args is None:
        args = {}
    payload = {
        "action": action,
        "args": args,
        "session": SESSION_NAME
    }
    resp = requests.post(DAEMON_URL, json=payload, timeout=30)
    return resp.json()

def scrape_full_album(album_url, output_json_path):
    print(f"[*] Navigating browser to: {album_url}", flush=True)
    nav_res = send_webbridge_cmd("navigate", {
        "url": album_url,
        "newTab": True,
        "group_title": "OSINT Neo Google Photos Scraping"
    })
    print(f"[+] Navigation response: {nav_res}", flush=True)

    print("[*] Waiting 5 seconds for initial page render...", flush=True)
    time.sleep(5)

    print("[*] Starting automated scroll loop to load ALL photos...", flush=True)
    last_count = 0
    stable_rounds = 0

    for scroll_step in range(1, 60):
        # Evaluate JS to get current photo count and scroll down
        js_code = """
        (() => {
            window.scrollTo(0, document.body.scrollHeight);
            const links = Array.from(document.querySelectorAll('a[href*="./photo/"], a[href*="/photo/"], a[data-id]'));
            return {
                height: document.body.scrollHeight,
                count: links.length
            };
        })()
        """
        eval_res = send_webbridge_cmd("evaluate", {"code": js_code})
        val = eval_res.get("value", {})
        count = val.get("count", 0) if isinstance(val, dict) else 0
        height = val.get("height", 0) if isinstance(val, dict) else 0

        print(f"  [Scroll #{scroll_step}] Detected {count} rendered photo links in DOM (Height: {height}px)", flush=True)

        if count == last_count and count > 0:
            stable_rounds += 1
            if stable_rounds >= 4:
                print(f"[+] Photo count stabilized at {count}. Reached bottom of album.", flush=True)
                break
        else:
            stable_rounds = 0
            last_count = count

        time.sleep(3)

    # Extract all photo metadata from DOM
    extract_js = """
    (() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"]'));
        const seen = new Set();
        const photos = [];
        for (let a of anchors) {
            const href = a.href;
            if (!seen.has(href)) {
                seen.add(href);
                const img = a.querySelector('img');
                const imgSrc = img ? (img.src || img.getAttribute('src')) : null;
                const aria = a.getAttribute('aria-label') || '';
                photos.push({
                    href: href,
                    image_url: imgSrc,
                    aria_label: aria
                });
            }
        }
        return photos;
    })()
    """
    final_res = send_webbridge_cmd("evaluate", {"code": extract_js})
    photos = final_res.get("value", []) if isinstance(final_res.get("value"), list) else []
    print(f"\n[+] Successfully extracted {len(photos)} total unique photos from live browser session!", flush=True)

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(photos, f, indent=2)
    print(f"[+] Saved full un-capped photos manifest to: {output_json_path}", flush=True)
    return photos

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://photos.app.goo.gl/fY89o9SK5KJDLgJm6"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/google_photos_album1_unlimited.json"
    scrape_full_album(target, out)
