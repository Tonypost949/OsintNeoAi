from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

print("=" * 70)
print("88 FAIR DR SHELL HUB - DEEP INVESTIGATION")
print("=" * 70)

# 1. All LLCs registered at 88 Fair Dr across ALL tables
print("\n--- ALL ENTITIES AT 88 FAIR DR ---")
q1 = bq.query(f"""
SELECT DISTINCT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       BorrowerZip, CurrentApprovalAmount, ForgivenessAmount,
       NAICSCode, BusinessType, LoanStatus, DateApproved, ServicingLenderName
FROM `{P}.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerAddress) LIKE '%88 FAIR%'
UNION ALL
SELECT DISTINCT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       BorrowerZip, CurrentApprovalAmount, ForgivenessAmount,
       NAICSCode, BusinessType, LoanStatus, DateApproved, ServicingLenderName
FROM `{P}.ppp_rico.ppp_up_to_150k`
WHERE UPPER(BorrowerAddress) LIKE '%88 FAIR%'
ORDER BY CurrentApprovalAmount DESC
""").to_dataframe()
print(q1.to_string(index=False))

# 2. Total money at this address
print("\n--- 88 FAIR DR TOTALS ---")
q2 = bq.query(f"""
SELECT
  COUNT(*) AS total_entities,
  COUNT(DISTINCT BorrowerName) AS unique_names,
  COUNT(DISTINCT NAICSCode) AS unique_naics,
  COUNT(DISTINCT BorrowerCity) AS unique_cities,
  ROUND(SUM(CurrentApprovalAmount), 2) AS total_approved,
  ROUND(SUM(ForgivenessAmount), 2) AS total_forgiven,
  MIN(DateApproved) AS first_loan,
  MAX(DateApproved) AS last_loan
FROM (
  SELECT BorrowerName, BorrowerAddress, BorrowerCity, NAICSCode,
         CurrentApprovalAmount, ForgivenessAmount, DateApproved
  FROM `{P}.ppp_rico.ppp_150k_plus`
  WHERE UPPER(BorrowerAddress) LIKE '%88 FAIR%'
  UNION ALL
  SELECT BorrowerName, BorrowerAddress, BorrowerCity, NAICSCode,
         CurrentApprovalAmount, ForgivenessAmount, DateApproved
  FROM `{P}.ppp_rico.ppp_up_to_150k`
  WHERE UPPER(BorrowerAddress) LIKE '%88 FAIR%'
)
""").to_dataframe()
print(q2.to_string(index=False))

# 3. NAICS breakdown - what "businesses" are these?
print("\n--- NAICS CODES AT 88 FAIR DR (what industries?) ---")
q3 = bq.query(f"""
SELECT NAICSCode,
       COUNT(*) AS entity_count,
       ROUND(SUM(CurrentApprovalAmount), 2) AS total_amount
FROM (
  SELECT NAICSCode, CurrentApprovalAmount FROM `{P}.ppp_rico.ppp_150k_plus`
  WHERE UPPER(BorrowerAddress) LIKE '%88 FAIR%'
  UNION ALL
  SELECT NAICSCode, CurrentApprovalAmount FROM `{P}.ppp_rico.ppp_up_to_150k`
  WHERE UPPER(BorrowerAddress) LIKE '%88 FAIR%'
)
GROUP BY NAICSCode
ORDER BY total_amount DESC
""").to_dataframe()
print(q3.to_string(index=False))

# 4. Cross-reference: do any of these names appear in hb_llcs or rico_matches?
print("\n--- CROSS-REF: Do 88 Fair Dr entities own HB properties? ---")
q4 = bq.query(f"""
SELECT p.BorrowerName, p.CurrentApprovalAmount, p.NAICSCode,
       h.SiteAddress, h.LastSaleValue, h.LastSaleDate, h.LastSeller
FROM (
  SELECT BorrowerName, BorrowerAddress, CurrentApprovalAmount, NAICSCode
  FROM `{P}.ppp_rico.ppp_150k_plus`
  WHERE UPPER(BorrowerAddress) LIKE '%88 FAIR%'
  UNION ALL
  SELECT BorrowerName, BorrowerAddress, CurrentApprovalAmount, NAICSCode
  FROM `{P}.ppp_rico.ppp_up_to_150k`
  WHERE UPPER(BorrowerAddress) LIKE '%88 FAIR%'
) p
JOIN `{P}.ppp_rico.hb_llcs` h
  ON UPPER(TRIM(p.BorrowerName)) = UPPER(TRIM(h.Owner1))
  OR UPPER(TRIM(p.BorrowerName)) = UPPER(TRIM(h.Owner2))
ORDER BY p.CurrentApprovalAmount DESC
""").to_dataframe()
if len(q4) > 0:
    print(q4.to_string(index=False))
else:
    print("No direct HB property ownership found under these exact names.")
    print("(May use nominee owners or shell layers - check lender patterns)")

# 5. Lender pattern - same bank funding all of them?
print("\n--- LENDERS funding 88 Fair Dr entities ---")
q5 = bq.query(f"""
SELECT ServicingLenderName,
       COUNT(*) AS loans_funded,
       ROUND(SUM(CurrentApprovalAmount), 2) AS total_funded
FROM (
  SELECT ServicingLenderName, CurrentApprovalAmount
  FROM `{P}.ppp_rico.ppp_150k_plus`
  WHERE UPPER(BorrowerAddress) LIKE '%88 FAIR%'
  UNION ALL
  SELECT ServicingLenderName, CurrentApprovalAmount
  FROM `{P}.ppp_rico.ppp_up_to_150k`
  WHERE UPPER(BorrowerAddress) LIKE '%88 FAIR%'
)
GROUP BY ServicingLenderName
ORDER BY total_funded DESC
""").to_dataframe()
print(q5.to_string(index=False))

print("\n" + "=" * 70)
print("INVESTIGATION COMPLETE")
print("=" * 70)
