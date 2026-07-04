from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

print("=" * 70)
print("PRECISE FIT LLC + GLOBAL IT RESOURCES - DOUBLE DIP FORENSICS")
print("=" * 70)

# 1. Full detail on PRECISE FIT
print("\n--- PRECISE FIT LIMITED ONE LLC - All loans ---")
q1 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, BorrowerZip,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode, BusinessType,
       LoanStatus, DateApproved, ServicingLenderName, JobsReported
FROM (SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
      UNION ALL SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`)
WHERE UPPER(BorrowerName) LIKE '%PRECISE FIT%'
ORDER BY DateApproved
""").to_dataframe()
print(q1.to_string(index=False))

# 2. Full detail on GLOBAL IT RESOURCES
print("\n--- GLOBAL INFORMATION TECHNOLOGY RESOURCES INC - All loans ---")
q2 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, BorrowerZip,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode, BusinessType,
       LoanStatus, DateApproved, ServicingLenderName, JobsReported
FROM (SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
      UNION ALL SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`)
WHERE UPPER(BorrowerName) LIKE '%GLOBAL INFORMATION TECHNOLOGY%'
ORDER BY DateApproved
""").to_dataframe()
print(q2.to_string(index=False))

# 3. Who else at 17011 Beach Blvd got PPP? Full entity list
print("\n--- ALL ENTITIES at 17011 Beach Blvd ---")
q3 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode,
       BusinessType, LoanStatus, DateApproved, ServicingLenderName, JobsReported
FROM (SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
      UNION ALL SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`)
WHERE UPPER(BorrowerAddress) LIKE '%17011%BEACH%'
ORDER BY CurrentApprovalAmount DESC
""").to_dataframe()
print(q3.to_string(index=False))

# 4. PRECISE FIT - same jobs count across two loans? Compare
print("\n--- JOB COUNT COMPARISON (fraud signal: inflated in round 2) ---")
q4 = bq.query(f"""
SELECT BorrowerName, DateApproved, CurrentApprovalAmount,
       JobsReported, NAICSCode, ServicingLenderName, LoanStatus
FROM (SELECT * FROM `{P}.ppp_rico.ppp_150k_plus`
      UNION ALL SELECT * FROM `{P}.ppp_rico.ppp_up_to_150k`)
WHERE UPPER(BorrowerName) LIKE '%PRECISE FIT%'
   OR UPPER(BorrowerName) LIKE '%GLOBAL INFORMATION TECHNOLOGY RESOURCES%'
   OR UPPER(BorrowerName) LIKE '%RUSSELL FISCHER%'
   OR UPPER(BorrowerName) LIKE '%ELMORE MOTORS%'
   OR UPPER(BorrowerName) LIKE '%AMP HOLDING%'
ORDER BY BorrowerName, DateApproved
""").to_dataframe()
print(q4.to_string(index=False))

# 5. Who owns 17011 Beach Blvd? Check HB LLCs
print("\n--- HB_LLCS: Who owns 17011 Beach Blvd? ---")
q5 = bq.query(f"""
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity,
       APN, LastSeller, LastSaleDate, LastSaleValue
FROM `{P}.ppp_rico.hb_llcs`
WHERE UPPER(SiteAddress) LIKE '%17011%'
   OR UPPER(SiteAddress) LIKE '%17011 BEACH%'
""").to_dataframe()
print(q5.to_string(index=False) if len(q5) > 0 else "17011 Beach Blvd not in hb_llcs.")

# 6. Clearinghouse CDFI PPP - same lender pattern across suspects?
print("\n--- CLEARINGHOUSE CDFI PPP: Other large loans ---")
q6 = bq.query(f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       CurrentApprovalAmount, ForgivenessAmount, NAICSCode,
       LoanStatus, DateApproved, JobsReported
FROM `{P}.ppp_rico.ppp_150k_plus`
WHERE UPPER(ServicingLenderName) LIKE '%CLEARINGHOUSE CDFI%'
ORDER BY CurrentApprovalAmount DESC
LIMIT 20
""").to_dataframe()
print(q6.to_string(index=False))
