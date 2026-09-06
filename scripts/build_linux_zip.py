#!/usr/bin/env python3
import os
import zipfile

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
zip_path = os.path.join(root_dir, "azure_deploy.zip")

files_to_include = [
    "app.py",
    "terminal.html",
    "OSINTNeoAiCLI_v2.py",
    "manifest.json",
    "service-worker.js",
    "requirements.txt"
]

dirs_to_include = ["scripts", "bin", "cli", "data"]

print("[*] Creating Linux-compatible azure_deploy.zip with forward slashes...")

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in files_to_include:
        fp = os.path.join(root_dir, f)
        if os.path.exists(fp):
            zf.write(fp, arcname=f)
            print(f" + Added file: {f}")

    for d in dirs_to_include:
        dp = os.path.join(root_dir, d)
        if os.path.exists(dp):
            for root, _, files in os.walk(dp):
                if "__pycache__" in root or ".git" in root:
                    continue
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, root_dir).replace("\\", "/")
                    zf.write(full_p, arcname=rel_p)
                    print(f" + Added: {rel_p}")

print(f"✓ Zip built successfully at: {zip_path}")
