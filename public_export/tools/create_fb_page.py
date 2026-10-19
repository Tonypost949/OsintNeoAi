"""
Meta Graph API Script: Programmatically Create a Facebook Page
Reference: https://developers.facebook.com/docs/graph-api/reference/user/accounts/
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

def create_facebook_page(
    page_name: str = "OSINTNeoAi",
    category_enum: str = "SCIENCE_TECHNOLOGY_ENGINEERING",
    about: str = "See More. Know First. Trust Nothing. Verify Everything. Tactical OSINT & Forensic Intelligence.",
    user_access_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates a Facebook Page using the Meta Graph API.
    Requires a User Access Token with 'pages_manage_metadata' and 'pages_manage_posts' permissions.
    """
    token = user_access_token or os.environ.get("META_USER_ACCESS_TOKEN")
    
    if not token:
        print("[AUTH REQUIRED] Meta Graph API requires a User Access Token to create Pages programmatically.")
        print("To generate one:")
        print("1. Go to: https://developers.facebook.com/tools/explorer/")
        print("2. Select your App -> Add permissions: 'pages_manage_metadata', 'pages_manage_posts'")
        print("3. Click 'Generate Access Token'")
        print("4. Set environment variable: $env:META_USER_ACCESS_TOKEN='your_token'")
        return {"error": "Missing META_USER_ACCESS_TOKEN"}

    url = "https://graph.facebook.com/v20.0/me/accounts"
    payload = urllib.parse.urlencode({
        "name": page_name,
        "category_enum": category_enum,
        "about": about,
        "access_token": token
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[SUCCESS] Created Facebook Page ID: {data.get('id')}")
            return data
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"[HTTP ERROR {e.code}] {err_msg}")
        return {"error": err_msg}
    except Exception as e:
        print(f"[ERROR] {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    token_arg = sys.argv[1] if len(sys.argv) > 1 else None
    create_facebook_page(user_access_token=token_arg)
