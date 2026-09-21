import os
import re
import json

DOWNLOADS_DIR = r"C:\Users\Amd949609\Downloads"
KEYWORDS = ["stormtech", "hbnc", "plumbing", "permit", "corrosion", "wrapped", "blueprint", "pipe"]

results = []

for root, dirs, files in os.walk(DOWNLOADS_DIR):
    for f in files:
        file_path = os.path.join(root, f)
        f_lower = f.lower()
        
        # Check filename match
        matched_filename = [k for k in KEYWORDS if k in f_lower]
        
        # Text inspection if HTML or TXT
        matched_text = []
        if f_lower.endswith((".html", ".htm", ".txt", ".json")):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as content_file:
                    text = content_file.read().lower()
                    matched_text = [k for k in KEYWORDS if k in text]
            except Exception:
                pass

        if matched_filename or matched_text:
            results.append({
                "filename": f,
                "path": file_path,
                "matched_in_name": matched_filename,
                "matched_in_content": matched_text,
                "size_bytes": os.path.getsize(file_path)
            })

print(f"Total matching files found in Downloads: {len(results)}")
for r in results:
    print(f"\n[+] File: {r['filename']}")
    print(f"    Path: {r['path']}")
    print(f"    Name Matches: {r['matched_in_name']}")
    print(f"    Content Matches: {r['matched_in_content']}")

with open(r"C:\OsintNeoAi\evidence\downloads_stormtech_corrosion_search.json", "w", encoding="utf-8") as out:
    json.dump(results, out, indent=2)
