from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

print("=== CHECKING UNCLAIMED PROPERTY DATASET SCHEMA ===")
# List tables in the unclaimed_property dataset
tables = list(bq.list_tables(f"{P}.unclaimed_property"))
for t in tables:
    print(f"Table: {t.table_id}")
    table_obj = bq.get_table(t.reference)
    for field in table_obj.schema[:10]: # Print first 10 fields
        print(f"  {field.name}: {field.field_type}")

print("\n=== RUNNING SEARCH FOR MERCY HOUSE & LARRY HAYNES ===")
# Let's search all tables in the dataset for Mercy House or Larry Haynes
for t in tables:
    table_name = f"{P}.unclaimed_property.{t.table_id}"
    print(f"\nSearching table: {table_name}")
    
    # We will search fields dynamically. Let's look for columns with 'name' or 'owner' or 'business'
    schema = bq.get_table(t.reference).schema
    cols = [f.name for f in schema]
    
    name_cols = [c for c in cols if any(term in c.lower() for term in ['name', 'owner', 'recipient', 'claimant'])]
    if not name_cols:
        name_cols = cols[:3] # fallback
        
    print(f"Searching columns: {name_cols}")
    
    # Build query
    conditions = []
    for col in name_cols:
        conditions.append(f"UPPER({col}) LIKE '%MERCY HOUSE%'")
        conditions.append(f"UPPER({col}) LIKE '%LARRY HAYNES%'")
        conditions.append(f"UPPER({col}) LIKE '%HAYNES LARRY%'")
    
    where_clause = " OR ".join(conditions)
    
    q = f"SELECT * FROM `{table_name}` WHERE {where_clause} LIMIT 50"
    try:
        results = bq.query(q).to_dataframe()
        if len(results) > 0:
            print(f"✅ FOUND {len(results)} RECORDS in {t.table_id}:")
            print(results.to_string())
        else:
            print("No records found in this table.")
    except Exception as e:
        print(f"Error querying table {t.table_id}: {e}")
