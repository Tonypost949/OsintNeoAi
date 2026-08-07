"""
live_gis_to_json.py — Export forensic_layers entities to geo JSON for the OSINTNeoAi map.
Run this whenever BigQuery data updates to regenerate osint_geo_data.js.
"""
from google.cloud import bigquery
import json, os

PROJECT = "project-743aab84-f9a5-4ec7-954"
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "osint_geo_data.js")

client = bigquery.Client(project=PROJECT)

toxic = []
suspect = []
other = []

# 1. Toxic sites from environmental data (GeoTracker UST)
q_env = f"""
SELECT BUSINESS_NAME, ADDRESS, LATITUDE, LONGITUDE, CALENVIROSCREEN4PERCENTILE
FROM `{PROJECT}.forensic_layers.geotracker_ust`
WHERE CITY = 'HUNTINGTON BEACH' OR COUNTY = 'Orange'
LIMIT 100
"""
try:
    for row in client.query(q_env):
        score_str = str(row.CALENVIROSCREEN4PERCENTILE or '0').replace('%', '').strip()
        if '-' in score_str:
            parts = score_str.split('-')
            try:
                score = (float(parts[0]) + float(parts[1])) / 2.0
            except:
                score = 0.0
        else:
            try:
                score = float(score_str)
            except:
                score = 0.0
        toxic.append({
            "label": str(row.BUSINESS_NAME)[:30],
            "desc": f"UST / {row.ADDRESS} / CalEnviroScreen: {score}%",
            "lat": float(row.LATITUDE or 33.68),
            "lng": float(row.LONGITUDE or -118.0),
            "value": score
        })
except Exception as e:
    print(f"env query: {e}")

# 2. PPP loans with geo from forensic layers
q_ppp = f"""
SELECT entity_name, hb_property, ppp_loan_1_amount, naics, naics_description, mail_address
FROM `{PROJECT}.forensic_layers.ppp_loans`
WHERE ppp_loan_1_amount > 500000
ORDER BY ppp_loan_1_amount DESC
LIMIT 100
"""
try:
    for row in client.query(q_ppp):
        name = str(row.entity_name or '')[:40]
        addr = str(row.hb_property or row.mail_address or '')
        amt = float(row.ppp_loan_1_amount or 0)
        # crude geo lookup for known HB area cities
        city = "HUNTINGTON BEACH" if "HUNTINGTON" in addr.upper() else "WESTMINSTER"
        coords = None
        if 'HUNTINGTON' in addr.upper(): coords = [33.685, -118.0]
        elif 'WESTMINSTER' in addr.upper(): coords = [33.75, -117.99]
        else: coords = [33.68, -117.99]
        
        if coords:
            # jitter to avoid overlap
            coords = [coords[0]+(hash(name)%10)*0.001-0.004, coords[1]+(hash(name)%10)*0.001-0.004]
            if amt > 1000000:
                suspect.append({"lat":coords[0],"lng":coords[1],"label":name,"desc":f"PPP ${amt:,.0f} / {row.naics_description or '?'} / {addr[:50]}","value":min(amt/1000000*20,100)})
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
