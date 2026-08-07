from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Find zero-dollar transfer clusters
query = """
SELECT 
  LastSeller,
  COUNT(*) as transfer_count,
  ARRAY_AGG(Owner1) as buyers,
  ARRAY_AGG(SiteAddress) as addresses
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE CAST(LastSaleValue AS FLOAT64) = 0
  AND LastSeller IS NOT NULL
  AND LastSeller != ''
GROUP BY LastSeller
HAVING COUNT(*) >= 2
ORDER BY transfer_count DESC
LIMIT 20
"""

results = client.query(query).result()
print('=== ZERO-DOLLAR TRANSFER CLUSTERS ===\n')

for row in results:
    print(f'{row.transfer_count} transfers from {row.LastSeller}')
    for buyer, addr in zip(row.buyers[:5], row.addresses[:5]):
        print(f'  {buyer} -> {addr}')
    if len(row.buyers) > 5:
        print(f'  ... and {len(row.buyers) - 5} more')
    print()
