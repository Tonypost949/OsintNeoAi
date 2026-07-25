import json
import urllib.request
import websocket
import time

def click_and_solve():
    res = urllib.request.urlopen("http://127.0.0.1:9222/json")
    tabs = json.loads(res.read().decode('utf-8'))
    ws_url = None
    for tab in tabs:
        if tab.get("id") == "274FE63BEA3697F1A9D70FDCBEC669B6":
            ws_url = tab.get("webSocketDebuggerUrl")
            break
            
    if not ws_url:
        print("Tab not found.")
        return

    ws = websocket.create_connection(ws_url, suppress_origin=True)
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.recv()
    
    # Reload and wait for Turnstile iframe to render
    print("Reloading...")
    ws.send(json.dumps({"id": 2, "method": "Page.reload"}))
    ws.recv()
    time.sleep(5)
    
    # Check if we can find the Turnstile iframe coordinates to trigger a click
    js_find_coords = """
    (() => {
      const iframe = document.querySelector('iframe[src*="cloudflare"]');
      if (!iframe) return 'Iframe not found';
      const rect = iframe.getBoundingClientRect();
      return {
        x: rect.left + (rect.width / 2),
        y: rect.top + (rect.height / 2),
        width: rect.width,
        height: rect.height
      };
    })()
    """
    ws.send(json.dumps({"id": 3, "method": "Runtime.evaluate", "params": {"expression": js_find_coords, "returnByValue": True}}))
    
    coords = None
    ws.settimeout(3.0)
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 3:
                coords = data.get("result", {}).get("result", {}).get("value")
                print("Turnstile coordinates:", coords)
                break
        except websocket.WebSocketTimeoutException:
            break
            
    if coords and isinstance(coords, dict) and 'x' in coords:
        # Click the center of the Turnstile checkbox
        print(f"Clicking Turnstile checkbox at x={coords['x']}, y={coords['y']}...")
        ws.send(json.dumps({"id": 4, "method": "Input.dispatchMouseEvent", "params": {
            "type": "mousePressed",
            "x": coords['x'],
            "y": coords['y'],
            "button": "left",
            "clickCount": 1
        }}))
        ws.recv()
        ws.send(json.dumps({"id": 5, "method": "Input.dispatchMouseEvent", "params": {
            "type": "mouseReleased",
            "x": coords['x'],
            "y": coords['y'],
            "button": "left",
            "clickCount": 1
        }}))
        ws.recv()
        
        print("Click dispatched. Waiting 5 seconds...")
        time.sleep(5)
        
        # Check if the page is unlocked and enter the search term
        js_search = """
        (() => {
          const input = document.getElementById('lastName');
          if (!input) return 'lastName input not found';
          input.focus();
          input.value = 'Mercy House Living Centers';
          input.dispatchEvent(new Event('input', { bubbles: true }));
          
          const searchBtn = document.querySelector('button.btn-secondary') || document.getElementById('searchButton');
          if (searchBtn) {
            searchBtn.click();
            return 'Clicked search';
          }
          return 'Search button not found';
        })()
        """
        ws.send(json.dumps({"id": 6, "method": "Runtime.evaluate", "params": {"expression": js_search, "returnByValue": True}}))
        ws.recv()
        
    ws.close()

click_and_solve()
