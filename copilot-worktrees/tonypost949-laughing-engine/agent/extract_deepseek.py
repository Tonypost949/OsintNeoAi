"""
Robust extractor for DeepSeek shared chats using the active Chrome DevTools Protocol.
Performs PUT requests to open tabs, and prints all websocket frames.
"""
import urllib.request
import json
import time
import websocket
import ssl

def extract_deepseek_chat(url, output_file):
    print(f"\n{'='*40}")
    print(f"Extracting DeepSeek chat: {url}")
    print(f"{'='*40}")
    try:
        # Check active tabs
        res = urllib.request.urlopen("http://127.0.0.1:9222/json")
        tabs = json.loads(res.read().decode('utf-8'))
    except Exception as e:
        print(f"Failed to connect to local Chrome on 9222: {e}")
        return False

    # Open a new tab via PUT method
    try:
        # To make a PUT request in urllib, we pass empty data or use a Custom Request
        req = urllib.request.Request("http://127.0.0.1:9222/json/new", method="PUT")
        new_tab_res = urllib.request.urlopen(req)
        new_tab = json.loads(new_tab_res.read().decode('utf-8'))
        ws_url = new_tab.get("webSocketDebuggerUrl")
        print(f"Opened new tab: {new_tab.get('id')}")
    except Exception as e:
        print(f"Failed to open new tab: {e}")
        # Fallback to reusing the first tab
        ws_url = tabs[0].get("webSocketDebuggerUrl")
        print("Reusing existing tab instead.")

    print(f"Connecting to websocket: {ws_url}")
    ws = websocket.create_connection(ws_url, suppress_origin=True)
    
    # Enable Page and Runtime
    ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
    print("Page enabled:", ws.recv())
    ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))
    print("Runtime enabled:", ws.recv())

    # Navigate
    print(f"Navigating to {url}...")
    ws.send(json.dumps({"id": 3, "method": "Page.navigate", "params": {"url": url}}))
    print("Navigation response:", ws.recv())

    # Wait for page load and client-side rendering
    print("Waiting 15 seconds for client-side JS rendering...")
    time.sleep(15)

    # JS to extract conversation messages from DeepSeek's DOM
    js_extract = """
    (() => {
      // DeepSeek chats render inside main or article tags, or inside chats lists
      // We will capture the whole text content of the page
      const text = document.body.innerText;
      const html = document.body.innerHTML;
      
      return {
        length: text.length,
        text: text,
        html_length: html.length
      };
    })()
    """
    
    print("Sending evaluation request...")
    ws.send(json.dumps({
        "id": 100,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_extract,
            "returnByValue": True,
            "awaitPromise": True
        }
    }))
    
    ws.settimeout(10.0)
    data_val = None
    
    # Read messages from websocket
    for _ in range(50):
        try:
            msg = ws.recv()
            data = json.loads(msg)
            # Log all messages to see details
            if "id" in data:
                print(f"Received msg ID={data.get('id')}")
            if data.get("id") == 100:
                result = data.get("result", {})
                if "exceptionDetails" in result:
                    print("JS Exception:", result.get("exceptionDetails"))
                data_val = result.get("result", {}).get("value")
                break
        except websocket.WebSocketTimeoutException:
            print("Websocket timeout waiting for response.")
            break
        except Exception as e:
            print(f"Error reading websocket: {e}")
            break

    if data_val:
        print(f"Extracted {data_val.get('length')} characters of text.")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(data_val.get("text", ""))
        print(f"Saved text content to {output_file}")
    else:
        print("Failed to get data from Runtime.evaluate.")

    # Close tab
    try:
        tab_id = new_tab.get("id") if 'new_tab' in locals() else None
        if tab_id:
            print(f"Closing tab {tab_id}...")
            urllib.request.urlopen(f"http://127.0.0.1:9222/json/close/{tab_id}")
    except Exception as e:
        print(f"Failed to close tab: {e}")
        
    ws.close()
    return True

if __name__ == "__main__":
    extract_deepseek_chat("https://chat.deepseek.com/a/chat/s/06e3c77c-3466-4e6c-817d-facd96370cf2", "deepseek_session_1.txt")
    extract_deepseek_chat("https://chat.deepseek.com/a/chat/s/41317237-4280-4707-8c82-0ac3f6d73c45", "deepseek_session_2.txt")
