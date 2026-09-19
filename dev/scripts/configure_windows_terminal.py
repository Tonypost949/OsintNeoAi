"""Safely configure Windows Terminal profile for OsintNeoAi modern DevShell."""

import json
import os
import shutil
from datetime import datetime

SETTINGS_PATH = os.path.expandvars(
    r"%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
)

PROFILE_GUID = "{a7b9d62f-0e1b-4f93-8a39-938210c4f801}"
PROFILE_NAME = "OsintNeoAi VS2022 + AGY"
VS_LAUNCH_CMD = (
    r"powershell.exe -NoExit -ExecutionPolicy Bypass -Command "
    r"\"& 'C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\Launch-VsDevShell.ps1' -Arch amd64 -HostArch amd64; "
    r"Set-Location 'C:\OsintNeoAi'; "
    r"if (Test-Path 'C:\OsintNeoAi\cli\developer_menu.ps1') { . 'C:\OsintNeoAi\cli\developer_menu.ps1' }; "
    r"Write-Host '⚡ OsintNeoAi Modern DevShell Ready (Zero-Lag Bracketed Paste Enabled)' -ForegroundColor Green\""
)

def configure():
    if not os.path.exists(SETTINGS_PATH):
        print(f"[-] Windows Terminal settings.json not found at {SETTINGS_PATH}")
        return False

    # Create timestamped backup of settings.json
    backup_path = SETTINGS_PATH + f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(SETTINGS_PATH, backup_path)
    print(f"[+] Backed up settings.json to {backup_path}")

    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    profiles = data.get("profiles", {})
    profile_list = profiles.get("list", [])

    existing = next((p for p in profile_list if p.get("guid") == PROFILE_GUID or p.get("name") == PROFILE_NAME), None)

    dev_profile = {
        "guid": PROFILE_GUID,
        "name": PROFILE_NAME,
        "commandline": VS_LAUNCH_CMD,
        "startingDirectory": r"C:\OsintNeoAi",
        "icon": "ms-appx:///ProfileIcons/{61c54bbd-c2c6-5271-96e7-009a87ff44bf}.png",
        "colorScheme": "Campbell",
        "font": {
            "face": "Cascadia Code"
        },
        "hidden": False
    }

    if existing:
        print(f"[+] Updating existing profile '{PROFILE_NAME}'...")
        existing.update(dev_profile)
    else:
        print(f"[+] Adding new profile '{PROFILE_NAME}' to Windows Terminal...")
        profile_list.append(dev_profile)

    profiles["list"] = profile_list
    data["profiles"] = profiles

    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("[✅] Windows Terminal configuration updated successfully!")
    return True

if __name__ == "__main__":
    configure()
