import urllib.request
import re
import csv
import json

url = "https://docs.google.com/spreadsheets/d/1GiNM335Vn4T7WgK6fdmYDluvwY8dD23loQbjClvViDk/htmlview"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL)
        print(f"Total HTML rows found: {len(rows)}")
        parsed_table = []
        for r in rows:
            cells = re.findall(r"<(?:td|th)[^>]*>(.*?)</(?:td|th)>", r, re.DOTALL)
            clean_cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            if any(clean_cells):
                parsed_table.append(clean_cells)
        
        with open("parsed_sheet.json", "w", encoding="utf-8") as f:
            json.dump(parsed_table, f, indent=2)
            
        print("First 10 rows:")
        for r in parsed_table[:10]:
            print(" | ".join(r))
except Exception as e:
    print(f"Exception: {e}")
