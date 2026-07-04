import json
import urllib.request
import urllib.error
import websocket
import time

def extract_dom():
    res = urllib.request.urlopen("http://127.0.0.1:9222/json")
    tabs = json.loads(res.read().decode('utf-8'))
    ws_url = None
    for tab in tabs:
        if tab.get("id") == "C6E86A58CB4F555E85566B80E7F03086":
            ws_url = tab.get("webSocketDebuggerUrl")
            break
    
    if not ws_url:
        print("Tab C6E86A58CB4F555E85566B80E7F03086 not found.")
        return

    ws = websocket.create_connection(ws_url, suppress_origin=True)
    
    # 1. Enable Runtime and Page to ensure page context is fully ready
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.recv()
    
    # Let's read incoming events until we get no more, then execute our script
    ws.settimeout(0.5)
    while True:
        try:
            ws.recv()
        except websocket.WebSocketTimeoutException:
            break

    # JS Code to extract the DOM
    js_code = """
    (() => {
      const tables = document.querySelectorAll('table');
      if (tables.length > 0) {
        return Array.from(tables).map(t => t.outerHTML).join('\\n\\n');
      }
      return document.body.innerHTML;
    })()
    """
    
    # We call Runtime.evaluate. Since context ID might change or we want the default context,
    # we don't specify contextId to default to the main frame context.
    cmd = {
        "id": 100,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_code,
            "returnByValue": True
        }
    }
    ws.send(json.dumps(cmd))
    
    # Loop to capture the response to our specific message ID 100
    ws.settimeout(5.0)
    for _ in range(20):
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 100:
                result = data.get("result", {}).get("result", {})
                val = result.get("value")
                if val:
                    print("\n=== SUCCESS: EXTRACTED DOM ===")
                    print(val[:500] + "...")
                    with open("unclaimed_property_raw.html", "w", encoding="utf-8") as f:
                        f.write(val)
                    print(f"Saved {len(val)} bytes to unclaimed_property_raw.html")
                    return
                else:
                    print("Error or empty value returned:")
                    print(json.dumps(data, indent=2))
                    return
        except websocket.WebSocketTimeoutException:
            print("Timeout waiting for evaluation response.")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

    ws.close()

extract_dom()
