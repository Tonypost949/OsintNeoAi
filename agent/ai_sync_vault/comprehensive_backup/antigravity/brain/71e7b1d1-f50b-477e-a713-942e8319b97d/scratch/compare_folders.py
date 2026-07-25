import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

md_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)\MD"
orig_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)\ORIGINAL\I-S00N\0"

md_files = set(os.listdir(md_dir))
orig_files = set(os.listdir(orig_dir))

diff = orig_files - md_files
print(f"Files found in ORIGINAL but missing from MD ({len(diff)} files):")
for f in sorted(diff):
    fp = os.path.join(orig_dir, f)
    print(f"  - {f} ({os.path.getsize(fp)} bytes)")
