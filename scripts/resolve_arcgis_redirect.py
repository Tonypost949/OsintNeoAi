import urllib.request

url = 'https://arcg.is/051Wiy'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    response = urllib.request.urlopen(req)
    final_url = response.geturl()
    print(f"=== ARCGIS SHORTLINK RESOLVED ===")
    print(f"Shortlink: {url}")
    print(f"Final Redirect Target URL: {final_url}")
except Exception as e:
    print(f"Error resolving redirect: {e}")
