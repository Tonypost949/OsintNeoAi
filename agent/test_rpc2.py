import requests
import re
import json

url = 'https://photos.google.com/share/AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew?key=d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3'
session = requests.Session()
r = session.get(url)

wiz_match = re.search(r'window\.WIZ_global_data\s*=\s*({.*?});', r.text, re.DOTALL)
wiz = json.loads(wiz_match.group(1))
bl = wiz.get("cfb2h", "")
sid = wiz.get("FdrFJe", "")

share_id = "AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew"
album_key = "d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3"

m = re.search(r'AF_initDataCallback\(({key: \'ds:1\'.*?})\);</script>', r.text, re.DOTALL)
blob = m.group(1)
data_json = json.loads(re.search(r'data:(.*?), sideChannel:', blob, re.DOTALL).group(1))
next_token = data_json[2]

req_payload = [share_id, next_token, None, None, album_key]
f_req = json.dumps([[["snAcKc", json.dumps(req_payload), None, "generic"]]])

paths = [
    f'https://photos.google.com/_/PhotosUi/data/batched?rpcids=snAcKc&f.sid={sid}&bl={bl}&hl=en&_reqid=12345&rt=c',
    f'https://photos.google.com/_/PhotosUi/data/batched/?rpcids=snAcKc&f.sid={sid}&bl={bl}&hl=en&_reqid=12345&rt=c',
    f'https://photos.google.com/share/_/PhotosUi/data/batched?rpcids=snAcKc&f.sid={sid}&bl={bl}&hl=en&_reqid=12345&rt=c',
    f'https://photos.google.com/_/PhotosUi/browserinfo?rpcids=snAcKc&f.sid={sid}&bl={bl}&hl=en&_reqid=12345&rt=c',
]

for p in paths:
    res = session.post(p, data={'f.req': f_req}, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'X-Same-Domain': '1',
        'Referer': url
    })
    print(f"{p[:70]} -> {res.status_code} (len: {len(res.text)})")
    if res.status_code == 200:
        print("Success! Head:", res.text[:200])
