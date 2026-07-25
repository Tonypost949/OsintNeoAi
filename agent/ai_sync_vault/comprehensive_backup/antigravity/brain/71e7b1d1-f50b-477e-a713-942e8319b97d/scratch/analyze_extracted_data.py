import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

base_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)"

print(f"Analyzing extracted data in: {base_dir}")

# Let's see the subdirectories and how many files are in each
for item in os.listdir(base_dir):
    item_path = os.path.join(base_dir, item)
    if os.path.isdir(item_path):
        files = []
        for root, dirs, filenames in os.walk(item_path):
            for f in filenames:
                files.append(os.path.join(root, f))
        print(f"Directory: {item} | Total files: {len(files)}")
        # Let's print the first 5 files inside
        for f in files[:5]:
            print(f"  - {os.path.relpath(f, base_dir)}")
            
# Let's check some high-value TXT files first
txt_dir = os.path.join(base_dir, "TXT")
if os.path.exists(txt_dir):
    print("\nAnalyzing files in TXT folder:")
    for f in os.listdir(txt_dir):
        fp = os.path.join(txt_dir, f)
        if os.path.isfile(fp):
            # Print size and first 5 lines of the file
            size_kb = os.path.getsize(fp) / 1024
            print(f"\n--- File: {f} | Size: {size_kb:.2f} KB ---")
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
                    lines = file_obj.readlines()
                    print(f"Total lines: {len(lines)}")
                    for line in lines[:10]:
                        print(f"  {line.strip()}")
                    if len(lines) > 10:
                        print("  ...")
            except Exception as e:
                print(f"  Error reading file: {e}")

# Let's check some LOG files
log_dir = os.path.join(base_dir, "LOG")
if os.path.exists(log_dir):
    print("\nAnalyzing files in LOG folder:")
    for f in os.listdir(log_dir):
        fp = os.path.join(log_dir, f)
        if os.path.isfile(fp):
            size_kb = os.path.getsize(fp) / 1024
            print(f"\n--- File: {f} | Size: {size_kb:.2f} KB ---")
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
                    lines = file_obj.readlines()
                    print(f"Total lines: {len(lines)}")
                    for line in lines[:10]:
                        print(f"  {line.strip()}")
                    if len(lines) > 10:
                        print("  ...")
            except Exception as e:
                print(f"  Error reading file: {e}")
