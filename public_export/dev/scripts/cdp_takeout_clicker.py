import urllib.request
import json
import asyncio
import os

def list_tabs():
    try:
        req = urllib.request.urlopen("http://[PRIVATE_IP]:9222/json")
        tabs = json.loads(req.read().decode())
        print(f"[CDP] Found {len(tabs)} tabs open in Chrome:")
        for t in tabs:
            print(f"  Tab ID: {t.get('id')} | Title: {t.get('title')} | URL: {t.get('url')}")
        return tabs
    except Exception as e:
        print(f"[CDP ERROR] Failed to connect to port 9222: {e}")
        return []

if __name__ == "__main__":
    list_tabs()
