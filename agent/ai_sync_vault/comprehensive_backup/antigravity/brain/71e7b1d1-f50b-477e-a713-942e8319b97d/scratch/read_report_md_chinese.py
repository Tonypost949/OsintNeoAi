import re

filepath = r"C:\Users\HP\Downloads\report\report.md"
chinese_char_re = re.compile(r"[\u4e00-\u9fff]")

print(f"Reading {filepath}...")
with open(filepath, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if chinese_char_re.search(line):
            print(f"Line {i+1}: {line.strip()}")
