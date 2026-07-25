import os
import zipfile
import datetime
import shutil

# Paths
BRAIN_DIR = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7"
OUTPUT_DIR = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent"
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
ZIP_NAME = f"HBNC_Criminal_Referral_Evidence_Pack_{TIMESTAMP}.zip"
ZIP_PATH = os.path.join(OUTPUT_DIR, ZIP_NAME)

# Files to include (Targeting the brain directory)
TARGET_EXTENSIONS = ('.pdf', '.md', '.csv')

def package_evidence():
    print("="*60)
    print("  OSINTNeoAi EVIDENCE PACKAGER  ")
    print("="*60)
    print(f"[PACKAGING] Scanning {BRAIN_DIR} for evidence files...")

    files_to_zip = []
    for root, dirs, files in os.walk(BRAIN_DIR):
        # Skip system generated folders
        if '.system_generated' in root:
            continue
        for file in files:
            if file.endswith(TARGET_EXTENSIONS):
                files_to_zip.append(os.path.join(root, file))

    if not files_to_zip:
        print("[!] No evidence files found.")
        return

    print(f"[PACKAGING] Found {len(files_to_zip)} evidentiary files. Creating archive...")

    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_zip:
            # Arcname ensures the zip structure is flat or clean, relative to brain dir
            arcname = os.path.relpath(file, BRAIN_DIR)
            zipf.write(file, arcname)
            print(f"  -> Added: {arcname}")

    print("="*60)
    print(f"[+] Evidence successfully packaged and sealed.")
    print(f"[+] Archive Path: {ZIP_PATH}")
    print("[INFO] You can now move this zip file directly to your external 500GB hard drive.")
    print("="*60)

if __name__ == "__main__":
    package_evidence()
