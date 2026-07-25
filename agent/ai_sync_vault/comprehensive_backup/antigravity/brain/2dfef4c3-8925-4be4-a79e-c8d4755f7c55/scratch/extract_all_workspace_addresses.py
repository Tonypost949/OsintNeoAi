import os
import re
import json

txt_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\opencode_work\extracted_text"
output_report = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\workspace_all_extracted_addresses.json"

print("=== STARTING FULL WORKSPACE ADDRESS EXTRACTION (OCR TEXTS) ===")

all_addresses = set()

# Regex to capture street addresses
addr_pattern = re.compile(
    r"(\d{3,6}\s+[A-Za-z0-9\s\.\#\-]{2,30}\s+(?:BLVD|LN|LN\.|AVE|RD|ST|DR|WAY|COURT|CT|PLAZA|PL|TERRACE|CIRCLE|HUNTINGTON|GARDEN|CARLETON|COLE|SLATER|BEACH))",
    re.IGNORECASE
)

if not os.path.exists(txt_dir):
    print("OCR text directory not found!")
    exit(1)

files = [f for f in os.listdir(txt_dir) if f.lower().endswith('.txt')]
print(f"Scanning {len(files)} OCR text files...")

for f in files:
    path = os.path.join(txt_dir, f)
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as file_obj:
            content = file_obj.read()
            matches = addr_pattern.findall(content)
            for m in matches:
                addr_clean = m.strip().upper()
                # Exclude company boilerplate and standard headers
                if not any(exclude in addr_clean for exclude in ("ARMSTRONG", "SHELTON", "CT 06484", "800.352.0050", "INQUIRY", "Toll Free", "ZIP CODE")):
                    # Normalize whitespace
                    addr_clean = " ".join(addr_clean.split())
                    all_addresses.add(addr_clean)
    except Exception as e:
        pass

# Group by street name for clean viewing
grouped = {}
for addr in all_addresses:
    # Try to extract street name
    match = re.search(r"\d+\s+(.*)", addr)
    if match:
        street = match.group(1).strip()
        grouped.setdefault(street, []).append(addr)

# Save to JSON
with open(output_report, 'w', encoding='utf-8') as f:
    json.dump(list(all_addresses), f, indent=2)

print(f"\nDone! Saved {len(all_addresses)} unique addresses to {output_report}")
for street, addrs in sorted(grouped.items())[:40]: # Print first 40 groups
    print(f"Street: {street}")
    for a in sorted(addrs)[:10]:
        print(f"  - {a}")
