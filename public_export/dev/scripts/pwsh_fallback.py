#!/usr/bin/env python3
import sys
import os
import datetime
import subprocess

def run_pwsh_command(args):
    cmd_str = " ".join(args).strip()
    if not cmd_str:
        print("OSINT Neo AI PowerShell Dev Console (Python Emulation Runtime)")
        print("Usage: pwsh -c <command>")
        return 0

    # Common PowerShell cmdlet mappings
    if cmd_str.lower() in ["get-date", "get-date;", "date"]:
        print(datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M:%S %p"))
        return 0
    elif cmd_str.lower() in ["get-location", "pwd"]:
        print(os.getcwd())
        return 0
    elif cmd_str.lower().startswith("write-host "):
        print(cmd_str[11:].strip("'\""))
        return 0
    elif cmd_str.lower() in ["get-childitem", "dir"]:
        cmd_str = "ls -la"

    # Execute as bash command with timeout
    try:
        res = subprocess.run(cmd_str, shell=True, capture_output=True, text=True, timeout=15)
        if res.stdout:
            print(res.stdout, end="")
        if res.stderr:
            print(res.stderr, end="", file=sys.stderr)
        return res.returncode
    except subprocess.TimeoutExpired:
        print(f"[PowerShell Fallback] Command execution timed out: {cmd_str}", file=sys.stderr)
        return 124
    except Exception as e:
        print(f"[PowerShell Fallback Error] {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raw_args = sys.argv[1:]
    if raw_args and raw_args[0] in ["-c", "-Command", "-command"]:
        raw_args = raw_args[1:]
    sys.exit(run_pwsh_command(raw_args))
