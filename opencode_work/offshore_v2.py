"""Fix and run offshore query - clean"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
c = bigquery.Client()

print("OFFSHORE / FOREIGN INDICATORS IN all_state_records")
q = """
SELECT state, npi.organization_name, npi.cms_billing_code, npi.unaccounted_fund_delta,
  REGEXP_EXTRACT(LOWER(npi.organization_name), r'(remit|overseas|foreign|international|philippines|manila)') as offshore_indicator
FROM noble-beanbag-497411-m4.national_audits.all_state_records,
UNNEST(non_profiteers_index) as npi
WHERE REGEXP_CONTAINS(LOWER(npi.organization_name), r'(remit|overseas|foreign|international|philippines|manila)')
ORDER BY CAST(npi.unaccounted_fund_delta AS NUMERIC) DESC
"""
rows = list(c.query(q).result())
print(f"Matches: {len(rows)}")
for r in rows:
    amt = r.get("unaccounted_fund_delta") or 0
    st = r["state"]
    org = str(r.get("organization_name",""))[:70]
    code = str(r.get("cms_billing_code",""))[:30]
    ind = str(r.get("offshore_indicator",""))
    print(f"  ${float(amt):>15,.0f}  {st}  {org}  [{code}]  indicator={ind}")

print()
print("ALL CA PROFITEERS")
q2 = """
SELECT state, npi.organization_name, npi.cms_billing_code, npi.unaccounted_fund_delta
FROM noble-beanbag-497411-m4.national_audits.all_state_records,
UNNEST(non_profiteers_index) as npi
WHERE state = 'CA'
ORDER BY CAST(npi.unaccounted_fund_delta AS NUMERIC) DESC
"""
for r in c.query(q2).result():
    amt = r.get("unaccounted_fund_delta") or 0
    org = str(r.get("organization_name",""))[:70]
    code = str(r.get("cms_billing_code",""))[:40]
    print(f"  ${float(amt):>15,.0f}  {org}  [{code}]")
