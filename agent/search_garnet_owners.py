from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Querying hb_llcs for MailAddress = 15822 Garnet ---")
q = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleValue
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
WHERE UPPER(MailAddress) LIKE '%15822%GARNET%'
"""

try:
    results = client.query(q).result()
    count = 0
    for r in results:
        count += 1
        print(f"Match {count}:")
        print(f"Owner1: {r.Owner1} | Owner2: {r.Owner2}")
        print(f"Site Address: {r.SiteAddress}")
        print(f"Mail Address: {r.MailAddress}, {r.MailCity}")
        print(f"Seller: {r.LastSeller} | Value: ${r.LastSaleValue:,.2f}")
        print(f"APN: {r.APN}")
        print("-" * 40)
except Exception as e:
    print(f"Error querying hb_llcs: {e}")
