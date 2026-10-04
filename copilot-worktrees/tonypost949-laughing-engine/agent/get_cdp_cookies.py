"""
Extracts DeepSeek cookies directly from the running Chrome instance using DevTools Protocol.
Avoids file locking issues by querying Chrome's active process memory.
"""
import urllib.request
import json
import websocket

def get_cookies_via_cdp():
    try:
        res = urllib.request.urlopen("http://127.0.0.1:9222/json")
        tabs = json.loads(res.read().decode('utf-8'))
    except Exception as e:
        print(f"Could not connect to Chrome debugging port: {e}")
        return None
        
    # Find any page target
    ws_url = None
    for t in tabs:
        if t.get("webSocketDebuggerUrl") and not t.get("url", "").startswith("chrome-extension"):
            ws_url = t.get("webSocketDebuggerUrl")
            break
            
    if not ws_url:
        print("No active page tab found to query cookies. Opening a blank tab...")
        try:
            req = urllib.request.Request("http://127.0.0.1:9222/json/new", method="PUT")
            new_tab = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
            ws_url = new_tab.get("webSocketDebuggerUrl")
        except Exception as e:
            print(f"Failed to open new tab: {e}")
            return None
            
    print(f"Connecting to tab websocket: {ws_url}")
    ws = websocket.create_connection(ws_url, suppress_origin=True)
    
    # Enable Network domain
    ws.send(json.dumps({"id": 1, "method": "Network.enable"}))
    ws.recv()
    
    # Request all cookies
    # Note: Network.getAllCookies might be blocked on some secure versions, so we try it first
    print("Requesting all cookies via DevTools...")
    ws.send(json.dumps({"id": 2, "method": "Network.getAllCookies"}))
    
    ws.settimeout(5.0)
    cookies_list = []
    for _ in range(20):
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 2:
                cookies_list = data.get("result", {}).get("cookies", [])
                break
        except Exception as e:
            print(f"Error reading socket: {e}")
            break
            
    # Close connection
    ws.close()
    
    # Filter and format deepseek cookies
    ds_cookies = []
    for c in cookies_list:
        domain = c.get("domain", "")
        if "deepseek" in domain:
            ds_cookies.append(f"{c.get('name')}={c.get('value')}")
            
    return "; ".join(ds_cookies) if ds_cookies else None

if __name__ == "__main__":
    cookies = get_cookies_via_cdp()
    if cookies:
        print("Found DeepSeek cookies via CDP:")
        print(cookies[:100] + "...")
        with open("deepseek_cookies.txt", "w") as f:
            f.write(cookies)
    else:
        print("No DeepSeek cookies retrieved via CDP.")
