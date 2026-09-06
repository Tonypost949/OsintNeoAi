"""
kali_bridge.py — Kali Linux WSL2 Execution Bridge

Enables Windows Python scripts to trigger Kali Linux security tools
inside WSL2 without leaving the Windows environment.

Usage:
    bridge = KaliBridge()
    result = bridge.run_kali("nmap -sV 192.168.1.1")
    result = bridge.run_kali("theHarvester -d example.com -b google")
"""

import subprocess
import json
import os
from datetime import datetime


class KaliBridge:
    def __init__(self, distro: str = "kali-linux"):
        self.distro = distro
        self.user = "osintneoai"
        self._verify_distro()

    def _verify_distro(self) -> bool:
        try:
            result = subprocess.run(
                ["wsl", "-d", self.distro, "-u", self.user, "--", "uname", "-a"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def run_kali(self, command: str, timeout: int = 120) -> dict:
        try:
            result = subprocess.run(
                ["wsl", "-d", self.distro, "-u", self.user, "--", "bash", "-c", command],
                capture_output=True, text=True, timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out", "command": command}
        except Exception as e:
            return {"success": False, "error": str(e), "command": command}

    def run_osint_tool(self, tool: str, args: str) -> dict:
        tool_commands = {
            "nmap": f"nmap {args}",
            "harvester": f"theHarvester {args}",
            "sherlock": f"sherlock {args}",
            "recon-ng": f"recon-ng {args}",
            "nikto": f"nikto {args}",
            "whois": f"whois {args}",
            "dig": f"dig {args}",
            "host": f"host {args}",
            "sublist3r": f"sublist3r {args}",
            "amass": f"amass {args}",
        }
        cmd = tool_commands.get(tool.lower(), f"{tool} {args}")
        return self.run_kali(cmd)

    def check_tool_availability(self) -> dict:
        tools = ["nmap", "theHarvester", "sherlock", "nikto", "whois", "dig", "host"]
        available = {}
        for tool in tools:
            result = self.run_kali(f"which {tool}")
            available[tool] = result["success"]
        return available

    def batch_scan(self, targets: list[str], tool: str = "nmap", extra_args: str = "") -> list[dict]:
        results = []
        for target in targets:
            cmd = f"{tool} {extra_args} {target}"
            results.append(self.run_kali(cmd))
        return results


if __name__ == "__main__":
    bridge = KaliBridge()
    print("Kali Bridge Status:", "Connected" if bridge._verify_distro() else "Disconnected")
    print("\nAvailable tools:")
    tools = bridge.check_tool_availability()
    for tool, available in tools.items():
        print(f"  {tool}: {'✓' if available else '✗'}")
