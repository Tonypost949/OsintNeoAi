import re
import os
import json
from html.parser import HTMLParser

html_path = r"C:\Users\Amd949609\Downloads\OC Land Insights - Home.html"

class OCLandInsightsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_href = None
        self.current_text = []
        self.in_link = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value:
                    self.current_href = value
                    self.in_link = True
                    self.current_text = []
    
    def handle_endtag(self, tag):
        if tag == 'a' and self.in_link:
            text = ' '.join(self.current_text).strip()
            if self.current_href and text:
                self.links.append({
                    'url': self.current_href,
                    'text': text
                })
            self.in_link = False
            self.current_href = None
            self.current_text = []
    
    def handle_data(self, data):
        if self.in_link:
            self.current_text.append(data.strip())

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8", errors="ignore") as fp:
        html = fp.read()
        print(f"HTML size: {len(html)} bytes")
        
        parser = OCLandInsightsParser()
        parser.feed(html)
        
        print(f"\nFound {len(parser.links)} links:")
        print("-" * 80)
        
        categories = {
            'maps': [],
            'resources': [],
            'other': []
        }
        
        for link in parser.links:
            url = link['url']
            text = link['text']
            
            if 'map-viewer' in url:
                categories['maps'].append(link)
            elif any(kw in url.lower() for kw in ['youtube', 'opendata', 'ocpublicworks', 'hub.arcgis']):
                categories['resources'].append(link)
            else:
                categories['other'].append(link)
        
        print("\n=== FEATURED MAPS ===")
        for link in categories['maps']:
            print(f"  {link['text']}")
            print(f"    -> {link['url']}")
        
        print("\n=== RESOURCES ===")
        for link in categories['resources']:
            print(f"  {link['text']}")
            print(f"    -> {link['url']}")
        
        print("\n=== OTHER LINKS ===")
        for link in categories['other']:
            print(f"  {link['text']}")
            print(f"    -> {link['url']}")
        
        # Save to JSON
        output_path = r"C:\Users\Amd949609\StudioProjects\OsintNeoAi\data\oc_land_insights_links.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2)
        print(f"\nSaved to: {output_path}")
        
else:
    print("OC Land Insights - Home.html not found.")
