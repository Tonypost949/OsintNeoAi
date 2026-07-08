from google.cloud import bigquery
c = bigquery.Client(project="noble-beanbag-497411-m4")

print("=== MERCY HOUSE / CHDO CA addresses ===")
q = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE (UPPER(BorrowerName) LIKE '%MERCY%' OR UPPER(BorrowerName) LIKE '%CHDO%')
  AND BorrowerState = 'CA'
"""
df = c.query(q).to_dataframe()
print(df.to_string())

mercy_addrs = set()
for addr in df["BorrowerAddress"].str.upper().tolist():
    if addr and addr != "NA":
        mercy_addrs.add(addr.strip())

llc_addrs = {
    "21951 BROOKHURST ST", "20002 BROOKHURST ST", "20052 BROOKHURST ST",
    "19822 BROOKHURST ST", "19001 BROOKHURST ST", "20972 BROOKHURST ST",
    "21501 BROOKHURST ST", "17025 BROOKHURST ST", "19071 BROOKHURST ST",
    "3311 BOUNTY CIR", "1077 PACIFIC COAST HWY",
    "9874 RARITAN AVE", "15565 BROOKHURST ST",
    "333 WASHINGTON BLVD", "8541 EMERYWOOD DR",
}

overlap = mercy_addrs.intersection(llc_addrs)
print(f"\nOverlapping addresses with Mercy House: {overlap}")

print("\n=== OSINT entities near Brookhurst ===")
q2 = """
SELECT name, address, city, state
FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
WHERE UPPER(address) LIKE '%BROOKHURST%'
   OR UPPER(address) LIKE '%333 WASHINGTON%'
   OR UPPER(address) LIKE '%RARITAN%'
   OR UPPER(address) LIKE '%BOUNTY%'
LIMIT 20
"""
df2 = c.query(q2).to_dataframe()
print(df2.to_string() if not df2.empty else "  None found")

print("\n=== 333 Washington Blvd anywhere in data ===")
q3 = """
SELECT 'PPP' as src, BorrowerName, BorrowerAddress, BorrowerCity
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerAddress) LIKE '%333 WASHINGTON%'
UNION ALL
SELECT 'OSINT' as src, name, address, city
FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
WHERE UPPER(address) LIKE '%333 WASHINGTON%'
LIMIT 20
"""
df3 = c.query(q3).to_dataframe()
print(df3.to_string() if not df3.empty else "  None found")

print("\n=== 333 Washington Blvd search in LLC records ===")
q4 = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(MailAddress) LIKE '%333 WASHINGTON%'
   OR UPPER(SiteAddress) LIKE '%333 WASHINGTON%'
LIMIT 10
"""
df4 = c.query(q4).to_dataframe()
print(df4.to_string() if not df4.empty else "  None found")

print("\n=== Search for 333 WASHINGTON BLVD in national_audits ===")
q5 = """
SELECT file_name, file_path, file_type
FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
WHERE UPPER(file_path) LIKE '%333 WASHINGTON%'
   OR UPPER(file_name) LIKE '%333 WASHINGTON%'
LIMIT 10
"""
try:
    df5 = c.query(q5).to_dataframe()
    print(df5.to_string() if not df5.empty else "  None found")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone.")
