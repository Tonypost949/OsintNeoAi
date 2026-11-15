from bs4 import BeautifulSoup

with open(r'C:\Amd949609_Antigravity_v1\evidence\truthfinder_records\dale_ann_verma_report_view.html', encoding='utf-8', errors='ignore') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

for a in soup.find_all('a'):
    href = a.get('href') or ''
    text = a.get_text(strip=True)
    if 'report' in href.lower() or 'report' in text.lower():
        print(f"{text} -> {href}")
