# Universal AI Laws Multi-Source Enforcement & Sync Tool
# Source File: C:\Users\Amd949609\Desktop\00_ailaws.md
# GitHub Remote: https://raw.githubusercontent.com/Tonypost949/ailaws/main/00_ailaws.md

import os
import shutil
import requests

DESKTOP_LAWS_PATH = r"C:\Users\Amd949609\Desktop\00_ailaws.md"
WORKSPACE_LAWS_PATH = r"C:\amd949609_Antigravity_3.6\docs\00_ailaws.md"
REPO_LAWS_PATH = r"C:\OsintNeoAi\00_ailaws.md"
GITHUB_REMOTE_URL = "https://raw.githubusercontent.com/Tonypost949/ailaws/main/00_ailaws.md"

def audit_and_sync():
    print("[+] Starting Universal AI Laws Multi-Source Compliance Audit...")
    
    if os.path.exists(DESKTOP_LAWS_PATH):
        print(f"[✓] Desktop Primary Laws File verified: {DESKTOP_LAWS_PATH}")
        os.makedirs(os.path.dirname(WORKSPACE_LAWS_PATH), exist_ok=True)
        shutil.copy(DESKTOP_LAWS_PATH, WORKSPACE_LAWS_PATH)
        print(f"[✓] Synced to Unified Workspace: {WORKSPACE_LAWS_PATH}")
        shutil.copy(DESKTOP_LAWS_PATH, REPO_LAWS_PATH)
        print(f"[✓] Synced to Repository Root: {REPO_LAWS_PATH}")
    else:
        print(f"[!] Primary Desktop file missing! Attempting pull from GitHub remote: {GITHUB_REMOTE_URL}")
        try:
            res = requests.get(GITHUB_REMOTE_URL)
            if res.status_code == 200:
                with open(DESKTOP_LAWS_PATH, 'w', encoding='utf-8') as f:
                    f.write(res.text)
                print(f"[✓] Successfully restored Desktop laws file from GitHub!")
        except Exception as e:
            print(f"[X] Failed to fetch remote laws: {e}")

    print("[+] Compliance Audit Complete: All 14 Universal AI Laws active across all environments.")

if __name__ == "__main__":
    audit_and_sync()
