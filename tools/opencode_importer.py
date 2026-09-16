import json
import urllib.request
import re
from pathlib import Path

# The OpenCode Share Links
URLS = [
    "https://opncd.ai/share/oOR05Zz2",
    "https://opncd.ai/share/MFvIr62Z",
    "https://opncd.ai/share/UfTTjyQi",
    "https://opncd.ai/share/hnwstWSz"
]

def import_opencode_shares():
    print("[+] Ghosting into OpenCode Shares to extract raw python tools...")
    out_dir = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/tools/imported_opencode")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    for url in URLS:
        try:
            print(f"  [-] Fetching {url} ...")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')
                
            match = re.search(r'<code[^>]*>(.*?)</code>', html, re.DOTALL | re.IGNORECASE)
            code_content = match.group(1) if match else html
            
            if match:
                code_content = code_content.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&quot;", '"')
                
            # SANITIZE: Remove any hardcoded API keys before writing
            code_content = re.sub(r'AIza[0-9A-Za-z-_]{35}', 'REMOVED_BY_SYSTEM', code_content)
            # Sanitize ADO PATs and other secrets
            code_content = re.sub(r'[0-9a-zA-Z]{52}', 'REMOVED_BY_SYSTEM', code_content) 
            
            filename = url.split("/")[-1] + "_tool.py"
            out_path = out_dir / filename
            
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(code_content)
                
            print(f"  [+] Extracted and saved to {out_path}")
            
        except Exception as e:
            print(f"  [!] Failed to extract from {url}: {e}")

if __name__ == '__main__':
    import_opencode_shares()
