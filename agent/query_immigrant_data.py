from google.cloud import bigquery

client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

print("--- Searching for Immigrant/Migrant/Unaccompanied Data in BQ ---")

queries = [
    """
    SELECT * 
    FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.cps_trafficking_layer`
    WHERE LOWER(entity) LIKE '%immigrant%' OR LOWER(entity) LIKE '%migrant%' OR LOWER(entity) LIKE '%unaccompanied%' OR LOWER(entity) LIKE '%border%' OR LOWER(role) LIKE '%immigrant%' OR LOWER(role) LIKE '%migrant%' OR LOWER(role) LIKE '%unaccompanied%'
    """,
    """
    SELECT * 
    FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.national_pipeline_map`
    WHERE LOWER(forensic_flags) LIKE '%immigrant%' OR LOWER(forensic_flags) LIKE '%migrant%' OR LOWER(forensic_flags) LIKE '%unaccompanied%'
    """
]

for i, q in enumerate(queries):
    try:
        res = client.query(q).result()
        rows = list(res)
        print(f"Query {i+1} results: {len(rows)}")
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Query {i+1} failed: {e}")
