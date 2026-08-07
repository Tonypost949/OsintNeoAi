from google.cloud import bigquery
import pandas as pd

def separate_datasets():
    bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
    P = "project-743aab84-f9a5-4ec7-954"
    
    # 1. Create a dedicated Orange County Procurement dataset
    new_dataset_id = f"{P}.orange_county_procurement"
    print(f"Creating new dataset: {new_dataset_id}...")
    dataset = bigquery.Dataset(new_dataset_id)
    dataset.location = "US"
    
    try:
        dataset = bq.create_dataset(dataset, exists_ok=True)
        print("Successfully created dataset orange_county_procurement.")
    except Exception as e:
        print(f"Error creating dataset: {e}")
        
    # 2. Migration: Copy data from unclaimed_property.oc_ammunition_bids to orange_county_procurement.oc_ammunition_bids
    src_table = f"{P}.unclaimed_property.oc_ammunition_bids"
    dest_table = f"{P}.orange_county_procurement.oc_ammunition_bids"
    
    print(f"Migrating table data from {src_table} to {dest_table}...")
    try:
        # Load data from source
        df = bq.query(f"SELECT * FROM `{src_table}`").to_dataframe()
        
        # Write to new target dataset
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        job = bq.load_table_from_dataframe(df, dest_table, job_config=job_config)
        job.result()
        print(f"Successfully migrated ammunition records to {dest_table}")
        
        # 3. Clean up / Delete old combined table to keep schemas separate
        print(f"Deleting legacy combined table {src_table}...")
        bq.delete_table(src_table, not_found_ok=True)
        print("Legacy table removed successfully.")
        
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    separate_datasets()
