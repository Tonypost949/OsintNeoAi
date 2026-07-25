import zipfile
import os

zips = [
    r"C:\Users\HP\OneDrive - Post University,inc\files\T10000018579_2025-Mar-23-124354.zip",
    r"C:\Users\HP\OneDrive\Imports\txtdjdrop@gmail.com - Google Drive\T10000018579_2024-Nov-27-022844.zip"
]

def search_zip(path):
    if not os.path.exists(path):
        print(f"[!] ZIP not found: {path}")
        return
        
    print(f"\n[*] Scanning contents of ZIP: {path}")
    try:
        with zipfile.ZipFile(path, 'r') as zf:
            namelist = zf.namelist()
            print(f"    Total files inside: {len(namelist)}")
            
            # Print files matching EDR or 2025 or similar
            matches = [f for f in namelist if "edr" in f.lower() or "environmental" in f.lower() or "report" in f.lower()]
            if matches:
                print(f"    [+] Found {len(matches)} matching files:")
                for m in matches[:30]:
                    print(f"      - {m}")
                if len(matches) > 30:
                    print(f"      ... and {len(matches) - 30} more.")
            else:
                print("    [ ] No matching filenames found inside.")
    except Exception as e:
        print(f"    [ERROR] Failed to read ZIP: {e}")

for z in zips:
    search_zip(z)
