import os
import shutil

src_root = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
dest_root = r"C:\Users\HP\OneDrive\Documents\OsintNeoAi"

items_to_copy = [
    ("OSINTNeoAI-Core", "dir"),
    ("briefings", "dir"),
    ("briefings_data.js", "file"),
    ("knowledge_base.html", "file"),
    ("setup_kb.py", "file"),
    ("forensic_master_spreadsheet.csv", "file"),
    ("nodes.json", "file"),
    ("edges.json", "file")
]

print("--- Consolidating Files to OsintNeoAi Repo ---")

for item, itype in items_to_copy:
    src_path = os.path.join(src_root, item)
    dest_path = os.path.join(dest_root, item)
    
    if os.path.exists(src_path):
        if itype == "dir":
            # Remove dest if it exists to overwrite completely
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            print(f"[OK] Copied directory {item} to {dest_path}")
        else:
            shutil.copy2(src_path, dest_path)
            print(f"[OK] Copied file {item} to {dest_path}")
    else:
        print(f"[WARNING] Source {item} not found at {src_path}")

print("--- Transfer Complete ---")
