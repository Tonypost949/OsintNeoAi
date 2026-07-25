from google.cloud import bigquery
import pandas as pd

client = bigquery.Client()
project = client.project
dataset = "ppp_rico"

sql = f"""
SELECT ppp_state, COUNT(*) as count, SUM(ppp_amount) as total_amount
FROM `{project}.{dataset}.v_rico_enterprise_master`
GROUP BY ppp_state
ORDER BY total_amount DESC
"""

df = client.query(sql).result().to_dataframe()
print("RICO States and Loan Amounts:")
print(df.to_string())
df.to_csv("rico_states_summary.csv", index=False)
