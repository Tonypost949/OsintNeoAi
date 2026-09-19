import os
from pathlib import Path

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/docs"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/AiRiCOSwarm/reports")
]
KEYWORDS = ["stormtech", "storm tech", "sewer", "anomaly", "vault"]
EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.html', '.js', '.py']

def search():
    print("[+] Searching for 'stormtech', 'sewer', 'vault', 'anomaly'...")
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
                            if "stormtech" in line_lower or "storm tech" in line_lower:
                                hits.append(f"STORMTECH HIT in {Path(filepath).name} (Line {i+1}): {line.strip()[:150]}")
                            elif "sewer" in line_lower and ("cameron" in line_lower or "hbnc" in line_lower or "anomaly" in line_lower or "vault" in line_lower):
                                hits.append(f"SEWER+CONTEXT HIT in {Path(filepath).name} (Line {i+1}): {line.strip()[:150]}")
                except Exception:
                    pass
                    
    for h in set(hits):
        print(h)
    
    if not hits:
        print("[-] No direct text matches found for 'StormTech' or correlated 'sewer/anomaly'.")

if __name__ == "__main__":
    search()
