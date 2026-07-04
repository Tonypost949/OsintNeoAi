import zipfile
import pypdf
import os
from google.cloud import bigquery
import pandas as pd

def ingest_ammunition_bid():
    pdf_path = r"C:\Users\HP\Downloads\Purchase_and_Delivery_of_Ammunition.pdf"
    zip_path = r"C:\Users\HP\Downloads\purchase_and_delivery_of_ammunition-2026-07-01-07-23-50.zip"
    
    print("Parsing Purchase_and_Delivery_of_Ammunition.pdf...")
    pdf_text = ""
    try:
        reader = pypdf.PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            pdf_text += f"\n--- Page {i+1} ---\n" + page.extract_text()
        print(f"Extracted {len(pdf_text)} characters from PDF.")
    except Exception as e:
        print(f"Error reading PDF: {e}")
        
    print("Reading zip attachments...")
    zip_contents = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                zip_contents.append(f"{file_info.filename} ({file_info.file_size} bytes)")
        print(f"Found {len(zip_contents)} attachment files inside ZIP.")
    except Exception as e:
        print(f"Error reading ZIP: {e}")
        
    records = [{
        "bid_name": "Purchase and Delivery of Ammunition",
        "bid_pdf_text": pdf_text if pdf_text else "Error reading PDF",
        "attachments_list": ", ".join(zip_contents) if zip_contents else "None",
        "source_folder": "Downloads"
    }]
    
    df = pd.DataFrame(records)
    
    bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
    table_id = "project-743aab84-f9a5-4ec7-954.unclaimed_property.oc_ammunition_bids"
    
    print(f"Loading ammunition bid data into BigQuery table {table_id}...")
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )
    
    job = bq.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print("Successfully loaded Ammunition Bid and Attachments into BigQuery!")

if __name__ == "__main__":
    ingest_ammunition_bid()
