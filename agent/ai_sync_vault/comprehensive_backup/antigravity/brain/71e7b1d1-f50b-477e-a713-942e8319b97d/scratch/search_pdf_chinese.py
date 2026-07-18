import os
import re
import pypdf

downloads_path = r"C:\Users\HP\Downloads"
chinese_char_re = re.compile(r"[\u4e00-\u9fff]")

print("Scanning PDFs for Chinese characters...")

results = []

for root, dirs, files in os.walk(downloads_path):
    for file in files:
        if file.lower().endswith('.pdf'):
            filepath = os.path.join(root, file)
            try:
                reader = pypdf.PdfReader(filepath)
                text = ""
                # Scan up to first 5 pages for efficiency
                for page in reader.pages[:5]:
                    text += page.extract_text() or ""
                matches = chinese_char_re.findall(text)
                if matches:
                    results.append((filepath, len(matches)))
            except Exception as e:
                pass

results.sort(key=lambda x: x[1], reverse=True)
print(f"Found {len(results)} PDFs with Chinese characters:")
for path, count in results[:30]:
    print(f"{path}: {count} Chinese characters found in first 5 pages")
