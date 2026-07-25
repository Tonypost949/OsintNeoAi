"""
Nationwide EIN-Splitting Sweep — find PPP borrowers with loans in multiple states
"""
from google.cloud import bigquery
from pathlib import Path

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
client = bigquery.Client(project="noble-beanbag-497411-m4")

print("=" * 60)
print("1. NATIONWIDE EIN-SPLITTING: Same normalized name across states")
print("=" * 60)

q1 = """
WITH name_state_groups AS (
  SELECT
    UPPER(BorrowerName) AS norm_name,
    BorrowerState,
    COUNT(*) AS loans,
    SUM(CAST(InitialApprovalAmount AS NUMERIC)) AS total_amount,
    ARRAY_AGG(DISTINCT ServicingLenderName LIMIT 3) AS lenders,
    ARRAY_AGG(DISTINCT BorrowerCity LIMIT 5) AS cities
  FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
  WHERE UPPER(BorrowerName) NOT LIKE '%HOSPITAL%'
    AND UPPER(BorrowerName) NOT LIKE '%MEDICAL%'
    AND UPPER(BorrowerName) NOT LIKE '%SCHOOL%'
    AND UPPER(BorrowerName) NOT LIKE '%UNIVERSITY%'
    AND UPPER(BorrowerName) NOT LIKE '%CHURCH%'
    AND UPPER(BorrowerName) NOT LIKE '%URGENT%'
    AND UPPER(BorrowerName) NOT LIKE '%CLINIC%'
  GROUP BY 1, 2
),
multi_state AS (
  SELECT norm_name, ARRAY_AGG(STRUCT(BorrowerState AS state, loans AS loans, total_amount AS amount)) AS states
  FROM name_state_groups
  GROUP BY 1
  HAVING COUNT(*) >= 2
)
SELECT
  m.norm_name,
  ARRAY_LENGTH(m.states) AS num_states,
  m.states,
  SUM(CAST(s.total_amount AS NUMERIC)) OVER (PARTITION BY m.norm_name) AS grand_total
FROM multi_state m
JOIN name_state_groups s ON s.norm_name = m.norm_name
ORDER BY grand_total DESC
LIMIT 50
"""
df1 = client.query(q1).to_dataframe()
print(f"Found {len(df1)} multi-state entities")
for _, row in df1.head(30).iterrows():
    states = [f"{s['state']}:${s['amount']:,.0f}" for s in row['states']]
    print(f"  {row['norm_name'][:50]} | {row['num_states']} states | ${row['grand_total']:,.0f}")
    print(f"    {', '.join(states[:6])}")

print("\n" + "=" * 60)
print("2. HIGH-VALUE MULTI-STATE PPP: $5M+ total across states")
print("=" * 60)

q2 = """
WITH name_state_groups AS (
  SELECT
    UPPER(BorrowerName) AS norm_name,
    BorrowerState,
    SUM(CAST(InitialApprovalAmount AS NUMERIC)) AS state_total
  FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
  GROUP BY 1, 2
),
multi_state AS (
  SELECT norm_name, SUM(state_total) AS grand_total
  FROM name_state_groups
  GROUP BY 1
  HAVING SUM(state_total) > 5000000 AND COUNT(*) >= 2
)
SELECT
  m.norm_name,
  m.grand_total,
  ARRAY_AGG(STRUCT(n.BorrowerState AS state, n.BorrowerCity AS city, n.InitialApprovalAmount AS amount, n.ServicingLenderName AS lender))
    WITHIN RECORD AS details
FROM multi_state m
JOIN `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus` n ON UPPER(n.BorrowerName) = m.norm_name
ORDER BY m.grand_total DESC
LIMIT 20
"""
try:
    df2 = client.query(q2).to_dataframe()
    print(df2.to_string())
except Exception as e:
    print(f"Query error: {e}")

print("\n" + "=" * 60)
print("3. CA ENTITIES WITH MULTI-STATE FOOTPRINT")
print("=" * 60)

q3 = """
WITH ca_entities AS (
  SELECT
    UPPER(BorrowerName) AS norm_name,
    BorrowerState,
    BorrowerCity,
    BorrowerAddress,
    InitialApprovalAmount,
    ServicingLenderName,
    LoanStatus,
    DateApproved
  FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
  WHERE BorrowerState = 'CA'
    AND UPPER(BorrowerName) NOT LIKE '%HOSPITAL%'
    AND UPPER(BorrowerName) NOT LIKE '%MEDICAL%'
    AND UPPER(BorrowerName) NOT LIKE '%CLINIC%'
    AND UPPER(BorrowerName) NOT LIKE '%SCHOOL%'
    AND UPPER(BorrowerName) NOT LIKE '%UNIVERSITY%'
),
name_national AS (
  SELECT
    UPPER(BorrowerName) AS norm_name,
    COUNT(DISTINCT BorrowerState) AS states,
    SUM(CAST(InitialApprovalAmount AS NUMERIC)) AS national_total,
    ARRAY_AGG(DISTINCT BorrowerState LIMIT 10) AS other_states
  FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
  WHERE BorrowerState != 'CA'
  GROUP BY 1
  HAVING COUNT(*) >= 2
)
SELECT
  c.norm_name, c.BorrowerCity, c.InitialApprovalAmount, c.ServicingLenderName, c.LoanStatus,
  n.states AS other_states_count, n.national_total, n.other_states
FROM ca_entities c
JOIN name_national n ON c.norm_name = n.norm_name
WHERE n.states >= 2 AND n.national_total > 500000
ORDER BY n.national_total DESC
LIMIT 30
"""
df3 = client.query(q3).to_dataframe()
print(f"Found {len(df3)} CA entities with multi-state PPP")
for _, row in df3.iterrows():
    print(f"  {row['norm_name'][:50]} | CA: {row['BorrowerCity']} | ${row['InitialApprovalAmount']:,.0f}")
    print(f"    Other states: {row['other_states_count']} | Total: ${row['national_total']:,.0f}")
    print(f"    States: {row['other_states']}")

print("\n" + "=" * 60)
print("4. VIRTUAL OFFICE HUB SEARCH: Search for common virtual office addresses in PPP")
print("=" * 60)

VIRTUAL_PATTERNS = [
    "SUITE 300", "SUITE 400", "SUITE 500", "SUITE 600", "SUITE 700",
    "SUITE 800", "SUITE 900", "SUITE 1000", "SUITE 1500", "SUITE 2000",
    "STE 300", "STE 400", "STE 500", "STE 600", "STE 800", "STE 1000",
    "#300", "#400", "#500", "#600", "#800", "#1000",
    "REGUS", "VIRTUAL OFFICE", "WEWORK", "SERVICED OFFICE",
    "333 WASHINGTON", "350 CALIFORNIA", "1 MARKET PLZ", "44 MONTGOMERY",
    "505 PARKS", "555 CALIFORNIA", "345 SPEAR"
]

for pattern in VIRTUAL_PATTERNS[:10]:
    q = f"""
        SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
               InitialApprovalAmount, LoanStatus, DateApproved, ServicingLenderName
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
        WHERE UPPER(BorrowerAddress) LIKE '%{pattern}%'
           OR UPPER(BorrowerAddress) LIKE '%{pattern.replace(' ', '%')}%'
        ORDER BY InitialApprovalAmount DESC
        LIMIT 5
    """
    df = client.query(q).to_dataframe()
    if not df.empty:
        print(f"\n--- {pattern} ({len(df)} matches) ---")
        print(df[["BorrowerName", "BorrowerCity", "BorrowerState", "InitialApprovalAmount"]].head(5).to_string())

print("\n" + "=" * 60)
print("5. ENVIRONMENTAL + HAZARDOUS WASTE COMPANIES — MULTI-STATE")
print("=" * 60)

q5 = """
SELECT
  UPPER(BorrowerName) AS name,
  BorrowerState,
  BorrowerCity,
  InitialApprovalAmount,
  LoanStatus,
  DateApproved,
  ServicingLenderName,
  NAICSCode
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE NAICSCode IN ('562111', '562112', '562211', '562212', '562219', '562910', '562920', '562930', '562940', '562990')
   OR UPPER(BorrowerName) LIKE '%HAZARDOUS%'
   OR UPPER(BorrowerName) LIKE '%REMEDIATION%'
   OR UPPER(BorrowerName) LIKE '%ENVIRONMENTAL%'
   OR UPPER(BorrowerName) LIKE '%WASTE MANAGEMENT%'
   OR UPPER(BorrowerName) LIKE '%CLEANING SOLUTIONS%'
   OR UPPER(BorrowerName) LIKE '%PESTICIDE%'
ORDER BY InitialApprovalAmount DESC
LIMIT 30
"""
df5 = client.query(q5).to_dataframe()
print(f"Found {len(df5)} environmental/waste PPP loans")
print(df5[["name", "BorrowerState", "InitialApprovalAmount", "LoanStatus", "NAICSCode"]].to_string())

print("\nDone.")
