import os
import re

downloads_path = r"C:\Users\HP\Downloads"

chinese_char_re = re.compile(r"[\u4e00-\u9fff]")

print("Scanning for files containing Chinese characters...")

def is_text_file(filepath):
    # Check simple text file extensions
    ext = os.path.splitext(filepath)[1].lower()
    return ext in [".txt", ".md", ".json", ".csv", ".html", ".htm", ".xml", ".js", ".py"]

results = []

for root, dirs, files in os.walk(downloads_path):
    # Skip some binary folders or large zip/tmp files if needed
    for file in files:
        filepath = os.path.join(root, file)
        if not is_text_file(filepath):
            continue
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = chinese_char_re.findall(content)
                if matches:
                    results.append((filepath, len(matches)))
        except Exception as e:
            pass

results.sort(key=lambda x: x[1], reverse=True)
for path, count in results[:30]:
    print(f"{path}: {count} Chinese characters")
