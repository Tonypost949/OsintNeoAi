"""Check national scope of RICO/environmental patterns"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=" * 60)
print("NATIONAL ENVIRONMENTAL SITE ASSESSMENTS BY STATE")
print("=" * 60)
q1 = f"SELECT state, environmental_site_assessments FROM `{PRJ}.national_audits.all_state_records`"
for r in client.query(q1).result():
    esa = str(r["environmental_site_assessments"])
    if esa and esa != "None" and len(esa) > 10:
        flags = []
        if "Cr" in esa or "chromium" in esa.lower():
            flags.append("CrVI")
        if "fraud" in esa.lower() or "Fraudulent" in esa:
            flags.append("FRAUD")
        if "Disputed" in esa:
            flags.append("DISPUTED")
        flag_str = f" [{','.join(flags)}]" if flags else ""
        print(f"  {r['state']}: {len(esa)} chars{flag_str}")
        if flags:
            print(f"    {esa[:300]}")

print()
print("=" * 60)
print("TOP FORENSIC HAZARD SITES (mat_looker_forensic_base)")
print("=" * 60)
q2 = f"""
SELECT state_anchor, hazard_site, toxic_severity_multiplier, 
       active_audits, total_homeless_count
FROM `{PRJ}.national_audits.mat_looker_forensic_base` 
ORDER BY toxic_severity_multiplier DESC LIMIT 20
"""
for r in client.query(q2).result():
    ts = r.get("toxic_severity_multiplier", "N/A")
    print(f"  {r['state_anchor']}: hazard={r.get('hazard_site','?')}, tox_x{ts}, audits={r.get('active_audits',0)}, homeless={r.get('total_homeless_count',0)}")

print()
print("=" * 60)
print("RICO/FRAUD RELATED EMAILS (gmail_index)")
print("=" * 60)
q3 = f"""
SELECT subject, sender, recipient, date_header, snippet 
FROM `{PRJ}.national_audits.gmail_index` 
WHERE LOWER(subject) LIKE '%rico%' 
   OR LOWER(subject) LIKE '%fraud%' 
   OR LOWER(subject) LIKE '%ppp%'
ORDER BY date_header DESC LIMIT 10
"""
for r in client.query(q3).result():
    print(f"  [{r['date_header']}] {str(r['subject'])[:80]}")
    print(f"    From: {str(r['sender'])[:50]}")

print()
print("=" * 60)
print("PPP NONPROFIT LOANS BY STATE (NON-CA)")
print("=" * 60)
q4 = f"""
SELECT BorrowerState, COUNT(*) AS loans, 
       ROUND(SUM(CAST(CurrentApprovalAmount AS FLOAT64)),0) AS total_ppp
FROM `{PRJ}.ppp_rico.ppp_150k_plus`
WHERE NonProfit = 'Y' AND BorrowerState != 'CA'
GROUP BY BorrowerState
ORDER BY total_ppp DESC LIMIT 15
"""
for r in client.query(q4).result():
    print(f"  {r['BorrowerState']}: {r['loans']} loans, ${r['total_ppp']:,.0f}")

print()
print("DONE")
