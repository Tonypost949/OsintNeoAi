import os
from pathlib import Path

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/docs"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/AiRiCOSwarm/reports")
]
KEYWORDS = [
    "excavation", "digging", "soil removal", "waste haul", "hauler",
    "hazardous waste", "manifest", "disposal", "michael baker", "contractor"
]
EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.html', '.js', '.py']

def search():
    print("[+] Searching for excavation, waste hauling, and contractor records related to the HBNC site...")
    hits = []
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists(): continue
        for root, _, files in os.walk(search_dir):
            for file in files:
                if Path(file).suffix.lower() not in EXTENSIONS: continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            line_lower = line.lower()
                            # Look for waste/digging keywords in proximity to stormtech/hbnc context
                            if any(kw in line_lower for kw in KEYWORDS) and ("stormtech" in line_lower or "cameron" in line_lower or "hbnc" in line_lower or "17631" in line_lower or "17642" in line_lower):
                                hits.append(f"WASTE/DIGGING HIT in {Path(filepath).name} (Line {i+1}): {line.strip()[:150]}")
                except Exception:
                    pass
                    
    for h in set(hits):
        print(h)
    
    if not hits:
        print("[-] No direct text matches found for waste hauling/digging correlated to HBNC.")

if __name__ == "__main__":
    search()
