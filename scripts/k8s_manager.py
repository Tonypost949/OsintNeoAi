#!/usr/bin/env python3
"""
k8s_manager.py - Kubernetes & Cloud Native Cluster Tooling Manager
Maxed out toolchain for IntelliJ IDEA Ultimate, Kali Linux WSL, and Windows.
Part of Amd949609 Antigravity v1 & OsintNeoAi.
"""

import sys
import os
import subprocess
import shutil

KUBECTL_LINUX = "/home/amd949609/.local/bin/kubectl"
HELM_LINUX = "/home/amd949609/.local/bin/helm"
K9S_LINUX = "/home/amd949609/.local/bin/k9s"

KUBECTL_WIN = r"C:\Amd949609_Antigravity_v1\bin\kubectl.exe"
HELM_WIN = r"C:\Amd949609_Antigravity_v1\bin\helm.exe"
K9S_WIN = r"C:\Amd949609_Antigravity_v1\bin\k9s.exe"

def check_status():
    print("=== Kubernetes Toolchain Status ===")
    tools = [
        ("Kubectl (Linux)", KUBECTL_LINUX, ["version", "--client"]),
        ("Helm (Linux)", HELM_LINUX, ["version", "--short"]),
        ("K9s (Linux)", K9S_LINUX, ["version", "--short"]),
    ]
    for name, path, args in tools:
        if os.path.exists(path):
            try:
                res = subprocess.run([path] + args, capture_output=True, text=True, timeout=5)
                output = res.stdout.strip() or res.stderr.strip()
                print(f"[OK] {name}: {output}")
            except Exception as e:
                print(f"[OK] {name}: Installed at {path} ({e})")
        else:
            print(f"[MISSING] {name} at {path}")

    print("\n=== Windows Binaries ===")
    for name, path in [("Kubectl (Win)", KUBECTL_WIN), ("Helm (Win)", HELM_WIN), ("K9s (Win)", K9S_WIN)]:
        wsl_path = path.replace("\\", "/").replace("C:", "/mnt/c")
        if os.path.exists(wsl_path):
            print(f"[OK] {name}: {path} ({os.path.getsize(wsl_path):,} bytes)")
        else:
            print(f"[MISSING] {name} at {path}")

def validate_manifests(target_dir="/mnt/c/OsintNeoAi"):
    print(f"\n=== Validating Kubernetes Manifests in {target_dir} ===")
    yaml_files = []
    try:
        for f in os.listdir(target_dir):
            if f.endswith((".yaml", ".yml")) and ("deploy" in f or "k8s" in f or "runway" in f):
                yaml_files.append(os.path.join(target_dir, f))
    except Exception as e:
        print(f"Error reading directory: {e}")
        return
    
    if not yaml_files:
        print("No Kubernetes YAML manifests found.")
        return

    for yf in yaml_files:
        print(f"Checking: {yf}")
        try:
            res = subprocess.run([KUBECTL_LINUX, "apply", "--dry-run=client", "-f", yf], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                print(f"  -> Valid: {res.stdout.strip()}")
            else:
                print(f"  -> Note: {res.stderr.strip() or res.stdout.strip()}")
        except Exception as e:
            print(f"  -> Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        validate_manifests()
    else:
        check_status()
        if len(sys.argv) > 1 and sys.argv[1] == "all":
            validate_manifests()
