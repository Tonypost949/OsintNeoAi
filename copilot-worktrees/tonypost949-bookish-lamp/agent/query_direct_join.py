from google.cloud import bigquery

GCP_PROJECT = "noble-beanbag-497411-m4"
client = bigquery.Client(project=GCP_PROJECT)

query = """
SELECT
    prop.Owner1 AS property_wrapper,
    prop.SiteAddress AS property_address,
    prop.LastSaleDate AS transfer_date,
    prop.LastSaleValue AS transfer_amount,
    bridge.entity_name AS ppp_entity,
    bridge.ppp_loan_1_amount AS loan_amount,
    bridge.ppp_loan_1_date AS ppp_loan_date,
    DATE_DIFF(SAFE.PARSE_DATE('%m/%d/%Y', prop.LastSaleDate), SAFE.PARSE_DATE('%m/%d/%Y', bridge.ppp_loan_1_date), DAY) AS days_delta
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs` prop
JOIN `noble-beanbag-497411-m4.forensic_layers.ppp_loans` bridge 
    ON UPPER(prop.Owner1) LIKE CONCAT('%', UPPER(bridge.entity_name), '%')
LIMIT 10
"""

print("Running direct join between hb_llcs and ppp_loans...")
try:
    query_job = client.query(query)
    results = list(query_job.result())
    print(f"Found {len(results)} direct join matches:")
    for row in results:
        print(f"Prop: {row.property_wrapper} | Entity: {row.ppp_entity} | Delta: {row.days_delta} days")
except Exception as e:
    print(f"Error: {e}")
