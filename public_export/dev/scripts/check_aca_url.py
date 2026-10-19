import urllib.request
import json

url = "https://huntingtonbeachca.gov/aca/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
try:
    req = urllib.request.Request(url, headers=headers)
    res = urllib.request.urlopen(req)
    final_url = res.geturl()
    print(f"[+] Final ACA URL: {final_url}")
except Exception as e:
    print(f"[!] Error: {e}")
