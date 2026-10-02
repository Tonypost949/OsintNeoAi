import fitz  # PyMuPDF
import easyocr
import subprocess
import os

pdf_path = r"C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\db66e1e0-b949-11f1-8e00-dbd4e67e7847.pdf"
out_txt = r"C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\db66e1e0-b949-11f1-8e00-dbd4e67e7847.pdf.txt"

print("Rasterizing PDF pages to images using PyMuPDF (fitz)...")
doc = fitz.open(pdf_path)
reader = easyocr.Reader(['en'], gpu=False)

extracted_text = ""

for page_index in range(len(doc)):
    page = doc[page_index]
    pix = page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")
    
    print(f"Running EasyOCR on Page {page_index + 1} / {len(doc)}...")
    results = reader.readtext(img_bytes)
    
    page_text = f"--- PAGE {page_index + 1} ---\n"
    for bbox, text, prob in results:
        page_text += f"{text}\n"
    
    extracted_text += page_text + "\n"

with open(out_txt, "w", encoding="utf-8") as f:
    f.write(extracted_text)

print(f"Neural OCR extraction complete. Saved {len(extracted_text)} characters to {out_txt}")

# Mirror to Google Drive
subprocess.run(["rclone", "copy", out_txt, "gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/20_ANALYSIS", "-v"])
print("Synced extracted text to Google Drive.")
