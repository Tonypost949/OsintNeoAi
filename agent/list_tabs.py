import json
import urllib.request

def check_active_pages():
    try:
        res = urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2)
        tabs = json.loads(res.read().decode('utf-8'))
        print("=== ACTIVE BROWSER TABS ===")
        for tab in tabs:
            print(f"ID: {tab.get('id')} | Title: {tab.get('title')} | URL: {tab.get('url')}")
    except Exception as e:
        print(f"Error connecting to Chrome: {e}")

check_active_pages()
