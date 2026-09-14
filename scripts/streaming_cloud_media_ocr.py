import subprocess
import zipfile
import json
import os
import io
import time
import glob

BASE_DIR = r"C:\OsintNeoAi\data\takeouts\etp949609_takeout_20260913"
OCR_DIR = os.path.join(BASE_DIR, "OCR_Extracted_Text")
METAMEDIA_DIR = os.path.join(BASE_DIR, "metamedia")
REMOTE_BASE = "gdrive:Sharedall/takeouts all 22226"
TMP_CHUNK_DIR = r"C:\OsintNeoAi\data\takeout_chunks_tmp"

os.makedirs(OCR_DIR, exist_ok=True)
os.makedirs(METAMEDIA_DIR, exist_ok=True)
os.makedirs(TMP_CHUNK_DIR, exist_ok=True)

def run_cloud_media_ocr_pipeline():
    print("==================================================")
    print("STREAMING CLOUD MEDIA NEURAL OCR ENGINE")
    print(f"Target Remote: {REMOTE_BASE}")
    print(f"OCR Transcript Destination: {OCR_DIR}")
    print("==================================================")

    # Initialize EasyOCR
    try:
        import easyocr
        from PIL import Image
        print("[OCR ENGINE] Loading EasyOCR neural model into memory...")
        reader = easyocr.Reader(['en'], gpu=False)
        print("[✓] EasyOCR neural reader loaded successfully!")
    except Exception as e:
        print(f"[ERROR] Failed loading EasyOCR: {e}")
        return

    # List all remote zip files
    print("[RCLONE] Listing Takeout zip chunks from Google Drive...")
    res = subprocess.run(["rclone", "lsf", REMOTE_BASE, "--include", "*.zip"], capture_output=True, text=True)
    zip_list = [f.strip() for f in res.stdout.splitlines() if f.strip().endswith('.zip')]
    zip_list.sort()
    print(f"[RCLONE] Found {len(zip_list)} Takeout zip chunks.")

    img_exts = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.heic']

    # Process 2 zip chunks at a time to keep local disk usage under 4 GB
    BATCH_SIZE = 2

    for i in range(0, len(zip_list), BATCH_SIZE):
        batch = zip_list[i:i+BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(zip_list) + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"\n==========================================")
        print(f"[BATCH {batch_num}/{total_batches}] Downloading for Neural OCR: {batch}")
        print(f"==========================================")

        for zip_name in batch:
            print(f"[DOWNLOADING] {zip_name} -> {TMP_CHUNK_DIR}")
            dl_cmd = [
                "rclone", "copy", f"{REMOTE_BASE}/{zip_name}", TMP_CHUNK_DIR,
                "--retries", "10", "--low-level-retries", "20", "--drive-acknowledge-abuse"
            ]
            subprocess.run(dl_cmd)

            local_zip_path = os.path.join(TMP_CHUNK_DIR, zip_name)
            if os.path.exists(local_zip_path):
                print(f"[NEURAL OCR SCAN] Inspecting images inside {zip_name}...")
                try:
                    with zipfile.ZipFile(local_zip_path, 'r') as zf:
                        for item in zf.namelist():
                            lower = item.lower()
                            if any(lower.endswith(ext) for ext in img_exts):
                                img_name = os.path.basename(item)
                                txt_check = os.path.join(OCR_DIR, f"{img_name}.ocr.txt")
                                
                                if not os.path.exists(txt_check):
                                    try:
                                        img_bytes = zf.read(item)
                                        # Run EasyOCR on image bytes in memory
                                        res = reader.readtext(img_bytes)
                                        ocr_lines = [r[1] for r in res if len(r[1].strip()) > 1]
                                        
                                        if ocr_lines:
                                            full_text = "\n".join(ocr_lines)
                                            with open(txt_check, "w", encoding="utf-8") as out_fp:
                                                out_fp.write(f"SOURCE_IMAGE: {img_name}\n")
                                                out_fp.write(f"ARCHIVE_CHUNK: {zip_name}\n")
                                                out_fp.write(f"TIMESTAMP: {time.time()}\n")
                                                out_fp.write("="*60 + "\n\n")
                                                out_fp.write(full_text)
                                            print(f"  [★ OCR HIT] {img_name} -> {len(ocr_lines)} lines extracted")
                                    except Exception as img_err:
                                        pass
                except Exception as z_err:
                    print(f"  [ERROR] Reading zip {zip_name}: {z_err}")

                # Immediate cleanup of the raw zip chunk from local disk
                try:
                    os.remove(local_zip_path)
                    print(f"[CLEANUP] Deleted local chunk {zip_name} (Disk footprint: 0 MB)")
                except Exception:
                    pass

    print("\n[✓] ALL CLOUD TAKEOUT CHUNKS FULLY PROCESSED BY NEURAL OCR!")

if __name__ == "__main__":
    run_cloud_media_ocr_pipeline()
