import os
import shutil

src_dirs = [
    r"C:\Users\HP\Downloads\deepseek_data-2026-07-02",
    r"C:\Users\HP\Downloads\deepseek_data-2026-07-02 (1)"
]

dst_parent = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

print("Copying DeepSeek directories to scratch...")

for idx, src in enumerate(src_dirs):
    if os.path.exists(src):
        dst_name = f"deepseek_data_{idx}"
        dst = os.path.join(dst_parent, dst_name)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"  Copied {src} to {dst}")
    else:
        print(f"  Source not found: {src}")

print("Copy process complete.")
