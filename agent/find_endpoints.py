import requests
import re

url = 'https://photos.google.com/share/AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew?key=d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3'
r = requests.get(url)

# Find all script URLs and occurrences of batched
for m in re.finditer(r'([a-zA-Z0-9_/]+batched[a-zA-Z0-9_/]*)', r.text):
    print("Found batched string:", m.group(0))

# Find any RPC URLs in JS
for m in re.finditer(r'"(/_/[^"]+)"', r.text):
    print("Found relative path:", m.group(1))
