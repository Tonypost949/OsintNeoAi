import json
import urllib.request
import urllib.error
import websocket
import sys

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

    print(f"Connecting to: {ws_url}")
    # Fix 403 Forbidden origin issue by omitting the Origin header
    ws = websocket.create_connection(ws_url, suppress_origin=True)
    
    # Enable Page and Runtime
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.recv()
    
    # Execute JS to get the innerHTML of the results table/body
    js_code = """
    (() => {
      const tables = document.querySelectorAll('table');
      if (tables.length > 0) {
        return Array.from(tables).map(t => t.outerHTML).join('\\n\\n');
      }
      const divs = Array.from(document.querySelectorAll('div, tr, td')).filter(el => {
        return el.innerText && (el.innerText.includes('Mercy') || el.innerText.includes('Haynes'));
      });
      return divs.map(d => d.innerText).slice(0, 10).join('\\n');
    })()
    """
    
    cmd = {
        "id": 2,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_code,
            "returnByValue": True
        }
    }
    ws.send(json.dumps(cmd))
    
    res = ws.recv()
    data = json.loads(res)
    
    result = data.get("result", {}).get("result", {})
    val = result.get("value")
    if val:
        print("\n=== EXTRACTED DATA FROM SCREEN ===")
        print(val[:1000] + "..." if len(val) > 1000 else val)
        with open("unclaimed_property_raw.html", "w", encoding="utf-8") as f:
            f.write(val)
        print(f"\nSaved raw data to unclaimed_property_raw.html ({len(val)} bytes)")
    else:
        print("No value returned from JS evaluation.")
        print(data)
    
    ws.close()

extract_dom()
