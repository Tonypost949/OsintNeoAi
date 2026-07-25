import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

md_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)\MD"

print(f"Analyzing MD folder contents in: {md_dir}")
md_files = [f for f in os.listdir(md_dir) if f.lower().endswith('.md')]
print(f"Found {len(md_files)} markdown files.")

# Let's inspect files with simple numbered names first (like 1.md, 2.md)
numbered_files = sorted([f for f in md_files if re.match(r'^\d+\.md$', f)], key=lambda x: int(os.path.splitext(x)[0]))
print(f"Numbered MD files: {numbered_files}")

for f in numbered_files[:15]:
    fp = os.path.join(md_dir, f)
    print(f"\n=========================================")
    print(f"File: {f} | Size: {os.path.getsize(fp)} bytes")
    print(f"=========================================")
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
            content = file_obj.read()
            # Print first 500 characters
            print(content[:600])
            if len(content) > 600:
                print("\n... [TRUNCATED] ...")
    except Exception as e:
        print(f"Error reading file: {e}")
