import os
from google.cloud import bigquery

OUTPUT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.environ['APPDATA'], 'gcloud', 'application_default_credentials.json')
client = bigquery.Client()

# Check BigQuery for Mercy House / HBNC / homeless nonprofit connections
queries = []

# 1. Mercy House in PPP data
queries.append(("MERCY in PPP 150k+",
    "SELECT BorrowerName, LoanAmount, LoanStatus, ServicingLenderName, DateApproved "
    "FROM ppp_rico.ppp_150k_plus "
    "WHERE BorrowerName LIKE '%MERCY%' OR BorrowerName LIKE '%MERCY HOUSE%' "
    "LIMIT 20"))

# 2. Search for homeless shelter nonprofits in PPP
queries.append(("Homeless shelter PPP loans",
    "SELECT BorrowerName, LoanAmount, LoanStatus, ServicingLenderName, NAICSCode "
    "FROM ppp_rico.ppp_150k_plus "
    "WHERE NAICSCode LIKE '623%' OR NAICSCode LIKE '624%' OR BorrowerName LIKE '%SHELTER%' "
    "OR BorrowerName LIKE '%HOUSING%' OR BorrowerName LIKE '%HOMELESS%' "
    "LIMIT 20"))

# 3. Check HBNC connections - Mercy House in rico_evidence_matrix
queries.append(("MERCY in rico_evidence_matrix",
    "SELECT * FROM ppp_rico.rico_evidence_matrix "
    "WHERE llc_name LIKE '%MERCY%' OR llc_name LIKE '%HOUSE%' "
    "LIMIT 20"))

# 4. Check all rico_matches
queries.append(("All rico_matches",
    "SELECT * FROM ppp_rico.rico_matches LIMIT 20"))

for label, q in queries:
    try:
        print(f"\n=== {label} ===")
        df = client.query(q).to_dataframe()
        print(f"Rows: {len(df)}")
        if len(df) > 0:
            print(df.to_string(index=False, max_colwidth=40))
            # Save
            safe = label.replace(' ', '_').replace('/', '_')[:40]
            df.to_csv(os.path.join(OUTPUT_DIR, f"bq_query_{safe}.csv"), index=False)
            print(f"Saved to bq_query_{safe}.csv")
    except Exception as e:
        print(f"ERROR: {e}")
