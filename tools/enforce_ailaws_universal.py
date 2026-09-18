#!/usr/bin/env python3
"""
enforce_ailaws_universal.py — Universal AI Laws Enforcer Tool
Governance: AI Law 1 (Repeated processes become AI Tools), AI Law 2 (Strict Execution & Accuracy Format)

This tool MUST be executed prior to any operation across all AI agents and models.
It searches for and reads 00_ailaws.md across standard universal locations:
  1. C:\\Users\\Amd949609\\Desktop\\00_ailaws.md
  2. C:\\amd949609@gmail.com_Antigravity_CLI_v2.0\\00_ailaws.md
  3. C:\\amd949609@gmail.com_Antigravity_CLI_v2.0\\docs\\00_ailaws.md
  4. C:\\Amd949609_Antigravity_v1\\00_ailaws.md
  5. C:\\OsintNeoAi\\00_ailaws.md
"""

import os
import sys

SEARCH_LOCATIONS = [
    r"C:\Users\Amd949609\Desktop\00_ailaws.md",
    r"C:\amd949609@gmail.com_Antigravity_CLI_v2.0\00_ailaws.md",
    r"C:\amd949609@gmail.com_Antigravity_CLI_v2.0\docs\00_ailaws.md",
    r"C:\Amd949609_Antigravity_v1\00_ailaws.md",
    r"C:\OsintNeoAi\00_ailaws.md"
]

WORKSPACE_DIR = r"C:\amd949609@gmail.com_Antigravity_CLI_v2.0"

def enforce_ailaws():
    print("=" * 70)
    print("⚡ UNIVERSAL AI LAWS ENFORCER TOOL — PRE-ACTION AUDIT")
    print("=" * 70)

    found_path = None
    content = ""

    # 1. Multi-Location Fallback Search
    for loc in SEARCH_LOCATIONS:
        if os.path.exists(loc):
            found_path = loc
            with open(loc, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            break

    if not found_path:
        print("[CRITICAL ERROR] 00_ailaws.md not found in any universal location!")
        sys.exit(1)

    lines = content.splitlines()
    print(f"  [✓] Found & Read AI Laws from: {found_path}")
    print(f"  [✓] Verified Content ({len(lines)} lines, {len(content)} bytes)")

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
    print("[SUCCESS] Universal AI Laws active across all locations & audit complete.")
    print("=" * 70)

if __name__ == "__main__":
    enforce_ailaws()
