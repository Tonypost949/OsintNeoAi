import os
import re
import json
import pypdf

pdf_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\opencode_work\Private_EDR_2025_Real"
output_report = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\edr_masked_address_log.json"

print("=== STARTING DETAILED COORDINATE AND COVER ADDRESS EXTRACTION ===")

results = []

for f in sorted(os.listdir(pdf_dir)):
    if not f.lower().endswith('.pdf'):
        continue
        
    path = os.path.join(pdf_dir, f)
    try:
        reader = pypdf.PdfReader(path)
        
        # Extract first 10 pages to search for coordinates and target address
        full_text = ""
        for page in reader.pages[:10]:
            full_text += page.extract_text() or ""
            
        # Look for Target Property address block
        addr_match = re.search(r"Target Property\s*[:\-\s]+([^\n\r]+)", full_text, re.IGNORECASE)
        # Fallback search for cover address (usually near Inquiry Number or top of pages)
        cover_addr_match = re.search(r"(?:17\d{3}\s+[A-Za-z0-9\s]+(?:BLVD|LN|AVE|RD|ST))", full_text, re.IGNORECASE)
        
        # Look for Latitude & Longitude
        lat_match = re.search(r"Latitude\s*\(North\):\s*([\d\.\s]+)", full_text, re.IGNORECASE)
        lon_match = re.search(r"Longitude\s*\(West\):\s*([\d\.\s]+)", full_text, re.IGNORECASE)
        
        # Clean extracted values
        address = addr_match.group(1).strip() if addr_match else ""
        if not address and cover_addr_match:
            address = cover_addr_match.group(0).strip()
            
        # Fallback to general lines
        if not address:
            for line in full_text.splitlines()[:15]:
                if any(x in line.lower() for x in ("beach", "cameron", "slater", "warner")):
                    address = line.strip()
                    break
                    
        latitude = lat_match.group(1).strip() if lat_match else ""
        longitude = lon_match.group(1).strip() if lon_match else ""
        
        # Clean latitude/longitude if they have trailing degrees
        latitude = re.sub(r"[^\d\.]", "", latitude)
        longitude = re.sub(r"[^\d\.]", "", longitude)
        
        if latitude or longitude or address:
            results.append({
                "file": f,
                "cover_address": address,
                "latitude": latitude,
                "longitude": longitude
            })
            
    except Exception as e:
        # Skip failed PDFs (like some password-protected or raster-only PDFs)
        pass

# Write directly to JSON to avoid terminal CP1252 console limitations
with open(output_report, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"\nCompleted! Processed {len(results)} files. Summary written to {output_report}")
for r in results:
    # Print only ASCII to be safe from cp1252 error
    clean_addr = r['cover_address'].encode('ascii', errors='ignore').decode()
    print(f"File: {r['file']} | Address: {clean_addr} | Lat: {r['latitude']} | Lon: {r['longitude']}")
