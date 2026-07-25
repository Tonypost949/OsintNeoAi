import json
import urllib.request
import websocket

def verify_live_dom_text():
    res = urllib.request.urlopen("http://127.0.0.1:9222/json")
    tabs = json.loads(res.read().decode('utf-8'))
    ws_url = None
    for tab in tabs:
        if tab.get("id") == "274FE63BEA3697F1A9D70FDCBEC669B6":
            ws_url = tab.get("webSocketDebuggerUrl")
            break
            
    if not ws_url:
        print("Active search tab not found.")
        return

    ws = websocket.create_connection(ws_url, suppress_origin=True)
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.recv()
    
    # Get the body innerText to verify if search results are displayed
    js_code = "document.body.innerText;"
    
    ws.send(json.dumps({"id": 100, "method": "Runtime.evaluate", "params": {"expression": js_code, "returnByValue": True}}))
    
    ws.settimeout(4.0)
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 100:
                val = data.get("result", {}).get("result", {}).get("value")
                print("\n=== RAW SCREEN TEXT VERIFICATION ===")
                print(val)
                break
        except websocket.WebSocketTimeoutException:
            print("Timeout reading page text.")
            break
            
    ws.close()

verify_live_dom_text()
