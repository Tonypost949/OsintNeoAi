import requests
import re
import json

url = 'https://photos.google.com/share/AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew?key=d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3'
session = requests.Session()
r = session.get(url)

wiz_match = re.search(r'window\.WIZ_global_data\s*=\s*({.*?});', r.text, re.DOTALL)
if wiz_match:
    wiz = json.loads(wiz_match.group(1))
    print("WIZ Keys:", list(wiz.keys()))
    at = wiz.get("SNlM0e", "")
    bl = wiz.get("cfb2h", "")
    sid = wiz.get("FdrFJe", "")
    print(f"at: {at}, bl: {bl}, sid: {sid}")

    ep = 'https://photos.google.com/_/PhotosUi/data/batched'
    full_ep = f"{ep}?rpcids=snAcKc&f.sid={sid}&bl={bl}&hl=en&_reqid=12345&rt=c"
    req_payload = ["AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew", "AH_uQ40vqJE5rijuNNj0ilAW0ONI0U3F6mkJhqFuXOtNWVkgqv9kViXjb0j1ct5EaPdLg9-cx8fgIWoM", None, None, "d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3"]
    f_req = json.dumps([[["snAcKc", json.dumps(req_payload), None, "generic"]]])

    res = session.post(full_ep, data={'f.req': f_req, 'at': at}, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Referer': url,
        'Origin': 'https://photos.google.com'
    })
    print(f"Status: {res.status_code}, Length: {len(res.text)}")
    print("Response head:", res.text[:300])
