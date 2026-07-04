from google.cloud import bigquery

def main():
    gcp_project_id = "project-743aab84-f9a5-4ec7-954"
    client = bigquery.Client(project=gcp_project_id)
    
    query = """
    SELECT 
        base_records.state,
        npi.organization_name,
        npi.unaccounted_fund_delta
    FROM 
        `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records` AS base_records,
        UNNEST(base_records.non_profiteers_index) AS npi
    LIMIT 100;
    """
    
    try:
        results = client.query(query).result()
        for idx, row in enumerate(results):
            print(f"{idx+1}. State: {row.state} | Org: {row.organization_name} | Fund Delta: {row.unaccounted_fund_delta}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
