import os
import pypdf

pdf_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\Jesse_Knabb_v_City_of_Huntington_Beach_et_al__cacdce-26-00348__0001.0.pdf"

print("Scanning the Jesse Knabb lawsuit PDF for disgrace...")

try:
    reader = pypdf.PdfReader(pdf_path)
    found = False
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for line_num, line in enumerate(text.split('\n'), 1):
            if "disgrace" in line.lower():
                print(f"MATCH on Page {idx+1}, Line {line_num}:")
                print(f"  {line.strip()}")
                found = True
    if not found:
        print("No matches for 'disgrace' in the PDF file.")
except Exception as e:
    print(f"Error reading PDF: {e}")
