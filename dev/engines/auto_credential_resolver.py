#!/usr/bin/env python3
"""
Zero-Key Zero-Hunting Automated Credential & OAuth Resolver.
Automatically acquires ADC tokens from gcloud/gcloud auth print-access-token,
local gcp_adc.json, or OpenCode sessions without asking the user for API keys.
"""

import os
import sys
import json
import subprocess

def get_gcloud_access_token():
    try:
        res = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None

def resolve_credentials_silently():
    # 1. Check existing environment
    if os.environ.get("GEMINI_API_KEY"):
        return {"type": "API_KEY", "value": os.environ["GEMINI_API_KEY"]}

    # 2. Check local gcp_adc.json in C:\OsintNeoAi
    adc_file = r"C:\OsintNeoAi\gcp_adc.json"
    if os.path.exists(adc_file):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = adc_file
        return {"type": "ADC_FILE", "value": adc_file}

    # 3. Auto-extract token from active gcloud session
    token = get_gcloud_access_token()
    if token:
        return {"type": "OAUTH_BEARER", "value": token}

    # 4. Fallback to local CLI auth
    return {"type": "OPENCODE_CLI", "value": "LOCAL_SESSION"}

if __name__ == "__main__":
    cred = resolve_credentials_silently()
    print(f"[+] Credentials resolved automatically without prompt: {cred['type']}")
