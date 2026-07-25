"""Trace CPS -> foster -> group home -> homeless -> disappeared pipeline"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"
HEADER = "=" * 60

# 1. Foster care / group home / residential care PPP nationally
print(HEADER)
print("FOSTER CARE / GROUP HOME / RESIDENTIAL YOUTH PPP NATIONWIDE")
print(HEADER)
q1 = f"""
SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, DateApproved, 
       LoanStatus, NAICSCode, NonProfit, JobsReported
FROM `{PRJ}.ppp_rico.ppp_150k_plus`
WHERE (UPPER(BorrowerName) LIKE '%FOSTER%' OR UPPER(BorrowerName) LIKE '%GROUP HOME%'
    OR UPPER(BorrowerName) LIKE '%RESIDENTIAL%CHILD%' OR UPPER(BorrowerName) LIKE '%YOUTH%HOME%'
    OR UPPER(BorrowerName) LIKE '%BOYS%HOME%' OR UPPER(BorrowerName) LIKE '%GIRLS%HOME%'
    OR UPPER(BorrowerName) LIKE '%CHILDREN%HOME%' OR UPPER(BorrowerName) LIKE '%BOYS%RANCH%'
    OR UPPER(BorrowerName) LIKE '%GIRLS%RANCH%' OR UPPER(BorrowerName) LIKE '%YOUTH%SHELTER%'
    OR UPPER(BorrowerName) LIKE '%TEEN%SHELTER%' OR UPPER(BorrowerName) LIKE '%RUNAWAY%'
    OR UPPER(BorrowerName) LIKE '%ORPHAN%' OR UPPER(NaicSCode) IN ('624110','624120','624190','623220','623990'))
ORDER BY CurrentApprovalAmount DESC LIMIT 30
"""
df1 = client.query(q1).to_dataframe()
print(f"Foster/residential youth PPP: {len(df1)}")
for _, r in df1.iterrows():
    print(f"  ${r['CurrentApprovalAmount']:>10,.0f}  {r['BorrowerCity']}, {r['BorrowerState']}  {str(r['BorrowerName'])[:60]}  NAICS:{r['NAICSCode']}  NP:{r['NonProfit']}")

# 2. CPS / Child Protective Services entities
print(f"\n{HEADER}")
print("CPS / CHILD PROTECTIVE / FOSTER AGENCY ENTITIES")
print(HEADER)
q2 = f"""
SELECT name, type, address, city, state, ein, source
FROM `{PRJ}.hb_church_osint.entities`
WHERE UPPER(name) LIKE '%CHILD%PROTECT%' OR UPPER(name) LIKE '%FOSTER%FAMILY%'
   OR UPPER(name) LIKE '%CASA%' OR UPPER(name) LIKE '%COURT%APPOINTED%'
   OR UPPER(name) LIKE '%ADOPTION%' OR UPPER(name) LIKE '%GUARDIAN%AD%LITEM%'
   OR UPPER(name) LIKE '%YOUTH%SERVICES%' OR UPPER(name) LIKE '%CHILD%ADVOCACY%'
   OR UPPER(name) LIKE '%FAMILY%SERVICES%CHILD%' OR UPPER(name) LIKE '%CHILD%WELFARE%'
ORDER BY state, city LIMIT 30
"""
rows2 = list(client.query(q2).result())
print(f"CPS/foster entities: {len(rows2)}")
for r in rows2:
    print(f"  {str(r['name'])[:60]} | {r['city']}, {r['state']} | EIN:{r.get('ein','?')}")

# 3. Total homeless count data from mat_looker_forensic_base
print(f"\n{HEADER}")
print("HOMELESS COUNTS + UNSHELTERED BY STATE")
print(HEADER)
q3 = f"""
SELECT state_anchor, total_homeless_count, total_unsheltered_count, total_coc_funding, leakage_delta
FROM `{PRJ}.national_audits.mat_looker_forensic_base`
ORDER BY total_homeless_count DESC LIMIT 15
"""
rows3 = list(client.query(q3).result())
for r in rows3:
    leak = r.get('leakage_delta', 'N/A')
    print(f"  {r['state_anchor']}: homeless={r.get('total_homeless_count',0):,}, unsheltered={r.get('total_unsheltered_count',0):,}, CoC_funding=${r.get('total_coc_funding',0):,.0f}, leakage=${leak}")

# 4. OC-specific child/youth facilities in PPP
print(f"\n{HEADER}")
print("OC-AREA CHILD/YOUTH/RESIDENTIAL FACILITIES IN PPP")
print(HEADER)
q4 = f"""
SELECT BorrowerName, BorrowerCity, CurrentApprovalAmount, DateApproved, NAICSCode
FROM `{PRJ}.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerState) = 'CA'
  AND UPPER(BorrowerCity) IN ('HUNTINGTON BEACH','SANTA ANA','COSTA MESA','NEWPORT BEACH','FOUNTAIN VALLEY','IRVINE','ANAHEIM','FULLERTON','ORANGE','GARDEN GROVE')
  AND (UPPER(NaicSCode) IN ('624110','624120','624190','623220','623990','624221','624229','624230')
    OR UPPER(BorrowerName) LIKE '%CHILD%' OR UPPER(BorrowerName) LIKE '%YOUTH%'
    OR UPPER(BorrowerName) LIKE '%FOSTER%' OR UPPER(BorrowerName) LIKE '%SHELTER%'
    OR UPPER(BorrowerName) LIKE '%FAMILY%SERVICE%')
ORDER BY CurrentApprovalAmount DESC LIMIT 25
"""
df4 = client.query(q4).to_dataframe()
print(f"OC youth/residential PPP: {len(df4)}")
for _, r in df4.iterrows():
    print(f"  ${r['CurrentApprovalAmount']:>10,.0f}  {r['BorrowerCity']}  {str(r['BorrowerName'])[:55]}  NAICS:{r['NAICSCode']}")

# 5. email search for CPS / foster / trafficking / group home
print(f"\n{HEADER}")
print("CPS / FOSTER / GROUP HOME IN EMAILS")
print(HEADER)
q5 = f"""
SELECT subject, sender, date_header, snippet
FROM `{PRJ}.national_audits.gmail_index`
WHERE LOWER(subject) LIKE '%foster%' OR LOWER(subject) LIKE '%child protective%'
   OR LOWER(subject) LIKE '%group home%' OR LOWER(subject) LIKE '%cps%investig%'
   OR LOWER(snippet) LIKE '%foster care%' OR LOWER(snippet) LIKE '%child protective services%'
   OR LOWER(snippet) LIKE '%group home%'
ORDER BY date_header DESC LIMIT 10
"""
rows5 = list(client.query(q5).result())
print(f"Foster/CPS emails: {len(rows5)}")
for r in rows5:
    print(f"  [{r['date_header']}] {str(r['subject'])[:80]}")

print(f"\n{HEADER}")
print("DONE")
