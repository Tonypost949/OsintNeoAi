from google.cloud import bigquery
import os
import json

os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\HP\AppData\Roaming\gcloud\legacy_credentials\txtdjdrop@gmail.com\adc.json"
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=== SEARCHING GEOGRAPHIC VICINITY IN HB_LLCS ===")

# Query for Beach Blvd (in the 17000-18000 block), Slater Ave, and Cameron Ln
query = f"""
SELECT APN, Owner1, Owner2, SiteAddress, MailAddress, MailCity,
       LastSaleDate, LastSaleValue
FROM `{PRJ}.ppp_rico.hb_llcs`
WHERE (
    UPPER(SiteAddress) LIKE '%CAMERON%'
    OR (UPPER(SiteAddress) LIKE '%BEACH%' AND (
        SiteAddress LIKE '%175%' OR SiteAddress LIKE '%176%' OR SiteAddress LIKE '%177%' 
        OR SiteAddress LIKE '%174%' OR SiteAddress LIKE '%178%'
    ))
    OR (UPPER(SiteAddress) LIKE '%SLATER%' AND (
        SiteAddress LIKE '%78%' OR SiteAddress LIKE '%79%' OR SiteAddress LIKE '%80%'
        OR SiteAddress LIKE '%77%' OR SiteAddress LIKE '%81%'
    ))
)
ORDER BY SiteAddress
"""

try:
    results = []
    query_job = client.query(query)
    for r in query_job.result():
        results.append(dict(r))
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "radius_raw_data.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
        
    print(f"Successfully exported {len(results)} matching properties in vicinity.")
except Exception as e:
    print(f"Error querying BigQuery: {e}")
