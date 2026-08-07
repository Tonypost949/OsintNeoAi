from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

print("=" * 70)
print("DRT LLC / DRT INVESTMENTS LLC - FULL DEEP DIVE")
print("=" * 70)

# 1. All PPP loans for DRT entities
print("\n--- ALL PPP LOANS: DRT ---")
q1 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, BorrowerZip,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode, BusinessType,
       LoanStatus, DateApproved, ServicingLenderName, JobsReported
FROM (
  SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
  UNION ALL
  SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`
)
WHERE UPPER(BorrowerName) LIKE '%DRT%'
ORDER BY CurrentApprovalAmount DESC
""").to_dataframe()
print(q1.to_string(index=False))

# 2. All HB LLC properties matching DRT
print("\n--- HB_LLCS: DRT Properties ---")
q2 = bq.query(f"""
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity,
       APN, LastSeller, LastSaleDate, LastSaleValue
FROM `{P}.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%DRT%'
   OR UPPER(Owner2) LIKE '%DRT%'
   OR UPPER(SiteAddress) LIKE '%19900 BEACH%'
   OR UPPER(SiteAddress) LIKE '%16862 CORAL%'
ORDER BY LastSaleValue DESC
""").to_dataframe()
print(q2.to_string(index=False))

# 3. Who SOLD to DRT? (LastSeller = straw seller / nominee)
print("\n--- WHO SOLD TO DRT? (Upstream sellers) ---")
q3 = bq.query(f"""
SELECT LastSeller, COUNT(*) AS properties_sold_to_drt,
       SUM(LastSaleValue) AS total_sale_value,
       STRING_AGG(SiteAddress, ' | ') AS addresses
FROM `{P}.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%DRT%' OR UPPER(Owner2) LIKE '%DRT%'
GROUP BY LastSeller
ORDER BY total_sale_value DESC
""").to_dataframe()
print(q3.to_string(index=False))

# 4. Does 19900 Beach Blvd appear anywhere in existing RICO evidence?
print("\n--- 19900 BEACH BLVD cross-reference ---")
q4 = bq.query(f"""
SELECT * FROM `{P}.ppp_rico.rico_evidence_matrix`
WHERE UPPER(TO_JSON_STRING(rico_evidence_matrix)) LIKE '%19900%'
   OR UPPER(TO_JSON_STRING(rico_evidence_matrix)) LIKE '%BEACH BLVD%'
LIMIT 20
""").to_dataframe()
if len(q4) > 0:
    print(q4.to_string(index=False))
else:
    # Try unified_enterprise
    q4b = bq.query(f"""
    SELECT * FROM `{P}.ppp_rico.unified_enterprise`
    WHERE UPPER(TO_JSON_STRING(unified_enterprise)) LIKE '%19900%'
       OR UPPER(TO_JSON_STRING(unified_enterprise)) LIKE '%DRT%'
    LIMIT 10
    """).to_dataframe()
    print(q4b.to_string(index=False) if len(q4b) > 0 else "Not in unified_enterprise either.")

# 5. Phoenix AZ connection - other entities also mailing to Phoenix AZ in HB_LLCS
print("\n--- OTHER HB ENTITIES mailing to Phoenix AZ (same mail hub) ---")
q5 = bq.query(f"""
SELECT Owner1, SiteAddress, MailAddress, MailCity,
       LastSaleValue, LastSaleDate, LastSeller
FROM `{P}.ppp_rico.hb_llcs`
WHERE UPPER(MailCity) IN ('PHOENIX','SCOTTSDALE','TEMPE','MESA','CHANDLER','GILBERT')
ORDER BY LastSaleValue DESC
LIMIT 20
""").to_dataframe()
print(q5.to_string(index=False))

# 6. NAICS code for DRT - what business did they claim to be?
print("\n--- TRIUMVIRATE LLC full PPP detail ---")
q6 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode,
       BusinessType, LoanStatus, DateApproved, ServicingLenderName, JobsReported
FROM (
  SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
  UNION ALL
  SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`
)
WHERE UPPER(BorrowerName) LIKE '%TRIUMVIRATE%'
   OR UPPER(BorrowerName) LIKE '%STEWART INDUSTRIES%'
   OR UPPER(BorrowerName) LIKE '%DBS ENTERPRISE%'
   OR UPPER(BorrowerName) LIKE '%FIRST HIGHLAND%'
ORDER BY BorrowerName, DateApproved
""").to_dataframe()
print(q6.to_string(index=False))
