"""Cross-ref Mercy House board members + vendors against PPP data"""
import os, pandas as pd
os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PROJECT = "noble-beanbag-497411-m4"
HEADER = "=" * 70

# Build search terms
people = [
    "BRYANT", "PAVALKO", "BUNTICH", "BERGMAN", "MCCARTY",
    "JULIAN", "COLE", "BROOKS", "HAYNES", "BUKATY", "CLYDE",
    "BAKER", "BELZ", "WILSON", "LONG", "GROSS", "MIZE",
    "RUMBAUGH", "CONWAY", "KAY",
]

companies = [
    "ASL ELECTRIC", "ASL PLUMBING", "RBA BUILDERS", "SHOPOFF",
    "ADVANCED REAL ESTATE", "COLE & COMPANY", "COLE AND COMPANY",
    "BUNTICH", "WOODBRIDGE MEADOWS", "CLARITY TAX",
    "DIVERSIFIED INVESTMENT",
]

hb_adjacent = [
    "HUNTINGTON BEACH", "SEAL BEACH", "FOUNTAIN VALLEY",
    "NEWPORT BEACH", "COSTA MESA", "SANTA ANA", "LONG BEACH",
    "WESTMINSTER", "GARDEN GROVE", "IRVINE",
]

def build_ppp_query(names, table_name):
    clauses = " OR ".join([f"UPPER(BorrowerName) LIKE '%{n}%'" for n in names])
    return f"""
    SELECT 
        BorrowerName, BorrowerCity, BorrowerState, BorrowerZip,
        CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
        BusinessType, NAICSCode, NonProfit, JobsReported,
        ServicingLenderName, OriginatingLender,
        '150k_plus' AS source_table
    FROM `{PROJECT}.ppp_rico.{table_name}`
    WHERE ({clauses}) AND BorrowerName IS NOT NULL
    ORDER BY CurrentApprovalAmount DESC
    """

# ============ QUERY 1: People names in 150k_plus ============
print(HEADER)
print("QUERY 1: Board member names in PPP 150k_plus")
print(HEADER)
q1 = build_ppp_query(people, "ppp_150k_plus")
df1 = client.query(q1).to_dataframe()
print(f"Found: {len(df1)} matches")
if len(df1) > 0:
    print(df1.to_string())
print()

# ============ QUERY 2: People names in up_to_150k ============
print(HEADER)
print("QUERY 2: Board member names in PPP up_to_150k")
print(HEADER)
q2 = build_ppp_query(people, "ppp_up_to_150k")
df2 = client.query(q2).to_dataframe()
print(f"Found: {len(df2)} matches")
if len(df2) > 0:
    print(df2.to_string())
print()

# ============ QUERY 3: Company names in both tables ============
print(HEADER)
print("QUERY 3: Vendor company names in PPP 150k_plus")
print(HEADER)
q3 = build_ppp_query(companies, "ppp_150k_plus")
df3 = client.query(q3).to_dataframe()
print(f"Found: {len(df3)} matches")
if len(df3) > 0:
    print(df3.to_string())
print()

print("QUERY 3b: Vendor companies in PPP up_to_150k")
q3b = build_ppp_query(companies, "ppp_up_to_150k")
df3b = client.query(q3b).to_dataframe()
print(f"Found: {len(df3b)} matches")
if len(df3b) > 0:
    print(df3b.to_string())
print()

# ============ QUERY 4: Address + name cross-match (high value) ============
print(HEADER)
print("QUERY 4: HB/OC area loans matching board names (150k_plus only, for speed)")
print(HEADER)
city_clause = " OR ".join([f"UPPER(BorrowerCity) = '{c}'" for c in hb_adjacent])
name_clause = " OR ".join([f"UPPER(BorrowerName) LIKE '%{n}%'" for n in people[:6]])  # First 6 for speed
q4 = f"""
SELECT 
    BorrowerName, BorrowerCity, BorrowerState,
    CurrentApprovalAmount, DateApproved, LoanStatus,
    BusinessType, NAICSCode, NonProfit, JobsReported,
    ServicingLenderName
FROM `{PROJECT}.ppp_rico.ppp_150k_plus`
WHERE ({name_clause})
  AND ({city_clause})
ORDER BY CurrentApprovalAmount DESC
"""
df4 = client.query(q4).to_dataframe()
print(f"Found: {len(df4)} OC-area name matches")
if len(df4) > 0:
    print(df4.to_string())
print()

# ============ QUERY 5: HB_LLCs matching board names ============
print(HEADER)
print("QUERY 5: HB LLCs matching board/vendor names")
print(HEADER)
llc_name_clauses = " OR ".join([f"UPPER(Owner1) LIKE '%{n}%' OR UPPER(Owner2) LIKE '%{n}%' OR UPPER(MailAddress) LIKE '%{n}%'" for n in people[:6]])
q5 = f"""
SELECT Owner1, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleDate, LastSaleValue
FROM `{PROJECT}.ppp_rico.hb_llcs`
WHERE {llc_name_clauses}
ORDER BY LastSaleDate DESC
"""
df5 = client.query(q5).to_dataframe()
print(f"Found: {len(df5)} HB LLC matches")
if len(df5) > 0:
    print(df5.to_string())
print()

# ============ QUERY 6: All Mercy House-related PPP (broader search) ============
print(HEADER)
print("QUERY 6: ALL PPP loans with 'Mercy' or 'Homeless' in name")
print(HEADER)
q6 = f"""
SELECT 
    BorrowerName, BorrowerCity, BorrowerState,
    CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
    BusinessType, NAICSCode, NonProfit, JobsReported, ServicingLenderName,
    '150k_plus' AS src
FROM `{PROJECT}.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%MERCY%'
UNION ALL
SELECT 
    BorrowerName, BorrowerCity, BorrowerState,
    CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
    BusinessType, NAICSCode, NonProfit, JobsReported, ServicingLenderName,
    'up_to_150k' AS src
FROM `{PROJECT}.ppp_rico.ppp_up_to_150k`
WHERE UPPER(BorrowerName) LIKE '%MERCY%'
ORDER BY CurrentApprovalAmount DESC
"""
df6 = client.query(q6).to_dataframe()
print(f"Found: {len(df6)} Mercy-named PPP loans")
if len(df6) > 0:
    print(df6.to_string())
print()

# ============ QUERY 7: 990 officer names in PPP ============
print(HEADER)
print("QUERY 7: Mercy House 990 officers (Haynes, Long, Gross, Wilson, Mize, Bukaty, Clyde, Baker, Belz) in PPP")
print(HEADER)
officers = ["HAYNES", "LONG", "GROSS", "WILSON", "MIZE", "BUKATY", "CLYDE", "BAKER", "BELZ"]
oc = " OR ".join([f"UPPER(BorrowerName) LIKE '%{n}%'" for n in officers])
q7 = f"""
SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, DateApproved, LoanStatus, ServicingLenderName
FROM `{PROJECT}.ppp_rico.ppp_150k_plus`
WHERE {oc}
UNION ALL
SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, DateApproved, LoanStatus, ServicingLenderName
FROM `{PROJECT}.ppp_rico.ppp_up_to_150k`
WHERE {oc}
ORDER BY CurrentApprovalAmount DESC
"""
df7 = client.query(q7).to_dataframe()
# Filter out noise (common names like "WILSON" or "LONG" will match thousands)
# Only show results in CA or with high amounts
if len(df7) > 0:
    df7_ca = df7[df7['BorrowerState'] == 'CA']
    print(f"Raw matches: {len(df7)}, CA-restricted: {len(df7_ca)}")
    if len(df7_ca) > 0:
        print(df7_ca.to_string())

# Save all results
combined = pd.concat([df for df in [df1, df2, df3, df3b, df4, df5, df6] if len(df) > 0])
combined.to_csv(r"C:\Users\HP\OneDrive\Documents\opencode_work\bq_board_ppp_results.csv", index=False)
print(f"\n{HEADER}")
print(f"DONE - Saved {len(combined)} total rows")
