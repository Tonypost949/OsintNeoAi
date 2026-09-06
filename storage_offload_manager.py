#!/usr/bin/env python3
"""
Storage Offload Manager for OsintNeoAi & TaxFunded Platform.
Transfers heavy directories (raw data, cloud takeouts, node_modules, build caches)
from C: drive to secondary/external D: drive (D:\envy backup\) and establishes directory symbolic links.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

SOURCE_ROOT = Path(r"C:\OsintNeoAi")
TARGET_ROOT = Path(r"D:\envy backup\OsintNeoAi_Offload")

OFFLOAD_DIRECTORIES = [
    "data",
    "evidence",
    "extracted_zips",
    "extracted_documents",
    "extracted_tasklets",
    "node_modules",
]

def ensure_target_dir():
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"[+] Offload directory ready at: {TARGET_ROOT}")

def offload_path(rel_path_str):
    src = SOURCE_ROOT / rel_path_str
    dst = TARGET_ROOT / rel_path_str

    if not src.exists():
        print(f"[-] Source path does not exist, skipping: {src}")
        return

    if src.is_symlink():
        print(f"[!] Path is already a symbolic link: {src}")
        return

    print(f"[*] Moving: {src} -> {dst}")
    if src.is_dir():
        if dst.exists():
            print(f"[!] Target path exists. Merging content: {dst}")
            shutil.copytree(src, dst, dirs_exist_only=True)
            shutil.rmtree(src)
        else:
            shutil.move(str(src), str(dst))
        
        # Create directory junction
        cmd = f'cmd /c mklink /J "{src}" "{dst}"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[+] Directory junction created: {src} -> {dst}")
        else:
            print(f"[X] Failed to create junction: {res.stderr}")

def main():
    print("==================================================")
    print("  OsintNeoAi Storage Offload Manager (C: -> D:)  ")
    print("==================================================")
    ensure_target_dir()
    for rel_path in OFFLOAD_DIRECTORIES:
        offload_path(rel_path)
    print("\n[+] Storage offloading cycle complete!")

if __name__ == "__main__":
    main()
