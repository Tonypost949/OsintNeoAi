#!/usr/bin/env python3
"""
Forensic Extractor Script
Recursively scans the evidence/ directory, generates SHA-256 hashes for chain-of-custody,
and attempts to extract EXIF metadata (if applicable).
Outputs to evidence_ledger.csv.
"""

import os
import hashlib
import csv
from datetime import datetime

# Pillow is needed for EXIF, but we will wrap it in a try/except so it degrades gracefully
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

EVIDENCE_DIR = "/data/data/com.termux/files/home/osintneoai/evidence"
OUTPUT_CSV = "/data/data/com.termux/files/home/osintneoai/evidence_ledger.csv"

def hash_file(filepath):
    """Generate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256.update(block)
        return sha256.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"

def extract_exif(filepath):
    """Extract basic EXIF data if it is an image."""
    if not HAS_PIL:
        return "Install Pillow (pip install Pillow) for EXIF extraction"
    
    if not filepath.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        return "N/A (Not an image)"
    
    try:
        img = Image.open(filepath)
        exif_data = img.getexif()
        if not exif_data:
            return "No EXIF Data Found"
        
        extracted = []
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag in ['DateTime', 'DateTimeOriginal', 'Make', 'Model', 'Software']:
                extracted.append(f"{tag}: {value}")
        
        return " | ".join(extracted) if extracted else "No relevant EXIF found"
    except Exception as e:
        return f"EXIF ERROR: {str(e)}"

def main():
    print(f"[*] Scanning directory: {EVIDENCE_DIR}")
    if not os.path.exists(EVIDENCE_DIR):
        print("[!] Evidence directory not found.")
        return

    records = []
    
    for root, dirs, files in os.walk(EVIDENCE_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            print(f"[*] Processing: {file}")
            
            # Gather metadata
            file_size = os.path.getsize(filepath)
            created = datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            sha256_hash = hash_file(filepath)
            exif_info = extract_exif(filepath)
            
            records.append({
                "Filename": file,
                "Path": filepath,
                "Size (Bytes)": file_size,
                "System_Created": created,
                "SHA-256": sha256_hash,
                "EXIF_Data": exif_info
            })

    # Write to CSV
    if records:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Filename", "Path", "Size (Bytes)", "System_Created", "SHA-256", "EXIF_Data"])
            writer.writeheader()
            writer.writerows(records)
        print(f"\n[+] Successfully processed {len(records)} files.")
        print(f"[+] Forensic ledger saved to: {OUTPUT_CSV}")
    else:
        print("[-] No files found to process.")

if __name__ == "__main__":
    main()
