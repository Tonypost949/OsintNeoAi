from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

print("=== DEEP DB SCAN: SEARCHING ALL DATASETS FOR TARGETS ===")

datasets = ["ppp_rico", "unclaimed_property", "forensic_layers", "forensic_views", "fraud_mart", "hb_church_osint"]

for ds in datasets:
    try:
        tables = list(bq.list_tables(f"{P}.{ds}"))
        for t in tables:
            table_name = f"{P}.{ds}.{t.table_id}"
            t_obj = bq.get_table(t.reference)
            str_cols = [f.name for f in t_obj.schema if f.field_type == 'STRING']
            if not str_cols:
                continue
                
            conditions = []
            for col in str_cols:
                conditions.append(f"UPPER({col}) LIKE '%MERCY%'")
                conditions.append(f"UPPER({col}) LIKE '%HAYNES%'")
                
            where_clause = " OR ".join(conditions)
            q = f"SELECT * FROM `{table_name}` WHERE {where_clause} LIMIT 10"
            
            try:
                res = bq.query(q).to_dataframe()
                if len(res) > 0:
                    print(f"\n[FOUND MATCHES] Dataset: {ds} | Table: {t.table_id} | Rows: {len(res)}")
                    print(res.to_string())
            except Exception as e:
                pass
    except Exception as e:
        print(f"Error accessing dataset {ds}: {e}")

print("\n=== SCAN COMPLETE ===")
