import os
import time
import zipfile
import json
import glob

DOWNLOADS_DIR = os.path.expanduser(r"~\Downloads")
TARGET_DIR = r"C:\OsintNeoAi\data\takeouts\etp949609_takeout_20260913"

os.makedirs(TARGET_DIR, exist_ok=True)

def watch_and_extract():
    print(f"[WATCHER] Monitoring {DOWNLOADS_DIR} for incoming 2026 Takeout downloads...")
    print(f"[WATCHER] Destination: {TARGET_DIR}")
    
    processed = set()
    
    while True:
        # Look for any new zip files or mbox files in Downloads
        files = glob.glob(os.path.join(DOWNLOADS_DIR, "takeout-*.zip")) + glob.glob(os.path.join(DOWNLOADS_DIR, "*.mbox"))
        
        for f in files:
            # Make sure it's not a .crdownload (incomplete Chrome download)
            if f not in processed and not f.endswith(".crdownload"):
                # Wait for file to finish writing
                time.sleep(1)
                print(f"\n[NEW DOWNLOAD DETECTED] Processing: {f}")
                
                if f.endswith(".zip"):
                    try:
                        with zipfile.ZipFile(f, 'r') as zf:
                            print(f"[EXTRACTING] Unpacking {len(zf.namelist())} files into {TARGET_DIR}...")
                            zf.extractall(TARGET_DIR)
                            print(f"[✓] Extraction complete for {os.path.basename(f)}")
                            
                            # Immediately search for September 11 records inside extracted files
                            for item in zf.namelist():
                                lower = item.lower()
                                if any(term in lower for term in ['location', 'records.json', 'semantic', 'activity', 'history', 'chrome', 'mail']):
                                    extracted_path = os.path.join(TARGET_DIR, item)
                                    if os.path.exists(extracted_path) and os.path.isfile(extracted_path):
                                        print(f"  -> Critical file extracted: {item}")
                    except Exception as e:
                        print(f"[ERROR] Failed to extract {f}: {e}")
                elif f.endswith(".mbox"):
                    try:
                        dest = os.path.join(TARGET_DIR, os.path.basename(f))
                        import shutil
                        shutil.copy2(f, dest)
                        print(f"[✓] Copied MBOX to {dest}")
                    except Exception as e:
                        print(f"[ERROR] Failed to copy mbox {f}: {e}")
                        
                processed.add(f)
                
        time.sleep(2)

if __name__ == "__main__":
    watch_and_extract()
