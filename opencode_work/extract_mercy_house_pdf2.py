import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"G:\DL BACKUP\non profit data mercy house 2024-06-GSAFAC-0000355035.pdf"
OUTPUT_PATH = r"C:\Users\HP\OneDrive\Documents\opencode_work\mercy_house_990_text.txt"

if not os.path.exists(PDF_PATH):
    print(f"PDF not found: {PDF_PATH}")
    sys.exit(1)

print(f"Extracting text via pdfminer: {PDF_PATH}")

from pdfminer.high_level import extract_text

full_text = extract_text(PDF_PATH)
print(f"Total chars: {len(full_text):,}")

with open(OUTPUT_PATH, 'w', encoding='utf-8', errors='replace') as fout:
    fout.write(full_text)

print(f"Saved to: {OUTPUT_PATH}")

# Preview
print("\n--- FIRST 3000 CHARS ---")
print(full_text[:3000])
