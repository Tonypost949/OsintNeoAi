import json

with open(r'C:\OsintNeoAi\evidence\stormtech_legal_permit_index.json') as f:
    permits = json.load(f)

print(f'Total permits: {len(permits)}')

# Filter for Huntington Beach
hb_permits = [p for p in permits if 'huntington beach' in p.get('agency', '').lower()]
print(f'Huntington Beach permits: {len(hb_permits)}')
for p in hb_permits:
    print(f'  {p["permit_no"]}: {p["title"]} - {p["desc"]}')

# Filter for StormTech
st_permits = [p for p in permits if 'stormtech' in p.get('title', '').lower() or 'stormtech' in p.get('desc', '').lower()]
print(f'StormTech permits: {len(st_permits)}')
for p in st_permits:
    print(f'  {p["permit_no"]}: {p["agency"]} - {p["title"]} - {p["desc"]}')

# Filter for Costa Mesa (skate park StormTech)
cm_permits = [p for p in permits if 'costa mesa' in p.get('agency', '').lower()]
print(f'Costa Mesa permits: {len(cm_permits)}')
for p in cm_permits:
    print(f'  {p["permit_no"]}: {p["title"]} - {p["desc"]}')

# Filter for hexavalent chromium
cr6_permits = [p for p in permits if 'hexavalent' in p.get('title', '').lower() or 'hexavalent' in p.get('desc', '').lower() or 'chromium' in p.get('title', '').lower() or 'chromium' in p.get('desc', '').lower()]
print(f'Hexavalent Chromium permits: {len(cr6_permits)}')
for p in cr6_permits:
    print(f'  {p["permit_no"]}: {p["agency"]} - {p["title"]} - {p["desc"]}')

# Filter for Orange County
oc_permits = [p for p in permits if 'orange county' in p.get('agency', '').lower()]
print(f'Orange County permits: {len(oc_permits)}')
for p in oc_permits[:10]:
    print(f'  {p["permit_no"]}: {p["agency"]} - {p["title"]} - {p["desc"][:80]}...')