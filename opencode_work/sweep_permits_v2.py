import os
import fitz  # pymupdf
from concurrent.futures import ThreadPoolExecutor, as_completed

manifest_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\permit_backups_manifest.txt"
targets = ["17642 Beach", "17631 Cameron"]
matches = []

print("=== Starting Targeted Permit Sweep (v2 - pymupdf) ===")

with open(manifest_path, "r", encoding="utf-8", errors="ignore") as f:
    files = [line.strip() for line in f if line.strip() and line.strip().lower().endswith('.pdf')]

print(f"Scanning {len(files)} PDF files for targets: {targets}...\n")

def scan_file(file_path):
    local_matches = []
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            text = doc[page_num].get_text()
            if not text:
                continue
            lower_text = text.lower()
            for target in targets:
                if target.lower() in lower_text:
                    hit = f"Match found in [{file_path}] on Page {page_num + 1} for '{target}'"
                    print(f"HIT: {hit}")
                    local_matches.append(hit)
        doc.close()
    except Exception as e:
        pass
    return local_matches

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(scan_file, fp): fp for fp in files}
    for future in as_completed(futures):
        matches.extend(future.result())

print("\n=== Sweep Complete ===")
print(f"Total target matches flagged: {len(matches)}")

output_log = r"C:\Users\HP\OneDrive\Documents\opencode_work\permit_search_hits.txt"
with open(output_log, "w", encoding="utf-8") as out:
    out.write("\n".join(matches))
print(f"Results saved to {output_log}")
