from google.cloud import bigquery
import datetime

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

def check_history(table_name):
    print(f"\nChecking history for project-743aab84-f9a5-4ec7-954.national_audits.{table_name}:")
    for hours in [1, 4, 12, 24, 48, 72, 96, 120, 144, 160]:
        try:
            query = f"""
                SELECT COUNT(*) as count 
                FROM `project-743aab84-f9a5-4ec7-954.national_audits.{table_name}` 
                FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {hours} HOUR)
            """
            result = list(client.query(query).result())[0].count
            print(f"  - {hours} hours ago: {result} rows")
        except Exception as e:
            # Handle out of range time travel
            if "SYSTEM_TIME" in str(e) or "invalid" in str(e).lower():
                pass
            else:
                print(f"  - {hours} hours ago: Error ({e})")

check_history("gmail_index")
check_history("google_photos_index")
check_history("drive_file_index")

