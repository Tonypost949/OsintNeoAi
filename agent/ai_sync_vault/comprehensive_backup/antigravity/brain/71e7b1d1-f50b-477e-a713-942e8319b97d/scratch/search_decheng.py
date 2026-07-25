import os
import re

downloads_path = r"C:\Users\HP\Downloads"
target_words = ["decheng", "deceng", "深圳市", "德诚"]

print("Searching for files containing Decheng or related keywords...")
matches = []

for root, dirs, files in os.walk(downloads_path):
    for file in files:
        filepath = os.path.join(root, file)
        # Only check text-like files, word docs, pdfs
        ext = os.path.splitext(file)[1].lower()
        if ext in ['.txt', '.md', '.json', '.xml', '.html', '.htm', '.js', '.py', '.csv', '.docx']:
            try:
                if ext == '.docx':
                    import zipfile
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        content = zip_ref.read('word/document.xml').decode('utf-8', errors='ignore')
                else:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                
                content_lower = content.lower()
                for word in target_words:
                    if word.lower() in content_lower:
                        matches.append((filepath, word))
                        print(f"MATCH found in {filepath} for word: {word}")
                        break
            except Exception as e:
                pass

print(f"Total matches found: {len(matches)}")
