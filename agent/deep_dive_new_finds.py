from google.cloud import bigquery
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

# THE LE FAMILY LLC
print('=== THE LE FAMILY LLC ===')
for t in ['ppp_150k_plus', 'ppp_up_to_150k']:
    q = f"SELECT * FROM project-743aab84-f9a5-4ec7-954.ppp_rico.{t} WHERE UPPER(BorrowerName) LIKE '%LE FAMILY%' ORDER BY DateApproved"
    rows = list(client.query(q).result())
    if rows:
        for r in rows:
            fg = f"${r.ForgivenessAmount:,.0f}" if r.ForgivenessAmount else "N/A"
            print(f"  [{t}] ${r.CurrentApprovalAmount:,.0f} | {r.BorrowerName[:60]} | {r.BorrowerCity}, {r.BorrowerState} | {r.LoanStatus} | Forgiven: {fg} | Lender: {r.OriginatingLender}")

q = "SELECT * FROM project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs WHERE UPPER(Owner1) LIKE '%LE FAMILY%'"
rows = list(client.query(q).result())
for r in rows:
    print(f"  Property: {r.Owner1} | {r.SiteAddress} | APN {r.APN} | Mail: {r.MailAddress}, {r.MailCity} | Sale: {r.LastSaleDate} ${r.LastSaleValue:,.0f}" if r.LastSaleValue else f"  Property: {r.Owner1} | {r.SiteAddress} | APN {r.APN} | Mail: {r.MailAddress}, {r.MailCity}")

# HB LLC
print('\n=== HB LLC ===')
q = "SELECT * FROM project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs WHERE UPPER(Owner1) LIKE '%HB LLC%'"
rows = list(client.query(q).result())
for r in rows[:8]:
    sv = f" | Sale: {r.LastSaleDate} ${r.LastSaleValue:,.0f}" if r.LastSaleValue else ""
    print(f"  {r.Owner1} | {r.SiteAddress} | Mail: {r.MailAddress}, {r.MailCity} | APN: {r.APN}{sv}")

# HB LLC PPP
print('\n=== HB LLC PPP ===')
for t in ['ppp_150k_plus', 'ppp_up_to_150k']:
    q = f"SELECT * FROM project-743aab84-f9a5-4ec7-954.ppp_rico.{t} WHERE UPPER(BorrowerName) = 'HB LLC' ORDER BY DateApproved"
    rows = list(client.query(q).result())
    if rows:
        for r in rows:
            fg = f"${r.ForgivenessAmount:,.0f}" if r.ForgivenessAmount else "N/A"
            print(f"  [{t}] ${r.CurrentApprovalAmount:,.0f} | {r.BorrowerName} | {r.BorrowerCity}, {r.BorrowerState} | Status: {r.LoanStatus} | Forgiven: {fg} | Lender: {r.OriginatingLender} | Jobs: {r.JobsReported}")

# RICO check
print('\n=== RICO MATRIX ===')
q = "SELECT * FROM project-743aab84-f9a5-4ec7-954.ppp_rico.rico_evidence_matrix WHERE UPPER(llc_name) LIKE '%HB LLC%' OR UPPER(llc_name) LIKE '%LE FAMILY%'"
rows = list(client.query(q).result())
for r in rows:
    d = {k: str(v)[:100] for k, v in dict(r).items() if v}
    print(f"  {json.dumps(d)}")

print('\nDone.')
