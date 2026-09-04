import re
import urllib.request
from pathlib import Path

content_file = Path(r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e616d655-4be6-4f57-bfad-24249ce3f54e\.system_generated\steps\1864\content.md')
text = content_file.read_text(encoding='utf-8', errors='ignore')

# Extract direct image link from lightshot HTML
img_urls = re.findall(r'https://image\.prntscr\.com/image/[^\"]+', text)
if not img_urls:
    img_urls = re.findall(r'<meta property=\"og:image\" content=\"([^\"]+)\"', text)
if not img_urls:
    img_urls = re.findall(r'src=\"(https://[^\"]+)\"', text)

print("=== LIGHTSHOT SCREENSHOT EXTRACTOR ===")
print("Found Image URLs:", img_urls)

if img_urls:
    img_url = img_urls[0]
    out_img = Path(r'C:\OsintNeoAi\scratch\lightshot_screenshot.png')
    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        data = urllib.request.urlopen(req).read()
        out_img.write_bytes(data)
        print(f"✓ Downloaded Lightshot screenshot ({len(data)} bytes) to: {out_img}")
    except Exception as e:
        print("Download error:", e)
