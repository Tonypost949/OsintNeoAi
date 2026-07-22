import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

md_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)\MD"
output_file = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\us_db_search_output.txt"

print("Scanning chat markdown files...")

keywords = ["美国", "美数据", "美国数据", "fbi", "cia", "pentagon", "mail", "mail.gov", "unclaimed", "laundering", "vietnam", "tv", "电视"]
results = []

for file in os.listdir(md_dir):
    if file.endswith('.md'):
        filepath = os.path.join(md_dir, file)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    for kw in keywords:
                        if kw in line.lower():
                            start_idx = max(0, i - 2)
                            end_idx = min(len(lines), i + 3)
                            snippet = "".join(lines[start_idx:end_idx])
                            results.append(f"=== FILE: {file} | LINE {i+1} | Keyword: {kw} ===\n{snippet}\n")
                            break
        except Exception as e:
            print(f"Error reading {file}: {e}")

with open(output_file, 'w', encoding='utf-8') as out:
    out.write(f"Found {len(results)} occurrences:\n\n")
    out.write("\n".join(results))

print(f"Done! Written {len(results)} occurrences to {output_file}")
