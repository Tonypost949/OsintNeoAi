import json
import urllib.request
import websocket

def print_page_details():
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
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.recv()
    
    # Dump entire document text, all input values, and check for tables
    js_code = """
    (() => {
      const inputs = Array.from(document.querySelectorAll('input')).map(i => ({ id: i.id, value: i.value }));
      const tables = Array.from(document.querySelectorAll('table')).map(t => t.innerText);
      const spans = Array.from(document.querySelectorAll('span, p, div')).map(s => s.innerText).filter(t => t && t.trim().length > 0).slice(0, 100);
      return {
        url: window.location.href,
        inputs: inputs,
        tablesCount: tables.length,
        tablesContent: tables,
        textPreview: document.body.innerText
      };
    })()
    """
    ws.send(json.dumps({"id": 100, "method": "Runtime.evaluate", "params": {"expression": js_code, "returnByValue": True}}))
    
    ws.settimeout(3.0)
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 100:
                val = data.get("result", {}).get("result", {}).get("value")
                print(json.dumps(val, indent=2))
                break
        except websocket.WebSocketTimeoutException:
            break
            
    ws.close()

print_page_details()
