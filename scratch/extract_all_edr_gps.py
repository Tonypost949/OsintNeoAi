import os
import re
import json
import pypdf

pdf_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\opencode_work\Private_EDR_2025_Real"
output_json = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\edr_all_gps_coordinates.json"

print("=== STARTING ROBUST EDR GPS EXTRACTION ===")

results = []

# Multiple regexes for latitude/longitude formats
lat_patterns = [
    re.compile(r"Latitude\s*\(North\):\s*([\d\.\s\u00b0\u02da'\"]+)", re.IGNORECASE),
    re.compile(r"Lat:\s*([\d\.\s\-]+)", re.IGNORECASE),
    re.compile(r"Latitude:\s*([\d\.\s\-]+)", re.IGNORECASE)
]

lon_patterns = [
    re.compile(r"Longitude\s*\(West\):\s*([\d\.\s\u00b0\u02da'\"]+)", re.IGNORECASE),
    re.compile(r"Lon:\s*([\d\.\s\-]+)", re.IGNORECASE),
    re.compile(r"Longitude:\s*([\d\.\s\-]+)", re.IGNORECASE)
]

# Helper to clean coordinate strings
def clean_coord(s):
    if not s:
        return ""
    # remove degree signs, quotes, spaces, etc.
    s = re.sub(r"[^\d\.\-]", "", s)
    return s.strip()

for f in sorted(os.listdir(pdf_dir)):
    if not f.lower().endswith('.pdf'):
        continue
    path = os.path.join(pdf_dir, f)
    try:
        reader = pypdf.PdfReader(path)
        
        # Scan more pages (up to 25 pages) to ensure we don't miss coordinate tables
        full_text = ""
        for page in reader.pages[:25]:
            full_text += page.extract_text() or ""
            
        cover_address = ""
        # Search first 5 pages for address patterns
        for line in full_text.splitlines()[:30]:
            line_clean = line.strip()
            # Look for lines starting with numbers and containing street terms
            if re.match(r"^\d{3,5}\s+[A-Za-z0-9\s]+", line_clean):
                if any(k in line_clean.lower() for k in ("beach", "cameron", "slater", "ln", "blvd", "ave", "st")):
                    cover_address = line_clean
                    break
        
        # Fallback target property search
        if not cover_address:
            addr_match = re.search(r"Target Property\s*[:\-\s]+([^\n\r]+)", full_text, re.IGNORECASE)
            if addr_match:
                cover_address = addr_match.group(1).strip()
                
        lat = ""
        lon = ""
        
        for pat in lat_patterns:
            m = pat.search(full_text)
            if m:
                lat = clean_coord(m.group(1))
                break
                
        for pat in lon_patterns:
            m = pat.search(full_text)
            if m:
                lon = clean_coord(m.group(1))
                break
                
        if lat or lon or cover_address:
            results.append({
                "file": f,
                "cover_address": cover_address,
                "latitude": lat,
                "longitude": lon
            })
    except Exception as e:
        pass

# Reverse geocoding approximations for the coordinates found:
# 33.708848, 117.986835 -> 17631 Cameron Lane (shelter)
# 33.708173, 117.986794 -> 17540 Cameron Lane (Shea Homes)
# 33.681532, 118.009042 -> 20002 Beach Blvd (south near Huntington State Beach / Adams Ave area)

for r in results:
    lat_val = r["latitude"]
    lon_val = r["longitude"]
    
    # Estimate real location
    if lat_val and lon_val:
        try:
            lf = float(lat_val)
            lg = float(lon_val)
            if lg > 0:
                lg = -lg
            
            if abs(lf - 33.7088) < 0.002:
                r["real_physical_location"] = "17631 Cameron Lane (Homeless Shelter lot)"
            elif abs(lf - 33.7081) < 0.002:
                r["real_physical_location"] = "17540 Cameron Lane (Shea Homes Mini-Village)"
            elif abs(lf - 33.6815) < 0.002:
                r["real_physical_location"] = "20002 Beach Blvd (South Huntington Beach near Adams Ave)"
            else:
                r["real_physical_location"] = f"Lat {lf:.5f}, Lon {lg:.5f}"
        except:
            r["real_physical_location"] = "Unknown / Map Coordinates"
    else:
        r["real_physical_location"] = "Not listed in PDF text"

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"Extraction completed. Saved {len(results)} records to {output_json}.")
