import os
from google.cloud import bigquery

def audit_counts():
    project_id = "noble-beanbag-497411-m4"
    client = bigquery.Client(project=project_id)
    
    target_tables = [
        ("drive_forensics", "drive_documents"),
        ("national_audits", "drive_file_index"),
        ("national_audits", "google_photos_index"),
        ("national_audits", "all_state_records"),
        ("onedrive_forensics", "onedrive_documents"),
        ("forensic_layers", "fca_timeline"),
        ("fraud_mart", "corporate_entities"),
        ("hb_church_osint", "property_records"),
        ("ppp_rico", "ppp_loan_records")
    ]
    
    print(f"\n========================================================")
    print(f" BIGQUERY EVIDENCE & AUDIT INVENTORY: {project_id}")
    print(f"========================================================")
    print(f"{'Dataset.Table':<45} | {'Row Count':>12}")
    print(f"{'-'*45}-|-{'-'*12}")
    
    total_records = 0
    for ds, tbl in target_tables:
        full_table = f"{project_id}.{ds}.{tbl}"
        try:
            query = f"SELECT count(*) as cnt FROM `{full_table}`"
            job = client.query(query)
            cnt = list(job.result())[0].cnt
            print(f"{ds + '.' + tbl:<45} | {cnt:>12,}")
            total_records += cnt
        except Exception as e:
            err_msg = str(e).split('\n')[0][:30]
            print(f"{ds + '.' + tbl:<45} | ERROR: {err_msg}")
            
    print(f"{'-'*45}-|-{'-'*12}")
    print(f"{'TOTAL INDEXED EVIDENCE RECORDS':<45} | {total_records:>12,}")
    print(f"========================================================\n")

if __name__ == "__main__":
    audit_counts()
