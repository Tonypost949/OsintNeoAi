import os
from google.cloud import bigquery

GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"
BQ_DATASET = "national_audits"

def run_queries():
    client = bigquery.Client(project=GCP_PROJECT)
    
    # 1. Query for Mercy House files
    print("Querying for Mercy House files...")
    q1 = f"""
    SELECT file_name, mime_type, modified_time, web_view_link, owner_emails
    FROM `{GCP_PROJECT}.{BQ_DATASET}.drive_file_index`
    WHERE EXISTS (
      SELECT 1 FROM UNNEST(owner_emails) e
      WHERE e LIKE '%mercyhouse%'
    )
    ORDER BY modified_time DESC
    LIMIT 50
    """
    try:
        rows = list(client.query(q1).result())
        print(f"Found {len(rows)} Mercy House files:")
        for r in rows:
            print(f"- {r.file_name} (Owner: {r.owner_emails})")
            print(f"  Link: {r.web_view_link}")
    except Exception as e:
        print(f"Error querying Mercy House: {e}")
        
    # 2. Query for School District and Gov files
    print("\nQuerying for Government / School District files...")
    q2 = f"""
    SELECT file_name, mime_type, modified_time, web_view_link, owner_emails
    FROM `{GCP_PROJECT}.{BQ_DATASET}.drive_file_index`
    WHERE EXISTS (
      SELECT 1 FROM UNNEST(owner_emails) e
      WHERE e LIKE '%hbcsd.us%' OR e LIKE '%ivc.edu%' OR e LIKE '%pinalcounty%'
    )
    ORDER BY modified_time DESC
    LIMIT 50
    """
    try:
        rows = list(client.query(q2).result())
        print(f"Found {len(rows)} Gov/District files:")
        for r in rows:
            print(f"- {r.file_name} (Owner: {r.owner_emails})")
            print(f"  Link: {r.web_view_link}")
    except Exception as e:
        print(f"Error querying Gov/District: {e}")

if __name__ == "__main__":
    run_queries()
