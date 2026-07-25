from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

# Query 1: Create and seed the Entity Resolution table
ddl1 = """
CREATE OR REPLACE TABLE `project-743aab84-f9a5-4ec7-954.forensic_layers.entity_resolution` (
    canonical_id STRING,
    raw_name_variant STRING,
    resolved_group STRING,
    associated_ein STRING
);
"""

insert_sql = """
INSERT INTO `project-743aab84-f9a5-4ec7-954.forensic_layers.entity_resolution` (canonical_id, raw_name_variant, resolved_group, associated_ein)
VALUES 
    ('ENT-NGUYEN-TAM', 'TAM NGUYEN', 'TAM NGUYEN NETWORK', NULL),
    ('ENT-NGUYEN-TAM', 'NGUYEN, TAM', 'TAM NGUYEN NETWORK', NULL),
    ('ENT-360CLINIC', '360 CLINIC', '360 CLINIC NETWORK', NULL),
    ('ENT-360CLINIC', '360 COVID CLINIC', '360 CLINIC NETWORK', NULL),
    ('ENT-360CLINIC', 'MD24 CA, INC.', '360 CLINIC NETWORK', NULL),
    ('ENT-2TMEDIA', '2T MEDIA', '2T MEDIA GROUP', NULL),
    ('ENT-2TMEDIA', '2T MEDIA LLC', '2T MEDIA GROUP', NULL),
    ('ENT-PHAM-PETER', 'PETER PHAM', 'PETER PHAM NETWORK', NULL),
    ('ENT-PHAM-PETER', 'PETER ANH PHAM', 'PETER PHAM NETWORK', NULL),
    ('ENT-PHAM-PETER', 'CP PREMIER CAPITAL LLC', 'PETER PHAM NETWORK', NULL);
"""

# Query 2: Create the Property Timing View (corrected to map ppp_loans table schema)
ddl2 = """
CREATE OR REPLACE VIEW `project-743aab84-f9a5-4ec7-954.forensic_layers.ppp_property_timing` AS
SELECT
    er.resolved_group AS entity_identity,
    prop.Owner1 AS property_wrapper,
    prop.SiteAddress AS property_address,
    prop.LastSaleDate AS transfer_date,
    prop.LastSaleValue AS transfer_amount,
    bridge.ppp_loan_1_amount AS loan_amount,
    bridge.ppp_loan_1_date AS ppp_loan_date,
    DATE_DIFF(SAFE.PARSE_DATE('%m/%d/%Y', prop.LastSaleDate), SAFE.PARSE_DATE('%m/%d/%Y', bridge.ppp_loan_1_date), DAY) AS days_delta
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs` prop
JOIN `project-743aab84-f9a5-4ec7-954.forensic_layers.ppp_loans` bridge 
    ON UPPER(prop.Owner1) LIKE CONCAT('%', UPPER(bridge.entity_name), '%')
JOIN `project-743aab84-f9a5-4ec7-954.forensic_layers.entity_resolution` er 
    ON UPPER(bridge.entity_name) LIKE CONCAT('%', UPPER(er.raw_name_variant), '%')
WHERE prop.LastSaleValue = 0 
  AND ABS(DATE_DIFF(SAFE.PARSE_DATE('%m/%d/%Y', prop.LastSaleDate), SAFE.PARSE_DATE('%m/%d/%Y', bridge.ppp_loan_1_date), DAY)) <= 180;
"""

def run_query(sql, description):
    print(f"Running: {description}...")
    try:
        query_job = client.query(sql)
        query_job.result()  # Wait for query to complete
        print(f"SUCCESS: Successfully executed: {description}\n")
    except Exception as e:
        print(f"ERROR: Error executing {description}: {e}\n")

if __name__ == "__main__":
    run_query(ddl1, "Create entity_resolution table")
    run_query(insert_sql, "Seed entity_resolution table data")
    run_query(ddl2, "Create ppp_property_timing view")
