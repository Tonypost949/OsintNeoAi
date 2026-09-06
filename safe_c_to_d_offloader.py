#!/usr/bin/env python3
"""
Safe Offload Manager for C: to D: Drive.
Moves heavy static folders (backups, raw data, model caches) from C: to D:
and establishes Windows Directory Junctions (mklink /J).
Tools and Python scripts continue to operate at full speed without knowing the difference!
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

TARGET_D_ROOT = Path(r"D:\envy backup\C_Drive_Offloads")

# Paths on C: to offload to D:
OFFLOAD_TARGETS = [
    r"C:\OsintNeoAi_backups",
    r"C:\OSINTNeoAiNews_2026-08-20_0111",
    r"C:\osintneoai5202633",
    r"C:\data",
    r"C:\transforms"
]

def ensure_d_root():
    TARGET_D_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"[+] Offload target directory ready on D: {TARGET_D_ROOT}")

def safe_offload_folder(src_path_str):
    src = Path(src_path_str)
    if not src.exists():
        print(f"[-] Folder does not exist, skipping: {src}")
        return

    if src.is_symlink():
        print(f"[!] Path is already a symbolic link/junction: {src}")
        return

    dst = TARGET_D_ROOT / src.name
    print(f"[*] Moving: {src} -> {dst}")

    # Use robocopy for fast multi-threaded transfer
    cmd = f'robocopy "{src}" "{dst}" /E /MOVE /MT:16 /R:1 /W:1'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"[+] Robocopy move completed with code: {res.returncode}")

    # Clean up empty residual folder if any
    if src.exists() and not src.is_symlink():
        try:
            shutil.rmtree(src)
        except Exception:
            pass

    # Create Directory Junction (mklink /J)
    link_cmd = f'cmd /c mklink /J "{src}" "{dst}"'
    link_res = subprocess.run(link_cmd, shell=True, capture_output=True, text=True)
    if link_res.returncode == 0:
        print(f"[+] Directory junction successfully established: {src} <===> {dst}")
    else:
        print(f"[X] Failed to create junction: {link_res.stderr}")

def main():
    print("=========================================================")
    print("   Safe C: to D: Drive Offload & Junction Manager       ")
    print("=========================================================")
    ensure_d_root()
    for folder in OFFLOAD_TARGETS:
        safe_offload_folder(folder)
    print("\n[+] Safe offloading & junction linking complete!")

if __name__ == "__main__":
    main()
