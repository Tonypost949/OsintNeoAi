import pandas as pd
from google.cloud import bigquery

bq = bigquery.Client()
q = """
SELECT DISTINCT clean_owner 
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.v_rico_enterprise_master`
WHERE clean_owner IS NOT NULL
  AND UPPER(clean_owner) NOT LIKE '%LLC%'
  AND UPPER(clean_owner) NOT LIKE '%INC%'
  AND UPPER(clean_owner) NOT LIKE '%TRUST%'
  AND UPPER(clean_owner) NOT LIKE '%CITY %'
  AND UPPER(clean_owner) NOT LIKE '%STATE %'
  AND UPPER(clean_owner) NOT LIKE '%CHURCH%'
  AND UPPER(clean_owner) NOT LIKE '%CORP%'
  AND UPPER(clean_owner) NOT LIKE '%COMPANY%'
  AND UPPER(clean_owner) NOT LIKE '%L.P.%'
  AND UPPER(clean_owner) NOT LIKE '%LP'
  AND UPPER(clean_owner) NOT LIKE '%PARTNERS%'
  AND clean_owner LIKE '% %'
LIMIT 50
"""
df = bq.query(q).to_dataframe()
print('Potential Human Owners (Master View):')
for name in df['clean_owner']:
    print(name)
