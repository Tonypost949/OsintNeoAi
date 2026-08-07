import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=== rico_network_map schema ===")
table1 = client.get_table(f"{PRJ}.forensic_layers.rico_network_map")
for field in table1.schema:
    print(f"  {field.name} ({field.field_type})")

print("\n=== fca_timeline schema ===")
table2 = client.get_table(f"{PRJ}.forensic_layers.fca_timeline")
for field in table2.schema:
    print(f"  {field.name} ({field.field_type})")

print("\n=== gmail_index schema ===")
table3 = client.get_table(f"{PRJ}.national_audits.gmail_index")
for field in table3.schema:
    print(f"  {field.name} ({field.field_type})")
