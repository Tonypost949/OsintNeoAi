import urllib.parse
import urllib.request
import re
import json

url = 'https://photos.google.com/share/AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew?key=d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3'

req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
})

with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8')

wiz = json.loads(re.search(r'window\.WIZ_global_data\s*=\s*({.*?});', html, re.DOTALL).group(1))
bl = wiz.get("cfb2h", "")
sid = wiz.get("FdrFJe", "")

share_id = "AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew"
album_key = "d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3"

m = re.search(r'AF_initDataCallback\(({key: \'ds:1\'.*?})\);</script>', html, re.DOTALL)
data_json = json.loads(re.search(r'data:(.*?), sideChannel:', m.group(1), re.DOTALL).group(1))
next_token = data_json[2]

print("Extracted continuation token:", next_token[:30], "...")

rpc_url = f"https://photos.google.com/_/PhotosUi/data/batched?rpcids=snAcKc&f.sid={sid}&bl={bl}&hl=en&_reqid=123456&rt=c"

# Prepare payload
inner_json = json.dumps([share_id, next_token, None, None, album_key])
f_req = json.dumps([[["snAcKc", inner_json, None, "generic"]]])

post_params = urllib.parse.urlencode({'f.req': f_req}).encode('utf-8')

post_req = urllib.request.Request(rpc_url, data=post_params, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Origin': 'https://photos.google.com',
    'Referer': url
})

try:
    with urllib.request.urlopen(post_req) as post_resp:
        res_data = post_resp.read().decode('utf-8')
        print("Success! Status:", post_resp.status, "Length:", len(res_data))
        print("Head:", res_data[:300])
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.reason)
    print("Error body:", e.read().decode('utf-8')[:300])
except Exception as e:
    print("Error:", e)
