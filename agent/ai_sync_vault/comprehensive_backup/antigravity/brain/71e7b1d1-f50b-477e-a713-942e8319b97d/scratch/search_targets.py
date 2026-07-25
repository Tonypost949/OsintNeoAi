import os
import re
import pypdf
import zipfile

target_dirs = [
    r"C:\Users\HP\Downloads",
    r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
]

keywords = [
    "yuxi", "雨希", "tai", "djibouti", "guinea", "cambodia", "柬埔寨", 
    "congo", "macedonia", "timor", "east timor", "australia"
]

print("Scanning for targets...")
results = []

def extract_docx_text(filepath):
    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            xml_content = zip_ref.read('word/document.xml').decode('utf-8')
            text_matches = re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml_content)
            return " ".join(text_matches)
    except Exception as e:
        return ""

for target_dir in target_dirs:
    for root, dirs, files in os.walk(target_dir):
        if "node_modules" in root or ".git" in root or ".venv" in root or ".agents" in root:
            continue
        for file in files:
            filepath = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            text = ""
            try:
                if ext in ['.txt', '.md', '.json', '.xml', '.html', '.htm', '.js', '.py', '.csv', '.bat', '.ps1']:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                elif ext == '.pdf':
                    reader = pypdf.PdfReader(filepath)
                    for page in reader.pages:
                        text += page.extract_text() or ""
                elif ext == '.docx':
                    text = extract_docx_text(filepath)
                
                text_lower = text.lower()
                found_kws = []
                for kw in keywords:
                    if kw in text_lower:
                        found_kws.append(kw)
                
                if found_kws:
                    results.append((filepath, found_kws))
                    print(f"MATCH: {filepath} contains {found_kws}")
            except Exception as e:
                pass

print(f"\nScan complete. Found {len(results)} matching files.")
