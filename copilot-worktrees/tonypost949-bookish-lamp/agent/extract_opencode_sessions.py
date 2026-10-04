"""
Extract conversation data from OpenCode shared session links.
Saves extracted text blocks to files with UTF-8 encoding.
"""
import re
import sys
import os

def extract_opencode_session(raw_html):
    """Parse the inline script data from an OpenCode share page."""
    parts = []
    
    # Pattern to find text content in the serialized data
    text_pattern = r'type:"text",\s*text:"((?:[^"\\]|\\.)*)"'
    matches = re.findall(text_pattern, raw_html)
    
    for m in matches:
        try:
            content = m.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\').replace('\\t', '\t').replace('\\x3C', '<')
            if content.strip() and len(content.strip()) > 2:
                parts.append(content)
        except:
            pass
    
    return parts

def main():
    urls = [
        "https://opncd.ai/share/uE1o0rJY",
        "https://opncd.ai/share/nofIV75K"
    ]
    
    import urllib.request
    import ssl
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    for url in urls:
        share_id = url.split("/")[-1]
        print(f"Processing {share_id}...", flush=True)
        
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                raw = resp.read().decode('utf-8', errors='replace')
            
            print(f"  Downloaded {len(raw)} bytes", flush=True)
            
            parts = extract_opencode_session(raw)
            print(f"  Found {len(parts)} text blocks", flush=True)
            
            # Save all blocks to a single file
            outfile = f"opencode_data_{share_id}.txt"
            with open(outfile, "w", encoding="utf-8") as f:
                for i, p in enumerate(parts):
                    f.write(f"{'='*80}\n")
                    f.write(f"BLOCK {i+1}\n")
                    f.write(f"{'='*80}\n")
                    f.write(p)
                    f.write("\n\n")
            
            print(f"  Saved to {outfile}", flush=True)
                
        except Exception as e:
            print(f"  Error: {e}", flush=True)

if __name__ == "__main__":
    main()
