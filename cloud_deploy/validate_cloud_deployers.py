"""Validator test for Cloud Deployer scripts."""

import os
import subprocess
from pathlib import Path

CLOUD_DEPLOY_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = CLOUD_DEPLOY_DIR.parent / "scripts"

def test_cloud_scripts_exist():
    required_scripts = [
        CLOUD_DEPLOY_DIR / "azure_student_vm_setup.sh",
        CLOUD_DEPLOY_DIR / "digitalocean_relay_setup.sh",
        SCRIPTS_DIR / "deploy_headless_compute.sh",
        SCRIPTS_DIR / "mobile_termux_tailscale_init.sh"
    ]
    print("[+] Validating cloud deployment & bootstrap scripts:")
    for script in required_scripts:
        assert script.exists(), f"Missing script: {script}"
        assert script.stat().st_size > 100, f"Script empty or incomplete: {script}"
        print(f"  ✓ {script.name:<35} ({script.stat().st_size} bytes)")

    print("[✅] All cloud deployer and bootstrap scripts verified successfully!")
    return True

if __name__ == "__main__":
    assert test_cloud_scripts_exist()
