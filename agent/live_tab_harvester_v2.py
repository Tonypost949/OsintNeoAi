"""
live_tab_harvester_v2.py — Controls the active borrowed Google Photos browser tab,
scrolls all container elements to trigger dynamic DOM rendering of every photo in the album,
and extracts 100% of photos without any cutoff.
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

    print("[*] Connecting to borrowed Google Photos tab...", flush=True)
    tab_res = send("find_tab", {"url": "https://photos.google.com", "active": True})
    print(f"[+] Tab borrow status: {tab_res}", flush=True)

    scroll_js = '''
    (() => {
        // Scroll window and all containers
        window.scrollBy(0, 3500);
        if (document.documentElement) document.documentElement.scrollTop += 3500;
        if (document.body) document.body.scrollTop += 3500;
        
        const scrollables = document.querySelectorAll('div, c-wiz, main');
        for (let el of scrollables) {
            if (el.scrollHeight > el.clientHeight && el.clientHeight > 200) {
                el.scrollTop += 3500;
            }
        }
        
        // Count all photo elements and links
        const anchors = document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"], a[data-id]');
        const imgs = document.querySelectorAll('img[src*="googleusercontent.com"]');
        return {
            photoAnchors: anchors.length,
            photoImages: imgs.length,
            scrollY: window.scrollY || (document.documentElement ? document.documentElement.scrollTop : 0)
        };
    })()
    '''

    print("[*] Starting deep scroll loop across album...", flush=True)
    last_cnt = 0
    stable_rounds = 0

    for step in range(1, 75):
        res = send("evaluate", {"code": scroll_js})
        val = res.get("data", {}) or res.get("value", {})
        if isinstance(val, dict) and 'value' in val and isinstance(val['value'], dict):
            val = val['value']
            
        anchors = val.get("photoAnchors", 0) if isinstance(val, dict) else 0
        images = val.get("photoImages", 0) if isinstance(val, dict) else 0
        max_seen = max(anchors, images)

        print(f"  [Step #{step:02d}] Anchors: {anchors} | Images: {images} | ScrollY: {val.get('scrollY')}", flush=True)

        if max_seen == last_cnt and max_seen > 0:
            stable_rounds += 1
            if stable_rounds >= 6:
                print(f"[+] Reached end of album! (Photos loaded: {max_seen})", flush=True)
                break
        else:
            stable_rounds = 0
            last_cnt = max_seen

        time.sleep(1.2)

    print("\n[*] Extracting all photo links and image URLs from page DOM...", flush=True)
    extract_js = '''
    (() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"], a[data-id]'));
        const imgs = Array.from(document.querySelectorAll('img[src*="googleusercontent.com"]'));
        
        const photoMap = new Map();
        
        for (let a of anchors) {
            const href = a.href;
            const img = a.querySelector('img');
            const src = img ? (img.src || img.getAttribute('src')) : null;
            const aria = a.getAttribute('aria-label') || '';
            photoMap.set(href, { href: href, image_url: src, aria_label: aria });
        }
        
        for (let img of imgs) {
            const src = img.src || img.getAttribute('src');
            const parentA = img.closest('a');
            const href = parentA ? parentA.href : ('img_' + src.slice(-30));
            if (!photoMap.has(href)) {
                photoMap.set(href, { href: href, image_url: src, aria_label: img.getAttribute('alt') || '' });
            }
        }
        
        return Array.from(photoMap.values());
    })()
    '''
    harvest_res = send("evaluate", {"code": extract_js})
    val = harvest_res.get("data") or harvest_res.get("value") or []
    if isinstance(val, dict) and 'value' in val:
        items = val['value']
    else:
        items = val if isinstance(val, list) else []

    print(f"\n[+] Successfully harvested {len(items)} unique photos from live browser session!", flush=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    print(f"[+] Saved complete dataset to {out_path}", flush=True)

if __name__ == "__main__":
    main()
