from google.cloud import bigquery

GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"
client = bigquery.Client(project=GCP_PROJECT)

query = """
SELECT clean_owner, ppp_borrower, SiteAddress, ppp_amount, ppp_date, lender, rico_risk_tier
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.v_rico_enterprise_master`
WHERE UPPER(clean_owner) LIKE '%360 CLINIC%' 
   OR UPPER(clean_owner) LIKE '%2T MEDIA%' 
   OR UPPER(clean_owner) LIKE '%TAM NGUYEN%'
   OR UPPER(ppp_borrower) LIKE '%360 CLINIC%' 
   OR UPPER(ppp_borrower) LIKE '%2T MEDIA%' 
   OR UPPER(ppp_borrower) LIKE '%TAM NGUYEN%'
LIMIT 20
"""

print("Querying v_rico_enterprise_master for target entities...")
try:
    query_job = client.query(query)
    results = list(query_job.result())
    print(f"\nFound {len(results)} matches in Master Enterprise View:\n")
    print(f"{'Clean Owner':<25} | {'PPP Borrower':<25} | {'Site Address':<30} | {'Amount':<12} | {'Risk Tier'}")
    print("-" * 110)
    for row in results:
        amt = row.ppp_amount if row.ppp_amount else 0
        print(f"{str(row.clean_owner):<25} | {str(row.ppp_borrower):<25} | {str(row.SiteAddress):<30} | ${amt:,.2f} | {row.rico_risk_tier}")
except Exception as e:
    print(f"Error querying Master Enterprise View: {e}")
