"""
OSINTNeoAi Auto-Poster to Facebook Page ID 61594100636376
Publishes official launch message and links to Makaveli tactical HUD.
"""

import os
import sys
import json
import urllib.request
import urllib.parse

PAGE_ID = "61594100636376"
LAUNCH_MESSAGE = """⚡ OSINTNeoAi — Official Lead Intelligence Node.

"See More. Know First. Trust Nothing. Verify Everything."

Tactical OSINT Agent (Makaveli) is now live for public forensic correlation:
👉 https://tonypost949.github.io/OsintNeoAi/makavelli/

Drop a target domain, company name, or registry docket below to initiate tracking."""

def post_to_page(access_token: str = None):
    token = access_token or os.environ.get("META_PAGE_ACCESS_TOKEN")
    if not token:
        print("[AUTH NOTICE] Set your Page Access Token via $env:META_PAGE_ACCESS_TOKEN or pass as argument.")
        print("Copy-paste the post text manually from C:\\OSINTNEOAI\\makavelli\\POST_THIS_TEXT.txt")
        return

    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
    payload = urllib.parse.urlencode({
        "message": LAUNCH_MESSAGE,
        "access_token": token
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[SUCCESS] Post published to Page! Post ID: {data.get('id')}")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else None
    post_to_page(t)
