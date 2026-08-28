"""
keyboard_scroll_harvester.py — Uses keyboard events (PageDown / End / ArrowDown)
and virtual scroll dispatching via Kimi WebBridge to unroll every photo in Google Photos albums.
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
    out_path = sys.argv[1] if len(sys.argv) > 1 else "data/google_photos_unlimited_live.json"

    print("[*] Connecting to live Google Photos tab...", flush=True)
    tab_res = send("find_tab", {"url": "https://photos.google.com", "active": True})
    print(f"[+] Tab status: {tab_res}", flush=True)

    key_scroll_js = '''
    (() => {
        // Dispatch PageDown and ArrowDown events to window and active elements
        const eventOptions = { key: 'PageDown', code: 'PageDown', keyCode: 34, which: 34, bubbles: true, cancelable: true };
        window.dispatchEvent(new KeyboardEvent('keydown', eventOptions));
        window.dispatchEvent(new KeyboardEvent('keyup', eventOptions));
        
        if (document.body) {
            document.body.dispatchEvent(new KeyboardEvent('keydown', eventOptions));
        }

        // Also scroll every container
        window.scrollBy(0, 5000);
        document.documentElement.scrollTop += 5000;
        
        const allDivs = document.querySelectorAll('div, c-wiz, main');
        for (let d of allDivs) {
            if (d.scrollHeight > d.clientHeight && d.clientHeight > 100) {
                d.scrollTop += 5000;
            }
        }
        
        // Find all unique photos in the virtual grid
        const allAnchors = document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"], a[data-id]');
        const allImgs = document.querySelectorAll('img[src*="googleusercontent.com"]');
        return {
            anchors: allAnchors.length,
            images: allImgs.length
        };
    })()
    '''

    all_harvested = {}

    print("[*] Executing continuous virtual scroll & DOM accumulator...", flush=True)
    for i in range(1, 90):
        res = send("evaluate", {"code": key_scroll_js})
        
        # Accumulate currently visible photo links into our master map
        acc_js = '''
        (() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/photo/"], a[href*="./photo/"], a[data-id]'));
            return anchors.map(a => ({
                href: a.href,
                image_url: a.querySelector('img') ? (a.querySelector('img').src || a.querySelector('img').getAttribute('src')) : null,
                aria: a.getAttribute('aria-label') || ''
            }));
        })()
        '''
        acc_res = send("evaluate", {"code": acc_js})
        val = acc_res.get("data") or acc_res.get("value") or []
        if isinstance(val, dict) and 'value' in val:
            items = val['value']
        else:
            items = val if isinstance(val, list) else []

        for it in items:
            if it.get("href"):
                all_harvested[it["href"]] = it

        print(f"  [Pass #{i:02d}] Total Accumulated Unique Photos in Memory: {len(all_harvested)}", flush=True)
        time.sleep(1.2)

    print(f"\n[+] Total unique photos harvested across all scroll cycles: {len(all_harvested)}", flush=True)
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(list(all_harvested.values()), f, indent=2)
    print(f"[+] Saved complete un-capped dataset to {out_path}", flush=True)

if __name__ == "__main__":
    main()
