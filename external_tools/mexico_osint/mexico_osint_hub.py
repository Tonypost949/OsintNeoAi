#!/usr/bin/env python3
"""
🇲🇽 MEXICO OSINT MASTER SUITE v1.0
Integrated for OSINTNeoAi Terminal
Tools Included:
- osintxcurp: RENAPO CURP citizen verification
- osintximss: IMSS Social Security & Employment lookup
- osintxcarplate: REPUVE & SCT Vehicle and transit verification
- osintxphone / MeXiCOSINT: IFETEL Carrier & Mobile routing intelligence
"""

import os
import sys
import json
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TOOLS = {
    "curp": {
        "name": "OSINT-x-CURP (RENAPO)",
        "path": os.path.join(BASE_DIR, "osintxcurp", "OSINT-x-CURP.py"),
        "desc": "Verify and extract Mexican citizen records via CURP."
    },
    "imss": {
        "name": "OSINT-x-IMSS (Social Security)",
        "path": os.path.join(BASE_DIR, "osintximss", "OSINT-x-IMSS.py"),
        "desc": "Check IMSS social security and formal employment records."
    },
    "plate": {
        "name": "OSINT-x-PLATE (REPUVE & SCT)",
        "path": os.path.join(BASE_DIR, "osintxcarplate", "OSINT_x_PLATE.py"),
        "desc": "Look up vehicle plates, SCT commercial transit, and theft reports."
    },
    "phone": {
        "name": "OSINT-x-Phone (IFETEL)",
        "path": os.path.join(BASE_DIR, "osintxphone", "OSINT-x-Phone.py"),
        "desc": "Identify Mexican phone carrier, state, and geographic routing."
    }
}

def list_tools():
    print("\n=========================================================")
    print("           🇲🇽 MEXICO OSINT MASTER TOOLKIT                ")
    print("=========================================================\n")
    for key, info in TOOLS.items():
        exists = "✅ Ready" if os.path.exists(info["path"]) else "❌ Missing"
        print(f"  [{key:<6}] {info['name']:<30} [{exists}]")
        print(f"          -> {info['desc']}\n")

def run_tool(tool_key, args):
    if tool_key not in TOOLS:
        print(f"[-] Unknown tool '{tool_key}'. Available: {list(TOOLS.keys())}")
        return
    tool_info = TOOLS[tool_key]
    script_path = tool_info["path"]
    if not os.path.exists(script_path):
        print(f"[-] Script not found at {script_path}")
        return
    
    cmd = [sys.executable, script_path] + args
    print(f"[*] Launching {tool_info['name']}...")
    os.system(" ".join(cmd))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mexico OSINT Master Suite")
    parser.add_argument("tool", nargs="?", choices=["curp", "imss", "plate", "phone", "list"], default="list", help="Tool to run")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed to the underlying tool")
    
    parsed = parser.parse_args()
    if parsed.tool == "list":
        list_tools()
    else:
        run_tool(parsed.tool, parsed.args)
