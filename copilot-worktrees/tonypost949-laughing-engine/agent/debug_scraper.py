import requests

def fetch_page_content():
    url = "https://catalog.data.gov/?sort=distance&q=&sort=distance&spatial_filter=&spatial_geometry=%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B-118.84765381417903%2C33.14470990718543%5D%2C%5B-117.22074874805651%2C33.14470990718543%5D%2C%5B-117.22074874805651%2C33.904870572105885%5D%2C%5B-118.84765381417903%2C33.904870572105885%5D%2C%5B-118.84765381417903%2C33.14470990718543%5D%5D%5D%7D&spatial_within=true&geography_label=Orange+County%2C+California&page=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")

if __name__ == "__main__":
    fetch_page_content()
