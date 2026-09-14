import os
import sys
import requests
import zipfile

TARGET_DIR = r"C:\OsintNeoAi\data\takeouts\etp949609_takeout_20260913"
os.makedirs(TARGET_DIR, exist_ok=True)

def download_with_cookies():
    try:
        import browser_cookie3
        print("[AUTH] Extracting Google session cookies from Chrome...")
        cj = browser_cookie3.chrome(domain_name='.google.com')
        print("[AUTH] Successfully loaded Chrome session cookies!")
    except Exception as e:
        print(f"[AUTH ERROR] Failed to load cookies: {e}")
        return

    # Base Takeout manage URL
    manage_url = "https://takeout.google.com/manage"
    s = requests.Session()
    s.cookies = cj
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    print("[FETCH] Querying Google Takeout manage page...")
    resp = s.get(manage_url)
    print(f"[FETCH] Status Code: {resp.status_code}")
    
    # Search for download URLs in response HTML
    import re
    download_urls = re.findall(r'href="([^"]*(?:takeout\.google\.com/download|googleusercontent\.com)[^"]*)"', resp.text)
    if not download_urls:
        download_urls = re.findall(r'href="(/download/[^"]+)"', resp.text)
        download_urls = ["https://takeout.google.com" + u for u in download_urls]
        
    print(f"[FOUND] Found {len(download_urls)} download URLs on Takeout page.")
    
    for idx, url in enumerate(download_urls):
        print(f"\n[{idx+1}/{len(download_urls)}] Downloading from {url}...")
        try:
            r = s.get(url, stream=True)
            cd = r.headers.get('content-disposition', '')
            fname = f"takeout_part_{idx+1}.zip"
            if 'filename=' in cd:
                fname = re.findall(r'filename="?([^";]+)"?', cd)[0]
                
            out_file = os.path.join(TARGET_DIR, fname)
            print(f"  -> Saving to: {out_file} (Status: {r.status_code})")
            
            with open(out_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            print(f"[✓] Downloaded: {fname}")
            
            # If it's a zip file, immediately unpack it
            if out_file.endswith('.zip'):
                try:
                    with zipfile.ZipFile(out_file, 'r') as zf:
                        zf.extractall(TARGET_DIR)
                        print(f"[✓] Extracted: {fname}")
                except Exception as e:
                    print(f"  Extraction error: {e}")
        except Exception as e:
            print(f"[ERROR] Download failed: {e}")

if __name__ == "__main__":
    download_with_cookies()
