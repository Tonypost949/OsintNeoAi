import os
from google.cloud import bigquery

GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"
BQ_DATASET = "national_audits"

def check_counts():
    try:
        client = bigquery.Client(project=GCP_PROJECT)
        
        # Check Gmail
        try:
            gmail_query = f"SELECT COUNT(*) as count FROM `{GCP_PROJECT}.{BQ_DATASET}.gmail_index`"
            gmail_job = client.query(gmail_query)
            gmail_count = list(gmail_job.result())[0].count
            print(f"Gmail Total: {gmail_count}")
        except Exception as e:
            print(f"Error checking Gmail: {e}")

        # Check Photos
        try:
            photos_query = f"SELECT COUNT(*) as count FROM `{GCP_PROJECT}.{BQ_DATASET}.google_photos_index`"
            photos_job = client.query(photos_query)
            photos_count = list(photos_job.result())[0].count
            print(f"Photos Total: {photos_count}")
        except Exception as e:
            print(f"Error checking Photos: {e}")

        # Check Drive
        try:
            drive_query = f"SELECT COUNT(*) as count FROM `{GCP_PROJECT}.{BQ_DATASET}.drive_file_index`"
            drive_job = client.query(drive_query)
            drive_count = list(drive_job.result())[0].count
            print(f"Drive Files Total: {drive_count}")
        except Exception as e:
            print(f"Error checking Drive: {e}")

        # Check Drive Photos EXIF
        try:
            exif_query = f"SELECT COUNT(*) as count FROM `{GCP_PROJECT}.{BQ_DATASET}.drive_photos_exif`"
            exif_job = client.query(exif_query)
            exif_count = list(exif_job.result())[0].count
            print(f"Drive Photos EXIF Total: {exif_count}")
        except Exception as e:
            print(f"Error checking EXIF Photos: {e}")

    except Exception as e:
        print(f"Error checking counts: {e}")

if __name__ == "__main__":
    check_counts()

