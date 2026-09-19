import os
import sys
import glob
import json
import re

EVIDENCE_DIR = r"C:\OsintNeoAi\evidence\lawsuit_info_full_dimarcello"
OUTPUT_DIR = os.path.join(EVIDENCE_DIR, "ocr_transcripts")
INDEX_FILE = os.path.join(EVIDENCE_DIR, "FULL_OCR_EVIDENCE_INDEX.md")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    from rapidocr_onnxruntime import RapidOCR
    import pymupdf  # PyMuPDF
    from PIL import Image
    import io

    ocr = RapidOCR()
    print("✓ RapidOCR initialized successfully.")

    files = sorted(os.listdir(EVIDENCE_DIR))
    results = []

    for filename in files:
        filepath = os.path.join(EVIDENCE_DIR, filename)
        if os.path.isdir(filepath) or filename.startswith("FULL_OCR") or filename.endswith(".py"):
            continue

        ext = os.path.splitext(filename)[1].lower()
        print(f"\n[*] Processing: {filename}...")
        extracted_text = ""

        # 1. Images (PNG, JPG)
        if ext in [".png", ".jpg", ".jpeg"]:
            try:
                res, _ = ocr(filepath)
                if res:
                    extracted_text = "\n".join([line[1] for line in res])
                else:
                    extracted_text = "[NO DETECTABLE TEXT IN IMAGE]"
            except Exception as e:
                extracted_text = f"[OCR ERROR: {e}]"

        # 2. PDFs
        elif ext == ".pdf":
            try:
                doc = pymupdf.open(filepath)
                total_pages = len(doc)
                print(f"    - PDF Pages: {total_pages}")
                for page_idx in range(total_pages):
                    page = doc[page_idx]
                    page_text = page.get_text("text").strip()
                    
                    # If page text is minimal (e.g. scanned image), render and OCR
                    if len(page_text) < 50:
                        pix = page.get_pixmap(dpi=150)
                        img_bytes = pix.tobytes("png")
                        res, _ = ocr(img_bytes)
                        if res:
                            page_text = "\n".join([line[1] for line in res])
                        else:
                            page_text = "[SCANNED PAGE - NO TEXT RECOGNIZED]"
                    
                    extracted_text += f"\n--- Page {page_idx + 1} ---\n" + page_text
            except Exception as e:
                extracted_text = f"[PDF ERROR: {e}]"

        # 3. HTML / Text
        elif ext in [".html", ".txt", ".json"]:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()
            except Exception as e:
                extracted_text = f"[TEXT READ ERROR: {e}]"

        # Save individual transcript
        txt_path = os.path.join(OUTPUT_DIR, f"{filename}.txt")
        with open(txt_path, "w", encoding="utf-8", errors="ignore") as out_f:
            out_f.write(extracted_text)

        print(f"    ✓ Extracted {len(extracted_text):,} characters -> {txt_path}")
        results.append({
            "filename": filename,
            "char_count": len(extracted_text),
            "snippet": extracted_text[:300].replace("\n", " ")
        })

    print(f"\n[✓] Deep Neural OCR complete across {len(results)} files!")

if __name__ == "__main__":
    main()
