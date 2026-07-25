
from google.cloud import bigquery

# A general query to sample organization names from the table.
sql_query = """
SELECT 
    t.state,
    npi.organization_name,
    npi.unaccounted_fund_delta
FROM 
    `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records` AS t,
    UNNEST(t.non_profiteers_index) as npi
WHERE
    npi.organization_name IS NOT NULL
ORDER BY 
    t.state
LIMIT 100;
"""

def execute_query():
    """Executes the BigQuery script and prints the results."""
    try:
        client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
        query_job = client.query(sql_query)  # API request

        print("Executing query to sample organization names...")
        results = query_job.result()  # Waits for job to complete

        print("-" * 80)
        print(f"{'State':<5} | {'Organization Name':<80} | {'Unaccounted Delta':>20}")
        print("-" * 80)

        for row in results:
            # Ensure organization_name is not None before trying to format it
            org_name = row.organization_name or "N/A"
            print(f"{row.state:<5} | {org_name:<80} | {row.unaccounted_fund_delta:>20}")
        
        print("-" * 80)
        print("Sample query finished.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    execute_query()
