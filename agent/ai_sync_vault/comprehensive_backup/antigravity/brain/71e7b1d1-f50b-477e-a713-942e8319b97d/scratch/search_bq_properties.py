from google.cloud import bigquery
import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
output_file = os.path.join(scratch_dir, "bq_property_search_results.txt")

client = bigquery.Client()
project = client.project
dataset = "ppp_rico"

with open(output_file, "w", encoding="utf-8") as out:
    out.write("BigQuery Property and Entity Search Results\n")
    out.write("===========================================\n\n")
    
    # 1. Search v_rico_enterprise_master
    out.write("--- 1. Search v_rico_enterprise_master ---\n")
    sql_master = f"""
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
      OR LOWER(Owner1) LIKE '%gilbert%'
      OR LOWER(Owner2) LIKE '%gilbert%'
      OR LastSaleValue = 685000
    """
    try:
        query_job = client.query(sql_master)
        results = list(query_job.result())
        out.write(f"Found {len(results)} rows.\n")
        for row in results:
            out.write(f"Row: {dict(row)}\n")
    except Exception as e:
        out.write(f"Error querying v_rico_enterprise_master: {str(e)}\n")
        
    # 2. Search regional_llcs
    out.write("\n--- 2. Search regional_llcs ---\n")
    sql_llcs = f"""
    SELECT llc_name, property_address, city, state, ppp_amount, ppp_forgiven, status, source
    FROM `{project}.{dataset}.regional_llcs`
    WHERE 
      LOWER(property_address) LIKE '%gilbert%' 
      OR LOWER(property_address) LIKE '%east%'
      OR LOWER(llc_name) LIKE '%gilbert%'
      OR LOWER(llc_name) LIKE '%east%'
      OR LOWER(llc_name) LIKE '%covenant%'
      OR ppp_amount = 685000
    """
    try:
        query_job = client.query(sql_llcs)
        results = list(query_job.result())
        out.write(f"Found {len(results)} rows.\n")
        for row in results:
            out.write(f"Row: {dict(row)}\n")
    except Exception as e:
        out.write(f"Error querying regional_llcs: {str(e)}\n")

print(f"Done! Results written to {output_file}")
