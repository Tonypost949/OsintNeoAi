import re

html_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\855\content.md"

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("Searching for folder ID context:")
lines = content.splitlines()
for i, line in enumerate(lines):
    if "173mY5p0bvl_2SjiGdmExkoOKDYgj_loN" in line:
        print(f"Line {i+1}: {line[:300]}...")

print("\nLet's print some lines of all_scripts.js that mention '_INITIAL_DATA' or similar:")
try:
    with open("all_scripts.js", "r", encoding='utf-8') as f:
        js = f.read()
    for line in js.splitlines():
        if "INITIAL_DATA" in line:
            print(line[:300])
except Exception as e:
    print(f"Error reading all_scripts.js: {e}")
