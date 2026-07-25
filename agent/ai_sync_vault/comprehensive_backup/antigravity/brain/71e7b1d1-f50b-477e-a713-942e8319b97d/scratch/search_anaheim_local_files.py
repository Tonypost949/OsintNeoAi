import os
import re

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

def search_file(filename, keywords):
    filepath = os.path.join(scratch_dir, filename)
    if not os.path.exists(filepath):
        print(f"File {filename} does not exist!")
        return
    print(f"\n==================================================")
    print(f"SEARCHING IN: {filename}")
    print(f"==================================================")
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Split by common delimiters or lines
    lines = content.splitlines()
    print(f"Total lines: {len(lines)}")
    
    # Find matching lines
    matches = []
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw.lower() in line_lower for kw in keywords):
            matches.append((idx + 1, line))
            
    print(f"Found {len(matches)} matching lines.")
    # Show first 50 matches
    for line_num, text in matches[:50]:
        print(f"Line {line_num}: {text[:150]}")
    if len(matches) > 50:
        print(f"... and {len(matches) - 50} more matches.")

search_file("anaheim_details.txt", ["Gilbert", "East", "Covenant"])
search_file("anaheim_gilbert_east_covenant_matches.txt", ["Gilbert", "East", "Covenant"])
