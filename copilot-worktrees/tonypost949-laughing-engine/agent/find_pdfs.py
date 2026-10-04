import requests
from bs4 import BeautifulSoup
import os

url = "https://huntingtonbeach.legistar.com/LegislationDetail.aspx?ID=4610116&GUID=68D01C0E-9C8A-4A0B-976E-80436FF81A72" # I need to search for the right ID first, so let's just search the main page or use the API.
# Actually, the Legistar search page is POST-based and complex. 
# A better way is to use the Legistar web API if available, or just Google the exact PDF.

# Let's write a generic Google Search scraper using DuckDuckGo to find the exact PDF links
import urllib.parse
import re

def search_ddg_pdfs(query):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    for a in soup.find_all('a', class_='result__url'):
        href = a.get('href')
        if href and 'pdf' in href.lower():
            print(f"Found PDF: {href}")

print("Searching for Navigation Center Lease PDF...")
search_ddg_pdfs('site:huntingtonbeachca.gov "17642 Beach" "lease" filetype:pdf')
search_ddg_pdfs('site:huntingtonbeachca.gov "Navigation Center" "contract" filetype:pdf')
search_ddg_pdfs('site:huntingtonbeach.legistar.com "20-1799" filetype:pdf')
