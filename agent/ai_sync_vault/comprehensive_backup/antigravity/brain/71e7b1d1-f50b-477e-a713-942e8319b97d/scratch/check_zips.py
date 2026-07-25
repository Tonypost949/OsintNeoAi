import zipfile
import os

downloads_path = r"C:\Users\HP\Downloads"

for file in os.listdir(downloads_path):
    if file.lower().endswith('.zip'):
        filepath = os.path.join(downloads_path, file)
        print(f"\nZIP file: {filepath}")
        try:
            with zipfile.ZipFile(filepath, 'r') as z:
                # Print first 20 file paths in zip
                namelist = z.namelist()
                print(f"Total files: {len(namelist)}")
                for name in namelist[:20]:
                    print(f"  - {name}")
                if len(namelist) > 20:
                    print("  - ...")
        except Exception as e:
            print(f"  Error: {e}")
