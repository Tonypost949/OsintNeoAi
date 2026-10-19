import os
import csv
from pathlib import Path

WORKSPACE_DIR = r"C:\OsintNeoAi"
GITHUB_BASE_URL = "https://github.com/Tonypost949/OsintNeoAi/blob/main"
OUTPUT_CSV = r"C:\OsintNeoAi\repository_paths.csv"

# Directories to exclude from the listing
EXCLUDE_DIRS = {
    '.git', 'node_modules', 'venv', '__pycache__', '.gemini', '.github',
    'extracted_backup', 'archive', 'backups'
}

def should_exclude(path):
    parts = Path(path).relative_to(WORKSPACE_DIR).parts
    return any(p in EXCLUDE_DIRS for p in parts)

def generate_sheet():
    files_list = []

    for root, dirs, files in os.walk(WORKSPACE_DIR):
        # Modify dirs in-place to avoid descending into excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]

        for file in files:
            full_local_path = os.path.join(root, file)
            if should_exclude(full_local_path):
                continue

            relative_path = os.path.relpath(full_local_path, WORKSPACE_DIR)
            # Normalize to forward slashes for URL pathing
            url_path = relative_path.replace(os.sep, '/')
            github_url = f"{GITHUB_BASE_URL}/{url_path}"

            files_list.append({
                "Local Path": full_local_path,
                "GitHub URL": github_url
            })

    # Write to CSV
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Local Path", "GitHub URL"])
        writer.writeheader()
        for entry in files_list:
            writer.writerow(entry)

    print(f"Spreadsheet generated: {OUTPUT_CSV}")
    print(f"Total files cataloged: {len(files_list)}")

if __name__ == "__main__":
    generate_sheet()
