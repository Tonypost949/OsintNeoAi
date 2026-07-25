from google.cloud import bigquery

GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"
client = bigquery.Client(project=GCP_PROJECT)

query = """
SELECT entity_identity, property_wrapper, property_address, transfer_date, transfer_amount, loan_amount, ppp_loan_date, days_delta
FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.ppp_property_timing`
ORDER BY ABS(days_delta) ASC
LIMIT 50
"""

print("Running cross-join analysis on ppp_property_timing view...")
try:
    query_job = client.query(query)
    results = list(query_job.result())
    print(f"\nFound {len(results)} matching timing correlations:\n")
    print(f"{'Entity':<25} | {'Property Wrapper':<30} | {'Address':<25} | {'Days Delta':<10} | {'Loan Amt':<12}")
    print("-" * 110)
    for row in results:
        print(f"{row.entity_identity:<25} | {row.property_wrapper[:30]:<30} | {row.property_address[:25]:<25} | {row.days_delta:<10} | ${row.loan_amount:,.2f}")
except Exception as e:
    print(f"Error querying ppp_property_timing view: {e}")
