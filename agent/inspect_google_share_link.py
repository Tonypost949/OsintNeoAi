import urllib.request
import re
import os

url = "https://share.google/aimode/ajW40CRwfBZ90ihuO"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        print("HTTP Response Length:", len(html))
        
        # Save raw HTML to file for inspection
        os.makedirs("evidence", exist_ok=True)
        with open("evidence/google_share_link.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved raw HTML to evidence/google_share_link.html")

        # Regex search for shared prompts/responses or text
        prompts = re.findall(r'"([^"]{20,})"', html)
        print(f"Extracted string candidates: {len(prompts)}")
        for p in prompts[:10]:
            if any(k in p.lower() for k in ["prompt", "model", "gemini", "osint", "system", "role", "user"]):
                print(" -> Candidate:", p[:150])
except Exception as e:
    print("Error fetching Google Share URL:", e)
