import zipfile
import os
import sys

# Ensure stdout uses utf-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

zips = [
    r"C:\Users\HP\OneDrive\Documents\drive-download-20260629T205840Z-3-001.zip",
    r"C:\Users\HP\OneDrive\Documents\drive-download-20260629T205840Z-3-002.zip"
]

for filepath in zips:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
    print(f"\nListing ZIP file: {filepath}")
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            namelist = z.namelist()
            print(f"Total files inside ZIP: {len(namelist)}")
            
            # Let's count files by directory/category or extension
            categories = {}
            for name in namelist:
                _, ext = os.path.splitext(name)
                ext = ext.lower()
                categories[ext] = categories.get(ext, 0) + 1
            print("Files by extension:")
            for ext, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {ext if ext else '[No Extension/Directory]'}: {count}")
                
            # Let's list the first 100 file paths safely
            print("\nFirst 100 files/folders inside:")
            for name in namelist[:100]:
                try:
                    # Some zip libraries decode paths as cp437 or utf-8
                    # ZipFile namelist returns string directly
                    print(f"  - {name}")
                except Exception as e:
                    print(f"  - [Path encoding error]: {repr(name)}")
            if len(namelist) > 100:
                print("  - ...")
                
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
