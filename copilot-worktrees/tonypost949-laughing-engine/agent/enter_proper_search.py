import json
import urllib.request
import websocket
import time

def enter_proper_search():
    res = urllib.request.urlopen("http://127.0.0.1:9222/json")
    tabs = json.loads(res.read().decode('utf-8'))
    ws_url = None
    for tab in tabs:
        if tab.get("id") == "C6E86A58CB4F555E85566B80E7F03086":
            ws_url = tab.get("webSocketDebuggerUrl")
            break
            
    if not ws_url:
        print("Tab not found.")
        return

    ws = websocket.create_connection(ws_url, suppress_origin=True)
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.recv()
    
    # Robust script to fill inputs and trigger Angular form updates
    js_code = """
    (() => {
      const input = document.getElementById('lastName');
      if (!input) return 'lastName input not found';
      
      // Clear any errors by focusing and typing
      input.focus();
      input.value = '';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      
      input.value = 'Mercy House Living Centers';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      input.blur();
      
      // Force click on search button
      const searchBtn = document.getElementById('searchButton') || document.querySelector('button.btn-secondary') || document.querySelector('button[type="submit"]');
      if (!searchBtn) return 'Search button not found';
      
      searchBtn.click();
      return 'Proper input filled and searched';
    })()
    """
    
    ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {"expression": js_code, "returnByValue": True}}))
    ws.recv()
    
    print("Submitted proper form. Waiting 4 seconds for Turnstile/results...")
    time.sleep(4)
    
    # Capture final state screenshot
    ws.send(json.dumps({"id": 3, "method": "Page.captureScreenshot"}))
    ws.settimeout(10.0)
    import base64
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 3:
                img_data = data.get("result", {}).get("data")
                if img_data:
                    with open("C:\\Users\\HP\\.gemini\\antigravity-ide\\scratch\\osint-agent\\turnstile_screenshot_final.png", "wb") as f:
                        f.write(base64.b64decode(img_data))
                    print("Captured turnstile_screenshot_final.png")
                break
        except websocket.WebSocketTimeoutException:
            break
            
    ws.close()

enter_proper_search()
