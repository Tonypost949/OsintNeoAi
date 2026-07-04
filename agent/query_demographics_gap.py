from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

print("--- National Pipeline Map Math (Adult Gap + Demographics) ---")
q1 = """
SELECT state, pit_count, sheltered, unsheltered, cps_est, gap 
FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.national_pipeline_map`
WHERE state = 'CA'
"""
res1 = client.query(q1).result()
for r in res1:
    print(dict(r))

print("\n--- Demographics / Race Math (PPP Loans or other tables) ---")
q2 = """
SELECT demographics, count(*) as cnt 
FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.ppp_loans`
GROUP BY demographics
"""
try:
    res2 = client.query(q2).result()
    for r in res2:
        print(dict(r))
except Exception as e:
    print(e)
