import sqlite3
from google.cloud import bigquery

GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"
DB_PATH = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\master_index_v2.db"

# 7561 Center Ave Convergence Data
convergence_rows = [
    {
        "unit": "#J1",
        "owner": "DYLAN & ANDREW HOLDINGS LLC",
        "acquired_date": "05/20/2022",
        "price": 725000.0,
        "mail_address": "15822 GARNET ST, WESTMINSTER",
        "flags": "Weaver audit node"
    },
    {
        "unit": "#E1",
        "owner": "KRS WERKS LLC",
        "acquired_date": "08/23/2023",
        "price": 825000.0,
        "mail_address": "13337 SOUTH ST #683",
        "flags": "Mailbox suite"
    },
    {
        "unit": "#D1",
        "owner": "BROWN HUBERT LLC",
        "acquired_date": "04/29/2016",
        "price": 0.0,
        "mail_address": "PO BOX 531604, HENDERSON NV",
        "flags": "NV shell — CORPORATE CREATIONS NETWORK INC. (formed 03/15/2021)"
    },
    {
        "unit": "#G3",
        "owner": "FREEDMAN ENTERPRISES LLC",
        "acquired_date": "12/31/2009",
        "price": 0.0,
        "mail_address": "19295 WOODLANDS DR",
        "flags": "Family transfer"
    },
    {
        "unit": "Ste 45",
        "owner": "TAM NGUYEN",
        "acquired_date": "03/26/2021",
        "price": None,
        "mail_address": "$1,997 PPP (812112 - Beauty Salons)",
        "flags": "Weaver audit signer for GGCF ARPA grants"
    }
]

def load_to_bigquery():
    print("Connecting to BigQuery...")
    client = bigquery.Client(project=GCP_PROJECT)
    table_id = f"{GCP_PROJECT}.forensic_layers.hbnc_convergence_points"
    
    schema = [
        bigquery.SchemaField("unit", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("owner", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("acquired_date", "STRING"),
        bigquery.SchemaField("price", "FLOAT"),
        bigquery.SchemaField("mail_address", "STRING"),
        bigquery.SchemaField("flags", "STRING")
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    try:
        # Create table if not exists
        table = client.create_table(table, exists_ok=True)
        print(f"BigQuery Table {table_id} is ready.")
        
        # Load rows
        errors = client.insert_rows_json(table_id, convergence_rows)
        if errors == []:
            print("Successfully loaded convergence rows into BigQuery.")
        else:
            print(f"Error loading to BQ: {errors}")
    except Exception as e:
        print(f"Failed loading to BigQuery: {e}")

def load_to_sqlite():
    print("\nConnecting to SQLite master_index_v2.db...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hbnc_convergence_points (
            unit TEXT PRIMARY KEY,
            owner TEXT,
            acquired_date TEXT,
            price REAL,
            mail_address TEXT,
            flags TEXT
        )
        """)
        
        # Insert or replace
        for r in convergence_rows:
            cursor.execute("""
            INSERT OR REPLACE INTO hbnc_convergence_points (unit, owner, acquired_date, price, mail_address, flags)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (r["unit"], r["owner"], r["acquired_date"], r["price"], r["mail_address"], r["flags"]))
            
        conn.commit()
        conn.close()
        print("Successfully loaded convergence rows into SQLite!")
    except Exception as e:
        print(f"Failed loading to SQLite: {e}")

if __name__ == "__main__":
    load_to_bigquery()
    load_to_sqlite()
