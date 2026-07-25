import zipfile
import pypdf
import io
import re

zip_path = r"C:\Users\HP\Downloads\Sources.zip"
keywords = ["isoon", "i-soon", "anxun", "an-xun", "apt", "chinese", "translate", "translation", "china", "shanghai"]

print(f"Scanning files inside {zip_path} for I-Soon or Chinese references...")

try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        for name in z.namelist():
            if name.lower().endswith('.pdf'):
                try:
                    data = z.read(name)
                    pdf_file = io.BytesIO(data)
                    reader = pypdf.PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() or ""
                    
                    text_lower = text.lower()
                    found_kws = [kw for kw in keywords if kw in text_lower]
                    if found_kws:
                        print(f"MATCH: {name} contains {found_kws}")
                        lines = text.split('\n')
                        for line in lines:
                            for kw in found_kws:
                                if kw in line.lower():
                                    print(f"  Snippet ({kw}): {line.strip()[:120]}")
                                    break
                except Exception as e:
                    print(f"Error reading {name}: {e}")
except Exception as e:
    print(f"Error: {e}")
