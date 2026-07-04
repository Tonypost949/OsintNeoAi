import requests
from bs4 import BeautifulSoup
import json
import sys

def scrape_dataset_urls():
    base_url = "https://catalog.data.gov/?sort=distance&q=&sort=distance&spatial_filter=&spatial_geometry=%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B-118.84765381417903%2C33.14470990718543%5D%2C%5B-117.22074874805651%2C33.14470990718543%5D%2C%5B-117.22074874805651%2C33.904870572105885%5D%2C%5B-118.84765381417903%2C33.904870572105885%5D%2C%5B-118.84765381417903%2C33.14470990718543%5D%5D%5D%7D&spatial_within=true&geography_label=Orange+County%2C+California"
    dataset_urls = []

    for page in range(1, 17):
        page_url = f"{base_url}&page={page}"
        try:
            response = requests.get(page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for h2 in soup.find_all('h3', class_='usa-collection__heading'):
                a = h2.find('a')
                if a and a.has_attr('href'):
                    url = a['href']
                    if not url.startswith('http'):
                        url = f"https://catalog.data.gov{url}"
                    dataset_urls.append(url)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}", file=sys.stderr)

    return dataset_urls

if __name__ == "__main__":
    urls = scrape_dataset_urls()
    result = {"dataset_urls": urls}
    print(json.dumps(result, indent=2))
