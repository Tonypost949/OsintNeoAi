import json
import urllib.request
import urllib.error
import websocket
import time

def reload_and_extract():
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
    
    # Enable Page
    ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
    ws.recv()
    
    # Reload page
    print("Reloading page...")
    ws.send(json.dumps({"id": 2, "method": "Page.reload"}))
    ws.recv()
    
    # Wait 3 seconds for reload
    time.sleep(3)
    
    # Enable Runtime
    ws.send(json.dumps({"id": 3, "method": "Runtime.enable"}))
    ws.recv()

    # JS code to type Mercy House and click Search
    js_code = """
    (() => {
      const input = document.getElementById('lastName');
      if (!input) return 'Input field not found';
      
      input.focus();
      input.value = 'Mercy House Living Centers';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      
      const searchBtn = document.querySelector('button.btn-secondary') || document.getElementById('btn-turnstile');
      if (!searchBtn) return 'Search button not found';
      
      searchBtn.click();
      return 'Form reloaded, filled, and searched.';
    })()
    """
    
    cmd = {
        "id": 101,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_code,
            "returnByValue": True
        }
    }
    ws.send(json.dumps(cmd))
    
    # Capture response
    ws.settimeout(2.0)
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 101:
                print("JS output:", data.get("result", {}).get("result", {}).get("value"))
                break
        except websocket.WebSocketTimeoutException:
            break

    print("Form has been submitted. Check your browser now for the Turnstile verification.")
    ws.close()

reload_and_extract()
