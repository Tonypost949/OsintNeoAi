"""Shea Homes connections across all datasets"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

# 1. Shea in PPP
print("=" * 60)
print("SHEA IN PPP")
print("=" * 60)
q1 = f"""
SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, 
       ForgivenessAmount, DateApproved, LoanStatus, NAICSCode, JobsReported,
       ServicingLenderName
FROM `{PRJ}.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%SHEA%'
ORDER BY CurrentApprovalAmount DESC LIMIT 20
"""
for r in client.query(q1).result():
    print(f"  ${r['CurrentApprovalAmount']:>10,.0f}  {r['BorrowerCity']}, {r['BorrowerState']}  {str(r['BorrowerName'])[:55]}  NAICS:{r['NAICSCode']}  [{r['LoanStatus']}]")

# 2. Shea in hb_llcs (properties)
print(f"\n{'='*60}")
print("SHEA IN HB LLCS")
print("=" * 60)
q2 = f"""
SELECT Owner1, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleDate, LastSaleValue
FROM `{PRJ}.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%SHEA%' OR UPPER(Owner2) LIKE '%SHEA%'
   OR UPPER(SiteAddress) LIKE '%SHEA%' OR UPPER(MailAddress) LIKE '%SHEA%'
   OR UPPER(LastSeller) LIKE '%SHEA%'
ORDER BY LastSaleDate DESC
"""
for r in client.query(q2).result():
    print(f"  {str(r['Owner1'])[:35]} | {str(r['SiteAddress'])[:35]} | ${r.get('LastSaleValue',0)} | {r.get('LastSaleDate','')} | Seller:{str(r.get('LastSeller',''))[:30]}")

# 3. Shea in hb_church_osint entities
print(f"\n{'='*60}")
print("SHEA IN HB ENTITIES")
print("=" * 60)
q3 = f"""
SELECT name, type, address, city, state, ein, source
FROM `{PRJ}.hb_church_osint.entities`
WHERE UPPER(name) LIKE '%SHEA%' OR UPPER(address) LIKE '%SHEA%'
LIMIT 20
"""
for r in client.query(q3).result():
    print(f"  [{r['type']}] {str(r['name'])[:55]} | {r['city']}, {r['state']} | EIN:{r.get('ein','?')}")

# 4. Shea in email index
print(f"\n{'='*60}")
print("SHEA IN EMAILS")
print("=" * 60)
q4 = f"""
SELECT subject, sender, date_header, snippet
FROM `{PRJ}.national_audits.gmail_index`
WHERE LOWER(subject) LIKE '%shea%' OR LOWER(snippet) LIKE '%shea homes%'
   OR LOWER(snippet) LIKE '%shea properties%' OR LOWER(snippet) LIKE '%shea eviction%'
   OR LOWER(snippet) LIKE '%parkside%shea%'
ORDER BY date_header DESC LIMIT 15
"""
for r in client.query(q4).result():
    print(f"  [{r['date_header']}] {str(r['subject'])[:80]}")
    s = str(r.get('snippet',''))[:120]
    if s: print(f"    {s}")

# 5. Shea in drive_file_index (any referenced PDFs/docs)
print(f"\n{'='*60}")
print("SHEA IN DRIVE FILES")
print("=" * 60)
q5 = f"""
SELECT file_name, mime_type, size_bytes, created_time, owner_names, web_view_link
FROM `{PRJ}.national_audits.drive_file_index`
WHERE LOWER(file_name) LIKE '%shea%' OR LOWER(file_name) LIKE '%parkside%'
ORDER BY created_time DESC LIMIT 15
"""
for r in client.query(q5).result():
    sz_mb = int(r.get('size_bytes',0))/1e6
    print(f"  {str(r['file_name'])[:70]} ({sz_mb:.1f}MB) | {str(r.get('owner_names',''))[:30]}")

# 6. Dimarcello / eviction / Shea connections
print(f"\n{'='*60}")
print("SHEA + DIMARCELLO + EVICTION IN EMAILS")
print("=" * 60)
q6 = f"""
SELECT subject, sender, date_header, snippet
FROM `{PRJ}.national_audits.gmail_index`
WHERE (LOWER(subject) LIKE '%dimarcello%' OR LOWER(subject) LIKE '%eviction%shea%'
    OR LOWER(snippet) LIKE '%dimarcello%shea%' OR LOWER(snippet) LIKE '%shea%evict%')
ORDER BY date_header DESC LIMIT 10
"""
for r in client.query(q6).result():
    print(f"  [{r['date_header']}] {str(r['subject'])[:80]}")

print(f"\n{'='*60}")
print("DONE")
