import urllib.request
from bs4 import BeautifulSoup
import ssl

def parse_ddg_results():
    url = "https://html.duckduckgo.com/html/?q=site:claimit.ca.gov+%22Mercy+House%22"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Print all result snippets and links
            results = soup.find_all('div', class_='result__body')
            print(f"Total results found: {len(results)}")
            for r in results:
                title = r.find('a', class_='result__url')
                snippet = r.find('a', class_='result__snippet')
                if title and snippet:
                    print("-" * 70)
                    print("Title:", title.get_text().strip())
                    print("URL:", title.get('href'))
                    print("Snippet:", snippet.get_text().strip())
    except Exception as e:
        print(f"Error parsing: {e}")

parse_ddg_results()
