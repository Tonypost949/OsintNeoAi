from google.cloud import bigquery
import pandas as pd

def check_audit():
    client = bigquery.Client(project='noble-beanbag-497411-m4')
    query = """
    SELECT * FROM `noble-beanbag-497411-m4.forensic_layers.v_expanded_structural_audit`
    LIMIT 1
    """
    try:
        df = client.query(query).to_dataframe()
        print("Columns in v_expanded_structural_audit:", df.columns.tolist())
    except Exception as e:
        print(e)

if __name__ == '__main__':
    check_audit()
