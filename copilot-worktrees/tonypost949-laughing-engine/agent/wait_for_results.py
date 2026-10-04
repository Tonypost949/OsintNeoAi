import json
import urllib.request
import websocket
import time

def wait_for_results():
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
    
    # Wait up to 15 seconds, checking every 3 seconds for either the results table or the Turnstile check status
    for i in range(5):
        print(f"Check {i+1}/5...")
        js_code = """
        (() => {
          const table = document.querySelector('table');
          const allText = document.body.innerText;
          const turnstileIframe = document.querySelector('iframe[src*="cloudflare"]');
          
          return {
            tableFound: !!table,
            tableHTML: table ? table.outerHTML.substring(0, 1000) : 'none',
            hasText: allText.includes('Mercy') || allText.includes('Haynes') || allText.includes('No properties found'),
            bodyPreview: allText.substring(0, 500),
            iframeFound: !!turnstileIframe
          };
        })()
        """
        
        ws.send(json.dumps({"id": 200 + i, "method": "Runtime.evaluate", "params": {"expression": js_code, "returnByValue": True}}))
        ws.settimeout(3.0)
        
        while True:
            try:
                msg = ws.recv()
                data = json.loads(msg)
                if data.get("id") == 200 + i:
                    res_val = data.get("result", {}).get("result", {}).get("value")
                    print(json.dumps(res_val, indent=2))
                    if res_val.get("tableFound") or "No properties found" in res_val.get("bodyPreview"):
                        print("Found results or no-results message!")
                        # Save DOM
                        ws.send(json.dumps({"id": 999, "method": "Runtime.evaluate", "params": {"expression": "document.body.innerHTML", "returnByValue": True}}))
                        msg_dom = ws.recv()
                        dom_val = json.loads(msg_dom).get("result", {}).get("result", {}).get("value")
                        with open("unclaimed_property_final_results.html", "w", encoding="utf-8") as f:
                            f.write(dom_val)
                        print("Saved results to unclaimed_property_final_results.html")
                        ws.close()
                        return
                    break
            except websocket.WebSocketTimeoutException:
                break
        time.sleep(3)
        
    ws.close()

wait_for_results()
