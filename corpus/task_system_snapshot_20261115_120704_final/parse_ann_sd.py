from bs4 import BeautifulSoup

with open(r'C:\Amd949609_Antigravity_v1\evidence\truthfinder_records\TF_Search_Ann_Verma_SD.html', encoding='utf-8', errors='ignore') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("Title:", soup.title)
for person in soup.find_all('div', class_='person'):
    name = person.get('data-name') or ''
    age = person.get('data-age') or ''
    order = person.get('data-response-order') or ''
    tcg_id = person.get('data-tcg-id') or ''
    text = person.get_text(separator=' | ', strip=True)
    print(f"Match #{order}: {name} (Age: {age}) [ID: {tcg_id}]")
    print(f"Details: {text[:300]}\n---")
