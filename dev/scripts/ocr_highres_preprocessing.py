import cv2
import numpy as np
import urllib.request
import easyocr
from pathlib import Path

img_url = "https://img.lightshot.app/5wHc6TolQE23u8dZ7oFXgg.png"
raw_path = Path(r'C:\OsintNeoAi\scratch\highres_raw.png')

req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
data = urllib.request.urlopen(req).read()
raw_path.write_bytes(data)

print(f"✓ Downloaded image ({len(data)} bytes) to: {raw_path}")

# Load and preprocess image for high accuracy OCR
img = cv2.imread(str(raw_path))

# 1. Upscale image 2x for small text recognition
height, width = img.shape[:2]
upscaled = cv2.resize(img, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)

# 2. Convert to Grayscale
gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)

# 3. Enhance Contrast via CLAHE
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
enhanced = clahe.apply(gray)

proc_path = Path(r'C:\OsintNeoAi\scratch\highres_processed.png')
cv2.imwrite(str(proc_path), enhanced)

print("=== EXECUTING ENHANCED OCR ===")
reader = easyocr.Reader(['en'], gpu=False)
results = reader.readtext(str(proc_path))

lines = [res[1] for res in results if res[2] > 0.15]

print("\n✓ HIGH-ACCURACY OCR TRANSCRIPT:")
print("---------------------------------------------------------")
for line in lines:
    print(f"  • {line}")
print("---------------------------------------------------------")

out_txt = Path(r'C:\OsintNeoAi\evidence\highres_ocr_transcript.md')
out_txt.write_text("# 🖼️ HIGH-ACCURACY PREPROCESSED OCR TRANSCRIPT\n\n" + "\n".join(f"- `{l}`" for l in lines), encoding='utf-8')
print(f"\n✓ Saved transcript to: {out_txt}")
