#!/usr/bin/env python3
"""
Single-Sign-On Multi-Account Token Pooler for OsintNeoAi.
Harvests OAuth tokens from all authenticated gcloud accounts silently
to provide combined AI rate limits and zero-key access.
"""

import subprocess
import json

ACCOUNTS = [
    "amd949609@gmail.com",
    "osintneoai@gmail.com",
    "txtdjdrop@gmail.com"
]

def get_token_for_account(account):
    try:
        # Get access token for specified account without prompt
        cmd = ["gcloud", "auth", "print-access-token", f"--account={account}"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception as e:
        print(f"[-] Failed to harvest token for {account}: {e}")
    return None

def build_active_token_pool():
    pool = {}
    print("[*] Harvesting active SSO tokens across logged-in Google accounts...")
    for acc in ACCOUNTS:
        token = get_token_for_account(acc)
        if token:
            pool[acc] = token
            print(f"[+] Token active for: {acc}")
    return pool

if __name__ == "__main__":
    token_pool = build_active_token_pool()
    print(f"\n[+] Single Sign-On Token Pool Ready! Active accounts: {len(token_pool)}")
