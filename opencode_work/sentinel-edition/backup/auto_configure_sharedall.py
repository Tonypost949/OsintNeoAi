#!/usr/bin/env python3
"""
Auto-discover SharedAll folder and configure backup system.
Uses existing OAuth credentials from OSINT_VAULT_BACKUP.
"""

import json
import os
import requests
from pathlib import Path

VAULT_BACKUP = Path(r"C:\Users\HP\OneDrive\Documents\opencode_work\OSINT_VAULT_BACKUP")
CLIENT_SECRET = VAULT_BACKUP / "client_secret.json"
TOKEN_FILE = VAULT_BACKUP / "token_drive_upload.json"
CONFIG_OUT = Path(__file__).parent / ".sharedall_config.json"


def refresh_access_token(client_data, token_data):
    """Use refresh token to get a new access token."""
    url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": token_data["client_id"],
        "client_secret": token_data["client_secret"],
        "refresh_token": token_data["refresh_token"],
        "grant_type": "refresh_token",
    }
    resp = requests.post(url, data=payload, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("access_token")
    else:
        print(f"[ERROR] Token refresh failed: {resp.status_code} {resp.text}")
        return None


def find_sharedall_folder(access_token):
    """Search Google Drive for SharedAll or shared backup folders."""
    headers = {"Authorization": f"Bearer {access_token}"}

    # Search for folders with shared/backup/sharedall in name
    queries = [
        "name contains 'sharedall' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        "name contains 'SharedAll' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        "name contains 'backup' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        "name contains 'OsintNeoAi' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        "name contains 'osintneoai' and mimeType='application/vnd.google-apps.folder' and trashed=false",
    ]

    all_folders = []
    for q in queries:
        url = f"https://www.googleapis.com/drive/v3/files?q={q}&fields=files(id,name,parents,createdTime)&pageSize=50"
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            files = resp.json().get("files", [])
            all_folders.extend(files)

    # Deduplicate
    seen = set()
    unique = []
    for f in all_folders:
        if f["id"] not in seen:
            seen.add(f["id"])
            unique.append(f)

    return unique


def list_all_folders(access_token, max_results=100):
    """List all folders in root of Drive."""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://www.googleapis.com/drive/v3/files?q=mimeType='application/vnd.google-apps.folder' and trashed=false&fields=files(id,name,parents)&pageSize={max_results}"
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 200:
        return resp.json().get("files", [])
    return []


def main():
    print("[AUTO-CONFIG] Loading credentials...")

    with open(CLIENT_SECRET) as f:
        client_data = json.load(f)
    with open(TOKEN_FILE) as f:
        token_data = json.load(f)

    print("[AUTO-CONFIG] Refreshing access token...")
    access_token = refresh_access_token(client_data, token_data)
    if not access_token:
        print("[FAILED] Could not get access token")
        return

    print("[AUTO-CONFIG] Access token obtained. Searching for SharedAll folder...")

    # Search for matching folders
    folders = find_sharedall_folder(access_token)
    if folders:
        print(f"\n[AUTO-CONFIG] Found {len(folders)} matching folders:")
        for i, f in enumerate(folders):
            print(f"  {i+1}. {f['name']} (ID: {f['id']})")

        # Use the first match (most relevant)
        best = folders[0]
        print(f"\n[AUTO-CONFIG] Using: {best['name']} ({best['id']})")
    else:
        print("[AUTO-CONFIG] No matching folders found. Listing all root folders...")
        all_folders = list_all_folders(access_token)
        if all_folders:
            print(f"\n[AUTO-CONFIG] Found {len(all_folders)} folders in Drive root:")
            for i, f in enumerate(all_folders[:20]):
                print(f"  {i+1}. {f['name']} (ID: {f['id']})")

            # Check for sharedwithme
            shared_url = f"https://www.googleapis.com/drive/v3/files?q=sharedWithMe=true and mimeType='application/vnd.google-apps.folder'&fields=files(id,name)&pageSize=50"
            resp = requests.get(shared_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=30)
            if resp.status_code == 200:
                shared = resp.json().get("files", [])
                if shared:
                    print(f"\n[AUTO-CONFIG] Shared with you ({len(shared)}):")
                    for i, f in enumerate(shared):
                        print(f"  {i+1}. {f['name']} (ID: {f['id']})")

            # Use first available folder or create a new one
            if all_folders:
                best = all_folders[0]
                print(f"\n[AUTO-CONFIG] Using first available: {best['name']} ({best['id']})")
            else:
                # Create a new folder
                print("[AUTO-CONFIG] Creating new 'SentinelBackups' folder...")
                create_url = "https://www.googleapis.com/drive/v3/files"
                metadata = {"name": "SentinelBackups", "mimeType": "application/vnd.google-apps.folder"}
                resp = requests.post(create_url, headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}, json=metadata, timeout=30)
                if resp.status_code == 200:
                    best = resp.json()
                    print(f"[AUTO-CONFIG] Created: {best['name']} ({best['id']})")
                else:
                    print(f"[FAILED] Could not create folder: {resp.status_code}")
                    return
        else:
            print("[FAILED] No folders found in Drive")
            return

    # Save config
    config = {
        "folder_id": best["id"],
        "folder_name": best.get("name", "unknown"),
        "client_secret_path": str(CLIENT_SECRET),
        "token_path": str(TOKEN_FILE),
        "auth_method": "oauth_refresh_token",
        "setup_date": "2026-07-11T07:30:00Z",
        "setup_by": "sentinel_auto_configure",
    }

    with open(CONFIG_OUT, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n[AUTO-CONFIG] Config saved to: {CONFIG_OUT}")
    print(f"[AUTO-CONFIG] Folder: {best.get('name', 'unknown')} ({best['id']})")
    print("[AUTO-CONFIG] SharedAll backup is now configured!")


if __name__ == "__main__":
    main()
