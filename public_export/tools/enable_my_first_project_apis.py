#!/usr/bin/env python3
"""
Enable Key Google Cloud APIs on 'My First Project' (project-2c88fd11-2b1e-44c5-b89)
and AI Studio project (project-1a000f44-d2c5-42f6-abf).
"""

import os
import subprocess
import sys
import json

PROJECTS = [
    "project-2c88fd11-2b1e-44c5-b89",
    "project-1a000f44-d2c5-42f6-abf"
]

SERVICES = [
    "generativelanguage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudbilling.googleapis.com",
    "aiplatform.googleapis.com"
]

def enable_apis():
    print("[+] Enabling Google Cloud APIs for active billing projects...")
    
    for proj in PROJECTS:
        print(f"\n[+] Processing Project: {proj}")
        for svc in SERVICES:
            cmd = f"gcloud services enable {svc} --project={proj}"
            print(f"  [>] Executing: {cmd}")
            try:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                if res.returncode == 0:
                    print(f"  [✓] Enabled {svc} on {proj}")
                else:
                    print(f"  [!] Output ({res.returncode}): {res.stderr.strip() or res.stdout.strip()}")
            except Exception as e:
                print(f"  [!] Error enabling {svc}: {e}")

if __name__ == "__main__":
    enable_apis()
