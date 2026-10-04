import json
import urllib.request
import urllib.error
import websocket
import time

def run_search_on_tab():
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
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
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
      input.blur();
      
      const searchBtn = document.querySelector('button.btn-secondary') || document.getElementById('btn-turnstile');
      if (!searchBtn) return 'Search button not found';
      
      searchBtn.click();
      return 'Typed and clicked search';
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

    # Wait 4 seconds for AJAX results to load
    print("Waiting 4 seconds for results...")
    time.sleep(4)

    # JS code to dump results table
    dump_js = """
    (() => {
      const table = document.querySelector('table');
      if (table) return table.outerHTML;
      
      // Let's check for any message or other elements
      const mainText = document.body.innerText;
      if (mainText.includes('No properties found') || mainText.includes('no matching records')) {
        return 'NO_PROPERTIES_FOUND';
      }
      return 'NO_TABLE_YET: ' + mainText.substring(0, 1000);
    })()
    """
    
    cmd2 = {
        "id": 102,
        "method": "Runtime.evaluate",
        "params": {
            "expression": dump_js,
            "returnByValue": True
        }
    }
    ws.send(json.dumps(cmd2))
    
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            if data.get("id") == 102:
                val = data.get("result", {}).get("result", {}).get("value")
                print("\n=== SEARCH RESULTS ===")
                if val == 'NO_PROPERTIES_FOUND':
                    print("No unclaimed property found for 'Mercy House Living Centers'.")
                else:
                    print(val[:2000] + "..." if len(val) > 2000 else val)
                    with open("search_results.html", "w", encoding="utf-8") as f:
                        f.write(val)
                break
        except websocket.WebSocketTimeoutException:
            break

    ws.close()

run_search_on_tab()
