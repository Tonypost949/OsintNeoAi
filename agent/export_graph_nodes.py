import os
from google.cloud import bigquery
import csv

def main():
    gcp_project_id = "project-743aab84-f9a5-4ec7-954"
    client = bigquery.Client(project=gcp_project_id)
    
    exports = [
        ("neo4j_nodes_org.csv", """
        SELECT DISTINCT
          FARM_FINGERPRINT(LOWER(organization_name)) AS id,
          organization_name AS name,
          'Organization' AS label
        FROM `project-743aab84-f9a5-4ec7-954.fraud_mart.fact_transactions`
        WHERE organization_name IS NOT NULL;
        """),
        
        ("neo4j_edges_indicator.csv", """
        SELECT
          org_id AS source,
          indicator AS target,
          'HAS_INDICATOR' AS relationship
        FROM `project-743aab84-f9a5-4ec7-954.fraud_mart.bridge_org_indicator`
        WHERE org_id IS NOT NULL;
        """),
        
        ("neo4j_edges_high_risk.csv", """
        SELECT
          transaction_id AS source,
          'HIGH_RISK' AS target,
          NEAREST_CENTROIDS_DISTANCE[OFFSET(0)].DISTANCE AS fraud_distance
        FROM `project-743aab84-f9a5-4ec7-954.fraud_mart.fraud_scores`
        WHERE NEAREST_CENTROIDS_DISTANCE[OFFSET(0)].DISTANCE > 0.0;
        """)
    ]

    print("[*] Exporting Neo4j Graph Data...")
    for filename, sql in exports:
        print(f"[*] Extracting to {filename}...")
        try:
            job = client.query(sql)
            rows = list(job.result())
            if not rows:
                print(f"[-] No data found for {filename}")
                continue
                
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(rows[0].keys())
                # Write data
                for row in rows:
                    writer.writerow(row.values())
            print(f"[+] Successfully exported {len(rows)} records to {filename}")
        except Exception as e:
            print(f"[-] Error exporting {filename}: {e}")

if __name__ == "__main__":
    main()
