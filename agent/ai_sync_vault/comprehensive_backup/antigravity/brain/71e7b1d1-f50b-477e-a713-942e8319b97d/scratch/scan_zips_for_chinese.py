import zipfile
import re
import pypdf
import io

zip_path = r"C:\Users\HP\Downloads\Sources.zip"
chinese_char_re = re.compile(r"[\u4e00-\u9fff]")

print(f"Scanning files inside {zip_path} for Chinese characters...")

try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        for name in z.namelist():
            if name.lower().endswith('.pdf'):
                print(f"Reading {name}...")
                try:
                    data = z.read(name)
                    pdf_file = io.BytesIO(data)
                    reader = pypdf.PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() or ""
                    
                    matches = chinese_char_re.findall(text)
                    if matches:
                        print(f"🎯 FOUND CHINESE CHARACTERS in {name}: {len(matches)} matches!")
                        print(f"Snippet: {text[:300].replace('\n', ' ')}")
                    else:
                        # Check if it mentions "chinese" or "translate"
                        text_lower = text.lower()
                        if "chinese" in text_lower or "translate" in text_lower:
                            print(f"📝 Found 'Chinese'/'Translate' text reference in {name}!")
                            print(f"Snippet: {text[:300].replace('\n', ' ')}")
                except Exception as e:
                    print(f"Error reading {name}: {e}")
except Exception as e:
    print(f"Error: {e}")
