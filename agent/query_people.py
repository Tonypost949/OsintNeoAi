import pandas as pd
from google.cloud import bigquery

bq = bigquery.Client()

queries = [
    """
    SELECT BorrowerName, BorrowerAddress, BorrowerCity, CurrentApprovalAmount, 'PPP > 150k' as Source 
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus` 
    WHERE UPPER(BorrowerName) LIKE '%CARMEN LUEGE%' OR UPPER(BorrowerName) LIKE '%VICTOR NUNEZ%' OR UPPER(BorrowerName) LIKE '%PAUL BARNES%'
    """,
    """
    SELECT BorrowerName, BorrowerAddress, BorrowerCity, CurrentApprovalAmount, 'PPP < 150k' as Source 
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k` 
    WHERE UPPER(BorrowerName) LIKE '%CARMEN LUEGE%' OR UPPER(BorrowerName) LIKE '%VICTOR NUNEZ%' OR UPPER(BorrowerName) LIKE '%PAUL BARNES%'
    """
]

for i, q in enumerate(queries):
    try:
        df = bq.query(q).to_dataframe()
        if not df.empty:
            print(f"Match found in query {i+1}:")
            print(df)
        else:
            print(f"No match in query {i+1}")
    except Exception as e:
        print(f"Error in query {i+1}: {e}")
