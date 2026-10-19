import os
import json
import easyocr
from pathlib import Path

reader = easyocr.Reader(['en'], gpu=False)

def ocr_album(album_dir, output_md):
    images = sorted(list(album_dir.glob('*.jpg')))
    print(f"\n=== RUNNING EASYOCR ACROSS {len(images)} IMAGES IN {album_dir.name} ===")
    
    lines = [
        f"# 📸 EASYOCR FULL TEXT INDEX FOR `{album_dir.name}`",
        f"**Total Processed Images:** {len(images)}",
        "",
        "---",
        ""
    ]
    
    for idx, img_path in enumerate(images):
        try:
            results = reader.readtext(str(img_path), detail=0)
            extracted_text = "\n".join(results)
        except Exception as e:
            extracted_text = f"[OCR Error: {e}]"
            
        print(f"[{idx+1}/{len(images)}] Processed {img_path.name} ({len(extracted_text)} chars)")
        lines.append(f"### Photo #{idx+1:02d} — `{img_path.name}`")
        lines.append(f"- **File Path:** [`{img_path}`](file:///{img_path.as_posix()})")
        lines.append("```text")
        lines.append(extracted_text if extracted_text else "[No Text Detected]")
        lines.append("```")
        lines.append("")
        
    output_md.write_text("\n".join(lines), encoding='utf-8')
    print(f"✓ Saved full OCR index to {output_md}")

if __name__ == '__main__':
    ocr_album(Path(r'C:\OsintNeoAi\scratch\album_W6cAZwiDkZQtkMKr7'), Path(r'C:\OsintNeoAi\evidence\album_W6cAZwiDkZQtkMKr7_easyocr_index.md'))
    ocr_album(Path(r'C:\OsintNeoAi\scratch\album_oHVp9WKkEdMpupYN6'), Path(r'C:\OsintNeoAi\evidence\album_oHVp9WKkEdMpupYN6_easyocr_index.md'))
