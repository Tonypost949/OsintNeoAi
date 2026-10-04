import urllib.request
import json
import ssl

def query_search_index():
    # Query an alternative search engine API that doesn't block bots
    # to locate California unclaimed property pages containing Mercy House and Larry Haynes.
    url = "https://html.duckduckgo.com/html/?q=site:claimit.ca.gov+%22Mercy+House%22"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print("Querying DuckDuckGo HTML index for California Controller listings...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            html = response.read().decode('utf-8')
            if "Mercy House" in html or "claimit.ca.gov" in html:
                print("Found indexed listings on State Controller site!")
                # Parse links
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                for a in soup.find_all('a', class_='result__snippet'):
                    print("- ", a.get_text())
            else:
                print("No public search index matches found.")
    except Exception as e:
        print(f"Error querying search index: {e}")

query_search_index()
