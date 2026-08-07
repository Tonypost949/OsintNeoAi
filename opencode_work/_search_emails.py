import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

q = f"""
SELECT msg_id, subject, sender, date_header, snippet
FROM `{PRJ}.national_audits.gmail_index`
WHERE LOWER(subject) LIKE '%foster care%' 
   OR LOWER(subject) LIKE '%dependency court%'
   OR LOWER(subject) LIKE '%child welfare%'
   OR LOWER(subject) LIKE '%iv-e%' OR LOWER(subject) LIKE '%title iv%'
   OR LOWER(subject) LIKE '%icwa%' OR LOWER(subject) LIKE '%indian child%'
   OR LOWER(subject) LIKE '%iim%' OR LOWER(subject) LIKE '%individual indian money%'
   OR LOWER(subject) LIKE '%group home%' OR LOWER(subject) LIKE '%congregate care%'
   OR LOWER(subject) LIKE '%orphanage%'
   OR LOWER(snippet) LIKE '%foster care%'
   OR LOWER(snippet) LIKE '%dependency court%'
   OR LOWER(snippet) LIKE '%child welfare%'
   OR LOWER(snippet) LIKE '%iv-e%' OR LOWER(snippet) LIKE '%title iv-e%'
   OR LOWER(snippet) LIKE '%icwa%' OR LOWER(snippet) LIKE '%indian child welfare%'
   OR LOWER(snippet) LIKE '%group home%' OR LOWER(snippet) LIKE '%congregate care%'
   OR LOWER(snippet) LIKE '%cps%removal%'
   OR LOWER(snippet) LIKE '%child protective%'
   OR LOWER(snippet) LIKE '%orphanage%'
ORDER BY date_header DESC LIMIT 50
"""
rows = list(client.query(q).result())
print(f"CPS-related emails found: {len(rows)}")
for r in rows:
    print(f"  MSG:{r['msg_id']} | {r['date_header']} | {str(r['subject'])[:80]}")
    print(f"    FROM: {str(r['sender'])[:80]}")
    print(f"    SNIP: {str(r['snippet'])[:140]}")
    print()
