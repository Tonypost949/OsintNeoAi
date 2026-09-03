import os
import re
import urllib.request
from pathlib import Path

content_file = Path(r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e616d655-4be6-4f57-bfad-24249ce3f54e\.system_generated\steps\1271\content.md')
out_dir = Path(r'C:\OsintNeoAi\scratch\album_a74G5sEDR54YwTiF7')
out_dir.mkdir(parents=True, exist_ok=True)

if content_file.exists():
    text = content_file.read_text(encoding='utf-8', errors='ignore')
    raw_urls = re.findall(r'https://lh3\.googleusercontent\.com/pw/[a-zA-Z0-9_\-]+', text)
    unique_urls = list(set(raw_urls))
    print(f"=== DOWNLOADING ALL {len(unique_urls)} PHOTOS FROM ALBUM a74G5sEDR54YwTiF7 ===")

    for idx, url in enumerate(unique_urls):
        full_url = f"{url}=w1600"
        dst = out_dir / f"photo_{idx+1:03d}.jpg"
        try:
            urllib.request.urlretrieve(full_url, dst)
            print(f"[{idx+1}/{len(unique_urls)}] Downloaded: {dst.name}")
        except Exception as e:
            print(f"[{idx+1}/{len(unique_urls)}] Error: {e}")

    print(f"✓ Downloaded all photos to {out_dir}")
else:
    print(f"File not found: {content_file}")
