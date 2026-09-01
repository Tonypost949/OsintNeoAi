"""
Meta Graph API Webhook Linker
Subscribes Facebook Page 61594100636376 and Meta App to Azure Cloud Webhook endpoint.
Reference: https://developers.facebook.com/docs/graph-api/webhooks/
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

CALLBACK_URL = "https://osintneoai-app-949.azurewebsites.net/webhook"
VERIFY_TOKEN = "makaveli_osint_verify_2026"
PAGE_ID = "61594100636376"

def link_app_webhook(app_id: str, app_secret: str) -> Dict[str, Any]:
    """Subscribes the Meta App to receive Page webhooks."""
    app_access_token = f"{app_id}|{app_secret}"
    url = f"https://graph.facebook.com/v20.0/{app_id}/subscriptions"
    payload = urllib.parse.urlencode({
        "object": "page",
        "callback_url": CALLBACK_URL,
        "fields": "feed,mention,messages",
        "verify_token": VERIFY_TOKEN,
        "access_token": app_access_token
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[SUCCESS] App Webhook Subscribed: {data}")
            return data
    except Exception as e:
        print(f"[ERROR APP WEBHOOK] {e}")
        return {"error": str(e)}

def link_page_subscribed_apps(page_token: str, page_id: str = PAGE_ID) -> Dict[str, Any]:
    """Subscribes the Page to the App's webhook feed."""
    url = f"https://graph.facebook.com/v20.0/{page_id}/subscribed_apps"
    payload = urllib.parse.urlencode({
        "subscribed_fields": "feed,mention,messages",
        "access_token": page_token
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[SUCCESS] Page {page_id} Subscribed: {data}")
            return data
    except Exception as e:
        print(f"[ERROR PAGE SUBSCRIPTION] {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    page_token = os.getenv("FB_PAGE_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if page_token:
        link_page_subscribed_apps(page_token)
    else:
        print("[NOTICE] Target Webhook: " + CALLBACK_URL)
        print("[NOTICE] Verify Token: " + VERIFY_TOKEN)
        print("[NOTICE] Target Page ID: " + PAGE_ID)
