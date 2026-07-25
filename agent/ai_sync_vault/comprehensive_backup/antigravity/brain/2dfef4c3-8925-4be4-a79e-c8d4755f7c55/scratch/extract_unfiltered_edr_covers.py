import os
import re
import json
import pypdf

pdf_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\opencode_work\Private_EDR_2025_Real"

print("=== EXTRACTING ALL UNIQUE ADDRESSES FROM EDR FILES ===")

all_addresses = set()

# Regex to capture street addresses like: 123 Main St, 17642 Beach Blvd, etc.
addr_pattern = re.compile(
    r"(\d{3,6}\s+[A-Za-z0-9\s\.\#\-]{2,30}\s+(?:BLVD|LN|LN\.|AVE|RD|ST|DR|WAY|COURT|CT|PLAZA|PL|TERRACE|CIRCLE|HUNTINGTON|GARDEN))",
    re.IGNORECASE
)

for f in sorted(os.listdir(pdf_dir)):
    if not f.lower().endswith('.pdf'):
        continue
    path = os.path.join(pdf_dir, f)
    try:
        reader = pypdf.PdfReader(path)
        # Scan first 5 pages for each document
        for page in reader.pages[:5]:
            text = page.extract_text() or ""
            
            # Find all potential address lines
            matches = addr_pattern.findall(text)
            for m in matches:
                addr_clean = m.strip().upper()
                # Exclude EDR corporate address and zip codes
                if not any(exclude in addr_clean for exclude in ("ARMSTRONG", "SHELTON", "CT 06484", "800.352.0050", "INQUIRY", "Toll Free")):
                    # Normalize whitespace
                    addr_clean = " ".join(addr_clean.split())
                    all_addresses.add(addr_clean)
    except Exception as e:
        pass

print(f"\nDone! Found {len(all_addresses)} unique address strings across files.")
for a in sorted(all_addresses):
    print(f" - {a}")
