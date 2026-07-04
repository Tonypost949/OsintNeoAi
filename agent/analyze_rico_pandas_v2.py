# analyze_rico_pandas_v2.py
# Full RICO pattern analysis using Python/pandas - no Gemini API needed.
# Pulls real data from BigQuery views and finds red-handed anomalies.

from google.cloud import bigquery
import pandas as pd

bq = bigquery.Client()

SEPARATOR = "-" * 70

def fetch(table_id: str, limit: int = 5000) -> pd.DataFrame:
    """Fetch data from BigQuery table safely with a limit."""
    query = f"SELECT * FROM `{table_id}` LIMIT {limit}"
    return bq.query(query).to_dataframe()

def analyze_site_address_clustering(df: pd.DataFrame):
    """Find site addresses shared by multiple entities in the master view."""
    print("\n[ANOMALY] Site Addresses Shared by Multiple Clean Owners:")
    print(SEPARATOR)
    if 'SiteAddress' not in df.columns or 'clean_owner' not in df.columns:
        print("Required columns (SiteAddress, clean_owner) not present.")
        return
        
    df_clean = df.dropna(subset=['SiteAddress', 'clean_owner'])
    df_clean = df_clean[df_clean['SiteAddress'].astype(str).str.strip() != '']
    
    grouped = df_clean.groupby('SiteAddress').agg(
        owner_count=('clean_owner', 'nunique'),
        owners=('clean_owner', lambda x: ", ".join(list(x.unique())[:5]))
    ).reset_index()
    
    anomalies = grouped[grouped['owner_count'] > 1].sort_values(by='owner_count', ascending=False)
    if not anomalies.empty:
        for _, row in anomalies.head(15).iterrows():
            print(f"Site Address: {row['SiteAddress']}")
            print(f"  Unique Owners Count: {row['owner_count']}")
            print(f"  Owners:              {row['owners']}")
            print()
    else:
        print("No significant site address clustering found.")

def analyze_mailbox_hubs(df: pd.DataFrame):
    """Display pre-calculated mailbox cluster hubs from the DB view."""
    print("\n[ANOMALY] Mailbox Cluster Hubs (From View):")
    print(SEPARATOR)
    if df.empty:
        print("No mailbox hubs data found.")
        return
        
    # Columns: MailAddress, llc_count, avg_sale_value, first_sale, last_sale, llc_names, apns, risk_level, cluster_notes
    for _, row in df.head(10).iterrows():
        print(f"Mailbox/Address: {row.get('MailAddress', 'N/A')}")
        print(f"  LLC Count:      {row.get('llc_count', 0)}")
        print(f"  Risk Level:     {row.get('risk_level', 'N/A')}")
        print(f"  Associated:     {row.get('llc_names', 'N/A')[:100]}...")
        if pd.notna(row.get('cluster_notes')):
            print(f"  Notes:          {row.get('cluster_notes')}")
        print()

def analyze_self_dealing(df: pd.DataFrame):
    """Display nonprofit board member self-dealing instances."""
    print("\n[ANOMALY] Nonprofit Board PPP Self-Dealing:")
    print(SEPARATOR)
    if df.empty:
        print("No self-dealing anomalies found.")
        return
        
    # Columns: board_member, nonprofit, vendor_entity, ppp_borrower_name, ppp_amount, ppp_location, ppp_status, legal_exposure, source_doc
    for _, row in df.iterrows():
        print(f"Board Member: {row.get('board_member', 'N/A')}")
        print(f"  Nonprofit:    {row.get('nonprofit', 'N/A')}")
        print(f"  Borrower:     {row.get('ppp_borrower_name', 'N/A')} (Amount: ${row.get('ppp_amount', 0):,.2f})")
        print(f"  Exposure:     {row.get('legal_exposure', 'N/A')}")
        print(f"  Source Doc:   {row.get('source_doc', 'N/A')}")
        print()

def analyze_nonprofit_entities(df: pd.DataFrame):
    """Filter master view for nonprofit flag and inspect funding anomalies."""
    print("\n[ANOMALY] Nonprofit Entities Associated with PPP Funding:")
    print(SEPARATOR)
    if 'NonProfit' not in df.columns:
        print("NonProfit flag column not present in master view.")
        return
        
    df_np = df[df['NonProfit'].astype(str).str.lower().str.strip().isin(['y', 'yes', 'true', '1'])]
    if not df_np.empty:
        for _, row in df_np.head(10).iterrows():
            print(f"Entity (Clean Owner): {row.get('clean_owner', 'N/A')}")
            print(f"  Site Address:        {row.get('SiteAddress', 'N/A')}")
            print(f"  PPP Borrower:        {row.get('ppp_borrower', 'N/A')} (Amount: ${row.get('ppp_amount', 0):,.2f})")
            print(f"  Lender:              {row.get('lender', 'N/A')}")
            print()
    else:
        print("No nonprofit entities identified in the master view sample.")

def main():
    print("Connecting to BigQuery and fetching analytics...")
    
    # 1. Fetch from v_rico_enterprise_master
    try:
        print("Fetching master enterprise view...")
        df_master = fetch("project-743aab84-f9a5-4ec7-954.ppp_rico.v_rico_enterprise_master", limit=3000)
        analyze_site_address_clustering(df_master)
        analyze_nonprofit_entities(df_master)
    except Exception as e:
        print(f"Error analyzing master enterprise view: {e}")
        
    # 2. Fetch from v_mailbox_cluster_hubs
    try:
        print("\nFetching mailbox cluster hubs view...")
        df_mail = fetch("project-743aab84-f9a5-4ec7-954.ppp_rico.v_mailbox_cluster_hubs", limit=50)
        analyze_mailbox_hubs(df_mail)
    except Exception as e:
        print(f"Error analyzing mailbox cluster hubs: {e}")

    # 3. Fetch from v_nonprofit_board_ppp_self_dealing
    try:
        print("\nFetching nonprofit self-dealing view...")
        df_self = fetch("project-743aab84-f9a5-4ec7-954.ppp_rico.v_nonprofit_board_ppp_self_dealing", limit=50)
        analyze_self_dealing(df_self)
    except Exception as e:
        print(f"Error analyzing self dealing: {e}")

if __name__ == "__main__":
    main()
