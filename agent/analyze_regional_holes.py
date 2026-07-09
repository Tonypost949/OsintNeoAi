import pandas as pd
from google.cloud import bigquery
import json
import os

def fetch(bq, table_id: str, limit: int = 5000) -> pd.DataFrame:
    query = f"SELECT *OM `{table_id}` LIMIT {limit}"
    return bq.query(query).to_dataframe()

def main():
    bq = bigquery.Client()
    print("Fetching regional holes data (Mercy House, Covenant House, Illumination Foundation)...")
    
    # Fetch data
    df_master = fetch(bq, "project-743aab84-f9a5-4ec7-954.ppp_rico.v_rico_enterprise_master", limit=10000)
    df_mail = fetch(bq, "project-743aab84-f9a5-4ec7-954.ppp_rico.v_mailbox_cluster_hubs", limit=1000)
    df_self = fetch(bq, "project-743aab84-f9a5-4ec7-954.ppp_rico.v_nonprofit_board_ppp_self_dealing", limit=1000)
    
    # Filter for regional targets
    target_names = ['mercy house', 'covenant house', 'illumination foundation']
    
    regional_master = df_master[
        df_master['clean_owner'].astype(str).str.lower().apply(lambda x: any(t in x for t in target_names)) |
        df_master['SiteAddress'].astype(str).str.lower().apply(lambda x: 'fullerton' in x or 'anaheim' in x or 'hollywood' in x or 'stanton' in x)
    ]
    
    regional_self_dealing = df_self[
        df_self['nonprofit'].astype(str).str.lower().apply(lambda x: any(t in x for t in target_names))
    ]
    
    regional_mail = df_mail[
        df_mail['MailAddress'].astype(str).str.lower().apply(lambda x: 'fullerton' in x or 'anaheim' in x or 'hollywood' in x or 'stanton' in x)
    ]

    output_data = {
        "targets": target_names,
        "master_anomalies": regional_master.to_dict(orient="records"),
        "self_dealing_anomalies": regional_self_dealing.to_dict(orient="records"),
        "cmra_hubs": regional_mail.to_dict(orient="records")
    }

    out_file = 'regional_holes_data.json'
    with open(out_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
        
    print(f"Extracted {len(regional_master)} master records, {len(regional_self_dealing)} self-dealing records, {len(regional_mail)} CMRA hubs.")
    print(f"Data saved to {out_file}")

if __name__ == "__main__":
    main()
