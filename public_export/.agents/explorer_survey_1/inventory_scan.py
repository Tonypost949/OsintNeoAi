import os
import json
from pathlib import Path
from collections import defaultdict

def scan_dir(base_path, max_files_per_ext=10):
    stats = {
        "base_path": str(base_path),
        "exists": os.path.exists(base_path),
        "total_files": 0,
        "total_size_bytes": 0,
        "extensions": defaultdict(lambda: {"count": 0, "total_bytes": 0, "samples": []}),
        "subdirs": [],
        "errors": []
    }
    
    if not stats["exists"]:
        return stats
        
    try:
        subdirs = [d.name for d in Path(base_path).iterdir() if d.is_dir()]
        stats["subdirs"] = subdirs
    except Exception as e:
        stats["errors"].append(f"iterdir error: {e}")

    for root, dirs, files in os.walk(base_path):
        for f in files:
            stats["total_files"] += 1
            full_path = os.path.join(root, f)
            try:
                size = os.path.getsize(full_path)
                stats["total_size_bytes"] += size
                ext = Path(f).suffix.lower() or "(no extension)"
                
                ext_stat = stats["extensions"][ext]
                ext_stat["count"] += 1
                ext_stat["total_bytes"] += size
                if len(ext_stat["samples"]) < max_files_per_ext:
                    rel_path = os.path.relpath(full_path, base_path)
                    ext_stat["samples"].append({
                        "rel_path": rel_path,
                        "size_bytes": size,
                        "name": f
                    })
            except Exception as e:
                stats["errors"].append(f"file error {full_path}: {e}")

    return stats

evidence_stats = scan_dir("C:\\OsintNeoAi\\evidence")
downloads_stats = scan_dir("C:\\Users\\Amd949609\\Downloads")

with open("C:\\OsintNeoAi\\.agents\\explorer_survey_1\\inventory_evidence.json", "w", encoding="utf-8") as f:
    json.dump(evidence_stats, f, indent=2)

with open("C:\\OsintNeoAi\\.agents\\explorer_survey_1\\inventory_downloads.json", "w", encoding="utf-8") as f:
    json.dump(downloads_stats, f, indent=2)

print("Inventory scan complete. Saved to inventory_evidence.json and inventory_downloads.json")
