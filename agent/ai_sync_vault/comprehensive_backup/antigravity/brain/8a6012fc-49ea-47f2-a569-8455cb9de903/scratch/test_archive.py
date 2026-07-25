import tarfile
from pathlib import Path

archive_path = Path(r"C:\Users\HP\OneDrive\Documents\opencode_work_backup\AG2OSINTNEOMAXX_20260702.tar.gz")

try:
    with tarfile.open(archive_path, "r") as tar:
        print("Archive is valid. Listing first 10 files:")
        names = tar.getnames()
        for name in names[:10]:
            print(f" - {name}")
except Exception as e:
    print(f"Failed to open archive: {e}")
