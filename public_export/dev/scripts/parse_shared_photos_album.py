import re
import json
from pathlib import Path

content_file = Path(r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e616d655-4be6-4f57-bfad-24249ce3f54e\.system_generated\steps\1118\content.md')

if content_file.exists():
    text = content_file.read_text(encoding='utf-8', errors='ignore')
    # Find all Google Photos media URL strings
    urls = set(re.findall(r'https://lh3\.googleusercontent\.com/[a-zA-Z0-9_\-]+', text))
    print(f"TOTAL UNIQUE GOOGLE PHOTOS MEDIA URLS EXTRACTED: {len(urls)}\n")
    for idx, u in enumerate(list(urls)[:20]):
        print(f"[{idx+1}] {u}")
else:
    print(f"File not found: {content_file}")
