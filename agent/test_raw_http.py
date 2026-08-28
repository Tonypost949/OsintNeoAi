import http.client
import urllib.parse
import ssl
import json
import re

url = 'https://photos.google.com/share/AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew?key=d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3'

conn = http.client.HTTPSConnection("photos.google.com", context=ssl._create_unverified_context())
conn.request("GET", "/share/AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew?key=d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3", headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
})
resp = conn.getresponse()
html = resp.read().decode('utf-8')

wiz = json.loads(re.search(r'window\.WIZ_global_data\s*=\s*({.*?});', html, re.DOTALL).group(1))
bl = wiz.get("cfb2h", "")
sid = wiz.get("FdrFJe", "")

share_id = "AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew"
album_key = "d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3"

m = re.search(r'AF_initDataCallback\(({key: \'ds:1\'.*?})\);</script>', html, re.DOTALL)
data_json = json.loads(re.search(r'data:(.*?), sideChannel:', m.group(1), re.DOTALL).group(1))
next_token = data_json[2]

print("Token extracted:", next_token[:25])

rpc_path = f"/_/PhotosUi/data/batched?rpcids=snAcKc&f.sid={sid}&bl={bl}&hl=en&_reqid=12345&rt=c"

# Payload structure: [[["snAcKc", "[\"share_id\",\"token\",null,null,\"key\"]", null, "generic"]]]
inner_str = json.dumps([share_id, next_token, None, None, album_key])
req_obj = [[["snAcKc", inner_str, None, "generic"]]]
post_body = "f.req=" + urllib.parse.quote(json.dumps(req_obj, separators=(',', ':')))

headers = {
    'Host': 'photos.google.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Origin': 'https://photos.google.com',
    'Referer': url,
    'X-Same-Domain': '1'
}

conn.request("POST", rpc_path, body=post_body, headers=headers)
rpc_res = conn.getresponse()
print("RPC Status Code:", rpc_res.status)
data = rpc_res.read().decode('utf-8')
print("RPC Data Length:", len(data))
print("Sample:", data[:300])

if rpc_res.status == 200:
    # Clean and parse response
    clean = re.sub(r'^\)]}\'\s*', '', data)
    lines = clean.strip().split('\n')
    for l in lines:
        if l.strip().startswith('['):
            try:
                parsed = json.loads(l)
                for entry in parsed:
                    if isinstance(entry, list) and len(entry) >= 3 and entry[0] == 'wrb.fr' and entry[1] == 'snAcKc':
                        page_data = json.loads(entry[2])
                        print(f"Extracted {len(page_data[0])} additional photos from Page 2!")
                        print("Third token present:", bool(page_data[1]))
            except Exception as e:
                print("Parse error on line:", e)
