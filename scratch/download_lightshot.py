import os
import re
import urllib.request

html_file = r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e0259c57-0b03-45f8-956f-927ea22d1195\.system_generated\steps\5958\content.md'
with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Look for image URLs
matches = re.findall(r'https?://[^\s"\'<>]+\.(?:png|jpg|jpeg|webp)', text)
print("Found matches:", matches)

img_url = None
for m in matches:
    if "prntscr" in m or "imgur" in m or "image" in m:
        img_url = m
        break

if not img_url and matches:
    img_url = matches[0]

print("Selected Image URL:", img_url)

if img_url:
    out_path = os.path.join(r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e0259c57-0b03-45f8-956f-927ea22d1195', 'screenshot_lightshot.png')
    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req) as resp, open(out_path, 'wb') as out_f:
            out_f.write(resp.read())
        print(f"[✓] Saved screenshot to: {out_path} ({os.path.getsize(out_path)} bytes)")
    except Exception as e:
        print(f"[-] Download error: {e}")
