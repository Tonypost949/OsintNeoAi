import json
import urllib.request
import websocket
import time

def fix_viewport_and_reload():
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
    ws.send(json.dumps({"id": 1, "method": "Emulation.setDeviceMetricsOverride", "params": {
        "width": 1920,
        "height": 1080,
        "deviceScaleFactor": 1,
        "mobile": False
    }}))
    ws.recv()
    
    print("Resized viewport to 1920x1080. Reloading page...")
    ws.send(json.dumps({"id": 2, "method": "Page.reload"}))
    ws.recv()
    
    time.sleep(4)
    
    ws.send(json.dumps({"id": 3, "method": "Runtime.enable"}))
    ws.recv()
    
    # Enter search name and click search
    js_code = """
    (() => {
      const input = document.getElementById('lastName');
      if (!input) return 'Input not found';
      input.value = 'Mercy House Living Centers';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      
      const searchBtn = document.querySelector('button.btn-secondary') || document.querySelector('button[type="submit"]');
      if (!searchBtn) return 'Button not found';
      searchBtn.click();
      return 'Form submitted in resized window.';
    })()
    """
    ws.send(json.dumps({"id": 4, "method": "Runtime.evaluate", "params": {"expression": js_code, "returnByValue": True}}))
    ws.recv()
    
    print("Search submitted. Waiting 3 seconds for Turnstile rendering...")
    time.sleep(3)
    
    # Capture new screenshot
    ws.send(json.dumps({"id": 5, "method": "Page.captureScreenshot"}))
    ws.settimeout(10.0)
    import base64
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 5:
                img_data = data.get("result", {}).get("data")
                if img_data:
                    with open("C:\\Users\\HP\\.gemini\\antigravity-ide\\scratch\\osint-agent\\turnstile_screenshot_resized.png", "wb") as f:
                        f.write(base64.b64decode(img_data))
                    print("Captured turnstile_screenshot_resized.png")
                break
        except websocket.WebSocketTimeoutException:
            break
            
    ws.close()

fix_viewport_and_reload()
