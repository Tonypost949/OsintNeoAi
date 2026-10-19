#!/usr/bin/env python3
"""
Cloud Dashboard Deployment Script (Google Cloud Shell / Azure App Service / Cloudflare Pages)
Bundles and prepares master_admin_dashboard.html and dependent sub-dashboards for 24/7 cloud hosting.
"""

import os
import sys
import shutil
import json
from pathlib import Path

WORKSPACE = Path(r"C:\OsintNeoAi")
BUILD_DIR = WORKSPACE / "opencode_work" / "cloud_dashboard_dist"

REQUIRED_FILES = [
    "master_admin_dashboard.html",
    "workspace_v2.html",
    "tasks.html",
    "osint_toolkit_hub.html",
    "badass_arcgis_tactical_map.html",
    "interactive_evidence_showcase.html",
    "taxfunded_explorer.html",
    "terminal.html"
]

def bundle_dashboard():
    print("[+] Preparing Cloud Dashboard Web Package...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    for fname in REQUIRED_FILES:
        src = WORKSPACE / fname
        if src.exists():
            shutil.copy2(src, BUILD_DIR / fname)
            print(f"  [✓] Bundled: {fname}")
        else:
            print(f"  [!] Warning: File {fname} not found in workspace root.")

    # Create index.html fallback
    shutil.copy2(WORKSPACE / "master_admin_dashboard.html", BUILD_DIR / "index.html")
    print("  [✓] Created index.html -> master_admin_dashboard.html")

    # Create Cloud Shell / Vercel / Netlify / Cloudflare deployment config
    manifest = {
        "name": "OsintNeoAi Master Admin Dashboard",
        "version": "2.0.0",
        "entry": "master_admin_dashboard.html",
        "cloud_targets": {
            "google_cloud_shell": "python3 -m http.server 8080 --directory .",
            "azure_app_service": "az webapp up --sku F1 --name osint-neo-ai-dash",
            "cloudflare_pages": "npx wrangler pages deploy ."
        }
    }

    with open(BUILD_DIR / "dashboard_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[+] Bundle complete at: {BUILD_DIR}")
    print("  Run 'python3 -m http.server 8080 --directory opencode_work/cloud_dashboard_dist' for local testing.")

if __name__ == "__main__":
    bundle_dashboard()
