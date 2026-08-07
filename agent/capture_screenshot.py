import json
import urllib.request
import websocket
import base64

def capture_screenshot():
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
    ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
    ws.recv()
    
    # Capture Screenshot via CDP Page.captureScreenshot
    cmd = {
        "id": 100,
        "method": "Page.captureScreenshot",
        "params": {
            "format": "png"
        }
    }
    ws.send(json.dumps(cmd))
    
    ws.settimeout(10.0)
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 100:
                img_data = data.get("result", {}).get("data")
                if img_data:
                    with open("C:\\Users\\HP\\.gemini\\antigravity-ide\\scratch\\osint-agent\\turnstile_screenshot.png", "wb") as f:
                        f.write(base64.b64decode(img_data))
                    print("✅ Successfully captured screenshot to turnstile_screenshot.png")
                else:
                    print("No image data returned.")
                break
        except websocket.WebSocketTimeoutException:
            print("Timeout capturing screenshot.")
            break
            
    ws.close()

capture_screenshot()
