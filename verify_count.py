from google.cloud import bigquery

client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
query = 'SELECT COUNT(*) as cnt FROM `project-743aab84-f9a5-4ec7-954.national_audits.takeout_chrome_history`'
results = list(client.query(query).result())
print('VERIFIED COUNT:', results[0].cnt)
