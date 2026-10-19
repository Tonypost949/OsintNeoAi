import os
import json
from pathlib import Path

def inspect_evidentiary_files(dir_path):
    target_exts = {'.pdf', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.html', '.htm', '.eml', '.msg', '.mbox', '.docx', '.json', '.csv', '.txt', '.zip'}
    files_info = []
    
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in target_exts:
                full_path = os.path.join(root, f)
                try:
                    size = os.path.getsize(full_path)
                    files_info.append({
                        "filename": f,
                        "ext": ext,
                        "rel_path": os.path.relpath(full_path, dir_path),
                        "full_path": full_path,
                        "size_bytes": size,
                        "size_mb": round(size / (1024 * 1024), 2)
                    })
                except Exception as e:
                    pass
    return files_info

ev_files = inspect_evidentiary_files("C:\\OsintNeoAi\\evidence")
dl_files = inspect_evidentiary_files("C:\\Users\\Amd949609\\Downloads")

print(f"Evidence target files: {len(ev_files)}")
print(f"Downloads target files: {len(dl_files)}")

with open("C:\\OsintNeoAi\\.agents\\explorer_survey_1\\evidentiary_files_list.json", "w", encoding="utf-8") as f:
    json.dump({"evidence": ev_files, "downloads": dl_files}, f, indent=2)

print("Saved detailed list to evidentiary_files_list.json")
