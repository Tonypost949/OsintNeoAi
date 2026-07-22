import json
import os

json_path = r"C:\Users\HP\OneDrive\Documents\OsintNeoAi\edr_gps_mapping_clean.json"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

unique = {}
for d in data:
    addr = d.get('cover_address')
    if addr and addr != 'NOT FOUND':
        # Clean up double address strings
        lines = [x.strip() for x in addr.split('\n') if x.strip()]
        if lines:
            addr = lines[0]
        unique[addr] = (d.get('latitude'), d.get('longitude'), d.get('real_physical_location'))

print("=== DECOY/COVER ADDRESSES TO REAL TARGET MAPPING ===")
for k, v in sorted(unique.items()):
    print(f"Cover Address   : {k}")
    print(f"GPS Coordinates : Lat {v[0]}, Lon -{v[1]}" if v[0] != 'N/A' else "GPS Coordinates : N/A")
    print(f"Real Location   : {v[2]}")
    print("-" * 50)
