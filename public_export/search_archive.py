import requests
import json

# Search Internet Archive for Gospel Swamp plat maps
search_url = 'https://archive.org/advancedsearch.php?q=gospel+swamp+plat+map+1912+orange+county&fl[]=identifier,title,creator,date&rows=20&output=json'
r2 = requests.get(search_url, timeout=30)
print(f'Search Gospel Swamp: {r2.status_code}')
if r2.status_code == 200:
    data = r2.json()
    print(f'Results: {data.get("response", {}).get("numFound", 0)}')
    for doc in data.get('response', {}).get('docs', [])[:5]:
        print(f'  {doc.get("title", "N/A")} - {doc.get("identifier", "N/A")}')

# Also search for Tract 405
search_url2 = 'https://archive.org/advancedsearch.php?q=tract+405+huntington+beach+plat&fl[]=identifier,title,creator,date&rows=20&output=json'
r3 = requests.get(search_url2, timeout=30)
print(f'Search Tract 405: {r3.status_code}')
if r3.status_code == 200:
    data = r3.json()
    print(f'Results: {data.get("response", {}).get("numFound", 0)}')
    for doc in data.get('response', {}).get('docs', [])[:5]:
        print(f'  {doc.get("title", "N/A")} - {doc.get("identifier", "N/A")}')

# Search for PW# 20-020
search_url3 = 'https://archive.org/advancedsearch.php?q=PW+20-020+huntington+beach&fl[]=identifier,title,creator,date&rows=20&output=json'
r4 = requests.get(search_url3, timeout=30)
print(f'Search PW# 20-020: {r4.status_code}')
if r4.status_code == 200:
    data = r4.json()
    print(f'Results: {data.get("response", {}).get("numFound", 0)}')
    for doc in data.get('response', {}).get('docs', [])[:5]:
        print(f'  {doc.get("title", "N/A")} - {doc.get("identifier", "N/A")}')