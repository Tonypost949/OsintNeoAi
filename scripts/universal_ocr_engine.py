import os
import sys
import json
import time
from pathlib import Path
from PIL import Image
import easyocr

def run_universal_ocr(input_path):
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"❌ Error: File not found: {input_path}")
        return None

    print("=========================================================")
    print(f"  🧠 NEURAL UNIVERSAL OCR ENGINE — PROCESSING: {input_path.name}")
    print("=========================================================")

    # Initialize EasyOCR Deep Learning Reader
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(str(input_path))

    lines = []
    for bbox, text, prob in results:
        if prob > 0.15:
            lines.append(text)

    transcript_text = "\n".join(lines)
    print("\n✓ EXTRACTED TRANSCRIPT PREVIEW:")
    print("---------------------------------------------------------")
    for l in lines[:20]:
        print(f"  • {l}")
    print("---------------------------------------------------------")

    # Save permanent transcript evidence
    out_dir = Path(r'C:\OsintNeoAi\evidence\ocr_transcripts')
    out_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"OCR_TRANSCRIPT_{input_path.stem}_{timestamp}.md"
    
    content = f"# 🖼️ NEURAL OCR TRANSCRIPT\n"
    content += f"- **Source File:** `{input_path}`\n"
    content += f"- **Timestamp:** `{timestamp}`\n"
    content += f"- **Extracted Lines:** {len(lines)}\n\n"
    content += "## Extracted Text:\n```text\n" + transcript_text + "\n```\n"

    out_file.write_text(content, encoding='utf-8')
    print(f"\n✓ Permanent Transcript Saved: {out_file}")
    return transcript_text

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_universal_ocr(sys.argv[1])
    else:
        # Default run on last downloaded screenshot
        target = Path(r'C:\OsintNeoAi\scratch\github_billing_screenshot.png')
        if target.exists():
            run_universal_ocr(target)
