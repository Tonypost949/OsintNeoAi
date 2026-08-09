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
    print("Building regional LLCs table from PPP data...")
    
    # Target addresses pattern
    addresses = [
        "1111%STATE%COLLEGE",
        "17831%GOTHARD",
        "19744%BEACH",
        "1325%WESTERN", # Covenant House Hollywood
        "1091%BATAVIA", # Illumination Foundation Orange
        "7855%KATELLA"  # Illumination Stanton
    ]
    
    address_conditions = " OR ".join([f"UPPER(BorrowerAddress) LIKE '%{addr}%'" for addr in addresses])
    
    # 1. Create regional_llcs by combining ppp_150k_plus and ppp_up_to_150k
    create_llc_query = f"""
    CREATE OR REPLACE TABLE `{project_dataset}.regional_llcs` AS
    SELECT 
        BorrowerName AS llc_name,
        BorrowerAddress AS property_address,
        BorrowerCity AS city,
        BorrowerState AS state,
        InitialApprovalAmount AS ppp_amount,
        ForgivenessAmount AS ppp_forgiven,
        LoanStatus AS status,
        'PPP_Database' AS source
    FROM `{project_dataset}.ppp_150k_plus`
    WHERE {address_conditions}
    UNION ALL
    SELECT 
        BorrowerName AS llc_name,
        BorrowerAddress AS property_address,
        BorrowerCity AS city,
        BorrowerState AS state,
        InitialApprovalAmount AS ppp_amount,
        ForgivenessAmount AS ppp_forgiven,
        LoanStatus AS status,
        'PPP_Database' AS source
    FROM `{project_dataset}.ppp_up_to_150k`
    WHERE {address_conditions}
    """
    execute(create_llc_query)
    
    # 2. Query and print results to verify
    df = bq.query(f"SELECT * FROM `{project_dataset}.regional_llcs`").to_dataframe()
    print(f"Inserted {len(df)} regional LLCs/entities.")
    if len(df) > 0:
        print(df[['llc_name', 'property_address', 'ppp_amount']].head(20))

if __name__ == "__main__":
    main()
