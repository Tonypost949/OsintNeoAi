from google.cloud import bigquery

client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

q = """SELECT * 
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k` 
WHERE UPPER(BorrowerName) LIKE '%SCHUYLER OPPENHEIMER%'"""

print("=== SCHUYLER OPPENHEIMER DETAILS ===")
for r in client.query(q).result():
    for k, v in dict(r).items():
        print(f"  {k}: {v}")
