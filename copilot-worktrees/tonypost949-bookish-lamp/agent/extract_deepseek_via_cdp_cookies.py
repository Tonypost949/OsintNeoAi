"""
API-based DeepSeek extractor using cookies retrieved via CDP.
"""
import json
import urllib.request
import ssl

def fetch_chat_api(share_id, cookie):
    url = f"https://chat.deepseek.com/api/v0/chat/share/detail?share_id={share_id}"
    print(f"Fetching chat details from API for share_id: {share_id}...")
    
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": cookie,
        "Accept": "application/json"
    })
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            raw = resp.read().decode('utf-8')
            print(f"Response status: {resp.status}")
            print(f"Response body (first 500 chars): {raw[:500]}")
            data = json.loads(raw)
            return data
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        try:
            print(f"Error body: {e.read().decode('utf-8')[:500]}")
        except:
            pass
        return None
    except Exception as e:
        print(f"API fetch failed: {e}")
        return None

def format_chat(data):
    if not data or 'data' not in data:
        return "No data found."
    
    chat_data = data.get('data', {})
    title = chat_data.get('title', 'Untitled Chat')
    messages = chat_data.get('messages', [])
    
    out = []
    out.append(f"# DeepSeek Chat: {title}\n")
    
    for msg in messages:
        role = msg.get('role', '').upper()
        content = msg.get('content', '')
        out.append(f"{'='*80}\n{role}\n{'='*80}\n{content}\n\n")
        
    return "".join(out)

def main():
    try:
        with open("deepseek_cookies.txt", "r") as f:
            cookie = f.read().strip()
    except Exception as e:
        print(f"Failed to read deepseek_cookies.txt: {e}")
        return

    shares = [
        "06e3c77c-3466-4e6c-817d-facd96370cf2",
        "41317237-4280-4707-8c82-0ac3f6d73c45"
    ]
    
    for i, share_id in enumerate(shares):
        data = fetch_chat_api(share_id, cookie)
        if data:
            formatted = format_chat(data)
            outfile = f"deepseek_session_{i+1}.txt"
            with open(outfile, "w", encoding="utf-8") as f:
                f.write(formatted)
            print(f"Successfully saved formatting to {outfile}")
        else:
            print(f"Could not retrieve details for {share_id}")

if __name__ == "__main__":
    main()
