import os
import zipfile

BACKUP_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"
OUTPUT_DIR = r"C:\Users\HP\OneDrive\Documents\new_program_scratch\unzipped_data"

def inspect_and_unzip():
    print("[*] Initializing Forensic ZIP Discovery Loop...")
    if not os.path.exists(BACKUP_DIR):
        print(f"[-] Error: Backup directory not found at {BACKUP_DIR}")
        return
        
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    zip_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".zip")]
    print(f"[*] Found {len(zip_files)} ZIP files in backup directory.")
    
    for zf in zip_files:
        full_path = os.path.join(BACKUP_DIR, zf)
        size_mb = os.path.getsize(full_path) / (1024 * 1024)
        print(f" -> Found ZIP: {zf} ({size_mb:.2f} MB)")
        
        # Target specific interesting ZIP files (chats or conversations or brain)
        if any(keyword in zf.lower() for keyword in ["conversation", "brain", "agent", "opencode"]):
            target_extract_folder = os.path.join(OUTPUT_DIR, zf.replace(".zip", ""))
            if os.path.exists(target_extract_folder):
                print(f"   [!] Already unzipped: {target_extract_folder}")
                continue
                
            print(f"   [*] Unzipping {zf} to {target_extract_folder}...")
            try:
                with zipfile.ZipFile(full_path, "r") as zip_ref:
                    # Just extract markdown, text, and JSON files to avoid unzipping massive binary blobs
                    for member in zip_ref.namelist():
                        if member.endswith((".json", ".md", ".txt", ".jsonl", ".csv")):
                            zip_ref.extract(member, target_extract_folder)
                print(f"   [+] Successfully unzipped metadata from {zf}")
            except Exception as e:
                print(f"   [-] Failed to unzip {zf}: {e}")

if __name__ == "__main__":
    inspect_and_unzip()
