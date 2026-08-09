
from google.cloud import bigquery

def query_offshore_borrowers():
    """
    Queries PPP loan tables to find borrowers with names containing
    offshore-related keywords.
    """
    try:
        client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
        
        tables_to_query = [
            "project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus",
            "project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k"
        ]
        
        offshore_keywords = r'(remit|overseas|foreign|international|philippines|manila)'

        for table_id in tables_to_query:
            print("\\n" + "="*80)
            print(f"Querying table: {table_id}")
            print("="*80)

            sql_query = f"""
                SELECT
                    BorrowerName,
                    BorrowerCity,
                    BorrowerState,
                    InitialApprovalAmount,
                    BusinessType,
                    OriginatingLender
                FROM
                    `{table_id}`
                WHERE
                    REGEXP_CONTAINS(LOWER(BorrowerName), r'{offshore_keywords}')
                ORDER BY
                    InitialApprovalAmount DESC
                LIMIT 50;
            """

            query_job = client.query(sql_query)
            results = query_job.result()

            if results.total_rows > 0:
                print(f"{'Borrower Name':<50} | {'City':<20} | {'State':<5} | {'Amount':>15} | {'Lender'}")
                print("-" * 120)
                for row in results:
                    print(f"{row.BorrowerName:<50} | {row.BorrowerCity:<20} | {row.BorrowerState:<5} | {row.InitialApprovalAmount:>15.2f} | {row.OriginatingLender}")
            else:
                print("No borrowers found with offshore keywords in this table.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    query_offshore_borrowers()
