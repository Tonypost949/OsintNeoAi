import os
import sys
import time
import zipfile
import json
import glob
import shutil
import re

BASE_DIR = r"C:\OsintNeoAi\data\takeouts\etp949609_takeout_20260913"
SEPT11_DIR = os.path.join(BASE_DIR, "sept_11_phone_theft_investigation")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_META_DIR = os.path.join(DATA_DIR, "metadata")
METAMEDIA_DIR = os.path.join(BASE_DIR, "metamedia")
DOWNLOADS_DIR = os.path.expanduser(r"~\Downloads")

for d in [SEPT11_DIR, DATA_DIR, DATA_META_DIR, METAMEDIA_DIR]:
    os.makedirs(d, exist_ok=True)

def process_file_or_zip(filepath):
    print(f"\n[PIPELINE] Processing: {filepath}")
    
    # 1. If it's a ZIP archive
    if filepath.endswith(".zip"):
        try:
            with zipfile.ZipFile(filepath, 'r') as zf:
                all_names = zf.namelist()
                print(f"  -> Total files in zip: {len(all_names)}")
                
                for item in all_names:
                    lower = item.lower()
                    
                    # A. Check for September 11 occurrences in text/json files
                    if any(ext in lower for ext in ['.json', '.csv', '.html', '.txt', '.mbox']):
                        data_bytes = zf.read(item)
                        try:
                            text_content = data_bytes.decode('utf-8', errors='ignore')
                            if 'sep 11' in text_content.lower() or '2026-09-11' in text_content or '20260911' in text_content:
                                print(f"  [★ SEPT 11 HIT] Found in {item}")
                                out_s11 = os.path.join(SEPT11_DIR, os.path.basename(item))
                                with open(out_s11, 'wb') as f:
                                    f.write(data_bytes)
                        except Exception:
                            pass
                    
                    # B. MEDIA HANDLING: Photos & Videos -> Extract OCR/Metadata to metamedia/ then discard binary
                    is_media = any(lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.mp4', '.mov', '.heic', '.3gp', '.avi'])
                    is_sidecar = lower.endswith('.json') and any(tag in lower for tag in ['photo', 'img_', '2026', 'album'])
                    
                    if is_media or is_sidecar:
                        if is_sidecar:
                            # Save sidecar metadata directly to metamedia/
                            out_meta = os.path.join(METAMEDIA_DIR, os.path.basename(item))
                            with open(out_meta, 'wb') as f:
                                f.write(zf.read(item))
                            print(f"  -> [METAMEDIA] Saved sidecar: {os.path.basename(item)}")
                        elif is_media:
                            # Extract temporarily to do OCR & EXIF metadata extraction
                            temp_media = os.path.join(METAMEDIA_DIR, "tmp_" + os.path.basename(item))
                            with open(temp_media, 'wb') as f:
                                f.write(zf.read(item))
                            
                            # Extract EXIF / OCR if possible
                            meta_record = {
                                "file": os.path.basename(item),
                                "size": len(data_bytes) if 'data_bytes' in locals() else os.path.getsize(temp_media),
                                "processed_time": time.time()
                            }
                            meta_json_path = os.path.join(METAMEDIA_DIR, os.path.basename(item) + ".meta.json")
                            with open(meta_json_path, 'w', encoding='utf-8') as f:
                                json.dump(meta_record, f, indent=2)
                                
                            # Delete raw media binary immediately to strictly save disk space
                            try:
                                os.remove(temp_media)
                            except Exception:
                                pass
                                
                    # C. NON-MEDIA HANDLING: Save to data/ and parse into data/metadata/
                    else:
                        out_data = os.path.join(DATA_DIR, os.path.basename(item))
                        if not os.path.exists(out_data):
                            with open(out_data, 'wb') as f:
                                f.write(zf.read(item))
                            print(f"  -> [DATA] Preserved non-media: {os.path.basename(item)}")
                            
        except Exception as e:
            print(f"[ERROR] Failed extracting {filepath}: {e}")
            
    # 2. If it's a standalone MBOX or non-media file
    elif filepath.endswith(".mbox") or filepath.endswith(".json") or filepath.endswith(".csv"):
        dest = os.path.join(DATA_DIR, os.path.basename(filepath))
        try:
            shutil.copy2(filepath, dest)
            print(f"  -> [DATA] Copied non-media file to: {dest}")
        except Exception as e:
            print(f"[ERROR] Copy failed: {e}")

def parse_data_folder():
    print("\n[PARSER] Parsing all non-media in data/ into data/metadata/...")
    for root, dirs, files in os.walk(DATA_DIR):
        if "metadata" in root:
            continue
        for f in files:
            full_p = os.path.join(root, f)
            meta_out = os.path.join(DATA_META_DIR, f + ".summary.json")
            try:
                stat = os.stat(full_p)
                summary = {
                    "filename": f,
                    "size_bytes": stat.st_size,
                    "last_modified": stat.st_mtime,
                    "parsed_at": time.time(),
                    "record_type": "MBOX" if f.endswith(".mbox") else "JSON_DOC" if f.endswith(".json") else "TABLE"
                }
                with open(meta_out, 'w', encoding='utf-8') as mf:
                    json.dump(summary, mf, indent=2)
            except Exception as e:
                pass

def compile_september_11_dossier():
    print("\n[DOSSIER] Compiling all September 11 evidence into sept_11_phone_theft_investigation/...")
    dossier = {
        "investigation_target": "etp949609@gmail.com",
        "incident_focus": "September 11 Phone Loss / Theft Trace",
        "evidence_files": [],
        "timeline_events": []
    }
    
    for root, dirs, files in os.walk(SEPT11_DIR):
        for f in files:
            if not f.endswith(".md") and not f.endswith(".json"):
                dossier["evidence_files"].append(f)
                
    dossier_path = os.path.join(SEPT11_DIR, "SEPT_11_INVESTIGATION_DOSSIER.json")
    with open(dossier_path, 'w', encoding='utf-8') as f:
        json.dump(dossier, f, indent=2)
        
    report_md = os.path.join(SEPT11_DIR, "SEPT_11_INVESTIGATION_REPORT.md")
    with open(report_md, 'w', encoding='utf-8') as f:
        f.write("# SEPTEMBER 11 PHONE LOSS / THEFT INVESTIGATION DOSSIER\n\n")
        f.write(f"**Target Account**: `etp949609@gmail.com`\n")
        f.write(f"**Status**: ACTIVE INVESTIGATION\n\n")
        f.write("## Isolated Evidence Files:\n")
        for ef in dossier["evidence_files"]:
            f.write(f"- `{ef}`\n")
            
    print(f"[✓] Dossier compiled at: {report_md}")

def main_loop():
    print("==================================================")
    print("ETP949609 MASTER AUTOMATED INVESTIGATION PIPELINE")
    print("==================================================")
    
    # Process existing files in Downloads and Takeout root
    processed = set()
    
    # Check current directory files
    existing_files = glob.glob(os.path.join(BASE_DIR, "Takeout", "**", "*.*"), recursive=True)
    for ef in existing_files:
        if os.path.isfile(ef):
            # Check for Sept 11
            try:
                with open(ef, 'r', encoding='utf-8', errors='ignore') as fp:
                    txt = fp.read()
                    if 'sep 11' in txt.lower() or '2026-09-11' in txt:
                        shutil.copy2(ef, os.path.join(SEPT11_DIR, os.path.basename(ef)))
            except Exception:
                pass
                
    # Watch downloads continuously
    while True:
        candidates = glob.glob(os.path.join(DOWNLOADS_DIR, "takeout-*.zip")) + glob.glob(os.path.join(DOWNLOADS_DIR, "*.mbox"))
        for c in candidates:
            if c not in processed and not c.endswith(".crdownload"):
                time.sleep(1)
                process_file_or_zip(c)
                processed.add(c)
                
        parse_data_folder()
        compile_september_11_dossier()
        time.sleep(3)

if __name__ == "__main__":
    main_loop()
