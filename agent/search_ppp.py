from google.cloud import bigquery

GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"
client = bigquery.Client(project=GCP_PROJECT)

query = """
SELECT BorrowerName, CurrentApprovalAmount, DateApproved, OriginatingLender
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%360 CLINIC%' 
   OR UPPER(BorrowerName) LIKE '%2T MEDIA%' 
   OR UPPER(BorrowerName) LIKE '%TAM NGUYEN%'
LIMIT 10
"""

print("Searching ppp_150k_plus for target entities...")
try:
    query_job = client.query(query)
    results = list(query_job.result())
    print(f"Found {len(results)} matches:")
    for row in results:
        print(f"Name: {row.BorrowerName} | Amount: ${row.CurrentApprovalAmount:,.2f} | Date: {row.DateApproved} | Lender: {row.OriginatingLender}")
except Exception as e:
    print(f"Error: {e}")
