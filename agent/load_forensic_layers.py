import os
from google.cloud import bigquery

def load_data():
    project_id = "project-743aab84-f9a5-4ec7-954"
    client = bigquery.Client(project=project_id)
    
    # 1. Create dataset if it doesn't exist
    dataset_id = f"{project_id}.forensic_layers"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "us-central1"
    
    try:
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"Dataset {dataset_id} is ready.")
    except Exception as e:
        print(f"Error creating dataset: {e}")
        return

    # 2. Define schema and table
    table_id = f"{dataset_id}.ppp_loans"
    schema = [
        bigquery.SchemaField("entity_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("hb_property", "STRING"),
        bigquery.SchemaField("apn", "STRING"),
        bigquery.SchemaField("mail_address", "STRING"),
        bigquery.SchemaField("last_sale_date", "STRING"),
        bigquery.SchemaField("last_sale_amount", "NUMERIC"),
        bigquery.SchemaField("last_sale_notes", "STRING"),
        bigquery.SchemaField("ppp_loan_1_date", "STRING"),
        bigquery.SchemaField("ppp_loan_1_amount", "NUMERIC"),
        bigquery.SchemaField("ppp_loan_1_lender", "STRING"),
        bigquery.SchemaField("ppp_loan_2_date", "STRING"),
        bigquery.SchemaField("ppp_loan_2_amount", "NUMERIC"),
        bigquery.SchemaField("ppp_loan_2_lender", "STRING"),
        bigquery.SchemaField("total_forgiven", "NUMERIC"),
        bigquery.SchemaField("naics", "STRING"),
        bigquery.SchemaField("naics_description", "STRING"),
        bigquery.SchemaField("jobs_claimed", "INTEGER"),
        bigquery.SchemaField("location_claimed", "STRING"),
        bigquery.SchemaField("demographics", "STRING")
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    try:
        table = client.create_table(table, exists_ok=True)
        print(f"Table {table_id} is ready.")
    except Exception as e:
        print(f"Error creating table: {e}")
        return

    # 3. Data to insert
    rows_to_insert = [
        {
            "entity_name": "STEWART INDUSTRIES LLC",
            "hb_property": "3311 BOUNTY CIR",
            "apn": "178-431-14",
            "mail_address": "1077 PACIFIC COAST HWY #247, SEAL BEACH",
            "last_sale_date": "05/04/2021",
            "last_sale_amount": 0,
            "last_sale_notes": "family transfer from STEWART, JOSH; STEWART, BRENDA",
            "ppp_loan_1_date": "04/15/2020",
            "ppp_loan_1_amount": 564162,
            "ppp_loan_1_lender": "Bank of America",
            "ppp_loan_2_date": "03/31/2021",
            "ppp_loan_2_amount": 564165,
            "ppp_loan_2_lender": "Bank of America",
            "total_forgiven": 1137910.56,
            "naics": "336211",
            "naics_description": "Motor Vehicle Body Manufacturing",
            "jobs_claimed": 54,
            "location_claimed": "150 Mcquiston Dr, Battle Creek, MI",
            "demographics": "Black/African American Male Owned, Non-Veteran"
        },
        {
            "entity_name": "TRIUMVIRATE LLC",
            "hb_property": "21951 BROOKHURST ST",
            "apn": "151-234-09",
            "mail_address": "9874 RARITAN AVE, FOUNTAIN VALLEY",
            "last_sale_date": "11/19/2021",
            "last_sale_amount": 2800000,
            "last_sale_notes": "from ROSELL, DAVID T; ROSELL, LORI L",
            "ppp_loan_1_date": "04/09/2020",
            "ppp_loan_1_amount": 619100,
            "ppp_loan_1_lender": "Community Banks of Colorado / Bank of Jackson Hole Trust (WY)",
            "ppp_loan_2_date": "02/17/2021",
            "ppp_loan_2_amount": 852740,
            "ppp_loan_2_lender": "Community Banks of Colorado / Bank of Jackson Hole Trust (WY)",
            "total_forgiven": 859751.42,
            "naics": "721199",
            "naics_description": "All Other Traveler Accommodation (Hotels) + 713920 (Skiing Facilities)",
            "jobs_claimed": 33,
            "location_claimed": "3705 Arctic Blvd, Anchorage, AK",
            "demographics": "Male Owned"
        }
    ]

    # Insert rows
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors == []:
        print("Successfully loaded forensic entities into BigQuery.")
    else:
        print(f"Errors occurred while inserting rows: {errors}")

if __name__ == "__main__":
    load_data()
