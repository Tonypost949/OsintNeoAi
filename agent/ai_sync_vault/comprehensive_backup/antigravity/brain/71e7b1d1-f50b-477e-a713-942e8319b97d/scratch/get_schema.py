from google.cloud import bigquery
client = bigquery.Client()
table_ref = client.get_table("noble-beanbag-497411-m4.ppp_rico.hb_llcs")
print("Columns in hb_llcs:")
for field in table_ref.schema:
    print(f" - {field.name}: {field.field_type}")
