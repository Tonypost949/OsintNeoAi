from google.cloud import bigquery

client = bigquery.Client(project='noble-beanbag-497411-m4')

q = """SELECT * 
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k` 
WHERE UPPER(BorrowerName) LIKE '%SCHUYLER OPPENHEIMER%'"""

print("=== SCHUYLER OPPENHEIMER DETAILS ===")
for r in client.query(q).result():
    for k, v in dict(r).items():
        print(f"  {k}: {v}")
