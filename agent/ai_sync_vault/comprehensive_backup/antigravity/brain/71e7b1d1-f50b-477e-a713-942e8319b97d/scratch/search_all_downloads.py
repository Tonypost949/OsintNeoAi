import os
import re
import pypdf
import zipfile

downloads_path = r"C:\Users\HP\Downloads"
chinese_char_re = re.compile(r"[\u4e00-\u9fff]")

print("Scanning all files under C:\\Users\\HP\\Downloads for Chinese characters...")

results = []

def extract_docx_text(filepath):
    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            xml_content = zip_ref.read('word/document.xml').decode('utf-8')
            # Extract text within <w:t> tags
            text_matches = re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml_content)
            return " ".join(text_matches)
    except Exception as e:
        return ""

def scan_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    try:
        if ext in ['.txt', '.md', '.json', '.xml', '.html', '.htm', '.js', '.py', '.csv']:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        elif ext == '.pdf':
            reader = pypdf.PdfReader(filepath)
            for page in reader.pages:
                text += page.extract_text() or ""
        elif ext == '.docx':
            text = extract_docx_text(filepath)
        # Check for Chinese
        matches = chinese_char_re.findall(text)
        if matches:
            results.append((filepath, len(matches), text[:200].replace('\n', ' ')))
    except Exception as e:
        pass

for root, dirs, files in os.walk(downloads_path):
    # Avoid scanning node modules or temp directories if any
    if "node_modules" in root or ".git" in root:
        continue
    for file in files:
        filepath = os.path.join(root, file)
        scan_file(filepath)

print(f"\nScan complete. Found {len(results)} files containing Chinese characters:")
for path, count, snippet in sorted(results, key=lambda x: x[1], reverse=True)[:50]:
    print(f"- {path}: {count} characters (Snippet: {snippet})")
