import os
import zipfile

downloads_path = r"C:\Users\HP\Downloads"

print("Searching all zip files in Downloads for 'Chinese' or 'Translated'...")

for root, dirs, files in os.walk(downloads_path):
    for file in files:
        if file.lower().endswith('.zip'):
            filepath = os.path.join(root, file)
            try:
                with zipfile.ZipFile(filepath, 'r') as z:
                    for name in z.namelist():
                        if "chinese" in name.lower() or "translated" in name.lower():
                            print(f"MATCH in {filepath}: {name}")
            except Exception as e:
                pass
