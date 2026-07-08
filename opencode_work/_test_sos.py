import requests
import re

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

r = s.get('https://bizfileonline.sos.ca.gov/search/business', timeout=15)
print('Status:', r.status_code)
print('URL:', r.url)
print('Content-Type:', r.headers.get('Content-Type', ''))
print('Length:', len(r.text))

# Find forms and actions
actions = re.findall(r'action="([^"]*)"', r.text)
forms = re.findall(r'<form[^>]*>', r.text)
print('Forms:', forms[:5])
print('Actions:', actions[:5])

# Find search-related URLs
urls = re.findall(r'"(/[^"]*(?:search|query|api|business)[^"]*)"', r.text, re.I)
print('Search URLs:', urls[:10])

# Save HTML for inspection
with open(r"C:\Users\HP\OneDrive\Documents\opencode_work\ca_sos_search.html", "w", encoding="utf-8") as f:
    f.write(r.text)
print("Saved HTML to ca_sos_search.html")
