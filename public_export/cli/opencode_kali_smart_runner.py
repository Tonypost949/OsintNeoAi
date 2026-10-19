#!/usr/bin/env python3
"""
OpenCode Kali & OSINT Smart Auto-Installer & Runner.
Analyzes requested tools/commands, checks if installed, auto-installs via apt/pip/OsintNeoAi if missing, and executes.
"""

import sys
import os
import subprocess
import shutil

OSINTNEOAI_DIR = "/mnt/c/OsintNeoAi"

# Mapping of common tool aliases to APT package names in Kali Linux
KALI_APT_MAP = {
    "nmap": "nmap",
    "sherlock": "sherlock",
    "spiderfoot": "spiderfoot",
    "theharvester": "theharvester",
    "harvester": "theharvester",
    "amass": "amass",
    "sublist3r": "sublist3r",
    "gobuster": "gobuster",
    "ffuf": "ffuf",
    "dirb": "dirb",
    "dirsearch": "dirsearch",
    "wpscan": "wpscan",
    "nikto": "nikto",
    "hydra": "hydra",
    "john": "john",
    "hashcat": "hashcat",
    "sqlmap": "sqlmap",
    "volatility": "volatility3",
    "autopsy": "autopsy",
    "exiftool": "libimage-exiftool-perl",
    "tshark": "tshark",
    "wireshark": "wireshark",
    "aircrack-ng": "aircrack-ng",
    "recon-ng": "recon-ng",
    "metasploit": "metasploit-framework",
    "msfconsole": "metasploit-framework"
}

def resolve_and_install_tool(tool_name):
    print(f"[*] Checking availability of target tool: '{tool_name}'...")
    
    # 1. Check if tool is already in PATH
    if shutil.which(tool_name):
        print(f"[✓] Tool '{tool_name}' is already installed.")
        return True

    # 2. Check OsintNeoAi local scripts
    osint_path = os.path.join(OSINTNEOAI_DIR, "cli", f"{tool_name}.py")
    if os.path.exists(osint_path):
        print(f"[✓] Found OsintNeoAi tool module: {osint_path}")
        return True

    # 3. Check Kali APT repositories
    apt_pkg = KALI_APT_MAP.get(tool_name.lower(), tool_name.lower())
    print(f"[!] Tool '{tool_name}' not found. Attempting Kali auto-install (apt package: '{apt_pkg}')...")
    
    try:
        res = subprocess.run(f"sudo apt-get update -y && sudo apt-get install -y {apt_pkg}", shell=True)
        if res.returncode == 0 and shutil.which(tool_name):
            print(f"[✓] Successfully installed '{tool_name}' from Kali repos!")
            return True
    except Exception as e:
        print(f"[-] Apt install attempt failed: {e}")

    # 4. Check Python PyPI (pip) fallback
    print(f"[!] Attempting fallback pip installation for '{tool_name}'...")
    try:
        res = subprocess.run(f"pip install --break-system-packages {tool_name}", shell=True)
        if res.returncode == 0:
            print(f"[✓] Successfully installed '{tool_name}' via pip!")
            return True
    except Exception as e:
        print(f"[-] Pip install attempt failed: {e}")

    print(f"[-] Warning: Could not auto-install '{tool_name}'. Proceeding with OpenCode launch...")
    return False

def main():
    if len(sys.argv) > 1:
        target_input = sys.argv[1]
        resolve_and_install_tool(target_input)

    # Launch opencode
    print("[🚀] Launching OpenCode with Kali & OsintNeoAi Auto-Resolution...")
    os.execvp("opencode", ["opencode"] + sys.argv[1:])

if __name__ == "__main__":
    main()
