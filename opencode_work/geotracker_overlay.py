from google.cloud import bigquery
import json

client = bigquery.Client(project='noble-beanbag-497411-m4')

targets = ['3311 BOUNTY CIR', '21951 BROOKHURST ST', '3311 BOUNTY CIRCLE', '21951 BROOKHURST STREET']

print("=== PRIORITY 2: GEOTRACKER / UST OVERLAY ===\n")

# Check all datasets for UST/GeoTracker data
for dataset_id in ['ppp_rico', 'hb_church_osint', 'national_audits', 'ai_sandbox', 'nppes_export']:
    try:
        tables = list(client.list_tables(dataset_id))
    except:
        continue
    for t in tables:
        if not any(kw in t.table_id.lower() for kw in ['ust', 'geo', 'tank', 'environ', 'well', 'contamin', 'cleanup', 'leaking']):
            continue
        table_ref = f'noble-beanbag-497411-m4.{dataset_id}.{t.table_id}'
        schema = client.get_table(table_ref).schema
        str_cols = [c.name for c in schema if c.field_type == 'STRING']
        
        for addr in targets:
            conditions = ' OR '.join([f"UPPER(CAST(`{c}` AS STRING)) LIKE '%{addr}%'" for c in str_cols[:8]])
            try:
                q = f"SELECT * FROM `{table_ref}` WHERE {conditions} LIMIT 5"
                rows = list(client.query(q).result())
                if rows:
                    print(f"[{dataset_id}.{t.table_id}] '{addr}': {len(rows)} match(es)")
                    for row in rows[:3]:
                        d = {k: str(v)[:120] for k, v in dict(row).items() if v is not None}
                        print(f"  {json.dumps(d)}")
            except Exception as e:
                pass

# Also check hb_llcs for these addresses specifically
print("\n=== HB LLCS — 3311 Bounty & 21951 Brookhurst ===")
table_ref = 'noble-beanbag-497411-m4.ppp_rico.hb_llcs'
for addr in ['3311 BOUNTY', '21951 BROOKHURST']:
    q = f"""
    SELECT Owner1, MailAddress, MailCity, SiteAddress, APN, LastSaleDate, LastSaleValue
    FROM `{table_ref}`
    WHERE UPPER(SiteAddress) LIKE '%{addr}%'
    """
    rows = list(client.query(q).result())
    if rows:
        print(f"  SiteAddress '{addr}': {len(rows)} match(es)")
        for row in rows:
            print(f"    {row.Owner1} | Mail: {row.MailAddress}, {row.MailCity} | APN: {row.APN} | Sale: {row.LastSaleDate} ${row.LastSaleValue:,.0f}" if row.LastSaleValue else f"    {row.Owner1} | Mail: {row.MailAddress}, {row.MailCity} | APN: {row.APN}")
    else:
        print(f"  SiteAddress '{addr}': 0 matches")

# Also check the out_of_state_llc_ppp_network.csv locally for these
print("\n=== LOCAL CSV CHECK — out_of_state_llc_ppp_network.csv ===")
import csv
csv_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\out_of_state_llc_ppp_network.csv"
try:
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for addr in ['3311 BOUNTY', '21951 BROOKHURST']:
            matches = []
            f.seek(0)
            reader = csv.DictReader(f)
            for row in reader:
                prop_addr = str(row.get('property_address', '')).upper()
                if addr in prop_addr:
                    matches.append(row)
            if matches:
                print(f"  '{addr}': {len(matches)} match(es)")
                for m in matches[:3]:
                    print(f"    {m.get('owner_name')} | Mail: {m.get('property_mail_city')} | PPP: ${m.get('ppp_amount')} | {m.get('ppp_borrower_name')}")
            else:
                print(f"  '{addr}': 0 matches")
except Exception as e:
    print(f"  Error reading CSV: {e}")

print("\nDone.")
