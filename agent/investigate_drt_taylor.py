from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

print("=" * 70)
print("DRT MAIL DROP + DANIEL TAYLOR + 19900 BEACH BLVD DEEP DIVE")
print("=" * 70)

# 1. Who else mails to 20101 SW Birch St (the UPS Store drop)?
print("\n--- ALL HB_LLCS using 20101 SW Birch St mail drop ---")
q1 = bq.query(f"""
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity,
       APN, LastSeller, LastSaleDate, LastSaleValue
FROM `{P}.ppp_rico.hb_llcs`
WHERE UPPER(MailAddress) LIKE '%20101%BIRCH%'
   OR UPPER(MailAddress) LIKE '%SW BIRCH%'
ORDER BY LastSaleValue DESC
""").to_dataframe()
print(f"Entities sharing this mail drop: {len(q1)}")
print(q1.to_string(index=False))

# 2. Daniel R Taylor - does he appear anywhere in PPP or LLC data?
print("\n--- DANIEL TAYLOR in PPP data ---")
q2 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode,
       BusinessType, DateApproved, ServicingLenderName
FROM (
  SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
  UNION ALL
  SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`
)
WHERE UPPER(BorrowerName) LIKE '%TAYLOR%'
  AND UPPER(BorrowerAddress) LIKE '%BIRCH%'
  OR (UPPER(BorrowerName) LIKE '%DANIEL%TAYLOR%')
  OR (UPPER(BorrowerName) LIKE '%TAYLOR%' AND UPPER(BorrowerCity) IN ('NEWPORT BEACH','HUNTINGTON BEACH','COSTA MESA','FOUNTAIN VALLEY'))
ORDER BY CurrentApprovalAmount DESC
LIMIT 20
""").to_dataframe()
print(q2.to_string(index=False))

# 3. What other PPP entities list 19900 Beach Blvd or nearby Beach Blvd HB addresses?
print("\n--- PPP LOANS at Beach Blvd HB corridor (17000-20000 block) ---")
q3 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode,
       BusinessType, LoanStatus, DateApproved, ServicingLenderName, JobsReported
FROM (
  SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
  UNION ALL
  SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`
)
WHERE UPPER(BorrowerAddress) LIKE '%BEACH BLVD%'
  AND UPPER(BorrowerCity) IN ('HUNTINGTON BEACH','WESTMINSTER','FOUNTAIN VALLEY','GARDEN GROVE')
ORDER BY CurrentApprovalAmount DESC
LIMIT 30
""").to_dataframe()
print(q3.to_string(index=False))

# 4. What is 19900 Beach Blvd? Check regional LLC data for that address
print("\n--- REGIONAL LLCs at or near 19900 Beach Blvd ---")
q4 = bq.query(f"""
SELECT *
FROM `{P}.ppp_rico.regional_llcs`
WHERE UPPER(TO_JSON_STRING(regional_llcs)) LIKE '%19900%'
   OR UPPER(TO_JSON_STRING(regional_llcs)) LIKE '%BEACH BLVD%'
LIMIT 20
""").to_dataframe()
if len(q4) > 0:
    print(q4.to_string(index=False))
else:
    print("Not in regional_llcs. Checking unified_enterprise...")
    q4b = bq.query(f"""
    SELECT * FROM `{P}.ppp_rico.unified_enterprise`
    WHERE UPPER(TO_JSON_STRING(unified_enterprise)) LIKE '%19900 BEACH%'
    LIMIT 10
    """).to_dataframe()
    print(q4b.to_string(index=False) if len(q4b) > 0 else "Not found in unified_enterprise.")

# 5. DRI LLC - who is DRI LLC that sold to DRT LLC?
print("\n--- DRI LLC in PPP and HB_LLCS data ---")
q5 = bq.query(f"""
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity,
       APN, LastSeller, LastSaleDate, LastSaleValue
FROM `{P}.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%DRI LLC%'
   OR UPPER(Owner2) LIKE '%DRI LLC%'
   OR UPPER(LastSeller) LIKE '%DRI LLC%'
""").to_dataframe()
print(f"DRI LLC appearances: {len(q5)}")
print(q5.to_string(index=False))

q5b = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode, DateApproved
FROM (
  SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
  UNION ALL
  SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`
)
WHERE UPPER(BorrowerName) LIKE '%DRI LLC%'
ORDER BY CurrentApprovalAmount DESC
LIMIT 10
""").to_dataframe()
print(q5b.to_string(index=False) if len(q5b) > 0 else "DRI LLC not in PPP data.")
