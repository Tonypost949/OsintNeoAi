import sys
import os
import time
from google.cloud import bigquery

# We will try to fetch the page source using the active CDP session of the running browser.
# If the browser is open at C6E86A58CB4F555E85566B80E7F03086, we can query the page DOM using a script.
# Let's write a python script that connects to Chrome DevTools (usually running on port 9222)
# and dumps the DOM of the active tab.

import urllib.request
import json

def get_active_tab_dom():
    try:
        # Check if Chrome debugging is open
        res = urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2)
        tabs = json.loads(res.read().decode('utf-8'))
        for tab in tabs:
            if "claim-search" in tab.get("url", ""):
                print(f"Found active claim-search tab: {tab['id']}")
                # We can use websocket to connect, but let's see if we can get info
                return tab
    except Exception as e:
        print(f"Error checking Chrome debugging port: {e}")
    return None

get_active_tab_dom()
