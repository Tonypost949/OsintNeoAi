import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
for f in os.listdir(scratch_dir):
    if "mercy" in f.lower() or "conflict" in f.lower() or "buntich" in f.lower() or "paval" in f.lower() or "shopoff" in f.lower() or "meli" in f.lower():
        print(f"Found file: {f} (Size: {os.path.getsize(os.path.join(scratch_dir, f))})")
