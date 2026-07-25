import pypdf
import re

filepath = r"C:\Users\HP\Downloads\Adobe Downloads\dl\chen Combine February 28, 2026.pdf"
out_filepath = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\chen_extracted_text.txt"

print(f"Reading {filepath} and writing to {out_filepath}...")
try:
    reader = pypdf.PdfReader(filepath)
    with open(out_filepath, 'w', encoding='utf-8') as out_f:
        out_f.write(f"DUMP OF CHEN COMBINE PDF\n")
        out_f.write(f"Total pages: {len(reader.pages)}\n\n")
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            out_f.write(f"================ PAGE {i+1} ================\n")
            out_f.write(text)
            out_f.write("\n\n")
    print("Dump completed successfully!")
except Exception as e:
    print(f"Error: {e}")
