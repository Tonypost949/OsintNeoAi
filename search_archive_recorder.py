import requests
import json
import time

# Search Internet Archive for Gospel Swamp / Tract 405 plat maps
print('=== Searching Internet Archive ===')

searches = [
    'gospel swamp plat map 1912 orange county',
    'tract 405 huntington beach plat map',
    'tract 405 orange county plat',
    'gospel swamp orange county 1912',
    'wintersburg plat map orange county',
]

for query in searches:
    url = 'https://archive.org/advancedsearch.php'
    params = {
        'q': query,
        'fl[]': ['identifier', 'title', 'creator', 'date', 'mediatype'],
        'rows': 20,
        'output': 'json'
    }
    r = requests.get(url, params=params, timeout=30)
    print(f'\nQuery: {query}')
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        num_found = data.get('response', {}).get('numFound', 0)
        print(f'Results: {num_found}')
        for doc in data.get('response', {}).get('docs', [])[:3]:
            print(f'  Title: {doc.get("title", "N/A")}')
            print(f'  Identifier: {doc.get("identifier", "N/A")}')
            print(f'  Date: {doc.get("date", "N/A")}')
            print(f'  Mediatype: {doc.get("mediatype", "N/A")}')

# Also try the OC Recorder online search
print('\n=== OC Recorder Online Search ===')
# The OC Recorder has an online grantor/grantee search at:
# https://cr.occlerkrecorder.gov/RecorderWorksInternet
# But it requires interaction. Let me check if there's an API or if we can search via the catalog
url = 'http://7048.sydneyplus.com/archive/final/Portal/Default.aspx?lang=en-US'
r = requests.get(url, timeout=30)
print(f'OC Archives Catalog: {r.status_code}')

# Try the OC Recorder online search for grantor/grantee
url2 = 'https://cr.occlerkrecorder.gov/RecorderWorksInternet/Default.aspx'
r2 = requests.get(url2, timeout=30)
print(f'RecorderWorksInternet: {r2.status_code}')
if r2.status_code == 200:
    # Check for search forms
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r2.text, 'html.parser')
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action', '')
        method = form.get('method', '')
        print(f'Form action: {action}, method: {method}')
        inputs = form.find_all('input')
        for inp in inputs:
            name = inp.get('name', '')
            itype = inp.get('type', '')
            if name:
                print(f'  Input: name={name}, type={itype}')