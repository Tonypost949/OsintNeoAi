import re
import os
import sys
import time
import urllib.request
from pathlib import Path

HTML = Path(r'C:\Users\Amd949609\.local\share\opencode\tool-output\tool_066eb453300186iAIg8S5L00tW')
BASE = Path(r'C:\Users\AMD949~1\AppData\Local\Temp\opencode\photos_a74G5sEDR54YwTiF7')
DL = BASE / 'downloads'
OCR = BASE / 'ocr'
DL.mkdir(parents=True, exist_ok=True)
OCR.mkdir(parents=True, exist_ok=True)

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def extract_urls():
    html = HTML.read_text(encoding='utf-8', errors='ignore')
    found = set()
    for m in re.finditer(r'https://lh3\.googleusercontent\.com/pw/[^"\s\\\)]+=w\d+-h\d+-no', html):
        url = m.group(0).rstrip(')')
        if 'ogw/default-user' in url:
            continue
        # full-res original
        full = re.sub(r'=w\d+-h\d+-no$', '=d', url)
        found.add((url, full))
    return sorted(found)

def download(url, dest):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, 'wb') as f:
            f.write(r.read())
        return True
    except Exception as e:
        print(f'  DOWNLOAD FAIL {dest.name}: {e}', flush=True)
        return False

def main():
    items = extract_urls()
    print(f'Extracted {len(items)} photo URLs', flush=True)
    downloaded = []
    n = 0
    for thumb, full in items:
        n += 1
        fname = f'photo_{n:03d}.jpg'
        dest = DL / fname
        if not dest.exists():
            print(f'[{n}/{len(items)}] downloading', flush=True)
            if not download(full, dest):
                print(f'  trying thumbnail fallback', flush=True)
                download(thumb, dest)
        else:
            print(f'[{n}/{len(items)}] exists', flush=True)
        downloaded.append((n, fname, dest))
        time.sleep(0.3)
    print(f'Downloaded/verified {len(downloaded)} images to {DL}', flush=True)

if __name__ == '__main__':
    main()
