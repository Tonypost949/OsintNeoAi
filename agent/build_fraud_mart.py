import os
from google.cloud import bigquery
from google.api_core.exceptions import Conflict

def main():
    gcp_project_id = "project-743aab84-f9a5-4ec7-954"
    client = bigquery.Client(project=gcp_project_id)

    # 1. Create dataset
    dataset_id = f"{gcp_project_id}.fraud_mart"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    try:
        client.create_dataset(dataset, timeout=30)
        print(f"Created dataset {dataset_id}")
    except Conflict:
        print(f"Dataset {dataset_id} already exists")

    queries = [
        ("fact_transactions", """
        CREATE OR REPLACE TABLE `project-743aab84-f9a5-4ec7-954.fraud_mart.fact_transactions` AS
        SELECT
          GENERATE_UUID() AS transaction_id,
          base.state,
          npi.organization_name,
          npi.cms_billing_code,
          SAFE_CAST(npi.unaccounted_fund_delta AS NUMERIC) AS fund_delta,
          CURRENT_TIMESTAMP() AS ingestion_ts
        FROM
          `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records` base
        CROSS JOIN
          UNNEST(base.non_profiteers_index) AS npi;
        """),
        
        ("dim_organization", """
        CREATE OR REPLACE TABLE `project-743aab84-f9a5-4ec7-954.fraud_mart.dim_organization` AS
        SELECT DISTINCT
          FARM_FINGERPRINT(LOWER(organization_name)) AS org_id,
          organization_name,
          LOWER(organization_name) AS normalized_name
        FROM `project-743aab84-f9a5-4ec7-954.fraud_mart.fact_transactions`
        WHERE organization_name IS NOT NULL;
        """),

        ("dim_indicator", """
        CREATE OR REPLACE TABLE `project-743aab84-f9a5-4ec7-954.fraud_mart.dim_indicator` AS
        SELECT 'international' AS indicator UNION ALL
        SELECT 'foreign' UNION ALL
        SELECT 'remit' UNION ALL
        SELECT 'philippines' UNION ALL
        SELECT 'manila' UNION ALL
        SELECT 'land restriction' UNION ALL
        SELECT 'deed restriction' UNION ALL
        SELECT 'no further action';
        """),

        ("bridge_org_indicator", """
        CREATE OR REPLACE TABLE `project-743aab84-f9a5-4ec7-954.fraud_mart.bridge_org_indicator` AS
        SELECT
          FARM_FINGERPRINT(LOWER(organization_name)) AS org_id,
          indicator
        FROM `project-743aab84-f9a5-4ec7-954.fraud_mart.fact_transactions`,
        UNNEST(
          REGEXP_EXTRACT_ALL(
            LOWER(organization_name),
            r'(remit|foreign|international|philippines|manila|land restriction|deed restriction|no further action)'
          )
        ) AS indicator
        WHERE organization_name IS NOT NULL;
        """),

        ("vw_features", """
        CREATE OR REPLACE VIEW `project-743aab84-f9a5-4ec7-954.fraud_mart.vw_features` AS
        SELECT
          f.transaction_id,
          f.state,
          f.fund_delta,

          COUNTIF(b.indicator = 'international') AS international_hits,
          COUNTIF(b.indicator = 'philippines') AS philippines_hits,
          COUNTIF(b.indicator = 'manila') AS manila_hits,
          COUNTIF(b.indicator = 'remit') AS remit_hits,
          COUNTIF(b.indicator = 'land restriction') AS land_flags,
          COUNTIF(b.indicator = 'no further action') AS admin_flags

        FROM `project-743aab84-f9a5-4ec7-954.fraud_mart.fact_transactions` f
        LEFT JOIN `project-743aab84-f9a5-4ec7-954.fraud_mart.bridge_org_indicator` b
          ON FARM_FINGERPRINT(LOWER(f.organization_name)) = b.org_id
        GROUP BY 1,2,3;
        """),

        ("fraud_anomaly_model", """
        CREATE OR REPLACE MODEL `project-743aab84-f9a5-4ec7-954.fraud_mart.fraud_anomaly_model`
        OPTIONS(
          MODEL_TYPE = 'KMEANS',
          NUM_CLUSTERS = 2
        ) AS
        SELECT
          IFNULL(fund_delta, 0) AS fund_delta,
          international_hits,
          remit_hits,
          land_flags
        FROM `project-743aab84-f9a5-4ec7-954.fraud_mart.vw_features`;
        """),
        
        ("fraud_scores", """
        CREATE OR REPLACE TABLE `project-743aab84-f9a5-4ec7-954.fraud_mart.fraud_scores` AS
        SELECT
          *
        FROM
          ML.PREDICT(MODEL `project-743aab84-f9a5-4ec7-954.fraud_mart.fraud_anomaly_model`,
            TABLE `project-743aab84-f9a5-4ec7-954.fraud_mart.vw_features`);
        """)
    ]

    for name, sql in queries:
        print(f"[*] Executing {name}...")
        try:
            job = client.query(sql)
            job.result()
            print(f"[+] Successfully executed {name}")
        except Exception as e:
            print(f"[-] Error executing {name}: {e}")

if __name__ == "__main__":
    main()
