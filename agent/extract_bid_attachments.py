import zipfile
import pypdf
import os
from google.cloud import bigquery
import pandas as pd

def extract_and_load_all_attachments():
    zip_path = r"C:\Users\HP\Downloads\purchase_and_delivery_of_ammunition-2026-07-01-07-23-50.zip"
    extract_dir = "extracted_bid_attachments"
    
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
        
    print("Unzipping bid attachments archive...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print("Successfully extracted zip contents.")
    except Exception as e:
        print(f"Error unzipping files: {e}")
        return
        
    parsed_docs = []
    for file_name in os.listdir(extract_dir):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(extract_dir, file_name)
            print(f"Extracting text from attachment document: {file_name}")
            pdf_text = ""
            try:
                reader = pypdf.PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    pdf_text += f"\n--- Page {i+1} ---\n" + page.extract_text()
                
                parsed_docs.append({
                    "attachment_name": file_name,
                    "attachment_text": pdf_text,
                    "file_size_bytes": os.path.getsize(file_path)
                })
                print("Extracted text successfully.")
            except Exception as e:
                print(f"Error reading PDF {file_name}: {e}")
                
    if not parsed_docs:
        print("No PDF attachments found to load.")
        return
        
    df = pd.DataFrame(parsed_docs)
    
    bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
    table_id = "project-743aab84-f9a5-4ec7-954.orange_county_procurement.oc_ammunition_attachments_text"
    
    print(f"Loading extracted document text into BigQuery table {table_id}...")
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )
    job = bq.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print("Successfully loaded all attachment document text into BigQuery.")

if __name__ == "__main__":
    extract_and_load_all_attachments()
