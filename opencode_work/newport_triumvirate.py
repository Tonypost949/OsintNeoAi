from google.cloud import bigquery
import json

client = bigquery.Client(project='noble-beanbag-497411-m4')
table_ref = 'noble-beanbag-497411-m4.ppp_rico.hb_llcs'

print("=== NEWPORT CENTER DR AUDIT ===\n")

# Dedupe check
q = f"""
SELECT Owner1 as llc_name, COUNT(*) as record_count
FROM `{table_ref}`
WHERE UPPER(MailAddress) LIKE '%220 NEWPORT CENTER DR%'
GROUP BY Owner1
ORDER BY record_count DESC
"""
rows = list(client.query(q).result())
print(f"Unique LLCs: {len(rows)}")
print(f"Total records: {sum(r.record_count for r in rows)}")
print()
for r in rows:
    print(f"  {r.llc_name}: {r.record_count} records")

# Check if the sites are all the same building (condo artifact) or varied
print("\n=== SITE ADDRESS ANALYSIS ===")
q2 = f"""
SELECT Owner1, SiteAddress, APN, LastSaleDate, LastSaleValue
FROM `{table_ref}`
WHERE UPPER(MailAddress) LIKE '%220 NEWPORT CENTER DR%'
ORDER BY Owner1, SiteAddress
"""
rows2 = list(client.query(q2).result())
sites = set()
for r in rows2:
    sites.add(r.SiteAddress)
print(f"Unique site addresses: {len(sites)}")
# Show first 15 records
for r in rows2[:15]:
    print(f"  {r.Owner1} | {r.SiteAddress} | APN {r.APN}")

print("\n\n=== TRIUMVIRATE PPP DEEP DIVE ===\n")

for table_name in ['ppp_150k_plus', 'ppp_up_to_150k']:
    ppp_table = f'noble-beanbag-497411-m4.ppp_rico.{table_name}'
    q3 = f"""
    SELECT *
    FROM `{ppp_table}`
    WHERE UPPER(BorrowerName) LIKE '%TRIUMVIRATE%'
    ORDER BY DateApproved
    """
    rows3 = list(client.query(q3).result())
    if rows3:
        print(f"[{table_name}] {len(rows3)} loans:")
        for r in rows3:
            d = dict(r)
            # Extract key fields
            key_fields = {
                'DateApproved': d.get('DateApproved'),
                'BorrowerName': d.get('BorrowerName'),
                'BorrowerCity': d.get('BorrowerCity'),
                'BorrowerState': d.get('BorrowerState'),
                'CurrentApprovalAmount': d.get('CurrentApprovalAmount'),
                'LoanStatus': d.get('LoanStatus'),
                'ForgivenessAmount': d.get('ForgivenessAmount'),
                'JobsReported': d.get('JobsReported'),
                'NAICSCode': d.get('NAICSCode'),
                'BusinessType': d.get('BusinessType'),
                'OriginatingLender': d.get('OriginatingLender'),
                'OriginatingLenderCity': d.get('OriginatingLenderCity'),
                'OriginatingLenderState': d.get('OriginatingLenderState'),
                'ProjectCity': d.get('ProjectCity'),
                'ProjectState': d.get('ProjectState'),
                'ProcessingMethod': d.get('ProcessingMethod'),
                'Term': d.get('Term'),
                'Gender': d.get('Gender'),
                'Race': d.get('Race'),
            }
            print(f"\n  {json.dumps(key_fields, indent=4)}")
    else:
        print(f"[{table_name}] No Triumvirate loans")

# Also check RICO matrix for Triumvirate
print("\n\n=== RICO MATRIX DETAIL FOR TRIUMVIRATE ===\n")
q4 = f"""
SELECT *
FROM `noble-beanbag-497411-m4.ppp_rico.rico_evidence_matrix`
WHERE UPPER(llc_name) LIKE '%TRIUMVIRATE%'
"""
rows4 = list(client.query(q4).result())
for r in rows4:
    print(json.dumps(dict(r), indent=2))

print("\nDone.")
