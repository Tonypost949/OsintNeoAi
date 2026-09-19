#!/usr/bin/env python3
"""
Multi-Provider Free AI Proxy Router for OsintNeoAi & OpenCode.
Routes queries across free & perk-tier models to conserve Antigravity quotas:
1. Google AI Studio (Gemini 1.5 Pro / Flash via free GEMINI_API_KEY)
2. OpenCode CLI (Free-tier open models)
3. Local Ollama / Open-source fallback
"""

import os
import sys
import json
import subprocess

def query_google_genai_free(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY environment variable not set. Falling back to OpenCode CLI...")
        return None

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"[-] Google GenAI Free call failed: {e}")
        return None

def query_opencode_cli(prompt):
    try:
        cmd = ["opencode", "run", prompt]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout
    except Exception as e:
        print(f"[-] OpenCode CLI call failed: {e}")
    return None

def route_ai_request(prompt):
    print("[*] Routing AI Request through Free / Perk Tier Providers...")
    
    # Provider 1: Free Google AI Studio Key
    res = query_google_genai_free(prompt)
    if res:
        print("[+] Processed via Google AI Studio (Free Tier)")
        return res

    # Provider 2: Installed OpenCode CLI
    res = query_opencode_cli(prompt)
    if res:
        print("[+] Processed via OpenCode CLI")
        return res

    print("[!] No free provider succeeded.")
    return "Error: All free AI providers failed or lack API keys."

if __name__ == "__main__":
    test_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello from OsintNeoAi Free Model Router!"
    print(route_ai_request(test_prompt))
