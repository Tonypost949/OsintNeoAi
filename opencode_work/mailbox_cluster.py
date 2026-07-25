from google.cloud import bigquery
import json

client = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== PRIORITY 1: MAILBOX CLUSTER — 1077 PACIFIC COAST HWY ===\n")

table_ref = 'noble-beanbag-497411-m4.ppp_rico.hb_llcs'

# Exact search for 1077 PCH
q1 = f"""
SELECT Owner1, Owner2, MailAddress, MailCity, SiteAddress, APN, LastSaleDate, LastSaleValue
FROM `{table_ref}`
WHERE UPPER(MailAddress) LIKE '%1077%' AND (UPPER(MailAddress) LIKE '%PACIFIC%' OR UPPER(MailAddress) LIKE '%PCH%')
"""
rows = list(client.query(q1).result())
print(f"Exact 1077 PCH matches: {len(rows)}")
for row in rows:
    print(f"  {row.Owner1} | {row.MailAddress}, {row.MailCity} | Site: {row.SiteAddress} | APN: {row.APN} | Sold: {row.LastSaleDate} ${row.LastSaleValue:,.0f}" if row.LastSaleValue else f"  {row.Owner1} | {row.MailAddress}, {row.MailCity}")

if not rows:
    # Broader search: any entity with "1077" AND "PACIFIC" in MailAddress
    print("\nNo exact matches. Trying broader PCH search...")
    q1b = f"""
    SELECT Owner1, MailAddress, MailCity, SiteAddress, APN, LastSaleDate, LastSaleValue
    FROM `{table_ref}`
    WHERE UPPER(MailAddress) LIKE '%1077%PACIFIC%'
       OR UPPER(MailAddress) LIKE '%1077%PCH%'
       OR UPPER(MailAddress) LIKE '%1077 P C H%'
    """
    rows2 = list(client.query(q1b).result())
    print(f"Broader 1077 PCH: {len(rows2)}")
    for row in rows2:
        print(f"  {row.Owner1} | {row.MailAddress}, {row.MailCity}")

# PCH cluster analysis
print("\n\n=== ALL PCH ADDRESS CLUSTERS (Top 30) ===")
q2 = f"""
SELECT MailAddress, COUNT(*) as entity_count
FROM `{table_ref}`
WHERE UPPER(MailAddress) LIKE '%PACIFIC%COAST%'
   OR UPPER(MailAddress) LIKE '% PCH %'
   OR UPPER(MailAddress) LIKE '%PCH %'
   OR UPPER(MailAddress) LIKE '% PCH'
GROUP BY MailAddress
HAVING COUNT(*) >= 2
ORDER BY entity_count DESC
LIMIT 30
"""
rows2 = list(client.query(q2).result())
print(f"PCH clusters with 2+ entities: {len(rows2)}")
for row in rows2:
    marker = "🔴" if row.entity_count >= 6 else "⚠️" if row.entity_count >= 3 else "•"
    print(f"  {marker} {row.MailAddress}: {row.entity_count} entities")

# Top mailbox clusters overall (not just PCH)
print("\n\n=== TOP MAILBOX CLUSTERS OVERALL (ALL HB) ===")
q3 = f"""
SELECT MailAddress, COUNT(*) as entity_count, 
       COUNT(DISTINCT MailCity) as cities,
       COUNT(DISTINCT Owner1) as unique_owners
FROM `{table_ref}`
WHERE MailAddress IS NOT NULL AND MailAddress != ''
GROUP BY MailAddress
HAVING COUNT(*) >= 5
ORDER BY entity_count DESC
LIMIT 20
"""
rows3 = list(client.query(q3).result())
print(f"All mailbox clusters with 5+ entities: {len(rows3)}")
for row in rows3:
    print(f"  {row.MailAddress}: {row.entity_count} entities, {row.unique_owners} owners, {row.cities} cities")

print("\nDone.")
