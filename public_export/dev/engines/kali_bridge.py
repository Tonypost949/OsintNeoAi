#!/usr/bin/env python3
"""
Kali Linux WSL2 Execution Bridge for OsintNeoAi.
Executes advanced OSINT and security tools inside Kali Linux WSL2
directly from Windows Python & CLI scripts.
"""

import sys
import subprocess

def run_kali_command(cmd_str):
    print(f"[*] Executing in Kali Linux (WSL2): {cmd_str}")
    wsl_cmd = ["wsl", "-d", "kali-linux", "bash", "-c", cmd_str]
    res = subprocess.run(wsl_cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print("[+] Kali Command Output:")
        print(res.stdout)
        return res.stdout
    else:
        print(f"[-] Kali Command Error (Exit Code {res.returncode}):")
        print(res.stderr)
        return None

if __name__ == "__main__":
    test_cmd = sys.argv[1] if len(sys.argv) > 1 else "uname -a && whoami"
    run_kali_command(test_cmd)
