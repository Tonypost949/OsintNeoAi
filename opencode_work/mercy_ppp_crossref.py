from google.cloud import bigquery
import pandas as pd
from pathlib import Path

client = bigquery.Client(project='noble-beanbag-497411-m4')
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

print("Searching ppp_150k_plus for Mercy House...")
q1 = """
    SELECT 'ppp_150k_plus' as dataset, BorrowerName, BorrowerAddress, BorrowerCity,
           BorrowerState, InitialApprovalAmount, LoanStatus, DateApproved, LoanNumber,
           ServicingLenderName, OriginatingLender
    FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
    WHERE UPPER(BorrowerName) LIKE '%MERCY%'
       OR UPPER(BorrowerName) LIKE '%CAS A%'
       OR UPPER(BorrowerName) LIKE '%VAGABOND%'
       OR UPPER(BorrowerName) LIKE '%CENTURY HOUSING%'
    LIMIT 200
"""
df1 = client.query(q1).to_dataframe()
print(f"  {len(df1)} hits")

print("Searching hb_llcs...")
q2 = """
    SELECT 'hb_llcs' as dataset, Owner1, Owner2, SiteAddress, MailAddress,
           LastSaleValue, LastSeller, MailCity
    FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
    WHERE UPPER(Owner1) LIKE '%MERCY%'
       OR UPPER(Owner2) LIKE '%MERCY%'
       OR UPPER(Owner1) LIKE '%CAS A%'
       OR UPPER(LastSeller) LIKE '%MERCY%'
    LIMIT 200
"""
df2 = client.query(q2).to_dataframe()
print(f"  {len(df2)} hits")

print("Searching ppp_up_to_150k (full table scan - just Mercy)...")
q3 = """
    SELECT 'ppp_up_to_150k' as dataset, BorrowerName, BorrowerAddress, BorrowerCity,
           BorrowerState, InitialApprovalAmount, LoanStatus, DateApproved, LoanNumber,
           ServicingLenderName, OriginatingLender
    FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
    WHERE UPPER(BorrowerName) LIKE '%MERCY%'
    LIMIT 200
"""
df3 = client.query(q3).to_dataframe()
print(f"  {len(df3)} hits")

all_dfs = [df for df in [df1, df2, df3] if not df.empty]
if all_dfs:
    combined = pd.concat(all_dfs, ignore_index=True)
    out_path = WORK_DIR / "mercy_ppp_crossref.csv"
    combined.to_csv(out_path, index=False)
    print(f"\nTotal: {len(combined)} rows -> mercy_ppp_crossref.csv")
    print(combined[['dataset','BorrowerName','InitialApprovalAmount','LoanStatus']].drop_duplicates().to_string())
else:
    print("\nNo PPP matches found.")
