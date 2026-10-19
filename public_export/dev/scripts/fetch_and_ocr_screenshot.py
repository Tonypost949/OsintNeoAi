import urllib.request
import easyocr
from pathlib import Path

img_url = "https://img.lightshot.app/sfwvwSkZRS6asbNwzJ9UFQ.png"
out_path = Path(r'C:\OsintNeoAi\scratch\jet_brains_toolbox_screenshot.png')

req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
data = urllib.request.urlopen(req).read()
out_path.write_bytes(data)

print(f"✓ Downloaded screenshot image ({len(data)} bytes) to: {out_path}")

print("=== EXECUTING NEURAL OCR ON JETBRAINS TOOLBOX SCREENSHOT ===")
reader = easyocr.Reader(['en'], gpu=False)
results = reader.readtext(str(out_path))

ocr_lines = []
for (bbox, text, prob) in results:
    if prob > 0.3:
        ocr_lines.append(text)

print("\nExtracted Screenshot Text:")
for line in ocr_lines:
    print(f"  - {line}")

out_txt = Path(r'C:\OsintNeoAi\evidence\jetbrains_toolbox_screenshot_ocr.md')
out_txt.write_text("# 🖼️ JETBRAINS TOOLBOX SCREENSHOT OCR TRANSCRIPT\n\n" + "\n".join(f"- `{l}`" for l in ocr_lines), encoding='utf-8')
print(f"\n✓ Saved OCR transcript to: {out_txt}")
