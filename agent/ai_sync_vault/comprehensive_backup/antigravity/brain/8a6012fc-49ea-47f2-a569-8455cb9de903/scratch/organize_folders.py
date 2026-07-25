import os
import shutil
import glob

# Destination folders
base_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work"
edr_dest = os.path.join(base_dir, "2025_EDR_Reports")
shelter_dest = os.path.join(base_dir, "Public_Shelter_Records")

os.makedirs(edr_dest, exist_ok=True)
os.makedirs(shelter_dest, exist_ok=True)

print(f"[*] Target Directories Created:")
print(f"    - EDR: {edr_dest}")
print(f"    - Shelter: {shelter_dest}")

# 1. Gather EDR files from multiple locations on the system
edr_sources = [
    r"C:\Users\HP\OneDrive - Post University,inc\files\*T10000018579*",
    r"C:\Users\HP\OneDrive\Downloads (1)\*T10000018579*",
    r"C:\Users\HP\Downloads\Adobe Downloads\*T10000018579*",
    r"C:\Users\HP\OneDrive\Imports\txtdjdrop@gmail.com - Google Drive\*T10000018579*"
]

copied_edr = 0
for src_pattern in edr_sources:
    for filepath in glob.glob(src_pattern):
        if os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            dest_path = os.path.join(edr_dest, filename)
            try:
                shutil.copy2(filepath, dest_path)
                print(f"  [+] Copied EDR: {filename}")
                copied_edr += 1
            except Exception as e:
                print(f"  [ERROR] Failed to copy {filename}: {e}")

# 2. Gather Public Shelter Records & Complaints
shelter_sources = [
    # In opencode_work text/doc sources
    r"C:\Users\HP\OneDrive\Documents\opencode_work\extracted_text\*Formal_Complaint*",
    r"C:\Users\HP\OneDrive\Documents\opencode_work\extracted_text\*HBNC*",
    r"C:\Users\HP\OneDrive\Documents\opencode_work\extracted_text\*Huntington_Beach*",
    r"C:\Users\HP\OneDrive\Documents\opencode_work\extracted_text\*geotracker.waterboards*",
    r"C:\Users\HP\OneDrive\Documents\opencode_work\phase1_esa.txt"
]

copied_shelter = 0
for src_pattern in shelter_sources:
    for filepath in glob.glob(src_pattern):
        if os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            dest_path = os.path.join(shelter_dest, filename)
            try:
                shutil.copy2(filepath, dest_path)
                print(f"  [+] Copied Shelter Record: {filename}")
                copied_shelter += 1
            except Exception as e:
                print(f"  [ERROR] Failed to copy {filename}: {e}")

print(f"\n[SUCCESS] Organizing completed!")
print(f"    - Total EDR Files Copied: {copied_edr}")
print(f"    - Total Shelter Record Files Copied: {copied_shelter}")
