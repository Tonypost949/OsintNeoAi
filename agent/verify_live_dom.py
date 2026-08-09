import json
import urllib.request
import websocket

def verify_live_dom():
    res = urllib.request.urlopen("http://127.0.0.1:9222/json")
    tabs = json.loads(res.read().decode('utf-8'))
    ws_url = None
    for tab in tabs:
        if tab.get("id") == "274FE63BEA3697F1A9D70FDCBEC669B6":
            ws_url = tab.get("webSocketDebuggerUrl")
            break
            
    if not ws_url:
        print("Tab 274FE63BEA3697F1A9D70FDCBEC669B6 not found. Checking open claim-search URLs:")
        for t in tabs:
            if "claim-search" in t.get("url", ""):
                print(f"- ID: {t.get('id')} | URL: {t.get('url')}")
                ws_url = t.get("webSocketDebuggerUrl")
        if not ws_url:
            return

    ws = websocket.create_connection(ws_url, suppress_origin=True)
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.recv()
    
    # JS code to read ALL text on the page, check for tables, check for messages
    js_code = """
    (() => {
      const allText = document.body.innerText;
      const tables = Array.from(document.querySelectorAll('table')).map(t => t.outerHTML);
      const elements = Array.from(document.querySelectorAll('sws-claim-search, sws-process-page')).map(el => el.innerText);
      
      return {
        url: window.location.href,
        hasTable: tables.length > 0,
        tablesCount: tables.length,
        tablesHTML: tables.map(t => t.substring(0, 1000)),
        bodyText: allText,
        elementsCount: elements.length
      };
    })()
    """
    
    ws.send(json.dumps({"id": 100, "method": "Runtime.evaluate", "params": {"expression": js_code, "returnByValue": True}}))
    
    ws.settimeout(4.0)
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 100:
                val = data.get("result", {}).get("result", {}).get("value")
                print("\n=== LIVE PORTAL DOM VERIFICATION ===")
                print(json.dumps(val, indent=2))
                with open("live_portal_verification.json", "w", encoding="utf-8") as f:
                    json.dump(val, f, indent=2)
                break
        except websocket.WebSocketTimeoutException:
            print("WebSocket timeout.")
            break
            
    ws.close()

verify_live_dom()
