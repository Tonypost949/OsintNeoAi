import json
import urllib.request
import urllib.error
import websocket
import time

def trigger_turnstile_on_tab():
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
    
    # Enable Page and Runtime
    ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
    ws.recv()
    ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))
    ws.recv()
    
    # Force page reload to get a fresh Turnstile captcha challenge on user's screen
    print("Reloading page...")
    ws.send(json.dumps({"id": 3, "method": "Page.reload"}))
    ws.recv()
    
    # Wait for reload to complete
    time.sleep(3)
    
    # JS code to type and click search to trigger Turnstile pop-up
    js_code = """
    (() => {
      const input = document.getElementById('lastName');
      if (!input) return 'Input field not found';
      
      input.focus();
      input.value = 'Mercy House Living Centers';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      
      const searchBtn = document.querySelector('button.btn-secondary') || document.getElementById('btn-turnstile') || document.querySelector('button[type="submit"]');
      if (!searchBtn) return 'Search button not found';
      
      searchBtn.click();
      return 'Triggered Search - Turnstile should now pop up';
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

    print("\nFresh search triggered. Check your browser screen now to click the Turnstile checkbox.")
    ws.close()

trigger_turnstile_on_tab()
