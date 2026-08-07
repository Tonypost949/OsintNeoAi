"""Focused: Board member PPP matches only (no Mercy noise)"""
import os, pandas as pd
os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

people = ["BRYANT","PAVALKO","BUNTICH","BERGMAN","MCCARTY","JULIAN","COLE","BROOKS",
          "HAYNES","LONG","GROSS","WILSON","MIZE","BUKATY","CLYDE","BAKER","BELZ","RUMBAUGH","CONWAY"]

companies = ["ASL ELECTRIC","RBA BUILDERS","SHOPOFF","ADVANCED REAL ESTATE",
             "COLE AND COMPANY","COLE & COMPANY","BUNTICH","CLARITY TAX"]

def query_table(table):
    clauses = " OR ".join([f"UPPER(BorrowerName) LIKE '%{n}%'" for n in people])
    return f"""
    SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, 
           ForgivenessAmount, DateApproved, LoanStatus, BusinessType, NAICSCode,
           ServicingLenderName, JobsReported
    FROM `{PRJ}.ppp_rico.{table}`
    WHERE ({clauses}) AND BorrowerName IS NOT NULL
    ORDER BY CurrentApprovalAmount DESC
    """

def query_companies(table):
    clauses = " OR ".join([f"UPPER(BorrowerName) LIKE '%{n}%'" for n in companies])
    return f"""
    SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount,
           DateApproved, LoanStatus, ServicingLenderName
    FROM `{PRJ}.ppp_rico.{table}`
    WHERE ({clauses}) AND BorrowerName IS NOT NULL
    ORDER BY CurrentApprovalAmount DESC
    """

# People in 150k_plus
print("=" * 70)
print("BOARD MEMBER + OFFICER NAMES IN PPP 150k_plus")
print("=" * 70)
df1 = client.query(query_table("ppp_150k_plus")).to_dataframe()
print(f"Matches: {len(df1)}")
for _, r in df1.iterrows():
    print(f"  ${r['CurrentApprovalAmount']:>10,.0f}  {r['BorrowerCity']}, {r['BorrowerState']}  {r['BorrowerName'][:55]}  [{r['LoanStatus']}]")

# People in up_to_150k (only show first 20)
print("\n" + "=" * 70)
print("BOARD MEMBER + OFFICER NAMES IN PPP up_to_150k (top 20)")
print("=" * 70)
df2 = client.query(query_table("ppp_up_to_150k")).to_dataframe()
print(f"Matches: {len(df2)}")
for _, r in df2.head(20).iterrows():
    print(f"  ${r['CurrentApprovalAmount']:>10,.0f}  {r['BorrowerCity']}, {r['BorrowerState']}  {r['BorrowerName'][:55]}  [{r['LoanStatus']}]")

# Companies
print("\n" + "=" * 70)
print("VENDOR COMPANIES IN PPP")
print("=" * 70)
df3a = client.query(query_companies("ppp_150k_plus")).to_dataframe()
df3b = client.query(query_companies("ppp_up_to_150k")).to_dataframe()
df3 = pd.concat([df3a, df3b]).sort_values("CurrentApprovalAmount", ascending=False)
print(f"Matches: {len(df3)}")
for _, r in df3.iterrows():
    print(f"  ${r['CurrentApprovalAmount']:>10,.0f}  {r['BorrowerCity']}, {r['BorrowerState']}  {r['BorrowerName'][:55]}  [{r['LoanStatus']}]")

# OC area cross-match
print("\n" + "=" * 70)
print("OC-AREA NAME CROSS-MATCH (150k_plus)")
print("=" * 70)
oc = ["HUNTINGTON BEACH","SEAL BEACH","FOUNTAIN VALLEY","NEWPORT BEACH","COSTA MESA",
      "SANTA ANA","LONG BEACH","WESTMINSTER","GARDEN GROVE","IRVINE"]
oc_in = ",".join([f"'{c}'" for c in oc])
pclauses = " OR ".join([f"UPPER(BorrowerName) LIKE '%{n}%'" for n in people[:9]])
q4 = f"""
SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, DateApproved, LoanStatus, NAICSCode
FROM `{PRJ}.ppp_rico.ppp_150k_plus`
WHERE ({pclauses}) AND UPPER(BorrowerCity) IN ({oc_in})
ORDER BY CurrentApprovalAmount DESC
"""
df4 = client.query(q4).to_dataframe()
print(f"Matches: {len(df4)}")
for _, r in df4.iterrows():
    print(f"  ${r['CurrentApprovalAmount']:>10,.0f}  {r['BorrowerCity']}, {r['BorrowerState']}  {r['BorrowerName'][:55]}  NAICS:{r['NAICSCode']}")

# Save
all_df = pd.concat([d for d in [df1, df2, df3, df4] if len(d) > 0])
all_df.to_csv(r"C:\Users\HP\OneDrive\Documents\opencode_work\bq_board_ppp_final.csv", index=False)
print(f"\nSaved {len(all_df)} rows to bq_board_ppp_final.csv")
