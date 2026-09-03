import re
from pathlib import Path

content_file = Path(r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e616d655-4be6-4f57-bfad-24249ce3f54e\.system_generated\steps\1146\content.md')

if content_file.exists():
    text = content_file.read_text(encoding='utf-8', errors='ignore')
    # Find canonical share URL
    canonical = re.findall(r'https://photos\.google\.com/share/[^\"]+', text)
    print(f"Canonical URL: {canonical[0] if canonical else 'None'}\n")
    # Find OG title or image metadata
    og_title = re.findall(r'<meta property=\"og:title\" content=\"([^\"]+)\"', text)
    og_desc = re.findall(r'<meta property=\"og:description\" content=\"([^\"]+)\"', text)
    og_img = re.findall(r'<meta property=\"og:image\" content=\"([^\"]+)\"', text)
    print(f"OG Title: {og_title[0] if og_title else 'None'}")
    print(f"OG Description: {og_desc[0] if og_desc else 'None'}")
    print(f"OG Image: {og_img[0] if og_img else 'None'}")
else:
    print(f"File not found: {content_file}")
