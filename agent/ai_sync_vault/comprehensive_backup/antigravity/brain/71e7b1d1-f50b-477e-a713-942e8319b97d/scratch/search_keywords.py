import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

md_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)\MD"
keywords = ["落查", "控", "小样", "万里", "渗透", "安洵", "i-soon", "isoon"]

print(f"Searching MD files in: {md_dir} for core keywords...")
md_files = [f for f in os.listdir(md_dir) if f.lower().endswith('.md')]

for filename in md_files:
    fp = os.path.join(md_dir, filename)
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            matches = []
            for i, line in enumerate(lines):
                for kw in keywords:
                    if kw in line:
                        matches.append((i+1, line.strip()))
                        break
            if matches:
                print(f"\nFile: {filename} - {len(matches)} matches")
                for line_num, line_content in matches[:10]: # show first 10 matches
                    print(f"  Line {line_num}: {line_content[:150]}")
                if len(matches) > 10:
                    print(f"  ... and {len(matches)-10} more matches")
    except Exception as e:
        print(f"Error reading {filename}: {e}")
