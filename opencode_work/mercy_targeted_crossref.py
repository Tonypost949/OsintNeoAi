from google.cloud import bigquery
import pandas as pd
from pathlib import Path

client = bigquery.Client(project='noble-beanbag-497411-m4')
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

# High-priority targets
targets = [
    ("MERCY HOUSE LIVING CENTERS", "ppp_150k_plus"),
    ("MERCY HOUSING AND SHELTER", "ppp_150k_plus"),
    ("CENTURY HOUSING", "ppp_150k_plus"),
    ("VAGABOND", "ppp_150k_plus"),
    ("CAS ACQUISITION", "ppp_150k_plus"),
    ("CAS A ", "ppp_150k_plus"),
]

all_rows = []
for term, dataset in targets:
    q = f"""
        SELECT '{dataset}' as dataset, LoanNumber, BorrowerName, BorrowerAddress, BorrowerCity,
               BorrowerState, InitialApprovalAmount, CurrentApprovalAmount, LoanStatus,
               DateApproved, ServicingLenderName, OriginatingLender, NAICSCode,
               JobsReported, ForgivenessAmount, ForgivenessDate
        FROM `noble-beanbag-497411-m4.ppp_rico.{dataset}`
        WHERE UPPER(BorrowerName) LIKE '%{term}%'
        LIMIT 50
    """
    df = client.query(q).to_dataframe()
    if not df.empty:
        all_rows.append(df)
        print(f"'{term}': {len(df)} hits")

if all_rows:
    combined = pd.concat(all_rows, ignore_index=True)
    out = WORK_DIR / "mercy_targeted_crossref.csv"
    combined.to_csv(out, index=False)
    print(f"\nSaved {len(combined)} rows to mercy_targeted_crossref.csv")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_colwidth', 40)
    print(combined[['dataset','BorrowerName','BorrowerCity','InitialApprovalAmount','LoanStatus','ServicingLenderName']].to_string())
