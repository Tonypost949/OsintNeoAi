from bs4 import BeautifulSoup

with open(r'C:\Amd949609_Antigravity_v1\evidence\truthfinder_records\dale_ann_verma_report_view.html', encoding='utf-8', errors='ignore') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

buttons = soup.find_all(['button', 'div', 'span', 'form'])
for b in buttons:
    txt = b.get_text(strip=True)
    if 'open report' in txt.lower():
        print(f"Tag: {b.name}, Attributes: {b.attrs}")
        parent = b.parent
        print(f"Parent Tag: {parent.name}, Parent Attrs: {parent.attrs}\n---")
