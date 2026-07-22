import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

def search_directory(directory, keywords):
    print(f"Searching directory: {directory} for keywords {keywords}")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.txt', '.md', '.csv', '.json', '.html')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    content_lower = content.lower()
                    for kw in keywords:
                        if kw.lower() in content_lower:
                            # Let's count occurrences and print some sample
                            occurrences = [m.start() for m in re.finditer(re.escape(kw.lower()), content_lower)]
                            print(f"\n[FOUND] File: {file} contains keyword '{kw}' ({len(occurrences)} times)")
                            # Let's print context for first 3 occurrences
                            lines = content.splitlines()
                            printed = 0
                            for idx, line in enumerate(lines):
                                if kw.lower() in line.lower():
                                    print(f"  Line {idx+1}: {line.strip()[:180]}")
                                    printed += 1
                                    if printed >= 5:
                                        print("  ... truncated ...")
                                        break
                except Exception as e:
                    pass

import re
search_directory(scratch_dir, ["213 n. gilbert", "213 gilbert", "632 n. east", "632 east", "632 north east", "covenant house"])
