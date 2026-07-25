from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

print("=" * 70)
print("TRIUMVIRATE LLC - FULL INVESTIGATION")
print("=" * 70)

# 1. All PPP loans for TRIUMVIRATE
print("\n--- ALL PPP LOANS: TRIUMVIRATE ---")
q1 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, BorrowerZip,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode, BusinessType,
       LoanStatus, DateApproved, ServicingLenderName, JobsReported
FROM (SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
      UNION ALL SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`)
WHERE UPPER(BorrowerName) LIKE '%TRIUMVIRATE%'
ORDER BY CurrentApprovalAmount DESC
""").to_dataframe()
print(q1.to_string(index=False))

# 2. TRIUMVIRATE in HB_LLCS
print("\n--- HB_LLCS: TRIUMVIRATE ---")
q2 = bq.query(f"""
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity,
       APN, LastSeller, LastSaleDate, LastSaleValue
FROM `{P}.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%TRIUMVIRATE%' OR UPPER(Owner2) LIKE '%TRIUMVIRATE%'
   OR UPPER(SiteAddress) LIKE '%21951%'
""").to_dataframe()
print(q2.to_string(index=False) if len(q2) > 0 else "Not in hb_llcs by name.")

# 3. What's at 21951 Brookhurst St? Who else is there?
print("\n--- ALL PPP AT 21951 BROOKHURST ST (Fountain Valley) ---")
q3 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode,
       BusinessType, LoanStatus, DateApproved, ServicingLenderName
FROM (SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
      UNION ALL SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`)
WHERE UPPER(BorrowerAddress) LIKE '%21951%BROOKHURST%'
   OR UPPER(BorrowerAddress) LIKE '%BROOKHURST%' AND UPPER(BorrowerCity) = 'FOUNTAIN VALLEY'
ORDER BY CurrentApprovalAmount DESC
LIMIT 20
""").to_dataframe()
print(q3.to_string(index=False))

# 4. NAICS 654 = what did Triumvirate claim to be?
print("\n--- TRIUMVIRATE NAICS lookup ---")
naics_map = {
    "541618": "Other Management Consulting",
    "523930": "Investment Advice",
    "531110": "Lessors of Residential Buildings",
    "531120": "Lessors of Nonresidential Buildings",
}
for code, desc in naics_map.items():
    print(f"  {code} = {desc}")

print("\n--- OTHER ALASKA-BASED PPP in HB/OC area ---")
q5 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode, DateApproved
FROM (SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
      UNION ALL SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`)
WHERE BorrowerState = 'AK'
  AND UPPER(BorrowerCity) NOT IN ('ANCHORAGE','JUNEAU','FAIRBANKS','WASILLA','SITKA','KENAI')
  AND CurrentApprovalAmount > 100000
ORDER BY CurrentApprovalAmount DESC
LIMIT 20
""").to_dataframe()
print(q5.to_string(index=False))
