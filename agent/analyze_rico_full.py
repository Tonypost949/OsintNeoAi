# analyze_rico_pandas.py
# Full RICO pattern analysis using Python/pandas - no Gemini API needed.
# Pulls real data from BigQuery and finds red-handed anomalies.

from google.cloud import bigquery
import pandas as pd

bq = bigquery.Client()

SEPARATOR = "-" * 70

def fetch(table_id: str, limit: int = 5000) -> pd.DataFrame:
    """Fetch data from BigQuery table safely with a limit."""
    query = f"SELECT * FROM `{table_id}` LIMIT {limit}"
    return bq.query(query).to_dataframe()

def analyze_address_clustering(df: pd.DataFrame):
    """Find property addresses shared by multiple LLCs."""
    print("\n[ANOMALY] Property Addresses Shared by Multiple LLCs:")
    print(SEPARATOR)
    
    col_addr = 'property_address' if 'property_address' in df.columns else None
    col_llc = 'llc_name' if 'llc_name' in df.columns else None
    
    if not col_addr or not col_llc:
        print(f"Required columns missing. Found: {list(df.columns)}")
        return

    df_clean = df.dropna(subset=[col_addr, col_llc])
    df_clean = df_clean[df_clean[col_addr].astype(str).str.strip() != '']
    
    grouped = df_clean.groupby(col_addr).agg(
        llc_count=(col_llc, 'nunique'),
        llcs=(col_llc, lambda x: ", ".join(list(x.unique())[:5]))
    ).reset_index()
    
    anomalies = grouped[grouped['llc_count'] > 1].sort_values(by='llc_count', ascending=False)
    if not anomalies.empty:
        for _, row in anomalies.head(15).iterrows():
            print(f"Address: {row[col_addr]}")
            print(f"  Count: {row['llc_count']} LLCs")
            print(f"  LLCs:  {row['llcs']}")
            print()
    else:
        print("No significant property address clustering found.")

def analyze_mail_clustering(df: pd.DataFrame):
    """Find mailing addresses shared by multiple LLCs."""
    print("\n[ANOMALY] Mailing Addresses Shared by Multiple LLCs:")
    print(SEPARATOR)
    
    # Check possible names for mail address
    col_mail = None
    for col in ['mail_address', 'mailing_address', 'mail_addr', 'address']:
        if col in df.columns:
            col_mail = col
            break
            
    col_llc = 'llc_name' if 'llc_name' in df.columns else None
    
    if not col_mail or not col_llc:
        print(f"Mailing address column not found. Available: {list(df.columns)}")
        return

    df_clean = df.dropna(subset=[col_mail, col_llc])
    df_clean = df_clean[df_clean[col_mail].astype(str).str.strip() != '']
    
    grouped = df_clean.groupby(col_mail).agg(
        llc_count=(col_llc, 'nunique'),
        llcs=(col_llc, lambda x: ", ".join(list(x.unique())[:5]))
    ).reset_index()
    
    anomalies = grouped[grouped['llc_count'] > 1].sort_values(by='llc_count', ascending=False)
    if not anomalies.empty:
        for _, row in anomalies.head(15).iterrows():
            print(f"Mail Address: {row[col_mail]}")
            print(f"  Count:        {row['llc_count']} LLCs")
            print(f"  LLCs:         {row['llcs']}")
            print()
    else:
        print("No significant mailing address clustering found.")

def analyze_nonprofit_overlaps(df: pd.DataFrame):
    """Find LLCs co-located or associated with nonprofits."""
    print("\n[ANOMALY] LLCs Associated with Nonprofits:")
    print(SEPARATOR)
    
    col_np = None
    for col in ['nonprofit_name', 'nonprofit', 'np_name']:
        if col in df.columns:
            col_np = col
            break
            
    if not col_np:
        print(f"Nonprofit column not found. Available: {list(df.columns)}")
        return
        
    df_nonprofit = df[df[col_np].notna() & (df[col_np].astype(str).str.strip() != '') & (df[col_np].astype(str) != 'nan')]
    if not df_nonprofit.empty:
        for _, row in df_nonprofit.head(15).iterrows():
            print(f"LLC:           {row.get('llc_name', 'N/A')}")
            print(f"  Address:     {row.get('property_address', 'N/A')}")
            print(f"  Nonprofit:   {row[col_np]} (EIN: {row.get('nonprofit_ein', 'N/A')})")
            print(f"  NTEE Code:   {row.get('nonprofit_ntee', 'N/A')}")
            print(f"  Revenue:     ${row.get('nonprofit_latest_revenue', 0):,.2f}")
            print()
    else:
        print("No nonprofit overlaps found in the sample.")

def analyze_ppp_hubs(df: pd.DataFrame):
    """Find LLCs with high-volume PPP loans in the evidence matrix."""
    print("\n[ANOMALY] High-Volume PPP Loan Recipients:")
    print(SEPARATOR)
    
    col_count = 'ppp_loan_count' if 'ppp_loan_count' in df.columns else None
    col_amount = 'ppp_total_amount' if 'ppp_total_amount' in df.columns else None
    
    if not col_count or not col_amount:
        print(f"PPP columns not found. Available: {list(df.columns)}")
        return
        
    df_ppp = df[df[col_count] > 0].sort_values(by=col_amount, ascending=False)
    if not df_ppp.empty:
        for _, row in df_ppp.head(15).iterrows():
            print(f"LLC:           {row.get('llc_name', 'N/A')}")
            print(f"  Loans:       {row[col_count]}")
            print(f"  Total Amt:   ${row[col_amount]:,.2f}")
            print(f"  Forgiven:    ${row.get('ppp_forgiven_amount', 0):,.2f}")
            print(f"  Details:     {row.get('ppp_loan_details', '[]')}")
            print()
    else:
        print("No PPP loan records found in the sample.")

def main():
    print("Fetching RICO evidence matrix from BigQuery...")
    # Fetch from the evidence matrix table
    table_id = "project-743aab84-f9a5-4ec7-954.ppp_rico.rico_evidence_matrix"
    try:
        df = fetch(table_id, limit=5000)
        print(f"Successfully loaded {len(df)} rows.")
        print("Columns found in table:", list(df.columns))
        
        analyze_address_clustering(df)
        analyze_mail_clustering(df)
        analyze_nonprofit_overlaps(df)
        analyze_ppp_hubs(df)
        
    except Exception as e:
        print(f"Error fetching/analyzing data: {e}")

if __name__ == "__main__":
    main()
