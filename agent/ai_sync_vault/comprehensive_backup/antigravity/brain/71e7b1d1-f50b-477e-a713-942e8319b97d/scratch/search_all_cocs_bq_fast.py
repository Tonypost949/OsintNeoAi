from google.cloud import bigquery
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

client = bigquery.Client()
project = client.project
dataset = "ppp_rico"

regex_pattern = r"(?i)orangewood|pathways of hope|homeaid|family assistance|illumination|covenant house|casa youth|waymakers|families forward|salvation army|serving people|hope harbor|laurel house|homeless intervention|thomas house|family promise|colette|american family|wiseplace|human options|laura's house|interval house|women's transitional|wtlc|radiant futures"

print("==================================================")
print("FAST BQ COCS PATTERN SEARCH")
print("==================================================")

# 1. regional_llcs
print("\n--- 1. Searching regional_llcs ---")
sql_1 = f"""
SELECT llc_name, property_address, city, state, ppp_amount, ppp_forgiven, status, source
FROM `{project}.{dataset}.regional_llcs`
WHERE REGEXP_CONTAINS(llc_name, r"{regex_pattern}")
   OR REGEXP_CONTAINS(property_address, r"{regex_pattern}")
"""
try:
    df_1 = client.query(sql_1).to_dataframe()
    print(f"Found {len(df_1)} matching rows in regional_llcs:")
    print(df_1.to_string())
except Exception as e:
    print(f"Error querying regional_llcs: {e}")

# 2. v_rico_enterprise_master
print("\n--- 2. Searching v_rico_enterprise_master ---")
sql_2 = f"""
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleDate, LastSaleValue, clean_owner, ppp_borrower, ppp_city, ppp_state, ppp_amount, ppp_status
FROM `{project}.{dataset}.v_rico_enterprise_master`
WHERE REGEXP_CONTAINS(ppp_borrower, r"{regex_pattern}")
   OR REGEXP_CONTAINS(Owner1, r"{regex_pattern}")
   OR REGEXP_CONTAINS(Owner2, r"{regex_pattern}")
   OR REGEXP_CONTAINS(SiteAddress, r"{regex_pattern}")
   OR REGEXP_CONTAINS(MailAddress, r"{regex_pattern}")
"""
try:
    df_2 = client.query(sql_2).to_dataframe()
    print(f"Found {len(df_2)} matching rows in v_rico_enterprise_master:")
    print(df_2.to_string())
except Exception as e:
    print(f"Error querying v_rico_enterprise_master: {e}")

# 3. v_nonprofit_board_ppp_self_dealing
print("\n--- 3. Searching v_nonprofit_board_ppp_self_dealing ---")
sql_3 = f"""
SELECT board_member, nonprofit, vendor_entity, ppp_borrower_name, ppp_amount, ppp_forgiven, ppp_location, ppp_status, legal_exposure, source_doc
FROM `{project}.{dataset}.v_nonprofit_board_ppp_self_dealing`
WHERE REGEXP_CONTAINS(nonprofit, r"{regex_pattern}")
   OR REGEXP_CONTAINS(vendor_entity, r"{regex_pattern}")
   OR REGEXP_CONTAINS(board_member, r"{regex_pattern}")
"""
try:
    df_3 = client.query(sql_3).to_dataframe()
    print(f"Found {len(df_3)} matching rows in v_nonprofit_board_ppp_self_dealing:")
    print(df_3.to_string())
except Exception as e:
    print(f"Error querying v_nonprofit_board_ppp_self_dealing: {e}")

# 4. unified_enterprise
print("\n--- 4. Searching unified_enterprise ---")
sql_4 = f"""
SELECT pipeline, entity_name, entity_type, oc_property, property_value, ppp_amount, ppp_state, ppp_lender, naics, sector, deaths, missing_children, address_note, hud_grant, ive_billing, flags
FROM `{project}.{dataset}.unified_enterprise`
WHERE REGEXP_CONTAINS(entity_name, r"{regex_pattern}")
   OR REGEXP_CONTAINS(oc_property, r"{regex_pattern}")
"""
try:
    df_4 = client.query(sql_4).to_dataframe()
    print(f"Found {len(df_4)} matching rows in unified_enterprise:")
    print(df_4.to_string())
except Exception as e:
    print(f"Error querying unified_enterprise: {e}")

print("\nFast search complete.")
