import os
import zipfile

source_dir = r"C:\OsintNeoAi"
target_zip = r"C:\Users\HP\OsintNeoAi_Master_Backup.zip"

def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zipf:
        for root, _, files in os.walk(folder_path):
            if ".git" in root:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if file_path == zip_path:
                        continue
                    zipf.write(file_path, os.path.relpath(file_path, folder_path))
                except Exception as e:
                    print(f"Skipping {file_path}: {e}")

print("Starting to zip...")
zip_directory(source_dir, target_zip)
print("Zipping complete.")
