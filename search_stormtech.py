import json
with open(r'C:\OsintNeoAi\evidence\stormtech_legal_permit_index.json') as f:
    permits = json.load(f)

# Search for any permit mentioning 2400, 2247, or similar
for p in permits:
    desc = p.get('desc', '').lower()
    title = p.get('title', '').lower()
    if '2400' in desc or '2400' in title or '2247' in desc or '2247' in title or '2,247' in desc or '2,247' in title:
        print(f'{p["permit_no"]}: {p["agency"]} - {p["title"]} - {p["desc"]}')

# Also search for 'trench', 'chamber', 'cameron', 'beach blvd'
print()
for p in permits:
    desc = p.get('desc', '').lower()
    title = p.get('title', '').lower()
    if 'trench' in desc or 'trench' in title or 'chamber' in desc or 'chamber' in title or 'cameron' in desc or 'cameron' in title or 'beach blvd' in desc or 'beach blvd' in title:
        print(f'{p["permit_no"]}: {p["agency"]} - {p["title"]} - {p["desc"][:120]}')