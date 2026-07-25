import sys
try:
    from google.cloud import bigquery
    client = bigquery.Client()
    print("google-cloud-bigquery client initialized successfully.")
    datasets = list(client.list_datasets())
    print("Datasets found:", [d.dataset_id for d in datasets])
except Exception as e:
    print("Error initializing bigquery client:", e)
