from google.cloud import bigquery
import pandas as pd
import sys

# Configure stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

client = bigquery.Client()
project = client.project
dataset = "ppp_rico"

# Robust list of CoC providers from Anaheim and County-wide lists
keywords = [
    ("Orangewood Children and Family Center (OCFC)", "Orangewood"),
    ("Pathways of Hope (Via Esperanza)", "Pathways of Hope"),
    ("HomeAid Family CareCenter", "HomeAid"),
    ("Family Assistance Ministries (FAM)", "Family Assistance"),
    ("Illumination Foundation", "Illumination"),
    ("Covenant House California", "Covenant House"),
    ("Casa Youth Shelter", "Casa Youth"),
    ("Huntington Beach Youth Shelter (Waymakers)", "Waymakers"),
    ("Families Forward", "Families Forward"),
    ("Salvation Army", "Salvation Army"),
    ("Serving People In Need (SPIN)", "Serving People"),
    ("Hope Harbor (Laurel House)", "Hope Harbor"),
    ("Hope Harbor (Laurel House) - Laurel House", "Laurel House"),
    ("Orangewood Foundation", "Orangewood"),
    ("Homeless Intervention Services of OC (HIS-OC)", "Homeless Intervention"),
    ("Thomas House Temporary Shelter", "Thomas House"),
    ("Family Promise of Orange County", "Family Promise"),
    ("Colette's Children's Home", "Colette"),
    ("American Family Housing", "American Family"),
    ("WISEPlace", "WISEPlace"),
    ("Human Options", "Human Options"),
    ("Laura's House", "Laura's House"),
    ("Interval House", "Interval House"),
    ("Women's Transitional Living Center (WTLC / Radiant Futures)", "Women's Transitional"),
    ("WTLC", "WTLC"),
    ("Radiant Futures", "Radiant Futures")
]

print("==================================================")
print("SEARCHING COCS IN BIGQUERY (ROBUST)")
print("==================================================")

# Function to escape single quotes in SQL strings
def escape_sql(text):
    return text.replace("'", "''")

# Search in regional_llcs
print("\n--- 1. Searching regional_llcs ---")
for org_name, kw in keywords:
    escaped_kw = escape_sql(kw.lower())
    sql = f"""
    SELECT llc_name, property_address, city, state, ppp_amount, ppp_forgiven, status, source
    FROM `{project}.{dataset}.regional_llcs`
    WHERE LOWER(llc_name) LIKE '%{escaped_kw}%'
       OR LOWER(property_address) LIKE '%{escaped_kw}%'
    """
    try:
        df = client.query(sql).to_dataframe()
        if len(df) > 0:
            print(f"\n[MATCH] {org_name} (Keyword: '{kw}') -> Found {len(df)} rows:")
            print(df.to_string())
    except Exception as e:
        print(f"Error querying regional_llcs for {org_name}: {e}")

# Search in v_rico_enterprise_master
print("\n--- 2. Searching v_rico_enterprise_master ---")
for org_name, kw in keywords:
    escaped_kw = escape_sql(kw.lower())
    sql = f"""
    SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleDate, LastSaleValue, clean_owner, ppp_borrower, ppp_city, ppp_state, ppp_amount, ppp_status
    FROM `{project}.{dataset}.v_rico_enterprise_master`
    WHERE LOWER(ppp_borrower) LIKE '%{escaped_kw}%'
       OR LOWER(Owner1) LIKE '%{escaped_kw}%'
       OR LOWER(Owner2) LIKE '%{escaped_kw}%'
       OR LOWER(SiteAddress) LIKE '%{escaped_kw}%'
       OR LOWER(MailAddress) LIKE '%{escaped_kw}%'
    """
    try:
        df = client.query(sql).to_dataframe()
        if len(df) > 0:
            print(f"\n[MATCH] {org_name} (Keyword: '{kw}') -> Found {len(df)} rows:")
            print(df.to_string())
    except Exception as e:
        print(f"Error querying v_rico_enterprise_master for {org_name}: {e}")

# Search in v_nonprofit_board_ppp_self_dealing
print("\n--- 3. Searching v_nonprofit_board_ppp_self_dealing ---")
for org_name, kw in keywords:
    escaped_kw = escape_sql(kw.lower())
    sql = f"""
    SELECT board_member, nonprofit, vendor_entity, ppp_borrower_name, ppp_amount, ppp_forgiven, ppp_location, ppp_status, legal_exposure, source_doc
    FROM `{project}.{dataset}.v_nonprofit_board_ppp_self_dealing`
    WHERE LOWER(nonprofit) LIKE '%{escaped_kw}%'
       OR LOWER(vendor_entity) LIKE '%{escaped_kw}%'
       OR LOWER(board_member) LIKE '%{escaped_kw}%'
    """
    try:
        df = client.query(sql).to_dataframe()
        if len(df) > 0:
            print(f"\n[MATCH] {org_name} (Keyword: '{kw}') -> Found {len(df)} rows:")
            print(df.to_string())
    except Exception as e:
        print(f"Error querying v_nonprofit_board_ppp_self_dealing for {org_name}: {e}")

# Search in unified_enterprise
print("\n--- 4. Searching unified_enterprise ---")
for org_name, kw in keywords:
    escaped_kw = escape_sql(kw.lower())
    sql = f"""
    SELECT pipeline, entity_name, entity_type, oc_property, property_value, ppp_amount, ppp_state, ppp_lender, naics, sector, deaths, missing_children, address_note, hud_grant, ive_billing, flags
    FROM `{project}.{dataset}.unified_enterprise`
    WHERE LOWER(entity_name) LIKE '%{escaped_kw}%'
       OR LOWER(oc_property) LIKE '%{escaped_kw}%'
    """
    try:
        df = client.query(sql).to_dataframe()
        if len(df) > 0:
            print(f"\n[MATCH] {org_name} (Keyword: '{kw}') -> Found {len(df)} rows:")
            print(df.to_string())
    except Exception as e:
        print(f"Error querying unified_enterprise for {org_name}: {e}")

print("\nSearch complete.")
