from google.cloud import bigquery
import json

client = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== THREAD 1: 7561 CENTER AVE — FULL SCAN ===\n")

# HB LLCs at/around 7561 Center Ave
table_ref = 'noble-beanbag-497411-m4.ppp_rico.hb_llcs'

q1 = f"""
SELECT Owner1, SiteAddress, APN, MailAddress, MailCity, LastSaleDate, LastSaleValue, LastSeller
FROM `{table_ref}`
WHERE UPPER(SiteAddress) LIKE '%CENTER AVE%'
   OR UPPER(MailAddress) LIKE '%CENTER AVE%'
   OR UPPER(SiteAddress) LIKE '%7561%'
   OR UPPER(MailAddress) LIKE '%7561%'
ORDER BY SiteAddress
"""
rows = list(client.query(q1).result())
print(f"Entities at/around Center Ave: {len(rows)}")
for r in rows:
    print(f"  {r.Owner1} | Site: {r.SiteAddress} | APN: {r.APN} | Mail: {r.MailAddress}, {r.MailCity} | Sale: {r.LastSaleDate} | ${r.LastSaleValue:,.0f}" if r.LastSaleValue else f"  {r.Owner1} | Site: {r.SiteAddress} | APN: {r.APN} | Mail: {r.MailAddress}, {r.MailCity}")

# Check PPP for Tam Nguyen
print("\n\n=== THREAD 2: TAM NGUYEN — PPP SWEEP ===\n")

for table_name in ['ppp_150k_plus', 'ppp_up_to_150k']:
    ppp_table = f'noble-beanbag-497411-m4.ppp_rico.{table_name}'
    q = f"""
    SELECT BorrowerName, BorrowerCity, BorrowerState, BorrowerAddress,
           CurrentApprovalAmount, DateApproved, LoanStatus, ForgivenessAmount,
           JobsReported, NAICSCode, BusinessType, OriginatingLender
    FROM `{ppp_table}`
    WHERE UPPER(BorrowerName) LIKE '%NGUYEN%TAM%'
       OR UPPER(BorrowerName) LIKE '%TAM%NGUYEN%'
    ORDER BY CurrentApprovalAmount DESC
    """
    rows = list(client.query(q).result())
    if rows:
        print(f"[{table_name}] {len(rows)} Tam Nguyen hits:")
        for r in rows[:10]:
            print(f"  ${r.CurrentApprovalAmount:,.0f} | {r.BorrowerName} | {r.BorrowerCity}, {r.BorrowerState} | {r.LoanStatus} | Lender: {r.OriginatingLender}")

# Check PPP for Peter Pham
print("\n\n=== THREAD 3: PETER PHAM — PPP + PROPERTY SWEEP ===\n")

for table_name in ['ppp_150k_plus', 'ppp_up_to_150k']:
    ppp_table = f'noble-beanbag-497411-m4.ppp_rico.{table_name}'
    q = f"""
    SELECT BorrowerName, BorrowerCity, BorrowerState, BorrowerAddress,
           CurrentApprovalAmount, DateApproved, LoanStatus, ForgivenessAmount,
           JobsReported, NAICSCode, BusinessType, OriginatingLender
    FROM `{ppp_table}`
    WHERE UPPER(BorrowerName) LIKE '%PETER%PHAM%'
       OR UPPER(BorrowerName) LIKE '%PHAM%'
    ORDER BY CurrentApprovalAmount DESC
    LIMIT 20
    """
    rows = list(client.query(q).result())
    if rows:
        print(f"[{table_name}] {len(rows)} Pham hits:")
        for r in rows[:15]:
            print(f"  ${r.CurrentApprovalAmount:,.0f} | {r.BorrowerName} | {r.BorrowerCity}, {r.BorrowerState} | {r.LoanStatus} | Lender: {r.OriginatingLender}")

# Check HB LLCs for Pham and Nguyen
print("\n\n=== THREAD 4: HB PROPERTY — NGUYEN / PHAM OWNERSHIP ===\n")
for name in ['NGUYEN', 'PHAM']:
    q = f"""
    SELECT Owner1, Owner2, SiteAddress, APN, MailAddress, MailCity, LastSaleDate, LastSaleValue
    FROM `{table_ref}`
    WHERE UPPER(Owner1) LIKE '%{name}%' OR UPPER(Owner2) LIKE '%{name}%'
    ORDER BY LastSaleDate DESC
    LIMIT 20
    """
    rows = list(client.query(q).result())
    if rows:
        print(f"  {name}: {len(rows)} property matches")
        for r in rows[:10]:
            o2 = f" / {r.Owner2}" if r.Owner2 and r.Owner2.strip() else ""
            print(f"    {r.Owner1}{o2} | {r.SiteAddress} | APN {r.APN} | Mail: {r.MailAddress}, {r.MailCity} | Sale: {r.LastSaleDate} ${r.LastSaleValue:,.0f}" if r.LastSaleValue else f"    {r.Owner1}{o2} | {r.SiteAddress} | APN {r.APN} | Mail: {r.MailAddress}, {r.MailCity}")

# Check CP PREMIER CAPITAL specifically
print("\n\n=== THREAD 5: CP PREMIER CAPITAL SWEEP ===\n")
q = f"""
SELECT *
FROM `{table_ref}`
WHERE UPPER(Owner1) LIKE '%CP PREMIER%'
   OR UPPER(Owner2) LIKE '%CP PREMIER%'
   OR UPPER(MailAddress) LIKE '%CERRITOS%'
"""
rows = list(client.query(q).result())
if rows:
    print(f"CP PREMIER matches: {len(rows)}")
    for r in rows:
        print(f"  {r.Owner1} {'/ ' + r.Owner2 if r.Owner2 else ''} | Site: {r.SiteAddress} | APN: {r.APN} | Mail: {r.MailAddress}")
else:
    print("No CP PREMIER matches in hb_llcs")

# Also search national_audits for these names
print("\n\n=== THREAD 6: NATIONAL AUDITS — NGUYEN / PHAM / 7561 CENTER ===\n")
for table_name in ['all_state_records', 'all_performance_reports', 'mat_looker_forensic_base']:
    table_ref = f'noble-beanbag-497411-m4.national_audits.{table_name}'
    try:
        schema = client.get_table(table_ref).schema
        str_cols = [c.name for c in schema if c.field_type == 'STRING']
        for kw in ['TAM NGUYEN', 'PETER PHAM', '7561 CENTER', 'GARDEN GROVE', 'CP PREMIER']:
            conds = ' OR '.join([f"UPPER(CAST(`{c}` AS STRING)) LIKE '%{kw}%'" for c in str_cols[:6]])
            try:
                q = f"SELECT * FROM `{table_ref}` WHERE {conds} LIMIT 3"
                rows = list(client.query(q).result())
                if rows:
                    print(f"[{table_name}] '{kw}': {len(rows)} hits")
                    for r in rows[:2]:
                        d = {k: str(v)[:100] for k, v in dict(r).items() if v}
                        print(f"  {json.dumps(d)}")
            except:
                pass
    except:
        pass

print("\nDone.")
