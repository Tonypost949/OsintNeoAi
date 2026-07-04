from google.cloud import bigquery
import pandas as pd

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

tribal_terms = [
    "KUMEYAAY", "LUISENO", "LUISEÑO", "TONGVA", "CAHUILLA", "SOBOBA", "PECHANGA",
    "PALA", "RINCON", "SOBOBA", "SYCUAN", "VIEJAS", "BARONA", "CAMPO", "MORONGO",
    "BAND OF", "INDIAN", "TRIBE", "TRIBAL", "MISSION INDIANS"
]

print("=== RUNNING SEARCH FOR TRIBAL ENTITIES IN UNCLAIMED PROPERTY ===")

table_name = f"{P}.unclaimed_property.ca_unclaimed_raw"
conditions = []
for term in tribal_terms:
    conditions.append(f"UPPER(decedent_or_heir_name) LIKE '%{term}%'")

where_clause = " OR ".join(conditions)
q = f"SELECT * FROM `{table_name}` WHERE {where_clause} LIMIT 100"

try:
    results = bq.query(q).to_dataframe()
    if len(results) > 0:
        print(f"FOUND {len(results)} TRIBAL-RELATED RECORDS:")
        print(results.to_string(index=False))
        # Save results to a file
        results.to_csv("tribal_unclaimed_matches.csv", index=False)
        print("\nResults saved to tribal_unclaimed_matches.csv")
    else:
        print("No tribal records found in ca_unclaimed_raw.")
except Exception as e:
    print(f"Error: {e}")
