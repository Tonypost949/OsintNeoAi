from google.cloud import bigquery
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

print("=== NATIONWIDE SWEEP: PPP OUT-OF-STATE vs PROPERTY LOCATION ===\n")

# 1. How many out-of-state PPP borrowers exist nationwide?
q1 = """
SELECT 
    p.BorrowerState AS ppp_state,
    h.MailCity AS property_city,
    COUNT(*) AS matches,
    SUM(p.CurrentApprovalAmount) AS total_ppp,
    SUM(p.ForgivenessAmount) AS total_forgiven
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus` p
INNER JOIN `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs` h 
    ON UPPER(REGEXP_REPLACE(h.Owner1, r'[^A-Z0-9]', '')) = 
       UPPER(REGEXP_REPLACE(p.BorrowerName, r'[^A-Z0-9]', ''))
WHERE p.BorrowerState NOT IN ('CA', '')
  AND p.CurrentApprovalAmount > 0
GROUP BY ppp_state, property_city
ORDER BY total_ppp DESC
LIMIT 30
"""
print("Out-of-state PPP -> HB property matches:")
try:
    rows = list(client.query(q1).result())
    for r in rows:
        print(f"  {r.ppp_state} -> {r.property_city}: {r.matches} matches, ${r.total_ppp:,.0f} PPP, ${r.total_forgiven:,.0f} forgiven")
except Exception as e:
    print(f"  (join too large: {str(e)[:80]})")

# 2. Top-10 states by out-of-state PPP to ANY property (not just HB)
print("\n=== NATIONWIDE: TOP MAILBOX CITIES FOR HB PROPERTIES ===\n")
q2 = """
SELECT 
    MailCity, 
    UPPER(MailCity) as city_upper,
    COUNT(*) AS entity_count,
    COUNT(DISTINCT Owner1) AS unique_owners,
    COUNT(DISTINCT APN) AS unique_properties
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
WHERE MailCity IS NOT NULL 
  AND MailCity != ''
  AND UPPER(MailCity) NOT IN ('HUNTINGTON BEACH', 'NEWPORT BEACH', 'FOUNTAIN VALLEY', 
                               'SEAL BEACH', 'COSTA MESA', 'WESTMINSTER', 'SANTA ANA',
                               'IRVINE', 'GARDEN GROVE', 'ANAHEIM', 'ORANGE', 'FULLERTON',
                               'HUNTINGTN BCH', 'HUNTINGTON BCH', 'HUNTINGTON', 'SUNSET BEACH')
GROUP BY MailCity
ORDER BY entity_count DESC
LIMIT 25
"""
rows = list(client.query(q2).result())
print(f"Non-OC mailing cities for HB properties: {len(rows)} total")
for r in rows[:25]:
    marker = "!!" if r.unique_owners >= 5 else "--" if r.unique_owners >= 3 else "  "
    print(f"  {marker} {r.MailCity}: {r.entity_count} entities, {r.unique_owners} owners, {r.unique_properties} properties")

# 3. Multi-state PPP patterns (same entity name, different states)
print("\n=== NATIONWIDE: SAME-NAME ENTITIES IN MULTIPLE STATES (150k+) ===\n")
q3 = """
SELECT 
    UPPER(REGEXP_REPLACE(BorrowerName, r'[^A-Z0-9]', '')) AS clean_name,
    BorrowerName,
    COUNT(DISTINCT BorrowerState) AS state_count,
    STRING_AGG(DISTINCT BorrowerState, ', ' ORDER BY BorrowerState) AS states,
    COUNT(*) AS loan_count,
    SUM(CurrentApprovalAmount) AS total_amount,
    SUM(ForgivenessAmount) AS total_forgiven
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
WHERE BorrowerName LIKE '%LLC%'
  AND CurrentApprovalAmount > 50000
GROUP BY clean_name, BorrowerName
HAVING COUNT(DISTINCT BorrowerState) >= 3
ORDER BY state_count DESC, total_amount DESC
LIMIT 20
"""
try:
    rows = list(client.query(q3).result())
    print(f"Entities with loans in 3+ states: {len(rows)} (showing top 20)")
    for r in rows:
        print(f"  {r.BorrowerName[:50]}: {r.state_count} states ({r.states[:60]}): {r.loan_count} loans, ${r.total_amount:,.0f}")
except Exception as e:
    print(f"  (query error: {str(e)[:80]})")

# 4. Top nationwide mailbox clusters
print("\n=== NATIONWIDE: MAILBOX ADDRESS CLUSTERS (5+ entities, non-OC) ===\n")
q4 = """
SELECT 
    MailAddress,
    MailCity,
    COUNT(*) AS entity_count,
    COUNT(DISTINCT Owner1) AS unique_owners
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
WHERE MailAddress IS NOT NULL 
  AND MailAddress != ''
  AND UPPER(MailCity) NOT IN ('HUNTINGTON BEACH', 'NEWPORT BEACH', 'FOUNTAIN VALLEY',
                               'SEAL BEACH', 'COSTA MESA', 'WESTMINSTER', 'SANTA ANA',
                               'IRVINE', 'GARDEN GROVE', 'ANAHEIM', 'ORANGE', 'FULLERTON')
GROUP BY MailAddress, MailCity
HAVING COUNT(DISTINCT Owner1) >= 5
ORDER BY unique_owners DESC, entity_count DESC
LIMIT 20
"""
rows = list(client.query(q4).result())
print(f"Non-OC mailbox clusters with 5+ unique owners: {len(rows)}")
for r in rows:
    print(f"  {r.MailAddress} [{r.MailCity}]: {r.entity_count} entities, {r.unique_owners} unique owners")

print("\nDone.")
