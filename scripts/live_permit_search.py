import urllib.request
import urllib.parse
import json

addresses = [
    "17631 Cameron", "17642 Beach", "17532 Cameron", 
    "17621 Cameron", "17622 Cameron", "17652 Cameron", 
    "17631 Cameron Lane", "17642 Beach Blvd"
]

print("[+] Executing live open-web search across Huntington Beach municipal domains for target permits...")

for addr in addresses:
    print(f"\n--- Searching live records for: {addr} ---")
    query = urllib.parse.quote(f'site:huntingtonbeachca.gov "{addr}" permit OR plan OR grading')
    url = f"https://html.duckduckgo.com/html/?q={query}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Simple extraction of result snippets
        import re
        results = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
        if results:
            for r in results[:3]:
                # clean up html tags
                clean_text = re.sub(r'<[^>]+>', '', r).strip()
                print(f"  [Hit] {clean_text}")
        else:
            print("  [-] No live indexed permits found.")
    except Exception as e:
        print(f"  [!] Search error: {e}")

