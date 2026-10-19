import re

with open(r'C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\db66e1e0-b949-11f1-8e00-dbd4e67e7847.pdf.txt') as f:
    text = f.read()

# Search for StormTech specifications
keywords = ['stormtech', 'mc-3500', 'chamber', 'storm drain', 'detention', 'retention', 'isolation', 'manifold', 'pipe', 'hpe', 'n-12', 'ads', '12"', '24"', 'hpe', 'isolation row', 'isolator row']

for kw in keywords:
    matches = [(m.start(), m.end()) for m in re.finditer(kw, text, re.IGNORECASE)]
    if matches:
        print(f"\n=== '{kw}' found {len(matches)} times ===")
        for start, end in matches[:5]:
            context = text[max(0,start-100):end+200]
            print(f"  ...{context}...")

# Also extract any numbers with LF, linear feet, etc.
print("\n=== LINEAR FOOTAGE / LENGTH SPECIFICATIONS ===")
lf_pattern = r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:lf|LF|linear feet|linear foot|feet|ft\.?|inches?|in\.?)'
for m in re.finditer(lf_pattern, text, re.IGNORECASE):
    val = m.group(1)
    context = text[max(0,m.start()-50):m.end()+100]
    if 'storm' in context.lower() or 'chamber' in context.lower() or 'pipe' in context.lower() or 'drain' in context.lower():
        print(f"  {val} - ...{context}...")

# Look for any quantity/count specifications
print("\n=== QUANTITY / COUNT SPECIFICATIONS ===")
qty_pattern = r'(?:number of|qty|quantity|count|chambers?|end caps?|rows?)\s*(?:=|:|is)?\s*(\d+)'
for m in re.finditer(qty_pattern, text, re.IGNORECASE):
    context = text[max(0,m.start()-80):m.end()+80]
    print(f"  {m.group(1)} - ...{context}...")