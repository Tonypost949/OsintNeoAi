from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

# First, check the schema of hb_llcs and rico_matches to build the bridge
print("=== hb_llcs schema ===")
t = bq.get_table("project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs")
for f in t.schema:
    print(f"  {f.name}: {f.field_type}")

print("\n=== rico_matches schema ===")
t2 = bq.get_table("project-743aab84-f9a5-4ec7-954.ppp_rico.rico_matches")
for f in t2.schema:
    print(f"  {f.name}: {f.field_type}")

print("\n=== Sample hb_llcs (5 rows) ===")
rows = bq.query("SELECT * FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs` LIMIT 5").to_dataframe()
print(rows.to_string())

print("\n=== Sample rico_matches (5 rows) ===")
rows2 = bq.query("SELECT * FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.rico_matches` LIMIT 5").to_dataframe()
print(rows2.to_string())
