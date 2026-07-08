import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"G:\DL BACKUP\non profit data mercy house 2024-06-GSAFAC-0000355035.pdf"
OUTPUT_PATH = r"C:\Users\HP\OneDrive\Documents\opencode_work\mercy_house_990_text.txt"

if not os.path.exists(PDF_PATH):
    print(f"PDF not found: {PDF_PATH}")
    sys.exit(1)

print(f"Extracting text from: {PDF_PATH}")

try:
    import fitz
    doc = fitz.open(PDF_PATH)
    print(f"Pages: {doc.page_count}")

    all_text = []
    for i, page in enumerate(doc):
        text = page.get_text()
        all_text.append(f"\n--- PAGE {i+1} ---\n{text}")
        print(f"  Page {i+1}: {len(text)} chars")

    full_text = "\n".join(all_text)
    print(f"\nTotal text: {len(full_text)} chars")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"Saved to: {OUTPUT_PATH}")

    # Also print first 2000 chars for quick review
    print("\n--- FIRST 2000 CHARS ---")
    print(full_text[:2000])

except ImportError:
    import PyPDF2
    reader = PyPDF2.PdfReader(PDF_PATH)
    print(f"Pages: {len(reader.pages)}")
    all_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        all_text.append(f"\n--- PAGE {i+1} ---\n{text}")
        print(f"  Page {i+1}: {len(text)} chars")

    full_text = "\n".join(all_text)
    print(f"\nTotal text: {len(full_text)} chars")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"Saved to: {OUTPUT_PATH}")
