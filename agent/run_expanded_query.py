import os
from google.cloud import bigquery

def main():
    gcp_project_id = "project-743aab84-f9a5-4ec7-954"
    client = bigquery.Client(project=gcp_project_id)
    
    # Corrected state_code to state to match schema, and implemented the user's upgraded multi-label extraction architecture.
    query = """
    WITH keyword_map AS (
      SELECT r'(remit|overseas|foreign|international|philippines|manila)' AS pattern, 'international_flag' AS category
      UNION ALL
      SELECT r'(no further action|land restriction|deed restriction)', 'regulatory_flag'
    ),

    cleaned_data AS (
      SELECT
        base_records.state,
        LOWER(IFNULL(npi.organization_name, '')) AS org_name,
        npi.organization_name,
        npi.cms_billing_code,
        SAFE_CAST(npi.unaccounted_fund_delta AS NUMERIC) AS fund_delta
      FROM
        `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records` AS base_records
      CROSS JOIN
        UNNEST(base_records.non_profiteers_index) AS npi
    ),

    matched AS (
      SELECT
        c.*,
        k.category,
        REGEXP_EXTRACT_ALL(c.org_name, k.pattern) AS matches
      FROM cleaned_data c
      JOIN keyword_map k
      ON REGEXP_CONTAINS(c.org_name, k.pattern)
    )

    SELECT
      state,
      organization_name,
      cms_billing_code,
      fund_delta,
      category,
      match AS analytical_indicator
    FROM matched,
    UNNEST(matches) AS match
    ORDER BY fund_delta DESC;
    """
    
    print("[*] Running user's upgraded production query (with state_code -> state correction)...")
    try:
        query_job = client.query(query)
        results = query_job.result()
        print("[+] Query completed successfully!")
        
        rows = list(results)
        print(f"[+] Retrieved {len(rows)} matching rows:")
        for idx, row in enumerate(rows[:20]):
            print(f" {idx+1}. State: {row.state} | Org: {row.organization_name} | Billing Code: {row.cms_billing_code} | Fund Delta: {row.fund_delta} | Category: {row.category} | Indicator: {row.analytical_indicator}")
        
        # Save results to a CSV in the workspace
        import csv
        csv_path = "expanded_query_results.csv"
        with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["state", "organization_name", "cms_billing_code", "fund_delta", "category", "analytical_indicator"])
            for row in rows:
                writer.writerow([row.state, row.organization_name, row.cms_billing_code, row.fund_delta, row.category, row.analytical_indicator])
        print(f"[+] Saved results to {csv_path}")
        
        # Update/create the view in BigQuery
        view_ddl = f"""
        CREATE OR REPLACE VIEW `project-743aab84-f9a5-4ec7-954.forensic_layers.v_expanded_structural_audit` AS
        {query}
        """
        print("[*] Materializing upgraded query as view: `project-743aab84-f9a5-4ec7-954.forensic_layers.v_expanded_structural_audit`...")
        client.query(view_ddl).result()
        print("[+] View created/updated successfully in BigQuery!")
        
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    main()
