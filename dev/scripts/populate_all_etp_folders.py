import os
import glob
import shutil
import json
import time

base = r"C:\OsintNeoAi\data\takeouts\etp949609_takeout_20260913"
takeout_root = os.path.join(base, "Takeout")
sept11_dir = os.path.join(base, "sept_11_phone_theft_investigation")
data_dir = os.path.join(base, "data")
data_meta_dir = os.path.join(data_dir, "metadata")
metamedia_dir = os.path.join(base, "metamedia")

for d in [sept11_dir, data_dir, data_meta_dir, metamedia_dir]:
    os.makedirs(d, exist_ok=True)

print("[SYNC] Populating all folders from 8,732 Takeout files...")

media_exts = ['.jpg', '.jpeg', '.png', '.mp4', '.mov', '.heic', '.3gp', '.avi', '.gif']

all_files = [f for f in glob.glob(os.path.join(takeout_root, '**', '*.*'), recursive=True) if os.path.isfile(f)]
print(f"Found {len(all_files)} total files to categorize.")

data_count = 0
metamedia_count = 0
sept11_count = 0

for f in all_files:
    fname = os.path.basename(f)
    lower = fname.lower()
    
    # 1. Check for Sept 11 content
    try:
        if any(ext in lower for ext in ['.json', '.csv', '.html', '.txt']):
            with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                txt = fp.read()
                if 'sep 11' in txt.lower() or '2026-09-11' in txt or '09-11' in txt:
                    dest = os.path.join(sept11_dir, fname)
                    if not os.path.exists(dest):
                        shutil.copy2(f, dest)
                        sept11_count += 1
    except Exception:
        pass

    # 2. Check if it's media metadata (JSON sidecar)
    if lower.endswith('.json') and any(tag in f.lower() for tag in ['google photos', 'photos', 'img_', 'photo']):
        dest = os.path.join(metamedia_dir, fname)
        if not os.path.exists(dest):
            shutil.copy2(f, dest)
            metamedia_count += 1
            
    # 3. Check if it's non-media data (Mail, Chrome, Drive, Location, Contacts, Keep)
    elif not any(lower.endswith(ext) for ext in media_exts):
        dest = os.path.join(data_dir, fname)
        if not os.path.exists(dest):
            shutil.copy2(f, dest)
            data_count += 1
            
            # Generate summary in data/metadata/
            meta_dest = os.path.join(data_meta_dir, fname + ".meta.json")
            try:
                st = os.stat(f)
                meta_info = {
                    "filename": fname,
                    "original_path": f.replace(takeout_root, "Takeout"),
                    "size_bytes": st.st_size,
                    "modified_time": st.st_mtime
                }
                with open(meta_dest, 'w', encoding='utf-8') as mfp:
                    json.dump(meta_info, mfp, indent=2)
            except Exception:
                pass

print(f"\n[✓] SYNC COMPLETE:")
print(f"  - September 11 Investigation Files: {sept11_count}")
print(f"  - Non-Media Data Files in data/: {data_count} (Metadata index in data/metadata/)")
print(f"  - Photo/Video Metadata in metamedia/: {metamedia_count}")
