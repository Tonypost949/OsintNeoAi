from google.cloud import bigquery
import pandas as pd
from pathlib import Path

client = bigquery.Client(project='noble-beanbag-497411-m4')
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
pd.set_option('display.max_colwidth', 60)

# Full detail on Mercy House Living Centers
print("=== MERCY HOUSE LIVING CENTERS - FULL PPP RECORD ===")
q = """
    SELECT *
    FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
    WHERE UPPER(BorrowerName) LIKE '%MERCY HOUSE LIVING CENTERS%'
"""
df = client.query(q).to_dataframe()
print(df.T.to_string())

# Now search for CENTURY HOUSING as lender (not borrower)
print("\n=== CENTURY HOUSING as ORIGINATING LENDER ===")
q2 = """
    SELECT BorrowerName, BorrowerCity, InitialApprovalAmount, LoanStatus,
           DateApproved, OriginatingLender, ServicingLenderName
    FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
    WHERE UPPER(OriginatingLender) LIKE '%CENTURY%'
       OR UPPER(ServicingLenderName) LIKE '%CENTURY%'
    LIMIT 20
"""
df2 = client.query(q2).to_dataframe()
print(df2.to_string())

# Search for BANC OF CALIFORNIA as lender
print("\n=== BANC OF CALIFORNIA as lender (OC-related borrowers) ===")
q3 = """
    SELECT BorrowerName, BorrowerCity, InitialApprovalAmount, LoanStatus,
           DateApproved, OriginatingLender
    FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
    WHERE UPPER(ServicingLenderName) LIKE '%BANC OF CALIFORNIA%'
    LIMIT 20
"""
df3 = client.query(q3).to_dataframe()
print(df3.to_string())

# Save all results
df.to_csv(WORK_DIR / "mercy_house_living_centers_ppp.csv", index=False)
df2.to_csv(WORK_DIR / "century_housing_as_lender.csv", index=False)
df3.to_csv(WORK_DIR / "banc_of_california_lender.csv", index=False)
print("\nSaved to mercy_house_living_centers_ppp.csv, century_housing_as_lender.csv, banc_of_california_lender.csv")
