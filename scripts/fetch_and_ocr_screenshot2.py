import urllib.request
import easyocr
from pathlib import Path

img_url = "https://img.lightshot.app/QU1PpbNMRm2suVByjtfjHg.png"
out_path = Path(r'C:\OsintNeoAi\scratch\jet_brains_toolbox_screenshot2.png')

req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
data = urllib.request.urlopen(req).read()
out_path.write_bytes(data)

print(f"✓ Downloaded second screenshot image ({len(data)} bytes) to: {out_path}")

print("=== EXECUTING NEURAL OCR ON SECOND JETBRAINS TOOLBOX SCREENSHOT ===")
reader = easyocr.Reader(['en'], gpu=False)
results = reader.readtext(str(out_path))

ocr_lines = []
for (bbox, text, prob) in results:
    if prob > 0.2:
        ocr_lines.append(text)

print("\nExtracted Screenshot Text:")
for line in ocr_lines:
    print(f"  - {line}")

out_txt = Path(r'C:\OsintNeoAi\evidence\jetbrains_toolbox_screenshot2_ocr.md')
out_txt.write_text("# 🖼️ JETBRAINS TOOLBOX SECOND SCREENSHOT TRANSCRIPT\n\n" + "\n".join(f"- `{l}`" for l in ocr_lines), encoding='utf-8')
print(f"\n✓ Saved OCR transcript to: {out_txt}")
