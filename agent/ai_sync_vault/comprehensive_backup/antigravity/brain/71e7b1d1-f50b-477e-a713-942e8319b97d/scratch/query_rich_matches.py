from google.cloud import bigquery
import pandas as pd

client = bigquery.Client()
project = client.project
dataset = "ppp_rico"

def search_table(table_name, search_cols, keyword):
    where_clauses = [f"LOWER({col}) LIKE '%{keyword.lower()}%'" for col in search_cols]
    sql = f"""
    SELECT *
    FROM `{project}.{dataset}.{table_name}`
    WHERE {" OR ".join(where_clauses)}
    """
    try:
        df = client.query(sql).result().to_dataframe()
        return df
    except Exception as e:
        print(f"Error querying {table_name}: {e}")
        return pd.DataFrame()

keywords = ["covenant", "nunez", "barnes", "shea", "gilbert", "east st"]

print("==================================================")
print("SEARCHING UNIFIED_ENTERPRISE")
print("==================================================")
cols = ["pipeline", "entity_name", "oc_property", "ppp_borrower", "flags"] # wait, let's look at schema
# Column list for unified_enterprise: pipeline, entity_name, entity_type, oc_property, property_value, ppp_amount, ppp_state, ppp_lender, naics, sector, deaths, missing_children, address_note, hud_grant, ive_billing, flags
cols = ["pipeline", "entity_name", "entity_type", "oc_property", "address_note", "flags"]
for kw in keywords:
    df = search_table("unified_enterprise", cols, kw)
    if len(df) > 0:
        print(f"Found {len(df)} rows for '{kw}':")
        print(df.to_string())

print("\n==================================================")
print("SEARCHING PPP_150K_PLUS")
print("==================================================")
cols_ppp = ["BorrowerName", "BorrowerAddress", "BorrowerCity", "BorrowerState", "ProjectCity", "OriginatingLender"]
for kw in keywords:
    df = search_table("ppp_150k_plus", cols_ppp, kw)
    if len(df) > 0:
        print(f"Found {len(df)} rows for '{kw}' (showing first 10):")
        print(df.head(10).to_string())

print("\n==================================================")
print("SEARCHING TRAFFICKING_MATCHES")
print("==================================================")
cols_traf = ["BorrowerName", "BorrowerAddress", "BorrowerCity", "BorrowerState"]
for kw in keywords:
    df = search_table("trafficking_matches", cols_traf, kw)
    if len(df) > 0:
        print(f"Found {len(df)} rows for '{kw}':")
        print(df.to_string())
