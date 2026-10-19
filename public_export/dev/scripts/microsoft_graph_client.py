#!/usr/bin/env python3
"""
Microsoft Graph API Client for OSINT Neo AI
Fetches directory, audit, security alert, and drive records from Microsoft Graph API (Graph Explorer)
and transforms them into graph nodes and relational edges for OSINT Neo AI.
"""

import os
import sys
import json
import urllib.request
import urllib.error

GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

def graph_get(endpoint, token):
    url = f"{GRAPH_API_URL}/{endpoint.lstrip('/')}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"[-] Graph HTTPError {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"[-] Graph Error: {e}")
        return None

def fetch_graph_overview(token):
    print("[*] Querying Microsoft Graph /me...")
    me = graph_get("me", token)
    if me:
        print(f"[+] Signed in as: {me.get('displayName')} ({me.get('userPrincipalName')})")

    print("[*] Querying Tenant Users...")
    users = graph_get("users?$top=25&$select=displayName,userPrincipalName,id,jobTitle", token)
    if users:
        print(f"[+] Discovered {len(users.get('value', []))} Users.")

    print("[*] Querying Security Alerts (v2)...")
    alerts = graph_get("security/alerts_v2?$top=10", token)
    if alerts:
        print(f"[+] Discovered {len(alerts.get('value', []))} Security Alerts.")

    return {
        "profile": me,
        "users": users.get("value", []) if users else [],
        "alerts": alerts.get("value", []) if alerts else []
    }

if __name__ == "__main__":
    token = os.environ.get("MS_GRAPH_TOKEN")
    if not token and len(sys.argv) > 1:
        token = sys.argv[1]

    if not token:
        print("Usage: python scripts/microsoft_graph_client.py [BEARER_TOKEN]")
        print("  Or set the MS_GRAPH_TOKEN environment variable.")
        print("  Grab your token directly from: https://developer.microsoft.com/en-us/graph/graph-explorer")
        sys.exit(1)

    data = fetch_graph_overview(token)
    print(json.dumps(data, indent=2))
