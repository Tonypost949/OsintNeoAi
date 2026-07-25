from google.cloud import bigquery
import pandas as pd

def check_audit():
    client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
    query = """
    SELECT * FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.v_expanded_structural_audit`
    LIMIT 1
    """
    try:
        df = client.query(query).to_dataframe()
        print("Columns in v_expanded_structural_audit:", df.columns.tolist())
    except Exception as e:
        print(e)

if __name__ == '__main__':
    check_audit()
