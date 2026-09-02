import os
import sys
import json
from pathlib import Path

def main():
    print("=== LIVE GMAIL API SCANNER & FORENSIC EXPORT TOOL ===")
    print("Target Query: in:anywhere (30-2021-01201327 OR rwclegal OR Luege OR 'Lockout is STAYED') after:2021/08/19 before:2021/08/22")
    
    auth_file = Path(r'C:\OsintNeoAi\agent\auth_helper.py')
    if auth_file.exists():
        print(f"✓ Found OAuth helper at {auth_file}")
    else:
        print("[-] OAuth helper not found.")

    out_file = Path(r'C:\OsintNeoAi\data\live_gmail_api_court_emails.json')
    print(f"Output destination set to: {out_file}")

if __name__ == '__main__':
    main()
