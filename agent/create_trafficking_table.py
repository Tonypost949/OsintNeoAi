import pandas as pd
from google.cloud import bigquery

bq = bigquery.Client()

q = """
CREATE OR REPLACE TABLE `project-743aab84-f9a5-4ec7-954.ppp_rico.trafficking_matches` AS
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, BorrowerZip, CurrentApprovalAmount, 'PPP > 150k' as Source 
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus` 
WHERE UPPER(BorrowerName) LIKE '%CARMEN LUEGE%' OR UPPER(BorrowerName) LIKE '%VICTOR NUNEZ%' OR UPPER(BorrowerName) LIKE '%PAUL BARNES%'
UNION ALL
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, BorrowerZip, CurrentApprovalAmount, 'PPP < 150k' as Source 
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k` 
WHERE UPPER(BorrowerName) LIKE '%CARMEN LUEGE%' OR UPPER(BorrowerName) LIKE '%VICTOR NUNEZ%' OR UPPER(BorrowerName) LIKE '%PAUL BARNES%'
"""

job = bq.query(q)
job.result()
print("Trafficking matches table created!")
