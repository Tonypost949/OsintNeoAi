from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project='noble-beanbag-497411-m4')

# Find all addresses with 3+ LLCs (shell factory pattern)
query = """
SELECT 
  SiteAddress,
  COUNT(DISTINCT Owner1) as llc_count,
  ARRAY_AGG(DISTINCT Owner1) as llcs
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE SiteAddress IS NOT NULL
GROUP BY SiteAddress
HAVING COUNT(DISTINCT Owner1) >= 3
ORDER BY llc_count DESC
"""

results = client.query(query).result()
print('=== SHELL FACTORY ADDRESSES (3+ LLCs) ===\n')

shell_factories = []
for row in results:
    shell_factories.append({
        'address': row.SiteAddress,
        'llc_count': row.llc_count,
        'llcs': row.llcs
    })
    print(f'{row.SiteAddress}: {row.llc_count} LLCs')
    for llc in row.llcs[:5]:  # Show first 5
        print(f'  - {llc}')
    if len(row.llcs) > 5:
        print(f'  ... and {len(row.llcs) - 5} more')
    print()

print(f'\nTotal shell factory addresses: {len(shell_factories)}')
print(f'Total LLCs in shell factories: {sum(sf["llc_count"] for sf in shell_factories)}')
