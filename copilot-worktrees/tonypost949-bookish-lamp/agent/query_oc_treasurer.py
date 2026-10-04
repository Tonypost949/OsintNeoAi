import urllib.request
import urllib.error
import ssl
from bs4 import BeautifulSoup

def query_oc_treasurer_unclaimed():
    # Query the Orange County Treasurer-Tax Collector's unclaimed funds pages
    # Let's search for published unclaimed funds tables or PDFs
    print("Querying Orange County Treasurer unclaimed funds index...")
    url = "https://www.ttc.ocgov.com/unclaimed-funds"
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
            # Look for links to PDFs or tables containing unclaimed funds lists
            links = []
            for a in soup.find_all('a'):
                href = a.get('href', '')
                if any(term in href.lower() for term in ['unclaimed', 'fund', 'money', 'check']):
                    links.append((a.get_text().strip(), href))
                    
            print(f"Found {len(links)} unclaimed funds resources on OC Treasurer site:")
            for title, href in links[:15]:
                print(f"- {title}: {href}")
    except Exception as e:
        print(f"Error querying OC Treasurer: {e}")

query_oc_treasurer_unclaimed()
