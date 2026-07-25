import os
import re

text_path = r"C:\Users\HP\Downloads\Data-Ingestion-and-Extraction-Plan.docx"
target_file = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\ingestion_plan_text.txt"

keywords = ["chinese", "translate", "decheng", "shenzhen", "yamada", "chen"]

with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

lines = text.split('\n')
print(f"Total lines: {len(lines)}")

for i, line in enumerate(lines):
    line_lower = line.lower()
    for kw in keywords:
        if kw in line_lower:
            print(f"Line {i+1} ({kw}): {line.strip()[:150]}")
