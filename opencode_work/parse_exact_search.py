from bs4 import BeautifulSoup

with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\brad_smith_exact.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
results = soup.find_all('li', class_='b_algo')

print(f'Found {len(results)} results\n')

for i, result in enumerate(results, 1):
    title_elem = result.find('h2')
    if title_elem:
        title = title_elem.get_text()
        link = title_elem.find('a')
        url = link['href'] if link else 'No URL'
        
        snippet_elem = result.find('p')
        snippet = snippet_elem.get_text() if snippet_elem else 'No snippet'
        
        print(f'{i}. {title}')
        print(f'   URL: {url}')
        print(f'   {snippet[:300]}')
        print()
