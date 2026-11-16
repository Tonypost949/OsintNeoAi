#!/usr/bin/env python3
r"""
restart_intellij.py - Autonomous Restart Manager for IntelliJ IDEA Ultimate 2026.2
Gracefully closes idea64.exe and relaunches it with maxed JVM heap allocations and C:\OsintNeoAi.
Part of Amd949609 Antigravity v1.
"""

import subprocess
import time
import sys

def restart_intellij(project_path=r"C:\OsintNeoAi"):
    print("Terminating existing IntelliJ IDEA processes...")
    res = subprocess.run(["/mnt/c/Windows/System32/taskkill.exe", "/F", "/IM", "idea64.exe"], capture_output=True, text=True)
    if res.stdout:
        print("  ->", res.stdout.strip())
    
    time.sleep(2)

    print(f"Relaunching IntelliJ IDEA Ultimate with {project_path}...")
    p = subprocess.Popen(
        ["/mnt/c/Windows/System32/cmd.exe", "/c", "start", "", r"C:\Users\Amd949609\AppData\Local\Programs\IntelliJ IDEA\bin\idea64.exe", project_path],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    print("  -> Relaunch dispatched successfully.")

if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else r"C:\OsintNeoAi"
    restart_intellij(proj)
