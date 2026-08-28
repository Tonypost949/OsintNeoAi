"""
paginate_google_photos.py — Complete album fetcher that follows Google Photos pagination tokens
to extract ALL photos in an album without the 300-item page limit.
"""
import requests
import re
import json
import os
import sys

def fetch_all_album_photos(album_url):
    print(f"[*] Resolving and scraping album URL: {album_url}")
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    resp = session.get(album_url, headers=headers, allow_redirects=True)
    if resp.status_code != 200:
        print(f"[-] Failed to fetch album: HTTP {resp.status_code}")
        return []

    final_url = resp.url
    print(f"[*] Final Album URL: {final_url}")

    # Extract share token / album key from URL
    share_id_match = re.search(r'photos\.google\.com/share/([a-zA-Z0-9_-]+)', final_url)
    share_id = share_id_match.group(1) if share_id_match else None
    
    key_match = re.search(r'key=([a-zA-Z0-9_-]+)', final_url)
    album_key = key_match.group(1) if key_match else None

    print(f"[*] Share ID: {share_id}")
    print(f"[*] Album Key: {album_key}")

    # Extract build label (bl), session id (f.sid), and XSRF/at token
    at_match = re.search(r'"SNlM0e":"(.*?)"', resp.text)
    at_token = at_match.group(1) if at_match else None

    bl_match = re.search(r'"cfb2h":"(.*?)"', resp.text)
    bl = bl_match.group(1) if bl_match else 'boq_photosuiserver_20260825.07_p0'

    sid_match = re.search(r'"FdrFJe":"(.*?)"', resp.text)
    f_sid = sid_match.group(1) if sid_match else None

    all_items = []
    
    # Parse initial page (ds:1)
    m = re.search(r'AF_initDataCallback\(({key: \'ds:1\'.*?})\);</script>', resp.text, re.DOTALL)
    next_token = None
    if m:
        blob = m.group(1)
        data_json = json.loads(re.search(r'data:(.*?), sideChannel:', blob, re.DOTALL).group(1))
        initial_items = data_json[1] if len(data_json) > 1 and isinstance(data_json[1], list) else []
        next_token = data_json[2] if len(data_json) > 2 else None
        
        for it in initial_items:
            all_items.append(it)
            
        print(f"[+] Page 1: Extracted {len(initial_items)} items. Next continuation token: {bool(next_token)}")

    # Follow continuation tokens for subsequent pages
    page = 2
    req_id = 100000
    while next_token:
        print(f"[*] Fetching Page {page} via Google Photos batch RPC (token: {next_token[:25]}...)...")
        rpc_url = f"https://photos.google.com/_/PhotosUi/data/batched?rpcids=snAcKc&bl={bl}&hl=en&_reqid={req_id}&rt=c"
        req_id += 10000
        
        req_payload = [share_id, next_token, None, None, album_key]
        f_req = json.dumps([[["snAcKc", json.dumps(req_payload), None, "generic"]]])
        
        post_data = {'f.req': f_req}
        if at_token:
            post_data['at'] = at_token

        post_headers = {
            'User-Agent': headers['User-Agent'],
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Referer': final_url
        }

        rpc_res = session.post(rpc_url, data=post_data, headers=post_headers, timeout=25)
        if rpc_res.status_code != 200:
            print(f"[-] RPC request failed with HTTP {rpc_res.status_code}")
            break

        raw_text = rpc_res.text
        # Strip protection prefix `)]}'\n`
        clean_text = re.sub(r'^\)]}\'\s*', '', raw_text)
        
        try:
            # Lines contain chunk sizes and JSON lines
            chunks = clean_text.strip().split('\n')
            found_items = False
            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk.startswith('['):
                    continue
                try:
                    envelope = json.loads(chunk)
                    for entry in envelope:
                        if isinstance(entry, list) and len(entry) >= 3 and entry[0] == 'wrb.fr' and entry[1] == 'snAcKc':
                            inner_data = json.loads(entry[2])
                            page_items = inner_data[0] if len(inner_data) > 0 and isinstance(inner_data[0], list) else []
                            next_token = inner_data[1] if len(inner_data) > 1 else None
                            
                            print(f"[+] Page {page}: Extracted {len(page_items)} additional items! (Next token available: {bool(next_token)})")
                            for it in page_items:
                                all_items.append(it)
                            found_items = True
                            break
                except Exception:
                    continue

            if not found_items:
                print(f"[-] No items extracted on Page {page}. Ending pagination.")
                break
                
            page += 1
            if not next_token:
                print("[*] Reached end of album (no further pagination tokens).")
                break
        except Exception as e:
            print(f"[-] Error parsing RPC response on page {page}: {e}")
            break

    print(f"\n[+] Total photos extracted across all pages: {len(all_items)}")

    # Format into manifest records
    manifest = []
    for idx, item in enumerate(all_items):
        manifest.append({
            'index': idx + 1,
            'id': item[0],
            'image_url': item[1][0] if len(item) > 1 and len(item[1]) > 0 else None,
            'width': item[1][1] if len(item) > 1 and len(item[1]) > 1 else None,
            'height': item[1][2] if len(item) > 1 and len(item[1]) > 2 else None,
            'timestamp': item[2] if len(item) > 2 else None
        })

    return manifest

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://photos.app.goo.gl/fY89o9SK5KJDLgJm6"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "data/full_album_manifest.json"
    
    manifest = fetch_all_album_photos(target_url)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] Saved full un-capped manifest with {len(manifest)} items to {out_file}")
