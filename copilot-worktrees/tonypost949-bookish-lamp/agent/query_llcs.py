from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

query = """
SELECT llc_name, principal_address, mailing_address, agent_of_service 
FROM `noble-beanbag-497411-m4.forensic_layers.hb_llcs` 
WHERE UPPER(mailing_address) LIKE '%9874 RARITAN%' 
   OR UPPER(principal_address) LIKE '%20951 BROOKHURST%'
   OR UPPER(principal_address) LIKE '%20951 BROOKHURST%';
"""

try:
    query_job = client.query(query)
    results = query_job.result()
    
    count = 0
    for row in results:
        count += 1
        print(f"LLC Name: {row.llc_name}")
        print(f"Principal Address: {row.principal_address}")
        print(f"Mailing Address: {row.mailing_address}")
        print(f"Agent of Service: {row.agent_of_service}")
        print("-" * 40)
    
    print(f"Total found: {count}")
except Exception as e:
    print(f"Error: {e}")
