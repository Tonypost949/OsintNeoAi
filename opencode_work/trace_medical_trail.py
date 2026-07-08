"""Trace medical fraud -> trafficking pipeline: SD, Black Hills, Native communities"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

HEADER = "=" * 60

# 1. SD entities in all datasets
print(HEADER)
print("SOUTH DAKOTA ENTITIES (hb_church_osint.entities)")
print(HEADER)
q1 = f"""
SELECT name, type, address, city, state, zip, ein, source
FROM `{PRJ}.hb_church_osint.entities`
WHERE UPPER(state) = 'SD'
ORDER BY type, name
"""
rows = list(client.query(q1).result())
print(f"Total SD entities: {len(rows)}")
for r in rows[:40]:
    print(f"  [{r['type']}] {str(r['name'])[:60]} | {r['city']}, SD | EIN:{r.get('ein','?')} | Src:{str(r.get('source',''))[:20]}")
if len(rows) > 40:
    print(f"  ... +{len(rows)-40} more")

# 2. SD PPP loans (medical/pharma focus)
print(f"\n{HEADER}")
print("SOUTH DAKOTA PPP LOANS (150k_plus, medical focus)")
print(HEADER)
q2 = f"""
SELECT BorrowerName, BorrowerCity, CurrentApprovalAmount, DateApproved, LoanStatus,
       BusinessType, NAICSCode, NonProfit, ServicingLenderName
FROM `{PRJ}.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerState) = 'SD'
  AND (UPPER(BorrowerName) LIKE '%MEDICAL%' OR UPPER(BorrowerName) LIKE '%HEALTH%'
    OR UPPER(BorrowerName) LIKE '%PHARM%' OR UPPER(BorrowerName) LIKE '%HOSPITAL%'
    OR UPPER(BorrowerName) LIKE '%CLINIC%' OR UPPER(BorrowerName) LIKE '%CARE%'
    OR UPPER(BorrowerName) LIKE '%HOSPICE%' OR UPPER(BorrowerName) LIKE '%WELLNESS%'
    OR UPPER(BorrowerName) LIKE '%BEHAVIOR%' OR UPPER(BorrowerName) LIKE '%TREATMENT%'
    OR UPPER(BorrowerName) LIKE '%COUNSEL%' OR UPPER(BorrowerName) LIKE '%THERAP%'
    OR UPPER(BorrowerName) LIKE '%RECOVERY%' OR UPPER(BorrowerName) LIKE '%REHAB%'
    OR UPPER(BorrowerName) LIKE '%SURGERY%' OR UPPER(BorrowerName) LIKE '%DENTAL%'
    OR UPPER(NaicSCode) LIKE '621%' OR UPPER(NaicSCode) LIKE '622%'
    OR UPPER(NaicSCode) LIKE '623%' OR UPPER(NaicSCode) LIKE '446%'
    OR UPPER(NaicSCode) LIKE '3254%')
ORDER BY CurrentApprovalAmount DESC LIMIT 30
"""
df2 = client.query(q2).to_dataframe()
print(f"SD medical PPP: {len(df2)} loans")
for _, r in df2.iterrows():
    print(f"  ${r['CurrentApprovalAmount']:>10,.0f}  {r['BorrowerCity']}, SD  {str(r['BorrowerName'])[:55]}  [{r['LoanStatus']}]  NAICS:{r['NAICSCode']}")

# 3. Native/tribal/IHS entities nationally in PPP
print(f"\n{HEADER}")
print("NATIVE / TRIBAL / IHS PPP LOANS NATIONWIDE")
print(HEADER)
q3 = f"""
SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, DateApproved, LoanStatus, NAICSCode
FROM `{PRJ}.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%TRIBAL%' OR UPPER(BorrowerName) LIKE '%NATIVE%'
   OR UPPER(BorrowerName) LIKE '%INDIAN HEALTH%' OR UPPER(BorrowerName) LIKE '%IHS%'
   OR UPPER(BorrowerName) LIKE '%RESERVATION%' OR UPPER(BorrowerName) LIKE '%SIOUX%'
   OR UPPER(BorrowerName) LIKE '%LAKOTA%' OR UPPER(BorrowerName) LIKE '%DAKOTA%'
   OR UPPER(BorrowerName) LIKE '%OJIBWE%' OR UPPER(BorrowerName) LIKE '%NAVAJO%'
   OR UPPER(BorrowerName) LIKE '%CHEROKEE%' OR UPPER(BorrowerName) LIKE '%CHOCTAW%'
ORDER BY CurrentApprovalAmount DESC LIMIT 25
"""
df3 = client.query(q3).to_dataframe()
print(f"Native/tribal PPP: {len(df3)} loans")
for _, r in df3.iterrows():
    print(f"  ${r['CurrentApprovalAmount']:>10,.0f}  {r['BorrowerCity']}, {r['BorrowerState']}  {str(r['BorrowerName'])[:55]}  NAICS:{r['NAICSCode']}")

# 4. Trafficking / CPS / McKinney-Vento keywords in gmail_index
print(f"\n{HEADER}")
print("TRAFFICKING / CPS / MCKINNEY-VENTO / MMIW IN EMAILS")
print(HEADER)
q4 = f"""
SELECT subject, sender, date_header, snippet
FROM `{PRJ}.national_audits.gmail_index`
WHERE LOWER(subject) LIKE '%traffick%' OR LOWER(subject) LIKE '%cps%child%'
   OR LOWER(subject) LIKE '%mckinney%' OR LOWER(subject) LIKE '%homeless%youth%'
   OR LOWER(subject) LIKE '%foster%' OR LOWER(subject) LIKE '%missing%indigenous%'
   OR LOWER(subject) LIKE '%mmiw%' OR LOWER(subject) LIKE '%native%women%'
   OR LOWER(snippet) LIKE '%trafficking%'
ORDER BY date_header DESC LIMIT 15
"""
rows4 = list(client.query(q4).result())
print(f"Trafficking emails: {len(rows4)}")
for r in rows4:
    print(f"  [{r['date_header']}] {str(r['subject'])[:80]}")
    print(f"    {str(r['snippet'])[:120]}")

# 5. SD properties in hb_church_osint
print(f"\n{HEADER}")
print("SOUTH DAKOTA PROPERTIES (hb_church_osint)")
print(HEADER)
q5 = f"""
SELECT owner_name, address, apn, city, last_sale_value, last_sale_date, mail_address, mail_city
FROM `{PRJ}.hb_church_osint.properties`
WHERE UPPER(city) LIKE '%SD%' OR UPPER(mail_city) LIKE '%SD%'
   OR UPPER(address) LIKE '%SD %' OR UPPER(address) LIKE '%SOUTH DAKOTA%'
LIMIT 20
"""
rows5 = list(client.query(q5).result())
print(f"SD properties: {len(rows5)}")
for r in rows5:
    print(f"  {str(r['owner_name'])[:40]} | {str(r['address'])[:40]} | ${r.get('last_sale_value',0)}")

print(f"\n{HEADER}")
print("DONE")
