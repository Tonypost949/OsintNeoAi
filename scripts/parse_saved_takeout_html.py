import re
import os

html_path = r"C:\Users\Amd949609\Downloads\Google Takeout.html"
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8", errors="ignore") as fp:
        html = fp.read()
        print(f"HTML size: {len(html)} bytes")
        links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', html)
        download_links = [l for l in links if "download" in l or "takeout" in l or "googleusercontent" in l]
        print(f"Found {len(download_links)} relevant download links:")
        for dl in download_links:
            print("  ->", dl)
else:
    print("Google Takeout.html not found.")
