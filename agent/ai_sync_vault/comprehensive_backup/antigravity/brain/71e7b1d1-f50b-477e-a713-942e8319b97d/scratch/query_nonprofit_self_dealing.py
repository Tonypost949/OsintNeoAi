from google.cloud import bigquery
import pandas as pd
import sys

# Configure stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

client = bigquery.Client()
project = client.project
dataset = "ppp_rico"

print("==================================================")
print("1. QUERYING v_nonprofit_board_ppp_self_dealing")
print("==================================================")

sql_self_dealing = f"""
SELECT board_member, nonprofit, vendor_entity, ppp_borrower_name, ppp_amount, ppp_forgiven, ppp_location, ppp_status, legal_exposure, source_doc
FROM `{project}.{dataset}.v_nonprofit_board_ppp_self_dealing`
"""
try:
    df_sd = client.query(sql_self_dealing).to_dataframe()
    print(f"Found {len(df_sd)} rows:")
    print(df_sd.to_string())
except Exception as e:
    print(f"Error: {e}")


print("\n==================================================")
print("2. QUERYING unified_enterprise FOR COCS")
print("==================================================")

sql_unified = f"""
SELECT pipeline, entity_name, entity_type, oc_property, property_value, ppp_amount, ppp_state, ppp_lender, hud_grant, flags
FROM `{project}.{dataset}.unified_enterprise`
"""
try:
    df_uni = client.query(sql_unified).to_dataframe()
    print(f"Found {len(df_uni)} rows total.")
    # Filter for any of our CoC keywords
    keywords = ["orangewood", "pathways", "homeaid", "illumination", "covenant", "casa", "waymakers", "salvation", "spin", "laurel", "thomas", "colette", "promise", "human options", "laura", "interval", "wtlc", "radiant", "wiseplace"]
    mask = df_uni['entity_name'].astype(str).str.lower().apply(lambda x: any(kw in x for kw in keywords))
    df_filtered = df_uni[mask]
    print(f"Found {len(df_filtered)} rows matching CoC keywords:")
    print(df_filtered.to_string())
except Exception as e:
    print(f"Error: {e}")
