import os
import shutil

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
opencode_work_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work"

os.makedirs(opencode_work_dir, exist_ok=True)

files_to_copy = [
    "index.html",
    "load_procurement_to_bq.py",
    "scrape_oc_procurement.py",
    "scrape_oc_procurement_v2.py",
    "scrape_oc_procurement_v3.py",
    "scrape_project_details.py",
    "oc_procurement_projects.csv",
    "oc_procurement_projects.json",
    "oc_procurement_raw_text.txt",
    "oc_projects_api_data.json",
    "oc_procurement_files_full.json",
    "oc_procurement_files_index.csv",
    "oc_procurement_files_index_full.csv",
    "oc_procurement_index.csv"
]

for filename in files_to_copy:
    src = os.path.join(scratch_dir, filename)
    dst = os.path.join(opencode_work_dir, filename)
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Copied {filename} to {opencode_work_dir}")
    else:
        print(f"File not found in scratch: {filename}")

# Also let's check index.html in C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX
repo_dir = r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
if os.path.exists(repo_dir):
    shutil.copy2(os.path.join(scratch_dir, "index.html"), os.path.join(repo_dir, "index.html"))
    print(f"Copied index.html to active repository: {repo_dir}")
