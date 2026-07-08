from google.cloud import bigquery
client = bigquery.Client(project="noble-beanbag-497411-m4")
q = """
SELECT column_name
FROM `noble-beanbag-497411-m4.ppp_rico.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'hb_llcs'
"""
df = client.query(q).to_dataframe()
print("hb_llcs columns:", df["column_name"].tolist())

q2 = """
SELECT column_name
FROM `noble-beanbag-497411-m4.ppp_rico.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'chdo_transactions'
"""
df2 = client.query(q2).to_dataframe()
print("chdo_transactions columns:", df2["column_name"].tolist())
