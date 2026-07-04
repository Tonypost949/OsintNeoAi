from google.cloud import bigquery
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

print('=== NV MAILBOXES IN HB PROPERTIES ===')
q = """SELECT MailAddress, COUNT(*) as cnt, COUNT(DISTINCT Owner1) as owners 
FROM project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs 
WHERE UPPER(MailCity) LIKE '%LAS VEGAS%' OR UPPER(MailCity) LIKE '%HENDERSON%' OR UPPER(MailCity) LIKE '%RENO%' 
GROUP BY MailAddress ORDER BY cnt DESC LIMIT 15"""
for r in client.query(q).result():
    print(f'  {r.MailAddress}: {r.cnt} records, {r.owners} owners')

print('\n=== NV RICO MATRIX ===')
q = """SELECT llc_name, mail_city, ppp_loan_count, ppp_total_amount 
FROM project-743aab84-f9a5-4ec7-954.ppp_rico.rico_evidence_matrix 
WHERE UPPER(mail_city) LIKE '%LAS VEGAS%' OR UPPER(mail_city) LIKE '%HENDERSON%'"""
for r in client.query(q).result():
    print(f'  {r.llc_name} | {r.mail_city} | {r.ppp_loan_count} loans | ${r.ppp_total_amount}')

print('\n=== NV HB LLC LOANS ===')
for t in ['ppp_150k_plus', 'ppp_up_to_150k']:
    q = f"""SELECT BorrowerName, BorrowerCity, CurrentApprovalAmount, LoanStatus, ForgivenessAmount, DateApproved
FROM project-743aab84-f9a5-4ec7-954.ppp_rico.{t}
WHERE UPPER(BorrowerState) = 'NV' AND UPPER(BorrowerName) LIKE '%LLC%'
ORDER BY CurrentApprovalAmount DESC LIMIT 10"""
    for r in client.query(q).result():
        fg = f'${r.ForgivenessAmount:,.0f}' if r.ForgivenessAmount else 'N/A'
        print(f'  ${r.CurrentApprovalAmount:,.0f} | {r.BorrowerName[:50]} | {r.BorrowerCity}, NV | {r.LoanStatus} | Forgiven: {fg}')

print('\nDone.')
