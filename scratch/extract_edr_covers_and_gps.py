import os
import re
import json
import pypdf

pdf_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\opencode_work\Private_EDR_2025_Real"
output_report = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\edr_gps_mapping_clean.json"

print("=== RUNNING DETAILED COVER ADDRESS AND GPS COORDINATE EXTRACTION ===")

results = []

for f in sorted(os.listdir(pdf_dir)):
    if not f.lower().endswith('.pdf'):
        continue
    path = os.path.join(pdf_dir, f)
    try:
        reader = pypdf.PdfReader(path)
        
        # Scan first 5 pages
        found_address = ""
        found_lat = ""
        found_lon = ""
        
        for i in range(min(5, len(reader.pages))):
            text = reader.pages[i].extract_text() or ""
            
            # Find addresses: e.g. "17642 BEACH BLVD" or "17540 CAMERON LN"
            addr_matches = re.findall(r"(\d{3,5}\s+[A-Za-z0-9\s\.\#\-]+(?:BEACH|CAMERON|SLATER|WARNER|BLVD|LN|AVE|RD|ST))", text, re.IGNORECASE)
            for am in addr_matches:
                am_clean = am.strip().upper()
                if "ARMSTRONG" not in am_clean and "SHELTON" not in am_clean: # Filter EDR corporate office address
                    found_address = am_clean
                    break
            
            # Look for Latitude & Longitude
            lat_m = re.search(r"Latitude\s*\(North\):\s*([\d\.\s]+)", text, re.IGNORECASE)
            lon_m = re.search(r"Longitude\s*\(West\):\s*([\d\.\s]+)", text, re.IGNORECASE)
            
            if lat_m:
                found_lat = re.sub(r"[^\d\.]", "", lat_m.group(1)).strip()
            if lon_m:
                found_lon = re.sub(r"[^\d\.]", "", lon_m.group(1)).strip()
                
            if found_address and found_lat and found_lon:
                break
                
        # If address not found in first 5 pages, search for "Target Property" label anywhere in first 5 pages
        if not found_address:
            for page in reader.pages[:5]:
                text = page.extract_text() or ""
                m = re.search(r"Target\s+Property\s*[:\-\s]+([^\n\r]+)", text, re.IGNORECASE)
                if m:
                    found_address = m.group(1).strip().upper()
                    break

        if found_address or found_lat or found_lon:
            # Map GPS coordinates to real addresses
            real_loc = "Unknown / Map Coordinates"
            if found_lat and found_lon:
                try:
                    lat_f = float(found_lat)
                    # Check proximity
                    if abs(lat_f - 33.7088) < 0.002:
                        real_loc = "17631 Cameron Lane (Homeless Shelter / Plume Center)"
                    elif abs(lat_f - 33.7081) < 0.002:
                        real_loc = "17540 Cameron Lane (Shea Homes Mini-Village)"
                    elif abs(lat_f - 33.6815) < 0.002:
                        real_loc = "20002 Beach Blvd (South Huntington Beach near Adams Ave)"
                except:
                    pass
            
            results.append({
                "file": f,
                "cover_address": found_address if found_address else "NOT FOUND",
                "latitude": found_lat if found_lat else "N/A",
                "longitude": found_lon if found_lon else "N/A",
                "real_physical_location": real_loc
            })
            
    except Exception as e:
        pass

# Save to JSON
with open(output_report, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved clean mapping report to {output_report}")
