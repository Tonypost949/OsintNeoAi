import pandas as pd
from google.cloud import bigquery
import re

bq = bigquery.Client()

def fetch(query: str) -> pd.DataFrame:
    return bq.query(query).to_dataframe()

def is_human_name(name: str) -> bool:
    if not isinstance(name, str): return False
    name = name.upper()
    exclude = ['LLC', 'INC', 'CORP', 'LTD', 'COMPANY', 'TRUST', 'CITY OF', 'COUNTY', 'STATE', 'CHURCH', 'FOUNDATION', 'BANK', 'ASSOCIATION', 'PARTNERSHIP', ' LP', ' L.P.', 'ENTERPRISES', 'HOLDINGS', 'INVESTMENTS', 'SERVICES', 'MANAGEMENT', 'GROUP', 'PROPERTIES', 'REALTY', 'USA', 'CO.']
    for ex in exclude:
        if ex in name:
            return False
    # Check if it has at least one space (First Last) and isn't just numbers
    if ' ' not in name.strip(): return False
    if bool(re.search(r'\d', name)): return False
    return True

def main():
    print("Extracting human names...")
    results = {}

    # 1. Board Members involved in self-dealing
    q_board = "SELECT DISTINCT board_member, nonprofit, vendor_entity FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.v_nonprofit_board_ppp_self_dealing`"
    df_board = fetch(q_board)
    results['Board Members (Self-Dealing)'] = df_board.to_dict('records')

    # 2. Human PPP Borrowers associated with the network
    # For speed, let's query the rico_matches or evidence_matrix which already cross-referenced PPP data
    q_rico = "SELECT DISTINCT ppp_names_matched FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.rico_evidence_matrix` WHERE ppp_names_matched IS NOT NULL AND ppp_names_matched != ''"
    df_rico = fetch(q_rico)
    human_ppp = set()
    for row in df_rico['ppp_names_matched']:
        names = row.split(', ')
        for n in names:
            if is_human_name(n):
                human_ppp.add(n)
    
    results['Human PPP Borrowers (Network Matched)'] = sorted(list(human_ppp))

    # 3. Human Property Owners (Owner1) in the Master View
    q_owner = "SELECT DISTINCT Owner1, MailCity FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.v_rico_enterprise_master`"
    df_owner = fetch(q_owner)
    human_owners = []
    for _, row in df_owner.iterrows():
        owner = row['Owner1']
        if is_human_name(owner):
            human_owners.append({"name": owner, "mail_city": row['MailCity']})
    
    results['Human Property Owners (Master View)'] = human_owners[:50] # Limit to 50 for brevity

    # Print results formatted for AI consumption
    for category, data in results.items():
        print(f"=== {category} ===")
        if isinstance(data, list):
            for item in data[:20]: # show top 20
                print(item)
            if len(data) > 20: print(f"... and {len(data)-20} more.")
        print()

if __name__ == "__main__":
    main()
