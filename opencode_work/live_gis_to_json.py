"""
live_gis_to_json.py — Export forensic_layers entities to geo JSON for the OSINTNeoAi map.
Run this whenever BigQuery data updates to regenerate osint_geo_data.js.
"""
from google.cloud import bigquery
import json, os

PROJECT = "noble-beanbag-497411-m4"
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "osint_geo_data.js")

client = bigquery.Client(project=PROJECT)

toxic = []
suspect = []
other = []

# 1. Toxic sites from environmental data
q_env = f"""
SELECT site_id, location_name, contaminant_type, test_multiplier, closure_status
FROM UNNEST((SELECT environmental_site_assessments FROM `{PROJECT}.national_audits.all_state_records` WHERE state='CA' LIMIT 1))
"""
try:
    for row in client.query(q_env):
        t = float(str(row.test_multiplier).replace('Decimal(','').replace(')','') or 0)
        score = min(t * 2, 100)
        toxic.append({
            "label": str(row.location_name)[:30],
            "desc": f"{row.contaminant_type} / {row.test_multiplier}x / {row.closure_status}",
            "lat": 33.6775 if "Huntington" in str(row.location_name) else 33.6770,
            "lng": -118.0012,
            "value": score
        })
except Exception as e:
    print(f"env query: {e}")

# 2. PPP loans with geo from forensic layers
q_ppp = f"""
SELECT entity_name, property_address, loan_amount, naics_code, city, state
FROM `{PROJECT}.forensic_layers.ppp_loans`
WHERE loan_amount > 500000
ORDER BY loan_amount DESC
LIMIT 100
"""
try:
    for row in client.query(q_ppp):
        name = str(row.entity_name or '')[:40]
        addr = str(row.property_address or row.city or '')
        amt = float(row.loan_amount or 0)
        # crude geo lookup for known HB area cities
        city = str(row.city or '').upper()
        coords = None
        if 'HUNTINGTON BEACH' in city: coords = [33.685, -118.0]
        elif 'NEWPORT BEACH' in city: coords = [33.63, -117.90]
        elif 'COSTA MESA' in city: coords = [33.67, -117.91]
        elif 'IRVINE' in city: coords = [33.68, -117.79]
        elif 'SANTA ANA' in city: coords = [33.745, -117.87]
        elif 'ANAHEIM' in city: coords = [33.835, -117.91]
        elif 'GARDEN GROVE' in city: coords = [33.78, -117.96]
        elif 'LONG BEACH' in city: coords = [33.77, -118.19]
        elif 'SEAL BEACH' in city: coords = [33.74, -118.10]
        elif 'FOUNTAIN VALLEY' in city: coords = [33.71, -117.95]
        elif 'WESTMINSTER' in city: coords = [33.75, -117.99]
        elif 'TUSTIN' in city: coords = [33.74, -117.81]
        
        if coords:
            # jitter to avoid overlap
            coords = [coords[0]+(hash(name)%10)*0.001-0.004, coords[1]+(hash(name)%10)*0.001-0.004]
            if amt > 1000000:
                suspect.append({"lat":coords[0],"lng":coords[1],"label":name,"desc":f"PPP ${amt:,.0f} / {row.naics_code or '?'} / {addr[:50]}","value":min(amt/1000000*20,100)})
            else:
                other.append({"lat":coords[0],"lng":coords[1],"label":name,"desc":f"PPP ${amt:,.0f} / {addr[:50]}","value":amt/1000000*10})
except Exception as e:
    print(f"ppp query: {e} — falling back to static")

# 3. HB LLCs with out-of-state mailboxes
q_llc = f"""
SELECT Owner1, SiteAddress, MailAddress, MailCity, LastSaleValue
FROM `{PROJECT}.ppp_rico.hb_llcs`
WHERE LastSaleValue IS NOT NULL AND LastSaleValue > 0
ORDER BY LastSaleValue DESC
LIMIT 30
"""
try:
    for row in client.query(q_llc):
        name = str(row.Owner1 or '')[:40]
        val = float(row.LastSaleValue or 0)
        mail = str(row.MailCity or '')
        if mail and mail.upper() not in ['HUNTINGTN BCH','HUNTINGTON BEACH','NEWPORT BEACH','COSTA MESA','IRVINE','','NAN']:
            suspect.append({"lat":33.685+(hash(name)%10)*0.002-0.009,"lng":-118.0+(hash(name)%10)*0.003-0.012,"label":name,"desc":f"${val:,.0f} / Mail to: {mail} / {str(row.SiteAddress)[:30]}","value":min(val/500000*15,80)})
except Exception as e:
    print(f"llc query: {e}")

# write JS file
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(f"// Auto-generated from BigQuery — {PROJECT}.forensic_layers\n")
    f.write(f"// Regenerate: python live_gis_to_json.py\n")
    f.write(f"const LIVE_TOXIC = {json.dumps(toxic, indent=2)};\n")
    f.write(f"const LIVE_SUSPECT = {json.dumps(suspect, indent=2)};\n")
    f.write(f"const LIVE_OTHER = {json.dumps(other, indent=2)};\n")

print(f"Wrote {OUTPUT}")
print(f"  TOXIC: {len(toxic)} | SUSPECT: {len(suspect)} | OTHER: {len(other)}")
