from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

print("=== CHECKING ALL TABLES FOR MERCY HOUSE & LARRY HAYNES ===")
q = f"""
SELECT 'network_assets' as source, suspect, state, holder, amount, property_id, address, status
FROM `{P}.unclaimed_property.network_assets`
WHERE UPPER(suspect) LIKE '%MERCY%' 
   OR UPPER(suspect) LIKE '%HAYNES%'
   OR UPPER(holder) LIKE '%MERCY%'
   OR UPPER(holder) LIKE '%HAYNES%'
   OR UPPER(address) LIKE '%MERCY%'
   OR UPPER(address) LIKE '%HAYNES%'
"""
try:
    results = bq.query(q).to_dataframe()
    if len(results) > 0:
        print(f"✅ Found {len(results)} matches in network_assets:")
        print(results.to_string())
    else:
        print("No direct matches in network_assets using broad filters.")
except Exception as e:
    print(f"Error querying network_assets: {e}")

# Check all tables in ppp_rico dataset for Larry Haynes or Mercy House
print("\n=== SEARCHING ALL TABLES IN ppp_rico DATASET ===")
tables = list(bq.list_tables(f"{P}.ppp_rico"))
for t in tables:
    table_name = f"{P}.ppp_rico.{t.table_id}"
    # Get columns
    t_obj = bq.get_table(t.reference)
    cols = [f.name for f in t_obj.schema]
    
    # Identify string columns
    str_cols = [f.name for f in t_obj.schema if f.field_type == 'STRING']
    if not str_cols:
        continue
        
    conditions = []
    for c in str_cols:
        conditions.append(f"UPPER({c}) LIKE '%MERCY HOUSE%'")
        conditions.append(f"UPPER({c}) LIKE '%LARRY HAYNES%'")
        
    where_clause = " OR ".join(conditions)
    q_search = f"SELECT * FROM `{table_name}` WHERE {where_clause} LIMIT 10"
    
    try:
        res = bq.query(q_search).to_dataframe()
        if len(res) > 0:
            print(f"\n✅ FOUND matches in ppp_rico.{t.table_id}:")
            print(res.to_string())
    except Exception as e:
        pass
