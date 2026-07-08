from google.cloud import bigquery
c = bigquery.Client(project="noble-beanbag-497411-m4")

names = ["TS MARKETPLACE", "19822 BROOKHURST", "HRAPTS1", "RAI PARTNERS",
         "SOOHOO ENTERPRISES", "JUSU CORNER", "BASRAON", "MV PROPERTIES",
         "MONGSON HOLDING", "AYRES BROOKHURST", "SILVER OAK", "G DIRE"]

for name in names:
    q = f"""
        SELECT BorrowerName, BorrowerCity, BorrowerState, InitialApprovalAmount, LoanStatus, DateApproved
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
        WHERE UPPER(BorrowerName) LIKE '%{name}%'
        LIMIT 5
    """
    df = c.query(q).to_dataframe()
    print(f"--- {name} ---")
    print(df.to_string() if not df.empty else "  No PPP records")

# Also check if any of these have OSINT entity records
print("\n=== OSINT for TS MARKETPLACE ===")
q2 = """
    SELECT name, address, city, state, ein
    FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
    WHERE UPPER(name) LIKE '%TS MARKETPLACE%'
       OR UPPER(name) LIKE '%19822 BROOKHURST%'
       OR UPPER(name) LIKE '%HRAPTS%'
    LIMIT 10
"""
df2 = c.query(q2).to_dataframe()
print(df2.to_string() if not df2.empty else "  Not found in OSINT")
