from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

print("--- Querying hb_llcs for DNA INVESTMENTS ---")
q1 = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleValue
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE Owner1 LIKE '%DNA INVESTMENTS%'
   OR SiteAddress LIKE '%IMA LOA%'
"""
try:
    results1 = client.query(q1).result()
    for row in results1:
        print(dict(row))
except Exception as e:
    print(f"Error querying DNA INVESTMENTS: {e}")
