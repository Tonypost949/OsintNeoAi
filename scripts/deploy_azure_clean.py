"""
scripts/deploy_azure_clean.py
=============================
Clean, Self-Contained Azure App Service Deployment Package Creator & Deployer.
Bundles all API modules, graph assets (nodes.json, edges.json), essential evidence datasets,
and scripts for complete autonomous execution in Azure App Service under 30 seconds.
"""

import os
import sys
import zipfile
import subprocess
from pathlib import Path

# Resolve dynamic root
THIS_FILE = Path(__file__).resolve()
ROOT_DIR_PATH = THIS_FILE.parents[1] if THIS_FILE.parents[1].name != "scripts" else THIS_FILE.parents[1]
if not (ROOT_DIR_PATH / "nodes.json").exists():
    for cand in [Path("/home/site/wwwroot"), Path("C:/OsintNeoAi"), Path.cwd()]:
        if (cand / "nodes.json").exists():
            ROOT_DIR_PATH = cand
            break

ROOT_DIR = str(ROOT_DIR_PATH)
ZIP_PATH = os.path.join(ROOT_DIR, "azure_deploy.zip")

INCLUDE_DIRS = ["api", "makavelli", "tools", "core", "public", "data", "scripts", "reports"]
EXCLUDE_PATTERNS = ["__pycache__", ".git", ".venv", "node_modules", ".pytest_cache", ".agents"]
EXCLUDE_EVIDENCE_SUBDIRS = [
    "google_photos", "google_photos_all", "google_photos_evidence",
    "google_photos_evidence_batch2", "google_photos_evidence_batch3",
    "google_photos_evidence_batch4", "google_photos_evidence_batch5",
    "google_photos_evidence_batch6", "google_photos_evidence_batch7",
    "google_photos_evidence_batch8", "lawsuit_info_full_dimarcello",
    "screenshots", "ocr_transcripts_photos"
]

INCLUDE_FILES = [
    "app.py",
    "OSINTNeoAiCLI.py",
    "gods_eye_view.html",
    "maps_hub.html",
    "requirements.txt",
    "nodes.json",
    "edges.json",
    "control_clusters.json",
    "openapi_azure_powerapps.json",
    "startup.sh"
]


def create_deployment_package(deploy_to_azure: bool = False) -> str:
    print(f"[1/3] Packaging clean self-contained deployment zip from {ROOT_DIR}...")
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in INCLUDE_FILES:
            fp = os.path.join(ROOT_DIR, f)
            if os.path.exists(fp):
                z.write(fp, f)
                print(f"  + Added root file: {f}")

        # Add include directories
        for d in INCLUDE_DIRS:
            dp = os.path.join(ROOT_DIR, d)
            if os.path.exists(dp):
                for root, dirs, files in os.walk(dp):
                    # Filter out excluded directory patterns
                    dirs[:] = [dr for dr in dirs if not any(ep in dr for ep in EXCLUDE_PATTERNS)]
                    for file in files:
                        if file.endswith(".pyc"):
                            continue
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, ROOT_DIR)
                        z.write(full_p, rel_p)
                print(f"  + Added directory: {d}/")

        # Add essential evidence files & selective subdirectories
        evidence_dp = os.path.join(ROOT_DIR, "evidence")
        if os.path.exists(evidence_dp):
            for root, dirs, files in os.walk(evidence_dp):
                dirs[:] = [dr for dr in dirs if dr not in EXCLUDE_EVIDENCE_SUBDIRS and not any(ep in dr for ep in EXCLUDE_PATTERNS)]
                for file in files:
                    if file.endswith((".png", ".jpg", ".jpeg", ".mp4", ".mov", ".zip", ".tar", ".gz")):
                        continue
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, ROOT_DIR)
                    z.write(full_p, rel_p)
            print("  + Added directory: evidence/ (excluding large photo archives)")

    zip_size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    print(f"[2/3] Package built: {ZIP_PATH} ({zip_size_mb:.2f} MB)")

    if deploy_to_azure:
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
    else:
        print("[3/3] Deployment packaging complete (dry-run/package only).")

    return ZIP_PATH


if __name__ == "__main__":
    deploy = "--deploy" in sys.argv
    create_deployment_package(deploy_to_azure=deploy)
