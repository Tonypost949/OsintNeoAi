from google.cloud import bigquery
import pandas as pd

client = bigquery.Client()
project = client.project
dataset = "ppp_rico"

def query_bq(sql):
    query_job = client.query(sql)
    results = query_job.result()
    return results.to_dataframe()

print("==================================================")
print("1. SEARCHING PROPERTIES AND ENTITIES IN v_rico_enterprise_master")
print("==================================================")

# Search SiteAddress/MailAddress for Gilbert or East
sql_properties = f"""
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleDate, LastSaleValue, clean_owner, ppp_borrower, ppp_city, ppp_state, ppp_amount
FROM `{project}.{dataset}.v_rico_enterprise_master`
WHERE 
  LOWER(SiteAddress) LIKE '%gilbert%' 
  OR LOWER(SiteAddress) LIKE '%east%'
  OR LOWER(MailAddress) LIKE '%gilbert%'
  OR LOWER(MailAddress) LIKE '%east%'
  OR LOWER(ppp_borrower) LIKE '%covenant%'
  OR LOWER(ppp_borrower) LIKE '%nunez%'
  OR LOWER(ppp_borrower) LIKE '%barnes%'
  OR LOWER(ppp_borrower) LIKE '%shea%'
"""
df_props = query_bq(sql_properties)
print(f"Found {len(df_props)} rows in v_rico_enterprise_master matching criteria:")
if len(df_props) > 0:
    print(df_props.to_string())
else:
    print("No rows found.")

print("\n==================================================")
print("2. SEARCHING IN regional_llcs")
print("==================================================")
sql_llcs = f"""
SELECT llc_name, property_address, city, state, ppp_amount, ppp_forgiven, status, source
FROM `{project}.{dataset}.regional_llcs`
WHERE 
  LOWER(property_address) LIKE '%gilbert%' 
  OR LOWER(property_address) LIKE '%east%'
  OR LOWER(llc_name) LIKE '%gilbert%'
  OR LOWER(llc_name) LIKE '%east%'
  OR LOWER(llc_name) LIKE '%covenant%'
"""
df_llcs = query_bq(sql_llcs)
print(f"Found {len(df_llcs)} rows in regional_llcs matching criteria:")
if len(df_llcs) > 0:
    print(df_llcs.to_string())
else:
    print("No rows found.")

print("\n==================================================")
print("3. INSPECTING city_cyber_recon")
print("==================================================")
sql_recon = f"""
SELECT domain, COUNT(*) as path_count, SUM(CAST(is_exposed AS INT64)) as exposed_count
FROM `{project}.{dataset}.city_cyber_recon`
GROUP BY domain
ORDER BY path_count DESC
"""
df_recon = query_bq(sql_recon)
print(f"Found {len(df_recon)} unique domains in city_cyber_recon:")
print(df_recon.head(30).to_string())
if len(df_recon) > 30:
    print(f"... and {len(df_recon) - 30} more domains.")
