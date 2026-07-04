import json
import os
import re
import requests
from bs4 import BeautifulSoup
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

def process_datasets():
    """
    Processes a list of dataset URLs from a file, downloads the data,
    and uploads it to BigQuery.
    """
    successful_uploads = []
    failed_uploads = []

    # Get the directory of the current script to build absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    urls_file_path = os.path.join(script_dir, 'dataset_urls.txt')
    downloads_dir = os.path.join(script_dir, 'downloads')

    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)

    try:
        with open(urls_file_path, 'r') as f:
            data = json.load(f)
            urls = data.get('dataset_urls', [])
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing dataset_urls.txt: {e}")
        return

    if not urls:
        print("No URLs found in dataset_urls.txt")
        return

    # Initialize BigQuery client
    try:
        bq_client = bigquery.Client()
    except Exception as e:
        print(f"Failed to initialize BigQuery client: {e}")
        print("Please ensure you have authenticated with Google Cloud and the BigQuery API is enabled.")
        return

    dataset_id = "data_gov_imports"
    try:
        bq_client.get_dataset(dataset_id)
    except NotFound:
        try:
            bq_client.create_dataset(dataset_id)
            print(f"Created BigQuery dataset: {dataset_id}")
        except Exception as e:
            print(f"Failed to create BigQuery dataset {dataset_id}: {e}")
            return


    for i, url in enumerate(urls):
        print(f"Processing URL {i+1}/{len(urls)}: {url}")
        try:
            # Fetch page content
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find download link
            download_link = None
            for a in soup.find_all('a', href=True):
                if any(ext in a.text.lower() for ext in ['csv', 'json']):
                    download_link = a['href']
                    if not download_link.startswith('http'):
                        # Handle relative URLs if necessary
                        from urllib.parse import urljoin
                        download_link = urljoin(url, download_link)
                    break
            
            if not download_link:
                print("No CSV or JSON download link found.")
                failed_uploads.append((url, "No download link found"))
                continue

            # Download the data
            file_response = requests.get(download_link, timeout=60)
            file_response.raise_for_status()

            # Get title and sanitize for table name
            title = soup.find('h1').text.strip()
            table_name = re.sub(r'[^a-zA-Z0-9]+', '_', title).lower()
            table_id = f"{dataset_id}.{table_name}"
            
            # Save file locally
            file_extension = 'csv' if 'csv' in download_link.lower() else 'json'
            local_file_path = os.path.join(downloads_dir, f"{table_name}.{file_extension}")
            with open(local_file_path, 'wb') as f:
                f.write(file_response.content)


            # Upload to BigQuery
            job_config = bigquery.LoadJobConfig(
                autodetect=True,
                source_format=bigquery.SourceFormat.CSV if file_extension == 'csv' else bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )
            
            with open(local_file_path, "rb") as source_file:
                job = bq_client.load_table_from_file(source_file, table_id, job_config=job_config)

            job.result()  # Wait for the job to complete.
            
            print(f"Successfully uploaded data to BigQuery table: {table_id}")
            successful_uploads.append(url)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {url}: {e}")
            failed_uploads.append((url, str(e)))
        except Exception as e:
            print(f"An unexpected error occurred for {url}: {e}")
            failed_uploads.append((url, str(e)))

    print("
--- Summary ---")
    print(f"Successfully uploaded: {len(successful_uploads)}")
    for url in successful_uploads:
        print(f"  - {url}")
    
    print(f"
Failed to upload: {len(failed_uploads)}")
    for url, reason in failed_uploads:
        print(f"  - {url} (Reason: {reason})")

if __name__ == '__main__':
    process_datasets()
