import os
from google.cloud import bigquery

DIR = r"G:\ppp_rico_data"
PROJECT = "157249702170"
DATASET = "ppp_rico"
RESULTS_TABLE = "rico_evidence_matrix"

def main():
    client = bigquery.Client(project=PROJECT)
    dest = os.path.join(DIR, "bq_rico_matches.csv")
    sql = f"SELECT * FROM `{PROJECT}.{DATASET}.{RESULTS_TABLE}` ORDER BY ppp_total_amount DESC"
    print("Querying and exporting to dataframe...")
    df = client.query(sql).to_dataframe()
    df.to_csv(dest, index=False)
    print(f"Successfully exported to {dest} ({len(df)} rows)")
    
    # Print preview
    for _, r in df.head(10).iterrows():
        print(f"  {r['llc_name'][:35]:35s}  ${r['ppp_total_amount']:>9,.0f}  ${(r['ppp_total_forgiven'] or 0):>9,.0f}  {r['ppp_loan_count']:2d} loans")

if __name__ == "__main__":
    main()
