import os
import re
import json
import pypdf

pdf_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\opencode_work\Private_EDR_2025_Real"
output_report = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\edr_gps_multiline_mapped.json"

print("=== STARTING MULTILINE GPS EXTRACTION ===")

results = []

for f in sorted(os.listdir(pdf_dir)):
    if not f.lower().endswith('.pdf'):
        continue
    path = os.path.join(pdf_dir, f)
    try:
        reader = pypdf.PdfReader(path)
        
        # Scan first 10 pages
        full_text = ""
        for page in reader.pages[:10]:
            full_text += page.extract_text() or ""
            
        lines = [line.strip() for line in full_text.splitlines() if line.strip()]
        
        lat = ""
        lon = ""
        cover_address = ""
        
        # Extract cover address
        for line in lines[:30]:
            if re.match(r"^\d{3,5}\s+[A-Za-z0-9\s]+", line):
                if any(k in line.lower() for k in ("beach", "cameron", "slater", "warner")):
                    cover_address = line
                    break
        
        # Parse coordinates (handling newlines)
        for idx, line in enumerate(lines):
            # If line is Latitude: look at the next line
            if "latitude" in line.lower() and idx + 1 < len(lines):
                next_line = lines[idx+1]
                val = re.sub(r"[^\d\.\-]", "", next_line)
                if val:
                    lat = val
            if "longitude" in line.lower() and idx + 1 < len(lines):
                next_line = lines[idx+1]
                val = re.sub(r"[^\d\.\-]", "", next_line)
                if val:
                    lon = val
                    
        # Check standard format as backup
        if not lat:
            m = re.search(r"Latitude\s*\(North\):\s*([\d\.]+)", full_text, re.IGNORECASE)
            if m:
                lat = m.group(1)
        if not lon:
            m = re.search(r"Longitude\s*\(West\):\s*([\d\.]+)", full_text, re.IGNORECASE)
            if m:
                lon = m.group(1)
                
        if lat or lon or cover_address:
            # Reverse-geocode approximations
            real_loc = "Unknown / Map Coordinates"
            if lat and lon:
                try:
                    lat_f = float(lat)
                    if abs(lat_f - 33.7088) < 0.002:
                        real_loc = "17631 Cameron Lane (Homeless Shelter / Plume Center)"
                    elif abs(lat_f - 33.7081) < 0.002:
                        real_loc = "17540 Cameron Lane (Shea Homes Mini-Village)"
                    elif abs(lat_f - 33.6815) < 0.002 or abs(lat_f - 118.0090) < 0.002: # sometimes lon is swapped into lat field in EDR abstracts
                        real_loc = "20002 Beach Blvd (South Huntington Beach decoy area)"
                except:
                    pass
            
            results.append({
                "file": f,
                "cover_address": cover_address if cover_address else "NOT FOUND",
                "latitude": lat if lat else "N/A",
                "longitude": lon if lon else "N/A",
                "real_physical_location": real_loc
            })
    except Exception as e:
        pass

# Save to JSON
with open(output_report, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"Saved results to {output_report}")
for r in results:
    if r["latitude"] != "N/A":
        print(f"File: {r['file']:<35} | Cover: {r['cover_address']:<25} | GPS: {r['latitude']}, {r['longitude']} -> Real: {r['real_physical_location']}")
