from google.cloud import bigquery
import pandas as pd

def check_cocs():
    client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
    query = """
    SELECT * FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.cps_trafficking_layer`
    LIMIT 1
    """
    try:
        df = client.query(query).to_dataframe()
        print("Columns in cps_trafficking_layer:", df.columns.tolist())
    except Exception as e:
        print(e)

if __name__ == '__main__':
    check_cocs()
