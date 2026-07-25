import zipfile
import os

zips = [
    r"C:\Users\HP\Downloads\windows.zip",
    r"C:\Users\HP\Downloads\Sources.zip"
]

for z in zips:
    if os.path.exists(z):
        print(f"\nListing {z}:")
        with zipfile.ZipFile(z, 'r') as zip_ref:
            infos = zip_ref.infolist()
            print(f"Total files: {len(infos)}")
            # Print first 20 files
            for info in infos[:40]:
                print(f"  {info.filename} ({info.file_size} bytes)")
            if len(infos) > 40:
                print(f"  ... and {len(infos)-40} more files")
    else:
        print(f"{z} does not exist.")
