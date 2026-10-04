import pandas as pd

SEPARATOR = "-" * 70

def analyze_address_clustering(df):
    print("\n[ANOMALY] Property Addresses Shared by Multiple LLCs:")
    print(SEPARATOR)
    
    col_addr = 'property_address'
    col_llc = 'llc_name'
    
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

def analyze_mail_clustering(df):
    print("\n[ANOMALY] Mailing Addresses Shared by Multiple LLCs:")
    print(SEPARATOR)
    
    col_mail = 'mail_address'
    col_llc = 'llc_name'
    
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

def analyze_nonprofit_overlaps(df):
    print("\n[ANOMALY] LLCs Associated with Nonprofits:")
    print(SEPARATOR)
    
    col_np = 'nonprofit_name'
    df_nonprofit = df[df[col_np].notna() & (df[col_np].astype(str).str.strip() != '') & (df[col_np].astype(str) != 'nan')]
    if not df_nonprofit.empty:
        for _, row in df_nonprofit.head(15).iterrows():
            print(f"LLC:           {row['llc_name']}")
            print(f"  Address:     {row['property_address']}")
            print(f"  Nonprofit:   {row[col_np]}")
            print(f"  Revenue:     ${row['nonprofit_latest_revenue']:,.2f}")
            print()
    else:
        print("No nonprofit overlaps found.")

def analyze_ppp_hubs(df):
    print("\n[ANOMALY] High-Volume PPP Loan Recipients:")
    print(SEPARATOR)
    
    col_count = 'ppp_loan_count'
    col_amount = 'ppp_total_amount'
    
    df_ppp = df[df[col_count] > 0].sort_values(by=col_amount, ascending=False)
    if not df_ppp.empty:
        for _, row in df_ppp.head(15).iterrows():
            print(f"LLC:           {row['llc_name']}")
            print(f"  Loans:       {row[col_count]}")
            print(f"  Total Amt:   ${row[col_amount]:,.2f}")
            print()
    else:
        print("No PPP loan records found.")

def main():
    print("Loading RICO evidence matrix from local CSV...")
    df = pd.read_csv("/root/workspace/OsintNeoAi_Repo/agent/rico_evidence_matrix.csv")
    print(f"Successfully loaded {len(df)} rows.")
    
    analyze_address_clustering(df)
    analyze_mail_clustering(df)
    analyze_nonprofit_overlaps(df)
    analyze_ppp_hubs(df)

if __name__ == "__main__":
    main()