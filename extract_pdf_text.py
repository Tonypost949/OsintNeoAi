import fitz
import sys
import os

def extract(pdf_path, txt_path):
    print(f"Extracting {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for i, page in enumerate(doc):
            text += f"\n--- PAGE {i+1} ---\n"
            text += page.get_text()
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Extracted {len(text)} chars to {txt_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract(sys.argv[1], sys.argv[2])
