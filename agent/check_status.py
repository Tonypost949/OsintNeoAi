import json
import urllib.request
import urllib.error
import websocket
import time

def check_where_it_is():
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
    
    # Check if we are stuck on Turnstile, or if the form is empty, or if error
    js_code = """
    (() => {
      const inputs = Array.from(document.querySelectorAll('input')).map(i => ({ id: i.id, value: i.value }));
      const turnstile = document.querySelector('.cf-turnstile') || document.querySelector('[id*="cf-"]') || document.querySelector('iframe[src*="cloudflare"]');
      const errorMsg = document.querySelector('.alert, .error, .invalid-feedback');
      return {
        url: window.location.href,
        inputs: inputs,
        turnstilePresent: !!turnstile,
        turnstileDetails: turnstile ? turnstile.outerHTML.substring(0, 300) : 'none',
        errorMessage: errorMsg ? errorMsg.innerText : 'none',
        bodyText: document.body.innerText.substring(0, 1000)
      };
    })()
    """
    
    cmd = {
        "id": 100,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_code,
            "returnByValue": True
        }
    }
    ws.send(json.dumps(cmd))
    
    ws.settimeout(2.0)
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 100:
                print(json.dumps(data.get("result", {}).get("result", {}).get("value"), indent=2))
                break
        except websocket.WebSocketTimeoutException:
            break
            
    ws.close()

check_where_it_is()
