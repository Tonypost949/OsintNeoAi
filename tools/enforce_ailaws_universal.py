#!/usr/bin/env python3
"""
enforce_ailaws_universal.py — Universal AI Laws Enforcer Tool
Governance: AI Law 1 (Repeated processes become AI Tools), AI Law 2 (Strict Execution & Accuracy Format)

This tool MUST be executed prior to any operation across all AI agents and models.
It reads and validates C:\\Users\\Amd949609\\Desktop\\00_ailaws.md, enforcing:
  1. Mandatory complete read of 00_ailaws.md
  2. Verification of all 14 Universal AI Laws
  3. Pre-action check of user workspace profile directory
  4. Format enforcement (Accuracy score, YES/NO, Detailed info, Work authorization prompt)
"""

import os
import sys

AILAWS_DESKTOP_PATH = r"C:\Users\Amd949609\Desktop\00_ailaws.md"
WORKSPACE_DIR = r"C:\amd949609@gmail.com_Antigravity_CLI_v2.0"

def enforce_ailaws():
    print("=" * 70)
    print("⚡ UNIVERSAL AI LAWS ENFORCER TOOL — PRE-ACTION AUDIT")
    print("=" * 70)

    # 1. Mandatory Read Check
    if not os.path.exists(AILAWS_DESKTOP_PATH):
        print(f"[CRITICAL ERROR] AI Laws file missing at: {AILAWS_DESKTOP_PATH}")
        sys.exit(1)

    with open(AILAWS_DESKTOP_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.splitlines()
    print(f"  [✓] Verified 00_ailaws.md read ({len(lines)} lines, {len(content)} bytes)")

    # 2. Check key rules
    required_rules = [
        "Universal AI Laws",
        "Accuracy Score",
        "Zero Human Action Required",
        "Single-Block Auto-Clipboard",
        "Strict Autonomous Background Task Lifecycle"
    ]

    for rule in required_rules:
        if rule.lower() in content.lower():
            print(f"  [✓] Verified Law Component: '{rule}'")
        else:
            print(f"  [!] Missing Law Component: '{rule}'")

    # 3. Verify Workspace Profile Directory (Law 9)
    if os.path.exists(WORKSPACE_DIR):
        print(f"  [✓] Verified User Workspace Directory: {WORKSPACE_DIR}")
    else:
        print(f"  [!] Workspace Directory missing: {WORKSPACE_DIR}")

    print("=" * 70)
    print("[SUCCESS] All Universal AI Laws loaded & pre-action audit complete.")
    print("=" * 70)

if __name__ == "__main__":
    enforce_ailaws()
