"""
ocr_17642_sar_tesseract.py
Batch OCR for T10000018579.20200625.Site Assessment Report.pdf
using PyMuPDF (fitz) + pytesseract (Tesseract 5.4.0)
Renders each page at 150 DPI -> runs tesseract -> saves full text.
Designed for CPU-only, ~10-20s per page (much faster than EasyOCR CPU).
"""
import sys
import os
import time
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Set Tesseract path (winget installs here by default)
TESS_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\Amd949609\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]
for tp in TESS_PATHS:
    if os.path.exists(tp):
        pytesseract.pytesseract.tesseract_cmd = tp
        print(f"[OCR] Tesseract found at: {tp}")
        break
else:
    print("[OCR] WARNING: Tesseract not found at known paths — will attempt system PATH")

PDF_PATH = r"C:\EVIDENCE_LOCKER_MASTER\01_ESA\HISTORIC FILES - SITE ASSESSMENT REPORT - T10000018579.20200625.Site Assessment Report.pdf"
OUT_PATH = r"C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\FULL_LOCKER_NEURAL_OCR\01_ESA_HISTORIC FILES - SITE ASSESSMENT REPORT - T10000018579.20200625.Site Assessment Report.pdf.ocr.txt"
DPI = 150
START_PAGE = 0  # 0-indexed; set to 5 to resume from page 6

def ocr_pdf(pdf_path, out_path, dpi=150, start_page=0):
    doc = fitz.open(pdf_path)
    total = len(doc)
    print(f"[OCR] Document: {pdf_path}")
    print(f"[OCR] Total pages: {total} | Starting from page {start_page + 1} | DPI: {dpi}")

    # Load existing text if resuming
    existing_text = ""
    if start_page > 0 and os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            existing_text = f.read()
        print(f"[OCR] Resuming — existing output: {len(existing_text):,} bytes")

    mode = "w" if start_page == 0 else "a"

    with open(out_path, mode, encoding="utf-8") as out:
        if start_page == 0 and existing_text:
            out.write(existing_text)

        for page_num in range(start_page, total):
            t0 = time.time()
            page = doc[page_num]

            # Render to pixmap at DPI
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
            img_data = pix.tobytes("png")

            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))

            # Run Tesseract
            text = pytesseract.image_to_string(img, lang="eng", config="--oem 3 --psm 6")

            out.write(f"\n--- PAGE {page_num + 1} ---\n")
            out.write(text)
            out.flush()

            elapsed = time.time() - t0
            remaining = (total - page_num - 1) * elapsed
            print(f"[OCR] Page {page_num + 1}/{total} done in {elapsed:.1f}s | "
                  f"Est. remaining: {remaining/60:.1f} min | "
                  f"Text chars: {len(text):,}")

    doc.close()
    print(f"\n[OCR] COMPLETE. Output written to: {out_path}")

if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else START_PAGE
    ocr_pdf(PDF_PATH, OUT_PATH, dpi=DPI, start_page=start)
