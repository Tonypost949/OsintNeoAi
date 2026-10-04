from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

restore_query = """
    CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.national_audits.gmail_index` AS 
    SELECT * 
    FROM `noble-beanbag-497411-m4.national_audits.gmail_index` 
    FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 48 HOUR)
"""

try:
    print("Attempting to restore gmail_index to its state 48 hours ago...")
    query_job = client.query(restore_query)
    query_job.result()
    print("Successfully restored!")
    
    # Verify count
    count_job = client.query("SELECT COUNT(*) as count FROM `noble-beanbag-497411-m4.national_audits.gmail_index`")
    count = list(count_job.result())[0].count
    print(f"Current rows in gmail_index: {count}")
except Exception as e:
    print(f"Error restoring table: {e}")
