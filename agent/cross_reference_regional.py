import pandas as pd
from google.cloud import bigquery

bq = bigquery.Client()
project_dataset = 'project-743aab84-f9a5-4ec7-954.ppp_rico'

def execute(query):
    print(f"Executing: {query[:100]}...")
    job = bq.query(query)
    job.result() # Wait for job to complete
    print("Done.")

def main():
    print("Cross-referencing Regional LLCs with Property Database...")
    
    # 1. Create a joined view matching regional LLC names with the master property records
    create_master_query = f"""
    CREATE OR REPLACE TABLE `{project_dataset}.v_regional_enterprise_master` AS
    SELECT 
        l.llc_name AS ppp_borrower_name,
        l.ppp_amount,
        l.ppp_forgiven,
        l.status AS ppp_status,
        l.property_address AS ppp_address,
        p.SiteAddress AS owned_property_address,
        p.MailAddress AS property_mail_address,
        p.LastSaleValue AS property_value,
        p.APN,
        p.clean_owner
    FROM `{project_dataset}.regional_llcs` l
    LEFT JOIN `{project_dataset}.v_rico_enterprise_master` p
      ON UPPER(l.llc_name) = UPPER(p.clean_owner)
      OR UPPER(l.property_address) = UPPER(p.MailAddress)
    """
    execute(create_master_query)
    
    # 2. Query and print the matches
    df = bq.query(f"SELECT * FROM `{project_dataset}.v_regional_enterprise_master` WHERE owned_property_address IS NOT NULL").to_dataframe()
    print(f"Found {len(df)} cross-referenced real estate matches for the regional LLCs.")
    if len(df) > 0:
        print(df[['ppp_borrower_name', 'owned_property_address', 'property_value']].head(20))

if __name__ == "__main__":
    main()
