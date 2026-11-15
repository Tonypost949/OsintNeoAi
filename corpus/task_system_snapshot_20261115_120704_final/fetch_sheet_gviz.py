import urllib.request

url = "https://docs.google.com/spreadsheets/d/1GiNM335Vn4T7WgK6fdmYDluvwY8dD23loQbjClvViDk/gviz/tq?tqx=out:csv&gid=0"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
try:
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode("utf-8")
        print("Exported CSV length:", len(content))
        print("First 1000 characters:")
        print(content[:1000])
        with open("/mnt/c/Amd949609_Antigravity_v1/summaries/LIVE_GOOGLE_SHEET_EXPORT.csv", "w", encoding="utf-8") as f:
            f.write(content)
except Exception as e:
    print("Error:", e)
