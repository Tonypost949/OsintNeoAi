import os
import shutil

private_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work\Private_EDR_2025_Real"
third_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work\Misc_Research_Docs_Review"

os.makedirs(third_dir, exist_ok=True)

# EDR order number patterns — these stay in Private_EDR_2025_Real
# 7887036 series (Cameron/HBNC), 7969270 series (May order), 074-0125 (Sanborn sheet), Volume-III-Appendix-D (EDR deliverable)
EDR_KEEP_PATTERNS = [
    "7887036", "78870367", "78870369", "788703618", "788703620",
    "7969270", "79692706", "79692707",
    "074-0125-014_Sanborn",
    "Volume-III-Appendix-D-Historical-Survey.pdf"  # Real EDR Appendix D (42MB)
]

print("[*] Sorting Private_EDR_2025_Real — removing junk, moving non-EDR docs to 3rd folder...\n")

for fname in os.listdir(private_dir):
    fpath = os.path.join(private_dir, fname)
    fsize = os.path.getsize(fpath)

    # Check if it matches any EDR order pattern
    is_real_edr = any(fname.startswith(pat) or fname == pat for pat in EDR_KEEP_PATTERNS)

    if is_real_edr:
        print(f"  [KEEP] {fname} ({fsize/1024/1024:.1f}MB)")
        continue

    # Zero-byte AI exports — delete them
    if fsize == 0:
        os.remove(fpath)
        print(f"  [DELETED 0-byte junk] {fname}")
        continue

    # Non-EDR, non-zero files — move to 3rd folder
    dest_path = os.path.join(third_dir, fname)
    try:
        shutil.move(fpath, dest_path)
        print(f"  [MOVED to 3rd folder] {fname} ({fsize/1024/1024:.1f}MB)")
    except Exception as e:
        print(f"  [ERROR] Could not move {fname}: {e}")

print(f"\n[DONE]")
print(f"\n=== Private_EDR_2025_Real (Real EDR Orders Only) ===")
for f in sorted(os.listdir(private_dir)):
    size = os.path.getsize(os.path.join(private_dir, f))
    print(f"  {f} ({size/1024/1024:.1f}MB)")

print(f"\n=== Misc_Research_Docs_Review (3rd Folder) ===")
for f in sorted(os.listdir(third_dir)):
    size = os.path.getsize(os.path.join(third_dir, f))
    print(f"  {f} ({size/1024/1024:.1f}MB)")
