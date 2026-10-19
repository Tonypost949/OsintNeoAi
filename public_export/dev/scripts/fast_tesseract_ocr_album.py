import os
from pathlib import Path
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img_dir = Path(r'C:\OsintNeoAi\scratch\album_oHVp9WKkEdMpupYN6')
images = sorted(list(img_dir.glob('*.jpg')))
print(f"=== FAST OCR EXTRACTION FOR ALBUM oHVp9WKkEdMpupYN6 ({len(images)} PHOTOS) ===")

out_md = Path(r'C:\OsintNeoAi\evidence\album_oHVp9WKkEdMpupYN6_ocr_transcripts.md')
lines = [f"# 📸 GOOGLE PHOTOS ALBUM `oHVp9WKkEdMpupYN6` (42 PHOTOS) FULL OCR TRANSCRIPT\n"]

for idx, img_path in enumerate(images):
    try:
        txt = pytesseract.image_to_string(Image.open(img_path))
        clean_txt = txt.strip()
    except Exception as e:
        clean_txt = f"[Tesseract execution note: {e}]"
    
    print(f"[{idx+1}/{len(images)}] Scanned {img_path.name} ({len(clean_txt)} chars)")
    lines.append(f"## Photo #{idx+1:02d} — {img_path.name}")
    lines.append("```text")
    lines.append(clean_txt if clean_txt else "[No text detected]")
    lines.append("```\n")

out_md.write_text("\n".join(lines), encoding='utf-8')
print(f"\n✓ Saved 42-photo OCR transcript to {out_md}")
