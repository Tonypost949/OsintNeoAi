import os
import re
from pathlib import Path
from collections import defaultdict

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data")
]

def scan_for_stormtech_context():
    print("[+] Hunting for exact 'StormTech' mentions and extracting surrounding records...")
    
    hits = defaultdict(list)
    files_scanned = 0
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists(): continue
        for root, _, files in os.walk(search_dir):
            for file in files:
                if not file.endswith(('.txt', '.md', '.csv', '.json', '.html')): continue
                filepath = os.path.join(root, file)
                files_scanned += 1
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if "stormtech" in content or "storm tech" in content:
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if "stormtech" in line or "storm tech" in line:
                                    # Grab context block
                                    start = max(0, i - 3)
                                    end = min(len(lines), i + 4)
                                    block = " ".join([l.strip() for l in lines[start:end]])
                                    # Clean up whitespace
                                    block = re.sub(r'\s+', ' ', block)[:400]
                                    hits[file].append(f"Line {i+1}: {block}")
                except Exception:
                    pass

    print(f"[✓] Scanned {files_scanned} files.")
    
    if not hits:
        print("[-] No StormTech matches found.")
    else:
        print(f"\n[✓] Found StormTech in {len(hits)} files:")
        for file, context in hits.items():
            print(f"\n--- {file} ---")
            for c in context[:3]:
                print(f"  {c}")

if __name__ == "__main__":
    scan_for_stormtech_context()
