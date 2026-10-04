import requests
from bs4 import BeautifulSoup

def find_hud_link():
    url = "https://www.huduser.gov/portal/datasets/ahar/ahar-2023-part-1.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    for a in soup.find_all('a', href=True):
        if 'xls' in a['href'] or 'csv' in a['href'] or '2023' in a['href']:
            print(f"Found link: {a['href']}")

if __name__ == '__main__':
    find_hud_link()
