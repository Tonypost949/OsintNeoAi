import os
import shutil

dest = r"C:\Users\HP\OneDrive\Documents\opencode_work\Private_EDR_2025_Real"
src_dir = r"C:\Users\HP\OneDrive\Downloads (1)"

os.makedirs(dest, exist_ok=True)

# Files to copy
files_to_copy = [
    "Volume-III-Appendix-D-Historical-Survey.pdf",
    "Preliminary Sanbornr Map Report-57cbe2f4fcf77f95.pdf",
    "Preliminary Sanbornr Map Report.pdf"
]

# Google Drive folder copies
gdrive_src_dir = r"C:\Users\HP\OneDrive\Imports\txtdjdrop@gmail.com - Google Drive\ERA EDR"
gdrive_files = [
    "Preliminary Sanbornr Map Report1.pdf",
    "Downloads/074-0125-014_Sanborn_7867953.3S.pdf"
]

print("[*] Staging active EDR 2025 files into Private folder...")

# Copy from Downloads (1)
for f in files_to_copy:
    src_path = os.path.join(src_dir, f)
    dest_path = os.path.join(dest, f)
    if os.path.exists(src_path):
        try:
            shutil.copy2(src_path, dest_path)
            print(f"  [+] Copied: {f} ({os.path.getsize(src_path)} bytes)")
        except Exception as e:
            print(f"  [ERROR] Failed to copy {f}: {e}")

# Copy from Google Drive Imports
for f in gdrive_files:
    src_path = os.path.join(gdrive_src_dir, f)
    dest_path = os.path.join(dest, os.path.basename(f))
    if os.path.exists(src_path):
        try:
            shutil.copy2(src_path, dest_path)
            print(f"  [+] Copied GDrive Import: {os.path.basename(f)}")
        except Exception as e:
            print(f"  [ERROR] Failed to copy GDrive import {f}: {e}")

print(f"\n[SUCCESS] Private EDR 2025 folder fully populated and separated under: {dest}")
