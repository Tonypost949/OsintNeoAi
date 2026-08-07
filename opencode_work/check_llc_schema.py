from google.cloud import bigquery
c = bigquery.Client(project="noble-beanbag-497411-m4")

q = """
SELECT column_name, data_type
FROM `noble-beanbag-497411-m4.ppp_rico.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = "hb_llcs"
ORDER BY ordinal_position
"""
df = c.query(q).to_dataframe()
print("hb_llcs columns:")
print(df.to_string())

# Get full data for the key LLCs
q2 = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, MailState,
       APN, LastSeller, LastSaleDate, LastSaleValue
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) IN (
    "TRIUMVIRATE LLC",
    "19822 BROOKHURST LLC",
    "RAI PARTNERS LLC",
    "TS MARKETPLACE LLC",
    "HRAPTS1 LLC"
)
"""
df2 = c.query(q2).to_dataframe()
print("\nKey LLCs full records:")
print(df2.to_string())

# Get ALL LLCs at 333 Washington Blvd
q3 = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSaleValue
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(MailAddress) LIKE '%333 WASHINGTON%'
ORDER BY LastSaleValue DESC
"""
df3 = c.query(q3).to_dataframe()
print("\nAll LLCs at 333 Washington Blvd:")
print(df3.to_string())
