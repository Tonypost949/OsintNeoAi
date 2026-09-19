"""
OsintNeoAi Unified Credentials & API Key Manager Script
"""

import os
import json

def load_credentials():
    env_path = r"C:\amd949609_Antigravity_3.6\amd949609_keys\credentials.env"
    creds = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    creds[k.strip()] = v.strip()
    return creds

def sync_env_vars():
    creds = load_credentials()
    for k, v in creds.items():
        if "YOUR_" not in v:
            os.environ[k] = v
            print(f"[+] Loaded environment key: {k}")

if __name__ == "__main__":
    sync_env_vars()
    print("[+] OsintNeoAi Credentials Manager synced successfully.")
