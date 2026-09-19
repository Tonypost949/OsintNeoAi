import os
import re
from pathlib import Path

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/docs")
]

# Specifically looking for WDID / Erosivity Waiver 8 30W004769, SWPPP, or SWRCB documents
TARGET_KEYWORDS = ["8 30w004769", "30w004769", "erosivity", "swrcb", "smarts"]
EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.html']

def scan_erosivity_waiver():
    print("[+] Hunting for SWRCB Erosivity Waiver No. 8 30W004769 and related SMARTS database entries...")
    hits = []
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists(): continue
        for root, _, files in os.walk(search_dir):
            for file in files:
                if Path(file).suffix.lower() not in EXTENSIONS: continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if any(k in content for k in TARGET_KEYWORDS):
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if any(k in line for k in TARGET_KEYWORDS):
                                    # Grab context
                                    start = max(0, i - 2)
                                    end = min(len(lines), i + 3)
                                    block = " ".join([l.strip() for l in lines[start:end]])
                                    block = re.sub(r'\s+', ' ', block)[:350]
                                    hits.append({
                                        "file": Path(filepath).name,
                                        "line": i+1,
                                        "context": block
                                    })
                except Exception:
                    pass

    if hits:
        print(f"\n[✓] Found {len(hits)} references to the Erosivity Waiver or SWRCB evasion:")
        # Deduplicate hits based on context snippet to avoid flooding terminal
        unique_contexts = set()
        for hit in hits:
            if hit['context'] not in unique_contexts:
                print(f"\n--- {hit['file']} (Line {hit['line']}) ---")
                print(f"  {hit['context']}")
                unique_contexts.add(hit['context'])
    else:
        print("[-] No specific documents found for Waiver 8 30W004769.")

if __name__ == "__main__":
    scan_erosivity_waiver()
