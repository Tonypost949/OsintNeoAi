import re

filepath = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\ingestion_plan_text.txt"
chinese_char_re = re.compile(r"[\u4e00-\u9fff]")

out_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\chinese_matches.txt"

print("Scanning ingestion_plan_text.txt for lines with Chinese characters...")
with open(filepath, 'r', encoding='utf-8') as f, open(out_path, 'w', encoding='utf-8') as out:
    for i, line in enumerate(f):
        if chinese_char_re.search(line):
            out.write(f"Line {i+1}: {line.strip()}\n")
            print(f"Line {i+1}: found Chinese (written to file)")
