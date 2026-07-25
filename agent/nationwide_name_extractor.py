import csv
from google.cloud import bigquery

OUTPUT_CSV = 'NATIONWIDE_INDIVIDUAL_TARGETS.csv'

def extract_nationwide_names():
    print("Querying BigQuery for nationwide individual targets (Independent Contractors, Sole Proprietors, Self-Employed) at high-density addresses...")
    client = bigquery.Client()

    # Query specifically for business types that use human names as the borrower name,
    # where multiple individuals are registered at the exact same address (>= 5 individuals).
    # This targets the "ghost employee" and "stolen identity" PPP rings nationwide.
    query = """
    SELECT 
        BorrowerName, 
        BorrowerAddress, 
        BorrowerCity, 
        BorrowerState, 
        BusinessType,
        COUNT(*) OVER(PARTITION BY BorrowerAddress) as cluster_size
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
    WHERE BusinessType IN ('Independent Contractors', 'Sole Proprietorship', 'Self-Employed Individuals')
      AND BorrowerAddress IS NOT NULL AND BorrowerAddress != ''
    """

    # We use a subquery to filter the window function results
    full_query = f"""
    WITH Clusters AS (
        {query}
    )
    SELECT * FROM Clusters
    WHERE cluster_size >= 10
    LIMIT 20000
    """

    data_rows = []
    names_set = set()

    try:
        query_job = client.query(full_query)
        results = query_job.result()
        for row in results:
            b_name = str(row['BorrowerName']).upper().strip()
            
            # Additional safety filter for non-human names
            if len(b_name) > 3 and not any(b_name.endswith(x) for x in [' LLC', ' INC', ' CORP', ' CO', ' INC.', ' L.L.C.', ' LLC.', ' COMPANY']):
                if b_name not in names_set:
                    names_set.add(b_name)
                    context = f"Fraud Ring Cluster of {row['cluster_size']} at {row['BorrowerAddress']}, {row['BorrowerCity']} {row['BorrowerState']} ({row['BusinessType']})"
                    data_rows.append({"Name": b_name, "Source": "BigQuery: PPP Nationwide Sweep", "Context": context})
    except Exception as e:
        print(f"BigQuery error: {e}")
        return

    print(f"Writing {len(data_rows)} names to {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Source", "Context"])
        writer.writeheader()
        writer.writerows(data_rows)

    print("Done!")

if __name__ == "__main__":
    extract_nationwide_names()
