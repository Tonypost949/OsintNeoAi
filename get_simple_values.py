from google.cloud import bigquery
bq = bigquery.Client(project='noble-beanbag-497411-m4')

# Simple query on beach_blvd_cluster
results = bq.query("SELECT SiteAddress, LastSaleValue FROM `noble-beanbag-497411-m4.ppp_rico.beach_blvd_cluster` LIMIT 20").result()
for r in results:
    val = r.LastSaleValue
    if val:
        print(f"{r.SiteAddress} | ${val:,.0f}")
    else:
        print(f"{r.SiteAddress} | [No sale value]")

print("\n=== HB TARGET PARCELS ===")
results = bq.query("SELECT * FROM `noble-beanbag-497411-m4.ai_sandbox.hb_target_parcels`").result()
for r in results:
    for k, v in r.items():
        if v is not None:
            print(f"  {k}: {v}")
    print()