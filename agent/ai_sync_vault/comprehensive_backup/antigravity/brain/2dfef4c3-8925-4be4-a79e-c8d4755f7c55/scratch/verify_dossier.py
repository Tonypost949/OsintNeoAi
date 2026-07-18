from google.cloud import bigquery
import json

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954", location="us-west1")
P = "project-743aab84-f9a5-4ec7-954"

q = f"SELECT section_name, SUBSTR(content, 1, 100) as snippet, parsed_metadata FROM `{P}.ppp_rico.forensic_investigative_dossier` ORDER BY section_name"
try:
    query_job = client.query(q)
    df = query_job.to_dataframe()
    for idx, row in df.iterrows():
        print(f"Section: {row['section_name']}")
        print(f"Snippet: {row['snippet'].strip()}...")
        print(f"Metadata: {row['parsed_metadata']}")
        print("-" * 50)
except Exception as e:
    print(f"Error: {e}")
