from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

print("--- Querying hb_llcs for CP PREMIER CAPITAL LLC ---")
q = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSeller, LastSaleValue, APN
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%CP PREMIER%' OR UPPER(Owner2) LIKE '%CP PREMIER%'
"""
try:
    results = list(client.query(q).result())
    print(f"Found {len(results)} matches:")
    for r in results:
        print(f"Owner1: {r.Owner1} | Owner2: {r.Owner2}")
        print(f"Site: {r.SiteAddress} | Mail: {r.MailAddress}, {r.MailCity}")
        print(f"Seller: {r.LastSeller} | Value: ${r.LastSaleValue:,.2f} | APN: {r.APN}")
        print("-" * 30)
except Exception as e:
    print(f"Error querying hb_llcs: {e}")
