import requests
import json
import re

url = 'https://photos.google.com/share/AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew?key=d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3'
session = requests.Session()
r = session.get(url)

wiz = json.loads(re.search(r'window\.WIZ_global_data\s*=\s*({.*?});', r.text, re.DOTALL).group(1))
bl = wiz.get("cfb2h", "")
sid = wiz.get("FdrFJe", "")
share_id = "AF1QipOfvIA-7D5ZW5bSwg8vuu5l-0fwxIwrKR06Q5WOYJtisu791Qou2NlSiHIxnn68ew"
album_key = "d3p5WXFzNnEySWhoRkNpaF9GOWp1NXF2a1pPY1F3"

m = re.search(r'AF_initDataCallback\(({key: \'ds:1\'.*?})\);</script>', r.text, re.DOTALL)
data_json = json.loads(re.search(r'data:(.*?), sideChannel:', m.group(1), re.DOTALL).group(1))
next_token = data_json[2]

print("Token:", next_token[:20])

# In Google Photos, the RPC endpoint is `https://photos.google.com/_/PhotosUi/data/batched`
# Note: it requires `?rpcids=snAcKc&_reqid=...`
rpc_url = f"https://photos.google.com/_/PhotosUi/data/batched?rpcids=snAcKc&f.sid={sid}&bl={bl}&hl=en&_reqid=12345&rt=c"
req_payload = [share_id, next_token, None, None, album_key]
f_req = json.dumps([[["snAcKc", json.dumps(req_payload), None, "generic"]]])

# Write curl command
curl_cmd = f'''curl -X POST "{rpc_url}" -H "Content-Type: application/x-www-form-urlencoded;charset=UTF-8" -H "Referer: {url}" -H "Origin: https://photos.google.com" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0" --data-urlencode "f.req={f_req}"'''

with open("agent/test_curl.bat", "w", encoding="utf-8") as f:
    f.write(curl_cmd)
print("Saved agent/test_curl.bat")
