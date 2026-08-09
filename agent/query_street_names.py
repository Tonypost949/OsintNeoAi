from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Querying hb_llcs for street name fragments ---")
streets = ["LANGPORT", "LAWSON"]

for st in streets:
    q = f"""
    SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleValue
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
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
