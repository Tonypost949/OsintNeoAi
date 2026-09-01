"""
Clean, Lightweight Azure App Service Deployment Package Creator & Deployer
Excludes multi-gigabyte CSVs and data folders to deploy in under 30 seconds.
"""

import os
import sys
import zipfile
import subprocess

ROOT_DIR = r"C:\OSINTNEOAI"
ZIP_PATH = os.path.join(ROOT_DIR, "azure_deploy.zip")

INCLUDE_DIRS = ["api", "makavelli", "tools", "core", "public", "data"]
INCLUDE_FILES = ["app.py", "OSINTNeoAiCLI.py", "gods_eye_view.html", "maps_hub.html", "requirements.txt"]

print("[1/3] Packaging clean deployment zip...")
with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for f in INCLUDE_FILES:
        fp = os.path.join(ROOT_DIR, f)
        if os.path.exists(fp):
            z.write(fp, f)
            print(f"  + Added file: {f}")

    for d in INCLUDE_DIRS:
        dp = os.path.join(ROOT_DIR, d)
        if os.path.exists(dp):
            for root, _, files in os.walk(dp):
                if "__pycache__" in root or ".git" in root:
                    continue
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, ROOT_DIR)
                    z.write(full_p, rel_p)
            print(f"  + Added directory: {d}/")

zip_size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
print(f"[2/3] Package built: {ZIP_PATH} ({zip_size_mb:.2f} MB)")

print("[3/3] Deploying package to Azure App Service: osintneoai-app-949...")
cmd = [
    "az", "webapp", "deploy",
    "--resource-group", "neoai-rg",
    "--name", "osintneoai-app-949",
    "--src-path", ZIP_PATH,
    "--type", "zip"
]

res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
print(res.stdout)
if res.stderr:
    print("[STDERR]", res.stderr)
print("[DEPLOY FINISHED]")
