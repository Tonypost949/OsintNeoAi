from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

print("--- Querying hb_llcs for street name fragments ---")
streets = ["LANGPORT", "LAWSON"]

for st in streets:
    q = f"""
    SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleValue
    FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
    WHERE UPPER(SiteAddress) LIKE '%{st}%' OR UPPER(MailAddress) LIKE '%{st}%'
    """
    try:
        results = list(client.query(q).result())
        print(f"\nStreet {st} matches: {len(results)}")
        for r in results:
            print(f"Owner1: {r.Owner1} | Owner2: {r.Owner2}")
            print(f"Site: {r.SiteAddress} | Mail: {r.MailAddress}")
            print(f"Seller: {r.LastSeller} | Value: ${r.LastSaleValue:,.2f}")
    except Exception as e:
        print(f"Error: {e}")
