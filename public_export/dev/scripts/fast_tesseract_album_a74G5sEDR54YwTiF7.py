import os
import pytesseract
from PIL import Image
from pathlib import Path

# Config pytesseract path if available or PIL inspection
img_dir = Path(r'C:\OsintNeoAi\scratch\album_a74G5sEDR54YwTiF7')
images = sorted(list(img_dir.glob('*.jpg')))
print(f"=== FULL OCR SCAN FOR ALBUM a74G5sEDR54YwTiF7 ({len(images)} IMAGES) ===")

out_md = Path(r'C:\OsintNeoAi\evidence\album_a74G5sEDR54YwTiF7_full_ocr_index.md')
lines = [
    f"# 📸 GOOGLE PHOTOS ALBUM `a74G5sEDR54YwTiF7` (131 PHOTOS) FULL OCR TRANSCRIPT",
    f"**Source Shared Album:** https://photos.app.goo.gl/a74G5sEDR54YwTiF7",
    f"**Total Processed Images:** {len(images)}",
    "",
    "---",
    ""
]

for idx, img_path in enumerate(images):
    try:
        txt = pytesseract.image_to_string(Image.open(img_path))
        clean_txt = txt.strip()
    except Exception as e:
        clean_txt = f"[OCR Note: {e}]"
    
    print(f"[{idx+1}/{len(images)}] Scanned {img_path.name}")
    lines.append(f"### Photo #{idx+1:03d} — `{img_path.name}`")
    lines.append(f"- **Path:** [`{img_path}`](file:///{img_path.as_posix()})")
    lines.append("```text")
    lines.append(clean_txt if clean_txt else "[No text detected]")
    lines.append("```")
    lines.append("")

out_md.write_text("\n".join(lines), encoding='utf-8')
print(f"✓ Saved 131-photo OCR transcript index to {out_md}")
