from google.cloud import bigquery

bq = bigquery.Client(project="noble-beanbag-497411-m4")
P = "noble-beanbag-497411-m4"

print("=== VERIFYING BIGQUERY TABLE: oc_ammunition_bids ===")
q = f"SELECT bid_name, attachments_list, source_folder FROM `{P}.unclaimed_property.oc_ammunition_bids`"
try:
    df = bq.query(q).to_dataframe()
    print(df.to_string(index=False))
except Exception as e:
    print(f"Error: {e}")
