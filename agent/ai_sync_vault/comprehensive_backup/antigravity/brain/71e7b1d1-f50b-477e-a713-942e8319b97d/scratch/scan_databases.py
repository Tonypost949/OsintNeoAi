import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

log_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)\LOG"
txt_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)\TXT"

def list_files(directory, name):
    if not os.path.exists(directory):
        print(f"{name} directory does not exist.")
        return
    print(f"\nListing files in {name} ({directory}):")
    files = os.listdir(directory)
    print(f"Total files: {len(files)}")
    for f in sorted(files)[:30]:
        fp = os.path.join(directory, f)
        print(f"  - {f} ({os.path.getsize(fp)} bytes)")
    if len(files) > 30:
        print(f"  ... and {len(files)-30} more files")

list_files(log_dir, "LOG")
list_files(txt_dir, "TXT")
