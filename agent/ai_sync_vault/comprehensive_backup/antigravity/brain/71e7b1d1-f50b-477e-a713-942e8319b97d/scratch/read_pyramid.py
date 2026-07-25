import zipfile
import pypdf
import io
import re

zip_path = r"C:\Users\HP\Downloads\Sources.zip"
chinese_char_re = re.compile(r"[\u4e00-\u9fff]")

try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        data = z.read("The-Pyramid-Code-English.pdf")
        pdf_file = io.BytesIO(data)
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        
        matches = chinese_char_re.findall(text)
        print(f"The-Pyramid-Code-English.pdf: {len(text)} chars, {len(matches)} Chinese chars.")
        if matches:
            print("Found Chinese characters!")
        
        # Write first 5000 chars of text to scratch file
        out_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\pyramid_text.txt"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Wrote text to pyramid_text.txt")
except Exception as e:
    print(f"Error: {e}")
