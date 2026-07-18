from google.cloud import bigquery

# Project ID from the user's AI Studio account
project_id = "project-9c94c2fa-3af4-49f1-a7b"
dataset_id = f"{project_id}.forensic_layers"
table_id = f"{dataset_id}.hbnc_esa_2020"

client = bigquery.Client(project=project_id)

# 1. Create dataset if it does not exist
print(f"[*] Ensuring dataset {dataset_id} exists...")
dataset = bigquery.Dataset(dataset_id)
dataset.location = "US"
try:
    client.get_dataset(dataset_id)
    print(f"[+] Dataset {dataset_id} already exists.")
except Exception:
    try:
        client.create_dataset(dataset, timeout=30)
        print(f"[+] Successfully created dataset {dataset_id}")
    except Exception as e:
        print(f"[ERROR] Failed to create dataset: {e}")
        exit(1)

# Schema definition for the ESA EDR 2020 records
schema = [
    bigquery.SchemaField("apn", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("address", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("contaminants", "STRING", mode="REPEATED"),
    bigquery.SchemaField("groundwater_depth_feet", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("property_owner", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("historical_use", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("recommended_actions", "STRING", mode="REPEATED"),
    bigquery.SchemaField("source_doc", "STRING", mode="REQUIRED"),
]

# Create table
print(f"[*] Creating table {table_id}...")
table = bigquery.Table(table_id, schema=schema)
try:
    client.delete_table(table_id, not_found_ok=True)
    table = client.create_table(table)
    print(f"[+] Successfully created table {table.table_id}")
except Exception as e:
    print(f"[ERROR] Failed to create table: {e}")
    exit(1)

# Structured rows to load
rows_to_load = [
    {
        "apn": "167-042-08",
        "address": "17631 Cameron Lane, Huntington Beach, California",
        "contaminants": ["Asbestos-containing materials (ACMs)", "Lead-based paint (LBP)", "Residual pesticides/herbicides"],
        "groundwater_depth_feet": "18 to 24 feet bgs",
        "property_owner": "Mitsuru Yamada Trustee",
        "historical_use": "Agricultural purposes (row crops) on southeastern portion 1930s-1950s; Residence along Cameron Lane (present) since 1940s",
        "recommended_actions": [
            "Perform an asbestos and lead-based paint survey at the existing residence (17631 Cameron Lane parcel) prior to any activities causing disturbance",
            "Soil sampling on both parcels to assess for potential residual pesticides/herbicides and lead"
        ],
        "source_doc": "Phase I Environmental Site Assessment (ESA) & EDR Report (2020)"
    },
    {
        "apn": "167-042-09",
        "address": "17642 Beach Boulevard, Huntington Beach, California",
        "contaminants": ["Asbestos-containing materials (ACMs)", "Lead-based paint (LBP)", "Residual pesticides/herbicides"],
        "groundwater_depth_feet": "18 to 24 feet bgs",
        "property_owner": "Mitsuru Yamada Trustee",
        "historical_use": "Undeveloped prior to 1930s; residence added 1930s-1950s, demolished in 1994; majority remains undeveloped vegetated lot",
        "recommended_actions": [
            "A geophysical survey and soil sampling on the southeast corner of the 17642 Beach Boulevard parcel to evaluate potential for buried materials or residual contamination",
            "Soil sampling on both parcels to assess for potential residual pesticides/herbicides and lead"
        ],
        "source_doc": "Phase I Environmental Site Assessment (ESA) & EDR Report (2020)"
    }
]

# Run a free Load Job to bypass sandbox DML limits
print("[*] Ingesting data via load_table_from_json...")
job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
)

try:
    load_job = client.load_table_from_json(
        rows_to_load,
        table_id,
        job_config=job_config
    )
    load_job.result()  # Wait for the load job to complete
    print("[SUCCESS] ESA EDR 2020 data successfully loaded into BigQuery via Load Job!")
except Exception as e:
    print(f"[ERROR] Load job failed: {e}")
