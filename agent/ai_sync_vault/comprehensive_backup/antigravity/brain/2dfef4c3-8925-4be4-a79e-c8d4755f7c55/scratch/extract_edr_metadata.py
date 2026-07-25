import os
import re
import json
from google.cloud import bigquery
import pypdf

# We can parse the PDFs locally using pypdf
pdf_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\opencode_work\Private_EDR_2025_Real"

print("=== PARSING EDR FILES FOR GPS-ADDRESS MISMATCHES ===")
mismatches = []

if not os.path.exists(pdf_dir):
    print("Private EDR folder not found!")
    exit(1)

# Compile Regex
gps_lat_re = re.compile(r"Latitude\s*\(North\):\s*([\d\.]+)", re.IGNORECASE)
gps_lon_re = re.compile(r"Longitude\s*\(West\):\s*([\d\.]+)", re.IGNORECASE)
addr_re = re.compile(r"Target\s+Property\s*[:\-\s]+([^\n\r]+)", re.IGNORECASE)

# Target coordinates for Cameron Lane Plume center (approx. 33.7088 N, 117.9868 W)
TARGET_LAT = 33.7088
TARGET_LON = 117.9868
TOLERANCE = 0.005 # ~500 meters

pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
print(f"Scanning {len(pdf_files)} PDF reports...")

for f in pdf_files:
    pdf_path = os.path.join(pdf_dir, f)
    try:
        reader = pypdf.PdfReader(pdf_path)
        # Scan first 5 pages for address and coordinates
        text = ""
        for i in range(min(5, len(reader.pages))):
            text += reader.pages[i].extract_text() or ""
            
        lat_match = gps_lat_re.search(text)
        lon_match = gps_lon_re.search(text)
        addr_match = addr_re.search(text)
        
        if lat_match and lon_match:
            lat = float(lat_match.group(1))
            lon = float(lon_match.group(1))
            # Some EDR logs represent longitude as positive but it's West (negative)
            if lon > 0:
                lon = -lon
                
            addr = addr_match.group(1).strip() if addr_match else "Unknown"
            
            # Check if close to Cameron Lane plume center
            lat_diff = abs(lat - TARGET_LAT)
            lon_diff = abs(lon - TARGET_LON)
            
            is_cameron_gps = lat_diff < TOLERANCE and lon_diff < TOLERANCE
            is_masked_address = "CAMERON" not in addr.upper() and is_cameron_gps
            
            if is_cameron_gps:
                mismatches.append({
                    "filename": f,
                    "address": addr,
                    "latitude": lat,
                    "longitude": lon,
                    "is_masked": is_masked_address
                })
    except Exception as e:
        # Skip if encrypted/uncorrupted
        pass

print(f"\nDone. Found {len(mismatches)} files with target GPS coordinates.")
for m in mismatches:
    status = "⚠️ [MASKED ADDRESS]" if m["is_masked"] else "✅ [CORRECT ADDRESS]"
    print(f"{status} File: {m['filename']}")
    print(f"   Address on Cover: {m['address']}")
    print(f"   GPS Coordinates : {m['latitude']} N, {m['longitude']} W")
    
# Save to JSON
with open(os.path.join(pdf_dir, "gps_mismatches_summary.json"), 'w') as out_f:
    json.dump(mismatches, out_f, indent=2)
