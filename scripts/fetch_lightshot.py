import urllib.request
import urllib.error
import re
from pathlib import Path
import json

URL = "https://prnt.sc/Ltbp9VGQsfDH"
OUTPUT_DIR = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence/screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "Ltbp9VGQsfDH_screenshot.png"

def download_lightshot(url, dest_path):
    print(f"[*] Fetching Lightshot page: {url}")
    # Use a realistic User-Agent to bypass basic blocks
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
        # Parse og:image or direct img tag
        # e.g., <meta name="twitter:image:src" content="https://image.prntscr.com/image/...">
        img_url = None
        match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if not match:
            match = re.search(r'<meta name="twitter:image:src" content="([^"]+)"', html)
        if not match:
            match = re.search(r'id="screenshot-image" src="([^"]+)"', html)
            
        if match:
            img_url = match.group(1)
            print(f"[+] Found direct image URL: {img_url}")
            
            # Download the actual image
            img_req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(img_req) as img_resp:
                img_data = img_resp.read()
                
            with open(dest_path, "wb") as f:
                f.write(img_data)
                
            print(f"[✓] Successfully saved image ({len(img_data)} bytes) to {dest_path}")
        else:
            print("[-] Could not find image URL in HTML.")
            
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    download_lightshot(URL, OUTPUT_FILE)
