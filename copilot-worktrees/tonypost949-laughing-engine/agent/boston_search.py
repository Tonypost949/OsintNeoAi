from google.cloud import bigquery

client = bigquery.Client(project='noble-beanbag-497411-m4')

print('=== SEARCHING BOSTON / MASSACHUSETTS LEADS ===')

# 1. Search for Charles Tevnan or Tevnan
print('\n--- Search for "Tevnan" ---')
for t in ['ppp_150k_plus', 'ppp_up_to_150k']:
    q = f"""SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, CurrentApprovalAmount, BusinessType
            FROM `noble-beanbag-497411-m4.ppp_rico.{t}`
            WHERE UPPER(BorrowerName) LIKE '%TEVNAN%' OR UPPER(BorrowerAddress) LIKE '%TEVNAN%'"""
    for r in client.query(q).result():
        print(f"  [{t}] {r.BorrowerName} | {r.BorrowerAddress}, {r.BorrowerCity}, {r.BorrowerState} | ${r.CurrentApprovalAmount:,.2f}")

# 2. Search for 15 Broad St in Boston
print('\n--- Search for "15 Broad St" in Boston ---')
for t in ['ppp_150k_plus', 'ppp_up_to_150k']:
    q = f"""SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, CurrentApprovalAmount
            FROM `noble-beanbag-497411-m4.ppp_rico.{t}`
            WHERE UPPER(BorrowerAddress) LIKE '%15 BROAD ST%' AND UPPER(BorrowerCity) = 'BOSTON'"""
    for r in client.query(q).result():
        print(f"  [{t}] {r.BorrowerName} | {r.BorrowerAddress} | ${r.CurrentApprovalAmount:,.2f}")

# 3. Search for "Pill", "Pharmacy", or similar terms in MA/Boston area
print('\n--- Search for Pill / Pharmacy / Pharmaceutical Keywords in MA ---')
for t in ['ppp_150k_plus', 'ppp_up_to_150k']:
    q = f"""SELECT BorrowerName, BorrowerAddress, BorrowerCity, CurrentApprovalAmount, JobsReported, LoanStatus
            FROM `noble-beanbag-497411-m4.ppp_rico.{t}`
            WHERE UPPER(BorrowerState) = 'MA' 
              AND (UPPER(BorrowerName) LIKE '%PILL%' 
                   OR UPPER(BorrowerName) LIKE '%PHARMACY%' 
                   OR UPPER(BorrowerName) LIKE '%PHARMA%'
                   OR UPPER(BorrowerName) LIKE '%RX%'
                   OR UPPER(BorrowerName) LIKE '%MEDICAL%'
                   OR UPPER(BorrowerName) LIKE '%LAB%')
            ORDER BY CurrentApprovalAmount DESC LIMIT 15"""
    for r in client.query(q).result():
        print(f"  [{t}] ${r.CurrentApprovalAmount:,.2f} | {r.BorrowerName} | {r.BorrowerAddress}, {r.BorrowerCity} | Jobs: {r.JobsReported} | Status: {r.LoanStatus}")

# 4. Search for "Oppenheimer" or "Sylvain" or Cambridge labs
print('\n--- Search for Oppenheimer / Sylvain / Cambridge Labs ---')
for t in ['ppp_150k_plus', 'ppp_up_to_150k']:
    q = f"""SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, CurrentApprovalAmount
            FROM `noble-beanbag-497411-m4.ppp_rico.{t}`
            WHERE UPPER(BorrowerName) LIKE '%OPPENHEIMER%' 
               OR UPPER(BorrowerName) LIKE '%SYLVAIN%'
               OR (UPPER(BorrowerCity) = 'CAMBRIDGE' AND UPPER(BorrowerState) = 'MA' AND (UPPER(BorrowerName) LIKE '%LAB%' OR UPPER(BorrowerName) LIKE '%PHARM%'))"""
    for r in client.query(q).result():
        print(f"  [{t}] {r.BorrowerName} | {r.BorrowerAddress}, {r.BorrowerCity}, {r.BorrowerState} | ${r.CurrentApprovalAmount:,.2f}")

print('\nSearch complete.')
