"""Pipeline 4: Philippines / Offshore Nexus query"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
c = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=" * 60)
print("PIPELINE 4: OFFSHORE / PHILIPPINES NEXUS")
print("=" * 60)

# Query 1: International remittance entities in all_state_records
q1 = f"""
SELECT state, npi.organization_name, npi.cms_billing_code, npi.unaccounted_fund_delta
FROM `{PRJ}.national_audits.all_state_records`,
UNNEST(non_profiteers_index) as npi
WHERE REGEXP_CONTAINS(LOWER(npi.organization_name), r'(remit|overseas|foreign|international|philippines|manila)')
ORDER BY npi.unaccounted_fund_delta DESC
"""
print()
print("--- International/Philippine entities in all_state_records ---")
results = list(c.query(q1).result())
print(f"Matches: {len(results)}")
for r in results:
    print(f"  {r['state']} | ${r.get('unaccounted_fund_delta',0)} | {r['organization_name'][:70]}")

# Query 2: PPP borrowers with international/Philippine ties
q2 = f"""
SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, DateApproved, NAICSCode
FROM `{PRJ}.ppp_rico.ppp_150k_plus`
WHERE REGEXP_CONTAINS(LOWER(BorrowerName), r'(philippin|manila|remit|international|overseas|foreign)')
ORDER BY CurrentApprovalAmount DESC LIMIT 20
"""
print()
print("--- PPP borrowers with international ties ---")
results2 = list(c.query(q2).result())
print(f"Matches: {len(results2)}")
for r in results2:
    print(f"  ${r['CurrentApprovalAmount']:>10,.0f}  {r['BorrowerCity']}, {r['BorrowerState']}  {r['BorrowerName'][:60]}")

# Query 3: Remittance/foreign emails
q3 = f"""
SELECT subject, sender, date_header, snippet
FROM `{PRJ}.national_audits.gmail_index`
WHERE REGEXP_CONTAINS(LOWER(subject), r'(remit|wire transfer|philippin|manila|foreign fund|overseas|western union|international transfer)')
ORDER BY date_header DESC LIMIT 10
"""
print()
print("--- Emails with remittance/foreign transfer keywords ---")
results3 = list(c.query(q3).result())
print(f"Matches: {len(results3)}")
for r in results3:
    print(f"  [{r['date_header']}] {r['subject'][:80]}")
    if r.get('snippet'):
        print(f"    {r['snippet'][:120]}")

# Query 4: LLCs with Philippines/Manila mail addresses
q4 = f"""
SELECT Owner1, SiteAddress, MailAddress, MailCity, LastSaleDate, LastSaleValue
FROM `{PRJ}.ppp_rico.hb_llcs`
WHERE REGEXP_CONTAINS(LOWER(MailAddress), r'(philippin|manila|foreign|overseas)')
   OR REGEXP_CONTAINS(LOWER(MailCity), r'(philippin|manila|foreign|overseas)')
ORDER BY LastSaleDate DESC
"""
print()
print("--- HB LLCs with Philippines/Foreign mail addresses ---")
results4 = list(c.query(q4).result())
print(f"Matches: {len(results4)}")
for r in results4:
    print(f"  {r['Owner1'][:35]} | {r['SiteAddress'][:35]} | {r['MailCity']} | ${r.get('LastSaleValue',0)}")

print()
print("DONE")
