from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

addresses = [
    "5911 LANGPORT",
    "10605 LAWSON",
    "14776 MORAN",
    "33512 SUNRIDGE",
    "9445 EDINGER",
    "10141 WESTMINSTER",
    "3265 EASY",
    "9741 BOLSA",
    "11561 MAGNOLIA",
    "8274 GALAXY",
    "7561 CENTER",
    "8161 BESTEL",
    "13262 ALAN",
    "12285 LIGHTHOUSE"
]

print("--- Querying hb_llcs for address fragments ---")
for addr in addresses:
    q = f"""
    SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleValue
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
    WHERE UPPER(SiteAddress) LIKE '%{addr}%'
       OR UPPER(MailAddress) LIKE '%{addr}%'
    """
    try:
        rows = list(client.query(q).result())
        if rows:
            print(f"\n[ADDRESS: {addr}] Found {len(rows)} matches in hb_llcs:")
            for r in rows:
                print(f"- Owner1: {r.Owner1} | Owner2: {r.Owner2}")
                print(f"  Address: {r.SiteAddress} | Mail: {r.MailAddress}, {r.MailCity}")
                print(f"  Seller: {r.LastSeller} | Value: ${r.LastSaleValue:,.2f}")
    except Exception as e:
        print(f"Error querying address {addr}: {e}")

print("\n--- Querying ppp_property_bridge for address fragments ---")
for addr in addresses:
    q = f"""
    SELECT entity_name, property_address, property_mail_address, last_seller, property_acquisition_value
    FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.ppp_property_bridge`
    WHERE UPPER(property_address) LIKE '%{addr}%'
       OR UPPER(property_mail_address) LIKE '%{addr}%'
    """
    try:
        rows = list(client.query(q).result())
        if rows:
            print(f"\n[ADDRESS: {addr}] Found {len(rows)} matches in ppp_property_bridge:")
            for r in rows:
                print(f"- Entity: {r.entity_name} | Property: {r.property_address} | Mail: {r.property_mail_address}")
                print(f"  Seller: {r.last_seller} | Value: ${r.property_acquisition_value:,.2f}")
    except Exception as e:
        print(f"Error querying address {addr}: {e}")
